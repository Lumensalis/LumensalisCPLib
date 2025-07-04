import sys

def reload( module ):
    name = module.__name__
    existingModule = sys.modules[name]
    assert sys.modules[name] == existingModule

    existingAttrs = {}
    for key in dir(existingModule):
        existingAttrs[key] = getattr( existingModule, key )
    
    with open(module.__file__,'r') as f:
        source = f.read()
        exec( source, existingAttrs, existingAttrs )
    for key,val in existingAttrs.items():
        setattr( existingModule, key, val )