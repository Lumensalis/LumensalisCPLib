
from LumensalisCP.Main.Manager import MainManager

class Initializer( object ):
    def __init__(self  ):
        self.main = MainManager.initOrGetManager()

    @property
    def espNVM(self): return self.main.identity.controllerNVM

    @property
    def i2cNVM(self): return self.main.identity.i2cNVM
    
    def initialize(self, quiet:bool = False ):
        if self.espNVM.isInitialized:
            if not quiet: print( "espNVM already initialized" )
        else:
            print( "initializing espNVM" )
            self.espNVM.initialize()

        if self.i2cNVM is None:
            print( "no i2cNVM found" )
        else:
            if self.i2cNVM.isInitialized:
                if not quiet: print( "i2cNVM already initialized" )
            else:
                print( "initializing i2cNVM" )
                self.i2cNVM.initialize()
    @property
    def project(self):
        return self.i2cNVM.project if self.i2cNVM is not None else self.espNVM.project
    
    def _setNVM( self, tag:str, value:str ):
        self.initialize()
        nvmName = 'i2cNVM' if self.i2cNVM is not None else 'espNVM'
        nvm = getattr( self, nvmName )
        print( f"setting {nvmName} {tag} to {repr(value)}" )
        setattr(nvm,tag,value)
            
    @project.setter
    def project(self,name:str):
        self._setNVM("project",name)
