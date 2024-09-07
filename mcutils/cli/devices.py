import click
import os
import subprocess


@click.group()
def devices():
    pass


@devices.command()
def ls():
    """
    List attached usb devices. Mount any that are not mounted using the mount command.
    """
    # Get list of block devices
    lsblk_output = subprocess.check_output(["lsblk", "-ndo", "NAME,TYPE,MOUNTPOINT"]).decode()

    # Parse the output
    devices = [line.split() for line in lsblk_output.strip().split('\n')]

    for device in devices:
        if len(device) >= 2 and device[1] == "disk":
            device_name = f"/dev/{device[0]}"

            # Get device info
            # info = subprocess.check_output(["udevadm", "info", "--query=all", "--name=" + device_name]).decode()
            # Get the device label
            try:
                label = subprocess.check_output(["lsblk", "-ndo", "LABEL", device_name]).decode().strip()
            except subprocess.CalledProcessError:
                label = "Unknown"

            print(f"Found USB drive: {device_name} (Label: {label})")

            # Check if the label matches the target name
            if True:
                # Check if it's already mounted
                if len(device) == 3 and device[2]:
                    print(f"Device {device_name} is already mounted at {device[2]}")
                else:
                    print("Would mount device")
                    # Create a mount point
                    # mount_point = f"/media/{label}"
                    # os.makedirs(mount_point, exist_ok=True)
                    #
                    # # Attempt to mount the device
                    # try:
                    #     subprocess.run(["sudo", "mount", device_name, mount_point], check=True)
                    #     print(f"Successfully mounted {device_name} at {mount_point}")
                    # except subprocess.CalledProcessError as e:
                    #     print(f"Failed to mount {device_name}: {e}")


