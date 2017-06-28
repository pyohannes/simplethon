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
    <genid1> = i.__lt__(3)
    if <genid1>:
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
    <genid1>: <genid2> = i.__lt__(10)
    if <genid2>:
        print(1)
        i = i.__add__(1)
        goto <genid1>
    return 0
""", 0)


def test_funcarg_1():
    assert_simplify(
"""def add(x: int, y: int) -> int:
    return x + y


def main(args: List[str]) -> int:
    x = add(add(3, 4), add(5, add(6, 7)))
    return 0
""",
"""

def add(x: int, y: int) -> int:
    <genid1> = x.__add__(y)
    return <genid1>

def main(args: List[str]) -> int:
    <genid2> = add(6, 7)
    <genid3> = add(3, 4)
    <genid4> = add(5, <genid2>)
    x = add(<genid3>, <genid4>)
    return 0
""", 0)


def test_funcarg_2():
    assert_simplify(
"""def main(args: List[str]) -> int:
    x = 5 + 6 + 7
    return 0
""",
"""

def main(args: List[str]) -> int:
    <genid1> = 5 .__add__(6)
    x = <genid1>.__add__(7)
    return 0
""", 0)


def test_while_break():
    assert_simplify(
"""def main(args: List[str]) -> int:
    i = 10
    while True:
        if i:
            i -= 1
        else:
            break
    return 0
""",
"""

def main(args: List[str]) -> int:
    i = 10
    <genid1>: if True:
        if i:
            i = i.__sub__(1)
        else:
            goto <genid2>
        goto <genid1>
    <genid2>: pass
    return 0
""", 0)


def test_while_continue_break():
    assert_simplify(
"""def main(args: List[str]) -> int:
    i = 10
    y = 0
    while True:
        i -= 1
        if i == 0:
            break
        if i % 2 == 0:
            continue
        y += 1
    return 0
""",
"""

def main(args: List[str]) -> int:
    i = 10
    y = 0
    <genid1>: if True:
        i = i.__sub__(1)
        <genid2> = i.__eq__(0)
        if <genid2>:
            goto <genid3>
        <genid4> = i.__mod__(2)
        <genid5> = <genid4>.__eq__(0)
        if <genid5>:
            goto <genid1>
        y = y.__add__(1)
        goto <genid1>
    <genid3>: pass
    return 0
""", 0)


def test_while_break_else():
    assert_simplify(
"""def main(args: List[str]) -> int:
    i = 10
    while i > 0:
        i -= 1
        if i % 11:
            break
    else:
        i = 11
    return 0
""",
"""

def main(args: List[str]) -> int:
    i = 10
    <genid1>: <genid2> = i.__gt__(0)
    if <genid2>:
        i = i.__sub__(1)
        <genid3> = i.__mod__(11)
        if <genid3>:
            goto <genid4>
        goto <genid1>
    else:
        i = 11
    <genid4>: pass
    return 0
""", 0)


def test_if_nested():
    assert_simplify(
"""def main(args: List[str]) -> int:
    x = 10
    if 4 < (x / 3):
        x -= 1
    return 0
""",
"""

def main(args: List[str]) -> int:
    x = 10
    <genid1> = x.__div__(3)
    <genid2> = 4 .__lt__(<genid1>)
    if <genid2>:
        x = x.__sub__(1)
    return 0
""", 0)


def test_class_strtypes():
    assert_simplify(
"""class X():
    def __init__(self: 'X'):
        self.x = 9

    def get_self(self: 'X') -> 'X':
        return self
""",
"""

class X():

    def __init__(self: X):
        self.x = 9

    def get_self(self: X) -> X:
        return self
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
    <genid1> = n.__lt__(4)
    if <genid1>:
        return True
    <genid2>: <genid3> = n.__div__(2)
    <genid4> = d.__lt__(<genid3>)
    if <genid4>:
        <genid5> = n.__mod__(d)
        <genid6> = <genid5>.__eq__(0)
        if <genid6>:
            return False
        d = d.__add__(1)
        goto <genid2>
    return True

def print_primes_from(start: int, end: int):
    <genid7>: <genid8> = start.__le__(end)
    if <genid8>:
        <genid9> = isprime(start)
        if <genid9>:
            print(start)
        start = start.__add__(1)
        goto <genid7>

def main(args: List[str]) -> int:
    print_primes_from(1, 100)
    return 0
""", 0)
