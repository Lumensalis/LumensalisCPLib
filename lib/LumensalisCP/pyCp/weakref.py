_weakrefImported = False
try:
    from weakref import ref, ReferenceType
    _weakrefImported = True
except:
    if not _weakrefImported:
        from ..CPTyping import ReferenceType
        class _ref(object):
            def __init__(self, target:object ):
                self.__referenced = target
                
            def __call__(self) -> object|None:
                return self.__referenced
            
        def ref(a): return _ref(a)
