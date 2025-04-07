from LumensalisCP.Main.Dependents import FactoryBase
from .Caernarfon import CaernarfonCastle
from .Harlech import HarlechCastle
from .Cilgerran import CilgerranCastle
from .Caerphilly import CaerphillyCastle

class TerrainTronicsFactory(FactoryBase):
    def addCaernarfon( self, config=None, **kwds ) -> CaernarfonCastle: pass
    def addHarlech( self, config=None, **kwds ) -> HarlechCastle: pass
    def addCilgerran( self, config=None, **kwds ) -> CilgerranCastle:pass
    def addCaerphilly( self, config=None, **kwds ) -> CaerphillyCastle:pass