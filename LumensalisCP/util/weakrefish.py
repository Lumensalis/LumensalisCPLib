try:
    from weakref import *
except:
    class ref(object):
        def __init__(self, target:object ):
            self.__referenced = target
            
        def __call__(self) -> object|None:
            return self.__referenced