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
    <genid1>{int} = 4.5{float}.__int__{self: float -> int}()
    x{int} = <genid1>{int}
    y{float} = 9.3{float}
    <genid2>{float} = 6{int} .__float__{self: int -> float}()
    y{float} = <genid2>{float}
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
    <genid1>{bool} = n{int}.__lt__{self: int, n: int -> bool}(10{int})
    return <genid1>{bool}

def funcfloat{f: float -> int}(f: float) -> int:
    return 3{int}

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{bool} = funcint{n: int -> bool}(3{int})
    y{int} = funcfloat{f: float -> int}(3.5{float})
    <genid2>{int} = funcfloat{f: float -> int}(3.14{float})
    z{bool} = funcint{n: int -> bool}(<genid2>{int})
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
    <genid1>{bool} = n{int}.__lt__{self: int, n: int -> bool}(10{int})
    return <genid1>{bool}

def funcfloat{f: float -> int}(f: float) -> int:
    return 3{int}

def main{args: List[str] -> int}(args: List[str]) -> int:
    <genid2>{int} = 3.5{float}.__int__{self: float -> int}()
    x{bool} = funcint{n: int -> bool}(<genid2>{int})
    <genid3>{float} = 3{int} .__float__{self: int -> float}()
    y{int} = funcfloat{f: float -> int}(<genid3>{float})
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
    <genid1>{float} = n{int}.__float__{self: int -> float}()
    return <genid1>{float}

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{float} = funcint{n: int -> float}(3{int})
    return 0{int}
""", 0)


def test_if_convert():
    assert_typify(
"""def main(args: List[str]) -> int:
    x = 10
    if x:
        x = 2
    return 0
""",
"""

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{int} = 10{int}
    <genid1>{bool} = x{int}.__bool__{self: int -> bool}()
    if <genid1>{bool}:
        x{int} = 2{int}
    return 0{int}
""", 0)


def test_while_convert():
    assert_typify(
"""def main(args: List[str]) -> int:
    x = 10
    while x:
        x -= 1
    return 0
""",
"""

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{int} = 10{int}
    <genid1>: <genid2>{bool} = x{int}.__bool__{self: int -> bool}()
    if <genid2>{bool}:
        x{int} = x{int}.__sub__{self: int, n: int -> int}(1{int})
        goto <genid1>
    return 0{int}
""", 0)


def test_if_nested():
    assert_typify(
"""def main(args: List[str]) -> int:
    x = 10
    if 4 < (x / 3):
        x -= 1
    return 0
""",
"""

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{int} = 10{int}
    <genid1>{int} = x{int}.__div__{self: int, n: int -> int}(3{int})
    <genid2>{bool} = 4{int} .__lt__{self: int, n: int -> bool}(<genid1>{int})
    if <genid2>{bool}:
        x{int} = x{int}.__sub__{self: int, n: int -> int}(1{int})
    return 0{int}
""", 0)


def test_free():
    assert_typify(
"""def main(args: List[str]) -> int:
    x = 10
    y = 3.4
    z = True
    free(x)
    free(y)
    free(z)
    return 0
""",
"""

def main{args: List[str] -> int}(args: List[str]) -> int:
    x{int} = 10{int}
    y{float} = 3.4{float}
    z{bool} = True{bool}
    <genid1>{craw} = x{int}.__craw__{self: int -> craw}()
    free{obj: craw -> }(<genid1>{craw})
    <genid2>{craw} = y{float}.__craw__{self: float -> craw}()
    free{obj: craw -> }(<genid2>{craw})
    <genid3>{craw} = z{bool}.__craw__{self: bool -> craw}()
    free{obj: craw -> }(<genid3>{craw})
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
    <genid1>{bool} = n{int}.__lt__{self: int, n: int -> bool}(4{int})
    if <genid1>{bool}:
        return True{bool}
    <genid2>: <genid3>{int} = n{int}.__div__{self: int, n: int -> int}(2{int})
    <genid4>{bool} = d{int}.__lt__{self: int, n: int -> bool}(<genid3>{int})
    if <genid4>{bool}:
        <genid5>{int} = n{int}.__mod__{self: int, n: int -> int}(d{int})
        <genid6>{bool} = <genid5>{int}.__eq__{self: int, n: int -> bool}(0{int})
        if <genid6>{bool}:
            return False{bool}
        d{int} = d{int}.__add__{self: int, n: int -> int}(1{int})
        goto <genid2>
    return True{bool}

def print_primes_from{start: int, end: int -> }(start: int, end: int):
    <genid7>: <genid8>{bool} = start{int}.__le__{self: int, n: int -> bool}(end{int})
    if <genid8>{bool}:
        <genid9>{bool} = isprime{n: int -> bool}(start{int})
        if <genid9>{bool}:
            print{s: int -> }(start{int})
        start{int} = start{int}.__add__{self: int, n: int -> int}(1{int})
        goto <genid7>

def main{args: List[str] -> int}(args: List[str]) -> int:
    print_primes_from{start: int, end: int -> }(1{int}, 100{int})
    return 0{int}
""", 0)
