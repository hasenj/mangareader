"""
    Author: Hasen el Judy
    License: GPL v2

    High Level scrolling logic
"""    

class ViewSettings(object):
    """ View settings hold information such as:
        zooming level
        max width
        .. etc ..
    """
    def __init__(self, zoom_level, max_width):
        self.zoom_level = zoom_level
        self.max_width = max_width

class IPage(object):
    """dummy class -- serves only as a documentation"""
    def get_height(self, view_settings):
        """ Calculate what the height of the image would be according to the given 
            ViewSettings
        """
        raise NotImplemented
    def is_loaded(self):
        """ Is the page loaded and ready for display? """
        raise NotImplemented

class IPageList(object):
    """ Interface for a partial view on a (potentially very huge) list of pages
    """
    def page_at(self, index):
        """ Index function
            @returns an IPage object
        """
        raise NotImplemented
    def reset_window(self, index):
        """ Load/Unload pages as needed, around `index`
            Returns the new index of the object that index was pointing to
        """
        raise NotImplemented
    def length(self):
        """ Length of the current view-list """
        raise NotImplemented

def get_loaded_context(list, index):
    """ Get a sub list of pages that are loaded and reachable from index, 
        where reachable means all items between it and the item and index 
        are also loaded

        @returns: (offset, list)
            where offset is the index of the first item of the list
            list is a list of the loaded pages
    """
    result = []
    for i in range(index, len(page_list)):
        page = page_list.page_it(i)
        if not page.is_loaded(): break
        result += page
    offset = index
    for i in range(index-1,-1,-1): # items before current index, in reverse
        page = page_list.page_it(i)
        if not page.is_loaded(): break
        offset = i
        result = [page] + result
    return offset, result

def is_page_available(page_list, index):
    return 0 <= index < page_list.length() and page_list.page_at(index).is_loaded()

class PageCursor(object):
    """
        A cursor/pointer/marker to where we are on a page list
    """
    def __init__(self, page_list, view_settings, index=0):
        self.view_settings = view_settings
        self.page_list = page_list
        self.index = index
        self.pixel = 0

    def move_cursor(self, amount):
        """ Move the cursor `amount` pixels, where amount can be positive or 
            negative (for moving backward).
            The amount can be more than what's actually available to move on, 
            The actual amount moved will be returned

            @returns: the amount of pixels actually moved
        """
        amount_moved = self._move_cursor(amount) 
        self.index = self.page_list.reset_index(self.index)
        return amount_moved

    def _move_cursor(self, amount):
        """ Get a list of heights and use that as a basis for moving.

            We consider the pixel position to be local if it's bound to 
            particular index. A global position is one that's not bount to a
            specific index, but relative to the whole list.
            We use a method to translate (local,index)<->global position, so
            moving the cursor is simply a matter of seeing the max available
            space to move across, doing the move globally, then translating
            it to local coordinates again
        """
        first_index, loaded_context = get_loaded_context(self.page_list, self.index)
        heights = (page.get_height(self.view_settings) 
                for page in loaded_context)

        def minmax(low, val, max):
            if low > val:
                return low
            if max < val:
                return max
            return val

        heights = HeightList(heights)

        local_index = self.index - first_index
        local_pixel = self.pixel
        global_pixel = heights.local_to_global(local_index, local_pixel)
        moved_global_pixel = minmax(0, global_pixel+amount, heights.max())
        amount_moved = moved_global_pixel - global_pixel
        local_index, local_pixel = heights.global_to_local(moved_global_pixel)

        # apply the results of the calculations
        self.index = first_index + local_index 
        self.pixel = pixel
        return amount_moved

class HeightList(object):
    def __init__(self, heights):
        self.heights = heights
    def local_to_global(self, lindex, lpixel):
        return sum(self.heights[:lindex]) + lpixel
    def global_to_local(self, pixel):
        sum = 0
        for i, h in enumerate(self.heights):
            if sum + h > pixel: # this is it!
                return i, pixel-sum
            sum += h
    def max(self):
        return sum(self.heights)-1

