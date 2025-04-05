from LumensalisCP.CPTyping import *
from ..Main.Dependents import MainChild
from ..Main.Expressions import ExpressionTerm, Expression, InputSource, OutputTarget
from LumensalisCP.common import *
from LumensalisCP.util.bags import *
from ..Main.Expressions import EvaluationContext
from ..Lights.Patterns import Pattern

class Setter(object):
    pass

class SceneTaskKwargs(TypedDict):
    task:Callable
    period:float | None

class SceneTask(object):
    def __init__(self, task:Callable = None, period:float|None = 0.02, name = None ):
        self.task_callback = task
        if name is None:
            try:
                name = task.__name__
            except:
                name = repr(task)

        self.__name = name
        self.__period = period
        self.__nextRun = period
        
    @property
    def period(self): return self.__period
    
    @property
    def name(self): return self.__name
    
    def run( self, scene:"Scene", context: EvaluationContext ):
        if self.__nextRun is not None:
            if scene.main.when < self.__nextRun:
                return
            self.__nextRun = scene.main.when + self.__period
        
        self.task_callback()

class SceneRule( Expression ):
    def __init__( self, target:OutputTarget=None, term:ExpressionTerm=None, name=None ):
        super().__init__(term)
        self.target = target
        self.__name = name or f"set {target.name}"
        
    @property
    def name(self): return self.__name
    
    def run( self, context:EvaluationContext):
        if 0: print( f"running rule {self.name}")
        if self.updateValue( context ): # or len(context.changedTerms):
            if 0: print( f"setting target {self.target.name} to {self.value} in rule {self.name}")
            self.target.set(self.value,context=context)

    
class Scene(MainChild):
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        
        self.__rules: Mapping[str,SceneRule] = {}
        self.__tasks:List[SceneTask] = []
        self.__patterns:List[Pattern] = NamedList()
        
        self.__patternRefreshPeriod = 0.1
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
    
    
    def runTasks(self, context:EvaluationContext):
        if 0: print( f"scene {self.name} run tasks ({len(self.__tasks)} tasks, {len(self.__rules)} rules) on update {context.updateIndex}..." )
        for task in self.__tasks:
            try:
                task.run( self, context )
            except Exception as inst:
                self.SHOW_EXCEPTION(  inst, "running task %s", task.name )
        for tag, rule in self.__rules.items():
            try:
                rule.run( context )
            except Exception as inst:
                self.SHOW_EXCEPTION( inst, "running rule %s", rule.name  )
        if self.__nextPatternsRefresh <= context.when:
            self.__nextPatternsRefresh = context.when +  self.__patternRefreshPeriod
            for pattern in self.__patterns:
                try:
                    pattern.refresh(context)
                except Exception as inst:
                    pattern.SHOW_EXCEPTION( inst, "pattern refresh failed in %r", self )




"""def addTaskDef( self, name:str = None, **kwds:SceneTaskKwargs  ) -> SceneTask:

        def addTask( callable ):
            scene.addTask(callable, name = name or callable.__name__, **kwds)
        return task
        """
    
def addSceneTask( scene:Scene, name:str = None, **kwds:SceneTaskKwargs ):
    def addTask( callable ):
        scene.addTask(callable, name = name, **kwds)
        
    return addTask