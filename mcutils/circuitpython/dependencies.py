import dataclasses
import shutil
from pathlib import Path
import zipfile
from mcutils.constants import CIRCUITPYTHON_DIR

lib_dir = CIRCUITPYTHON_DIR / "libs"


@dataclasses.dataclass
class Library:
    bundle: str
    name: str
    key: Path


def load_bundles() -> list[str]:
    bundles = lib_dir.glob("*.zip")
    return [bundle.stem for bundle in bundles]


def load_bundle(bundle: Path) -> list[Library]:
    libraries = []
    with zipfile.ZipFile(bundle) as z:
        # libraries are in the /lib directory of the zip file, under the top level directory
        # they can be files or directories
        lib_level_subitems = set()
        for info in z.infolist():
            first_level = info.filename.split("/")[1] # this is the level right under the top level, so lib or no lib
            if first_level == "lib":
                # we're in the right directory, truncate
                lib_level_subitems.add("/".join(info.filename.split("/")[0:3]))
        for subitem in lib_level_subitems:
            subitem_path = Path(subitem)
            if subitem_path.stem == "__init__":
                continue
            libraries.append(Library(name=subitem_path.stem, key=subitem_path, bundle=bundle.stem))

    return libraries


def load_all_libraries() -> list[Library]:
    bundles = load_bundles()
    libraries = []
    for bundle in bundles:
        libraries.extend(load_bundle(lib_dir / f"{bundle}.zip"))
    return libraries


def install_library(library: Library, device: Path) -> None:
    with zipfile.ZipFile(lib_dir / f"{library.bundle}.zip") as z:
        # just copy everything whose key starts with the library key
        for info in z.infolist():
            if info.filename.startswith(str(library.key)):
                with z.open(info) as f:
                    # remove the bundle prefix, keep the /lib
                    write_path = device / ("/".join(info.filename.split("/")[1:]))
                    write_path.parent.mkdir(parents=True, exist_ok=True)
                    print(f"Writing {info.filename} to {write_path}")
                    with open(write_path, "wb") as out:
                        out.write(f.read())
