from LumensalisCP.Main.Dependents import FactoryBase

class TerrainTronicsFactory(FactoryBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def addCaernarfon( self, config=None, **kwds ):
        from .Caernarfon import CaernarfonCastle
        return CaernarfonCastle( config=config, main=self.main, **kwds )
    
    def addHarlech( self, config=None, **kwds ):
        from .Harlech import HarlechCastle
        return HarlechCastle( config=config, main=self.main, **kwds )
    
    def addCilgerran( self, config=None, **kwds ):
        from .Cilgerran import CilgerranCastle
        return CilgerranCastle( config=config, main=self.main, **kwds )

    def addCaerphilly( self, config=None, **kwds ):
        from .Caerphilly import CaerphillyCastle
        return CaerphillyCastle( config=config, main=self.main, **kwds )

    def addHarlechXL( self, **kwds ):
        from .HarlechXL import HarlechXLCastle
        return HarlechXLCastle( main=self.main, **kwds )