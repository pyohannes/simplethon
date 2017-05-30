####+

from sth import ast
from sth.external.pycparser import c_ast, c_generator


class Translator(ast.RecursiveNodeVisitor):

    class NameExtractor(ast.RecursiveNodeVisitor):
    
        def __init__(self):
            super(Translator.NameExtractor, self).__init__(None)
            self.names = set()
    
        def visit_name(self, node):
            if node.id:
                self.names.add(node.id)
    
    def __init__(self):
        super(Translator, self).__init__(None)

    def _initialize(self, module):
        self._var_id_count = 0
        self._compound_scopes = dict()
        name_ex = Translator.NameExtractor()
        name_ex.visit(module)
        self._reserved_names = name_ex.names

    def translate(self, module):
        self._initialize(module)
        return c_ast.FileAST([ self.visit(n) for n in module.body ])

    def c_make_unique_var_name(self, name):
        if not name.id:
            self._var_id_count += 1
            genid = '_%d' % self._var_id_count
            if genid in self._reserved_names:
                return self.c_make_unique_var_name(name)
            else:
                name.id = genid

        return name.id 

    def c_make_compound(self, nodes):
        if not isinstance(nodes, list):
            nodes = [ nodes ]
        return c_ast.Compound(block_items=[ self.visit(n) for n in nodes ])

    def c_make_type_id(self, name, declname=None):
        if name.strip().endswith('*'):
            name = name.strip('*')
            return self.c_make_ptr_decl(declname, name)
        else:
            return c_ast.IdentifierType(names=[ name ])

    def c_make_type_decl(self, node, tp):
        if isinstance(tp, str):
            tp = self.c_make_type_id(tp)
        if isinstance(node, str):
            declname = node
        else:
            declname = self.c_make_unique_var_name(node)
        return c_ast.TypeDecl(declname=declname, quals=[], type=tp)

    def c_make_ptr_decl(self, node, tp):
        return c_ast.PtrDecl(quals=[], type=self.c_make_type_decl(node, tp))

    def c_make_func_arg(self, node, tp):
        declname = self.c_make_unique_var_name(node)
        if isinstance(tp, str):
            tp = self.c_make_type_id(tp, declname)
        return c_ast.Decl(name=declname, quals=[], storage=[], funcspec=[],
                init=None, bitsize=None, type=tp)

    def c_make_func_decl(self, name, tp, args):
        if isinstance(tp, str):
            tp = self.c_make_type_id(tp)
        return c_ast.FuncDecl(
                args=c_ast.ParamList(args), 
                type=self.c_make_type_decl(name, tp))

    def c_make_func_def(self, decl, body):
        return c_ast.FuncDef(decl=decl, param_decls=None, body=body)

    def c_make_goto(self, node):
        name = self.c_make_unique_var_name(node)
        return c_ast.Goto(name)

    def c_make_label(self, node):
        name = self.c_make_unique_var_name(node)
        return c_ast.Label(name, None)

    def c_make_return(self, value):
        return c_ast.Return(value)

    def c_make_struct_ref(self, value, attr, type="->"):
        field = self.c_make_id(attr)
        return c_ast.StructRef(value, type=type, field=field)

    def c_make_id(self, name):
        return c_ast.ID(name)

    def c_make_if(self, test, body, orelse):
        return c_ast.If(cond=test, iftrue=body, iffalse=orelse)

    def c_make_binop(self, op, left, right):
        return c_ast.BinaryOp(op, left, right)

    def c_make_call(self, func, args):
        return c_ast.FuncCall(func, args)

    def c_make_expr_list(self, exprs):
        return c_ast.ExprList(exprs)

    def c_make_constant(self, value, type):
        return c_ast.Constant(type, value)

    def c_make_assign(self, target, value):
        return c_ast.Assignment(op='=', lvalue=target, rvalue=value)

    def c_make_subscript(self, value, slice):
        return c_ast.ArrayRef(value, slice)

    def c_make_ctype_name(self, tp):
        return '%s*' % tp.cstr()

    def c_make_cast(self, tp, expr):
        return c_ast.Cast(to_type=tp, expr=expr)

    def visit_functiondef(self, node):
        name = 'sth_main' if node.name == 'main' else node.name
        fargs = [ self.c_make_func_arg(node.args.args[0].arg, 'SthStatus*') ]
        fdecl = self.c_make_func_decl(name, 'SthRet', fargs)

        self._compound_scopes.clear()
        fbody = self.c_make_compound(node.body)

        for k, v in self._compound_scopes.items():
           tpstr = self.c_make_ctype_name(v.tp)
           fbody.block_items.insert(0, self.c_make_func_arg(v, tpstr)) 

        return self.c_make_func_def(fdecl, fbody)

    def visit_goto(self, node):
        return self.c_make_goto(node.name)

    def visit_gotolabel(self, node):
        return self.c_make_label(node.name)

    def visit_return(self, node):
        value = self.visit(node.value)
        return self.c_make_return(value)

    def visit_attribute(self, node):
        value = self.visit(node.value)
        return self.c_make_struct_ref(value, node.attr)

    def visit_name(self, node):
        return self.c_make_id(self.c_make_unique_var_name(node))

    def visit_num(self, node):
        if isinstance(node.n, int):
            tp = 'long'
        else:
            tp = 'double'
        return self.c_make_constant(str(node.n), tp)

    def visit_if(self, node):
        test = self.visit(node.test)
        body = self.c_make_compound(node.body)
        if node.orelse:
            orelse = self.c_make_compound(node.orelse)
        else:
            orelse = None
        return self.c_make_if(test, body, orelse)

    def visit_compare(self, node):
        op = self.visit(node.ops[0])
        left = self.visit(node.left)
        right = self.visit(node.comparators[0])
        return self.c_make_binop(op, left, right)

    def visit_noteq(self, node):
        return '!='

    def visit_eq(self, node):
        return '=='

    def visit_lt(self, node):
        return '<'

    def visit_lte(self, node):
        return '<='

    def visit_gt(self, node):
        return '>'

    def visit_gte(self, node):
        return '>='

    def visit_call(self, node):
        name = self.visit(node.func)
        args = self.c_make_expr_list([ self.visit(n) for n in node.args ])
        return self.c_make_call(name, args)

    def visit_assign(self, node):
        target = node.targets[0]
        value = node.value
        ctarget = self.visit(target)
        cvalue = self.visit(value)
        if isinstance(ctarget, c_ast.ID):
            self._compound_scopes[target.id] = target
        if not hasattr(value, 'tp'):
            tpstr = self.c_make_ctype_name(target.tp)
            tp = self.c_make_type_id(tpstr, '')
            cvalue = self.c_make_cast(tp, cvalue)
        elif not hasattr(target, 'tp'):
            tp = self.c_make_type_id ('void*', '')
            cvalue = self.c_make_cast(tp, cvalue)
        return self.c_make_assign(ctarget, cvalue)

    def visit_subscript(self, node):
        value = self.visit(node.value)
        slice = self.visit(node.slice)
        return self.c_make_subscript(value, slice)



def translate(tree):
    return Translator().translate(tree)


def unparse(tree):
    generator = c_generator.CGenerator()
    return generator.visit(tree)
