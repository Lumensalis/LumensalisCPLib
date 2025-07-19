
_weakrefImported = False
try:
    from weakref import ref, ReferenceType
    _weakrefImported = True
    lcpfRef = ref
except:
    _standardWeakref = None
    #from LumensalisCP.CPTyping import ReferenceType
    ReferenceType = None
    class _ref(object):
        def __init__(self, target:object ):
            self.__referenced = target
            
        def __call__(self) -> object|None:
            return self.__referenced
    ref = _ref        
    lcpfRef = _ref 

__all__ = ['ref','ReferenceType', 'lcpfRef']