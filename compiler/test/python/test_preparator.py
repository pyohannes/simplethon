from sth.ast import parse, unparse
from sth.simplifier import simplify
from sth.typifier import typify
from sth.preparator import prepare


def assert_prepare(src, dst, ret):
    assert unparse(prepare(typify(simplify(parse(src))))) == dst


def test_simple():
    assert_prepare(
"""def main(args: List[str]) -> int:
    return 0
""",
"""

def main{args: List[str] -> int}(id@1: SthStatus, *id@2: int, args: List[str]) -> int:
    if (sth_int_new{ -> int}(id@1{SthStatus}, &id@3{int}, 0{int}) != STH_OK{SthRet}):
        goto id@4
    *id@2{int} = id@3{int}
    goto id@4
    id@4: return id@1{SthStatus}.status
""", 0)


def test_funcdef():
    assert_prepare(
"""def add1(n : int) -> int:
    return n + 1


def main(args: List[str]) -> int:
    x = add1(9)
    return x
""",
"""

def add1{n: int -> int}(id@1: SthStatus, *id@2: int, n: int) -> int:
    if (sth_int_new{ -> int}(id@1{SthStatus}, &id@3{int}, 1{int}) != STH_OK{SthRet}):
        goto id@4
    if (n{int}.__add__{self: int, n: int -> int}(id@1{SthStatus}, &id@5{int}, n{int}, id@3{int}) != STH_OK{SthRet}):
        goto id@4
    *id@2{int} = id@5{int}
    goto id@4
    id@4: return id@1{SthStatus}.status

def main{args: List[str] -> int}(id@6: SthStatus, *id@7: int, args: List[str]) -> int:
    if (sth_int_new{ -> int}(id@6{SthStatus}, &id@8{int}, 9{int}) != STH_OK{SthRet}):
        goto id@9
    if (add1{n: int -> int}(id@6{SthStatus}, &x{int}, id@8{int}) != STH_OK{SthRet}):
        goto id@9
    *id@7{int} = x{int}
    goto id@9
    id@9: return id@6{SthStatus}.status
""", 0)


def test_class_init():
    assert_prepare(
"""
class Point():
    def __init__(self: 'Point', x: int, y: int):
        self.x = x
        self.y = y

def main(args: List[str]) -> int:
    c = Point(0, 0)
    return 0
""",
"""

class id@1():
    __cls__
    x{int}
    y{int}

class id@2():
    __size__{int}
    __craw__{self: Point -> craw}
    __new__{ -> Point}
    __init__{self: Point, x: int, y: int -> }

def id@3{ -> Point}(id@4: SthStatus, *id@5: Point):
    if (sth_allocate(id@4{SthStatus}, &id@6{Point}, Point{class[Point]}.__size__) != STH_OK{SthRet}):
        goto id@7
    id@6{Point}.__cls__ = &Point{class[Point]}
    *id@5{Point} = id@6{Point}
    goto id@7
    id@7: return id@4{SthStatus}.status

def id@8{self: Point, x: int, y: int -> }(id@9: SthStatus, *id@10: craw, self: Point, x: int, y: int):
    self{Point}.x{int} = x{int}
    self{Point}.y{int} = y{int}
    id@11: return id@9{SthStatus}.status
Point{class[Point]} = id@2(sth_sizeof(id@2), id@3, id@8)

def main{args: List[str] -> int}(id@12: SthStatus, *id@13: int, args: List[str]) -> int:
    if (Point{class[Point]}.__new__{ -> Point}(id@12{SthStatus}, &c{Point}, Point{class[Point]}) != STH_OK{SthRet}):
        goto id@14
    if (sth_int_new{ -> int}(id@12{SthStatus}, &id@15{int}, 0{int}) != STH_OK{SthRet}):
        goto id@14
    if (sth_int_new{ -> int}(id@12{SthStatus}, &id@16{int}, 0{int}) != STH_OK{SthRet}):
        goto id@14
    
    if (c{Point}.__init__{self: Point, x: int, y: int -> }(id@12{SthStatus}, &id@17{craw}, c{Point}, id@15{int}, id@16{int}) != STH_OK{SthRet}):
        goto id@14
    if (sth_int_new{ -> int}(id@12{SthStatus}, &id@18{int}, 0{int}) != STH_OK{SthRet}):
        goto id@14
    *id@13{int} = id@18{int}
    goto id@14
    id@14: return id@12{SthStatus}.status
""", 0)


def test_primes_example():
    assert_prepare(
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

def isprime{n: int -> bool}(id@1: SthStatus, *id@2: bool, n: int) -> bool:
    if (sth_int_new{ -> int}(id@1{SthStatus}, &id@3{int}, 2{int}) != STH_OK{SthRet}):
        goto id@4
    d{int} = id@3{int}
    if (sth_int_new{ -> int}(id@1{SthStatus}, &id@5{int}, 4{int}) != STH_OK{SthRet}):
        goto id@4
    if (n{int}.__lt__{self: int, n: int -> bool}(id@1{SthStatus}, &id@6{bool}, n{int}, id@5{int}) != STH_OK{SthRet}):
        goto id@4
    if id@6{bool}.value{bool}:
        *id@2{bool} = Sth_True{bool}
        goto id@4
    id@7: if (sth_int_new{ -> int}(id@1{SthStatus}, &id@8{int}, 2{int}) != STH_OK{SthRet}):
        goto id@4
    if (n{int}.__div__{self: int, n: int -> int}(id@1{SthStatus}, &id@9{int}, n{int}, id@8{int}) != STH_OK{SthRet}):
        goto id@4
    if (d{int}.__lt__{self: int, n: int -> bool}(id@1{SthStatus}, &id@10{bool}, d{int}, id@9{int}) != STH_OK{SthRet}):
        goto id@4
    if id@10{bool}.value{bool}:
        if (n{int}.__mod__{self: int, n: int -> int}(id@1{SthStatus}, &id@11{int}, n{int}, d{int}) != STH_OK{SthRet}):
            goto id@4
        if (sth_int_new{ -> int}(id@1{SthStatus}, &id@12{int}, 0{int}) != STH_OK{SthRet}):
            goto id@4
        if (id@11{int}.__eq__{self: int, n: int -> bool}(id@1{SthStatus}, &id@13{bool}, id@11{int}, id@12{int}) != STH_OK{SthRet}):
            goto id@4
        if id@13{bool}.value{bool}:
            *id@2{bool} = Sth_False{bool}
            goto id@4
        if (sth_int_new{ -> int}(id@1{SthStatus}, &id@14{int}, 1{int}) != STH_OK{SthRet}):
            goto id@4
        if (d{int}.__add__{self: int, n: int -> int}(id@1{SthStatus}, &d{int}, d{int}, id@14{int}) != STH_OK{SthRet}):
            goto id@4
        goto id@7
    *id@2{bool} = Sth_True{bool}
    goto id@4
    id@4: return id@1{SthStatus}.status

def print_primes_from{start: int, end: int -> }(id@15: SthStatus, *id@16: craw, start: int, end: int):
    id@17: if (start{int}.__le__{self: int, n: int -> bool}(id@15{SthStatus}, &id@18{bool}, start{int}, end{int}) != STH_OK{SthRet}):
        goto id@19
    if id@18{bool}.value{bool}:
        if (isprime{n: int -> bool}(id@15{SthStatus}, &id@20{bool}, start{int}) != STH_OK{SthRet}):
            goto id@19
        if id@20{bool}.value{bool}:
            
            if (sth_print{s: int -> }(id@15{SthStatus}, &id@21{craw}, start{int}) != STH_OK{SthRet}):
                goto id@19
        if (sth_int_new{ -> int}(id@15{SthStatus}, &id@22{int}, 1{int}) != STH_OK{SthRet}):
            goto id@19
        if (start{int}.__add__{self: int, n: int -> int}(id@15{SthStatus}, &start{int}, start{int}, id@22{int}) != STH_OK{SthRet}):
            goto id@19
        goto id@17
    id@19: return id@15{SthStatus}.status

def main{args: List[str] -> int}(id@23: SthStatus, *id@24: int, args: List[str]) -> int:
    if (sth_int_new{ -> int}(id@23{SthStatus}, &id@25{int}, 1{int}) != STH_OK{SthRet}):
        goto id@26
    if (sth_int_new{ -> int}(id@23{SthStatus}, &id@27{int}, 100{int}) != STH_OK{SthRet}):
        goto id@26
    
    if (print_primes_from{start: int, end: int -> }(id@23{SthStatus}, &id@28{craw}, id@25{int}, id@27{int}) != STH_OK{SthRet}):
        goto id@26
    if (sth_int_new{ -> int}(id@23{SthStatus}, &id@29{int}, 0{int}) != STH_OK{SthRet}):
        goto id@26
    *id@24{int} = id@29{int}
    goto id@26
    id@26: return id@23{SthStatus}.status
""", 0)
