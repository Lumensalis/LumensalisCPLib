from collections import *

try:
    from collections import UserList
except:

    class UserList(object):
        """A minimally complete user-defined wrapper around list objects."""

        def __init__(self, initlist=None):
            self.data = []
            if initlist is not None:
                # XXX should this accept an arbitrary sequence?
                if type(initlist) == type(self.data):
                    self.data[:] = initlist
                elif isinstance(initlist, UserList):
                    self.data[:] = initlist.data[:]
                else:
                    self.data = list(initlist)

        def __repr__(self):
            return repr(self.data)

        def __contains__(self, item):
            return item in self.data

        def __len__(self):
            return len(self.data)

        def __getitem__(self, i):
            if isinstance(i, slice):
                return self.__class__(self.data[i])
            else:
                return self.data[i]

        def __setitem__(self, i, item):
            self.data[i] = item

        def __delitem__(self, i):
            del self.data[i]

        def __copy__(self):
            inst = self.__class__.__new__(self.__class__)
            inst.__dict__.update(self.__dict__)
            # Create a copy and avoid triggering descriptors
            inst.__dict__["data"] = self.__dict__["data"][:]
            return inst

        def append(self, item):
            self.data.append(item)


        def remove(self, item):
            self.data.remove(item)

        def clear(self):
            self.data.clear()

