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

  if (sth_status_frame_add(%(sta)s, 1, 1) != STH_OK)
  {
    goto %(err)s;
  }

  sth_status_frame_argval_set(%(sta)s, 0, (void* ) %(arg)s);
  if (sth_main(%(sta)s) != STH_OK)
  {
    goto %(err)s;
  }

  %(sthret)s = (SthInt* ) sth_status_frame_retval_get(%(sta)s, 0);
  %(ret)s = %(sthret)s->value;
  if (sth_status_frame_remove(%(sta)s) != STH_OK)
  {
    goto %(err)s;
  }

  if (sth_status_frame_add(%(sta)s, 1, 0) != STH_OK)
  {
    goto %(err)s;
  }

  sth_status_frame_argval_set(%(sta)s, 0, (void* ) %(sthret)s);
  if (sth_int_free(%(sta)s) != STH_OK)
  {
    goto %(err)s;
  }

  if (sth_status_frame_remove(%(sta)s) != STH_OK)
  {
    goto %(err)s;
  }

  sth_status_free(%(sta)s);
  return %(ret)s;
  %(err)s:
  

  fprintf(stderr, "Uncaught exception");
  if (%(sta)s)
  {
    fprintf(stderr, ": %%d\\n", sth_status_status_get(%(sta)s));
    return sth_status_status_get(%(sta)s);
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
"""SthRet sth_main(SthStatus *_1)
{
  SthInt *_3;
  SthList *args;
  args = (SthList* ) sth_status_frame_argval_get(_1, 0);
  if (sth_status_frame_add(_1, 0, 1) != STH_OK)
  {
    goto _2;
  }

  if (sth_int_new(_1) != STH_OK)
  {
    goto _2;
  }

  _3 = (SthInt* ) sth_status_frame_retval_get(_1, 0);
  if (sth_status_frame_remove(_1) != STH_OK)
  {
    goto _2;
  }

  _3->value = 0;
  sth_status_frame_retval_set(_1, 0, (void* ) _3);
  goto _2;
  _2:
  

  return sth_status_status_get(_1);
}

""", 0, 3)


def test_funcdef():
    assert_translate(
"""def add1(n : int) -> int:
    return n + 1


def main(args: List[str]) -> int:
    x = add1(9)
    return x
""",
"""SthRet add1(SthStatus *_1)
{
  SthInt *_4;
  SthInt *_3;
  SthInt *n;
  n = (SthInt* ) sth_status_frame_argval_get(_1, 0);
  if (sth_status_frame_add(_1, 0, 1) != STH_OK)
  {
    goto _2;
  }

  if (sth_int_new(_1) != STH_OK)
  {
    goto _2;
  }

  _3 = (SthInt* ) sth_status_frame_retval_get(_1, 0);
  if (sth_status_frame_remove(_1) != STH_OK)
  {
    goto _2;
  }

  _3->value = 1;
  if (sth_status_frame_add(_1, 2, 1) != STH_OK)
  {
    goto _2;
  }

  sth_status_frame_argval_set(_1, 0, (void* ) n);
  sth_status_frame_argval_set(_1, 1, (void* ) _3);
  if (n->__add__(_1) != STH_OK)
  {
    goto _2;
  }

  _4 = (SthInt* ) sth_status_frame_retval_get(_1, 0);
  if (sth_status_frame_remove(_1) != STH_OK)
  {
    goto _2;
  }

  sth_status_frame_retval_set(_1, 0, (void* ) _4);
  goto _2;
  _2:
  

  return sth_status_status_get(_1);
}

SthRet sth_main(SthStatus *_5)
{
  SthInt *x;
  SthInt *_7;
  SthList *args;
  args = (SthList* ) sth_status_frame_argval_get(_5, 0);
  if (sth_status_frame_add(_5, 0, 1) != STH_OK)
  {
    goto _6;
  }

  if (sth_int_new(_5) != STH_OK)
  {
    goto _6;
  }

  _7 = (SthInt* ) sth_status_frame_retval_get(_5, 0);
  if (sth_status_frame_remove(_5) != STH_OK)
  {
    goto _6;
  }

  _7->value = 9;
  if (sth_status_frame_add(_5, 1, 1) != STH_OK)
  {
    goto _6;
  }

  sth_status_frame_argval_set(_5, 0, (void* ) _7);
  if (add1(_5) != STH_OK)
  {
    goto _6;
  }

  x = (SthInt* ) sth_status_frame_retval_get(_5, 0);
  if (sth_status_frame_remove(_5) != STH_OK)
  {
    goto _6;
  }

  sth_status_frame_retval_set(_5, 0, (void* ) x);
  goto _6;
  _6:
  

  return sth_status_status_get(_5);
}

""", 0, 7)


def test_unique_name():
    assert_translate(
"""def main(args: List[str]) -> int:
    _1 = 0
    return _1
""",
"""SthRet sth_main(SthStatus *_2)
{
  SthInt *_1;
  SthInt *_4;
  SthList *args;
  args = (SthList* ) sth_status_frame_argval_get(_2, 0);
  if (sth_status_frame_add(_2, 0, 1) != STH_OK)
  {
    goto _3;
  }

  if (sth_int_new(_2) != STH_OK)
  {
    goto _3;
  }

  _4 = (SthInt* ) sth_status_frame_retval_get(_2, 0);
  if (sth_status_frame_remove(_2) != STH_OK)
  {
    goto _3;
  }

  _4->value = 0;
  _1 = _4;
  sth_status_frame_retval_set(_2, 0, (void* ) _1);
  goto _3;
  _3:
  

  return sth_status_status_get(_2);
}

""", 0, 4)
