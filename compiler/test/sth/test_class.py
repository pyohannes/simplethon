import pytest
from helper import assert_compiled_output_python_compat


def test_simple():
    assert_compiled_output_python_compat(
"""
class Point():
    def __init__(self: 'C', x, y):
        self.x = x
        self.y = y

def main(args: List[str]) -> int :
    c = C(0, 0)
    print(c.x)
    print(c.y)
    c.x = 3
    c.y = 5
    print(c.x)
    print(c.y)
    return 0
""", valgrind=False)


def test_counter():
    assert_compiled_output_python_compat(
"""
class Counter():

    def __init__(self: 'Counter', start: int):
        self._start = start

    def count(self: 'Counter'):
        self._start += 1
        print(self._start)


def main(args: List[str]) -> int:
    c = Counter(3)
    c.count()
    c.count()
    c.count()
    c.count()
    c.count()
    c.count()
    c.count()
    c.count()
    return 0
""", valgrind=False)


def test_inheritance():
    assert_compiled_output_python_compat(
"""
class A():
    def __init__(self: 'Point', a: int):
        self.a = a


class B(A):
    def __init__(self: 'Point', a: int, b: int):
        super(B, self).__init__(a)
        self.b = b


class C(B):
    def __init__(self: 'Point', a: int, b: int, c: int):
        super(C, self).__init__(a, b)
        self.c = c


class D(C):
    def __init__(self: 'Point', a: int, b: int, c: int, d: int):
        super(D, self).__init__(a, b, c)
        self.d = d


def main(args: List[str]) -> int:
    d = D(1, 2, 3, 4)
    print(d.a)
    print(d.b)
    print(d.c)
    print(d.d)
    return 0
""", valgrind=False)


def test_multiple_inheritance():
    assert_compiled_output_python_compat(
"""
class X():
    def __init__(self: 'X', x: int):
        self.x = x

    def print_x(self: 'X'):
        print(self.x)


class Y():
    def __init__(self: 'Y', y: int):
        self.y = y

    def print_y(self: 'Y'):
        print(self.y)


class XY(X, Y):
    def __init__(self: 'XY', x: int, y: int):
        X.__init__(self, x)
        Y.__init__(self, y)

    def print_xy(self: 'Point'):
        self.print_x()
        self.print_y()


def main(args: List[str]) -> int:
    x = X(1)
    y = Y(2)
    xy = XY(3, 4)
    x.print_x()
    y.print_y()
    xy.print_xy()
    return 0
""", valgrind=False)


def test_polymorphism():
    assert_compiled_output_python_compat(
"""
class Point():
    def __init__(self: 'Point', x: int, y: int):
        self.x = x
        self.y = y

    def print(self: 'Point'):
        print(self.x)
        print(self.y)


class Point3D(Point):
    def __init__(self: 'Point3D', x: int, y: int, z: int):
        super(Point3D, self).__init__(x, y)
        self.z = z

    def print(self: 'Point'):
        super(Point3D, self).print()
        print(self.z)


class Line():
    def __init__(self: 'Square', start: Point, end: Point):
        self.start = start
        self.end = end

    def print(self: 'Square'):
        self.start.print()
        self.end.print()


def main(args: List[str]) -> int:
    p1 = Point(3, 4)
    p2 = Point3D(5, 6, 7)
    l = Line(p1, p2)
    l.print()
    return 0
""", valgrind=False)
