import difflib
import os

import click
import subprocess
import pathlib
import json

from simple_term_menu import TerminalMenu


ADDITIONAL_BOARD_MANAGER_URLS = [
    "https://adafruit.github.io/arduino-board-index/package_adafruit_index.json"
]

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


@arduino.command()
@click.argument("search_term")
def lib_search(search_term):
    """
    Search for Arduino libraries and install the selected one
    """
    click.echo(f"Searching for Arduino libraries matching: {search_term}")

    # Search for libraries
    search_result = subprocess.run(["arduino-cli", "lib", "search", search_term, "--format", "json"],
                                   capture_output=True, text=True)
    libraries = json.loads(search_result.stdout)["libraries"]

    if not libraries:
        click.echo("No libraries found matching the search term.")
        return

    # Prepare menu items and descriptions
    menu_items = []
    descriptions = {}
    for lib in libraries:
        menu_item = f"{lib['name']} (v{lib['latest']['version']})"
        menu_items.append(menu_item)
        descriptions[menu_item] = lib['latest']['sentence']

    # Create TerminalMenu with preview window
    menu = TerminalMenu(
        menu_items,
        title="Select a library to install:",
        preview_command=lambda i: descriptions[i] if i is not None else "",
        preview_size=0.25
    )

    # Show menu and get selection
    selection = menu.show()

    if selection is not None:
        selected_library = libraries[selection]['name']
        click.echo(f"Installing library: {selected_library}")

        # Install the selected library
        install_result = subprocess.run(["arduino-cli", "lib", "install", selected_library], capture_output=True,
                                        text=True)

        if install_result.returncode == 0:
            click.echo(f"Successfully installed {selected_library}")
        else:
            click.echo(f"Failed to install {selected_library}. Error: {install_result.stderr}")
    else:
        click.echo("No library selected.")


@arduino.command()
@click.argument("search_term")
def core_search(search_term):
    """
    Search for Arduino core modules and install the selected one
    """
    click.echo(f"Searching for Arduino core modules matching: {search_term}")

    # update the board manager index
    subprocess.run(["arduino-cli", "core", "update-index"], check=True)

    # Prepare the command with additional URLs
    command = ["arduino-cli", "--additional-urls", ",".join(url for url in ADDITIONAL_BOARD_MANAGER_URLS), "core", "search", search_term, "--format", "json"]

    # Search for boards
    search_result = subprocess.run(command, capture_output=True, text=True)
    platforms = json.loads(search_result.stdout)["platforms"]
    if not platforms:
        click.echo("No platforms found matching the search term.")
        return

    # Prepare menu items and descriptions
    menu_items = []
    descriptions = {}
    for platform in platforms:
        version = platform['latest_version']
        current_release = platform['releases'][version]
        name = current_release['name']
        menu_item = f"{platform['id']} ({current_release}, v{version})"
        menu_items.append(menu_item)
        boards_string = "Boards:" + ", ".join(board["name"] for board in current_release["boards"])
        descriptions[menu_item] = f"{name}\n{boards_string}"

    # Create TerminalMenu with preview window
    menu = TerminalMenu(
        menu_items,
        title="Select a board to install:",
        preview_command=lambda i: descriptions[i] if i is not None else "",
        preview_size=0.25
    )

    # Show menu and get selection
    selection = menu.show()

    if selection is not None:
        platform = platforms[selection]['id']
        click.echo(f"Installing core package: {platform}")

        # Install the selected board
        install_command = [
            "arduino-cli",
            "--additional-urls",
            ",".join(url for url in ADDITIONAL_BOARD_MANAGER_URLS),
            "core",
            "install",
            platform
        ]

        install_result = subprocess.run(install_command, text=True)

        if install_result.returncode == 0:
            click.echo(f"Successfully installed {platform}")
        else:
            click.echo(f"Failed to install {platform}.")
    else:
        click.echo("No core package selected.")


@arduino.command()
@click.argument("example_name")
def load_example(example_name):
    """
    List installed libraries, select one, then load an example from that library
    """
    click.echo("Fetching installed libraries...")

    # Get list of examples and libraries
    lib_list_result = subprocess.run(["arduino-cli", "lib", "examples", "--json"], capture_output=True, text=True)
    libraries = json.loads(lib_list_result.stdout)["examples"]

    if not libraries:
        click.echo("No libraries installed.")
        return

    # pair libraries with examples
    examples = []
    for pair in libraries:
        for example in pair["examples"]:
            example = pathlib.Path(example)
            examples.append({"library": pair["library"]['name'], "example": example})
    # sort examples by similarity to search term
    examples.sort(key=lambda x: difflib.SequenceMatcher(None, x["example"].name, example_name).ratio(), reverse=True)

    example_menu_items = [f"{example['library']} - {example['example'].name}" for example in examples]
    # Create TerminalMenu for example selection
    example_menu = TerminalMenu(
        example_menu_items,
        title="Select a library:",
        preview_size=0.25
    )

    # Show menu and get library selection
    example_selection_index = example_menu.show()

    if example_selection_index is None:
        click.echo("No example selected.")
        return

    selected_example = examples[example_selection_index]["example"]

    click.echo(f"Loading example: {selected_example.name}")

    try:
        subprocess.run(["arduino-cli", "sketch", "new", selected_example.name], check=True)
        for item in os.listdir(selected_example):
            full_path = selected_example / item
            dest_path = pathlib.Path(selected_example.name) / item
            if full_path.is_file():
                subprocess.run(["cp", full_path, dest_path], check=True)
        click.echo(f"Successfully loaded example '{selected_example}' into the current directory.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to load example. Error: {e}")