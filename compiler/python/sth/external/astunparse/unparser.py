"Usage: unparse.py <path to source file>"
from __future__ import print_function, unicode_literals
import sys
import ast
import os
import tokenize
from io import StringIO

# Large float and imaginary literals get turned into infinities in the AST.
# We unparse those infinities to INFSTR.
INFSTR = "1e" + repr(sys.float_info.max_10_exp + 1)

def interleave(inter, f, seq):
    """Call f on each item in seq, calling inter() in between.
    """
    seq = iter(seq)
    try:
        f(next(seq))
    except StopIteration:
        pass
    else:
        for x in seq:
            inter()
            f(x)


class GenerateId(dict):

    def __init__(self):
        self.counter = 1

    def __getitem__(self, key):
        if not key in self:
            name = '<genid%d>' % self.counter
            self[key] = name
            self.counter += 1
        return super(GenerateId, self).__getitem__(key)
            

class Unparser:
    """Methods in this class recursively traverse an AST and
    output source code for the abstract syntax; original formatting
    is disregarded. """

    def __init__(self, tree, file=sys.stdout):
        """Unparser(tree, file=sys.stdout) -> None.
         Print the source for tree to file."""
        self.generate_id = GenerateId()
        self.avoid_fill = 0
        self.f = file
        self.future_imports = []
        self._indent = 0
        self.dispatch(tree)
        print("", file=self.f)
        self.f.flush()

    def fill(self, text = ""):
        "Indent a piece of text, according to the current indentation level"
        if self.avoid_fill:
            self.write(text)
            self.avoid_fill -= 1
        else:
            self.f.write("\n"+"    "*self._indent + text)

    def write(self, text):
        "Append a piece of text to the current line."
        self.f.write(text)

    def enter(self):
        "Print ':', and increase the indentation."
        self.write(":")
        self._indent += 1

    def leave(self):
        "Decrease the indentation level."
        self._indent -= 1

    def dispatch(self, tree):
        "Dispatcher function, dispatching tree type T to method _T."
        if isinstance(tree, list):
            for t in tree:
                self.dispatch(t)
            return
        meth = getattr(self, "_"+tree.__class__.__name__)
        meth(tree)

        ignore_instances = ( 'FunctionDef', 'Assign', 'Call', 'Pointer',
                             'ClassDef')
        if hasattr(tree, 'tp'):
            if not tree.__class__.__name__ in ignore_instances:
                if hasattr(tree.tp, 'args'):
                    # duck typing: types.Function
                    self._FunctionType(tree.tp)
                else:
                    self.write('{%s}' % tree.tp)


    ############### Unparsing methods ######################
    # There should be one method per concrete grammar type #
    # Constructors should be grouped by sum type. Ideally, #
    # this would follow the order in the grammar, but      #
    # currently doesn't.                                   #
    ########################################################

    def _GotoLabel(self, tree):
        self.fill()
        self.dispatch(tree.name)
        self.write(': ')
        self.avoid_fill = 1

    def _Goto(self, tree):
        self.write("goto ")
        self.dispatch(tree.name)

    def _Module(self, tree):
        for stmt in tree.body:
            self.dispatch(stmt)

    def _Interactive(self, tree):
        for stmt in tree.body:
            self.dispatch(stmt)

    def _Expression(self, tree):
        self.dispatch(tree.body)

    # stmt
    def _Expr(self, tree):
        self.fill()
        self.dispatch(tree.value)

    def _Import(self, t):
        self.fill("import ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)

    def _ImportFrom(self, t):
        # A from __future__ import may affect unparsing, so record it.
        if t.module and t.module == '__future__':
            self.future_imports.extend(n.name for n in t.names)

        self.fill("from ")
        self.write("." * t.level)
        if t.module:
            self.write(t.module)
        self.write(" import ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)

    def _Assign(self, t):
        self.fill()
        for target in t.targets:
            self.dispatch(target)
            self.write(" = ")
        self.dispatch(t.value)

    def _AugAssign(self, t):
        self.fill()
        self.dispatch(t.target)
        self.write(" "+self.binop[t.op.__class__.__name__]+"= ")
        self.dispatch(t.value)

    def _AnnAssign(self, t):
        self.fill()
        if not t.simple:
            self.write("(")
        self.dispatch(t.target)
        if not t.simple:
            self.write(")")
        self.write(": ")
        self.dispatch(t.annotation)
        if t.value:
            self.write(" = ")
            self.dispatch(t.value)

    def _Return(self, t):
        self.fill("return")
        if t.value:
            self.write(" ")
            self.dispatch(t.value)

    def _Pass(self, t):
        self.fill("pass")

    def _Break(self, t):
        self.fill("break")

    def _Continue(self, t):
        self.fill("continue")

    def _Delete(self, t):
        self.fill("del ")
        interleave(lambda: self.write(", "), self.dispatch, t.targets)

    def _Assert(self, t):
        self.fill("assert ")
        self.dispatch(t.test)
        if t.msg:
            self.write(", ")
            self.dispatch(t.msg)

    def _Exec(self, t):
        self.fill("exec ")
        self.dispatch(t.body)
        if t.globals:
            self.write(" in ")
            self.dispatch(t.globals)
        if t.locals:
            self.write(", ")
            self.dispatch(t.locals)

    def _Print(self, t):
        self.fill("print ")
        do_comma = False
        if t.dest:
            self.write(">>")
            self.dispatch(t.dest)
            do_comma = True
        for e in t.values:
            if do_comma:self.write(", ")
            else:do_comma=True
            self.dispatch(e)
        if not t.nl:
            self.write(",")

    def _Global(self, t):
        self.fill("global ")
        interleave(lambda: self.write(", "), self.write, t.names)

    def _Nonlocal(self, t):
        self.fill("nonlocal ")
        interleave(lambda: self.write(", "), self.write, t.names)

    def _Yield(self, t):
        self.write("(")
        self.write("yield")
        if t.value:
            self.write(" ")
            self.dispatch(t.value)
        self.write(")")

    def _YieldFrom(self, t):
        self.write("(")
        self.write("yield from")
        if t.value:
            self.write(" ")
            self.dispatch(t.value)
        self.write(")")

    def _Raise(self, t):
        self.fill("raise")
        if not t.exc:
            assert not t.cause
            return
        self.write(" ")
        self.dispatch(t.exc)
        if t.cause:
            self.write(" from ")
            self.dispatch(t.cause)

    def _Try(self, t):
        self.fill("try")
        self.enter()
        self.dispatch(t.body)
        self.leave()
        for ex in t.handlers:
            self.dispatch(ex)
        if t.orelse:
            self.fill("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()
        if t.finalbody:
            self.fill("finally")
            self.enter()
            self.dispatch(t.finalbody)
            self.leave()

    def _TryExcept(self, t):
        self.fill("try")
        self.enter()
        self.dispatch(t.body)
        self.leave()

        for ex in t.handlers:
            self.dispatch(ex)
        if t.orelse:
            self.fill("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

    def _TryFinally(self, t):
        if len(t.body) == 1 and isinstance(t.body[0], ast.TryExcept):
            # try-except-finally
            self.dispatch(t.body)
        else:
            self.fill("try")
            self.enter()
            self.dispatch(t.body)
            self.leave()

        self.fill("finally")
        self.enter()
        self.dispatch(t.finalbody)
        self.leave()

    def _ExceptHandler(self, t):
        self.fill("except")
        if t.type:
            self.write(" ")
            self.dispatch(t.type)
        if t.name:
            self.write(" as ")
            self.write(t.name)
        self.enter()
        self.dispatch(t.body)
        self.leave()

    def _ClassDef(self, t):
        self.write("\n")
        for deco in t.decorator_list:
            self.fill("@")
            self.dispatch(deco)
        self.fill("class "+t.name)
        self.write("(")
        comma = False
        for e in t.bases:
            if comma: self.write(", ")
            else: comma = True
            self.dispatch(e)
        for e in t.keywords:
            if comma: self.write(", ")
            else: comma = True
            self.dispatch(e)
        if sys.version_info[:2] < (3, 5):
            if t.starargs:
                if comma: self.write(", ")
                else: comma = True
                self.write("*")
                self.dispatch(t.starargs)
            if t.kwargs:
                if comma: self.write(", ")
                else: comma = True
                self.write("**")
                self.dispatch(t.kwargs)
        self.write(")")
        self.enter()
        self.dispatch(t.body)
        self.leave()

    def _FunctionType(self, t):
        args = []
        for n, v in t.args.items():
            if isinstance(n, ast.Name):
                n = n.id or self.generate_id[id(n)]
            args.append('%s: %s' % (n, v))
        rets = t.returns or ''
        self.write('{%s -> %s}' % (', '.join(args), rets))

    def _generic_FunctionDef(self, t, async=False):
        self.write("\n")
        for deco in t.decorator_list:
            self.fill("@")
            self.dispatch(deco)
        self.fill(("async " if async else "") + "def " + t.name)
        if hasattr(t, 'tp'):
            self._FunctionType(t.tp)
        self.write("(")
        self.dispatch(t.args)
        self.write(")")
        if getattr(t, "returns", False):
            self.write(" -> ")
            self.dispatch(t.returns)
        self.enter()
        self.dispatch(t.body)
        self.leave()

    def _FunctionDef(self, t):
        self._generic_FunctionDef(t)

    def _AsyncFunctionDef(self, t):
        self._generic_FunctionDef(t, async=True)

    def _generic_For(self, t, async=False):
        self.fill("async for " if async else "for ")
        self.dispatch(t.target)
        self.write(" in ")
        self.dispatch(t.iter)
        self.enter()
        self.dispatch(t.body)
        self.leave()
        if t.orelse:
            self.fill("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

    def _For(self, t):
        self._generic_For(t)

    def _AsyncFor(self, t):
        self._generic_For(t, async=True)

    def _If(self, t):
        self.fill("if ")
        self.dispatch(t.test)
        self.enter()
        self.dispatch(t.body)
        self.leave()
        # collapse nested ifs into equivalent elifs.
        while (t.orelse and len(t.orelse) == 1 and
               isinstance(t.orelse[0], ast.If)):
            t = t.orelse[0]
            self.fill("elif ")
            self.dispatch(t.test)
            self.enter()
            self.dispatch(t.body)
            self.leave()
        # final else
        if t.orelse:
            self.fill("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

    def _While(self, t):
        self.fill("while ")
        self.dispatch(t.test)
        self.enter()
        self.dispatch(t.body)
        self.leave()
        if t.orelse:
            self.fill("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

    def _generic_With(self, t, async=False):
        self.fill("async with " if async else "with ")
        if hasattr(t, 'items'):
            interleave(lambda: self.write(", "), self.dispatch, t.items)
        else:
            self.dispatch(t.context_expr)
            if t.optional_vars:
                self.write(" as ")
                self.dispatch(t.optional_vars)
        self.enter()
        self.dispatch(t.body)
        self.leave()

    def _With(self, t):
        self._generic_With(t)

    def _AsyncWith(self, t):
        self._generic_With(t, async=True)

    # expr
    def _Bytes(self, t):
        self.write(repr(t.s))

    def _Str(self, tree):
        self.write(repr(tree.s))

    format_conversions = {97: 'a', 114: 'r', 115: 's'}

    def _FormattedValue(self, t):
        # FormattedValue(expr value, int? conversion, expr? format_spec)
        self.write("{")
        self.dispatch(t.value)
        if t.conversion is not None and t.conversion != -1:
            self.write("!")
            self.write(self.format_conversions[t.conversion])
            #raise NotImplementedError(ast.dump(t, True, True))
        if t.format_spec is not None:
            self.write(":")
            if isinstance(t.format_spec, ast.Str):
                self.write(t.format_spec.s)
            else:
                self.dispatch(t.format_spec)
        self.write("}")

    def _JoinedStr(self, t):
        # JoinedStr(expr* values)
        self.write("f'''")
        for value in t.values:
            if isinstance(value, ast.Str):
                self.write(value.s)
            else:
                self.dispatch(value)
        self.write("'''")

    def _Name(self, t):
        self.write(t.id or self.generate_id[id(t)])

    def _Dereference(self, t):
        self.write('&')
        self.dispatch(t.name)

    def _Pointer(self, t):
        self.write('*')
        self.dispatch(t.name)

    def _NameConstant(self, t):
        self.write(repr(t.value))

    def _Repr(self, t):
        self.write("`")
        self.dispatch(t.value)
        self.write("`")

    def _Num(self, t):
        repr_n = repr(t.n)
        self.write(repr_n.replace("inf", INFSTR))

    def _List(self, t):
        self.write("[")
        interleave(lambda: self.write(", "), self.dispatch, t.elts)
        self.write("]")

    def _ListComp(self, t):
        self.write("[")
        self.dispatch(t.elt)
        for gen in t.generators:
            self.dispatch(gen)
        self.write("]")

    def _GeneratorExp(self, t):
        self.write("(")
        self.dispatch(t.elt)
        for gen in t.generators:
            self.dispatch(gen)
        self.write(")")

    def _SetComp(self, t):
        self.write("{")
        self.dispatch(t.elt)
        for gen in t.generators:
            self.dispatch(gen)
        self.write("}")

    def _DictComp(self, t):
        self.write("{")
        self.dispatch(t.key)
        self.write(": ")
        self.dispatch(t.value)
        for gen in t.generators:
            self.dispatch(gen)
        self.write("}")

    def _comprehension(self, t):
        if getattr(t, 'is_async', False):
            self.write(" async")
        self.write(" for ")
        self.dispatch(t.target)
        self.write(" in ")
        self.dispatch(t.iter)
        for if_clause in t.ifs:
            self.write(" if ")
            self.dispatch(if_clause)

    def _IfExp(self, t):
        self.write("(")
        self.dispatch(t.body)
        self.write(" if ")
        self.dispatch(t.test)
        self.write(" else ")
        self.dispatch(t.orelse)
        self.write(")")

    def _Set(self, t):
        assert(t.elts) # should be at least one element
        self.write("{")
        interleave(lambda: self.write(", "), self.dispatch, t.elts)
        self.write("}")

    def _Dict(self, t):
        self.write("{")
        def write_pair(pair):
            (k, v) = pair
            self.dispatch(k)
            self.write(": ")
            self.dispatch(v)
        interleave(lambda: self.write(", "), write_pair, zip(t.keys, t.values))
        self.write("}")

    def _Tuple(self, t):
        self.write("(")
        if len(t.elts) == 1:
            (elt,) = t.elts
            self.dispatch(elt)
            self.write(",")
        else:
            interleave(lambda: self.write(", "), self.dispatch, t.elts)
        self.write(")")

    unop = {"Invert":"~", "Not": "not", "UAdd":"+", "USub":"-"}
    def _UnaryOp(self, t):
        self.write("(")
        self.write(self.unop[t.op.__class__.__name__])
        self.write(" ")
        self.dispatch(t.operand)
        self.write(")")

    binop = { "Add":"+", "Sub":"-", "Mult":"*", "Div":"/", "Mod":"%",
                    "LShift":"<<", "RShift":">>", "BitOr":"|", "BitXor":"^", "BitAnd":"&",
                    "FloorDiv":"//", "Pow": "**",
                    "MatMult":"@"}
    def _BinOp(self, t):
        self.write("(")
        self.dispatch(t.left)
        self.write(" " + self.binop[t.op.__class__.__name__] + " ")
        self.dispatch(t.right)
        self.write(")")

    cmpops = {"Eq":"==", "NotEq":"!=", "Lt":"<", "LtE":"<=", "Gt":">", "GtE":">=",
                        "Is":"is", "IsNot":"is not", "In":"in", "NotIn":"not in"}
    def _Compare(self, t):
        self.write("(")
        self.dispatch(t.left)
        for o, e in zip(t.ops, t.comparators):
            self.write(" " + self.cmpops[o.__class__.__name__] + " ")
            self.dispatch(e)
        self.write(")")

    boolops = {ast.And: 'and', ast.Or: 'or'}
    def _BoolOp(self, t):
        self.write("(")
        s = " %s " % self.boolops[t.op.__class__]
        interleave(lambda: self.write(s), self.dispatch, t.values)
        self.write(")")

    def _Attribute(self,t):
        self.dispatch(t.value)
        # Special case: 3.__abs__() is a syntax error, so if t.value
        # is an integer literal then we need to either parenthesize
        # it or add an extra space to get 3 .__abs__().
        if isinstance(t.value, ast.Num) and isinstance(t.value.n, int):
            self.write(" ")
        self.write(".")
        self.write(t.attr)

    def _Call(self, t):
        self.dispatch(t.func)
        self.write("(")
        comma = False
        for e in t.args:
            if comma: self.write(", ")
            else: comma = True
            self.dispatch(e)
        for e in t.keywords:
            if comma: self.write(", ")
            else: comma = True
            self.dispatch(e)
        if sys.version_info[:2] < (3, 5):
            if t.starargs:
                if comma: self.write(", ")
                else: comma = True
                self.write("*")
                self.dispatch(t.starargs)
            if t.kwargs:
                if comma: self.write(", ")
                else: comma = True
                self.write("**")
                self.dispatch(t.kwargs)
        self.write(")")

    def _Subscript(self, t):
        self.dispatch(t.value)
        self.write("[")
        self.dispatch(t.slice)
        self.write("]")

    def _Starred(self, t):
        self.write("*")
        self.dispatch(t.value)

    # slice
    def _Ellipsis(self, t):
        self.write("...")

    def _Index(self, t):
        self.dispatch(t.value)

    def _Slice(self, t):
        if t.lower:
            self.dispatch(t.lower)
        self.write(":")
        if t.upper:
            self.dispatch(t.upper)
        if t.step:
            self.write(":")
            self.dispatch(t.step)

    def _ExtSlice(self, t):
        interleave(lambda: self.write(', '), self.dispatch, t.dims)

    # argument
    def _arg(self, t):
        if isinstance(t.arg, ast.Name):
            self._Name(t.arg)
        elif t.arg.__class__.__name__ == 'Pointer':
            self.write('*')
            self._Name(t.arg.name)
        else:
            self.write(t.arg)
        if t.annotation:
            self.write(": ")
            self.dispatch(t.annotation)

    # others
    def _arguments(self, t):
        first = True
        # normal arguments
        defaults = [None] * (len(t.args) - len(t.defaults)) + t.defaults
        for a,d in zip(t.args, defaults):
            if first:first = False
            else: self.write(", ")
            self.dispatch(a)
            if d:
                self.write("=")
                self.dispatch(d)

        # varargs, or bare '*' if no varargs but keyword-only arguments present
        if t.vararg or getattr(t, "kwonlyargs", False):
            if first: first = False
            else: self.write(", ")
            self.write("*")
            if t.vararg:
                if hasattr(t.vararg, 'arg'):
                    self.write(t.vararg.arg)
                    if t.vararg.annotation:
                        self.write(": ")
                        self.dispatch(t.vararg.annotation)
                else:
                    self.write(t.vararg)
                    if getattr(t, 'varargannotation', None):
                        self.write(": ")
                        self.dispatch(t.varargannotation)

        # keyword-only arguments
        if getattr(t, "kwonlyargs", False):
            for a, d in zip(t.kwonlyargs, t.kw_defaults):
                if first:first = False
                else: self.write(", ")
                self.dispatch(a),
                if d:
                    self.write("=")
                    self.dispatch(d)

        # kwargs
        if t.kwarg:
            if first:first = False
            else: self.write(", ")
            if hasattr(t.kwarg, 'arg'):
                self.write("**"+t.kwarg.arg)
                if t.kwarg.annotation:
                    self.write(": ")
                    self.dispatch(t.kwarg.annotation)
            else:
                self.write("**"+t.kwarg)
                if getattr(t, 'kwargannotation', None):
                    self.write(": ")
                    self.dispatch(t.kwargannotation)

    def _keyword(self, t):
        if t.arg is None:
            # starting from Python 3.5 this denotes a kwargs part of the invocation
            self.write("**")
        else:
            self.write(t.arg)
            self.write("=")
        self.dispatch(t.value)

    def _Lambda(self, t):
        self.write("(")
        self.write("lambda ")
        self.dispatch(t.args)
        self.write(": ")
        self.dispatch(t.body)
        self.write(")")

    def _alias(self, t):
        self.write(t.name)
        if t.asname:
            self.write(" as "+t.asname)

    def _withitem(self, t):
        self.dispatch(t.context_expr)
        if t.optional_vars:
            self.write(" as ")
            self.dispatch(t.optional_vars)

    def _Await(self, t):
        self.write("(")
        self.write("await")
        if t.value:
            self.write(" ")
            self.dispatch(t.value)
        self.write(")")

def roundtrip(filename, output=sys.stdout):
    with open(filename, "rb") as pyfile:
        encoding = tokenize.detect_encoding(pyfile.readline)[0]
    with open(filename, "r", encoding=encoding) as pyfile:
        source = pyfile.read()
    tree = compile(source, filename, "exec", ast.PyCF_ONLY_AST, dont_inherit=True)
    Unparser(tree, output)



def testdir(a):
    try:
        names = [n for n in os.listdir(a) if n.endswith('.py')]
    except OSError:
        print("Directory not readable: %s" % a, file=sys.stderr)
    else:
        for n in names:
            fullname = os.path.join(a, n)
            if os.path.isfile(fullname):
                output = StringIO()
                print('Testing %s' % fullname)
                try:
                    roundtrip(fullname, output)
                except Exception as e:
                    print('  Failed to compile, exception is %s' % repr(e))
            elif os.path.isdir(fullname):
                testdir(fullname)

def main(args):
    if args[0] == '--testdir':
        for a in args[1:]:
            testdir(a)
    else:
        for a in args:
            roundtrip(a)

if __name__=='__main__':
    main(sys.argv[1:])
