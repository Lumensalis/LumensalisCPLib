from LumensalisCP.ImportProfiler import ImportProfiler
import sys, time
ImportProfiler.SHOW_IMPORTS = False
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl, pmc_gcManager

if False:
    pmc_mainLoopControl.ENABLE_PROFILE = True
    pmc_gcManager.PROFILE_MEMORY = True
    pmc_gcManager.PROFILE_MEMORY_ENTRIES = True
    pmc_gcManager.PROFILE_MEMORY_NESTED = True

# pyright: reportUnusedImport=false

print( "importing LumensalisCP.Main.Manager")
from LumensalisCP.common import *
from LumensalisCP.Eval.EvaluationContext import EvaluationContext
from LumensalisCP.Main.Profiler import Profiler, ProfileFrameBase, ProfileWriteConfig
from LumensalisCP.util.bags import Bag
from LumensalisCP.Scenes.Scene import addSceneTask, Scene

import LumensalisCP.Main.Manager
from collections import OrderedDict

import supervisor
supervisor.runtime.autoreload = True

print( "creating  MainManger")
Debuggable.DBG_HEADER_FORMAT = "%.4f %s %s : "
class MainStub( LumensalisCP.Main.Manager.MainManager):
    def __init__(self, fakeTime:bool = True ) -> None:
        self.fakeTime = fakeTime
        self.__testTime:TimeInSeconds = TimeInSeconds(0)
        self.__testTimeIncrement:TimeInSeconds = TimeInSeconds(0.0001)
        self.__trueTimeOffset:TimeInSeconds = TimeInSeconds(time.monotonic())

        if fakeTime:

            def getOffsetNow()->TimeInSeconds:
                """ Get the current time"""
                return self.fakeOffsetNow()
            for module in sys.modules.values():
                if hasattr(module, 'getOffsetNow'):
                    setattr(module, 'getOffsetNow', getOffsetNow)

        super().__init__(unitTesting=True)


        self.asyncLoop = Bag( #type: ignore
            priorSleepWhen=TimeInSeconds(0)
        )
        if pmc_mainLoopControl.ENABLE_PROFILE:
            from LumensalisCP.Main.Profiler import ProfileFrame,ProfileSnapEntry,ProfileSubFrame,ProfileFrameBase
            ProfileFrame.releasablePreload( 20 )
            ProfileSubFrame.releasablePreload( 100 )
            ProfileSnapEntry.releasablePreload( 300 )

    def trueOffsetTime(self) -> TimeInSeconds:
        return TimeInSeconds(time.monotonic() - self.__trueTimeOffset)

    def fakeOffsetNow(self)->TimeInSeconds:
        """ Get the current time"""
        self.__testTime = TimeInSeconds(self.__testTime +self.__testTimeIncrement)
        return self.__testTime

    def step( self, when:Optional[float]=None,next:Optional[float]=None) -> None:
        if when is not None:
            now = TimeInSeconds(when)
            assert now >= self.__testTime, f"step: when={when} < {self.__testTime}"
            self.__testTime = now
        elif next is not None:
            ttd, ttr = divmod(self.__testTime,next)
            if ttr > 0: ttd += 1
            tt = TimeInSeconds(ttd * next)
            assert tt >= self.__testTime, f"step: next={next} leads to {tt} < {self.__testTime}"
            self.__testTime = tt
            now = tt
        else:
            now = self.getNewNow()

        with self.getTestFrame(now):
            context = self._privateCurrentContext
            self._refreshables.process(context, context.when)
            if self._timers is not None:
                self._timers.update( context )
            if self._scenes is not None:
                self._scenes.run(context)

        self.priorSleepWhen = self.getNewNow()

    def getTestFrame(self,now:TimeInSeconds) ->ProfileFrameBase:
        self._when = now
        if self.profiler.disabled:
            newFrame = self.profiler.stubFrame
            self._privateCurrentContext.reset(now,newFrame)
            return newFrame

        context = self._privateCurrentContext
        self._privateCurrentContext.reset(now,None)
        eSleep = TimeInSeconds( now - self.asyncLoop.priorSleepWhen )
        newFrame = self.profiler.nextNewFrame(context, eSleep = eSleep ) 
        assert isinstance( newFrame, ProfileFrameBase )
        
        context.baseFrame  = context.activeFrame = newFrame
        return newFrame        

    def getProfilerData(self, count:int = 10):
        info:StrAnyDict = {} # OrderedDict()
        settings: ProfileWriteConfig.KWDS = {
            'target': info,
            'minE': 0.00,
            'minF': 0.0,
            'minSubF': 0.0,
            'minB': 50,
            #'minEB': 0,
        }
        dumpConfig = ProfileWriteConfig( **settings )

        print( f"getProfilerInfo: settings = {settings}" )
        #self.profiler.getProfilerInfo(dumpConfig=dumpConfig)
        with dumpConfig.nestList('frames'):
            i = self.getContext().updateIndex
            while count and i >= 0:
                count -= 1
                frame = self.profiler.timingForUpdate( i )
                
                if frame is not None:
                    with dumpConfig.nestDict():
                        frame.writeOn( dumpConfig )
                i -= 1
                
        return info

