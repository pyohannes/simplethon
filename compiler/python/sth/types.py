import collections


class Type(object):

    def __init__(self):
        if not isinstance(self, Class):
            self.clstp = Class(self)

    def __str__(self):
        return self.name

    def cstr(self):
        return 'Sth%s%s' % (self.name[0].upper(), self.name[1:])

    def __eq__(self, o):
        return str(self) == str(o)

    def __ne__(self, o):
        return not self == o

    def populate(self):
        self.members = dict(
                __craw__=Function(collections.OrderedDict(self=self),
                                craw))


class CRaw(Type):
    name = 'craw'


class Num(Type):

    def populate(self):
        super(Num, self).populate()
        self.members.update(dict(
                __lt__=Function(collections.OrderedDict(self=self, n=self),
                                bool_),
                __gt__=Function(collections.OrderedDict(self=self, n=self),
                                bool_),
                __le__=Function(collections.OrderedDict(self=self, n=self),
                                bool_),
                __ge__=Function(collections.OrderedDict(self=self, n=self),
                                bool_),
                __eq__=Function(collections.OrderedDict(self=self, n=self),
                                bool_),
                __ne__=Function(collections.OrderedDict(self=self, n=self),
                                bool_),
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
                __bool__=Function(collections.OrderedDict(self=self),
                                bool_),
                __int__=Function(collections.OrderedDict(self=self),
                                int_),
                __float__=Function(collections.OrderedDict(self=self),
                                float_)))


class Int(Num):
    name = 'int'


class Float(Num):
    name = 'float'


class Bool(Type):
    name = 'bool'

    def populate(self):
        super(Bool, self).populate()
        self.members.update(dict(
                __int__=Function(collections.OrderedDict(self=self),
                                int_),
                __eq__=Function(collections.OrderedDict(self=self, b=self),
                                bool_)))


class CustomType(Type):                

    def __init__(self, name):
        super(CustomType, self).__init__()
        self.name = name


class Composite(Type):

    def __init__(self, subtypes):
        super(Composite, self).__init__()
        self.subtypes = subtypes

    def populate(self):
        super(Composite, self).populate()
        for t in self.subtypes:
            t.populate()

    def __str__(self):
        return '%s[%s]' % (self.name, 
                ', '.join([ str(s) for s in self.subtypes ]))


class List(Composite):
    name = 'List'


class Function(Type):

    def __init__(self, args, returns):
        super(Function, self).__init__()
        self.args = args
        self.returns = returns


class Class(Composite):
    name = 'class'

    def __init__(self, cls):
        super(Class, self).__init__([ cls ])

    @property
    def tp(self):
        return self.subtypes[0]

    @property
    def members(self):
        return self.tp.members


int_ = Int()
float_ = Float()
bool_ = Bool()
craw = CRaw()


for t in (int_, float_, bool_):
    t.populate()


def make_class(name):
    c = CustomType(name)
    c.populate()
    c.members['__new__'] = Function(collections.OrderedDict([]), c)
    return c
