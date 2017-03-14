import pytest

from sth.ast import parse, unparse
from sth.simplifier import simplify


def assert_simplify(src, dst, ret):
    assert unparse(simplify(parse(src))) == dst


def test_boolops():
    assert_simplify(
"""def main(args: List[str]) -> int:
    x = (1 == 1)
    x = (1 != 1)
    x = (1 <= 1)
    x = (1 >= 1)
    x = (1 > 1)
    x = (1 < 1)
    return 0
""",
"""

def main(args: List[str]) -> int:
    x = 1 .__eq__(1)
    x = 1 .__ne__(1)
    x = 1 .__le__(1)
    x = 1 .__ge__(1)
    x = 1 .__gt__(1)
    x = 1 .__lt__(1)
    return 0
""", 0)


def test_mathops():
    assert_simplify(
"""def main(args: List[str]) -> int:
    x = 1 + 1
    x = x - 1
    x = x * 1
    x = x / 1
    x = x % 1
    return 0
""",
"""

def main(args: List[str]) -> int:
    x = 1 .__add__(1)
    x = x.__sub__(1)
    x = x.__mul__(1)
    x = x.__div__(1)
    x = x.__mod__(1)
    return 0
""", 0)


@pytest.mark.skipif(True, reason="Wait for tuple support")
def test_assignment():
    assert_simplify(
"""def main(args: List[str]) -> int:
    a, b, c = d, e, f = g, h, i = 1, 2, 3
    return 0
""",
"""

def main(args: List[str]) -> int:
    a = 1
    b = 2
    c = 3
    d = 1
    e = 2
    f = 3
    g = 1
    h = 2
    i = 3
    return 0
""", 0)


def test_augassignment():
    assert_simplify(
"""def main(args: List[str]) -> int:
    x += 1
    x -= 1
    x *= 1
    x /= 1
    x %= 1
    return 0
""",
"""

def main(args: List[str]) -> int:
    x = x.__add__(1)
    x = x.__sub__(1)
    x = x.__mul__(1)
    x = x.__div__(1)
    x = x.__mod__(1)
    return 0
""", 0)


def test_boolops_if():
    assert_simplify(
"""def main(args: List[str]) -> int:
    if i < 3:
        print(1)
    else:
        print(2)
    return 0
""",
"""

def main(args: List[str]) -> int:
    if i.__lt__(3):
        print(1)
    else:
        print(2)
    return 0
""", 0)


def test_boolops_while():
    assert_simplify(
"""def main(args: List[str]) -> int:
    i = 0
    while i < 10:
        print(1)
        i += 1
    return 0
""",
"""

def main(args: List[str]) -> int:
    i = 0
    while i.__lt__(10):
        print(1)
        i = i.__add__(1)
    return 0
""", 0)


def test_primes_example():
    assert_simplify(
"""def isprime(n: int) -> bool:
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
""",
"""

def isprime(n: int) -> bool:
    d = 2
    if n.__lt__(4):
        return True
    while d.__lt__(n.__div__(2)):
        if n.__mod__(d).__eq__(0):
            return False
        d = d.__add__(1)
    return True

def print_primes_from(start: int, end: int):
    while start.__le__(end):
        if isprime(start):
            print(start)
        start = start.__add__(1)

def main(args: List[str]) -> int:
    print_primes_from(1, 100)
    return 0
""", 0)
