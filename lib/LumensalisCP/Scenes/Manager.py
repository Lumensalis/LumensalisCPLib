
from .Scene import Scene, SceneTask
from ..Main.Expressions import EvaluationContext

from LumensalisCP.CPTyping import *
from LumensalisCP.common import *
from LumensalisCP.Main.Profiler import Profiler

class SceneManager(Debuggable):
    def __init__(self, main ):
        super().__init__()
        self.name = "SceneManager"
        self.main = main
        self._scenes:Mapping[str,Scene] = {}
        self.__currentScene:Scene = None

    def addScene( self, name:str, *args, **kwds ) -> Scene:
        scene = Scene( *args, name=name, main=self.main, **kwds )
        self._scenes[name] = scene
        if self.__currentScene is None:
            self.__currentScene = scene
        return scene
    
    def run(self, context:EvaluationContext):
        if self.__currentScene is None: 
            #self.warnOut( "no current scene active" )
            return
        
        self.__currentScene.runTasks(context)
        
    @property
    def currentScene(self): return self.__currentScene
        
    @currentScene.setter
    def currentScene(self, scene:Scene):  self.setScene(scene)
        
    def setScene(self, scene:Scene|str ):
        if type(scene) is str:
            actualScene = self._scenes.get(scene,None)
            ensure( actualScene is not None, "unknown scene %r", scene )
            scene = actualScene
        
        if scene  != self.__currentScene:
            self.enableDbgOut and self.dbgOut( "switching from scene %r to scene %r", self.__currentScene, scene )
            self.__currentScene = scene
            
    def switchToNextIn( self, sceneList ):
        matched = False
        newSceneName = None
        currentSceneName = self.currentScene.name
        for sceneName in sceneList:
            if newSceneName is None: 
                # default to first in list
                newSceneName = sceneName
            if matched:
                newSceneName = sceneName
                break
            if currentSceneName == sceneName:
                matched = True
        
        print( f"switch from scene {currentSceneName} to {newSceneName}" )
        self.setScene( newSceneName )
        