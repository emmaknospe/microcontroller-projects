import dataclasses
import json
from typing import Iterable

import boto3
import dotenv
import tqdm
import click
import re
from packaging.version import Version
from mcutils.constants import CIRCUITPYTHON_DIR

dotenv.load_dotenv()

CIRCUITPYTHON_REPOSITORY_BUCKET = "adafruit-circuit-python"
CIRCUITPYTHON_PREFIX = "bin/"

flashes_dir = CIRCUITPYTHON_DIR / "flashes"
# e.g. https://downloads.circuitpython.org/bin/raspberry_pi_pico/en_US/adafruit-circuitpython-raspberry_pi_pico-en_US-9.1.3.uf2


@dataclasses.dataclass(frozen=True)
class CircuitPythonFlash:
    microcontroller: str
    version: str
    key: str


def update_flash_repository() -> None:
    # https://downloads.circuitpython.org is a url that points to a public S3 bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    # just list one level down, not recursively, to get a list of the microcontroller directories
    microcontroller_dirs = []
    paginator = s3.get_paginator("list_objects_v2")
    for result in paginator.paginate(Bucket=CIRCUITPYTHON_REPOSITORY_BUCKET, Prefix=CIRCUITPYTHON_PREFIX, Delimiter="/"):
        for prefix in result.get("CommonPrefixes", []):
            microcontroller_dirs.append(prefix.get("Prefix"))

    # add en_US to each microcontroller directory
    microcontroller_dirs = [microcontroller_dir + "en_US/" for microcontroller_dir in microcontroller_dirs]

    # list the versions in each microcontroller directory
    circuit_python_flashes = []
    for microcontroller_dir in tqdm.tqdm(microcontroller_dirs):
        paginator = s3.get_paginator("list_objects_v2")
        for result in paginator.paginate(Bucket=CIRCUITPYTHON_REPOSITORY_BUCKET, Prefix=microcontroller_dir):
            for content in result.get("Contents", []):
                key = content.get("Key")
                if key.endswith(".uf2"):
                    version = key.split("/")[-1].split("-")[-1].replace(".uf2", "")
                    circuit_python_flashes.append(
                        CircuitPythonFlash(
                            microcontroller=microcontroller_dir.split("/")[-3],
                            version=version,
                            key=key,
                        )
                    )
    click.echo(f"Found {len(circuit_python_flashes)} CircuitPython flashes")
    with open(flashes_dir / "circuit_python_flashes.json", "w") as f:
        json.dump([dataclasses.asdict(flash) for flash in circuit_python_flashes], f)


def load_flash_repository() -> list[CircuitPythonFlash]:
    with open(flashes_dir / "circuit_python_flashes.json", "r") as f:
        return [CircuitPythonFlash(**flash) for flash in json.load(f)]


def filter_and_sort_flashes(flashes: Iterable[CircuitPythonFlash]) -> Iterable[CircuitPythonFlash]:
    semver_pattern = re.compile(r'^\d+\.\d+\.\d+$')

    # Filter out non-semver versions
    valid_flashes = [flash for flash in flashes if semver_pattern.match(flash.version)]

    # Sort by semver
    sorted_flashes = sorted(valid_flashes, key=lambda flash: Version(flash.version))

    return sorted_flashes


def download_flash(flash: CircuitPythonFlash):
    flash_path = flashes_dir / flash.microcontroller / f"{flash.version}.uf2"
    flash_path.parent.mkdir(parents=True, exist_ok=True)
    if flash_path.exists():
        click.echo(f"Flash {flash.microcontroller} {flash.version} already is downloaded")
        return
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.download_file(CIRCUITPYTHON_REPOSITORY_BUCKET, flash.key, flash_path)
    click.echo(f"Downloaded {flash.microcontroller} {flash.version}")