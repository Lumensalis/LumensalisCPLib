from LumensalisCP.CPTyping import Any
import traceback



def getName( name:str|None, instance:Any = None, depth:int=1):
    #frame = inspect.currentframe()
    if name is None:
        stackData = ["???"]
        try:
            raise Exception
        except Exception as inst:
            traceback.print_exception(Exception, value=inst,tb=inst.__traceback__)
            stackData = traceback.format_exception(inst, )
            print( f"stackData = {stackData}")
            name = stackData[depth]
    
    
    return name or "???"
    
def testGetName( v, name:str|None = None ):
    name = getName(name)
    return { name:v }