
from .Scene import Scene, SceneTask
from ..Main.Expressions import EvaluationContext

from LumensalisCP.CPTyping import *

class SceneManager(object):
    def __init__(self, main ):
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
            print( "no current scene active")
            return
        self.__currentScene.runTasks(context)
        