from LumensalisCP.Main.Dependents import FactoryBase

class TerrainTronicsFactory(FactoryBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def addCaernarfon( self, config=None, **kwds ):
        from .Caernarfon import CaernarfonCastle
        castle = CaernarfonCastle( config=config, main=self.main, **kwds )
        self.main._boards.append(castle)
        return castle
    
    def addHarlech( self, config=None, **kwds ):
        from .Harlech import HarlechCastle
        castle = HarlechCastle( config=config, main=self.main, **kwds )
        self.main._boards.append(castle)
        return castle
    
    def addCilgerran( self, config=None, **kwds ):
        from .Cilgerran import CilgerranCastle
        castle = CilgerranCastle( config=config, main=self.main, **kwds )
        self.main._boards.append(castle)
        return castle