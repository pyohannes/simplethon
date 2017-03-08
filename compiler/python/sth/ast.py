#### +
#```((mode docu) (post ("replace-variables")))
#\section{\tc{``(file-basename)``}: Simplethon abstract syntax tree}
#\label{sec:sthast}
#```


import copy


class Node(object):
    INDENT = 4

    def __init__(self, tk):
        self._tk = tk

    def sthtoken_member(self):
        return self.sthtoken()

    def sthcode(self):
        return [ self.sthtoken() ]

    def simplified(self):
        return [ self ]


class ScopedNode(Node):
    def __init__(self, stmts, tk):
        super(ScopedNode, self).__init__(tk)
        self._stmts = stmts

    @property
    def stmts(self):
        return self._stmts

    def stmtsindented(self):
        ret = []
        for stmt in self._stmts:
            for line in stmt.sthcode():
                ret.append('%s%s' % (' ' * self.INDENT, line))
        return ret

    def sthcode(self):
        ret = []
        for child in self._stmts:
            ret.extend(child.sthcode())
            ret.extend(['', ''])
        ret = ret[:-2]
        return ret

    def simplified(self):
        ret = copy.copy(self) 
        ret._stmts = []
        for n in self._stmts:
            ret._stmts.extend(n.simplified())
        return [ ret ]


class IfNode(ScopedNode):
    def __init__(self, test, stmts, tk):
        super(IfNode, self).__init__(stmts, tk)
        self._test = test

    def sthcode(self, name='if'):
        return [ '%s %s:' % (
            name, self._test.sthtoken()) ] + self.stmtsindented()

    def simplified(self):
        ret = ScopedNode.simplified(self)[0]
        ret._test = self._test.simplified()[0]
        return [ ret ]


class ElseNode(ScopedNode):
    def sthcode(self):
        return [ 'else:' ] + self.stmtsindented()


class SingleWordNode(Node):
    def sthtoken(self):
        return self.__class__.__name__.lower()


class TwoArgumentNode(Node):
    def __init__(self, left, right, tk):
        super(TwoArgumentNode, self).__init__(tk)
        self._left = left
        self._right = right

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right


class OperationNode(TwoArgumentNode):
    operator = None

    def sthtoken(self):
        return '(%s %s %s)' % (
                self._left.sthtoken(),
                self.operator,
                self._right.sthtoken())


class LiteralNode(Node):
    def __init__(self, value, tk):
        super(LiteralNode, self).__init__(tk)
        self._value = value

    def sthtoken(self):
        return self._value


class LiteralNumberNode(LiteralNode):
    def sthtoken_member(self):
        return '(%s)' % self.sthtoken()


class AugmentedAssignmentNode(OperationNode):
    def sthtoken(self):
        return '%s %s %s' % (
                self._left.sthtoken(),
                self.operator,
                self._right.sthtoken())

    def simplified(self):
        operation = self.operator_cls(self._left, self._right,
                self._tk).simplified()
        return [ Assignment(
            left=[[ self._left ]], 
            right=operation, 
            tk=self._tk) ]

#### ------------- #

class Module(ScopedNode): pass


class TypedContainer(TwoArgumentNode):
    def sthtoken(self):
        contenttypes = ', '.join([ i.sthtoken() for i in self._right ])
        return '%s[%s]' % (self._left.sthtoken(), contenttypes)


class Integer(LiteralNumberNode): pass
class Float(LiteralNumberNode): pass
class Identifier(LiteralNode): pass
class Bool(LiteralNode): pass


class Call(TwoArgumentNode):
    def sthtoken(self):
        argstr = ', '.join([ arg.sthtoken() for arg in self._right ])
        return '%s(%s)' % (self._left.sthtoken(), argstr)


class Function(ScopedNode):
    def __init__(self, name, parameters, returns, stmts, tk):
        super(Function, self).__init__(stmts, tk)
        self._name = name
        self._parameters = parameters
        self._returns = returns

    def sthtoken(self):
        raise SyntaxError("")

    def sthcode(self):
        code = [ 'def %s(%s) -> %s:' % (
            self._name.sthtoken(),
            ', '.join([ p.sthtoken() for p in self._parameters ]),
            ', '.join([ r.sthtoken() for r in self._returns ])) ]
        code.extend(self.stmtsindented())
        return code


class Argument(Node):
    def __init__(self, name, value, tk):
        super(Argument, self).__init__(tk)
        self._name = name
        self._value = value

    @property
    def name(self): 
        return self._name

    @property
    def value(self): 
        return self._value

    def sthtoken(self):
        r = []
        if self.name:
            r.append('%s=' % self.name.sthtoken())
        r.append('%s' % self.value.sthtoken())
        return ''.join(r)


class ArgumentDefinition(Argument):
    def __init__(self, name, value, type, tk):
        super(ArgumentDefinition, self).__init__(name, value, tk)
        self._type = type

    @property
    def type(self):
        return self._type

    def sthtoken(self):
        r = [ '%s: %s' % (self._name.sthtoken(), self._type.sthtoken()) ]
        if self._value:
            r.append('=%s' % self._value.sthtoken())
        return ''.join(r)


class Return(Node):
    def __init__(self, values, tk):
        super(Return, self).__init__(tk)
        self._values = values

    def sthtoken(self):
        argstr = ', '.join([ arg.sthtoken() for arg in self._values])
        return 'return %s' % argstr


class Assignment(OperationNode):
    operator = '='

    def sthtoken(self):
        ret = []
        for target in self._left:
            ret.append(', '.join([ t.sthtoken() for t in target ]))
        ret.append(', '.join([ v.sthtoken() for v in self._right]))
        return (' %s ' % self.operator).join(ret)

    def simplified(self):
        ret = []
        for targetgroup in self._left:
            for target, value in zip(targetgroup, self._right):
                ret.append(self.__class__(
                    left=[[ target ]], 
                    right=value.simplified(),
                    tk=self._tk))
        return ret


class Member(TwoArgumentNode):
    def sthtoken(self):
        return '%s.%s' % (
                self._left.sthtoken_member(), self._right.sthtoken())


class MathOperationNode(OperationNode):
    def simplified(self):
        member = Member(
                left=self._left, 
                right=Identifier(self.operator_func, self._tk),
                tk=self._tk)
        return [ Call(member, [ self._right ], self._tk) ]


class Greater(MathOperationNode):
    operator = '>'
    operator_func = '__gt__'


class Less(MathOperationNode):
    operator = '<'
    operator_func = '__lt__'


class LessEquals(MathOperationNode):
    operator = '<='
    operator_func = '__le__'


class GreaterEquals(MathOperationNode):
    operator = '>='
    operator_func = '__ge__'


class NotEquals(MathOperationNode):
    operator = '!='
    operator_func = '__ne__'


class Equals(MathOperationNode):
    operator = '=='
    operator_func = '__eq__'


class Plus(MathOperationNode):
    operator = '+'
    operator_func = '__add__'


class Minus(MathOperationNode):
    operator = '-'
    operator_func = '__sub__'


class Multiply(MathOperationNode):
    operator = '*'
    operator_func = '__mul__'


class Divide(MathOperationNode):
    operator = '/'
    operator_func = '__div__'


class Percent(MathOperationNode):
    operator = '%'
    operator_func = '__mod__'


class PlusEquals(AugmentedAssignmentNode):
    operator = '+='
    operator_cls = Plus


class MinusEquals(AugmentedAssignmentNode):
    operator = '-='
    operator_cls = Minus


class MultiplyEquals(AugmentedAssignmentNode):
    operator = '*='
    operator_cls = Multiply


class DivideEquals(AugmentedAssignmentNode):
    operator = '/='
    operator_cls = Divide


class PercentEquals(AugmentedAssignmentNode):
    operator = '%='
    operator_cls = Percent


class Break(SingleWordNode): pass
class Continue(SingleWordNode): pass


class If(Node):
    def __init__(self, ifclauses, elseclause, tk):
        super(If, self).__init__(tk)
        self._ifclauses = ifclauses
        self._elseclause = elseclause

    def sthcode(self):
        ret = self._ifclauses[0].sthcode()
        for clause in self._ifclauses[1:]:
            ret.extend(clause.sthcode(name='elif'))
        if self._elseclause:
            ret.extend(self._elseclause.sthcode())
        return ret

    def simplified(self):
        else_simple = None
        if self._elseclause:
            else_simple = self._elseclause.simplified()[0]
        return [ self.__class__(
                [ ic.simplified()[0] for ic in self._ifclauses ],
                else_simple,
                self._tk) ]


class While(ScopedNode):
    def __init__(self, test, stmts, elseclause, tk):
        super(While, self).__init__(stmts, tk)
        self._test = test
        self._elseclause = elseclause

    def sthcode(self):
        ret = [ 'while %s:' % self._test.sthtoken() ]
        ret.extend(self.stmtsindented())
        if self._elseclause:
            ret.extend(self._elseclause.sthcode())
        return ret

    def simplified(self):
        ret = ScopedNode.simplified(self)[0]
        ret._test = self._test.simplified()[0]
        if self._elseclause:
            ret._elseclause = self._elseclause.simplified()[0]
        return [ ret ]
