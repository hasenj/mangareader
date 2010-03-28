"""
    Author: Hasen "hasenj" il Judy
    License: GPL v2

    Walk the directory tree, starting from an arbitrary node, and get some results.

    Here are some examples:
        
        we'll always be moving forward; to the left
        o represent directory nodes
        @ represent file nodes
        [o] is the starting node
        ^ below the node is the result we want to get:
        ... means there can be any arbitrary structure in this area (i.e. we don't care what's here)

        * starting at a non-empty directory get the first child

                    o
              .. ---+---+
                        |
               ....    [o]
                     +--+--+
             ......  |  |  |
                     @  @  @
                           ^

        * start at an empty directory gets the first child in its sibling

                    o
              .. ---+---+-----+  
                        |     |  
               ....     o    [o]  
                     +--+--+
             ......  |  |  |
                     @  @  @
                           ^

        * trivial (most common) case: a file that has a sibling file

                    o
              .. ---+---+---
                        |  
               ....     o      ....
                     +--+--+
             ......  |  |  |
                     @ [@] @
                           ^
        * last file in a last dir but not the very last

                    o                  
               +----+-------------+              
               o                  o              
            ---+--+            +--+---        
    ....          o            o         ....    
               +--+--+      +--+--+              
    .....      |  |  |      |  |  |     .......
               @  @  @     [@] @  @              
                     ^                          

"""

def step(tree, node, dir='next'):
    """Make a step in the tree, starting from node, in direction
    @param tree: an object conforming to ITree, must be knowledgable about the given node
    @param node: an object conforming to INode, the underlying node it represents must be logically a part of the tree
    @param dir: a string, 'next' or 'prev', also accepts:
        1, 'forward', 'for': interpreted as next
        -1, 'backward', 'backwards', 'back', 'previous': interpreted as 'prev'

    @returns: the next file node in the tree
    @note: walking the files on the tree can be done by stepping continuously
        e.g.:
            # walk starting from root
            node = tree.root_node
            while node is not None:
                # do something with node
                node = step(tree, node, 'next')
    """
    if dir in ('next', 'forward', 'for', 1):
        get_sibling = tree.sibling_next
        first_item = lambda list: list[0]
    elif dir in ('prev', 'previous', 'backwards', 'backward', 'back', -1):
        get_sibling = tree.sibling_prev
        first_item = lambda list: list[-1] # last item!
    else:
        raise ValueException("given value for `dir` is invalid")

    def start_from(node):
        sibling = get_sibling(node)
        if sibling is not None: # happy case
            return handle_sibling_exists(sibling)
        else: # sibling is none .. not so happy
            return handle_sibling_is_none(node) # difficult case

    def handle_sibling_exists(sibling):
        if sibling.isfile: # happy case
            return sibling
        else: # directory: recurse and step starting from the directory
            return step(tree, sibling, dir)

    def handle_sibling_is_none(node):
        assert get_sibling(node) is None
        root = tree.root
        while True:
            node = tree.parent(node)
            if node is root: break
            sibling = get_sibling(node)
            if sibling is not None:
                return handle_sibling_exists(sibling)
        # we reached the very end! that's it
        return None

    if node.isfile:
        return start_from(node)
    else: # node.isdir
        if node.ls: # non-empty directory
            first_child = first_item(node.ls)
            if first_child.isfile:
                return first_child
            else: # also a directory? recurse
                return step(tree, first_child, dir) # start from first child
        else: # empty directory
            return start_from(node)

