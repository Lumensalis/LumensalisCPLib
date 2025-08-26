from __future__ import annotations

from LumensalisCP.ImportProfiler import getReloadableImportProfiler
from usb_cdc import console
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
    def __init__(self, section:UIPageHelpersRL.UIPageSection, **kwds:Unpack[UIPageHelpersRL.SimpleTable.KWDS]) -> None:
        title = kwds.get('title')
        if title is not None:
            kwds.setdefault('divClass', title.replace(' ', '').lower() + 'Table')
        print(f"PanelTable init with title {title} and divClass {kwds.get('divClass',None)}")
        super().__init__(section, **kwds)

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


class SliderConfig(object):
    width=145
    height=360
    temp_value_x=28
    temp_value_y=35
    rail_x=60
    rail_y=47
    rail_width=8
    rail_height=300
    rail_height_rx=5
    focus_ring_x=35
    focus_ring_y=170
    focus_ring_width=105
    focus_ring_height=24
    focus_ring_rx=12
    value_x=94
    value_y=150
    thumb_x=35
    thumb_y=145
    thumb_width=48
    thumb_height=14
    thumb_rx=5
    def __init__(self,width:int=145,height:int=300 ) -> None:
        defaultWidth = self.width
        defaultHeight = self.height
        self.width = width
        self.height = height
        def setRelTag(tag:str):
            isWidth = tag.endswith('_x') or tag.endswith('_width')
            original = getattr(self.__class__, tag)
            if isWidth:
                scaled = int( original * width / defaultWidth )
            else:
                scaled = int( original * height / defaultHeight )

            setattr(self, tag, max( scaled, int(original/7)+2 ) )

        for tag in [
                'temp_value_x', 'temp_value_y', 
                'rail_x', 'rail_y',
                    'rail_width', 'rail_height', 'rail_height_rx',
                'focus_ring_x', 'focus_ring_y', 'focus_ring_width', 'focus_ring_height', 'focus_ring_rx',
                'value_x', 'value_y',
                'thumb_x', 'thumb_y', 'thumb_width', 'thumb_height', 'thumb_rx'
            ]:
            setRelTag(tag)

class PanelSlider(UIPageHelpersRL.UIPageSectionChild):
    def __init__(self, section:UIPageHelpersRL.UIPageSection, panelInstance:PanelControl[Any,Any]) -> None:
        super().__init__(section)
        self.panelInstance = panelInstance

        self.sliderValueId = f"id_{self.panelInstance.name}_slider"
        self.sliderSelectorName = f"{self.panelInstance.name}_sliderSelector"
        self.sliderConfig = SliderConfig(width=77, height=120)

        #//self.valueSelector = self.section.addSelector( self.nameId+"Monitor", self.nameId+"_monitor")                    
        self.section.addScript(f"""
            {{
                const { self.sliderSelectorName } = document.getElementById("{self.sliderValueId}");
                
                console.log( "added slider", { self.sliderSelectorName } );
                // Create an observer instance.
                function observeMutations(mutations) {{
                    value = { self.sliderSelectorName }.innerHTML;
                    const packet = JSON.stringify( 
                        {{ name: '{self.panelInstance.name}', value: value }}
                        );
                    console.log( "sending packet", packet );
                    ws.send( packet );
                }}

                var observer = new MutationObserver(
                    debounce(observeMutations,200)
                    //observeMutations
                );

                // Pass in the target node, as well as the observer options.
                observer.observe({ self.sliderSelectorName }, {{
                    childList: true,   // Observes direct child elements
                    subtree: true,     // Observes all descendants
                    attributes: true,  // Observes attribute changes
                    characterData: true // Observes changes to text content
                }});

            }}
""")
        
        """
                { self.sliderSelectorName }.oninput = ( debounce(() => {{
                    const packet = JSON.stringify( 
                        {{ name: '{self.panelInstance.name}', value: {self.sliderSelectorName}.value }}
                        );
                    console.log( "sending packet", packet );
                    ws.send( packet );
                    /* self.valueSelector.selector.textContent = self.sliderSelectorName.value; */
                }},200 ) );
        """
    def yieldHtml(self):
            pin=self.panelInstance
            minVal = pin._min
            maxVal = pin._max
            controlValue = pin.controlValue

            cfg = self.sliderConfig
            yield f"""
   
    <div class="slider-control-slot">
     <div id="id-temp-label-{pin.name}" class="label">{pin.displayName}</div>
    <div class="slider-control">

    <svg role="none" class="slider-group" width="{cfg.width}" height="{cfg.height}">
        <g role="slider" id="id-temp-slider" aria-orientation="vertical" tabindex="0" 
                aria-valuemin="{minVal}" aria-valuenow="{controlValue}" 
                aria-valuetext="{controlValue}" 
                aria-valuemax="{maxVal}" aria-labelledby="id-temp-label-{pin.name}">
        <text class="temp-value" x="{cfg.temp_value_x}" y="{cfg.temp_value_y}">{controlValue}</text>
        <rect class="rail" x="{cfg.rail_x}" y="{cfg.rail_y}" width="{cfg.rail_width}" height="{cfg.rail_height}" rx="{cfg.rail_height_rx}" aria-hidden="true"></rect>
        <text class="value" id="{self.sliderValueId}" x="{cfg.value_x}" y="{cfg.value_y}">{controlValue}</text>
        <rect class="focus-ring" x="{cfg.focus_ring_x}" y="{cfg.focus_ring_y}" width="{cfg.focus_ring_width}" height="{cfg.focus_ring_height}" rx="{cfg.focus_ring_rx}"></rect>
        <rect class="thumb" x="{cfg.thumb_x}" y="{cfg.thumb_y}" width="{cfg.thumb_width}" height="{cfg.thumb_height}" rx="{cfg.thumb_rx}"></rect>
        </g>
    </svg>
    </div>
    </div>
"""


class PanelSliders( UIPageHelpersRL.UIPageSection):
    def __init__(self, panel: PanelParts, section:Optional[UIPageHelpersRL.UIPageSection]=None):
        super().__init__(section or panel, divClass="sliders")
        for v in panel.panel.controls.values():
            print( f"  adding control {v.name} ({type(v)}) {v.kindMatch} {v.kind}" )
            slider = PanelSlider( self, v ) # type: ignore


#############################################################################

class UITrigger(UIPageHelpersRL.UIPageSectionChild):
    def __init__(self, section:UIPageHelpersRL.UIPageSection, trigger:PanelTrigger):
        super().__init__(section)
        self.trigger = trigger
        self.triggerName = trigger.name #.replace(' ','').lower()
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
<button type="button" class="trigger-button" id="{self.selector.nameId}">{self.trigger.displayName}</button>
            """ 

class TriggerSection(UIPageHelpersRL.UIPageSection):
    def __init__(self, panel:PanelParts,section:Optional[UIPageHelpersRL.UIPageSection]=None):
        super().__init__(section or panel,divClass="triggers")

        for v in panel.panel.triggers.values():
            print( f"  adding trigger {v.name} ({type(v)})")
            self.addTrigger(v)


    def addTrigger(self, trigger:PanelTrigger):
        return UITrigger( self, trigger )

class PanelControlsTable( PanelTable):
    def __init__(self, panel:PanelParts,section:Optional[UIPageHelpersRL.UIPageSection]=None):
        super().__init__(section or panel, divClass= "controlsTable", #title= "Controls", 
                headers= ["name","description","min","value","max","edit","etc"] )
        for v in panel.panel.controls.values():
            print( f"  adding control {v.name} ({type(v)}) {v.kindMatch} {v.kind}" )
            self.addControl(v)

    def addControl(self, control:PanelControl[Any,Any]):
            input = control
            instanceHelper = None
            kind = getattr(input,'kind',None)
            if kind == "int":
                instanceHelper = IntPanelControlInstanceHelper( self , input )
            elif kind == "RGB":
                instanceHelper = RGBPanelControlInstanceHelper( self, input )
            elif kind  in ( "float", "TimeSpanInSeconds" ):
                instanceHelper = FloatPanelControlInstanceHelper( self, input )
            elif kind  in ( "bool","switch" ):
                instanceHelper = BoolPanelControlInstanceHelper( self, input )

            else:
                kindMatch = control.kindMatch
                if kindMatch is RGB:
                    instanceHelper = RGBPanelControlInstanceHelper( self, input )
                elif kindMatch is float:
                    instanceHelper = FloatPanelControlInstanceHelper( self, input )
                elif kindMatch is bool:
                    instanceHelper = BoolPanelControlInstanceHelper( self, input )
                elif kindMatch is int:
                    instanceHelper = IntPanelControlInstanceHelper( self, input )
                else:
                    instanceHelper = BasicPanelControlInstanceHelper( self, input )

            self.addRow( instanceHelper )
            instanceHelper.addSelectors()

class PanelMonitoredTable( PanelTable):
    def __init__(self, panel: PanelParts, section:Optional[UIPageHelpersRL.UIPageSection]=None):
        super().__init__(section or panel, divClass= "monitoredTable", #title="Monitored",
                headers=["name","description","value"])

        for v in panel.panel.monitored.values(): 
            print( f"  adding monitored {v.source.name} ({type(v)})")
            self.addMonitored(v) 

    def addMonitored(self, monitored:PanelMonitor[Any]):
            #input = monitored.source
            instanceHelper = None
            kind = getattr(monitored,'kind',None)
            if kind == "int":
                instanceHelper = IntPanelControlInstanceHelper( self, monitored )
            elif kind == "RGB":
                instanceHelper = RGBPanelControlInstanceHelper( self, monitored )
            else:
                instanceHelper = BasicPanelControlInstanceHelper( self, monitored )

            self.addRow( instanceHelper )
            #instanceHelper.addSelectors()
            instanceHelper.addSelectors()
            #instanceHelper.wsReceivedBlock() 
        
class PanelParts(UIPageHelpersRL.UIPageSection):
    def __init__(self, page:UIPageHelpersRL.UIPage,  panel:ControlPanel):
        name = panel.name #.replace(' ','').lower()
        super().__init__(page, wsTarget=panel.name, divClass="controlPanel", divId=name+"_panel" )

        self.panel = panel  
        if panel.useSliders:
            self.sliders = PanelSliders( self )
        else:
            self.controls = PanelControlsTable( self )

        if len(panel.triggers) > 0:
            self.triggers = TriggerSection(self)

        if len(panel.monitored) > 0:
            self.monitors = PanelMonitoredTable( self )
        
    def yieldHtml(self):
            yield f"""
            <div class="controlPanelTitle">
                <h2>{self.panel.displayName}</h2>
            </div>
""" 

__profileImport.complete()
