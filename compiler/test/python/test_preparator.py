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

def main{args: List[str] -> int}(<genid1>: SthStatus) -> int:
    args{List[str]} = sth_status_frame_argval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_add(<genid1>{SthStatus}, 0, 1) != STH_OK{SthRet}):
        goto <genid2>
    if (sth_int_new{ -> int}(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid3>{int} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid3>{int}.value{int} = 0{int}
    sth_status_frame_retval_set(<genid1>{SthStatus}, 0, <genid3>{int})
    goto <genid2>
    <genid2>: return sth_status_status_get(<genid1>{SthStatus})
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

def add1{n: int -> int}(<genid1>: SthStatus) -> int:
    n{int} = sth_status_frame_argval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_add(<genid1>{SthStatus}, 0, 1) != STH_OK{SthRet}):
        goto <genid2>
    if (sth_int_new{ -> int}(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid3>{int} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid3>{int}.value{int} = 1{int}
    if (sth_status_frame_add(<genid1>{SthStatus}, 2, 1) != STH_OK{SthRet}):
        goto <genid2>
    sth_status_frame_argval_set(<genid1>{SthStatus}, 0, n{int})
    sth_status_frame_argval_set(<genid1>{SthStatus}, 1, <genid3>{int})
    if (n{int}.__add__{self: int, n: int -> int}(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid4>{int} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    sth_status_frame_retval_set(<genid1>{SthStatus}, 0, <genid4>{int})
    goto <genid2>
    <genid2>: return sth_status_status_get(<genid1>{SthStatus})

def main{args: List[str] -> int}(<genid5>: SthStatus) -> int:
    args{List[str]} = sth_status_frame_argval_get(<genid5>{SthStatus}, 0)
    if (sth_status_frame_add(<genid5>{SthStatus}, 0, 1) != STH_OK{SthRet}):
        goto <genid6>
    if (sth_int_new{ -> int}(<genid5>{SthStatus}) != STH_OK{SthRet}):
        goto <genid6>
    <genid7>{int} = sth_status_frame_retval_get(<genid5>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid5>{SthStatus}) != STH_OK{SthRet}):
        goto <genid6>
    <genid7>{int}.value{int} = 9{int}
    if (sth_status_frame_add(<genid5>{SthStatus}, 1, 1) != STH_OK{SthRet}):
        goto <genid6>
    sth_status_frame_argval_set(<genid5>{SthStatus}, 0, <genid7>{int})
    if (add1{n: int -> int}(<genid5>{SthStatus}) != STH_OK{SthRet}):
        goto <genid6>
    x{int} = sth_status_frame_retval_get(<genid5>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid5>{SthStatus}) != STH_OK{SthRet}):
        goto <genid6>
    sth_status_frame_retval_set(<genid5>{SthStatus}, 0, x{int})
    goto <genid6>
    <genid6>: return sth_status_status_get(<genid5>{SthStatus})
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

def isprime{n: int -> bool}(<genid1>: SthStatus) -> bool:
    n{int} = sth_status_frame_argval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_add(<genid1>{SthStatus}, 0, 1) != STH_OK{SthRet}):
        goto <genid2>
    if (sth_int_new{ -> int}(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid3>{int} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid3>{int}.value{int} = 2{int}
    d{int} = <genid3>{int}
    if (sth_status_frame_add(<genid1>{SthStatus}, 0, 1) != STH_OK{SthRet}):
        goto <genid2>
    if (sth_int_new{ -> int}(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid4>{int} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid4>{int}.value{int} = 4{int}
    if (sth_status_frame_add(<genid1>{SthStatus}, 2, 1) != STH_OK{SthRet}):
        goto <genid2>
    sth_status_frame_argval_set(<genid1>{SthStatus}, 0, n{int})
    sth_status_frame_argval_set(<genid1>{SthStatus}, 1, <genid4>{int})
    if (n{int}.__lt__{self: int, n: int -> bool}(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid5>{bool} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    if <genid5>{bool}:
        if (sth_status_frame_add(<genid1>{SthStatus}, 0, 1) != STH_OK{SthRet}):
            goto <genid2>
        if (sth_bool_new{ -> bool}(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        <genid6>{bool} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
        if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        <genid6>{bool}.value{bool} = 1
        sth_status_frame_retval_set(<genid1>{SthStatus}, 0, <genid6>{bool})
        goto <genid2>
    <genid7>: if (sth_status_frame_add(<genid1>{SthStatus}, 0, 1) != STH_OK{SthRet}):
        goto <genid2>
    if (sth_int_new{ -> int}(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid8>{int} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid8>{int}.value{int} = 2{int}
    if (sth_status_frame_add(<genid1>{SthStatus}, 2, 1) != STH_OK{SthRet}):
        goto <genid2>
    sth_status_frame_argval_set(<genid1>{SthStatus}, 0, n{int})
    sth_status_frame_argval_set(<genid1>{SthStatus}, 1, <genid8>{int})
    if (n{int}.__div__{self: int, n: int -> int}(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid9>{int} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    if (sth_status_frame_add(<genid1>{SthStatus}, 2, 1) != STH_OK{SthRet}):
        goto <genid2>
    sth_status_frame_argval_set(<genid1>{SthStatus}, 0, d{int})
    sth_status_frame_argval_set(<genid1>{SthStatus}, 1, <genid9>{int})
    if (d{int}.__lt__{self: int, n: int -> bool}(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid10>{bool} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    if <genid10>{bool}:
        if (sth_status_frame_add(<genid1>{SthStatus}, 2, 1) != STH_OK{SthRet}):
            goto <genid2>
        sth_status_frame_argval_set(<genid1>{SthStatus}, 0, n{int})
        sth_status_frame_argval_set(<genid1>{SthStatus}, 1, d{int})
        if (n{int}.__mod__{self: int, n: int -> int}(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        <genid11>{int} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
        if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        if (sth_status_frame_add(<genid1>{SthStatus}, 0, 1) != STH_OK{SthRet}):
            goto <genid2>
        if (sth_int_new{ -> int}(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        <genid12>{int} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
        if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        <genid12>{int}.value{int} = 0{int}
        if (sth_status_frame_add(<genid1>{SthStatus}, 2, 1) != STH_OK{SthRet}):
            goto <genid2>
        sth_status_frame_argval_set(<genid1>{SthStatus}, 0, <genid11>{int})
        sth_status_frame_argval_set(<genid1>{SthStatus}, 1, <genid12>{int})
        if (<genid11>{int}.__eq__{self: int, n: int -> bool}(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        <genid13>{bool} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
        if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        if <genid13>{bool}:
            if (sth_status_frame_add(<genid1>{SthStatus}, 0, 1) != STH_OK{SthRet}):
                goto <genid2>
            if (sth_bool_new{ -> bool}(<genid1>{SthStatus}) != STH_OK{SthRet}):
                goto <genid2>
            <genid14>{bool} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
            if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
                goto <genid2>
            <genid14>{bool}.value{bool} = 0
            sth_status_frame_retval_set(<genid1>{SthStatus}, 0, <genid14>{bool})
            goto <genid2>
        if (sth_status_frame_add(<genid1>{SthStatus}, 0, 1) != STH_OK{SthRet}):
            goto <genid2>
        if (sth_int_new{ -> int}(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        <genid15>{int} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
        if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        <genid15>{int}.value{int} = 1{int}
        if (sth_status_frame_add(<genid1>{SthStatus}, 2, 1) != STH_OK{SthRet}):
            goto <genid2>
        sth_status_frame_argval_set(<genid1>{SthStatus}, 0, d{int})
        sth_status_frame_argval_set(<genid1>{SthStatus}, 1, <genid15>{int})
        if (d{int}.__add__{self: int, n: int -> int}(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        d{int} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
        if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
            goto <genid2>
        goto <genid7>
    if (sth_status_frame_add(<genid1>{SthStatus}, 0, 1) != STH_OK{SthRet}):
        goto <genid2>
    if (sth_bool_new{ -> bool}(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid16>{bool} = sth_status_frame_retval_get(<genid1>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid1>{SthStatus}) != STH_OK{SthRet}):
        goto <genid2>
    <genid16>{bool}.value{bool} = 1
    sth_status_frame_retval_set(<genid1>{SthStatus}, 0, <genid16>{bool})
    goto <genid2>
    <genid2>: return sth_status_status_get(<genid1>{SthStatus})

def print_primes_from{start: int, end: int -> }(<genid17>: SthStatus):
    start{int} = sth_status_frame_argval_get(<genid17>{SthStatus}, 0)
    end{int} = sth_status_frame_argval_get(<genid17>{SthStatus}, 1)
    <genid18>: if (sth_status_frame_add(<genid17>{SthStatus}, 2, 1) != STH_OK{SthRet}):
        goto <genid19>
    sth_status_frame_argval_set(<genid17>{SthStatus}, 0, start{int})
    sth_status_frame_argval_set(<genid17>{SthStatus}, 1, end{int})
    if (start{int}.__le__{self: int, n: int -> bool}(<genid17>{SthStatus}) != STH_OK{SthRet}):
        goto <genid19>
    <genid20>{bool} = sth_status_frame_retval_get(<genid17>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid17>{SthStatus}) != STH_OK{SthRet}):
        goto <genid19>
    if <genid20>{bool}:
        if (sth_status_frame_add(<genid17>{SthStatus}, 1, 1) != STH_OK{SthRet}):
            goto <genid19>
        sth_status_frame_argval_set(<genid17>{SthStatus}, 0, start{int})
        if (isprime{n: int -> bool}(<genid17>{SthStatus}) != STH_OK{SthRet}):
            goto <genid19>
        <genid21>{bool} = sth_status_frame_retval_get(<genid17>{SthStatus}, 0)
        if (sth_status_frame_remove(<genid17>{SthStatus}) != STH_OK{SthRet}):
            goto <genid19>
        if <genid21>{bool}:
            
            if (sth_status_frame_add(<genid17>{SthStatus}, 1, 0) != STH_OK{SthRet}):
                goto <genid19>
            sth_status_frame_argval_set(<genid17>{SthStatus}, 0, start{int})
            if (print{s: int -> }(<genid17>{SthStatus}) != STH_OK{SthRet}):
                goto <genid19>
            if (sth_status_frame_remove(<genid17>{SthStatus}) != STH_OK{SthRet}):
                goto <genid19>
        if (sth_status_frame_add(<genid17>{SthStatus}, 0, 1) != STH_OK{SthRet}):
            goto <genid19>
        if (sth_int_new{ -> int}(<genid17>{SthStatus}) != STH_OK{SthRet}):
            goto <genid19>
        <genid22>{int} = sth_status_frame_retval_get(<genid17>{SthStatus}, 0)
        if (sth_status_frame_remove(<genid17>{SthStatus}) != STH_OK{SthRet}):
            goto <genid19>
        <genid22>{int}.value{int} = 1{int}
        if (sth_status_frame_add(<genid17>{SthStatus}, 2, 1) != STH_OK{SthRet}):
            goto <genid19>
        sth_status_frame_argval_set(<genid17>{SthStatus}, 0, start{int})
        sth_status_frame_argval_set(<genid17>{SthStatus}, 1, <genid22>{int})
        if (start{int}.__add__{self: int, n: int -> int}(<genid17>{SthStatus}) != STH_OK{SthRet}):
            goto <genid19>
        start{int} = sth_status_frame_retval_get(<genid17>{SthStatus}, 0)
        if (sth_status_frame_remove(<genid17>{SthStatus}) != STH_OK{SthRet}):
            goto <genid19>
        goto <genid18>
    <genid19>: return sth_status_status_get(<genid17>{SthStatus})

def main{args: List[str] -> int}(<genid23>: SthStatus) -> int:
    args{List[str]} = sth_status_frame_argval_get(<genid23>{SthStatus}, 0)
    if (sth_status_frame_add(<genid23>{SthStatus}, 0, 1) != STH_OK{SthRet}):
        goto <genid24>
    if (sth_int_new{ -> int}(<genid23>{SthStatus}) != STH_OK{SthRet}):
        goto <genid24>
    <genid25>{int} = sth_status_frame_retval_get(<genid23>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid23>{SthStatus}) != STH_OK{SthRet}):
        goto <genid24>
    <genid25>{int}.value{int} = 1{int}
    if (sth_status_frame_add(<genid23>{SthStatus}, 0, 1) != STH_OK{SthRet}):
        goto <genid24>
    if (sth_int_new{ -> int}(<genid23>{SthStatus}) != STH_OK{SthRet}):
        goto <genid24>
    <genid26>{int} = sth_status_frame_retval_get(<genid23>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid23>{SthStatus}) != STH_OK{SthRet}):
        goto <genid24>
    <genid26>{int}.value{int} = 100{int}
    
    if (sth_status_frame_add(<genid23>{SthStatus}, 2, 0) != STH_OK{SthRet}):
        goto <genid24>
    sth_status_frame_argval_set(<genid23>{SthStatus}, 0, <genid25>{int})
    sth_status_frame_argval_set(<genid23>{SthStatus}, 1, <genid26>{int})
    if (print_primes_from{start: int, end: int -> }(<genid23>{SthStatus}) != STH_OK{SthRet}):
        goto <genid24>
    if (sth_status_frame_remove(<genid23>{SthStatus}) != STH_OK{SthRet}):
        goto <genid24>
    if (sth_status_frame_add(<genid23>{SthStatus}, 0, 1) != STH_OK{SthRet}):
        goto <genid24>
    if (sth_int_new{ -> int}(<genid23>{SthStatus}) != STH_OK{SthRet}):
        goto <genid24>
    <genid27>{int} = sth_status_frame_retval_get(<genid23>{SthStatus}, 0)
    if (sth_status_frame_remove(<genid23>{SthStatus}) != STH_OK{SthRet}):
        goto <genid24>
    <genid27>{int}.value{int} = 0{int}
    sth_status_frame_retval_set(<genid23>{SthStatus}, 0, <genid27>{int})
    goto <genid24>
    <genid24>: return sth_status_status_get(<genid23>{SthStatus})
""", 0)
