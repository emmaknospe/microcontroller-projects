import click
import subprocess
import pathlib
import json

from simple_term_menu import TerminalMenu


@click.group
def arduino():
    pass


@arduino.command()
@click.argument("project_dir", type=click.Path(exists=True), default=".")
@click.option("--monitor", is_flag=True, help="Monitor the serial output")
def load(project_dir, monitor):
    """
    Load an Arduino project to a device
    """
    click.echo(f"Loading Arduino project from {project_dir}")
    # find available boards
    boards_raw = subprocess.run(["arduino-cli", "board", "list", "--json"], capture_output=True, text=True).stdout
    boards_response = json.loads(boards_raw)

    # filter to only matching boards
    matching_boards = [board for board in boards_response["detected_ports"] if "matching_boards" in board]

    selection = TerminalMenu(
        [f"{board['port']['label']} ({board['matching_boards'][0]['name']})" for board in matching_boards],
        title="Select board to load to.",
    ).show()
    selected_board = matching_boards[selection]
    fqbn = selected_board["matching_boards"][0]["fqbn"]
    address = selected_board["port"]["address"]

    # need to execute
    # arduino-cli compile -b rp2040:rp2040:adafruit_kb2040 --libraries ./libraries
    # arduino-cli upload -b rp2040:rp2040:adafruit_kb2040 -p /dev/cu.usbmodem14101
    # arduino-cli monitor  -p /dev/cu.usbmodem14101

    subprocess.run(["arduino-cli", "compile", "-b", fqbn, "--libraries", "./libraries"], check=True, cwd=project_dir)
    subprocess.run(["arduino-cli", "upload", "-b", fqbn, "-p", address], check=True, cwd=project_dir)
    if monitor:
        subprocess.run(["arduino-cli", "monitor", "-p", address], check=True, cwd=project_dir)


@arduino.command()
def monitor():
    """
    Monitor the serial output of an Arduino device
    """
    # find available ports
    ports_raw = subprocess.run(["arduino-cli", "board", "list", "--json"], capture_output=True, text=True).stdout
    ports_response = json.loads(ports_raw)
    ports = [port["port"]["address"] for port in ports_response["detected_ports"]]

    selection = TerminalMenu(
        ports,
        title="Select port to monitor.",
    ).show()
    selected_port = ports[selection]

    subprocess.run(["arduino-cli", "monitor", "-p", selected_port])