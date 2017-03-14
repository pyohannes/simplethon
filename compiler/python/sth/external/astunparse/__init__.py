# coding: utf-8
from __future__ import absolute_import
from io import StringIO
from .unparser import Unparser
from .printer import Printer


__version__ = '1.5.0'


def unparse(tree):
    v = StringIO()
    Unparser(tree, file=v)
    return v.getvalue()


def dump(tree):
    v = StringIO()
    Printer(file=v).visit(tree)
    return v.getvalue()
