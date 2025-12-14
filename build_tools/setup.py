from setuptools import setup
from Cython.Build import cythonize
import numpy
import os

# This setup script compiles specified .py files into native extensions.
# This is a key part of protecting the source code.

def find_py_files(directory):
    py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py" and file != "config.py":
                py_files.append(os.path.join(root, file))
    py_files.append("build_tools/init_models.py")
    py_files.append("build_tools/encrypt_model.py")
    return py_files

setup(
    ext_modules=cythonize(
        find_py_files("app"),
        compiler_directives={'language_level' : "3"}
    ),
    include_dirs=[numpy.get_include()]
)

# How to run:
# python build_tools/setup.py build_ext --inplace
# This will create .pyd files (on Windows) for all python files
# inside the app/ directory.
