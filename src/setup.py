import distutils.core

from Cython.Build import cythonize


import sys
import subprocess
import shutil
import os


SCRIPT_NAME = "othello_bot"


CURRENT_PATH = os.path.dirname(__file__)
PARENT_DIRECTORY = os.path.abspath(os.path.join(CURRENT_PATH, os.pardir))
DIST_LOCATION = os.path.join(PARENT_DIRECTORY, "dist")

original_items = tuple(map(lambda i: os.path.join(CURRENT_PATH, i), os.listdir(CURRENT_PATH)))


print("\033[33;1m <-- COMPILING FILES --> \033[0m")

sys.argv = sys.argv[:1]
sys.argv.append("build_ext")
sys.argv.append("--inplace")


os.environ["CFLAGS"] = "-O3"

distutils.core.setup(
    ext_modules=cythonize(
        "*.pyx",
        compiler_directives={"optimize.use_switch": True,
                             "optimize.unpack_method_calls": True},
        language_level=3,
        force=True,
    )
)


print("\033[33;1m <-- BUILDING_EXECUTABLE --> \033[0m")
subprocess.call(rf"python -m PyInstaller -y {SCRIPT_NAME}.py")


print("\033[33;1m <-- CLEANING UP --> \033[0m")

try:
    print(f"Removing existing dist folder if exists ({DIST_LOCATION}).")
    shutil.rmtree(DIST_LOCATION)
except FileNotFoundError:
    pass

print(f"Copying dist folder to parent directory (dist -> {DIST_LOCATION}).")
shutil.copytree("dist", DIST_LOCATION)
shutil.copy("network.h5", os.path.join(PARENT_DIRECTORY, "dist", SCRIPT_NAME))


things = tuple(map(lambda i: os.path.join(CURRENT_PATH, i), os.listdir(CURRENT_PATH)))
for item in filter(lambda i: i not in original_items, things):
    item_path = os.path.join(CURRENT_PATH, item)
    print(f"Removing item: {item_path}")
    try:
        os.remove(item_path)
    except PermissionError:
        shutil.rmtree(item_path)
