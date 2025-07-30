from __future__ import annotations

import gc # type: ignore[reportUnusedImport]
import time, sys # type: ignore[reportUnusedImport]
import supervisor # type: ignore[reportUnusedImport]

class mutableObject(object):
    def __init__(self,**kwds:StrAnyDict) -> None:
        for tag,val in kwds.items():
            setattr(self, tag, val)

if True:
    from LumensalisCP.CPTyping import *
else:
            
    try:
        
        from typing import List, Sequence, Tuple, Mapping
        from typing import Callable, TextIO, Any,  Optional, Self
        import weakref
        
        
        class PseudoTypingExpression(object): # type: ignore
            def __init__(self,*args,**kwds):
                raise NotImplementedError    
        
        class PseudoTypingType(object):
            def __init__(self,*args,**kwds): 
                raise NotImplementedError
            
        def makeTypingExpression( a ):  # type: ignore
            return a

    except ImportError:
        
        class PseudoTypingExpression(object):
            _typeCache = {}
            @staticmethod
            def makeExpression( arg ):
                if isinstance( arg, PseudoTypingExpression ):
                    return arg
                cached = PseudoTypingExpression._typeCache.get(arg,None)
                if cached is not None:
                    return cached
                aType = type(arg)
                if aType is type(object):
                    #print( f"adding class {arg} to cache" )
                    wrapper = PseudoTypingClass(arg)
                    PseudoTypingExpression._typeCache[arg] = wrapper
                    return wrapper
                    
                return arg
            
            @staticmethod
            def _addPods():
                for pod in [  int, float, bool, None, str ]:
                    pt = PseudoTypingPOD( pod )
                    PseudoTypingExpression._typeCache[pod] = pt
                    
            def __or__(self, nextValue ):
                return PseudoTypingUnion( self, nextValue )

        
        class PseudoTypingUnion(PseudoTypingExpression):
            def __init__(self, a, b ):
                super().__init__()
                self.types = []
                self.add(a)
                self.add(b)
                
            def add(self, t ):
                if isinstance( t, PseudoTypingUnion ):
                    self.types.extend(t.types)
                else:
                    self.types.append( self.makeExpression(t))


        class PseudoTypingBracketExpression(PseudoTypingExpression):
            
            def __init__(self, root, args):
                super().__init__()
                self.root = root
                self.args = self.makeExpression( args )
            


        class PseudoTypingBracketableMixin(object):
            
                
            def __getitem__(self, innards ):
                return PseudoTypingBracketExpression( self, innards )

        class PseudoTypingTType(PseudoTypingExpression):
            def __init__(self,name):
                super().__init__()
                self.name = name

        class PseudoTypingPOD(PseudoTypingTType):
            def __init__( self, t ):
                super().__init__( str(t) )
                self.t = t
                
        class PseudoTypingClass(PseudoTypingTType):
            def __init__( self, cls ):
                super().__init__( cls.__name__ )
                self.cls = cls


        class PseudoTypingTBType(PseudoTypingTType,PseudoTypingBracketableMixin):
            pass

        
        Callable = PseudoTypingTBType("Callable")
        TextIO = PseudoTypingTType("TextIO")
        Any = PseudoTypingTType("Any")
        Self = PseudoTypingTType("Self")
        Tuple = PseudoTypingTBType("Tuple")
        List = PseudoTypingTBType("List")
        Mapping = PseudoTypingTBType("Mapping")
        
        
        def makeTypingExpression( a ) -> PseudoTypingExpression:
            return PseudoTypingExpression.makeExpression(a)


    try:
        import weakref
    except ImportError:
        class weakref_ref(object):
            def __init__(self, target:object ):
                self.__referenced = target
                
            def __call__(self) -> object|None:
                return self.__referenced
        
        weakref = mutableObject( ref = weakref_ref)
