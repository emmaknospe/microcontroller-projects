import click

from mcutils.flash.circuitpython import update_flash_repository, load_flash_repository, filter_and_sort_flashes, \
    download_flash


@click.group()
def circuitpython():
    pass


@circuitpython.command()
def update_flashes():
    update_flash_repository()


@circuitpython.command()
def list_microcontrollers():
    flash_repository = load_flash_repository()
    microcontrollers = set()
    for flash in flash_repository:
        microcontrollers.add(flash.microcontroller)
    for microcontroller in sorted(microcontrollers):
        click.echo(microcontroller)


@circuitpython.command()
@click.argument("microcontroller")
def list_versions(microcontroller):
    flash_repository = load_flash_repository()
    versions = set()
    for flash in flash_repository:
        if flash.microcontroller == microcontroller:
            versions.add(flash)
    if versions:
        for version in filter_and_sort_flashes(versions):
            click.echo(version.version)
    else:
        click.echo(f"No versions found for microcontroller: {microcontroller}")


@circuitpython.command()
@click.argument("microcontroller")
@click.option("--version", default=None, help="Specify a version to download")
def download(microcontroller, version):
    flash_repository = load_flash_repository()
    flashes = [flash for flash in flash_repository if flash.microcontroller == microcontroller]

    if not flashes:
        click.echo(f"No flashes found for microcontroller: {microcontroller}")
        return

    if version:
        flash_to_download = next((flash for flash in flashes if flash.version == version), None)
        if not flash_to_download:
            click.echo(f"Version {version} not found for microcontroller: {microcontroller}")
            return
    else:
        sorted_flashes = filter_and_sort_flashes(flashes)
        flash_to_download = sorted_flashes[-1]  # Most recent version

    download_flash(flash_to_download)
