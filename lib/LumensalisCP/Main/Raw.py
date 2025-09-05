from __future__ import annotations

from LumensalisCP.ImportProfiler import  getImportProfiler
import digitalio
_sayImport = getImportProfiler( __name__, globals() )

# pylint: disable=redefined-builtin,unused-variable,unused-argument,broad-exception-caught
# pyright: reportUnusedImport=false

from LumensalisCP.IOContext import *

from LumensalisCP.Main.Dependents import MainChild
from LumensalisCP.Triggers.Trigger import Trigger, TriggerActionTypeArg
from LumensalisCP.Triggers.Action import do
from LumensalisCP.Eval.Evaluatable import NamedEvaluatableProtocolT, NamedEvaluatableProtocol
from LumensalisCP.Scenes.Scene import Scene
from LumensalisCP.Identity.Proxy import proxyMethod, ProxyAccessibleClass

if TYPE_CHECKING:
    from LumensalisCP.Behaviors.Rotation import DCMotorSpinner

_sayImport.parsing()

import microcontroller, board
import pwmio


#############################################################################
# pyright: reportPrivateUsage=false

class RawPinWrapper( NliInterface ):
    def __init__(self,parent:RawAccess, pin: microcontroller.Pin) -> None:
        self.pin = pin
        assert pin not in parent._pins, f"pin {pin} already in use"
        parent._pins[pin] = self

class RawDigitalIOWrapper( RawPinWrapper ):
    class KWDS(TypedDict):
        drive_mode:NotRequired[digitalio.DriveMode]
        pull:NotRequired[digitalio.Pull]

    def __init__(self, parent:RawAccess, pin: microcontroller.Pin,
                 drive_mode:Optional[digitalio.DriveMode]=None,
                 pull:Optional[digitalio.Pull]=None
                 ) -> None:
        RawPinWrapper.__init__(self,  parent=parent, pin=pin)
        
        self._io = digitalio.DigitalInOut(pin)
        if drive_mode is not None:
            self._io.drive_mode = drive_mode
        if pull is not None:
            self._io.pull = pull

    def matchesKwds( self, **kwargs:Unpack[KWDS] ) -> bool:
        drive_mode = kwargs.get('drive_mode', None)
        pull = kwargs.get('pull', None)
        if drive_mode is not None and self._io.drive_mode != drive_mode:
            return False
        if pull is not None and self._io.pull != pull:
            return False
        return True
    
class RawDigitalIOInputWrapper( RawDigitalIOWrapper, InputSource ):
    class KWDS(RawDigitalIOWrapper.KWDS, InputSource.KWDS):
        pass

    def __init__(self, parent:RawAccess, pin: microcontroller.Pin, **kwargs:Unpack[KWDS]) -> None:

        RawDigitalIOWrapper.__init__(self,  parent=parent, pin=pin, **kwargs)
        kwargs.setdefault('temporaryName', f"{pin}")
        InputSource.__init__(self, **kwargs)
        
        self._io.direction = digitalio.Direction.INPUT

    def getDerivedValue(self, context:EvaluationContext) -> Any:
        return self._io.value

    def matchesKwds( self, **kwargs:Unpack[KWDS] ) -> bool:
        return super().matchesKwds(**kwargs)

class RawDigitalOutputWrapper( RawDigitalIOWrapper, NamedOutputTarget ):
    class KWDS(RawDigitalIOWrapper.KWDS, NamedOutputTarget.KWDS):
        pass

    def __init__(self, parent:RawAccess, pin: microcontroller.Pin, **kwargs:Unpack[KWDS]) -> None:

        RawDigitalIOWrapper.__init__(self,  parent=parent, pin=pin, **kwargs)
        kwargs.setdefault('temporaryName', f"{pin}")
        NamedOutputTarget.__init__(self, **kwargs)
        
        self._io.direction = digitalio.Direction.OUTPUT

    def set( self, value:Any, context:EvaluationContext ) -> None:
        self._io.value = value

class RawPWMOutputWrapper( RawPinWrapper, NamedOutputTarget ):
    DUTY_CYCLE_RANGE:int = 65535

    class KWDS( NamedOutputTarget.KWDS):
        duty_cycle: NotRequired[int]
        frequency: NotRequired[int] # = 500
        variable_frequency: NotRequired[bool] #= False

        pass

    def __init__(self, parent:RawAccess, pin: microcontroller.Pin, **kwargs:Unpack[KWDS]) -> None:

        RawPinWrapper.__init__(self,  parent=parent, pin=pin)
        kwargs.setdefault('temporaryName', f"{pin}")
        NamedOutputTarget.__init__(self, **kwargs)
        pKwds = { 
            'duty_cycle': kwargs.get('duty_cycle', 0),
            'frequency': kwargs.get('frequency', 500),
            'variable_frequency': kwargs.get('variable_frequency', False)   
        }
        self.pKwds = pKwds
        self.infoOut( f"{self.__class__.__name__} on pin {pin}, pKwds: {pKwds}" )
        self.pin = pin 
        self._io = pwmio.PWMOut(pin, **pKwds)

    def set( self, value:Any, context:EvaluationContext ) -> None:
        
        duty_cycle = int( withinZeroToOne(value)* self.DUTY_CYCLE_RANGE)
        if self.enableDbgOut:
            self.dbgOut( f"setting {self.pin}duty_cycle to {duty_cycle} for {value}" )
        self._io.duty_cycle = duty_cycle


    def matchesKwds( self, **kwargs:Unpack[KWDS] ) -> bool:
        duty_cycle = kwargs.get('duty_cycle', None)
        frequency = kwargs.get('frequency', None)
        variable_frequency = kwargs.get('variable_frequency', None)
        if duty_cycle is not None and self.pKwds['duty_cycle'] != duty_cycle:
            return False
        if frequency is not None and self.pKwds['frequency'] != frequency:
            return False
        if variable_frequency is not None and self.pKwds['variable_frequency'] != variable_frequency:
            return False
        return True
    
    @property
    def duty_cycle(self) -> int:
        """ the current duty cycle of the LED """
        return self._io.duty_cycle

class RawAccess( MainChild ):
    """ deal directly with Controller IO

    """
    class KWDS(MainChild.KWDS):
        useSliders:NotRequired[bool]

    def __init__( self, useSliders:bool = False, **kwds:Unpack[MainChild.KWDS] ) -> None: 
        super().__init__( **kwds )

        self._pins:dict[microcontroller.Pin, RawPinWrapper] = {}

        #self._controlVariables:NliList[PanelControl[Any,Any]] = NliList(name='controls',parent=self)
        #self._monitored:NliList[PanelMonitor[Any]] = NliList(name='monitored',parent=self)
        #self._triggers:NliList[PanelTrigger] = NliList(name='triggers',parent=self)


    def getDigitalInput( self, pin:microcontroller.Pin,
                         **kwargs:Unpack[RawDigitalIOInputWrapper.KWDS]
            ) -> RawDigitalIOInputWrapper :
        io = self._pins.get(pin,None)
        if io is None:
            io = RawDigitalIOInputWrapper(parent=self, pin=pin)
            self._pins[pin] = io
        else:
            assert isinstance(io, RawDigitalIOInputWrapper)
            assert io.matchesKwds(**kwargs)
        return io
    
    def getDigitalOutput( self, pin:microcontroller.Pin, 
            **kwargs:Unpack[RawDigitalOutputWrapper.KWDS]
              ) -> RawDigitalOutputWrapper :
        io = self._pins.get(pin,None)
        if io is None:
            io = RawDigitalOutputWrapper(parent=self, pin=pin, **kwargs)
            self._pins[pin] = io
        else:
            assert isinstance(io, RawDigitalOutputWrapper)
            assert io.matchesKwds(**kwargs)
        return io
        
    def getPWMOutput( self, pin:microcontroller.Pin, 
            **kwargs:Unpack[RawPWMOutputWrapper.KWDS]
              ) -> RawPWMOutputWrapper :
        io = self._pins.get(pin,None)
        if io is None:
            io = RawPWMOutputWrapper(parent=self, pin=pin, **kwargs)
            self._pins[pin] = io
        else:
            assert isinstance(io, RawPWMOutputWrapper)
            assert io.matchesKwds(**kwargs)
        return io    

    
    def dcMotor( self, ia:microcontroller.Pin, ib:microcontroller.Pin, **kwargs:Unpack[RawPWMOutputWrapper.KWDS] ) -> DCMotorSpinner:

        """ return (inputA,inputB,speed) """

        a = self.getPWMOutput( ia, **kwargs )
        b = self.getPWMOutput( ib, **kwargs )

        kwargs.setdefault('duty_cycle', 0)
        kwargs.setdefault('frequency', 2000) # default to 2000Hz

        from LumensalisCP.Behaviors.Rotation import DCMotorSpinner
        motorArgs, outputArgs = DCMotorSpinner.extractMotorKwds(kwargs)
        rv = DCMotorSpinner(a, b, **motorArgs)

        return rv
    
    #########################################################################

    def nliGetContainers(self) -> NliGetContainersRVT:
        yield self._controlVariables
        yield self._monitored
        yield self._triggers

    def nliHasContainers(self) -> bool:
        return True

        
__all__ = [ 'RawAccess' ]

_sayImport.complete(globals())