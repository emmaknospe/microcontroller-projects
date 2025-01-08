import dataclasses
import re
import click
from simple_term_menu import TerminalMenu
import difflib
from mcutils.flash.circuitpython import load_flash_repository, filter_and_sort_flashes, flash_downloaded, \
    download_flash, flash_device
from mcutils.constants import VOLUMES_DIR


@dataclasses.dataclass
class BootDeviceInfo:
    fs_name: str
    uf2_info: str
    model: str
    board_id: str
    date: str


@click.group()
def devices():
    pass


@devices.command()
def ls():
    """
    List attached volumes, assuming they are mounted in VOLUMES_DIR
    """
    boot_devices = list_boot_volumes()

    for device in boot_devices:
        click.echo(f"{device.fs_name} (boot device: {device.model})")


@devices.command()
def list_flashes():
    """
    List available CircuitPython flashes
    """
    flashes = load_flash_repository()
    flashes = list(filter_and_sort_flashes(flashes))
    for flash in flashes:
        click.echo(f"{flash.microcontroller} {flash.version}")


@devices.command()
@click.option("--microcontroller", "-m", help="Filter flashes by microcontroller", default=None)
def flash(microcontroller):
    """
    Flash a CircuitPython UF2 file to a device
    """
    boot_devices = list_boot_volumes()

    for i, device in enumerate(boot_devices):
        click.echo(f"{i}: {device.fs_name} (boot device: {device.model})")

    selection = TerminalMenu(
        [device.fs_name for device in boot_devices],
        title="Select your boot device.",
    ).show()
    device = boot_devices[selection]
    click.echo(f"Flashing {device.fs_name} with {device.uf2_info} ({device.model})")

    # find the nearest matching 5 devices in the CircuitPython flashes
    flash_repository = load_flash_repository()
    microcontrollers = {flash.microcontroller for flash in flash_repository}
    if microcontroller is not None:
        microcontrollers = {mc for mc in microcontrollers if microcontroller in mc}

    sorted_microcontrollers = sorted(
        microcontrollers,
        key=lambda x: difflib.SequenceMatcher(None, x.lower(), device.model.lower()).ratio(),
        reverse=True
    )
    selection = TerminalMenu(
        sorted_microcontrollers,
        title=f"Select the board matching {device.model}. Suggested boards are at the top.",
    ).show()
    microcontroller = sorted_microcontrollers[selection]
    click.echo(f"Selected {microcontroller}")
    # find the latest version for the selected microcontroller
    flashes = [flash for flash in flash_repository if flash.microcontroller == microcontroller]
    flashes = list(filter_and_sort_flashes(flashes))
    flashes.reverse()
    selection = TerminalMenu(
        [flash.version for flash in flashes],
        title="Select the version to flash.",
    ).show()
    flash = flashes[selection]
    if not flash_downloaded(flash):
        click.echo(f"Downloading {flash.version}")
        download_flash(flash)
    click.echo(f"Flashing {device.fs_name} with {flash.version}")
    flash_device(flash, device)


def list_boot_volumes():
    boot_devices = []
    for volume in VOLUMES_DIR.iterdir():
        # check for INFO_UF2.TXT
        info_uf2 = volume / 'INFO_UF2.TXT'
        if info_uf2.exists():
            with info_uf2.open() as f:
                file_text = f.read()
                # e.g.
                # TinyUF2 Bootloader 0.10.2 - tinyusb (0.12.0-203-ga4cfd1c69)
                # Model: Adafruit Feather ESP32-S3 TFT
                # Board-ID: ESP32S3-FeatherTFT-revA
                # Date: Jun 24 2022
                uf2_info = file_text.split('\n')[0]
                model = re.search(r'Model: (.+)', file_text).group(1)
                board_id = re.search(r'Board-ID: (.+)', file_text).group(1)
                try:
                    date = re.search(r'Date: (.+)', file_text).group(1)
                except AttributeError:
                    date = "Unknown"
                boot_devices.append(BootDeviceInfo(
                    volume.name,
                    uf2_info,
                    model,
                    board_id,
                    date
                ))
    return boot_devices
