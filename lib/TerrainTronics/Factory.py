
# pylint: disable=unused-import,import-error,reimported,import-outside-toplevel,used-before-assignment
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
        
from LumensalisCP.common import *
from LumensalisCP.Main.Dependents import FactoryBase
if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    from TerrainTronics.Caernarfon import CaernarfonCastle
    from TerrainTronics.Harlech import HarlechCastle

class TerrainTronicsFactory(FactoryBase):

    def addCaernarfon( self, **kwds:Unpack[CaernarfonCastle.KWDS] )-> CaernarfonCastle:
        from TerrainTronics.Caernarfon import CaernarfonCastle
        return self.makeChild( CaernarfonCastle, **kwds )
    
    def addHarlech( self, **kwds ) -> HarlechCastle:
        from TerrainTronics.Harlech import HarlechCastle
        return self.makeChild( HarlechCastle, **kwds )
    
    def addCilgerran( self, config=None, **kwds ):
        from TerrainTronics.Cilgerran import CilgerranCastle
        return self.makeChild( CilgerranCastle, config=config, **kwds )

    def addCaerphilly( self, config=None, **kwds ):
        from TerrainTronics.Caerphilly import CaerphillyCastle
        return self.makeChild( CaerphillyCastle, config=config, **kwds )

    def addHarlechXL( self, **kwds ):
        from TerrainTronics.HarlechXL import HarlechXLCastle
        return self.makeChild( HarlechXLCastle, **kwds )
