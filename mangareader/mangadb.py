"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    We keep a list of known mangas, and a few attributes about each of them. 
    We don't use a relational database system (they all suck).

    We use a config file, powered by `configobj`

    The format is really simple: (pseudo config object)

        manga_name:
            name: Humanized Manga Name
            path: /path/to/manga
            marks:
                mark1: relative/path/to/picture
                mark2: ..
                mark3: ..
                mark4: ..  # we only support 4 marks
            likness:
                votes: 3    # can also be negative
                last_vote: 30-1-2010

        detective_conan:
            name: Meitantei Conan
            path: /home/hasenj/manga/conan
            mark1: file_52/image10.png

    The actual section name is not *that* important, you can think of it as an id; it's only something we use internally (more like, something for the config file)

"""    

import os

def get_config_file_path():
    """Get the location of the config file """
    if os.name == 'posix':
        return os.path.expanduser('~')
    elif os.name == 'nt': # windows ...
        try:
            from win32com.shell import shellcon, shell
        except:
            print "Warning: win32com is required for remembering stuff"
            return ''
        return shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        
from configobj import ConfigObj as conf

db = conf(os.path.join(get_config_file_path(), ".mangadb"))

def write_to_disk(db=db):
    """low-level function: saves configobj file to disk"""
    db.write()

def reload(db=db):
    """low-level function: reload configobj from disk"""
    if db.filename:
        db.reload()

def get_manga(manga_name, db=db):
    if not db.has_key(manga_name):
        db[manga_name] = {}
    return db[manga_name]

def find_manga_by_path(manga_path, db=db):
    for key, value in db.items():
        if value['path'] == path:
            return value
    return None

def rename_manga(oldname, newname, db=db):
    db.rename(oldname, newname)


