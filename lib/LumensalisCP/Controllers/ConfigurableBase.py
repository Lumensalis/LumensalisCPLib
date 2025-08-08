from __future__ import annotations

import os, board, microcontroller

from LumensalisCP.ImportProfiler import  getImportProfiler
_sayConfigurableBaseImport = getImportProfiler( __name__, globals() )

from LumensalisCP.Main.Dependents import MainChild
from LumensalisCP.common import *
_sayConfigurableBaseImport( "Controllers.Config" )
from LumensalisCP.Controllers.Config import ControllerConfig,ControllerConfigArg

_sayConfigurableBaseImport( "Controllers.Configs.Core" )
from LumensalisCP.Controllers.Configs.Core import getConfig

if TYPE_CHECKING:
    from LumensalisCP.Shields.Pins import PinProxy

    
_sayConfigurableBaseImport( "parsing" )    
class ConfigurableBase(CountedInstance):
    class KWDS( TypedDict ):
        config: NotRequired[ControllerConfigArg]
        defaults: NotRequired[dict[str, Any]]
        
    @staticmethod 
    def extractInitArgs(kwds:dict[str,Any]|Any) -> dict[str,Any]:
        return {
            'config': kwds.pop('config', None),
            'defaults': kwds.pop('defaults', None)
        }
            
    def __init__(self, config:Optional[ControllerConfigArg]=None, defaults:Optional[StrAnyDict]=None, **kwds:StrAnyDict ):
        super().__init__()
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
        
        assert isinstance(config, ControllerConfig), f"config must be ControllerConfig, not {type(config)}: {config}" 
        if defaults is not None:
            kwds = dict(kwds)
            for tag,val in defaults.items():
                kwds.setdefault(tag,val)

        config.bake( **kwds )
        self.config:ControllerConfig = config


    def asPin(self, pin:Union[microcontroller.Pin,str,PinProxy]) -> microcontroller.Pin:
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
    class KWDS( ConfigurableBase.KWDS, MainChild.KWDS ):
        pass        
    def __init__( self, **kwargs:Unpack[KWDS] ):
        cfgKwds =  ConfigurableBase.extractInitArgs(kwargs)
        MainChild.__init__(self, **kwargs  )
        ConfigurableBase.__init__( self, **cfgKwds ) # type: ignore
        #print( f"ControllerConfigurableChildBase.__init__( name={name} kwargs={kwargs})")

_sayConfigurableBaseImport.complete(globals())
