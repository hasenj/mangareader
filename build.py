"""
    builds a distribution for windows (not a cross-compiler; must be invoked under windows)

    requires:
        py2exe
        git (e.g. msysgit)
        rm (msys, or install msysgit with the option of installing unix tools on the PATH)
        7z (install 7-zip and make sure 7z.exe is in the PATH)
"""
import os

main = 'qt_gui.py'
dest = 'mangareader'
version = '0.0.5.x'
dest_7z = 'mangareader_v%s.7z' % version

def do_exe():
 setup(
        windows=[dict(
            script = main, 
                )], 
        options=dict(
            py2exe=dict(
                optimize=2, 
                includes=['sip'],
                compressed=True, 
                dist_dir=dest,
                bundle_files=1
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

os.system("7z a " + dest_7z + " " + dest) # create an archive suitable for distribution
os.system("rm -rf build")    # clean intermediate build files

