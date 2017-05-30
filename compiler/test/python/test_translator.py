from sth.ast import parse
from sth.simplifier import simplify
from sth.typifier import typify
from sth.preparator import prepare
from sth.translator import translate, unparse


def assert_translate(src, dst, ret):
    assert unparse(translate(prepare(typify(simplify(parse(src)))))) == dst


def test_simple():
    assert_translate(
"""def main(args: List[str]) -> int:
    return 0
""",
"""SthRet sth_main(SthStatus *_1)
{
  SthInt *_3;
  SthList *args;
  args = (SthList *) _1->current_frame->arg_values[0];
  if (sth_frame_new(_1, 0, 1) != STH_OK)
  {
    goto _2;
  }

  if (sth_int_new(_1) != STH_OK)
  {
    goto _2;
  }

  _3 = (SthInt *) _1->current_frame->return_values[0];
  if (sth_frame_free(_1) != STH_OK)
  {
    goto _2;
  }

  _3->value = 0;
  _1->current_frame->return_values[0] = (void *) _3;
  goto _2;
  _2:
  

  return _1->status;
}

""", 0)


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
  n = (SthInt *) _1->current_frame->arg_values[0];
  if (sth_frame_new(_1, 0, 1) != STH_OK)
  {
    goto _2;
  }

  if (sth_int_new(_1) != STH_OK)
  {
    goto _2;
  }

  _3 = (SthInt *) _1->current_frame->return_values[0];
  if (sth_frame_free(_1) != STH_OK)
  {
    goto _2;
  }

  _3->value = 1;
  if (sth_frame_new(_1, 2, 1) != STH_OK)
  {
    goto _2;
  }

  _1->current_frame->arg_values[0] = (void *) n;
  _1->current_frame->arg_values[1] = (void *) _3;
  if (n->__add__(_1) != STH_OK)
  {
    goto _2;
  }

  _4 = (SthInt *) _1->current_frame->return_values[0];
  if (sth_frame_free(_1) != STH_OK)
  {
    goto _2;
  }

  _1->current_frame->return_values[0] = (void *) _4;
  goto _2;
  _2:
  

  return _1->status;
}

SthRet sth_main(SthStatus *_5)
{
  SthInt *x;
  SthInt *_7;
  SthList *args;
  args = (SthList *) _5->current_frame->arg_values[0];
  if (sth_frame_new(_5, 0, 1) != STH_OK)
  {
    goto _6;
  }

  if (sth_int_new(_5) != STH_OK)
  {
    goto _6;
  }

  _7 = (SthInt *) _5->current_frame->return_values[0];
  if (sth_frame_free(_5) != STH_OK)
  {
    goto _6;
  }

  _7->value = 9;
  if (sth_frame_new(_5, 1, 1) != STH_OK)
  {
    goto _6;
  }

  _5->current_frame->arg_values[0] = (void *) _7;
  if (add1(_5) != STH_OK)
  {
    goto _6;
  }

  x = (SthInt *) _5->current_frame->return_values[0];
  if (sth_frame_free(_5) != STH_OK)
  {
    goto _6;
  }

  _5->current_frame->return_values[0] = (void *) x;
  goto _6;
  _6:
  

  return _5->status;
}

""", 0)


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
  args = (SthList *) _2->current_frame->arg_values[0];
  if (sth_frame_new(_2, 0, 1) != STH_OK)
  {
    goto _3;
  }

  if (sth_int_new(_2) != STH_OK)
  {
    goto _3;
  }

  _4 = (SthInt *) _2->current_frame->return_values[0];
  if (sth_frame_free(_2) != STH_OK)
  {
    goto _3;
  }

  _4->value = 0;
  _1 = _4;
  _2->current_frame->return_values[0] = (void *) _1;
  goto _3;
  _3:
  

  return _2->status;
}

""", 0)
