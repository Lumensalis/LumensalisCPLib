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
from LumensalisCP.util.Reloadable import reloadingMethod, ReloadableClass, addReloadableClass

from LumensalisCP.Main import RawRL

if TYPE_CHECKING:
    from LumensalisCP.Behaviors.Rotation import DCMotorSpinner

_sayImport.parsing()

import microcontroller, board
import pwmio, pulseio
import analogio



#############################################################################
# pyright: reportPrivateUsage=false

class RawPinWrapper( NliInterface ):
    class KWDS(TypedDict):
        pass

    def __init__(self,parent:RawAccess, pin: microcontroller.Pin) -> None:
        self.pin = pin
        assert pin not in parent._pins, f"pin {pin} already in use"
        parent._pins[pin] = self

    def matchesKwds( self, **kwargs:Any ) -> bool:
        return True

class RawDigitalIOWrapper( RawPinWrapper ):
    class KWDS(RawPinWrapper.KWDS):
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

        RawDigitalIOWrapper.__init__(self,  parent=parent, pin=pin, **kwargs) # type: ignore
        kwargs.setdefault('temporaryName', f"{pin}")
        InputSource.__init__(self, **kwargs)
        
        self._io.direction = digitalio.Direction.INPUT

    def getDerivedValue(self, context:EvaluationContext) -> Any:
        return self._io.value

    def matchesKwds( self, **kwargs:Any ) -> bool:
        return super().matchesKwds(**kwargs)

class RawDigitalOutputWrapper( RawDigitalIOWrapper, NamedOutputTarget ):
    class KWDS(RawDigitalIOWrapper.KWDS, NamedOutputTarget.KWDS):
        pass

    def __init__(self, parent:RawAccess, pin: microcontroller.Pin, **kwargs:Unpack[KWDS]) -> None:

        RawDigitalIOWrapper.__init__(self,  parent=parent, pin=pin, **kwargs) # type: ignore
        kwargs.setdefault('temporaryName', f"{pin}")
        NamedOutputTarget.__init__(self, **kwargs)
        
        self._io.direction = digitalio.Direction.OUTPUT

    def set( self, value:Any, context:EvaluationContext ) -> None:
        self._io.value = value

#############################################################################

class RawPWMOutputWrapper( RawPinWrapper, NamedOutputTarget ):
    DUTY_CYCLE_RANGE:int = 65535

    class KWDS( NamedOutputTarget.KWDS):
        duty_cycle: NotRequired[int]
        frequency: NotRequired[int] # = 500
        variable_frequency: NotRequired[bool] #= False

        pass

    def __init__(self, parent:RawAccess, pin: microcontroller.Pin, **kwargs:Unpack[KWDS]) -> None:

        RawPinWrapper.__init__(self,  parent=parent, pin=pin)
        kwargs.setdefault('temporaryName', NliMakeValidName(f"{pin}"))
        NamedOutputTarget.__init__(self, **kwargs)
        pKwds = { 
            'duty_cycle': kwargs.get('duty_cycle', 0),
            'frequency': kwargs.get('frequency', 500),
            'variable_frequency': kwargs.get('variable_frequency', False)   
        }
        self.pKwds = pKwds
        self.infoOut( f"{self.__class__.__name__} on pin {pin}, pKwds: {pKwds}" )
        self.pin = pin 
        self._io = pwmio.PWMOut(pin, **pKwds) # type: ignore

    def set( self, value:Any, context:EvaluationContext ) -> None:
        
        duty_cycle = int( withinZeroToOne(value)* self.DUTY_CYCLE_RANGE)
        if self.enableDbgOut:
            self.dbgOut( f"setting {self.pin}duty_cycle to {duty_cycle} for {value}" )
        self._io.duty_cycle = duty_cycle


    def matchesKwds( self, **kwargs:Any ) -> bool:
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

#############################################################################

#@ReloadableClass()
class RawPWMInputWrapper( RawPinWrapper, InputSource ):
    DUTY_CYCLE_RANGE:int = 65535

    class KWDS( RawPinWrapper.KWDS, InputSource.KWDS):
        #duty_cycle: NotRequired[int]
        #frequency: NotRequired[int] # = 500
        #variable_frequency: NotRequired[bool] #= False

        pass

    def __init__(self, parent:RawAccess, pin: microcontroller.Pin, **kwargs:Unpack[KWDS]) -> None:

        RawPinWrapper.__init__(self,  parent=parent, pin=pin)
        kwargs.setdefault('temporaryName', f"{pin}")

        InputSource.__init__(self, **kwargs)
        #self.digitalIn = digitalio.DigitalInOut(pin)
        #self.digitalIn.direction = digitalio.Direction.INPUT    
        #self.digitalIn.pull = digitalio.Pull.UP
        #self.digitalIn.deinit()

        self.pulseIn = pulseio.PulseIn(pin, maxlen=128, idle_state=False)
        pinName = getattr( kwargs, 'name', str(pin).replace('.','_')) 
        self.pulsesDetected = SimpleInputSource( 0, name=pinName+'_pulsesDetected' )
        self.readCycles = SimpleInputSource( 0, name=pinName+'_readCycles' )

        self._internalData = {
                'cycles': 0,
                'pulsesDetected': 0,
                'onCount': 0,
                'offCount': 0,
                'onTotal': 0,
                'offTotal': 0,
                'lastState': None,
            }

    #@reloadingMethod
    def getDerivedValue(self, context:EvaluationContext) -> Any:
        #raise NotImplementedError
        return RawRL.RawPWMInputWrapper_getDerivedValue(self, context)

    def matchesKwds( self, **kwargs:Unpack[KWDS] ) -> bool:
        return super().matchesKwds(**kwargs)
            
    #@reloadingMethod
    def rl( self, context:Optional[EvaluationContext]=None )  -> None:  
        RawRL.RawPWMInputWrapper_rl(self, context)

    #@reloadingMethod
    def boop( self, context:Optional[EvaluationContext]=None )  -> None:
        #raise NotImplementedError  
        RawRL.RawPWMInputWrapper_boop(self, context)

addReloadableClass(RawPWMInputWrapper, RawRL)
#############################################################################


class RawAnalogInputWrapper( RawPinWrapper, InputSource ):
    class KWDS(InputSource.KWDS):
        pass

    def __init__(self, parent:RawAccess, pin: microcontroller.Pin, **kwargs:Unpack[KWDS]) -> None:

        RawPinWrapper.__init__(self,  parent=parent, pin=pin)
        kwargs.setdefault('temporaryName', f"{pin}")
        InputSource.__init__(self, **kwargs)
        
        self._io = analogio.AnalogIn(pin)

    def getDerivedValue(self, context:EvaluationContext) -> Any:
        return self._io.value
    

#############################################################################
RPW_T=TypeVar('RPW_T', bound=RawPinWrapper)

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

    def _addIO( self, cls:Type[RPW_T], pin:microcontroller.Pin,
                         **kwargs:Unpack[RawPinWrapper.KWDS] ) -> RPW_T :

        io = self._pins.get(pin,None)
        if io is None:
            io = cls(parent=self, pin=pin, **kwargs)
            self._pins[pin] = io
        else:
            assert isinstance(io, cls)
            assert io.matchesKwds(**kwargs)            
        return io

    #########################################################################

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
        
    #########################################################################

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

    def getPWMInput( self, pin:microcontroller.Pin,
                         **kwargs:Unpack[RawPWMInputWrapper.KWDS]
            ) -> RawPWMInputWrapper :
        return self._addIO( RawPWMInputWrapper, pin, **kwargs )

    #########################################################################

    def getAnalogInput( self, pin:microcontroller.Pin,
                         **kwargs:Unpack[RawAnalogInputWrapper.KWDS]
            ) -> RawAnalogInputWrapper :
        return self._addIO( RawAnalogInputWrapper, pin, **kwargs )

    #########################################################################

    def dcMotor( self, ia:microcontroller.Pin, ib:microcontroller.Pin, **kwargs:Unpack[RawPWMOutputWrapper.KWDS] ) -> DCMotorSpinner:

        """ return (inputA,inputB,speed) """

        from LumensalisCP.Behaviors.Rotation import DCMotorSpinner
        motorArgs, outputArgs = DCMotorSpinner.extractMotorKwds(kwargs)

        a = self.getPWMOutput( ia, **outputArgs )
        b = self.getPWMOutput( ib, **outputArgs )

        kwargs.setdefault('duty_cycle', 0)
        kwargs.setdefault('frequency', 2000) # default to 2000Hz

        rv = DCMotorSpinner(a, b, **motorArgs)

        return rv
    
    #########################################################################

    #def nliGetContainers(self) -> NliGetContainersRVT:
    #    yield self._controlVariables
    #    yield self._monitored
    #    yield self._triggers

    #def nliHasContainers(self) -> bool:
    #    return True

        
__all__ = [ 'RawAccess' ]

_sayImport.complete(globals())