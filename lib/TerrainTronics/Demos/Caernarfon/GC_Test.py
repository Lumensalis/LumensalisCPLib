#import LumensalisCP.Main._preMainConfig, gc
from LumensalisCP.Main._preMainConfig import _mlc,gcm,printElapsed

printElapsed( "starting imports" )
from . import GC_TestRL
import gc
#from LumensalisCP.Main._preMainConfig import _mlc,gcm,printElapsed
#mlc = _mlc

GC_TestRL.setupMlcAndGcm()

from ..DemoBase import DemoBase
from LumensalisCP.Triggers.Timer import PeriodicTimer, addPeriodicTaskDef
from LumensalisCP.util.bags import Bag

import gc

printElapsed("parsing class GC_Test")

class GC_Test( DemoBase ):

    def setup(self):
        main = self.main

        dt = PeriodicTimer( interval=lambda : GC_TestRL.printDumpInterval, manager=main.timers, name="dump" )
        
        @dt.addTaskDef( "printDumpPeriod" )
        def dump():
            GC_TestRL.printDump(main)
            
        @addPeriodicTaskDef( "gc-collect", period=lambda: GC_TestRL.collectionCheckInterval, main=main )
        def runCollection(context=None, when=None):
            GC_TestRL.runCollection( context, when, show=True)
            
        @addPeriodicTaskDef( period=lambda: GC_TestRL.usbCheckInterval, main=main )
        def usbCheck(context=None, when=None):
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