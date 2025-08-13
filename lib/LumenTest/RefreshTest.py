from .MainStub import *
import time
main = MainStub()
scene = main.addScene( ) 

class PeriodicTest:
    def __init__(self,scene:Scene,name:str,refreshRate:TimeSpanInSeconds) -> None:
        self.refreshRate = refreshRate
        self.hitTimes:list[TimeInSeconds] = []
        self.task = scene.addTask(task=self.hit, name=name,refreshRate=refreshRate)

    def hit(self) -> None:
        self.hitTimes.append(main.getContext().when)

    def __repr__(self) -> str:
        fails = 0
        if len(self.hitTimes) > 1:
            prior = self.hitTimes[0]
            minRateDrift = self.refreshRate * 0.1
            for hit in self.hitTimes[1:]:
                diff = hit - prior
                drift = abs(diff - self.refreshRate)
                #print( f"  hit at {hit:.3f}, diff={diff:.3f}, drift={drift:.3f}" )
                if drift > minRateDrift:
                    fails += 1
                prior = hit
            

        return f"PeriodicTest(fails={fails}, hits={len(self.hitTimes)}, refreshRate={self.refreshRate}, hitTimes={self.hitTimes})"

t2 = PeriodicTest(  scene, "t2", refreshRate = 0.007 )
t1 = PeriodicTest(  scene, "t1", refreshRate = 0.3 )

if False:
    scene.enableDbgOut = True
    scene._sceneRefreshables.enableDbgOut = True
    t1.task.enableDbgOut = True
    t2.task.enableDbgOut = True
    main._refreshables.enableDbgOut = True

for x in range( 300 ):
    if x % 10 == 0:
        print( f"{main.getContext().when:.4f} step {x} advancing " )
        for r in main._refreshables: 
            print( f"  {repr(r)} : nextRefresh={r.nextRefresh:.4f}" )
            if isinstance(r, Scene):
                for r2 in r._sceneRefreshables:
                    print( f"     {repr(r2)} : nextRefresh={r2.nextRefresh:.4f}" )
    main.step(next=0.01)

print( f"t1Times = {t1}" )
print( f"t2Times = {t2}" )
import json 
#print(  json.dumps( main.getProfilerData() ))