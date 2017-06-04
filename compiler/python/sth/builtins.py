####+
import collections
from sth import types, ast


class Print(object):

    def __init__(self):
        self.name = 'print'
        self.sthname = ast.Name()
        self.sthname.id = 'sth_print'
        self.sthname.tp = self.type()

    def type(self):
        return types.Function(collections.OrderedDict(s=types.int_),
                              None)


class Free(object):

    def __init__(self):
        self.name = 'free'
        self.sthname = ast.Name()
        self.sthname.id = 'sth_free'
        self.sthname.tp = self.type()

    def type(self):
        return types.Function(collections.OrderedDict(obj=types.craw),
                              None)


__builtins__ = [ Print(), Free() ]
