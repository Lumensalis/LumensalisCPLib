
import LumensalisCP.Main
from LumensalisCP.common import *
from  .Config import ControllerConfig
from  .Configs.Core import getConfig
import LumensalisCP.Main
from  LumensalisCP.Main.Dependents import MainChild
import os, board, microcontroller
if TYPE_CHECKING:
    import LumensalisCP.Main.Manager
    
class ConfigurableBase(object):
    
    def __init__(self, config=None, defaults:Optional[dict]=None, **kwds ):
        if configSecondary := config == "secondary":
            config = None
            
        if config is None:
            config = os.getenv("TTCP_CONTROLLER")
            if config is None:
                config = board.board_id # type : ignore
                
        if configSecondary:
            ensure( config is not None, "auto config lookup failed" )
            config = config + "_secondary"
            
        if type(config) is str:
            configForName = getConfig(config)
            assert configForName is not None, f"no configuration exists for {config}"
            config = configForName.copy()
        elif config is None:
            config = ControllerConfig()
        
        assert type(config) is ControllerConfig
        if defaults is not None:
            kwds = dict(kwds)
            for tag,val in defaults.items():
                kwds.setdefault(tag,val)

        config.bake( **kwds )
        self.config = config


    def asPin(self, pin ):
        if not isinstance( pin, microcontroller.Pin ):
            if hasattr( pin, 'actualPin' ):
                pin = pin.actualPin
            if type(pin) is str:
                assert self.config.pins is not None
                pin =  self.config.pins.lookupPin(pin) 
            
        assert isinstance( pin, microcontroller.Pin )
        return pin
    
class ControllerConfigurableChildBase(ConfigurableBase,MainChild):
    def __init__( self, main:LumensalisCP.Main.Manager.MainManager, name:Optional[str]=None, **kwargs ):
        MainChild.__init__(self, main=main, name=name )
        ConfigurableBase.__init__( self, **kwargs )
        #print( f"ControllerConfigurableChildBase.__init__( name={name} kwargs={kwargs})")