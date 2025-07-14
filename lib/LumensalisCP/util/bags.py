
class Bag(dict):
    
    def __getattr__(self, name):
        try:
            return self[name]
        except:
            return super().__getattribute__(name)
        
    def __setattr__(self, name, value):
        self[name] = value
        
        
class NamedList(object):
    def __init__(self ):
        self.__items = []
        self.__byName = {}
        
    def __iter__(self):
        return iter(self.__items)

    def __len__(self):
        return len(self.__items)
    
    def keys(self):
        return self.__byName.keys()
    
    def values(self):
        return self.__byName.values()

    def items(self):
        return self.__byName.items()
    
    def __getitem__(self, x):
        if type(x) is str:
            return self.__byName[x]
        return self.__items[x]

    def append( self, item ):
        name = getattr(item,'name',None)
        if name is not None:
            assert item.name not in self.__byName
            self.__byName[name] = item
        self.__items.append(item)
                
    def extend( self, iterable ):
        for item in iterable:
            self.append(item)

    def __getattr__(self, name):
        try:
            return self.__byName[name]
        except:
            raise AttributeError
