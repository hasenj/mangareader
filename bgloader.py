'''
    Author: Hasen il Judy
    License: GPLv2

    Loads image files in a background thread

    Actually, this module provides a facility to queue a list of functions to be performed
    by some specific (named) thread. Right now though, we only use one thread: the image loading thread

'''
import thread, time
class RunnerQueue(object):
    """A thread that queues functions for running. functions must be short/not take a long time"""
    def __init__(self, name):
        self.name = name
        self.list = []
        self.list_lock = thread.allocate_lock()
        self.thread = thread.start_new_thread(self.run, ())
    def push(self, target):
        with self.list_lock:
            self.list.append(target)
    def run(self):
        """
            This function runs in its own thread!
        """
        while True:
            while len(self.list) == 0:
                time.sleep(0.2) # number is in seconds
            with self.list_lock:
                target = self.list.pop(0)
            target()

threads = {}
def queue_function_in_thread(target, name):
    """
        Put a function in the queue of a named thread.
        Right now we only use the image_loader thread, 
        but it sounds useful to generalize it a bit since it doesn't cost much at all

        @param target: function to run inside thread
        @param name: the name of the thread 
    """
    if not threads.has_key(name):
        threads[name] = RunnerQueue(name)
    threads[name].push(target)


def queue_image_loader(loader):
    queue_function_in_thread(loader, "image_loader")


