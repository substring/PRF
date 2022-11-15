import os

def list_subfolders(path):
    """
    Inspired from https://stackoverflow.com/a/49890887
    """
    filenames = os.listdir ("./" + path) # get all files' and folders' names in the current directory

    result = []
    for filename in filenames: # loop through all the files and folders
        if os.path.isdir(os.path.join(os.path.abspath("./" + path), filename)): # check whether the current object is a folder or not
            result.append(filename)
    return result
    #return next(os.walk(path))[1]

def loadModule(mod, extlib_folder):
    """
    First add to the path the extlib/* subfolders, then look there
    """
    try:
        # from pyrominfo import gameboy, etc
        subdirs = list_subfolders('extlibs')
        os.sys.path.insert(0, '/'.join(('extlibs', extlib_folder)))
        extlib = __import__(extlib_folder, globals(), locals(), [mod])
    except ImportError:
        raise ImportError("loadModule() can't find module %s" % mod)
    try:
        return getattr(extlib, mod)
    except AttributeError:
        raise ImportError("testutils.loadModule() can't find module %s in pyrominfo package" % mod)
