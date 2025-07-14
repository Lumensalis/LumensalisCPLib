from LumensalisCP.Main.Dependents import FactoryBase

class TerrainTronicsFactory(FactoryBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def addCaernarfon( self, config=None, **kwds ):
        from .Caernarfon import CaernarfonCastle
        return self.makeChild( CaernarfonCastle, config=config, **kwds )
    
    def addHarlech( self, config=None, **kwds ):
        from .Harlech import HarlechCastle
        return self.makeChild( HarlechCastle, config=config, **kwds )
    
    def addCilgerran( self, config=None, **kwds ):
        from .Cilgerran import CilgerranCastle
        return self.makeChild( CilgerranCastle, config=config, **kwds )

    def addCaerphilly( self, config=None, **kwds ):
        from .Caerphilly import CaerphillyCastle
        return self.makeChild( CaerphillyCastle, config=config, **kwds )

    def addHarlechXL( self, **kwds ):
        from .HarlechXL import HarlechXLCastle
        return self.makeChild( HarlechXLCastle, **kwds )
        