import click
from mcutils.cli.circuitpython import circuitpython
from mcutils.cli.devices import devices
from mcutils.cli.dev import dev
from mcutils.cli.arduino import arduino

@click.group()
def cli():
    pass


cli.add_command(circuitpython)
cli.add_command(devices)
cli.add_command(dev)
cli.add_command(arduino)
