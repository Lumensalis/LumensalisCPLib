

import LumensalisCP.Debug

import time, math, asyncio, traceback, os, gc, rainbowio, wifi, displayio
import busio, board
import collections

from LumensalisCP.common import *
from LumensalisCP.CPTyping import *


import LumensalisCP.I2C.I2CDevice
from LumensalisCP.I2C.I2CDevice import I2CDevice

from LumensalisCP.Controllers.ConfigurableBase import ConfigurableBase
from LumensalisCP.Controllers.Identity import ControllerIdentity
from .ControlVariables import ControlVariable, IntermediateVariable

from ..Scenes.Manager import SceneManager, Scene
from ..Triggers.Timer import PeriodicTimerManager

from .Expressions import EvaluationContext
from .Shutdown import ExitTask
from LumensalisCP.Debug import Debuggable 
import LumensalisCP.Audio 

import LumensalisCP.Main.Dependents
from TerrainTronics.Factory import TerrainTronicsFactory
from LumensalisCP.I2C.Adafruit.AdafruitI2CFactory import AdafruitFactory
from LumensalisCP.I2C.I2CFactory import I2CFactory
from LumensalisCP.HTTP.BasicServer import BasicServer
from LumensalisCP.Audio import Audio
from LumensalisCP.Lights.DMXManager import DMXManager
from socketpool import SocketPool

class MainManager(ConfigurableBase, Debuggable):
    
    theManager : MainManager|None
    i2cFactory : I2CFactory
    adafruitFactory : AdafruitFactory
    dmx : DMXManager
    socketPool : SocketPool
    
    @staticmethod
    def initOrGetManager()->MainManager:pass

    def __init__(self, config = None, **kwds ): pass
 
    def makeRef(self)-> LumensalisCP.Main.Dependents.MainRef: pass

    
    @property
    def identity(self) -> ControllerIdentity: pass
    
    @property
    def TerrainTronics(self) ->TerrainTronicsFactory: pass
    
    @property
    def when(self) -> TimeInSeconds: pass

    cycle: int
    millis: int
    seconds: TimeInSeconds
    
    newNow: TimeInSeconds

    @property
    def defaultI2C(self) -> busio.I2C: pass
    
    @property
    def scenes(self) -> SceneManager: pass
    
    @property
    def timers(self) -> PeriodicTimerManager: pass
    
    @property
    def latestContext(self)->EvaluationContext: pass

    def callLater( self, task ): pass

            
    def addExitTask(self,task:ExitTask|Callable): pass
        
    def _addI2CDevice(self, target:I2CDevice ): pass
   
    def addControlVariable( self, name, *args, **kwds ) -> ControlVariable: pass
        
    def addIntermediateVariable( self, name, *args, **kwds ) -> IntermediateVariable: pass
        
    def addScene( self, name:str, *args, **kwds ) -> Scene: pass
    
    def addBasicWebServer( self, *args, **kwds ) -> BasicServer: pass
        

    def handleWsChanges( self, changes:dict ): pass
        
    
    async def msDelay( self, milliseconds ): pass
    
    @property
    def audio(self) -> Audio: pass

    def addI2SAudio(self, *args, **kwds ) -> Audio: pass

    
    def movingValue( self, min=0, max=100, duration:float =1.0 ) -> float: pass
        
    def _addBoardI2C( self, board, i2c:busio.I2C ): pass

    def addTask( self, task ): pass

    def dumpLoopTimings( self, count:int, minE:TimeSpanInSeconds=None, minF:TimeSpanInSeconds=None, **kwds ): pass
    
    async def taskLoop( self ): pass

    def run( self ): pass
