from sth.ast import parse
from sth.simplifier import simplify
from sth.typifier import typify
from sth.preparator import prepare
from sth.translator import translate, unparse


def assert_translate(src, dst, ret, lastid):
    header = """#include "sth/sth.h"

"""
    mainfunc = """int main(int argc, char **argv)
{
  int %(ret)s;
  SthStatus *%(sta)s;
  SthList *%(arg)s;
  SthInt *%(sthret)s;
  %(ret)s = 0;
  %(sta)s = 0;
  %(arg)s = 0;
  %(sthret)s = 0;
  if (sth_status_new(&%(sta)s) != STH_OK)
  {
    goto %(err)s;
  }

  if (sth_main(%(sta)s, &%(sthret)s, %(arg)s) != STH_OK)
  {
    goto %(err)s;
  }

  %(ret)s = %(sthret)s->value;
  if (%(sthret)s->free(%(sthret)s) != STH_OK)
  {
    goto %(err)s;
  }

  sth_status_free(%(sta)s);
  return %(ret)s;
  %(err)s:
  

  fprintf(stderr, "Uncaught exception");
  if (%(sta)s)
  {
    fprintf(stderr, ": %%d\\n", %(sta)s->status);
    return %(sta)s->status;
  }
  else
  {
    fprintf(stderr, "\\n");
    return -1;
  }

}

""" % dict(
        ret='_%d' % (lastid + 1),
        sta='_%d' % (lastid + 2),
        arg='_%d' % (lastid + 3),
        sthret='_%d' % (lastid + 4),
        err='_%d' % (lastid + 5))
    assert unparse(translate(prepare(typify(simplify(parse(src)))))) == (
            header + dst + mainfunc)


def test_simple():
    assert_translate(
"""def main(args: List[str]) -> int:
    return 0
""",
"""SthRet sth_main(SthStatus *_1, SthInt **_2, SthList *args)
{
  SthInt *_3;
  if (sth_int_new(_1, &_3, 0) != STH_OK)
  {
    goto _4;
  }

  *_2 = _3;
  goto _4;
  _4:
  

  return _1->status;
}

""", 0, 4)


def test_funcdef():
    assert_translate(
"""def add1(n : int) -> int:
    return n + 1


def main(args: List[str]) -> int:
    x = add1(9)
    return x
""",
"""SthRet add1(SthStatus *_1, SthInt **_2, SthInt *n)
{
  SthInt *_5;
  SthInt *_3;
  if (sth_int_new(_1, &_3, 1) != STH_OK)
  {
    goto _4;
  }

  if (n->__add__(_1, &_5, n, _3) != STH_OK)
  {
    goto _4;
  }

  *_2 = _5;
  goto _4;
  _4:
  

  return _1->status;
}

SthRet sth_main(SthStatus *_6, SthInt **_7, SthList *args)
{
  SthInt *x;
  SthInt *_8;
  if (sth_int_new(_6, &_8, 9) != STH_OK)
  {
    goto _9;
  }

  if (add1(_6, &x, _8) != STH_OK)
  {
    goto _9;
  }

  *_7 = x;
  goto _9;
  _9:
  

  return _6->status;
}

""", 0, 9)


def test_unique_name():
    assert_translate(
"""def main(args: List[str]) -> int:
    _1 = 0
    return _1
""",
"""SthRet sth_main(SthStatus *_2, SthInt **_3, SthList *args)
{
  SthInt *_1;
  SthInt *_4;
  if (sth_int_new(_2, &_4, 0) != STH_OK)
  {
    goto _5;
  }

  _1 = _4;
  *_3 = _1;
  goto _5;
  _5:
  

  return _2->status;
}

""", 0, 5)


def test_print_int():
    assert_translate(
"""
def main(args: List[str]) -> int:
    print(23)
    return 0
""",
"""SthRet sth_main(SthStatus *_1, SthInt **_2, SthList *args)
{
  SthInt *_6;
  SthCraw *_5;
  SthInt *_3;
  if (sth_int_new(_1, &_3, 23) != STH_OK)
  {
    goto _4;
  }

  if (sth_print(_1, &_5, _3) != STH_OK)
  {
    goto _4;
  }

  if (sth_int_new(_1, &_6, 0) != STH_OK)
  {
    goto _4;
  }

  *_2 = _6;
  goto _4;
  _4:
  

  return _1->status;
}

""", 0, 6)
