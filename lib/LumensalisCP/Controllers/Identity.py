from LumensalisCP.common import *
from LumensalisCP.CPTyping import *
import os, sys, json
import microcontroller
import binascii
import board
import adafruit_24lc32 # pyright: ignore[reportMissingImports]
from adafruit_bus_device.i2c_device import I2CDevice
from LumensalisCP.Main.PreMainConfig import pmc_mainLoopControl

if TYPE_CHECKING:
    from nvm import ByteArray

class ControllerNVM(object):
    MAGIC = b"LCP"
    SIZE = 1024
    SPANS = dict(
        PROJECT=(5,105),
    )
    
    def __init__(self, nvm = microcontroller.nvm ):
        assert nvm is not None
        self.__nvm: ByteArray = nvm

    
    @property 
    
    def nvm(self): return self.__nvm
    

    def _nvmClear(self, span:str|Tuple[int,int] ):
        span = self.SPANS[span] if type(span) is str else span
        start, end = span
        self.__nvm[start:end] = b"\x00" * (end-start)

    def _nvmSetStr(self, span:str|Tuple[int,int], value:str ):
        span = self.SPANS[span] if type(span) is str else span
        start, end = span
        ensure( len(value) <= end-start, "string too long" )
        self._nvmClear(span)
        self.__nvm[start:start+len(value)] = bytes(value.encode())

    def _nvmGetStr(self, span:str|Tuple[int,int] ):
        span = self.SPANS[span] if type(span) is str else span
        start, end = span
        asBytes = self.__nvm[start:end]
        asStr = str( asBytes.decode() )
        return asStr[0:asStr.index("\0")]
            
    def initialize(self, overwrite:bool = False ):
        if self.isInitialized and not overwrite:
            raise RuntimeError( "NVM already initialized" )
            
        l = len(self.__nvm)
        self._nvmClear( (0,l) )
        self.__nvm[0:len(self.MAGIC)] = self.MAGIC

    @property
    def magic(self):
        return str(self.__nvm[0:len(self.MAGIC)])

    @property
    def isInitialized(self)->bool:
        magicContent = self.__nvm[0:len(self.MAGIC)]
        if magicContent != self.MAGIC:
            print( f"magic mismatch : {magicContent} != {self.MAGIC}")
        return magicContent == self.MAGIC

    @property
    def project(self):
        return self._nvmGetStr( "PROJECT" )

    @project.setter
    def project(self, name:str ):
        ensure( self.isInitialized, "must initialize NVM before setting project")
        self._nvmSetStr( "PROJECT", name) 


    def writeI2C(
        self,
        start: int,
        data: bytearray,
    ) -> None:
        buffer = bytearray(2)
        data_length = len(data)
        nvm = self.__nvm
        max_size = nvm._max_size
        
        
        if (start + data_length) > max_size:
                raise ValueError(
                    "Starting address + data length extends beyond"
                    " EEPROM maximum address. Use ``write_wraparound`` to"
                    " override this warning."
                )
        
        with nvm._i2c as i2c:
            for i in range(0, data_length):
                assert  (start + i) < max_size
                #buffer[0] = (start + i) >> 8
                buffer[0] = (start + i) & 0xFF
                #i2c.write(buffer)
                buffer[1] = data[i]
                i2c.write(buffer)

    
    def readI2C(self,start:int, end:int):
        write_buffer = bytearray(1)
        #write_buffer[0] = start >> 8
        write_buffer[0] = start & 0xFF
        read_buffer = bytearray(end-start)
        with self.__nvm._i2c as i2c:
            # i2c: I2CDevice
            i2c.write_then_readinto(write_buffer, read_buffer)
            
        print(f"wrote {write_buffer}, read {read_buffer}" )
        return read_buffer
    
class ControllerIdentity(object):
    def __init__(self, main):
        processorUid = microcontroller.cpu.uid
        if pmc_mainLoopControl.preMainVerbose: print( f"processorUid({type(processorUid)}) = {processorUid}")
        self.processorUid = binascii.hexlify(processorUid).decode('utf-8')

        try:
            with open('/configByCUID.json','r') as f:
                configs = json.load(f)
                self.CUIDConfig = configs.get( self.processorUid,None )
                
        except:
            self.CUIDConfig = {}

        self.envProject = os.getenv("project",None)
        nvm = ControllerNVM(microcontroller.nvm)
        self.controllerNVM = nvm
        self.controllerNVMProject = nvm.project if nvm.isInitialized else None

        
        if 1:
            self.i2cNVM = main.identityI2C
        else:
            try:
                i2c = main.defaultI2C
                eeprom = adafruit_24lc32.EEPROM_I2C(i2c_bus=i2c, max_size=1024)
                self.i2cNVM = ControllerNVM( eeprom[0:len(eeprom)] )
                del eeprom
            except Exception as inst:
                SHOW_EXCEPTION( inst, f"I2C identity exception ")
                self.i2cNVM = None
            
        self.i2cNVMProject = self.i2cNVM.project if self.i2cNVM is not None and self.i2cNVM.isInitialized else None
            
        self.project = (
                   self.i2cNVMProject or
                   self.controllerNVM.project
                   or self.CUIDConfig.get('project',None) 
                   or self.envProject 
                   or None
        )
