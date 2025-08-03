
_weakrefImported = False
try:
    from weakref import ref, ReferenceType
    _weakrefImported = True
    lcpfRef = ref
except:
    _standardWeakref = None
    #from LumensalisCP.CPTyping import ReferenceType
    from LumensalisCP.util.CountedInstance import CountedInstance

    ReferenceType = None
    class _ref(CountedInstance):
        def __init__(self, target:object ):
            super().__init__()
            self.__referenced = target
            
        def __call__(self) -> object|None:
            return self.__referenced
    ref = _ref        
    lcpfRef = _ref 

__all__ = ['ref','ReferenceType', 'lcpfRef']