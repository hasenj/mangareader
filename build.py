"""
    builds a distribution for windows (not a cross-compiler; must be invoked under windows)

    requires:
        py2exe
        git (e.g. msysgit)
        rm (msys, or install msysgit with the option of installing unix tools on the PATH)
        7z (install 7-zip and make sure 7z.exe is in the PATH)
"""
import os

main = 'manga'
dest = 'dist_nt'

def do_exe():
 setup(
        windows=[dict(
            script = main, 
                )], 
        options=dict(
            py2exe=dict(
                includes=['sip'],
                compressed=False, 
                dist_dir=dest,
                )),
        data_files = [ 
            ('art', ['art/icon.png']),
            ],
        )   

import sys
sys.argv = [sys.argv[0], "py2exe"]

from distutils.core import setup
import py2exe

os.system("rm -rf " + dest)  # clean previous build
do_exe()                     # call py2exe
os.system("git checkout-index -a -f --prefix=" + dest + "/src/") # add source code to build directory (because we're gpl)
os.system("rm -rf build")    # clean intermediate build files

