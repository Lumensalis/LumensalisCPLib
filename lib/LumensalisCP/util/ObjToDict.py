
try:
    from typing import Any
except ImportError: 
    pass

def objectToVal( obj:Any ) -> Any:
    if isinstance(obj, (str,bool,int,float,type(None))): return obj
    if isinstance(obj, (list, tuple)): return [objectToVal(v) for v in obj]
    if isinstance(obj, dict):
        rv:dict[str,Any] = {}
        for k, v in obj.items():
            if k.startswith('_'): continue
            rv[k] = objectToVal(v)
        return rv   
    if isinstance(obj, set): return [objectToVal(v) for v in obj]
    if isinstance(obj, type ): return repr(obj)

    rv:dict[str,Any] = {} # type: ignore
    typeName =obj.__class__.__name__
    for tag in dir(obj):
        if tag.startswith('_'): continue
        val = objectToVal( getattr(obj, tag) )
        #if callable(val) or: continue
        if obj.__class__.__name__ in ('function',): continue
        rv[tag] = val

    rv['_type'] = typeName
    return rv

def objectToDict( obj:Any ) -> dict[str,Any]|str:
    if isinstance(obj, dict): return {k: objectToDict(v) for k, v in obj.items()}
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