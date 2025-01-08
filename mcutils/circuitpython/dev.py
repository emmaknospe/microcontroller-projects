from pathlib import Path
import shutil

import click

from mcutils.circuitpython.dependencies import load_all_libraries, install_library
from mcutils.constants import VOLUMES_DIR
from mcutils.project import Project


def read_requirements(requirements: Path):
    """
    Read a requirements.txt file and return a list of dependencies
    """
    with open(requirements) as f:
        return [line.strip() for line in f.readlines() if not line.startswith("#") and line.strip() != ""]


def load_project(project: Project, device=VOLUMES_DIR / "CIRCUITPY", skip_deps=False):
    """
    Load a project to a device called CIRCUITPY
    """
    # check for requirements.txt
    requirements = project.path / "requirements.txt"
    if not skip_deps:
        if requirements.exists():
            all_libraries = load_all_libraries()
            # install the requirements
            dependencies = read_requirements(requirements)
            for dependency in dependencies:
                # find the library
                library = next((lib for lib in all_libraries if lib.name == dependency), None)
                if library is None:
                    raise FileNotFoundError(f"Library {dependency} not found")
                # copy the library to the device
                install_library(library, device=device)
        else:
            click.echo("No requirements.txt found, skipping library installation")
    else:
        click.echo("Skipping library installation")
    # copy the project to the device
    shutil.copytree(project.path, device, dirs_exist_ok=True)
    click.echo(f"Project loaded to {device}")


