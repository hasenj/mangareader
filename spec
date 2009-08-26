        MANGA READER APPLICATION

Goal:
    To create a simple and effecient application for reading manga
    Effeciency in both performance and user interaction.

Description:
    The program will read a directory that contains a specific manga
    within it. This manga can be split into multiple directories, so 
    the application must read images in this directory and all its
    subdirectories recursively.

    Images will be presented as a vertical filmstrip where the user
    reads by scrolling down (and up); much like reading a pdf document.

    The application will feature some concepts from vim, such as keyboard
    interaction and a command bar.
    
    Main features should be accessible both through keyboard commands and
    graphical elements, such as drop boxes, sliders, etc.

Minimum Requirements:
    * Read (and display) images recursively from a manga directory. [done]
        * Must be lazy; don't read entire directory tree at once. [done]
    * Scroll up/down using k/j keys and mouse wheel. [done]
    * Open a command bar when user hits : key.
    * Jump to a certain chapter, or volume/chapter, by number. 

Medium Level Requirements:    
    * Set width (of film strip) using percentage or pixel values. Also provide a GUI slider for it.
    * Save/load manga information, such as manga folder and where the user was last time.
    * Implement bookmarks: allow the user to bookmark a location and jump to it later.

    
