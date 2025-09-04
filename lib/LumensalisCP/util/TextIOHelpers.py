from __future__ import annotations

from LumensalisCP.CPTyping import *
from LumensalisCP.util.ObjToDict import valToJson, v2jSimpleTypes
import json

_digits = ["0","1","2","3","4","5","6","7","8","9"]
def writeIntOnTextIO( out:TextIO, val:int, pad:int = 0, mag:Optional[int]=None ) -> None:
    if val < 0:
        out.write( '-' )
        val = -val  
    if val >= 10000:
        out.write( _digits[val // 10000] )
        writeIntOnTextIO( out, val % 10000, pad, mag=5 )
    elif val >= 1000:
        out.write( _digits[val // 1000] )
        writeIntOnTextIO( out, val % 1000, pad, mag=mag or 4 )
    elif val >= 100:
        out.write( _digits[val // 100] )
        writeIntOnTextIO( out, val % 100, pad, mag=mag or 3 )
    elif val >= 10:
        out.write( _digits[val // 10] )
        writeIntOnTextIO( out, val % 10, pad, mag=mag or 2 )
    else:
        out.write( _digits[val] )

_DOUBLE_QUOTE='"'
_COLON=':'
_COMMA=','
_OPEN_BRACE=r'{'
_CLOSE_BRACE=r'}'
_OPEN_BRACKET=r'['
_CLOSE_BRACKET=r']'
_NULL='null'
_TRUE='true'
_FALSE='false'

def needsEscape( val:str ) -> bool:
    for c in val:
        if c in ('"', '\\'):
            return True
        if ord(c) < 32 or ord(c) > 126:
            return True
    return False

def writeJsonStrOnTextIO( out:TextIO, val:str ) -> None:
    if needsEscape(val):
        out.write(json.dumps(val))
    else:
        out.write( _DOUBLE_QUOTE )
        out.write( val )
        out.write( _DOUBLE_QUOTE )

_LIST_OR_TUPLE = (list, tuple)
def writeJsonOnTextIO( out:TextIO,  val:Any  ):
    if type(val) in v2jSimpleTypes:
        if isinstance(val, int):
            writeIntOnTextIO(out, val)
        elif isinstance(val, str):
            writeJsonStrOnTextIO(out, val)
        elif isinstance(val, bool):
            out.write( _TRUE if val else _FALSE )
        elif val is None:
            out.write( _NULL )
        else:
            out.write( repr(val) )
        return
        return 
    elif isinstance(val, _LIST_OR_TUPLE):
        out.write( _OPEN_BRACKET )
        if True:
            first = True
            for item in val:
                if not first:
                    out.write( _COMMA )
                writeJsonOnTextIO(out, item)
                first = False   
        else:
            item:Any
            n = len(val)
            if n > 1:
                writeJsonOnTextIO(out, val[0])
                i = 1
                while i < n:
                    out.write( _COMMA )
                    writeJsonOnTextIO(out, val[i])
                    i += 1
        out.write( _CLOSE_BRACKET )
        
        return
    elif isinstance(val, dict):
        first = True
        out.write( _OPEN_BRACE )
        if False:
            for key,v2 in val.items():
                if not first:
                    out.write( _COMMA )
                writeJsonStrOnTextIO(out, key)
                out.write( _COLON)
                writeJsonOnTextIO(out, v2)
                first = False
        else:
            for key in val:
                v2 = val[key]
                if not first:
                    out.write( _COMMA )
                writeJsonStrOnTextIO(out, key)
                out.write( _COLON)
                writeJsonOnTextIO(out, v2)
                first = False
        out.write( _CLOSE_BRACE )
        return
    elif isinstance(val, bool):
        out.write( _TRUE if val else _FALSE )
    elif val is None:
        out.write( _NULL )
    else:
        writeJsonOnTextIO( out,valToJson(val) )
