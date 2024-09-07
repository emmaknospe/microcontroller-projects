import click
from mcutils.cli.circuitpython import circuitpython
from mcutils.cli.devices import devices

@click.group()
def cli():
    pass


cli.add_command(circuitpython)
cli.add_command(devices)
