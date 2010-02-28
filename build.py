"""
    builds a distribution for windows (not a cross-compiler; must be invoked under windows)

    requires:
        py2exe
        git (e.g. msysgit)
        rm (msys, or install msysgit with the option of installing unix tools on the PATH)
        7z (install 7-zip and make sure 7za.exe is in the PATH)
"""
import os

# This is used to preserve XP/Vista look and feel
# Don't ask me why, but without this, it will look ugly
manifest = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="0.64.1.0"
    processorArchitecture="*"
    name="Python"
    type="win32"
/>
<description>Python Interpreter</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="*"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
"""

main = 'qt_gui.py'
dest = 'mangareader'
version = '0.0.5.x'
dest_7z = 'mangareader_v%s.7z' % version

def do_exe():
 setup(
        windows=[dict(
                script = main, 
                other_resources = [(24,1,manifest)]
                )], 
        options=dict(
            py2exe=dict(
                optimize=2, 
                includes=['sip'],
                compressed=True, 
                dist_dir=dest,
                bundle_files=3
                )),
        # zipfile = None,
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

os.system("7za a " + dest_7z + " " + dest) # create an archive suitable for distribution
os.system("rm -rf build")    # clean intermediate build files

