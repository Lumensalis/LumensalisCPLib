from __future__ import annotations

try:
	# imports used only for typing
    #import overrides
    from typing import Any
    from typing import List,  Tuple, Sequence
    from typing import Generator, Iterable, Iterator
    from typing import Dict, Mapping, MutableMapping
    from typing import IO, TextIO
    from typing import Callable
    from typing import Union, ForwardRef, Required, NotRequired, Optional
    from typing import Unpack, TypeAlias 
    from typing import Self 
    from typing import Type, TypeAlias, TypedDict, TypeVar
    from typing import NoReturn
    
    from typing import final, overload, override
    
    from functools import wraps
    
    
    # any imports below this won't happen if the error gets raised
    LCPF_TYPING_IMPORTED = True
    
    class PseudoTypingExpression(object): # type: ignore
        def __init__(self,*args,**kwds):
            raise NotImplementedError    
    
    class PseudoTypingType(object):
        def __init__(self,*args,**kwds):
            raise NotImplementedError
        
    def makeTypingExpression( a ): # type: ignore
        return a
    
    from weakref import ReferenceType

except ImportError:
    LCPF_TYPING_IMPORTED = False
    TYPE_CHECKING = False
    if not TYPE_CHECKING:
        
        class PseudoTypingExpression(object):
            _typeCache = {}
            @staticmethod
            def makeExpression( arg ):
                if isinstance( arg, PseudoTypingExpression ):
                    return arg
                cached = PseudoTypingExpression._typeCache.get(arg,None)
                if cached is not None:
                    return cached
                argType = type(arg)
                if argType is type(object):
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

        class PseudoTypingBracketableExpression(PseudoTypingExpression,PseudoTypingBracketableMixin):
            pass

        class PseudoTypingModifier(PseudoTypingBracketableExpression):
            def __init__(self,name):
                super().__init__()
                self.name = name
            
        Any = PseudoTypingTType("Any")
        NoReturn = PseudoTypingTType("NoReturn")
        TextIO = PseudoTypingTType("TextIO")
        Self = PseudoTypingTType("Self")
        
        Callable = PseudoTypingTBType("Callable")
        Tuple = PseudoTypingTBType("Tuple")
        Mapping = PseudoTypingTBType("Mapping")
        List = PseudoTypingTBType("List")
        Tuple = PseudoTypingTBType("Tuple")
        Dict = PseudoTypingTBType("Dict")
        Mapping = PseudoTypingTBType("Mapping")
        Generator =  PseudoTypingTBType("Generator")
        Iterable = PseudoTypingTBType("Iterable")
        
        
        Union = PseudoTypingModifier("Union")
        ForwardRef = PseudoTypingModifier("ForwardRef")
        Required = PseudoTypingModifier("Required")
        NotRequired = PseudoTypingModifier("NotRequired")
        Optional = PseudoTypingModifier("Optional")
        ReferenceType = PseudoTypingModifier("ReferenceType")
        Unpack = PseudoTypingModifier("Unpack")
        
        def makeTypingExpression( a ) -> PseudoTypingExpression:
            return PseudoTypingExpression.makeExpression(a)

        

        
        class __TDM(object):
            def __new__(cls, name, bases, ns, total=True):
                pass
        
        #def TypedDict(typename, *args, fields=None, total=True, **kwargs):
        #    return __TDM
        
        #_TypedDict = type.__new__(__TDM, 'TypedDict', (), {})
        #TypedDict.__mro_entries__ = lambda bases: (_TypedDict,)
        #TypedDict.__mro_entries__ = lambda bases: ()

        class TypedDict(object):
            pass
        
        
        def overload( f ): return f
        def override( f ): return f
        def final( f ): return f
        def wraps( f ): return f


if LCPF_TYPING_IMPORTED:
    # this is _not_ within the initial try/except because we do
    # _not_ want to silently ignore errors
    raise NotImplementedError
