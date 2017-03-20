####+
import collections


class Type(object):
    def __str__(self):
        return self.name

    def __eq__(self, o):
        return str(self) == str(o)

    def __ne__(self, o):
        return not self == o


class Num(Type):

    def populate(self):
        self.members = dict(
                __lt__=Function(collections.OrderedDict(self=self, n=self),
                                Bool()),
                __gt__=Function(collections.OrderedDict(self=self, n=self),
                                Bool()),
                __le__=Function(collections.OrderedDict(self=self, n=self),
                                Bool()),
                __ge__=Function(collections.OrderedDict(self=self, n=self),
                                Bool()),
                __eq__=Function(collections.OrderedDict(self=self, n=self),
                                Bool()),
                __ne__=Function(collections.OrderedDict(self=self, n=self),
                                Bool()),
                __add__=Function(collections.OrderedDict(self=self, n=self),
                                self),
                __sub__=Function(collections.OrderedDict(self=self, n=self),
                                self),
                __mul__=Function(collections.OrderedDict(self=self, n=self),
                                self),
                __div__=Function(collections.OrderedDict(self=self, n=self),
                                self),
                __mod__=Function(collections.OrderedDict(self=self, n=self),
                                self),
                __int__=Function(collections.OrderedDict(self=self),
                                int_),
                __float__=Function(collections.OrderedDict(self=self),
                                float_))


class Int(Num):
    name = 'int'


class Float(Num):
    name = 'float'


class Bool(Type):
    name = 'bool'


class Custom(Type):

    def __init__(self, name):
        super(Custom, self).__init__()
        self.name = name


class Collection(Type):

    def __init__(self, name, subtypes):
        super(Collection, self).__init__()
        self.name = name
        self.subtypes = subtypes

    def __str__(self):
        return '%s[%s]' % (self.name, ', '.join(self.subtypes))


class List(Collection):

    def __init__(self, subtypes):
        super(List, self).__init__('list', subtypes)


class Function(Type):

    def __init__(self, args, returns):
        self.args = args
        self.returns = returns

    def __str__(self):
        args = [ '%s: %s' % (n, v) for n, v in self.args.items() ]
        rets = self.returns or ''
        return '%s -> %s' % (', '.join(args), rets)


int_ = Int()
float_ = Float()
bool_ = Bool()

for t in (int_, float_):
    t.populate()