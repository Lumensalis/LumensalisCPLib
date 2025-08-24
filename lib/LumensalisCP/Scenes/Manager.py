
from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayScenesManagerImport = getImportProfiler( globals() ) # "Scenes.Manager"

from LumensalisCP.Identity.Local import NamedLocalIdentifiable, NliContainerMixin, NliList
from LumensalisCP.Scenes.Scene import Scene
from LumensalisCP.Eval.Expressions import EvaluationContext

from LumensalisCP.CPTyping import *
from LumensalisCP.common import *

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    
_sayScenesManagerImport.parsing()

# pyright: reportPrivateUsage=false

class SceneManager(NamedLocalIdentifiable):
    def __init__(self, main: MainManager,**kwds:Unpack[NamedLocalIdentifiable.KWDS]) -> None:
        super().__init__( **kwds)
        self.main = main
        #self._scenes:Mapping[str,Scene] = {}
        self._scenes:NliList[Scene] = NliList("scenes", parent=self)
        self.__currentScene:Scene|None = None

    def addScene( self, **kwds:Unpack[Scene.KWDS] ) -> Scene:
        kwds.setdefault("main", self.main)
        scene = Scene(  self, **kwds )
        scene.nliSetContainer(self._scenes)
        if self.__currentScene is None:
            self.setScene(scene)
        return scene
    
    def run(self, context:EvaluationContext):
        if self.__currentScene is None: 
            #self.warnOut( "no current scene active" )
            return
        
        #self.__currentScene.runTasks(context)

    def nliGetContainers(self) -> list[NliContainerMixin[Any]]:
        return [self._scenes]
    
    def nliHasContainers(self) -> bool:
        return True

    @property
    def currentScene(self): return self.__currentScene
        
    @currentScene.setter
    def currentScene(self, scene:Scene|str):  self.setScene(scene)
        
    def setScene(self, scene:Scene|str ):
        if isinstance(scene, str):
            actualScene = self._scenes.get(scene,None)
            assert actualScene is not None, safeFmt("unknown scene %r", scene )
            scene = actualScene
        
        if scene  != self.__currentScene:
            oldScene = self.__currentScene
            newScene = scene
            if oldScene is not None:
                oldScene.deactivate()
                for invocable in oldScene.__onExit:
                    invocable(context)

                transitions = oldScene.__transitionTo.get(newScene, None)
                if transitions is not None:
                    for invocable in transitions:
                        invocable(context)
            if self.enableDbgOut: self.dbgOut( "switching from scene %r to scene %r", oldScene, newScene )
            self.__currentScene = scene # type: ignore
            for invocable in newScene.__onEnter:
                invocable(context)
            scene.activate()
            
    def switchToNextIn( self, sceneList:list[str] ):
        matched = False
        newSceneName = None
        currentSceneName = self.currentScene.name if self.currentScene is not None else "?"
        for sceneName in sceneList:
            if newSceneName is None: 
                # default to first in list
                newSceneName = sceneName
            if matched:
                newSceneName = sceneName
                break
            if currentSceneName == sceneName:
                matched = True
        
        assert newSceneName is not None
        print( f"switch from scene {currentSceneName} to {newSceneName}" )
        self.setScene( newSceneName )
        
_sayScenesManagerImport.complete(globals())
