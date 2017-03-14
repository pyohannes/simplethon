####+
import ast
from ast import *

import sth.external.astunparse


class RecursiveNodeVisitor(NodeVisitor):
    def __init__(self, filename):
        super(RecursiveNodeVisitor, self).__init__()
        self.filename = filename
        self.current_lineno = 0
        self.current_col_offset = 0
        self.path = []

    def visit(self, node):
        self.path.append(node)
        try:
            try:
                self.current_lineno = node.lineno
                self.current_col_offset = node.col_offset
            except AttributeError: pass
            super(RecursiveNodeVisitor, self).visit(node)
            for n in iter_child_nodes(node):
                self.visit(n)
        finally:
            self.path.pop()

    def generic_visit(self, node):
        fname = 'visit_%s' % node.__class__.__name__.lower()
        if hasattr(self, fname):
            getattr(self, fname)(node)

    def raise_syntax_error(self, msg):
        error = SyntaxError(msg)
        error.lineno = self.current_lineno
        error.offset = self.current_col_offset
        error.filename = self.filename
        raise error


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
