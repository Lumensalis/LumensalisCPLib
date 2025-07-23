from __future__ import annotations

import os, board, microcontroller

from LumensalisCP.Main.Dependents import MainChild
from LumensalisCP.common import *
from LumensalisCP.Controllers.Config import ControllerConfig,ControllerConfigArg
from LumensalisCP.Controllers.Configs.Core import getConfig

if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    
class ConfigurableBase(object):
    class KWDS( TypedDict ):
        config: NotRequired[ControllerConfigArg]
        defaults: NotRequired[dict[str, Any]]
        
    def __init__(self, config:Optional[ControllerConfigArg]=None, defaults:Optional[StrAnyDict]=None, **kwds:StrAnyDict ):
        if configSecondary := config == "secondary":
            config = None
            
        if config is None:
            config = os.getenv("TTCP_CONTROLLER")
            if config is None:
                config = board.board_id # type: ignore # pylint: disable=no-member
                
        if configSecondary:
            ensure( config is not None, "auto config lookup failed" )
            assert isinstance(config, str)
            config = config + "_secondary"
            
        if isinstance(config, str):
            configForName = getConfig(config)
            assert configForName is not None, f"no configuration exists for {config}"
            config = configForName.copy()
        elif config is None:
            config = ControllerConfig()
        
        assert isinstance(config, ControllerConfig)
        if defaults is not None:
            kwds = dict(kwds)
            for tag,val in defaults.items():
                kwds.setdefault(tag,val)

        config.bake( **kwds )
        self.config:ControllerConfig = config


    def asPin(self, pin:Union[microcontroller.Pin,str]) -> microcontroller.Pin:
        if not isinstance( pin, microcontroller.Pin ):

            if isinstance(pin, str): # type: ignore
                assert self.config.pins is not None
                pin =  self.config.pins.lookupPin(pin) 
            elif hasattr( pin, 'actualPin' ):
                assert isinstance( pin.actualPin, microcontroller.Pin )
                pin = pin.actualPin
            
        assert isinstance( pin, microcontroller.Pin )
        return pin
    
class ControllerConfigurableChildBase(ConfigurableBase,MainChild):
    class KWDS( ConfigurableBase.KWDS ):
        name: NotRequired[str]
        main: NotRequired[MainManager]
        
    def __init__( self, main:Optional[MainManager]=None, name:Optional[str]=None, **kwargs:Unpack[ConfigurableBase.KWDS] ):
        if main is None:
            main = getMainManager()
        MainChild.__init__(self, main=main, name=name )
        ConfigurableBase.__init__( self, **kwargs ) # type: ignore
        #print( f"ControllerConfigurableChildBase.__init__( name={name} kwargs={kwargs})")