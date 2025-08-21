from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
from LumensalisCP.Eval.Expressions import EvaluationContext
_sayScenesSceneImport = getImportProfiler( "Scenes.Scene" )

#############################################################################

from LumensalisCP.common import *
from LumensalisCP.IOContext import *
from LumensalisCP.Main.Dependents import MainChild

from LumensalisCP.util.bags import NamedList
from LumensalisCP.Lights.Patterns import Pattern
from LumensalisCP.Main.Profiler import ProfileFrameBase
from LumensalisCP.Temporal.Refreshable import Refreshable, \
        RfMxnActivatable, RfMxnPeriodic, RfMxnNamed

from LumensalisCP.Eval.Evaluatable import NamedEvaluatableProtocolT
from LumensalisCP.Temporal.RefreshableList import NamedNestedRefreshableList


if TYPE_CHECKING:
    from LumensalisCP.Eval.Expressions import ExpressionTerm, Expression

#############################################################################

_sayScenesSceneImport.parsing()


class SceneTask( RfMxnActivatable, 
                RfMxnPeriodic, 
                RfMxnNamed,
                Refreshable ):

    RFD_autoRefresh:ClassVar[bool] = True
    class KWDS(Refreshable.KWDS, 
               RfMxnNamed.KWDS,
               RfMxnActivatable.KWDS,
               RfMxnPeriodic.KWDS):
        task:NotRequired[Callable[[],None]]

    def __init__(self, **kwds:Unpack[KWDS] ) -> None:
        
        task = kwds.pop('task',None)
        assert task is not None, "SceneTask requires a task callable"
        Refreshable.__init__(self, mixinKwds=kwds)
        self.task_callback = task

    def derivedRefresh(self, context: EvaluationContext) -> None:
        if self.enableDbgOut: self.dbgOut("running scene task %r", self.task_callback)
        self.task_callback()
    
    if False:
        def run( self, scene:"Scene", context: EvaluationContext, frame:ProfileFrameBase ):
            if scene.main.when < self.__nextRun:
                return
            self.__nextRun = TimeInSeconds( scene.main.when + self.__period )
            frame.snap( "runSceneTask", self.name )
            self.task_callback(context=context) # type: ignore[call-arg]

class SceneRule( NamedLocalIdentifiable, Expression,  NamedEvaluatableProtocolT[Any] ):
    def __init__( self, target:OutputTarget, term:ExpressionTerm, name:Optional[str]=None ):
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

class SceneRefreshables(NamedNestedRefreshableList):
    def __init__(self, scene: Scene) -> None:
        super().__init__(parent=scene.main.refreshables,name="sceneRefreshables")
        self.scene = scene

    def dsdsrefreshableCalculateNextRefresh(self, context: EvaluationContext, when: TimeInSeconds) -> TimeInSeconds | None:
        if self.enableDbgOut: self.dbgOut( "refreshableCalculateNextRefresh for scene %s at %.3f...", self.scene.name, when )
        nextRefresh = super().refreshableCalculateNextRefresh(context,when)
        nextList = self.getNextRefreshForList(context, when)
        if nextList is not None:
            if nextRefresh is None or nextList < nextRefresh:
                nextRefresh = nextList

        if self.enableDbgOut: self.dbgOut( "refreshableCalculateNextRefresh for scene %s is %.3f", nextRefresh )
        return nextRefresh
    
class Scene(MainChild):
    
    class KWDS( MainChild.KWDS):
        pass


    def __init__( self, **kwargs:Unpack[MainChild.KWDS] ) -> None:
        super().__init__( **kwargs )

        self._sceneRefreshables = SceneRefreshables( self )
            #parent=self.main.refreshables,name="sceneRefreshables" ) #, **kwargs)

        self.__rulesContainer:NliList[SceneRule] = NliList("rules",parent=self)
        self.__rules: Mapping[str,SceneRule] = {}
        
        self.__tasksContainer:NliList[SceneTask] = NliList("tasks",parent=self)
        self.__tasks:List[SceneTask] = []
        
        self.__patternsContainer:NliList[Pattern] = NliList("patterns",parent=self)
        self.__patterns:NamedList[Pattern] = NamedList()
        
        self.__patternRefreshPeriod = 0.02
        self.__nextPatternsRefresh = 0



    def nliGetContainers(self) -> list[NliContainerMixin[NamedLocalIdentifiable]]:
        return [self.__rulesContainer, self.__tasksContainer, self.__patternsContainer] # type: ignore[return-value]
    
    def refreshableCalculateNextRefresh(self, context: EvaluationContext, when: TimeInSeconds) -> TimeInSeconds | None:
        if self.enableDbgOut: self.dbgOut( "Scene.refreshableCalculateNextRefresh at %.3f...", when )
        nextRefresh = super().refreshableCalculateNextRefresh(context,when)
        nextList = self._sceneRefreshables.getNextRefreshForList(context, when)
        if nextList is not None:
            if nextRefresh is None or nextList < nextRefresh:
                nextRefresh = nextList

        if self.enableDbgOut: self.dbgOut( "Scene.refreshableCalculateNextRefresh is %.3f", nextRefresh )
        return nextRefresh
    
    @property
    def patterns(self) -> NamedList[Pattern]:
        return self.__patterns
    
    def addPattern(self, pattern:Pattern ) -> Pattern:
        self.__patterns.append(pattern)
        pattern.nliSetContainer(self.__patternsContainer)
        self._sceneRefreshables.add( context=getCurrentEvaluationContext(), item=pattern)
        return pattern

    def addPatterns(self, *patterns:Pattern ) -> tuple[Pattern, ...]:
        """add patterns to a scene - see http://lumensalis.com/ql/h2Scenes
        """
        for pattern in patterns:
            self.addPattern(pattern)
        return patterns
    
    def addRule(self, target:OutputTarget, 
                term:ExpressionTerm, 
                name:Optional[str]=None ) ->SceneRule:
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
        rv:dict[str,InputSource] = {}
        
        for setting in self.__rulesContainer:
            #setting:SceneRule
            sources = setting.sources()
            for source in sources.values():
                dictAddUnique( rv, source.name, source )
    
        return rv

    def addTask( self, **kwds:Unpack[SceneTask.KWDS]  ) -> SceneTask:
        kwds.setdefault('autoList', self._sceneRefreshables)
        sceneTask = SceneTask( **kwds )
        self.__tasks.append( sceneTask )
        sceneTask.nliSetContainer(self.__tasksContainer)
        context = UpdateContext.fetchCurrentContext(None)
        #self.add( context,sceneTask)
        if not sceneTask.isActiveRefreshable:
            sceneTask.activate(context)
        assert sceneTask.isActiveRefreshable, f"SceneTask {sceneTask} on {sceneTask.refreshList} is not active refreshable"

        return sceneTask
    
    
    def addSimpleTaskDef( self, **kwds:Unpack[SceneTask.KWDS]  ) -> Callable[[Callable[[],None]], SceneTask]:

        def addTask( callable:Callable[[],None] ) -> SceneTask:
            kwds['task'] = callable
            return self.addTask(**kwds)
        return addTask


    def derivedRefresh(self, context: EvaluationContext) -> None:
        self.runTasks(context)
    
    def runTasks(self, context:EvaluationContext):
        if self.enableDbgOut: self.dbgOut( 
f"scene {self.name} run tasks ({len(self.__tasks)} tasks, {len(self._sceneRefreshables._refreshables)} refreshables @ {self.nextRefresh}, {len(self.__rulesContainer)} rules) on update {context.updateIndex}..." )
        with context.subFrame('runScene', self.name ) as activeFrame:
        
            #for task in self.__tasks:
            #    try:
            #        task.run( self, context=context, frame=activeFrame )
            #    except Exception as inst:
            #        self.SHOW_EXCEPTION(  inst, "running task %s", task.name )
            self._sceneRefreshables.process(context, context.when)
            activeFrame.snap("rules")
            for rule in self.__rulesContainer:
                try:
                    rule.run( context, frame=activeFrame )
                except Exception as inst:
                    self.SHOW_EXCEPTION( inst, "running rule %s", rule.name  )
            if False:
                activeFrame.snap("patterns")
                if self.__nextPatternsRefresh <= context.when:
                    self.__nextPatternsRefresh = context.when +  self.__patternRefreshPeriod
                    for pattern in self.__patterns:
                        try:
                            pattern.refresh(context)
                        except Exception as inst:
                            SHOW_EXCEPTION( inst, "pattern %r refresh failed in %r", 
                                        getattr(pattern,'name',pattern), self )
                    if self.__nextPatternsRefresh < self._nextListRefresh:
                        self.setNextRefresh(context, self.__nextPatternsRefresh)

def addSceneTask( scene:Scene, **kwds:Unpack[SceneTask.KWDS] ) -> Callable[ [Callable[[],Any] ], SceneTask]:
    def addTask( callable:Callable[[],Any] ) -> SceneTask:
        kwds['task'] = callable
        return scene.addTask(**kwds)
        
    return addTask

#############################################################################

_sayScenesSceneImport.complete(globals())