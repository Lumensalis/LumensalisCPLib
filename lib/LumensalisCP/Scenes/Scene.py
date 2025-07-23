from LumensalisCP.common import *
from LumensalisCP.IOContext import *
from LumensalisCP.Main.Dependents import MainChild

from LumensalisCP.util.bags import NamedList
from LumensalisCP.Lights.Patterns import Pattern
from LumensalisCP.Main.Profiler import ProfileFrameBase

class Setter(object):
    pass

class SceneTaskKwargs(TypedDict):
    period:TimeInSeconds 
    name:Optional[str]

class SceneTask(NamedLocalIdentifiable):
    def __init__(self, task:Callable, period:TimeInSeconds = 0.02, name:Optional[str] = None ):
        super().__init__(name=name)
        self.task_callback = KWCallback.make( task )
        self.__period = period
        self.__nextRun = period
        
    @property
    def period(self) -> TimeInSeconds: return self.__period
    
    def run( self, scene:"Scene", context: EvaluationContext, frame:ProfileFrameBase ):
        if self.__nextRun is not None:
            if scene.main.when < self.__nextRun:
                return
            self.__nextRun = scene.main.when + self.__period
        frame.snap( f"runSceneTask-{self.__name}" )
        self.task_callback(context=context)

class SceneRule( NamedLocalIdentifiable, Expression,  ):
    def __init__( self, target:NamedOutputTarget, term:ExpressionTerm, name:Optional[str]=None ):
        #super().__init__(term)
        Expression.__init__(self,term)
        NamedLocalIdentifiable.__init__(self,name=name)
        self.target = target

    def run( self, context:EvaluationContext, frame:ProfileFrameBase):
        #if self.enableDbgOut: self.dbgOut( "running rule" )
        if self.updateValue( context ): # or len(context.changedTerms):
            if self.enableDbgOut: self.dbgOut( f"setting target {self.target.name} to {self.value} in rule {self.name}")
            frame.snap( "ruleSet", self.target.name )
            self.target.set(self.value,context=context)

class Scene(MainChild):
    
    def __init__( self, **kwargs:Unpack[MainChild.KWDS] ):
        super().__init__( **kwargs )

        self.__rulesContainer = NliList("rules",parent=self)
        self.__rules: Mapping[str,SceneRule] = {}
        
        self.__tasksContainer = NliList("tasks",parent=self)
        self.__tasks:List[SceneTask] = []
        
        self.__patternsContainer = NliList("patterns",parent=self)
        self.__patterns:NamedList[Pattern] = NamedList()
        
        self.__patternRefreshPeriod = 0.02
        self.__nextPatternsRefresh = 0

    def nliGetContainers(self) -> list[NliContainerMixin]|None:
        
        return [self.__rulesContainer, self.__tasksContainer, self.__patternsContainer]
    
    @property
    def patterns(self) -> NamedList[Pattern]:
        return self.__patterns
    
    def addPatterns(self, *patterns:Pattern ):
        """add patterns to a scene

        :param patternRefresh: _description_, defaults to None
        :type patternRefresh: float, optional
        """
        #if patternRefresh is not None:
        #    self.__patternRefreshPeriod = patternRefresh
        self.__patterns.extend(patterns)
        for pattern in patterns:
            pattern.nliSetContainer(self.__patternsContainer)
        
    
    def addRule(self, target:NamedOutputTarget, term:ExpressionTerm, name:Optional[str]=None ) ->SceneRule:
            assert isinstance( term, ExpressionTerm )
            rule = SceneRule( target=target, term=term, name=name )
            #dictAddUnique( self.__rules, target.name, rule )
            rule.nliSetContainer( self.__rulesContainer )
            return rule
        
        
    def findOutput( self, tag:str ) -> NamedOutputTarget:
        raise NotImplementedError
                    
    def addRules(self, **kwargs:ExpressionTerm ):
        for tag, val in kwargs.items():
            self.addRule( self.findOutput(tag), val )

    def sources( self ) -> Mapping[str,InputSource]:
        rv = {}
        for setting in self.__rulesContainer:
            for source in setting.sources().values():
                dictAddUnique( rv, source.name, source )
    
        return rv

    def addTask( self, task:Callable, **kwds:Unpack[SceneTaskKwargs]  ) -> SceneTask:
        sceneTask = SceneTask( task, **kwds )
        self.__tasks.append( sceneTask )
        sceneTask.nliSetContainer(self.__tasksContainer)
        return sceneTask
    
    
    def addTaskDef( self, **kwds:Unpack[SceneTaskKwargs]  )  -> Callable[..., Any]:

        def addTask( callable ):
            self.addTask(callable, **kwds)
            return callable
        
        return addTask
    
    def runTasks(self, context:EvaluationContext):
        if self.enableDbgOut: self.dbgOut( f"scene {self.name} run tasks ({len(self.__tasks)} tasks, {len(self.__rulesContainer)} rules) on update {context.updateIndex}..."  )
        with context.subFrame('runScene', self.name ) as activeFrame:
            for task in self.__tasks:
                try:
                    task.run( self, context=context, frame=activeFrame )
                except Exception as inst:
                    self.SHOW_EXCEPTION(  inst, "running task %s", task.name )
            activeFrame.snap("rules")
            for rule in self.__rulesContainer:
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
                        SHOW_EXCEPTION( inst, "pattern %r refresh failed in %r", 
                                       getattr(pattern,'name',pattern), self )

def addSceneTask( scene:Scene, **kwds:Unpack[SceneTaskKwargs] ):
    def addTask( callable ):
        scene.addTask(callable, **kwds)
        
    return addTask