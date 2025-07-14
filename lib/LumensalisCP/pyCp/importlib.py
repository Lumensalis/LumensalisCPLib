import sys
import supervisor

def reload( module, verbose=False ) -> None:
    """CircuitPython specific implementation of [importlib.reload](https://docs.python.org/3/library/importlib.html#importlib.reload)

This is intended to be functionally equivalent with **importlib.reload** 
for the purposes of CircuitPython.  It is _far_ simpler, because the
CircuitPython system for loading python modules is far less complex
than CPython's.

    :param module: The module to reload
    :param verbose: enable diagnostic print(...) calls, defaults to False
    :type verbose: bool, optional
    """
    if supervisor.runtime.autoreload:
        # makes no sense to actually reload, because the source file 
        # has not changed (otherwise autoreload would have restarted 
        # everything)
        if verbose: 
            print( f"skipping reload of module {module}, autoreload enabled" )
        return

    if verbose: 
        print( f"reloading module {module}")

    name = module.__name__
    # at this point, `del sys.modules[name]` followed by `__import__( name )`
    # would "work", but only for extremely trivial cases.  It fails to 
    # replicate some very important parts of **importlib.reload** behavior.
    # The most serious problem is that sys.modules[name] will now contain 
    # a _new_ instance, and any non-nested existing imports will still 
    # reference the old module (unless they are themselves reloaded afterwords)
    
    # This is why we have to go through the extra work of setting up
    # a custom global dict from the current module, `exec`ing the code,
    # and replacing the globals in the existing module - that makes things
    # work "properly" (i.e. similar to **importlib.reload**)

    # the target module __must__ already be imported and in sys.modules
    existingModule = sys.modules[name]
    assert sys.modules[name] == existingModule
    
    #########################################################################
    # extract attributes 
    # we make two copies (shallow copy won't work) to allow for 
    # detecting what actually changes. Preloading **newAttrs** also
    # preserves **import.reload** functionality when module code checks
    # its own globals to avoid "overwriting" things like singleton instances
    newAttrs = {}
    priorAttrs = {}
    for key in dir(existingModule):
        val = getattr( existingModule, key )
        newAttrs[key] = val
        priorAttrs[key] = val
    
    #########################################################################
    # now we load and **exec** the source for the module
    if verbose: print( f"newAttrs : {newAttrs.keys()}")
    with open(module.__file__,'r') as f:
        source = f.read()
        exec( source, newAttrs, newAttrs )

    #########################################################################
    # since **newAttrs** was used for globals in the `exec(...)` call
    # everything that was parsed/loaded from that source was stored 
    # in **newAttrs**.   We can now go update the _existing_ 
    # instance of the module with any changes.  
    for key,val in newAttrs.items():
        prior = priorAttrs.get(key,None)
        if val is prior:
            #if verbose: print( f"reload {name} : skipping exact {key}")
            continue

        if val == prior:
            if verbose: print( f"reload {name} : skipping equal {key}")
            continue
        if verbose: print( f"reload {name} : updating {key}")
        setattr( existingModule, key, val )
        
    #########################################################################
    # new code should now be "reloaded" into **module**