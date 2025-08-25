from __future__ import annotations

from LumensalisCP.ImportProfiler import getReloadableImportProfiler
__profileImport = getReloadableImportProfiler( __name__, globals() )


from LumensalisCP.HTTP.BSR.common import *

#############################################################################
# pyright: reportPrivateUsage=false, reportUnusedImport=false

__profileImport.parsing()


class Selector(CountedInstance):
    def __init__(self, section:UIPageSection, selector:str, nameId:str, suffix:str=""):
        super().__init__()
        self.selector = selector + "Selector" + suffix
        self.nameId = nameId + suffix

    def htmlScript(self) -> str:
        return f"""
            const {self.selector} = document.querySelector("#{self.nameId}");"""
    
class UIPageSection(CountedInstance):
    def __init__(self, parent:UIPageSection, wsTarget:Optional[str]=None):
        super().__init__()
        self.__parent = weakref.ref(parent) if parent is not self else None
        if parent is not self:
            parent.sections.append(self)
        else:
            assert isinstance(self, UIPage)
        self.wsTarget = wsTarget

        self.sections:list[UIPageSection] = []
        self.children:list[UIPageSectionChild] = []
        # self.htmlParts:list[str] = []
        self.__jsSelectors:list[Selector] = []
        self.__javascript:list[str] = []
        self.__wsReceived:list[str] = []
        if False and self.wsTarget is not None:
            self.__wsReceived.append( f'''
                function handleWSMessage_{self.nameId}( event ) {{
                    try {{
                        var msg = JSON.parse( event.data );
                        if( msg.target == "{self.wsTarget}" ) {{
                            {self.nameId}_wsMessage( msg );
                        }}
                    }} catch(e) {{
                        console.log( "Error in handleWSMessage_{self.nameId}: " + e );
                    }}
                }}
            ''' )

    def yieldHtml(self) -> Iterable[str]:
        for section in self.sections:
            assert section is not self
            yield from section.yieldHtml()
        for child in self.children:
            yield from child.yieldHtml()

    def yieldSelectorScript(self) -> Iterable[str]:
        for selector in self.__jsSelectors:
            yield selector.htmlScript()
        for section in self.sections:
            yield from section.yieldSelectorScript()

    def parent(self) -> UIPageSection:
        section = self if self.__parent is None else self.__parent()
        assert isinstance(section, UIPage)
        return section

    def yieldWsChecks(self) -> Iterable[str]:
        for section in self.sections:
            yield from section.yieldWsChecks()
        for child in self.children:
            yield from child.yieldWsChecks()

    def addSelector(self, selector:str, nameId:str, suffix:str="") -> Selector:
        rv =  Selector(self, selector, nameId, suffix)
        self.__jsSelectors.append( rv )
            # f"""const {selector}Selector = document.querySelector("#{nameId}");"""
        return rv

    def yieldJavaScript(self) -> Iterable[str]:
        for section in self.sections:
            yield from section.yieldJavaScript()
        for script in self.__javascript:
            yield script

    def addScript(self, script:str) -> None:
        self.__javascript.append(script)

class UIPageSectionChild(CountedInstance):
    def __init__(self, section:UIPageSection):
        super().__init__()
        self.__section = weakref.ref(section)
        section.children.append(self)

    @property
    def section(self) -> UIPageSection:
        section = self.__section()
        if section is None:
            raise ValueError("Section has been garbage collected")
        return section

    def yieldWsChecks(self) -> Iterable[str]:
        yield from ()

    def yieldHtml(self) -> Iterable[str]:
        yield from ()

class SimpleTableRow(UIPageSectionChild):
    def __init__(self, table:SimpleTable):
        super().__init__(table)

    def getCellContent(self,tag:str) -> Iterable[str]:
        raise NotImplementedError

    def yieldWsChecks(self) -> Iterable[str]:
        yield from ()

class SimpleTable(UIPageSection):

    def __init__(self, section:UIPageSection, title:str, headers:list[str]):
        super().__init__(section)
        self.title = title
        self.headers = headers
        self.rows:list[SimpleTableRow] = []

    def startTable(self) -> Iterable[str]:
        yield """
    <table class="center">
        <thead>
            <tr>"""
        for h in self.headers:
            yield """
                <th>"""
            yield h
            yield "</th>"
            
        yield """
            </tr>
        </thead>
    <tbody>

    """
    def endTable(self) -> Iterable[str]:
        yield """
        </tbody>
    </table>
    
        """
    def addRow(self, row:SimpleTableRow ) -> None:
        self.rows.append(row)

    def yieldHtml(self) -> Iterable[str]: 
        if len(self.rows) == 0: return
        yield "<h2>" + self.title + "</h2>"
        yield from self.startTable()
        for row in self.rows:
            yield "<tr>\n"
            for tag in self.headers:
                yield "   <td>"
                yield from row.getCellContent(tag)
                yield "</td>\n"
            yield "</tr>\n"
        yield from self.endTable()

    def yieldWsChecks(self) -> Iterable[str]:
        for row in self.rows:
            yield from row.yieldWsChecks()

class UIPage(UIPageSection):
    
    def __init__(self, main:MainManager):
        super().__init__(self)
        self.main = main

    def _yieldHtml(self) -> Iterable[str]:
        yield HTML_TEMPLATE_A

        yield from self.yieldHtml()

        yield  """
        <script>
            console.log('client on ' + location.host );
            let ws = new WebSocket('ws://' + location.host + '/connect-websocket');
            ws.onopen = () => console.log('WebSocket connection opened');
            ws.onclose = () => console.log('WebSocket connection closed');
"""
        yield from self.yieldSelectorScript()
        yield from self.yieldJavaScript()
        yield """
            function handleWSMessage( event ) {
                try {
                    const receivedMessage = JSON.parse(event.data);
                    console.log( "ws receivedMessage", receivedMessage);

                
"""
        yield from self.yieldWsChecks()
        yield """
                } catch (error) {
                        console.error('Error processing WebSocket message JSON:', error);
                }
            }
            ws.onmessage = event => handleWSMessage( event );

            function debounce(callback, delay = 1000) {
                let timeout
                return (...args) => {
                    clearTimeout(timeout)
                    timeout = setTimeout(() => {
                    callback(...args)
                  }, delay)
                }
            }
            
        </script>
    </body>
</html>
"""

    def y2(self) -> Iterable[str]:
        prior:Any = None
        x = 0

        for s in self._yieldHtml():
            x +=1
            if s is None: # type: ignore
                yield "NONE"
                continue
            assert isinstance(s, str), f"cannot yield ({type(s)}) : {repr(s)} at {x}, prior={prior}"
            yield s
            prior = s


    def makeHtml(self) -> str:

        html =  "".join(self.y2())
        return html



HTML_TEMPLATE_A = """
<html lang="en">
    <head>
        <title>Websocket Client</title>
        <link rel="stylesheet" href="static/common.css" />
    </head>

"""

HTML_TEMPLATE_B = """
 
        <script>
            console.log('client on ' + location.host );


            let ws = new WebSocket('ws://' + location.host + '/connect-websocket');
            ws.onopen = () => console.log('WebSocket connection opened');
            ws.onclose = () => console.log('WebSocket connection closed');
"""
#            ws.onerror = error => cpuTemp.textContent = error;

HTML_TEMPLATE_Z = """            
            ws.onmessage = event => handleWSMessage( event );

            function debounce(callback, delay = 1000) {
                let timeout
                return (...args) => {
                    clearTimeout(timeout)
                    timeout = setTimeout(() => {
                    callback(...args)
                  }, delay)
                }
            }
            
        </script>
    </body>
</html>
"""

#############################################################################

__all__ = ['SimpleTableRow', 'SimpleTable', 'UIPageSection', 'UIPage']

__profileImport.complete()
