import pytest

from sth.ast import parse


def assert_raises_syntax_error(code):
    with pytest.raises(SyntaxError):
        parse(code)


def assert_parses_ok(code):
    parse(code)


def test_restrict_str():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = "hello"
    return 0
""")


def test_restrict_tuple():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = (1, 3.14, False)
    return 0
""")


def test_restrict_and():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = True and True
    return 0
""")


def test_restrict_or():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = True or True
    return 0
""")


def test_restrict_as():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    with open(__file__, "r") as f:
        x = 3
    return 0
""")

def test_restrict_assert():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    assert 1
    return 0
""")


def test_restrict_del():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = 4
    del x
    return 0
""")


def test_restrict_try_except():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    try:
        x = 9
    except:
        x = 10
    return 0
""")


def test_restrict_finally():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    try:
        x = 9
    except:
        x = 10
    finally:
        y = 11
    return 0
""")


def test_restrict_for():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    for s in "ab":
        print(s)
    return 0
""")


def test_restrict_from():
    assert_raises_syntax_error(
"""from file import open

def main(args: List[str]) -> int:
    return 0
""")


def test_restrict_global():
    assert_raises_syntax_error(
"""x = 3


def main(args: List[str]) -> int:
    global x
    return 0
""")


def test_restrict_import():
    assert_raises_syntax_error(
"""import file


def main(args: List[str]) -> int:
    return 0
""")


def test_restrict_in():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = 'c' in 'abc'
    return 0
""")


def test_restrict_notin():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = 'c' not in 'abc'
    return 0
""")


def test_restrict_is():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = 3 is 4
    return 0
""")


def test_restrict_isnot():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = 3 is not 4
    return 0
""")


def test_restrict_lambda():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = lambda: 3
    return 0
""")


def test_restrict_nonlocal():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    nonlocal x
    return 0
""")


def test_restrict_not():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = not True
    return 0
""")


def test_restrict_pass():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    if True:
        pass
    return 0
""")


def test_restrict_raise():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    raise SyntaxError("error")
    return 0
""")


def test_restrict_with():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    with open(__file__, "r"):
        x = 3
    return 0
""")


def test_restrict_yield():
    assert_raises_syntax_error(
"""def ones() -> Generator[int]:
    yield 1


def main(args: List[str]) -> int:
    return 0
""")


def test_restrict_yieldfrom():
    assert_raises_syntax_error(
"""def ranger() -> Generator[int]:
    yield from range(3)


def main(args: List[str]) -> int:
    return 0
""")


def test_restrict_asyncfor():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    async for x in 'ab':
        print(x)
    return 0
""")


def test_restrict_asyncfuncdef():
    assert_raises_syntax_error(
"""async def add1(x: int) -> int:
    return x + 1


def main(args: List[str]) -> int:
    return 0
""")


def test_restrict_asyncawait():
    assert_raises_syntax_error(
"""async def add1(x: int) -> int:
    await asyncio.sleep(9)
    return x + 1


def main(args: List[str]) -> int:
    return 0
""")


def test_restrict_asyncwith():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    async with open(__file__, 'r'):
        x = 9
    return 0
""")


def test_restrict_bitand():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = 16 & 8
    return 0
""")


def test_restrict_bitor():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = 16 & 8
    return 0
""")


def test_restrict_list():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = [1, 2, 3]
    return 0
""")


def test_restrict_listcomp():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = [ x + 1 for x in [ 1, 2, 3, 4 ] ]
    return 0
""")


def test_restrict_dict():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = {x:1, y:2}
    return 0
""")


def test_restrict_dictcomp():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = { (x, y) for x, y in ( (1, 2), (3, 4)) }
    return 0
""")


def test_restrict_set():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = { 1, 2, 3, 4 }
    return 0
""")


def test_restrict_setcomp():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = { x for x in { 1, 2, 3, 4 } }
    return 0
""")


def test_restrict_ellipsis():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    ...
    return 0
""")


def test_restrict_slice_1():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = args[0]
    return 0
""")


def test_restrict_slice_2():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = args[0:-1]
    return 0
""")


def test_restrict_percent():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = "%d" % 3
    return 0
""")


def test_restrict_floordiv():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = 5 // 2
    return 0
""")


def test_restrict_bitxor():
    assert_raises_syntax_error(
"""
def main(args: List[str]) -> int:
    x = 16 ^ 8
    return 0
""")


def test_restrict_invert():
    assert_raises_syntax_error(
"""
def main(args: List[str]) -> int:
    x = 3
    ~x
    return 0
""")


def test_restrict_lshift():
    assert_raises_syntax_error(
"""
def main(args: List[str]) -> int:
    x = 3 << 1
    return 0
""")


def test_restrict_rshift():
    assert_raises_syntax_error(
"""
def main(args: List[str]) -> int:
    x = 3 >> 1
    return 0
""")


def test_restrict_pow():
    assert_raises_syntax_error(
"""
def main(args: List[str]) -> int:
    x = 3 ** 3
    return 0
""")


def test_restrict_starred_func_1():
    assert_raises_syntax_error(
"""def x(*args: List[str]) -> int:
    return 3

def main(args: List[str]) -> int:
    return 0
""")


def test_restrict_starred_func_2():
    assert_raises_syntax_error(
"""def x(**kwargs: Dict[str, str]) -> int:
    return 3

def main(args: List[str]) -> int:
    return 0
""")


def test_restrict_starred_1():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    l = [1, 2, 3]
    print(*l)
    return 0
""")


def test_restrict_starred_2():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    d = dict(x=1, y=2)
    print(**l)
    return 0
""")


def test_restrict_missing_types_arg1():
    assert_raises_syntax_error(
"""def main(args) -> int:
    return 0
""")


def test_restrict_missing_types_arg2():
    assert_raises_syntax_error(
"""def add1(i) -> int:
    return i + 1


def main(args: List[str]) -> int:
    return 0
""")


def test_restrict_nested_functions():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    def add1(x: int) -> int:
        return x + 1
    return 0
""")


def test_restrict_positional_args():
    assert_raises_syntax_error(
"""def add1(n: int) -> int:
    return n + 1


def main(args: List[str]) -> int:
    add1(n=3)
    return 0
""")


def test_restrict_multicompare():
    assert_raises_syntax_error(
"""def main(args: List[str]) -> int:
    x = 1 < 2 < 3
    return 0
""")


def test_primes_example():
    assert_parses_ok(
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
""")
