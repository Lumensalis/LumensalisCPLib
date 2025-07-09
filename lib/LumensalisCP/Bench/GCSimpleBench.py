

#############################################################################

from .simpleCommon import *


from .WriteScope import *

#############################################################################

class GCTestAllocScopeSample(object):
    mem_alloc: int
    mem_free: int
    when: float
    
    def __init__(self, copy:"GCTestAllocScopeSample"|None = None ):
        if copy is None:
            self.clear()
        else:
            self.mem_alloc = copy.mem_alloc
            self.mem_free = copy.mem_free
            self.when = copy.when

    def __repr__(self):
        if self.mem_alloc == -self.mem_free:
            return f"({self.mem_alloc},{self.when:0.3f})"
        return f"(a={self.mem_alloc}, f={self.mem_free}, t={self.when:0.3f})"


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
        
    def __sub__(self, rhs:"GCTestAllocScopeSample" ):
        rv = GCTestAllocScopeSample()
        rv.mem_alloc = self.mem_alloc - rhs.mem_alloc
        rv.mem_free = self.mem_free - rhs.mem_free
        rv.when = self.when - rhs.when
        #print( f"__sub__ {self} - {rhs} = {rv}" )
        return rv
    
    def __add__(self, rhs:"GCTestAllocScopeSample" ):
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
class GCTesterTestParameters(object):
    def __init__( self, name, args, kwds ):
        self.args = args
        optimizeArgs = None if kwds is None else kwds.pop('optimizeArgs',None)
        self.kwds = kwds
        self.name = name
        self.optimizeArgs = optimizeArgs
    
    @staticmethod
    def make( name:str, *args, **kwds ):
        
        if len(args) == 1 and len(kwds) == 0 and isinstance(args[0],GCTesterTestParameters):
            return args[0]
        if len(args) == 0: args = None
        if len(kwds) == 0: kwds = None
        
        return GCTesterTestParameters( name, args, kwds )

    def writeOnScope(self, writeScope:WriteScope|None = None):
        with writeScope.startDict(indentItems=False) as nested:
            nested.addTaggedItems( name=self.name, args=self.args, kwds=self.kwds )
            
#############################################################################
        
        
class GCTestAllocScopeData(object):
    before: GCTestAllocScopeSample
    after: GCTestAllocScopeSample
    
    def __repr__(self):
        return f"e:{self.elapsed}"
    
    def __init__(self, copy:"GCTestAllocScopeData"|None = None ):
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
    #args:list | None
    #kwds:dict | None
    
    def __init__( self, 
                 cycles:int|None=None, innerCycles:int|None=None, 
                 #args=None, kwds=None,
                 optimizeArgs:bool = False
                 ):
        self.cycles:int = cycles or 5
        self.innerCycles:int = innerCycles or 1
        #self.args = args
        #self.kwds = kwds
        self.optimizeArgs = optimizeArgs
    
    @property
    def totalCycles(self) ->int: return self.cycles * self.innerCycles

    def writeOnScope(self, writeScope:WriteScope|None = None):
        with writeScope.startDict(indentItems=False) as nested:
            #nested.addTaggedEntries([
            #        ('args',self.args),
            #        ('kwds',self.kwds),
            #    ])
                
            nested.addTaggedItems(
                c=self.cycles,
                ic=self.innerCycles,
                optimizeArgs=self.optimizeArgs
             )
    
    def __repr__(self):
        return f"(args={self.args} kwds={self.kwds} c={self.cycles} ic={self.innerCycles} optimizeArgs={self.optimizeArgs} )"
    
    def invoke(self, target:GCTestTarget, testArgs:GCTesterTestParameters ):
        args = testArgs.args
        kwds = testArgs.kwds
        optimizeArgs = self.optimizeArgs if testArgs.optimizeArgs is None else testArgs.optimizeArgs 
        callable = target.target
        if args is None:
            if kwds is None:
                return target.invoke()
            else:
                return target.invokeWithArgs( **kwds )
        else:
            if kwds is None:
                if optimizeArgs: 
                    argCount = len(args)
                    if argCount == 1: 
                        return callable( args[0] )
                    elif argCount == 2: 
                        return callable( args[0], args[1] )
                    elif argCount == 3: 
                        return callable( args[0], args[1], args[2] )
                    return callable( *args )
                    
                return target.invokeWithArgs( *args)
            else:
                return target.invokeWithArgs( *args, **kwds )


class GCTestRunResultScope(object):
    def __init__(self, config:GCTestRunConfig):
        self.outerScope = GCTestAllocScope()
        self.preCollectScope = GCTestAllocScope()
        self.postCollectScope = GCTestAllocScope()
        self.config = config

    def run(self, config:GCTestRunConfig, args:GCTesterTestParameters ):
        assert self.config is config
        with self.preCollectScope:
            gc.collect()
        with self.outerScope:
            rv = self.runInternal(config, args)
        with self.postCollectScope:
            gc.collect()            
        return rv
            
    def runInternal(self, config:GCTestRunConfig, args:GCTesterTestParameters ):
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
    
    def runInternal(self, config:GCTestRunConfig, args:GCTesterTestParameters ):
        if config.innerCycles == 1:
            for scope in self.scopes:
                with scope:
                    config.invoke(self.target, args)
        else:
            for scope in self.scopes:
                with scope:
                    for x in range( config.innerCycles ):
                        config.invoke(self.target, args)

    def writeOnScope(self, writeScope:WriteScope ):
        total = GCTestAllocScopeSample()
        with writeScope.startDict(indentItems=False) as selfWriteScope:
            if self.exc is not None:
                selfWriteScope.addTaggedItem('exc',repr(self.exc))    
                return 
            for scope in self.scopes:
                total = total + scope.elapsed
                
            selfWriteScope.addTaggedItem('per',total/self.config.totalCycles)
            selfWriteScope.addOrSkipDefaultTaggedItem('totalCycles', self.config.totalCycles)
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
    parameters:GCTesterTestParameters 
        
    def __init__(self, test:"GCTester", config:GCTestRunConfig, parameters:GCTesterTestParameters ):
        super().__init__(config)
        self.results = []
        self.signature = test.signature
        self.parameters = parameters
        for target in test.targets:
            self.results.append( GCTestRunResult(target, config) )

    def runInternal(self, config:GCTestRunConfig, args:GCTesterTestParameters ):
        assert args is self.parameters
        for result in self.results:
            try:
                result.run(config, args)
            except (Exception,TypeError) as inst:
                result.exc = inst
                #raise

    def writeOnScope(self, writeScope:WriteScope|None = None):
        #writeScope = TargetedWriteScope.makeScope(writeScope)

        with writeScope.startDict(indentItems=True) as selfScope:
            selfScope.addOrSkipDefaultTaggedItem( "config", self.config )
            selfScope.addOrSkipDefaultTaggedItem( "signature", self.signature )
            selfScope.addOrSkipDefaultTaggedItem( "parameters", self.parameters )
            #selfScope.addTaggedItem( "rc", len(self.results)  )
            if len(self.results):
                selfScope.addOrSkipDefaultTaggedItem( "totalCycles", self.config.totalCycles )
            total = GCTestAllocScopeSample()
            with selfScope.startDict("results",indentItems=True) as resultScope:
                for result in self.results:
                    if result.exc is None:
                    #if True:
                        resultScope.addTaggedItem( result.name, result )
                        total = total + result.outerScope.elapsed
                        
                    
            if selfScope.config.detailed:
                selfScope.addTaggedItems( outer=self.outerScope.elapsed,
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
    raise Exception( f"unnamed type {type(f)} : {f}")
    return fr


GCTArg_NO_DEFAULT = "NO_DEFAULT"
class GCTestSignatureArg(object):
    def __init__(self, name:str, kind:Any, default=GCTArg_NO_DEFAULT, **kwds ):
        self.name = name
        self.required = default is GCTArg_NO_DEFAULT
        
        self.kind = makeTypingExpression(kind)
        if default is not GCTArg_NO_DEFAULT:
            self.default = default

    
    def writeOnScope(self, writeScope:WriteScope ):
        with writeScope.startDict(indentItems=False) as selfWriteScope:
            selfWriteScope.addTaggedItems( name=self.name )
            selfWriteScope.addTaggedItems( id=id(self) )
            if self.required:
                selfWriteScope.addTaggedItems( required=True )
            if hasattr( self, 'default' ):
                selfWriteScope.addTaggedItems( default=self.default )
                        
GCTArg = GCTestSignatureArg        
        
class GCTestSignature(object):
    def __init__(self, name:str, arguments:List[GCTestSignatureArg] ):
        self.name = name
        self.arguments = arguments
    
    def writeOnScope(self, writeScope:WriteScope ):
        with writeScope.startDict(indentItems=False) as selfWriteScope:
            for arg in self.arguments:
                selfWriteScope.addTaggedItem( arg.name, arg )

class GCTester(object):
    """ manage gc tests for a common signature

    """
    targets:list[GCTestTarget] 
    signature:GCTestSignature
    
    def __init__(self,
                 signature:GCTestSignature|list,
                 baseline:Callable|None = None, 
                 ):
        self.targets = [GCTestTarget("baseline", baseline or (lambda *args,**kwds:None) )]
        if not isinstance(signature,GCTestSignature):
            sigArgs = signature
            signature = GCTestSignature( signature, sigArgs )
            
        assert isinstance(signature,GCTestSignature)
        self.signature = signature
    
    def addTests( self, *args, **kwds ):
        for test in args:
            self.targets.append( GCTestTarget(_getName(test),test) )
        for tag,val in kwds.items():
            self.targets.append( GCTestTarget(tag,val) )
            
    def run( self, config:GCTestRunConfig, args:GCTesterTestParameters, 
            #cycles:int|GCTestRunConfig|None = None, innerCycles:int|None = None,
            #config:GCTestRunConfig|None = None,  
             ) -> GCTestRunResults:
        if False:
            if isinstance(cycles,GCTestRunConfig):
                assert( config is None )
                config = cycles
                cycles = None
                
            if config is None:
                config = GCTestRunConfig( cycles=cycles, innerCycles=innerCycles )
            else:
                assert cycles is None
                assert innerCycles is None
        results = GCTestRunResults( self, config, args )
        results.run(config, args)
        return results



class GCTesterAndArgs(object):
    def __init__(self, name:str, tester:GCTester ):
        self.name = name
        self.tester = tester
        self.argsList:List[GCTesterTestParameters] = []
        self.signature = tester.signature
        
    def addArgs(self, name:str, *args, **kwds ):
        self.argsList.append( GCTesterTestParameters.make(name,*args,*kwds) )
        return self
    
    def run( self, config:GCTestRunConfig ):
        results = GCTesterAndArgsResults(self, config)

        for al in self.argsList:
            result = self.tester.run(config=config, args=al)
            results.entries.append(result)
            #results.entries.append(GCTesterAndParametersResult( result=result, config=config, parameters=al) )   
        return results

class GCTesterAndParametersResult(mutableObject):
    result:GCTestRunResults    
    config:GCTestRunConfig
    parameters:GCTesterTestParameters 

    name = property(lambda self: self.parameters.name )

    def writeOnScope( self, writeScope:DictWriteScope ):
        with writeScope.startNamedType(self, indentItems=True) as selfScope:
            selfScope.addOrSkipDefaultTaggedItem('config', self.config)
            selfScope.addOrSkipDefaultTaggedItem('parameters', self.parameters)
            selfScope.addTaggedItem('resultCount', len(self.result.results))
            selfScope.addTaggedItem('result', self.result)

                    
class GCTesterAndArgsResults(object):
    def __init__(self, root:GCTesterAndArgs, config:GCTestRunConfig ):
        self.entries:List [GCTesterAndParametersResult] = []
        self.name = root.name
        self.config = config
        self.signature = root.signature
    def writeOnScope( self, writeScope:DictWriteScope ):
        with writeScope.startNamedType(self, indentItems=True) as selfScope:
            selfScope.addOrSkipDefaultTaggedItem('config', self.config)
            selfScope.addOrSkipDefaultTaggedItem('signature', self.signature)
            #selfScope.addTaggedItem('resultCount',len(self.entries))
            selfScope.addTaggedItem('results',self.entries)



class GCTestSet(object):
    testers: Mapping[str,GCTesterAndArgs]
    
    def __init__( self ):
        pass
        self.testers = {}
        
    def addTester(self, name:str, signature:GCTestSignature|list, tests:List[Callable]|None = None, baseline:Callable|None=None ):
        tester = GCTester( signature=signature,baseline=baseline)
        
        tester.addTests(*tests)
        
        rv = GCTesterAndArgs( name, tester )
        self.testers[name] = rv
        return rv
    
    def run( self ):
        outerWriteScope = TargetedWriteScope( sys.stdout )
        outerWriteScope.config.detailed = False
        config = GCTestRunConfig(cycles=5, innerCycles=1,optimizeArgs=True)
        for tag,val in self.testers.items():
            with outerWriteScope.startDict(indentItems=True) as testsScope:
                result = val.run(config)
                testsScope.addItem(result)

        

#############################################################################

