from helper import assert_transpiled_output


def test_hello_world():
    assert_transpiled_output(
"""
def main(args: List[str]) -> int:
    return 0
""",
"""#include "sth/sth.h"

SthRet sth_main(SthStatus *_1)
{
  SthInt *_3;
  SthList *args;
  args = (SthList* ) _1->current_frame->arg_values[0];
  if (sth_frame_new(_1, 0, 1) != STH_OK)
  {
    goto _2;
  }

  if (sth_int_new(_1) != STH_OK)
  {
    goto _2;
  }

  _3 = (SthInt* ) _1->current_frame->return_values[0];
  if (sth_frame_free(_1) != STH_OK)
  {
    goto _2;
  }

  _3->value = 0;
  _1->current_frame->return_values[0] = (void* ) _3;
  goto _2;
  _2:
  

  return _1->status;
}

int main(int argc, char **argv)
{
  int _4;
  SthStatus *_5;
  SthList *_6;
  SthInt *_7;
  _4 = 0;
  _5 = 0;
  _6 = 0;
  _7 = 0;
  if (sth_status_new(&_5) != STH_OK)
  {
    goto _8;
  }

  if (sth_frame_new(_5, 1, 1) != STH_OK)
  {
    goto _8;
  }

  _5->current_frame->arg_values[0] = (void* ) _6;
  if (sth_main(_5) != STH_OK)
  {
    goto _8;
  }

  _7 = (SthInt* ) _5->current_frame->return_values[0];
  _4 = _7->value;
  if (sth_frame_free(_5) != STH_OK)
  {
    goto _8;
  }

  if (sth_frame_new(_5, 1, 0) != STH_OK)
  {
    goto _8;
  }

  _5->current_frame->arg_values[0] = (void* ) _7;
  if (sth_int_free(_5) != STH_OK)
  {
    goto _8;
  }

  if (sth_frame_free(_5) != STH_OK)
  {
    goto _8;
  }

  sth_status_free(_5);
  return _4;
  _8:
  

  fprintf(stderr, "Uncaught exception");
  if (_5)
  {
    fprintf(stderr, ": %d\\n", _5->status);
    return _5->status;
  }
  else
  {
    fprintf(stderr, "\\n");
    return -1;
  }

}

""", 0)
