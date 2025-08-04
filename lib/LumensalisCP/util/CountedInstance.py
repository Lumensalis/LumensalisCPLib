class CountedInstance:
    _ciCountedClasses:dict[str,type] = {}
    _ciCountedReloadedClasses:dict[str,list[int]] = {}

    @staticmethod
    def getClassName(cls:type) -> str:
        return cls.__name__ 

    @staticmethod
    def _getCiInstanceCounts() -> dict[str,int]:
        return dict(
            [ (CountedInstance.getClassName(cls), cls._ciInstanceCount) for cls in CountedInstance._ciCountedClasses.values() ] # type: ignore
        )
    
    def __init__(self) -> None:
        cls =  self.__class__
        instanceCount = cls.__dict__.get('_ciInstanceCount',None)
        if instanceCount is None:
            clsName = CountedInstance.getClassName(cls)
            if clsName in CountedInstance._ciCountedClasses:
                # class was replaced - typically by a reload
                oldCls = CountedInstance._ciCountedClasses[clsName]
                CountedInstance._ciCountedReloadedClasses.setdefault(clsName, [])
                oldCount = getattr(oldCls,'_ciInstanceCount',None)
                assert isinstance(oldCount, int), f"oldCls._ciInstanceCount is not an int: {oldCount}"
                CountedInstance._ciCountedReloadedClasses[clsName].append(oldCount)
            CountedInstance._ciCountedClasses[clsName] = cls
            setattr(cls,'_ciInstanceCount',  1)
        else:
            setattr(cls,'_ciInstanceCount',  instanceCount+1)

