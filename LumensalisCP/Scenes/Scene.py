from LumensalisCP.CPTyping import Mapping
from ..Main.Dependents import MainChild
from ..Main.Expressions import ExpressionTerm, Expression, InputSource, OutputTarget
from LumensalisCP.common import *
from ..Main.Expressions import EvaluationContext

class Setter(object):
    pass

class SceneTask(object):
    def __init__(self, task, period:float|None = None, **kwds ):
        self.task_callback = task
        self.__period = period
        self.__nextRun = period
        
    @property
    def period(self): return self.__period
    
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

    def addTask( self, task, **kwds  ) -> SceneTask:
        task = SceneTask( task, **kwds )
        self.__tasks.append( task )
        return task
    
    def runTasks(self, context:EvaluationContext):
        if 0: print( f"scene {self.name} run tasks ({len(self.__tasks)} tasks, {len(self.__rules)} rules) on update {context.updateIndex}..." )
        for task in self.__tasks:
            task.run( self, context )
        for tag, rule in self.__rules.items():
            rule.run( context )
