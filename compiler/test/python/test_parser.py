from sth.parser import parse_string


def _assert_sthcode(sthcode, output):
    modulecode = '\n'.join(sthcode) + '\n'
    assert output == modulecode


def assert_parser(input, output, ret):
    module = parse_string(input)
    _assert_sthcode(module.sthcode(), output or input)


def assert_parser_simplify(input, output, ret):
    module = parse_string(input)
    simplified = module.simplified()
    assert len(simplified) == 1
    _assert_sthcode(module.simplified()[0].sthcode(), output or input)


def test_mainfunc():
    assert_parser(
"""def main(args: List[str]) -> cint:
    return 0
""", None, 0)


def test_assignment():
    assert_parser(
"""def main(args: List[str]) -> cint:
    x = 1
    y = 3.14e-4
    z = False
    _ = True
    return 0
""", None, 0)


def test_mathops():
    assert_parser(
"""def main(args: List[str]) -> cint:
    x = ((1 + 2) - 3)
    y = ((3 * (4 - 2)) / 9)
    z = (34 % 9)
    x += 3
    x -= 3
    x *= 3
    x /= 3
    return 0
""", None, 0)


def test_boolops():
    assert_parser(
"""def main(args: List[str]) -> cint:
    x = (3 > 4)
    y = (3 < 4)
    z = (3 <= 4)
    a = ((3 + 3) >= (4 * 9))
    b = (3 == 3)
    b = (3 != 3)
    return 0
""", None, 0)


def test_emptylines():
    assert_parser(
"""

def main(args: List[str]) -> cint:



    x = 4

    return 0
""", 
"""def main(args: List[str]) -> cint:
    x = 4
    return 0
""", 0)


def test_comments():
    assert_parser(
"""
# Comment 1
def main(args: List[str]) -> cint:

     # Comment 2
# Comment 3
    x = 4

    return 0        # Comment 4


# Comment 5
""", 
"""def main(args: List[str]) -> cint:
    x = 4
    return 0
""", 0)


def test_simple_stmt_list():
    assert_parser(
"""def main(args: List[str]) -> cint: x = 4 ; y = 5 ; z = 6 ; return 0
""", 
"""def main(args: List[str]) -> cint:
    x = 4
    y = 5
    z = 6
    return 0
""", 0)


def test_simple_stmt_list_internal():
    assert_parser(
"""def main(args: List[str]) -> cint:
    x = 4 ; y = 5 ; z = 6
    return 0
""", 
"""def main(args: List[str]) -> cint:
    x = 4
    y = 5
    z = 6
    return 0
""", 0)


def test_newlines_in_stmts():
    assert_parser(
"""def main(args: List[str]) -> cint:
    add(3,
4)
    add(3
,4)
    add(
3
,

4
)
    return 0
""",
"""def main(args: List[str]) -> cint:
    add(3, 4)
    add(3, 4)
    add(3, 4)
    return 0
""", 0)


def test_if():
    assert_parser(
"""def main(args: List[str]) -> cint:
    x = 3
    if (x > 3):
        print(4)
    else:
        print(3)
    return 0
""", None, 0)


def test_if_nested():
    assert_parser(
"""def main(args: List[str]) -> cint:
    x = 3
    if (x > 3):
        if (x > 4):
            print(5)
        else:
            print(4)
    elif (x > 2):
        print(3)
    else:
        print(2)
    return 0
""", None, 0)


def test_while():
    assert_parser(
"""def main(args: List[str]) -> cint:
    x = 0
    while (x < 3):
        print(x)
        x += 1
    return 0
""", None, 0)


def test_while_break_continue():
    assert_parser(
"""def main(args: List[str]) -> cint:
    x = 0
    while True:
        print(x)
        if (x > 3):
            break
        else:
            continue
    else:
        print(x)
    return 0
""", None, 0)


def test_funcdef():
    assert_parser(
"""def fib(x: cint) -> cint:
    if (x < 2):
        return x
    else:
        return (fib((x - 1)) + fib((x - 2)))


def main(args: List[str]) -> cint:
    print(fib(9))
    return 0
""", None, 0)


def test_simplify_assignment():
    assert_parser_simplify(
"""def main(args: List[str]) -> cint:
    a, b, c = d, e, f = g, h, i = 1, 2, 3
    return 0
""",
"""def main(args: List[str]) -> cint:
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


def test_simplify_mathop():
    assert_parser_simplify(
"""def main(args: List[str]) -> cint:
    a = 1 + 4
    b = 4 - 3
    c = b * 9
    d = a / 5
    d = a % 3
    return 0
""",
"""def main(args: List[str]) -> cint:
    a = (1).__add__(4)
    b = (4).__sub__(3)
    c = b.__mul__(9)
    d = a.__div__(5)
    d = a.__mod__(3)
    return 0
""", 0)


def test_simplify_aug_assignment():
    assert_parser_simplify(
"""def main(args: List[str]) -> cint:
    a = 1
    a += 1
    a -= 1
    a *= 1
    a /= 1
    a %= 1
    return 0
""",
"""def main(args: List[str]) -> cint:
    a = 1
    a = a.__add__(1)
    a = a.__sub__(1)
    a = a.__mul__(1)
    a = a.__div__(1)
    a = a.__mod__(1)
    return 0
""", 0)


def test_simplify_boolops():
    assert_parser_simplify(
"""def main(args: List[str]) -> cint:
    a = 3 < 4
    a = 3 > 4
    a = 3 == 4
    a = 3 != 4
    a = 3 <= 4
    a = 3 >= 4
    return 0
""",
"""def main(args: List[str]) -> cint:
    a = (3).__lt__(4)
    a = (3).__gt__(4)
    a = (3).__eq__(4)
    a = (3).__ne__(4)
    a = (3).__le__(4)
    a = (3).__ge__(4)
    return 0
""", 0)


def test_simplify_boolops_if():
    assert_parser_simplify(
"""def main(args: List[str]) -> cint:
    x = 0
    if 3 < 4:
        x = 1
    elif 3:
        x = 2
    elif False:
        x = 3
    return 0
""",
"""def main(args: List[str]) -> cint:
    x = 0
    if (3).__lt__(4):
        x = 1
    elif 3:
        x = 2
    elif False:
        x = 3
    return 0
""", 0)


def test_simplify_boolops_while():
    assert_parser_simplify(
"""def main(args: List[str]) -> cint:
    x = 1
    while x < 15:
        x += 1
    return 0
""",
"""def main(args: List[str]) -> cint:
    x = 1
    while x.__lt__(15):
        x = x.__add__(1)
    return 0
""", 0)
