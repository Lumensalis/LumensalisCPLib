try:
    from typing import Any
except ImportError: 
    pass

def objectToDict( obj:Any ) -> dict[str,Any]|str:
    rv:dict[str,Any] = {} # type: ignore
    skip = []
    #if hasattr(obj, '__class__'):
    #    skip = dir(obj.__class__)
    for tag in dir(obj):
        if tag.startswith('_'): continue
        if tag in skip: continue
        val = getattr(obj, tag)
        if val is obj: continue
        if type(val) is type(obj): continue
        if isinstance(val,type): continue
        if callable(val): continue
        #print( f"  ...{tag}=({type(val)}) {val}" )
        if isinstance(val, (int, float, str, bool)): pass
        elif isinstance(val, (bytes, bytearray)): val = repr(val)
        else: val = objectToDict(val)
        rv[tag] = val
    if len(rv) == 0:
        return repr(obj)
    return rv