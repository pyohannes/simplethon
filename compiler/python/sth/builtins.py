####+
import collections
from sth import types, ast


class Print(object):

    def __init__(self):
        self.name = ast.Name()
        self.name.id = 'print'
        self.name.tp = self.type()

    def type(self):
        return types.Function(collections.OrderedDict(s=types.int_),
                              None)


__builtins__ = [ Print() ]
