"""
Support for "structured output" based lists, and dicts

Allows classes to implement a writeOnScope method which can be used for 
a variety of output options including indented printing, json, ...
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional
from .simpleCommon import *
if TYPE_CHECKING:
    import weakref
    
#############################################################################

class WriteConfig(object):
    """_summary_

    :param object: _description_
    :type object: _type_
    """
    def __init__(self):
        pass
        self.showScopes = False
        self.detailed = True

    
    def write( self, scope:WriteScope, value:Any ):
            
        if hasattr( value, 'writeOnScope' ):
            value.writeOnScope( scope )
            return
        
        if isinstance( value, (list,tuple)):
            assert type(value) is not str
            with scope.startList( indentItems=scope.indentItems ) as nested:
                for item in value:
                    nested.addListItem( item )
            return
        if isinstance( value, dict):
            with scope.startDict( indentItems=scope.indentItems ) as nested:
                for tag,val in value.items():
                    nested.addTaggedItem(tag,val)
            return
        
        scope.target.write( repr(value) )

class WriteScope(object):
    """combines config and target, and provides base for writing containers
    """
    target:TextIO
    config:WriteConfig
    _parentRef: weakref.ref [WriteScope] | None
    
    showScopes=property( lambda self: self.config.showScopes )
    
    wrappers= {
        dict: ('{','}'),
        list: ('[',']'),
        tuple: ('(',')'),
        None: ('',''),
    }
    
    
    def __init__(self, ts:WriteScope|None, mode=None,indentItems:Optional[bool]=None
                 ):
        """_summary_

        Args:
            ts (WriteScope | None): _description_
            mode (_type_, optional): _description_. Defaults to None.
            indentItems (bool | None, optional): _description_. Defaults to None.
        """
        if ts is not None:
            self.config:WriteConfig = ts.config 
            self.target:TextIO = ts.target
            self.indent = ts.indent + "   "
            self._parentRef = weakref.ref(ts)
        else:
            assert self.target is not None and self.config is not None
            self.indent = "\r\n"
            self._parentRef = None
        self.indentItems = indentItems
        self.mode=mode
        self.added = 0
        self._writingTagged = False
    
    @property
    def parent(self) -> WriteScope|None:
        if self._parentRef is not None:
            return self._parentRef()

    def getScopedDefault( self, tag:str ) -> Any:
        if self.parent is None: return None
        return self.parent.getScopedDefault(tag)
        
    def nestedTag( self, tag:str ) -> str|None:
        return None
    
    def startDict(self,tag:Optional[str]=None,indentItems:Optional[bool]=None) -> "DictWriteScope":
        """start scope for writing tag/value dict

        Args:
            tag (str | None, optional): tag if adding as dictionary
            indentItems (bool | None, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        self._addTagBeforeItem(tag)
        return DictWriteScope( self,indentItems=indentItems)
    
    def addDict(self, items:dict[str,Any], tag:Optional[str]=None,indentItems:Optional[bool]=None) -> DictWriteScope:
        """write dict"""
        with self.startDict( tag,indentItems=indentItems ) as nested:
            nested.addTaggedEntries( items.items() ) # type: ignore
        return nested

    
    def startNamedType(self,instance,tag:Optional[str]=None,indentItems:Optional[bool]=None) -> NamedTypeWriteScope:
        """start scope for writing tag/value dict

        Args:
            tag (str | None, optional): tag if adding as dictionary
            indentItems (bool | None, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        self._addTagBeforeItem(self.nestedTag( tag or instance.name) )
        return NamedTypeWriteScope( self, instance=instance, indentItems=indentItems)

    
    def startList(self,tag:Optional[str]=None,indentItems:Optional[bool]=None) -> "ListWriteScope":
        """open a ListWriteScope for writing a sequence of items

        Args:
            tag (str | None, optional): _description_. Defaults to None.
            indentItems (bool | None, optional): _description_. Defaults to None.

        Returns:
            ListWriteScope: _description_
        """
        self._addTagBeforeItem(tag)
        return ListWriteScope( self, indentItems=indentItems )

    def addList(self,items:list, tag:Optional[str]=None,indentItems:Optional[bool]=None):
        #assert self.mode is list
        with self.startList( tag,indentItems=indentItems ) as nested:
            for item in items:
                nested.addListItem( item )

    def _addTagBeforeItem(self, tag:str|None):
        if tag is None: 
            if self.mode is dict:
                assert self._writingTagged
            return
        assert self.mode is dict
        self._addComma()
        self.target.write( f"\"{tag}\":" )
        
    def _addComma(self):
        if self.added:
            self.target.write( ", " )
            if self.indentItems is True:
                self.target.write(self.indent)
        self.added += 1
        
    def addItem( self, item:Any ) -> None:
        raise NotImplemented
    
    def write( self, item ):
        if self.mode is not None:
            self._addComma()
        self.config.write(self, item)    

    def __enter__(self):
        self.target.write(self.wrappers[self.mode][0])
        if self.indentItems is not False: self.target.write( self.indent )
        return self
    
    def __exit__(self,eT,eV,tb):
        if self.indentItems is not False: self.target.write( self.indent )
        self.target.write(self.wrappers[self.mode][1])
        pass

class ListWriteScope(WriteScope):
    def __init__(self, ts:WriteScope|None, indentItems:Optional[bool]=None
                 ):
        super().__init__(ts=ts,mode=list,indentItems=indentItems)
    
    def addListItem( self, item:Any ):
        """write an item in this list scope

        Args:
            item (Any): _description_
        """
        self._addComma()
        self.config.write(self, item)
    
    def addItem( self, item:Any ):
        return self.addListItem(item)
    
class DictWriteScope(WriteScope):
    def __init__(self, ts:WriteScope|None, indentItems:Optional[bool]=None
                 ):
        super().__init__(ts=ts,mode=dict,indentItems=indentItems)
        self.__defaults = {}
        
    def nestedTag( self, tag:str ) -> str|None:
        return tag
    
    def getScopedDefault( self, tag:str ) -> Any:
        if tag in self.__defaults:
            return self.__defaults[tag]
        return super().getScopedDefault(tag)
    
    def _isSame(self, a, b ):
        if a is b: return True
        if type(a) is type(b):
            if type(a) in (int,bool,str,float): return a == b

        return False

    def addOrSkipDefaultTaggedItem( self, tag:str, item:Any ):
        d = self.getScopedDefault(tag)
        if d is item:
            return
        self.__defaults[tag] = item
        self.addTaggedItem(tag,item)
        


    def addTaggedItem( self, tag:str, item:Any ):
        """write a tag/value pair in this dictionary

        Args:
            tag (str): _description_
            item (Any): _description_
        """
        
        self._addTagBeforeItem(tag)
        self._writingTagged = True
        self.config.write(self, item)
        self._writingTagged = False

    def addItem( self, item:Any ):
        self.addTaggedItem( item.name, item )
        
    def addTaggedItems(self, **kwds ):
        """ add tag/value pairs
        """
        for tag,val in kwds.items():
            self.addTaggedItem(tag,val)

    def addTaggedEntries(self, entries:Sequence[tuple[str,Any]]):
        """  add tag/value pairs

        order of entries will be maintained in output (unlike addTaggedItems)
        Args:
            entries (List[Tuple[str,Any]]): _description_
        """
        assert self.mode is dict
        for tag,val in entries:
            self.addTaggedItem(tag,val)

class NamedTypeWriteScope(DictWriteScope):
    def __init__(self, ts:WriteScope, instance:Any, indentItems:Optional[bool]=None
                 ):
        super().__init__(ts=ts,indentItems=indentItems)
        self.instance = instance

    def __enter__(self):
        rv = super().__enter__()
        self.addTaggedItem( 'name', self.instance.name )
        self.addTaggedItem( 'type', type(self.instance).__name__ )
        return rv
    
    
class TargetedWriteScope(WriteScope):
    """outermost scope for using WriteScope formatting
    """

    def __init__(self, target:TextIO=sys.stdout, config:WriteConfig|None = None):
        """_summary_

        Args:
            target (TextIO, optional): _description_. Defaults to sys.stdout.
            config (WriteConfig | None, optional): _description_. Defaults to None.
        """
        self.config:WriteConfig = config or WriteConfig()
        self.target = target        
        super().__init__(None)

    @classmethod 
    def makeScope(cls, arg ):
        if arg is None:
            return TargetedWriteScope()
        if isinstance(arg,WriteScope):
            return arg
        if arg is sys.stdout:
            return TargetedWriteScope(arg)
        
        assert False

#############################################################################
    