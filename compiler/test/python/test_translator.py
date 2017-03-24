from sth.ast import parse, unparse
from sth.simplifier import simplify
from sth.typifier import typify
from sth.translator import translate


def assert_translate(src, dst, ret):
    assert unparse(translate(typify(simplify(parse(src))))) == dst


