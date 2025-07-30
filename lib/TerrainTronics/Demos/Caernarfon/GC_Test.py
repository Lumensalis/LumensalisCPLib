#import LumensalisCP.Main._preMainConfig, gc
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl,pmc_gcManager,printElapsed

printElapsed( "starting imports" )
from . import GC_TestRL
import gc
#from LumensalisCP.Main._preMainConfig import _mlc,gcm,printElapsed
#mlc = _mlc

GC_TestRL.setupMlcAndGcm()

from LumensalisCP.Demo.DemoBase import DemoBase
from LumensalisCP.Triggers.Timer import PeriodicTimer, addPeriodicTaskDef
from LumensalisCP.util.bags import Bag
from LumensalisCP.Eval.EvaluationContext  import EvaluationContext


import gc

printElapsed("parsing class GC_Test")

class GC_Test( DemoBase ):

    def setup(self):
        main = self.main
        # pydfdfright: reportUnusedFunction=false
        # pyright: reportUnusedFunction=false


        dt = PeriodicTimer( interval=lambda : GC_TestRL.printDumpInterval, manager=main.timers, name="dump" )
        
        @dt.addSimpleTaskDef( "printDumpPeriod" )
        def dump():
            GC_TestRL.printDump(main)
            
        @addPeriodicTaskDef( "gc-collect", 
                            period=lambda: GC_TestRL.collectionCheckInterval,
                            main=main
                 )
        def runCollection(context:EvaluationContext) -> None:
            GC_TestRL.runCollection( context, show=True)
            
        @addPeriodicTaskDef( period=lambda: GC_TestRL.usbCheckInterval, main=main )
        def usbCheck(context:EvaluationContext):
            GC_TestRL.usbCheck( context)
            
                        
        def firstGC():
            GC_TestRL.runCollection( main.getContext(), main.when, force=True)
        main.callLater(firstGC)
                    
        gc.disable()

def demoMain(*args,**kwds):
    printElapsed("instantiating GC_Test")
    demo = GC_Test( *args, **kwds )
    
    printElapsed("calling demo.run()")
    demo.run()