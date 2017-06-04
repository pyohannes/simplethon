import pytest
from helper import assert_compiled_output_python_compat


def test_print_int():
    assert_compiled_output_python_compat(
"""
def main(args: List[str]) -> int :
    x = 9
    print(x)
    free(x)
    return 0
""")
