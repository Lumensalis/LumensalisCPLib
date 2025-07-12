from LumensalisCP.CPTyping import *

class ControlValueInstanceHelper(object):
    
    def __init__(self, cv):
        self.cv = cv
    
    def htmlBlock(self): 
        return f'<p>{self.cv.description}: <div id="{self.cv.name}">-</div></p>'
    
    def jsSelectBlock(self):
        return f'''
                const {self.cv.name}Selector = document.querySelector("#{self.cv.name}");
'''
    
    def wsReceivedBlock(self):
        return f'console.log( "..." );'
    
class BasicControlValueInstanceHelper(ControlValueInstanceHelper):
    
    def htmlBlock(self): 
        description = getattr(self.cv,'description',None ) or f"{self.cv.name} ({type(self.cv).__name__})"
        return f'<p>{description}: <div id="{self.cv.name}">-</div></p>'
    
    def wsReceivedBlock(self):
        return f'{self.cv.name}Selector.textContent = value;'


class IntControlValueInstanceHelper(ControlValueInstanceHelper):
    
    def htmlBlock(self): 
        return f'<p>{self.cv.description}: <div id="{self.cv.name}">-</div></p>'
    
    def wsReceivedBlock(self):
        return f'{self.cv.name}Selector.textContent = value;'


class RGBControlValueInstanceHelper(ControlValueInstanceHelper):

    def htmlBlock(self): 
        return f'<p>{self.cv.description}: <input id="{self.cv.name}" type="color">'

    def jsSelectBlock(self):
        return super().jsSelectBlock() + \
            f"""
            {self.cv.name}Selector.oninput = debounce(() => 
                ws.send( JSON.stringify( {{ name: '{self.cv.name}', 
                    value: {self.cv.name}.value
                }} ) ), 200);
            """

class ControlValueTemplateHelper(object):
    
    def __init__( self, main=None ):
        self.main = main
    
    
    def varBlocks(self, vars:List[InputSource]):
        htmlParts = []
        jsSelectors = []
        wsReceiveds = []
        
        wsReceiveds.append( '''
            function handleWSMessage( event ) {
                try {
                    const receivedMessage = JSON.parse(event.data);
                
''' )
        for v in vars: #self.main._controlVariables.values():
            
            instanceHelper = None
            kind = getattr(v,'kind',None)
            if kind == "int":
                instanceHelper = IntControlValueInstanceHelper( v )
            elif kind == "RGB":
                instanceHelper = RGBControlValueInstanceHelper( v )
            else:
                instanceHelper = BasicControlValueInstanceHelper( v )
            
            htmlParts.append( instanceHelper.htmlBlock() )
            jsSelectors.append( instanceHelper.jsSelectBlock() )
            wsReceiveds.append( 
               f"""
                        if( receivedMessage.{v.name} !== undefined ) {{
                            value = receivedMessage.{v.name};
                            {instanceHelper.wsReceivedBlock()}
                        }}
""" )

        wsReceiveds.append( '''
                           
                    } catch (error) {
                        console.error('Error parsing JSON:', error);
                    }
                }
''' )
            
        return {
            'htmlParts' : "\n".join( htmlParts ),
            'jsSelectors' : "\n".join( jsSelectors ),
            'wsReceiveds': "\n".join( wsReceiveds ),
        }
        
