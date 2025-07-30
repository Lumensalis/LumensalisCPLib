
from __future__ import annotations

from LumensalisCP.Main.PreMainConfig import pmc_getImportProfiler
_sayScenesManagerImport = pmc_getImportProfiler( "Scenes.Manager" )

from LumensalisCP.Identity.Local import NamedLocalIdentifiable, NliContainerMixin, NliList
from LumensalisCP.Scenes.Scene import Scene
from LumensalisCP.Eval.Expressions import EvaluationContext

from LumensalisCP.CPTyping import *
from LumensalisCP.common import *

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    
_sayScenesManagerImport.parsing()

class SceneManager(NamedLocalIdentifiable):
    def __init__(self, main: MainManager) -> None:
        super().__init__("SceneManager")
        self.main = main
        #self._scenes:Mapping[str,Scene] = {}
        self._scenes:NliList[Scene] = NliList("scenes", parent=self)
        self.__currentScene:Scene|None = None

    def addScene( self, **kwds:Unpack[Scene.KWDS] ) -> Scene:
        kwds.setdefault("main", self.main)
        scene = Scene( **kwds )
        scene.nliSetContainer(self._scenes)
        if self.__currentScene is None:
            self.__currentScene = scene
        return scene
    
    def run(self, context:EvaluationContext):
        if self.__currentScene is None: 
            #self.warnOut( "no current scene active" )
            return
        
        self.__currentScene.runTasks(context)

    def nliGetContainers(self) -> list[NliContainerMixin[Any]]:
        return [self._scenes]
        
    @property
    def currentScene(self): return self.__currentScene
        
    @currentScene.setter
    def currentScene(self, scene:Scene|str):  self.setScene(scene)
        
    def setScene(self, scene:Scene|str ):
        if type(scene) is str:
            actualScene = self._scenes.get(scene,None)
            assert actualScene is not None, safeFmt("unknown scene %r", scene )
            scene = actualScene
        
        if scene  != self.__currentScene:
            if self.enableDbgOut: self.dbgOut( "switching from scene %r to scene %r", self.__currentScene, scene )
            self.__currentScene = scene # type: ignore
            
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
