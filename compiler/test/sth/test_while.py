import pytest
from helper import assert_compiled_output_python_compat


def test_while_simple():
    assert_compiled_output_python_compat(
"""
def main(args: List[str]) -> int :
    x = 5
    while x < 10:
        print(x)
        x = x + 1
    return 0
""", valgrind=False)


def test_primes():
    assert_compiled_output_python_compat(
"""
def isprime(n: int) -> bool:
    d = 2
    if n < 4:
        return True
    while d < (n / 2):
        if n % d == 0:
            return False
        d += 1
    return True


def print_primes_from(start: int, end: int):
    while start <= end:
        if isprime(start):
            print(start)
        start += 1


def main(args: List[str]) -> int:
    print_primes_from (1, 100)
    return 0
""", valgrind=False)
