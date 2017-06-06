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

def main{args: List[str] -> int}(<genid1>: SthStatus, *<genid2>: int, args: List[str]) -> int:
    if (sth_int_new{ -> int}(<genid1>{SthStatus}, &<genid3>{int}, 0{int}) != STH_OK{SthRet}):
        goto <genid4>
    *<genid2>{int} = <genid3>{int}
    goto <genid4>
    <genid4>: return <genid1>{SthStatus}.status
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

def add1{n: int -> int}(<genid1>: SthStatus, *<genid2>: int, n: int) -> int:
    if (sth_int_new{ -> int}(<genid1>{SthStatus}, &<genid3>{int}, 1{int}) != STH_OK{SthRet}):
        goto <genid4>
    if (n{int}.__add__{self: int, n: int -> int}(<genid1>{SthStatus}, &<genid5>{int}, n{int}, <genid3>{int}) != STH_OK{SthRet}):
        goto <genid4>
    *<genid2>{int} = <genid5>{int}
    goto <genid4>
    <genid4>: return <genid1>{SthStatus}.status

def main{args: List[str] -> int}(<genid6>: SthStatus, *<genid7>: int, args: List[str]) -> int:
    if (sth_int_new{ -> int}(<genid6>{SthStatus}, &<genid8>{int}, 9{int}) != STH_OK{SthRet}):
        goto <genid9>
    if (add1{n: int -> int}(<genid6>{SthStatus}, &x{int}, <genid8>{int}) != STH_OK{SthRet}):
        goto <genid9>
    *<genid7>{int} = x{int}
    goto <genid9>
    <genid9>: return <genid6>{SthStatus}.status
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

def isprime{n: int -> bool}(<genid1>: SthStatus, *<genid2>: bool, n: int) -> bool:
    if (sth_int_new{ -> int}(<genid1>{SthStatus}, &<genid3>{int}, 2{int}) != STH_OK{SthRet}):
        goto <genid4>
    d{int} = <genid3>{int}
    if (sth_int_new{ -> int}(<genid1>{SthStatus}, &<genid5>{int}, 4{int}) != STH_OK{SthRet}):
        goto <genid4>
    if (n{int}.__lt__{self: int, n: int -> bool}(<genid1>{SthStatus}, &<genid6>{bool}, n{int}, <genid5>{int}) != STH_OK{SthRet}):
        goto <genid4>
    if <genid6>{bool}.value{bool}:
        *<genid2>{bool} = Sth_True{bool}
        goto <genid4>
    <genid7>: if (sth_int_new{ -> int}(<genid1>{SthStatus}, &<genid8>{int}, 2{int}) != STH_OK{SthRet}):
        goto <genid4>
    if (n{int}.__div__{self: int, n: int -> int}(<genid1>{SthStatus}, &<genid9>{int}, n{int}, <genid8>{int}) != STH_OK{SthRet}):
        goto <genid4>
    if (d{int}.__lt__{self: int, n: int -> bool}(<genid1>{SthStatus}, &<genid10>{bool}, d{int}, <genid9>{int}) != STH_OK{SthRet}):
        goto <genid4>
    if <genid10>{bool}.value{bool}:
        if (n{int}.__mod__{self: int, n: int -> int}(<genid1>{SthStatus}, &<genid11>{int}, n{int}, d{int}) != STH_OK{SthRet}):
            goto <genid4>
        if (sth_int_new{ -> int}(<genid1>{SthStatus}, &<genid12>{int}, 0{int}) != STH_OK{SthRet}):
            goto <genid4>
        if (<genid11>{int}.__eq__{self: int, n: int -> bool}(<genid1>{SthStatus}, &<genid13>{bool}, <genid11>{int}, <genid12>{int}) != STH_OK{SthRet}):
            goto <genid4>
        if <genid13>{bool}.value{bool}:
            *<genid2>{bool} = Sth_False{bool}
            goto <genid4>
        if (sth_int_new{ -> int}(<genid1>{SthStatus}, &<genid14>{int}, 1{int}) != STH_OK{SthRet}):
            goto <genid4>
        if (d{int}.__add__{self: int, n: int -> int}(<genid1>{SthStatus}, &d{int}, d{int}, <genid14>{int}) != STH_OK{SthRet}):
            goto <genid4>
        goto <genid7>
    *<genid2>{bool} = Sth_True{bool}
    goto <genid4>
    <genid4>: return <genid1>{SthStatus}.status

def print_primes_from{start: int, end: int -> }(<genid15>: SthStatus, *<genid16>: craw, start: int, end: int):
    <genid17>: if (start{int}.__le__{self: int, n: int -> bool}(<genid15>{SthStatus}, &<genid18>{bool}, start{int}, end{int}) != STH_OK{SthRet}):
        goto <genid19>
    if <genid18>{bool}.value{bool}:
        if (isprime{n: int -> bool}(<genid15>{SthStatus}, &<genid20>{bool}, start{int}) != STH_OK{SthRet}):
            goto <genid19>
        if <genid20>{bool}.value{bool}:
            
            if (sth_print{s: int -> }(<genid15>{SthStatus}, &<genid21>{craw}, start{int}) != STH_OK{SthRet}):
                goto <genid19>
        if (sth_int_new{ -> int}(<genid15>{SthStatus}, &<genid22>{int}, 1{int}) != STH_OK{SthRet}):
            goto <genid19>
        if (start{int}.__add__{self: int, n: int -> int}(<genid15>{SthStatus}, &start{int}, start{int}, <genid22>{int}) != STH_OK{SthRet}):
            goto <genid19>
        goto <genid17>
    <genid19>: return <genid15>{SthStatus}.status

def main{args: List[str] -> int}(<genid23>: SthStatus, *<genid24>: int, args: List[str]) -> int:
    if (sth_int_new{ -> int}(<genid23>{SthStatus}, &<genid25>{int}, 1{int}) != STH_OK{SthRet}):
        goto <genid26>
    if (sth_int_new{ -> int}(<genid23>{SthStatus}, &<genid27>{int}, 100{int}) != STH_OK{SthRet}):
        goto <genid26>
    
    if (print_primes_from{start: int, end: int -> }(<genid23>{SthStatus}, &<genid28>{craw}, <genid25>{int}, <genid27>{int}) != STH_OK{SthRet}):
        goto <genid26>
    if (sth_int_new{ -> int}(<genid23>{SthStatus}, &<genid29>{int}, 0{int}) != STH_OK{SthRet}):
        goto <genid26>
    *<genid24>{int} = <genid29>{int}
    goto <genid26>
    <genid26>: return <genid23>{SthStatus}.status
""", 0)
