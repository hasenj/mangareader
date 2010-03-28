"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    The Directory tree has two kinds of nodes: files and directories.

    When walking the tree, we are usually more interested in files than directories: we're only
    interested in directories because they (potentially) contain files.

    File nodes are sort of like leafs, in that when walking the tree, we're interested in listing 
    files. However, they are different; leaf nodes can be directories, in which case we don't want
    to list them.
"""

class INode(object):
    """This is an interface, for documentation reference only"""
    @property
    def isfile(self):
        """Is this node a file?"""
        raise NotImplemented
    @property
    def isdir(self):
        """Is this a dir? always the opposite of `isfile`"""
        raise NotImplemented
    @property
    def ls(self):
        """return a list of child nodes. Only for directories"""
        raise NotImplemented

class ITree(object):
    """The node only carries information about its children, we need an encompassing
        object to be able to retrive a node's parent and siblings
    """
    @property
    def root(self):
        """get the root node in the tree"""
        raise NotImplemented

    def parent(self, node):
        """get the parent node. returns None for the root node"""
        raise NotImplemented
