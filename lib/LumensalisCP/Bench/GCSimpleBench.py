

import supervisor, gc, time, sys
from __future__ import annotations
try:
    from typing import List, Callable, TextIO, Any 
except:
    
    Callable = None
    TextIO = None
    Any = None
    #List = None
    
#############################################################################

from .WriteScope import *

#############################################################################

class GCTestAllocScopeSample(object):
    mem_alloc: int
    mem_free: int
    when: float
    
    def __init__(self, copy:GCTestAllocScopeSample|None = None ):
        if copy is None:
            self.clear()
        else:
            self.mem_alloc = copy.mem_alloc
            self.mem_free = copy.mem_free
            self.when = copy.when

    def __repr__(self):
        if self.mem_alloc == -self.mem_free:
            return f"({self.mem_alloc},{self.when:0.3f})"
        return f"\{a={self.mem_alloc}, f={self.mem_free}, t={self.when:0.3f}}"


    def writeOnScope(self, writeScope:WriteScope ):
        if self.mem_alloc == -self.mem_free:
            writeScope.addDict( dict( used=self.mem_alloc, e=self.when), indentItems=False )
        else:
            writeScope.addDict( dict( used=self.mem_alloc, f=self.mem_free, e=self.when), indentItems=False ) 
            
    def clear(self):
        self.mem_alloc = 0
        self.mem_free = 0
        self.when = 0.0
        
    def sample(self):
        self.mem_alloc = gc.mem_alloc()
        self.mem_free = gc.mem_free()
        self.when = time.monotonic()
        
    def __sub__(self, rhs:GCTestAllocScopeSample ):
        rv = GCTestAllocScopeSample()
        rv.mem_alloc = self.mem_alloc - rhs.mem_alloc
        rv.mem_free = self.mem_free - rhs.mem_free
        rv.when = self.when - rhs.when
        #print( f"__sub__ {self} - {rhs} = {rv}" )
        return rv
    
    def __add__(self, rhs:GCTestAllocScopeSample ):
        rv = GCTestAllocScopeSample()
        rv.mem_alloc = self.mem_alloc + rhs.mem_alloc
        rv.mem_free = self.mem_free + rhs.mem_free
        rv.when = self.when + rhs.when
        return rv    

    
    def __truediv__(self, rhs:int ):
        rv = GCTestAllocScopeSample()
        rv.mem_alloc = self.mem_alloc / rhs
        rv.mem_free = self.mem_free / rhs
        rv.when = self.when / rhs
        return rv    

#############################################################################

class GCTestAllocScopeData(object):
    before: GCTestAllocScopeSample
    after: GCTestAllocScopeSample
    
    def __repr__(self):
        return f"e:{self.elapsed}"
    
    def __init__(self, copy:GCTestAllocScopeData|None = None ):
        if copy is None:
            self.before = GCTestAllocScopeSample()
            self.after = GCTestAllocScopeSample()
        else:
            self.before = copy.before
            self.after = copy.after
    
    def clear(self):
        self.before.clear()
        self.after.clear()
        
    elapsed = property( lambda self: self.after-self.before )

    def writeOnScope(self, writeScope:WriteScope ):
        writeScope.write( self.elapsed )
                    
class GCTestAllocScope(GCTestAllocScopeData):


    def start(self):
        self.clear()
        self.before.sample()

    def finish(self):
        self.after.sample()
        
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, excT, extV, tb):
        self.finish()

#############################################################################
class GCTestTarget(object):
    def __init__(self, name:str, callable:Callable ):
        self.name = name
        self.target = callable
    
    def invokeWithArgs( self, *args, **kwds ):
        return self.target(*args,**kwds)

    def invoke( self ):
        return self.target()

#############################################################################
        
class GCTestRunConfig(object):
    args:list | None
    kwds:dict | None
    
    def __init__( self, 
                 cycles:int|None=None, innerCycles:int|None=None, 
                 args=None, kwds=None,
                 optimizeArgs:bool = False
                 ):
        self.cycles:int = cycles or 10
        self.innerCycles:int = innerCycles or 1
        self.args = args
        self.kwds = kwds
        self.optimizeArgs = optimizeArgs
    
    @property
    def totalCycles(self) ->int: return self.cycles * self.innerCycles

    def writeOnScope(self, writeScope:WriteScope|None = None):
        with writeScope.startDict(indentItems=False) as nested:
            nested.addTaggedEntries([
                    ('args',self.args),
                    ('kwds',self.kwds),
                ])
                
            nested.addTaggedItems(
                c=self.cycles,
                ic=self.innerCycles,
                optimizeArgs=self.optimizeArgs
             )
    
    def __repr__(self):
        return f"(args={self.args} kwds={self.kwds} c={self.cycles} ic={self.innerCycles} optimizeArgs={self.optimizeArgs} )"
    
    def invoke(self, target:GCTestTarget ):
        if self.args is None:
            if self.kwds is None:
                return target.invoke()
            else:
                return target.invokeWithArgs( **self.kwds )
        else:
            if self.kwds is None:
                if self.optimizeArgs: 
                    argCount = len(self.args)
                    if argCount == 1: 
                        return target.target( self.args[0] )
                    elif argCount == 2: 
                        return target.target( self.args[0], self.args[1] )
                    elif argCount == 3: 
                        return target.target( self.args[0], self.args[1], self.args[2] )
                    return target.target( *self.args )
                    
                return target.invokeWithArgs( *self.args)
            else:
                return target.invokeWithArgs( *self.args, **self.kwds )


class GCTestRunResultScope(object):
    def __init__(self, config:GCTestRunConfig):
        self.outerScope = GCTestAllocScope()
        self.preCollectScope = GCTestAllocScope()
        self.postCollectScope = GCTestAllocScope()
        self.config = config

    def run(self, config:GCTestRunConfig ):
        assert self.config is config
        with self.preCollectScope:
            gc.collect()
        with self.outerScope:
            rv = self.runInternal(config)
        with self.postCollectScope:
            gc.collect()            
        return rv
            
    def runInternal(self, config:GCTestRunConfig ):
        raise NotImplemented

class GCTestRunResult(GCTestRunResultScope):
    target:GCTestTarget
    name:str
    exc:Exception
    
    def __init__(self, target:GCTestTarget, config:GCTestRunConfig):
        super().__init__(config)
        self.target = target
        self.exc = None
        assert type(target.name) is str
        self.scopes = [GCTestAllocScope() for _ in range(config.cycles)]
        
    name = property( lambda self: self.target.name )
    
    def runInternal(self, config:GCTestRunConfig ):
        if config.innerCycles == 1:
            for scope in self.scopes:
                with scope:
                    config.invoke(self.target)
        else:
            for scope in self.scopes:
                with scope:
                    for x in range( config.innerCycles ):
                        config.invoke(self.target)

    def writeOnScope(self, writeScope:WriteScope ):
        total = GCTestAllocScopeSample()
        with writeScope.startDict(indentItems=False) as selfWriteScope:
            if self.exc is not None:
                selfWriteScope.addTaggedItem('exc',repr(self.exc))    
                return 
            for scope in self.scopes:
                total = total + scope.elapsed
                
            selfWriteScope.addTaggedItem('per',total/self.config.totalCycles)
            selfWriteScope.addTaggedItem('totalCycles', self.config.totalCycles)
            if writeScope.config.detailed:
                selfWriteScope.addTaggedEntries([
                    ('outer',self.outerScope.elapsed),
                    ('total',total),
                    ])
                          
                selfWriteScope.addTaggedItems( name=self.target.name, 
                            preGC=self.preCollectScope.elapsed,
                            postGC=self.postCollectScope.elapsed
                        )
        if writeScope.showScopes:
            selfWriteScope.addList( self.scopes, "scopes" )

class GCTestRunResults(GCTestRunResultScope):
    results:List[GCTestRunResult]
        
    def __init__(self, targets, config:GCTestRunConfig ):
        super().__init__(config)
        self.results = []
        for target in targets:
            self.results.append( GCTestRunResult(target, config) )

    def runInternal(self, config:GCTestRunConfig ):
        for result in self.results:
            try:
                result.run(config)
            except (Exception,TypeError) as inst:
                result.exc = inst

    def writeOnScope(self, writeScope:WriteScope|None = None):
        writeScope = TargettedWriteScope.makeScope(writeScope)

        with writeScope.startDict(indentItems=True) as resultsScope:
            resultsScope.addTaggedItem( "config", self.config )
            total = GCTestAllocScopeSample()
            with resultsScope.startDict("results",indentItems=True) as resultScope:
                for result in self.results:
                    if result.exc is None:
                        resultScope.addTaggedItem( result.name, result )
                        total = total + result.outerScope.elapsed
                    
            if resultsScope.config.detailed:
                resultsScope.addTaggedItems( outer=self.outerScope.elapsed,
                                        total=total,
                                        preGC=self.preCollectScope.elapsed,
                                        postGC=self.postCollectScope.elapsed
                                        ) 

        
#############################################################################
import re
_fNameRe = re.compile( r'^<function (.*) at [0-9a-fA-FxX]+>$' ) 
def _getName( f ):
    fn = getattr( f, '__name__', None )
    #print( f"f={f} fn={fn}" )
    fcls = getattr( f, '__class__',None )
    if fn is not None:
        #if fcls is not None:
        #    print( f"fcls={fcls} d={dir(fcls)} {fcls.__class__} {fcls.__dict__} {fcls.__bases__}")
        #    return fcls.__name__ + "." + fn
        return fn
    fr = repr(f)
    m = _fNameRe.match(fr)
    if m:
        return m.group(1)

    fcn = getattr( fcls, '__name__', None )
    print( f"f is a {type(f)} : {f}  df={dir(f)} fcn={fcn} fn={fn}" )
    return fr

class GCTester(object):
    targets:list[GCTestTarget] 
    
    def __init__(self, baseline:Callable|None = None):
        self.targets = [GCTestTarget("baseline", baseline or (lambda *args,**kwds:None) )]
    
    def addTests( self, *args, **kwds ):
        for test in args:
            self.targets.append( GCTestTarget(_getName(test),test) )
        for tag,val in kwds.items():
            self.targets.append( GCTestTarget(tag,val) )
            
    def run( self, cycles:int|GCTestRunConfig|None = None, innerCycles:int|None = None, config:GCTestRunConfig|None = None ):
        
        if isinstance(cycles,GCTestRunConfig):
            assert( config is None )
            config = cycles
            cycles = None
            
        if config is None:
            config = GCTestRunConfig( cycles=cycles, innerCycles=innerCycles )
        else:
            assert cycles is None
            assert innerCycles is None
        results = GCTestRunResults( self.targets, config )
        results.run(config)
        return results

#############################################################################
