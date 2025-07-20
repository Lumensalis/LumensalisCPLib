from LumensalisCP.Demo.DemoCommon import *
from LumensalisCP.Eval.Terms import *
from LumensalisCP.Scenes.Scene import addSceneTask

vv = 0

class HarlechLogicDemo( DemoBase ):
    def setup(self):
        main = self.main
        main.cyclesPerSecond = 2000
        
        #############################################################################
        # Add a HarlechCastle
        self.harlech = harlech = main.addHarlech(  )

        act1 = main.addScene( "firstAct" )

        def ledInfo( name, lx, ramp=None, blink = None, step=None ):
            rv = dict(
                name=name,
                lx=lx, 
                mode='ramp',
                ramp = (lx+1) * (2+ lx/7.0)
            )
                  
            return rv
        
            if ramp is not None:
                rv['ramp'] = float(ramp)
                rv['mode'] = 'ramp'
            elif blink is not None:
                rv['blink'] = float(blink)
                rv['mode'] = 'blink'
            elif step is not None:
                rv['step'] = float(step)
                rv['mode'] = 'step'
                                
            return rv
            
        p1 = 5.7
        p2 = 13.9
        ledConfigs = [
                ledInfo( "a", 0, ramp = 1, ),
                ledInfo( "b",1, step = p1 ),
                ledInfo( "c",2, ramp = p1 ),
                ledInfo( "d",3, blink = p1 ),
                ledInfo( "e",4, step = p2 ),
                ledInfo( "f",5, ramp = p2 ),
                ledInfo( "g",6, blink = p2 ),
                ledInfo( "h",7, blink = 5 ),
        ]
        
        
        leds = {}
        for config in ledConfigs:
            name = config['name']
            leds[name] = dict(
                led = harlech.led(config['lx'], name ),
                config = config,
                **config
            )
            print( f"added LED {name} : {leds[name]}")

        
        def rampEvery( nSeconds:float ):
            if nSeconds is None: return None
            return  divmod( main.when, nSeconds)[1] / nSeconds
            
            
        def blinkEvery( nSeconds:float ):
            if nSeconds is None: return None
            r = divmod( main.when, nSeconds)[1]
            return 0 if r < (nSeconds*0.5) else 1.0
            
                    
        def stepEvery( nSeconds:float ):
            if nSeconds is None: return None
            r = divmod( main.when, nSeconds)[1]
            return (int((r/nSeconds)*4))/4.0
        
        def updateLed( led ):
            
            mode = led['mode']
            if mode == 'ramp':
                level =  rampEvery( led['ramp'] )
            elif mode == 'blink':
                level =  blinkEvery( led['blink'] )
            elif mode == 'step':
                level =  stepEvery( led['step'] )
            else:
                print( f"BAD CONFIG FOR {led}" )
                level = 0
                return 
                    
            led['led'].set( level )

        ledKeys = sorted(leds.keys())
        
        #@addSceneTask( act1, period = 0.4 )
        def rainbow():
            for led in leds.values():
                updateLed(led)
            # harlech._update()
            #vstrs = [(f'{key}={harlech.values[leds[key]["lx"]]:.3f}') for key in ledKeys]
            # print( f"new values = {" ".join(vstrs)}")


        vv = 0
        @addSceneTask( act1, period = 4 )
        def nextDim():
            global vv
            vv = ((vv or 0) + 1) % 8
            for led in leds.values():
                lx = led['lx']
                value = ((lx + vv) % 8) / 7.0
                led['led'].set( value )
                # print( f"{value} for {led['led']}")


        #@addSceneTask( act1, period = None ) # 0.001 )
        #def hu():
         #   harlech._update()
            
                    
        # @addSceneTask( act1, period = 1 )
        def r2():            
            print( f"{main.when:0.3f} {main.cycle}  {rampEvery(5)} {stepEvery(5) } {blinkEvery(5) }")  
        

def demoMain(*args,**kwds):
    
    demo = HarlechLogicDemo( *args, **kwds )
    demo.run()