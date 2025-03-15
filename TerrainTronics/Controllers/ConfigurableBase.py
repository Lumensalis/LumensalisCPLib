
import TerrainTronics.Controllers
from  TerrainTronics.Controllers import ControllerConfig
import os


class ConfigurableBase(object):
    
    def __init__(self, config=None, defaults:dict=None, **kwds ):
        if config is None:
            config = os.getenv("TTCP_CONTROLLER")
            
        if type(config) is str:
            config = TerrainTronics.Controllers.configs[config].copy()
        elif config is None:
            config = ControllerConfig()
        
        assert type(config) is ControllerConfig
        if defaults is not None:
            kwds = dict(kwds)
            for tag,val in defaults.items():
                kwds.setdefault(tag,val)

        config.bake( **kwds )
        self.config = config
