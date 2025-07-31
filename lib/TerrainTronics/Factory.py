
# pylint: disable=unused-import,import-error,reimported,import-outside-toplevel,used-before-assignment
# pyright: reportMissingImports=false, reportImportCycles=false, reportUnusedImport=false
        
from LumensalisCP.ImportProfiler import getImportProfiler
__sayImport = getImportProfiler( globals() )

from LumensalisCP.common import *
from LumensalisCP.Main.Dependents import FactoryBase
if TYPE_CHECKING:
    from LumensalisCP.Main.Manager import MainManager
    from TerrainTronics.Caernarfon import CaernarfonCastle, CaernarfonCastleKWDS
    from TerrainTronics.Harlech import HarlechCastle

class TerrainTronicsFactory(FactoryBase):

    def addCaernarfon( self, **kwds:Unpack[CaernarfonCastleKWDS] )-> CaernarfonCastle:
        """ add a Caernarfon Castle board - see http://lumensalis.com/ql/h2Caernarfon
        """
        from TerrainTronics.Caernarfon import CaernarfonCastle
        
        return self.makeChild( CaernarfonCastle, **kwds ) # type: ignore
    
    def addHarlech( self, **kwds ) -> HarlechCastle:
        from TerrainTronics.Harlech import HarlechCastle
        return self.makeChild( HarlechCastle, **kwds ) # type: ignore
    
    def addCilgerran( self, config=None, **kwds ):
        from TerrainTronics.Cilgerran import CilgerranCastle
        return self.makeChild( CilgerranCastle, config=config, **kwds ) # type: ignore

    def addCaerphilly( self, config=None, **kwds ):
        from TerrainTronics.Caerphilly import CaerphillyCastle
        return self.makeChild( CaerphillyCastle, config=config, **kwds ) # type: ignore

    def addHarlechXL( self, **kwds ):
        from TerrainTronics.HarlechXL import HarlechXLCastle
        return self.makeChild( HarlechXLCastle, **kwds ) # type: ignore

__sayImport.complete()
