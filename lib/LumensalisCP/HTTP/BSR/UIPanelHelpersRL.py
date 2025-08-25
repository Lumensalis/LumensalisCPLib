from __future__ import annotations

from LumensalisCP.ImportProfiler import getReloadableImportProfiler
__profileImport = getReloadableImportProfiler( __name__, globals() )

#############################################################################
# pyright: reportPrivateUsage=false, reportUnusedImport=false

from LumensalisCP.HTTP.BSR.common import *
from LumensalisCP.Main.Panel import PanelControl, PanelMonitor, PanelTrigger, ControlPanel
from LumensalisCP.util.ObjToDict import objectToDict
from LumensalisCP.Eval.Evaluatable import NamedEvaluatableProtocolT, NamedEvaluatableProtocol

from LumensalisCP.HTTP.BSR import UIPageHelpersRL

#############################################################################

__profileImport.parsing()

# pyright: reportPrivateUsage=false
class PanelTable(UIPageHelpersRL.SimpleTable):
    pass

class PanelTableRow(UIPageHelpersRL.SimpleTableRow):
    def __init__(self, table:PanelTable) -> None:
        super().__init__(table)

class PanelControlInstanceHelper(PanelTableRow):
    
    kindMatch:type|None
    input:NamedEvaluatableProtocol[Any]

    def __init__(self, table:PanelTable,panelInstance:PanelControl[Any,Any]|PanelMonitor[Any]):
        super().__init__(table)
        self.panelInstance = panelInstance
        if isinstance(panelInstance, PanelMonitor):
            self.input = panelInstance.source
            self.kindMatch = None
        else:
            assert isinstance(panelInstance, PanelControl), f"panelInstance must be a PanelControl or PanelMonitor, got {type(panelInstance)}"
            self.input = panelInstance

            assert self.panelInstance.kind is not None, f"panelInstance.kind is None for {self.panelInstance.name} ({type(self.panelInstance)})"
            assert self.panelInstance.kindMatch is not None, f"panelInstance.kind is None for {self.panelInstance.name} ({type(self.panelInstance)})"
            self.kindMatch = self.panelInstance.kindMatch
        
        self.nameId = self.input.name
        self.editable:bool = isinstance(panelInstance,PanelControl)

    def getCellContent(self,tag:str) -> Iterable[str]:
            panelInstance = self.panelInstance
            if tag == 'name':
                if isinstance(panelInstance, PanelMonitor):
                    yield panelInstance.source.name
                else:
                    yield panelInstance.name
            elif tag == 'description':
                description = getattr(panelInstance,'description',None ) # or f"{panelInstance.name} ({type(self).__name__})"
                yield description or ''
            elif tag == 'min':
                yield str(panelInstance._min)
            elif tag == 'value':
                yield self.valueCell()
            elif tag == 'edit':
                yield self.editCell()
            elif tag == 'max':
                yield str(panelInstance._max)
            elif tag == 'etc':
                yield repr(panelInstance.kind)
                #yield f"{repr(self.kindMatch)} / {id(panelInstance)} {panelInstance.dbgName} {repr(panelInstance.kind)}  / {repr(panelInstance.kindMatch)} / {type(self).__name__}"
            else:
                yield f"Unknown tag {tag} for {panelInstance.name} ({type(panelInstance)})"

    def valueCell(self)-> str:
        return f'<div id="{self.valueSelector.nameId}">-</div>'
    
    def editCell(self)-> str:
        return f'<input id="{self.editSelector.nameId}" type="text" value="-"/>'

    def addSelectors(self):
        if isinstance(self.panelInstance, PanelMonitor):
            self.valueSelector = self.section.addSelector( self.nameId+"Monitor", self.nameId+"_monitor")
        else:
            self.valueSelector = self.section.addSelector( self.nameId, self.nameId)
            self.editSelector = self.section.addSelector( self.nameId+"Edit", self.nameId+"_edit")
        
    def yieldWsChecks(self) :
        yield   f"""
                        if( receivedMessage.{self.nameId} !== undefined ) {{
                            value = receivedMessage.{self.nameId};
                            console.log( "received {self.nameId} ", value );
                            {self.wsCellUpdate()}
                        }}
""" 

    def wsCellUpdate(self) -> str:
        return f'console.log( "..." );'
    
class BasicPanelControlInstanceHelper(PanelControlInstanceHelper):

    
    def wsCellUpdate(self) -> str:
        return f'{self.valueSelector.selector}.textContent = value;'

class EditCapablePanelControlInstanceHelper(PanelControlInstanceHelper):

    def addSelectors(self) :
        super().addSelectors()
        if self.editable:
            
            editSelector = self.editSelector.selector
            
            self.section.addScript(f"""
            {editSelector}.oninput = ( debounce(() => {{
                const packet = JSON.stringify( 
                    {{ name: '{self.nameId}', value: {editSelector}.value }}
                    );
                console.log( "sending packet", packet );
                ws.send( packet );
                {self.valueSelector.selector}.textContent = {editSelector}.value;

            }},200 ) );
            """)
    
    def valueCell(self)-> str:
        return f'<div id="{self.nameId}">{self.panelInstance.controlValue}</div>'

class IntPanelControlInstanceHelper(EditCapablePanelControlInstanceHelper):
    
    def editCell(self)-> str:
        low = self.panelInstance._min
        high = self.panelInstance._max
        assert isinstance(low, int)
        assert isinstance(high, int)
        span = high - low
        assert span > 0, f"span must be positive, got {span} for {self.panelInstance.name} ({type(self.panelInstance)})"
        assert isinstance( self.panelInstance, PanelControl)
        return f'<input id="{self.editSelector.selector}" type="range" min="{low}" max="{high}" value="{self.panelInstance.controlValue}"/>'


    def wsCellUpdate(self):
        return f'{self.valueSelector.selector}.textContent = value;'

class BoolPanelControlInstanceHelper(EditCapablePanelControlInstanceHelper):
    
    def editCell(self)-> str:
        assert isinstance( self.panelInstance, PanelControl)
        return f'<input id="{self.editSelector.nameId}" type="checkbox" value="{self.panelInstance.controlValue}"/>'

    def wsCellUpdate(self):
        return f'{self.valueSelector.selector}.textContent = value;'

class FloatPanelControlInstanceHelper(EditCapablePanelControlInstanceHelper):

    def wsCellUpdate(self):
        return f'{self.valueSelector.selector}.textContent = value;'
    
    def editCell(self)-> str:
        low = self.panelInstance._min
        high = self.panelInstance._max
        assert isinstance(low, (int, float)), f"low for {self.nameId} must be int or float, got {type(low)}"
        assert isinstance(high, (int, float)), f"high for {self.nameId}must be int or float, got {type(high)}"
        span = high - low
        assert isinstance( self.panelInstance, PanelControl)
        return f'<input id="{self.editSelector.nameId}" type="range" min="{low}" max="{high}" value="{self.panelInstance.controlValue}" step="{span/100}"/>'


class RGBPanelControlInstanceHelper(EditCapablePanelControlInstanceHelper):

    def editCell(self): 
        return f'<input id="{self.editSelector.nameId}" type="color">'

#############################################################################

class UITrigger(UIPageHelpersRL.UIPageSectionChild):
    def __init__(self, section:UIPageHelpersRL.UIPageSection, trigger:PanelTrigger):
        super().__init__(section)
        self.trigger = trigger
        self.triggerName = trigger.name
        self.selector = section.addSelector(self.triggerName,self.triggerName,"_trigger")
        self.section.addScript( f"""
            {self.selector.selector}.onclick = ( () => {{
                const packet = JSON.stringify( {{ trigger: '{self.triggerName}' }});
                console.log( "sending packet", packet );
                ws.send( packet );
            }} );
                               """);
    def yieldHtml(self):
            yield f"""
<button type="button" id="{self.selector.nameId}">{self.triggerName}</button>
            """ 

class PanelParts(UIPageHelpersRL.UIPageSection):
    def __init__(self, page:UIPageHelpersRL.UIPage,  panel:ControlPanel):
        super().__init__(page, wsTarget=panel.name)

        self.panel = panel  

        self.controls = PanelTable( self,"Controls",
                ["name","description","min","value","max","edit","etc"]  )
        self.monitors = PanelTable( self,"Monitor",["name","description","value"] )

        self.triggers = UIPageHelpersRL.UIPageSection(self)

        for v in panel.controls.values():
            print( f"  adding control {v.name} ({type(v)}) {v.kindMatch} {v.kind}" )
            self.addControl(v)

        for v in panel.monitored.values(): 
            print( f"  adding monitored {v.source.name} ({type(v)})")
            self.addMonitored(v) 

        for v in panel.triggers.values():
            print( f"  adding trigger {v.name} ({type(v)})")
            self.addTrigger(v)

        if False: self.wsReceived.append( '''
            function handleWSMessage( event ) {
                try {
                    const receivedMessage = JSON.parse(event.data);
''' )
    def yieldHtml(self) -> Iterable[str]:
        yield "<div class='panel'>"
        for section in self.sections:
            yield from section.yieldHtml()
        yield "</div>"

    def addControl(self, control:PanelControl[Any,Any]):
            input = control
            instanceHelper = None
            kind = getattr(input,'kind',None)
            if kind == "int":
                instanceHelper = IntPanelControlInstanceHelper( self.controls , input )
            elif kind == "RGB":
                instanceHelper = RGBPanelControlInstanceHelper( self.controls , input )
            elif kind  in ( "float", "TimeSpanInSeconds" ):
                instanceHelper = FloatPanelControlInstanceHelper( self.controls , input )
            elif kind  in ( "bool","switch" ):
                instanceHelper = BoolPanelControlInstanceHelper( self.controls , input )

            else:
                kindMatch = control.kindMatch
                if kindMatch is RGB:
                    instanceHelper = RGBPanelControlInstanceHelper( self.controls, input )
                elif kindMatch is float:
                    instanceHelper = FloatPanelControlInstanceHelper( self.controls, input )
                elif kindMatch is bool:
                    instanceHelper = BoolPanelControlInstanceHelper( self.controls, input )
                elif kindMatch is int:
                    instanceHelper = IntPanelControlInstanceHelper( self.controls, input )

                else:
                    instanceHelper = BasicPanelControlInstanceHelper( self.controls, input )

            self.controls.addRow( instanceHelper )
            instanceHelper.addSelectors()

    def addMonitored(self, monitored:PanelMonitor[Any]):
            #input = monitored.source
            instanceHelper = None
            kind = getattr(monitored,'kind',None)
            if kind == "int":
                instanceHelper = IntPanelControlInstanceHelper( self.monitors, monitored )
            elif kind == "RGB":
                instanceHelper = RGBPanelControlInstanceHelper( self.monitors, monitored )
            else:
                instanceHelper = BasicPanelControlInstanceHelper( self.monitors, monitored )

            self.monitors.addRow( instanceHelper )
            #instanceHelper.addSelectors()
            instanceHelper.addSelectors()
            #instanceHelper.wsReceivedBlock() 

    def addTrigger(self, trigger:PanelTrigger):
        return UITrigger( self.triggers, trigger )


__profileImport.complete()
