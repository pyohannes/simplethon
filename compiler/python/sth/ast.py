####+
import ast
from ast import *
from _ast import arg

import sth.external.astunparse


def flatten(l):
    ret = []
    for e in l:
        if isinstance(e, list):
            ret.extend(flatten(e))
        else:
            ret.append(e)
    return ret


class GotoLabel(AST):
    _fields = ('name',)

    def __init__(self, name=None):
        self.name = name


class Goto(AST):
    _fields = ('name',)

    def __init__(self, name=None):
        self.name = name


class Pointer(AST):
    _fields = ('name',)

    def __init__(self, name=None):
        self.name = name


class Dereference(AST):
    _fields = ('name',)

    def __init__(self, name=None):
        self.name = name


class RecursiveNodeVisitor(NodeVisitor):

    __scopefields__ = (
            'body', 'orelse')

    def __init__(self, filename, bottomup=False):
        super(RecursiveNodeVisitor, self).__init__()
        self.filename = filename
        self.bottomup = bottomup
        self.current_lineno = 0
        self.current_col_offset = 0
        self.path = []

    def visit(self, node):
        ret = None
        self.path.append(node)
        try:
            try:
                self.current_lineno = node.lineno
                self.current_col_offset = node.col_offset
            except AttributeError: pass
            if not self.bottomup:
                ret = super(RecursiveNodeVisitor, self).visit(node)
            for n in iter_child_nodes(node):
                self.visit(n)
            if self.bottomup:
                ret = super(RecursiveNodeVisitor, self).visit(node)
        finally:
            self.path.pop()
        return ret

    def generic_visit(self, node):
        fname = 'visit_%s' % node.__class__.__name__.lower()
        if hasattr(self, fname):
            return getattr(self, fname)(node)

    def raise_syntax_error(self, msg):
        error = SyntaxError(msg)
        error.lineno = self.current_lineno
        error.offset = self.current_col_offset
        error.filename = self.filename
        raise error

    def replace_in_parent(self, old, new, parent=None, listonly=False):
        parent = parent or self.path[-2]
        for f in parent._fields:
            child = getattr(parent, f)
            if child is old and not listonly:
                setattr(parent, f, new)
            elif isinstance(child, list):
                child = flatten([ new if c is old else c for c in child ])
                setattr(parent, f, child)
        if not isinstance(new, list):
            self.replace_in_path(old, new)

    def replace_in_path(self, old, new):
        self.path = [ new if p is old else p for p in self.path ]

    def add_in_parent_stmt_list(self, node):
        scopefields = set(self.__scopefields__)
        for i in range(len(self.path) - 1, 0, -1):
            child = self.path[i]
            parent = self.path[i - 1]
            scopes = scopefields.intersection(parent._fields)
            if scopes:
                found = False
                for s in scopes:
                    if child in getattr(parent, s):
                        self.replace_in_parent(child, [ node, child ],
                                parent=parent, listonly=True)
                        found = True
                        break
                if found:
                    break

    def make_name(self, id_, parent):
        name = ast.Name()
        name.id = id_
        self.copy_source_attrs(parent, name)
        return name

    def make_anonym_assign(self, value):
        genid = self.make_name(None, value)
        ass = ast.Assign()
        ass.targets = [ genid ]
        ass.value = value
        self.copy_source_attrs(value, ass)
        self.add_in_parent_stmt_list(ass)
        return genid

    def make_anonym_gotolabel(self, parent):
        label = GotoLabel()
        label.name = self.make_name(None, parent)
        self.copy_source_attrs(parent, label)
        return label

    def make_goto(self, name):
        goto = Goto()
        goto.name = name
        self.copy_source_attrs(name, goto)
        return Expr(value=goto)

    def make_attr(self, value, *attrs, slice=None):
        for a in attrs:
            value = ast.Attribute(attr=a, value=value)
        if slice:
            value = ast.Subscript(value=value, slice=slice)
        return value

    def make_pointer(self, name, parent):
        ptr = Pointer(name)
        self.copy_source_attrs(parent, ptr)
        return ptr

    def make_dereference(self, name, parent):
        ref = Dereference(name)
        self.copy_source_attrs(parent, ref)
        return ref

    def make_assign(self, targets, value):
        if not isinstance(targets, list):
            targets = [ targets ]
        return ast.Assign(targets=targets, value=value)

    def copy_source_attrs(self, src, dsts):
        try:
            dsts[0]
        except:
            dsts = [ dsts ]
        try:
            for d in dsts:
                d.lineno = src.lineno
                d.col_offset = src.col_offset
        except AttributeError: pass


class RestrictKeywords(RecursiveNodeVisitor):
    __unsupported__ = (
            And, Assert, AsyncFor, AsyncFunctionDef, 
            AsyncWith, Await, BitAnd, BitOr, BitXor,
            ClassDef, Del, Dict, DictComp, Ellipsis,
            ExceptHandler, ExtSlice, FloorDiv, For, 
            FormattedValue, GeneratorExp, Global, Import,
            ImportFrom, In, Interactive, Invert, Is,
            IsNot, LShift, Lambda, List, ListComp,
            Nonlocal, Not, MatMult, NotIn, Or, Pass,
            Pow, RShift, Raise, Set, SetComp, Slice,
            Starred, Str, Try, Tuple, With, Yield,
            YieldFrom
            )

    def generic_visit(self, node):
        for cls in self.__unsupported__:
            if isinstance(node, cls):
                self.raise_syntax_error(
                    "The Python node %s is not supported in Simplethon" % (
                        cls.__name__))


class RestrictAst(RecursiveNodeVisitor):

    def visit_call(self, node):
        for k in node.keywords:
            if not k.arg:
                self.raise_syntax_error(
                    "Argument expansion is not supported")
        if node.keywords:
            self.raise_syntax_error(
                "Keyword arguments are not supported")

    def visit_functiondef(self, node):
        if node.args.vararg:
            self.raise_syntax_error(
                "Variable arguments are not supported")
        for arg in node.args.args:
            if not arg.annotation:
                self.raise_syntax_error(
                    "Arguments must be type annotated")
        for n in self.path[:-1]:
            if isinstance(n, FunctionDef):
                self.raise_syntax_error(
                    "Nested functions are not supported")

    def visit_index(self, node):
        for n in self.path:
            if isinstance(n, arguments):
                return
        self.raise_syntax_error(
            "The Python node %s is not supported in Simplethon" % (
                node.__class__.__name__))

    def visit_compare(self, node):
        if len(node.ops) > 1:
            self.raise_syntax_error(
                "Multiple comparisons are not supported")


def parse(source, filename='<unknown>'):
    tree = ast.parse(source, filename)
    RestrictKeywords(filename).visit(tree)
    RestrictAst(filename).visit(tree)
    return tree


def unparse(tree):
    return sth.external.astunparse.unparse(tree)
