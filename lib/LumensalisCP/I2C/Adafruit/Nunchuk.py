from __future__ import annotations

import adafruit_nunchuk

from LumensalisCP.I2C.common import *

# pyright: reportPrivateUsage=false

class NunchukInput(I2CInputSource):
    def __init__( self, target:Nunchuk,  startValue:Any, **kwargs:Unpack[I2CInputSource.KWDS] ):
        super().__init__( target, **kwargs)
        self.nunchukVal:Any = startValue

    @final
    def getDerivedValue(self, context:EvaluationContext) -> bool: # pylint: disable=unused-argument
        return self.nunchukVal

    def setNunchukValue( self, val:Any, context:EvaluationContext ) -> bool:
        self.nunchukVal = val
        return self.updateValue( context ) 

class NunchukChild:
    def __init__( self, nunchuk:Nunchuk, **kwds:Any ):
        for name,startValue in kwds.items():
            setattr( self, name, NunchukInput( nunchuk, startValue, name=name ) )

class Joy(NunchukChild):
    x:NunchukInput
    y:NunchukInput

    def __init__( self, nunchuk:Nunchuk ):
        super().__init__(nunchuk, x=0, y=0)

class Accel(NunchukChild):
    ax:NunchukInput
    ay:NunchukInput
    az:NunchukInput
    def __init__( self, nunchuk:Nunchuk ):
        super().__init__(nunchuk, ax=0, ay=0, az=0)

class Buttons(NunchukChild):
    c:NunchukInput
    z:NunchukInput
    def __init__( self, nunchuk:Nunchuk ):
        super().__init__(nunchuk, c=0, z=0)



class Mapper :
    
    """
    Maps a number from one range to another.
    Note: This implementation handles values < in_min differently than arduino's map function does.

    :return: Returns value mapped to new range
    :rtype: float
    """
    def __init__(self,  in_min: float, in_max: float, out_min: float, out_max: float) -> None:
        self.in_min = in_min
        self.in_max = in_max
        self.out_min = out_min
        self.out_max = out_max
        self.in_range = in_max - in_min
        self.out_range = out_max - out_min


    def __call__(self, x: float) -> float:

        in_delta = x - self.in_min
        if self.in_range != 0:
            mapped = in_delta / self.in_range
        elif in_delta != 0:
            mapped = in_delta
        else:
            mapped = 0.5
        mapped *= self.out_range
        mapped += self.out_min
        if self.out_min <= self.out_max:
            return max(min(mapped, self.out_max), self.out_min)
        return min(max(mapped, self.out_max), self.out_min)



class Nunchuk(I2CDevice,):
    
    def __init__(self, **kwds:Unpack[I2CDevice.KWDS] ) -> None:
        I2CDevice.__init__( self,   **kwds )

        self.nunchuk = adafruit_nunchuk.Nunchuk(self.i2c)

        self.joystick = Joy( self )
        self.accel = Accel( self )
        self.buttons = Buttons( self )
        self._jMap = Mapper( 0, 255, -1, +1 )

    def derivedUpdateDevice(self, context:EvaluationContext) -> bool:
        """Override this method to implement the device update logic.
        Return True if changes were detected
        """

        self.nunchuk._read_data() # pylint: disable=protected-access    

        buf = self.nunchuk.buffer  
        changes:int = 0
        changes += self.joystick.x.setNunchukValue( self._jMap( buf[0] ), context )
        changes += self.joystick.y.setNunchukValue( self._jMap( buf[1] ), context )

        changes += self.accel.ax.setNunchukValue(  ((buf[5] & 0xC0) >> 6) | (buf[2] << 2), context )
        changes += self.accel.ay.setNunchukValue(  ((buf[5] & 0x30) >> 4) | (buf[3] << 2), context )
        changes += self.accel.az.setNunchukValue(  ((buf[5] & 0x0C) >> 2) | (buf[4] << 2), context )

        button_c = 1 if not bool(buf[5] & 0x02) else 0
        button_z = 1 if not bool(buf[5] & 0x01) else 0
        changes += self.buttons.c.setNunchukValue( button_c, context )
        changes += self.buttons.z.setNunchukValue( button_z, context )
        if self.enableDbgOut: 
            self.dbgOut( f"derivedUpdateDevice: changes={changes}, c={button_c}, z={button_z}, buf={buf.hex()}")

        return changes > 0

