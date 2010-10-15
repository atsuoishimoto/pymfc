# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from distutils.core import setup, Extension
import os

os.system("python c:\\python23jp\\scripts\\pyrexc -o gen_pymfclib.c _pymfclib.pyx ")
#_pymfclib = Extension("_pymfclib", ["gen_pymfclib.c"])

# Compile the extension module
#setup(name="pymfclib", ext_modules=[_pymfclib])