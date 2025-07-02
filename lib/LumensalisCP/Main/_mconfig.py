############################################################################
## INTERNAL USE ONLY

import supervisor

class _MainLoopControl(object):
    
    def __init__(self):
        self.__started = supervisor.ticks_ms()
        self.MINIMUM_LOOP = False
        self.ENABLE_PROFILE = False
    
    def getMsSinceStart(self):
        now = supervisor.ticks_ms()
        return now - self.__started
    
_mlc = _MainLoopControl()