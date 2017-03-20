import pytest

from sth.ast import parse, unparse
from sth.simplifier import simplify
from sth.typifier import typify


def assert_typify(src, dst, ret):
    assert unparse(typify(simplify(parse(src)))) == dst


def test_simple():
    assert_typify(
"""def main(args: List[str]) -> int:
    return 0
""",
"""

def main{args: List[str] -> int}(args: List[str]) -> int:
    return 0{int}
""", 0)


@pytest.mark.skipif(True, reason="Wait for tuple support")
def test_nested_collection():
    assert_typify(
"""def nested(n: MyType1[MyType2[List[str], float, int], MyType2[str, float, int]], i: int) -> int:
    return 0


def main(args: List[str]) -> int:
    return 0
""",
"""

def nested{n: MyType1[MyType2[List[str], float, int], MyType2[str, float, int]], i: int -> int}(n: MyType1[MyType2[List[str], float, int], MyType2[str, float, int]], i: int) -> int:
    return 0{int}


def main{args: List[str] -> int}(args: List[str]) -> int:
    return 0{int}
""", 0)


def test_num():
    assert_typify(
"""def main(args: List[str]) -> int:
    x = 10
    y = 9.3
    return 0
""",
"""

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{int} = 10{int}
    y{float} = 9.3{float}
    return 0{int}
""", 0)


def test_num_convert():
    assert_typify(
"""def main(args: List[str]) -> int:
    x = 10
    x = 4.5
    y = 9.3
    y = 6
    return 0
""",
"""

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{int} = 10{int}
    x{int} = 4.5{float}.__int__{self: float -> int}()
    y{float} = 9.3{float}
    y{float} = 6{int} .__float__{self: int -> float}()
    return 0{int}
""", 0)


def test_variable():
    assert_typify(
"""def main(args: List[str]) -> int:
    x = 10
    y = x
    return 0
""",
"""

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{int} = 10{int}
    y{int} = x{int}
    return 0{int}
""", 0)


def test_variable_scoped():
    assert_typify(
"""def main(args: List[str]) -> int:
    x = 10
    if True:
        y = x
        if True:
            z = y
        z = 10.3
    y = 9.5
    return 0
""",
"""

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{int} = 10{int}
    if True{bool}:
        y{int} = x{int}
        if True{bool}:
            z{int} = y{int}
        z{float} = 10.3{float}
    y{float} = 9.5{float}
    return 0{int}
""", 0)


def test_subscript():
    assert_typify(
"""def main(args: List[str]) -> int:
    x = 3
    y = x < 9
    return 0
""",
"""

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{int} = 3{int}
    y{bool} = x{int}.__lt__{self: int, n: int -> bool}(9{int})
    return 0{int}
""", 0)


def test_arg():
    assert_typify(
"""def funcint(n: int) -> bool:
    return n < 10


def funcfloat(f: float) -> int:
    return 3


def main(args: List[str]) -> int:
    x = funcint(3)
    y = funcfloat(3.5)
    z = funcint(funcfloat(3.14))
    return 0
""",
"""

def funcint{n: int -> bool}(n: int) -> bool:
    return n{int}.__lt__{self: int, n: int -> bool}(10{int})

def funcfloat{f: float -> int}(f: float) -> int:
    return 3{int}

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{bool} = funcint{n: int -> bool}(3{int})
    y{int} = funcfloat{f: float -> int}(3.5{float})
    z{bool} = funcint{n: int -> bool}(funcfloat{f: float -> int}(3.14{float}))
    return 0{int}
""", 0)


def test_arg_convert():
    assert_typify(
"""def funcint(n: int) -> bool:
    return n < 10


def funcfloat(f: float) -> int:
    return 3


def main(args: List[str]) -> int:
    x = funcint(3.5)
    y = funcfloat(3)
    return 0
""",
"""

def funcint{n: int -> bool}(n: int) -> bool:
    return n{int}.__lt__{self: int, n: int -> bool}(10{int})

def funcfloat{f: float -> int}(f: float) -> int:
    return 3{int}

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{bool} = funcint{n: int -> bool}(3.5{float}.__int__{self: float -> int}())
    y{int} = funcfloat{f: float -> int}(3{int} .__float__{self: int -> float}())
    return 0{int}
""", 0)


def test_return_empty():
    assert_typify(
"""def funcint(n: int):
    return


def main(args: List[str]) -> int:
    funcint(3)
    return 0
""",
"""

def funcint{n: int -> }(n: int):
    return

def main{args: List[str] -> int}(args: List[str]) -> int:
    funcint{n: int -> }(3{int})
    return 0{int}
""", 0)


def test_return_convert():
    assert_typify(
"""def funcint(n: int) -> float:
    return n


def main(args: List[str]) -> int:
    x = funcint(3)
    return 0
""",
"""

def funcint{n: int -> float}(n: int) -> float:
    return n{int}.__float__{self: int -> float}()

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{float} = funcint{n: int -> float}(3{int})
    return 0{int}
""", 0)


def test_primes_example():
    assert_typify(
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

def isprime{n: int -> bool}(n: int) -> bool:
    d{int} = 2{int}
    if n{int}.__lt__{self: int, n: int -> bool}(4{int}):
        return True{bool}
    while d{int}.__lt__{self: int, n: int -> bool}(n{int}.__div__{self: int, n: int -> int}(2{int})):
        if n{int}.__mod__{self: int, n: int -> int}(d{int}).__eq__{self: int, n: int -> bool}(0{int}):
            return False{bool}
        d{int} = d{int}.__add__{self: int, n: int -> int}(1{int})
    return True{bool}

def print_primes_from{start: int, end: int -> }(start: int, end: int):
    while start{int}.__le__{self: int, n: int -> bool}(end{int}):
        if isprime{n: int -> bool}(start{int}):
            print{s: int -> }(start{int})
        start{int} = start{int}.__add__{self: int, n: int -> int}(1{int})

def main{args: List[str] -> int}(args: List[str]) -> int:
    print_primes_from{start: int, end: int -> }(1{int}, 100{int})
    return 0{int}
""", 0)
