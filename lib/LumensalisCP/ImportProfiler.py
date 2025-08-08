# SPDX-FileCopyrightText: 2025 James Fowler
#
"""
`LumensalisCP.ImportProfiler`
====================================================

support tracking/logging/profiling of imports 

Usage:
```python
# start of module

# before any other imports...
from LumensalisCP.ImportProfiler import getImportProfiler
__profileImport = getImportProfiler( __name__, globals() )

##############
# imports, etc...

__profileImport.parsing()  # mark the start of parsing


####################
# classes, functions, etc...
# ...
# __all__ = [ ... ]

__profileImport.complete()  # last line - end of module

```

"""

############################################################################
from __future__ import annotations

try:
    from typing import TYPE_CHECKING, Any, Optional, ClassVar # type: ignore
except ImportError:
    
    TYPE_CHECKING = False # type: ignore
from LumensalisCP.Temporal.Time import getOffsetNow, TimeInSeconds

from LumensalisCP.Main.PreMainConfig import sayAtStartup, pmc_mainLoopControl, pmc_gcManager
from LumensalisCP.util.CountedInstance import CountedInstance
#############################################################################

class ImportProfiler(CountedInstance):
    """ A simple profiler for imports, to help identify slow imports """


    SHOW_IMPORTS:ClassVar[bool] = False
    """ If True, will print import profiling messages to the console.
    """

    RECORD_IMPORTS:ClassVar[bool|None] = True
    """ If false, disables import tracking (and reduces the overhead to __almost__ zero)
    """

    _importIndex:ClassVar[int] = 0
    NESTING:ClassVar[list[ActualImportProfiler]] = []
    IMPORTS:ClassVar[list[ActualImportProfiler]] = []

    def __init__(self ) -> None: 
        super().__init__()

    def __call__(self, desc:str) -> None: 
        raise NotImplementedError
        

    def parsing(self) -> None:
        raise NotImplementedError

    def complete(self, moduleGlobals:Optional[dict[str,Any]]=None) -> None:
        raise NotImplementedError

    @classmethod
    def dumpWorstImports(cls, count:int = 10) -> None:
        imports = sorted(ImportProfiler.IMPORTS, key=lambda i: i.innerElapsed, reverse=True)
        count = min( count, len(imports))
        print(f"top {count} of {len(ImportProfiler.IMPORTS)} Imports sorted by innerElapsed:")
        totals:dict[str,float] = dict( innerElapsed = 0.0, parsingElapsed = 0.0, childElapsed = 0.0, totalElapsed = 0.0 )
        for i in imports[:count]:
            print(f"  {i}")
            for k in totals:
                totals[k] += getattr(i, k, 0.0)

        print(f"Total: {totals}")
############################################################################

class FakeImportProfiler(ImportProfiler):
    def __call__(self, desc:str) -> None: 
        pass

    def parsing(self) -> None:
        pass

    def complete(self, moduleGlobals:Optional[dict[str,Any]]=None) -> None:
        pass

############################################################################

class ActualImportProfiler(ImportProfiler):
    """ A simple profiler for imports, to help identify slow imports """

    def __init__(self, name:Optional[str|dict[str,Any]]=None, moduleGlobals:Optional[dict[str,Any]]=None ) -> None:
        super().__init__()
        if name is None:
            assert moduleGlobals is not None, "moduleGlobals must be provided if name is not"
            name = moduleGlobals.get('__name__', None) 
            assert name is not None, "moduleGlobals must contain '__name__' key"

        if isinstance(name, dict):
            assert moduleGlobals is None, "moduleGlobals must not be provided if name is a dict"
            moduleGlobals = name
            assert isinstance(moduleGlobals, dict)
            name = moduleGlobals.get('__name__', None)
            assert isinstance(name, str), "moduleGlobals must contain '__name__' key"

        self.name:str = name
        self._globals:dict[str,Any]|None = moduleGlobals
        self.importIndex = ImportProfiler._importIndex
        ImportProfiler._importIndex += 1
        self.path = "->".join(  [i.name for i in ImportProfiler.NESTING] )
        self.startTime:float = getOffsetNow()
        self._endTime:Optional[float] = None
        self.childElapsed:float  = 0.0
        self.innerElapsed:float = 999.0
        self.startParsing:float|None = None
        self( "import starting")
        ImportProfiler.IMPORTS.append( self )
        ImportProfiler.NESTING.append( self )
        self.checkName()

    def checkName(self ) -> None:
        if self._globals is None: return
        name = self.name
        moduleName = self._globals.get('__name__', None)
        assert moduleName is not None, f"moduleGlobals must contain '__name__' key, got {self._globals.keys()}"

        if name == moduleName: return
        if moduleName.endswith(name): return
        if moduleName.endswith( '.__init__'):
            if moduleName.endswith(name+'.__init__'): return
        if (moduleName+'.__init__').endswith(name): return

        sayAtStartup( f"moduleGlobals name {moduleName} does not match provided name {name} at {self.path}" )
        assert False, f"moduleGlobals name {moduleName} does not match provided name {name} at {self.path}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}( inner={self.innerElapsed:2.03f}, parsing={self._parsingElapsed:2.03f}, child={self.childElapsed:2.03f}, total={self.elapsed:2.03f}, start={self.startTime:2.03f}, name={repr(self.name)}, path=[{self.path}] )"

    def __call__(self, desc:str) -> None:
        if self.SHOW_IMPORTS:
            sayAtStartup( f"IMPORT {self.path} | {self.name} : {desc}", importProfiler=self )

    def parsing(self) -> None:
        """ call to indicate the start of parsing """
        self.startParsing = getOffsetNow()
        self( "parsing" )

    def complete(self, moduleGlobals:Optional[dict[str,Any]]=None) -> None:
        """ call at the end of the module
         
        `moduleGlobals` is optional, but must be provided to complete() if it was 
        not provided in the `getImportProfiler(...)` call

        :param moduleGlobals: the globals dictionary for the module being imported (if name provided)
        """

        end = ImportProfiler.NESTING.pop()
        assert end is self, f"ImportProfiler nesting mismatch: {end.name} != {self.name}"
        self._endTime = getOffsetNow()
        self.elapsed = self._endTime - self.startTime
        self.innerElapsed = self.elapsed - self.childElapsed
        if moduleGlobals is None:
            assert self._globals is not None, f"moduleGlobals must be provided to complete() for {self.name}"
        else:
            self._globals = moduleGlobals
        message = f"import complete in {self.innerElapsed:.3f}s / {self.elapsed:.3f}s"
        if self.startParsing is not None:
            self._parsingElapsed = self._endTime - self.startParsing
            message += f" (parsing {self._parsingElapsed:.3f}s)"
        else:
            self._parsingElapsed = self.innerElapsed
        self( message )
        if len(ImportProfiler.NESTING) > 0:
            top = ImportProfiler.NESTING[-1]
            top.childElapsed += self.elapsed

        
        
        self.checkName()

class ReloadableImportProfiler(ActualImportProfiler):
    #SHOW_IMPORTS:ClassVar[bool] = False
    
    pass 

############################################################################
_fakeImportProfiler = FakeImportProfiler()


def getReloadableImportProfiler(name:Optional[str|dict[str,Any]]=None, moduleGlobals:Optional[dict[str,Any]]=None) -> ImportProfiler:
    """ returns a reloadable import profiler for the given name """
    if ReloadableImportProfiler.RECORD_IMPORTS is True or ReloadableImportProfiler.SHOW_IMPORTS is True:
        return ReloadableImportProfiler(name, moduleGlobals=moduleGlobals)
    return _fakeImportProfiler


def getImportProfiler(name:Optional[str|dict[str,Any]]=None, moduleGlobals:Optional[dict[str,Any]]=None,reloadable:bool=False) -> ImportProfiler:
    """  returns an import profiler for the given name 
    
    .. code-block:: python
        __profileImport = getImportProfiler( __name__, globals() )
    
    :param name: the name of the module being imported, or a dict containing the module globals
    :param moduleGlobals: the globals dictionary for the module being imported (if name provided)
    :param reloadable: if True, indicates that this module may be reloaded
    """

    if reloadable:
        return getReloadableImportProfiler(name, moduleGlobals=moduleGlobals)
    if ImportProfiler.RECORD_IMPORTS is True or ImportProfiler.SHOW_IMPORTS is True:
        return ActualImportProfiler(name, moduleGlobals=moduleGlobals)
    return _fakeImportProfiler

__all__ = [ 'getImportProfiler', 'sayAtStartup', 'pmc_mainLoopControl', 'pmc_gcManager' ]
