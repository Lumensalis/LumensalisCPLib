from LumensalisCP.CPTyping import Any, Callable, Generator, List, Mapping

def dictAddUnique( d:Mapping[str,Any], key:str, value:Any ) -> None:
    if key in d:
        assert d[key] == value
    else:
        d[key] = value