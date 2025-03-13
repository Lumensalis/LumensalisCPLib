

class I2CFactory(object):
    def __init__(self, main=None):
        self.main = main
    
        


class AdafruitFactory(I2CFactory):
    
    def createQTRotaryEncoder(self, *args, **kwds ):
        from .QTRotaryEncoder import QtRotary
        return QtRotary( *args, **kwds )
