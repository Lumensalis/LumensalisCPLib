from LumensalisCP.CPTyping import *
import re

#############################################################################

class KWCallback(object):
    """wrapper for a callable, allowing it  be invoked safely(ish) with more 
    positional and/or named parameters than expect.  Extra parameters will
    be silently discarded instead of raising an exception.
    
    This is not terribly efficient. It has a small risk of unexpected side 
    effects.  It is (IMHO) a
    rather inelegant hack.  It provides a workaround for a limitation 
    in CircuitPython / MicroPython - there is no way to determine what
    arguments are recognized (normally you could use inspect.signature(...) ).
    
    Each instance tracks the maximum allowed number of unnamed arguments, 
    as well as the names of unrecognized named arguments.  When invoking the 
    callback, positional arguments beyond the maximum allowed and known 
    unrecognized names are removed before invoking the wrapped callback.
    
    When an invocation triggers an "unexpected argument" exception, the
    position (for unnamed args) or name (for named args) is stored and 
    the callback is re-invoked until it succeeds or throws an exception 
    other than those used for unexpected arguments.   
    
    WARNING: if the state of anything changes - including 
    the state of any arguments between the nested invocation and the 
    catching of the argument exception prior to updating this instance's 
    max allowed / name blacklist and re-invocation, it could cause some
    rather strange and unexpected behavior.  This is probably not likely to
    occur without some twisted code (like explicitly throwing a TypeError 
    with a very similar message), but...
    """
    requiredKwds = None
    
    @classmethod
    def make( cls, cb:Callable, **kwds ):
        if isinstance( cb, cls ): return cb
        return cls( cb, **kwds )
        
    def __init__( self, cb:Callable, name:str|None = None, requiredKwds:List[str]|None = None ):
        self.__cb = cb
        self.__name = name or getattr(cb,'__name__', repr(cb) )
        
        if requiredKwds is not None:  # otherwise will use class level
            self.requiredKwds = requiredKwds
            
        self.__skippedKwds = {}
        self.__maxPositionals = None
    
    __ukaPre = "unexpected keyword argument '"
    __ukaPreLen = len(__ukaPre)
    __uka = re.compile( "unexpected keyword argument '(.*)'$" )
    __positionalArgs = re.compile( '^function takes (\d+) positional arguments but (\d+) were given$' )
    __missingArg = re.compile( '^function missing required positional argument #(\d+)$' )
    
    def __repr__(self):
        return f"{self.__name}[:{self.__maxPositionals}]!{self.__skippedKwds}"
    
    def __call__( self, *args, **kwds ):
        for k in self.__skippedKwds:
            if k in kwds:
                del kwds[k]
            
        if self.__maxPositionals is not None and len(args) > self.__maxPositionals:
            args = args[0:self.__maxPositionals]
        try:
            return self.__cb( *args, **kwds )
        except TypeError as inst:
            asStr = str(inst)
            kwdName = None
            if m := self.__uka.match( asStr ):
                kwdName = m.group(1)
                assert kwdName not in self.__skippedKwds
                if self.requiredKwds is not None and kwdName in self.requiredKwds:
                    raise TypeError( "keyword argument %r is required" % kwdName )
                self.__skippedKwds[kwdName] = 1
                # print(f"added kwdName = {kwdName}")
            elif m := self.__positionalArgs.match( asStr ):
                expected = int( m.group(1) )
                given = int( m.group(2) )
                if given > expected:
                    self.__maxPositionals = expected
                else:
                    raise
            elif asStr[0:self.__ukaPreLen] == self.__ukaPre:
                assert( asStr[-1:] == "'" )
                kwdName = asStr[self.__ukaPreLen:-1]
            else:
                # print( f"inst is {type(inst)} : {inst}")
                raise
        return self( *args,**kwds )
        