import pytest
from helper import assert_compiled_output_python_compat


def test_int_add():
    assert_compiled_output_python_compat(
"""
def main(args: List[str]) -> int :
    x = 9
    y = 1
    z = x + y
    print(z)
    free(x)
    free(y)
    free(z)
    return 0
""")


def test_int_ops():
    assert_compiled_output_python_compat(
"""
def main(args: List[str]) -> int :
    print(10 + 5)
    print(10 - 5)
    print(10 * 5)
    print(10 % 6)
    return 0
""", valgrind=False)
