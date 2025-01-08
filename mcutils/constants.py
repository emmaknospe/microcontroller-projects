from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent.parent
CIRCUITPYTHON_DIR = ROOT_DIR / "circuitpython"



if sys.platform == 'darwin':
    VOLUMES_DIR = Path('/Volumes')
elif sys.platform == 'linux':
    # assume linux
    username = Path.home().name
    VOLUMES_DIR = Path('/media') / username
else:
    raise NotImplementedError(f"Unsupported platform: {sys.platform}")

