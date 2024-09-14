import subprocess
import sys
import threading

import serial
import click
import pathlib
import tty
import termios
from simple_term_menu import TerminalMenu

from mcutils.circuitpython.dependencies import load_all_libraries
from mcutils.circuitpython.dev import load_project
from mcutils.project import Project


@click.group()
def dev():
    pass


@dev.command()
@click.argument("project_dir", type=click.Path(exists=True), default=".")
@click.option("--device", default="CIRCUITPY", help="The device to load the project to")
@click.option("--skip-deps", is_flag=True, help="Skip installing dependencies")
def load(project_dir, device, skip_deps):
    """
    Load a CircuitPython project to a device
    """
    project = Project.from_path(pathlib.Path(project_dir))
    load_project(project, pathlib.Path("/Volumes") / device, skip_deps=skip_deps)


@dev.command()
def monitor():
    """
    Monitor the serial output of a CircuitPython device
    """
    # find devices in /dev/tty.* with a name of usbmodem
    devices = subprocess.check_output(["ls", "/dev/"]).decode().split()
    devices = [device for device in devices if "tty.usbmodem" in device]
    if not devices:
        click.echo("No devices found")
        return
    if len(devices) > 1:
        selection = TerminalMenu(
            devices,
            title="Select your device",
        ).show()
        device = devices[selection]
    else:
        device = devices[0]

    # Configure the serial connection
    serial_terminal(f"/dev/{device}", 115200)


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def read_from_serial(ser):
    while True:
        if ser.in_waiting:
            sys.stdout.buffer.write(ser.read(ser.in_waiting))
            sys.stdout.flush()


def serial_terminal(port, baud_rate):
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connected to {port} at {baud_rate} baud")

        # Start a thread to continuously read from the serial port
        read_thread = threading.Thread(target=read_from_serial, args=(ser,), daemon=True)
        read_thread.start()

        print("Type your commands. Press Ctrl+] to exit.")

        while True:
            char = getch()

            if char == '\x1d':  # Ctrl+]
                print("\nExiting...")
                break
            elif char in ['\x03', '\x04']:  # Ctrl+C or Ctrl+D
                ser.write(char.encode())
            else:
                ser.write(char.encode())
                # sys.stdout.buffer.write(char.encode())
                # sys.stdout.flush()

    except serial.SerialException as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")


@dev.command()
def list_libraries():
    """
    List all available CircuitPython libraries
    """
    libraries = load_all_libraries()
    for library in libraries:
        click.echo(f"{library.name} ({library.key})")