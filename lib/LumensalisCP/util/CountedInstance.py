class CountedInstance:
    _ciCountedClasses:dict[str,type] = {}
    @staticmethod
    def _getCiInstanceCounts() -> dict[str,int]:
        return dict(
            [ (cls.__name__, cls._ciInstanceCount) for cls in CountedInstance._ciCountedClasses.values() ] # type: ignore
        )
    
    def __init__(self) -> None:
        cls =  self.__class__
        d = cls.__dict__
        i = d.get('_ciInstanceCount',None)
        if i is None:
            assert cls.__name__ not in CountedInstance._ciCountedClasses
            CountedInstance._ciCountedClasses[cls.__name__] = cls
            setattr(cls,'_ciInstanceCount',  1)
            #print(f"CountedInstance: {cls.__name__} initialized with instance count 0")

        else:
            setattr(cls,'_ciInstanceCount',  i+1)

