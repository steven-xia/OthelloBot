import distutils.core

from Cython.Build import cythonize


import sys
import subprocess
import shutil
import os


original_things = tuple(os.listdir("."))


print("\033[33;1m <-- COMPILING FILES --> \033[0m")

if len(sys.argv) == 1:
    sys.argv.append("build_ext")
    sys.argv.append("--inplace")


os.environ["CFLAGS"] = "-O3"

distutils.core.setup(
    ext_modules=cythonize(
        "*.pyx",
        # exclude=["setup.py", "othello_bot.py"],
        compiler_directives={"optimize.use_switch": True,
                             "optimize.unpack_method_calls": True},
        language_level=3,
        force=True,
    )
)


print("\033[33;1m <-- BUILDING_EXECUTABLE --> \033[0m")
subprocess.call(r"python -m PyInstaller -y othello_bot.py")


print("\033[33;1m <-- CLEANING UP --> \033[0m")

try:
    shutil.rmtree(os.path.join("..", "dist"))
except FileNotFoundError:
    pass

shutil.copytree("dist", os.path.join("..", "dist"))
shutil.copy("network.h5", os.path.join("..", "dist", "othello_bot"))


things = os.listdir(".")
for item in things:
    if item not in original_things:
        item_path = os.path.join(".", item)
        try:
            print(f"Removing file: {item_path}")
            os.remove(item_path)
        except PermissionError:
            print(f"Removing directory: {item_path}")
            shutil.rmtree(item_path)
