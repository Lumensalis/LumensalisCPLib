#from LumensalisCP.CPTyping import *
from ..Main.Dependents import MainChild
from ..Main.Expressions import ExpressionTerm, Expression
from  LumensalisCP.IOContext import *# InputSource, OutputTarget
#from LumensalisCP.common import *

from LumensalisCP.util.bags import *
#from ..Main.Expressions import EvaluationContext
from ..Lights.Patterns import Pattern
from LumensalisCP.util.kwCallback import KWCallback
from LumensalisCP.Main.Profiler import ProfileFrameBase

class Setter(object):
    pass

class SceneTaskKwargs(TypedDict):
    task:Callable
    period:float | None

class SceneTask(object):
    def __init__(self, task:Callable = None, period:float|None = 0.02, name = None ):
        self.task_callback = KWCallback.make( task )
        if name is None:
            try:
                name = task.__name__
            except:
                name = repr(task)

        self.__name = name or task.__name__
        self.__period = period
        self.__nextRun = period
        
    @property
    def period(self): return self.__period
    
    @property
    def name(self): return self.__name
    
    def run( self, scene:"Scene", context: EvaluationContext, frame:ProfileFrameBase ):
        if self.__nextRun is not None:
            if scene.main.when < self.__nextRun:
                return
            self.__nextRun = scene.main.when + self.__period
        frame.snap( f"runSceneTask-{self.__name}" )
        self.task_callback(context=context)

class SceneRule( Expression ):
    def __init__( self, target:OutputTarget=None, term:ExpressionTerm=None, name=None ):
        super().__init__(term)
        self.target = target
        self.__name = name or f"set {target.name}"
        
    @property
    def name(self): return self.__name
    
    def run( self, context:EvaluationContext, frame:ProfileFrameBase):
        if 0: print( f"running rule {self.name}")
        if self.updateValue( context ): # or len(context.changedTerms):
            if 0: print( f"setting target {self.target.name} to {self.value} in rule {self.name}")
            frame.snap(f"ruleSet{self.target.name}" )
            self.target.set(self.value,context=context)

    
class Scene(MainChild):
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        
        self.__rules: Mapping[str,SceneRule] = {}
        self.__tasks:List[SceneTask] = []
        self.__patterns:List[Pattern] = NamedList()
        
        self.__patternRefreshPeriod = 0.02
        self.__nextPatternsRefresh = 0

    @property
    def patterns(self) -> NamedList[Pattern]:
        return self.__patterns
    
    def addPatterns(self, *patterns, patternRefresh:float = None ):
        if patternRefresh is not None:
            self.__patternRefreshPeriod = patternRefresh
        self.__patterns.extend(patterns)
        
    
    def addRule(self, target:OutputTarget=None, term:ExpressionTerm=None, name=None ) ->SceneRule:
            assert isinstance( term, ExpressionTerm )
            rule = SceneRule( target=target, term=term, name=name )
            dictAddUnique( self.__rules, target.name, rule )
            return rule
        
    def findOutput( self, tag:str ) -> OutputTarget:
        raise NotImplemented
                    
    def addRules(self, **kwargs:Mapping[str,ExpressionTerm] ):
        for tag, val in kwargs.items():
            self.addRule( self.findOutput(tag), val )

    def sources( self ) -> Mapping[str,InputSource]:
        rv = {}
        for setting in self.__rules.values():
            for source in setting.sources().values():
                dictAddUnique( rv, source.name, source )
    
        return rv

    def addTask( self, *args, **kwds:SceneTaskKwargs  ) -> SceneTask:
        task = SceneTask( *args, **kwds )
        self.__tasks.append( task )
        return task
    
    
    def addTaskDef( self, name:str = None, **kwds:SceneTaskKwargs  ) -> SceneTask:

        def addTask( callable ):
            self.addTask(callable, name = name or callable.__name__, **kwds)
            return callable
        
        return addTask
    
    def runTasks(self, context:EvaluationContext):
        if 0: print( f"scene {self.name} run tasks ({len(self.__tasks)} tasks, {len(self.__rules)} rules) on update {context.updateIndex}..." )
        with context.subFrame('runScene', self.name ) as activeFrame:
            for task in self.__tasks:
                try:
                    task.run( self, context=context, frame=activeFrame )
                except Exception as inst:
                    self.SHOW_EXCEPTION(  inst, "running task %s", task.name )
            activeFrame.snap("a")
            activeFrame.snap("b")
            activeFrame.snap("rules")
            for tag, rule in self.__rules.items():
                try:
                    rule.run( context, frame=activeFrame )
                except Exception as inst:
                    self.SHOW_EXCEPTION( inst, "running rule %s", rule.name  )
            activeFrame.snap("patterns")
            if self.__nextPatternsRefresh <= context.when:
                self.__nextPatternsRefresh = context.when +  self.__patternRefreshPeriod
                for pattern in self.__patterns:
                    try:
                        pattern.refresh(context)
                    except Exception as inst:
                        pattern.SHOW_EXCEPTION( inst, "pattern refresh failed in %r", self )

def addSceneTask( scene:Scene, name:str = None, **kwds:SceneTaskKwargs ):
    def addTask( callable ):
        scene.addTask(callable, name = name, **kwds)
        
    return addTask