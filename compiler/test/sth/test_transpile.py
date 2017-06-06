from helper import assert_transpiled_output


def test_hello_world():
    assert_transpiled_output(
"""
def main(args: List[str]) -> int:
    return 0
""",
"""#include "sth/sth.h"

SthRet sth_main(SthStatus *_1, SthInt **_2, SthList *args)
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

int main(int argc, char **argv)
{
  int _5;
  SthStatus *_6;
  SthList *_7;
  SthInt *_8;
  _5 = 0;
  _6 = 0;
  _7 = 0;
  _8 = 0;
  if (sth_status_new(&_6) != STH_OK)
  {
    goto _9;
  }

  if (sth_main(_6, &_8, _7) != STH_OK)
  {
    goto _9;
  }

  _5 = _8->value;
  if (_8->free(_8) != STH_OK)
  {
    goto _9;
  }

  sth_status_free(_6);
  return _5;
  _9:
  

  fprintf(stderr, "Uncaught exception");
  if (_6)
  {
    fprintf(stderr, ": %d\\n", _6->status);
    return _6->status;
  }
  else
  {
    fprintf(stderr, "\\n");
    return -1;
  }

}

""", 0)
