from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
from ..Config import ControllerConfig

configs = {
    'lolin_s2_mini' : ControllerConfig(
        TX = "GPIO39",
        RX = "GPIO37",
        D1 = "GPIO35", #SCL
        D2 = "GPIO33", #SDA
        D3 = "GPIO18",
        D4 = "GPIO16",
        
        A0 = "GPIO3",
        D0 = "GPIO5",
        D5 = "GPIO7",
        D6 = "GPIO9",
        D7 = "GPIO11",
        D8 = "GPIO12",
     ),
    
     'lolin_s2_mini_secondary' : ControllerConfig(
        TX = "GPIO40",
        RX = "GPIO38",
        D1 = "GPIO36", #SCL
        D2 = "GPIO34", #SDA
        D3 = "GPIO21",
        D4 = "GPIO17",
        
        A0 = "GPIO2",
        D0 = "GPIO4",
        D5 = "GPIO6",
        D6 = "GPIO8",
        D7 = "GPIO10",
        D8 = "GPIO13",
     ),
     
    'lilygo_ttgo_t-oi-plus' :  ControllerConfig(
        TX = "GPIO21",
        RX = "GPIO20",
        D1 = "GPIO19", #SCL
        D2 = "GPIO18", #SDA
        D3 = "GPIO9",
        D4 = "GPIO8",
        
        A0 = "GPIO2",
        D0 = "GPIO4",
        D5 = "GPIO5",
        D6 = "GPIO6",
        D7 = "GPIO7",
        D8 = "GPIO10",
     ),
    
    'lolin_s3_mini' : ControllerConfig(
        TX = "GPIO43",
        RX = "GPIO44",
        D1 = "GPIO36", #SCL
        D2 = "GPIO35", #SDA
        D3 = "GPIO18",
        D4 = "GPIO16",
        
        A0 = "GPIO2",
        D0 = "GPIO4",
        D5 = "GPIO12",
        D6 = "GPIO13",
        D7 = "GPIO11",
        D8 = "GPIO10",
     ),
    
}

configs['WemosS2Mini'] = configs['lolin_s2_mini']

def getConfig( name:str ):

    return configs.get(name,None)