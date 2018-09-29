from collections import OrderedDict

class limited_dict(OrderedDict):

    def __init__(self, *a, **kw):
        self.limit = kw.pop("maxsize", None)
        OrderedDict.__init__(self, *a, **kw)

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        if self.limit:
            while len(self) > self.limit:
                self.popitem(last=False)
