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
        self._main_function = False
        name_ex = Translator.NameExtractor()
        name_ex.visit(module)
        self._reserved_names = name_ex.names

    def translate(self, module):
        self._initialize(module)
        body = [ self.visit(n) for n in module.body ]
        if self._main_function:
            body.append(self.create_main_function())
        return c_ast.FileAST(body)

    def c_make_unique_var_name(self, name):
        if not name.id:
            self._var_id_count += 1
            genid = '_%d' % self._var_id_count
            if genid in self._reserved_names:
                return self.c_make_unique_var_name(name)
            else:
                name.id = genid

        return name.id 

    def c_make_compound_list(self, nodes):
        if not isinstance(nodes, list):
            nodes = [ nodes ]
        # flatten nested compound lists
        items = []
        for n in nodes:
            item = self.visit(n)
            if isinstance(item, c_ast.Compound):
                items.extend(item.block_items)
            else:
                items.append(item)

        return items

    def c_make_compound(self, items):
        return c_ast.Compound(block_items=items)

    def c_make_type_id(self, name, declname=None):
        return c_ast.IdentifierType(names=[ name ])

    def c_make_type_decl(self, node, tp):
        if isinstance(node, str):
            declname = node
        else:
            declname = self.c_make_unique_var_name(node)
        if isinstance(tp, str):
            if tp.strip().endswith('*'):
                tpname = tp.strip(' ')[:-1]
                return self.c_make_ptr_decl(declname, tpname)
            else:
                tp = self.c_make_type_id(tp, declname)
        return c_ast.TypeDecl(declname=declname, quals=[], type=tp)

    def c_make_ptr_decl(self, node, tp):
        return c_ast.PtrDecl(quals=[], type=self.c_make_type_decl(node, tp))

    def c_make_func_arg(self, node, tp):
        if isinstance(node, ast.Pointer):
            return self.c_make_func_arg(node.name, tp + '*')
        elif isinstance(node, str):
            declname = node
        else:
            declname = self.c_make_unique_var_name(node)
        if isinstance(tp, str):
            tp = self.c_make_type_decl(declname, tp)
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
        if isinstance(func, str):
            func = self.c_make_id(func)
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

    def c_make_addrof(self, expr):
        return c_ast.UnaryOp(op='&', expr=expr)

    def c_make_unaryop(self, op, expr):
        return c_ast.UnaryOp(op=op, expr=expr)

    def visit_arg(self, node):
        if isinstance(node.annotation, ast.Name):
            sthtp = node.annotation.id
        elif isinstance(node.annotation, ast.Subscript):
            sthtp = node.annotation.value.id
        if sthtp == 'SthStatus':
            tp = 'SthStatus*'
        else:
            tp = 'Sth%s%s*' % (sthtp[0].upper(), sthtp[1:])
        return self.c_make_func_arg(node.arg, tp)

    def visit_functiondef(self, node):
        name = node.name
        if node.name  == 'main':
            name = 'sth_main'
            self._main_function = True
        fargs = [ self.visit(n) for n in node.args.args ]
        fdecl = self.c_make_func_decl(name, 'SthRet', fargs)

        self._compound_scopes.clear()
        fbody = self.c_make_compound(self.c_make_compound_list(node.body))

        for k, v in self._compound_scopes.items():
            if k in [ farg.name for farg in fargs ]:
                continue
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
        body = self.c_make_compound(self.c_make_compound_list(node.body))
        if node.orelse:
            orelse = self.c_make_compound(
                    self.c_make_compound_list(node.orelse))
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

    def visit_pointer(self, node):
        return self.c_make_unaryop('*', self.visit(node.name))

    def visit_dereference(self, node):
        return self.c_make_unaryop('&', self.visit(node.name))

    def visit_call(self, node):
        name = self.visit(node.func)
        for ref in node.args[1:3]:
            if isinstance(ref, ast.Dereference) and ref.name.id:
                self._compound_scopes[ref.name.id] = ref.name
        args = self.c_make_expr_list([ self.visit(n) for n in node.args ])
        return self.c_make_call(name, args)

    def visit_assign(self, node):
        target = node.targets[0]
        value = node.value
        ctarget = self.visit(target)
        cvalue = self.visit(value)
        if isinstance(ctarget, c_ast.ID):
            self._compound_scopes[target.id] = target
        elif isinstance(ctarget, c_ast.UnaryOp) and ctarget.op == '*':
            self._compound_scopes[target.name.id] = target.name
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

    def visit_expr(self, node):
        return self.c_make_compound(self.c_make_compound_list(node.value))

    def create_main_function(self):

        def _call_sth_onearg_call(name):
            return self.c_make_if(
                self.c_make_binop(
                    '!=', 
                    self.c_make_call(
                        self.c_make_id(name),
                        self.c_make_id(staname.id)),
                    self.c_make_id('STH_OK')),
                self.c_make_compound([ self.c_make_goto(gotoname) ]), 
                None)

        def _arg_value_0_set(value):
            return self.c_make_call(
                    'sth_status_frame_argval_set',
                    self.c_make_expr_list([
                        self.c_make_id(staname.id),
                        self.c_make_constant('0', 'int'),
                        self.c_make_cast(
                            self.c_make_type_id('void*', ''),
                            value)]))
 
        # int main(int argc, char **argv) {
        fargs = [
                self.c_make_func_arg(ast.Name(id='argc'), 'int'),
                self.c_make_func_arg(ast.Name(id='argv'), 'char**') ]
        fdecl = self.c_make_func_decl('main', 'int', fargs)

        body = []

        # int ret;
        # SthStatus *st;
        # SthList *args;
        retname = ast.Name(id=None)
        staname = ast.Name(id=None)
        argname = ast.Name(id=None)
        sthretname = ast.Name(id=None)
        body.extend([
            self.c_make_func_arg(retname, 'int'),
            self.c_make_func_arg(staname, 'SthStatus*'),
            self.c_make_func_arg(argname, 'SthList*'),
            self.c_make_func_arg(sthretname, 'SthInt*'),
            self.c_make_assign(self.c_make_id(retname.id),
                self.c_make_constant('0', 'int')),
            self.c_make_assign(self.c_make_id(staname.id),
                self.c_make_constant('0', 'int')),
            self.c_make_assign(self.c_make_id(argname.id),
                self.c_make_constant('0', 'int')),
            self.c_make_assign(self.c_make_id(sthretname.id),
                self.c_make_constant('0', 'int')) ])

        # if (sth_status_new(&st) != STH_OK) {
        #   goto stherror;
        # }
        gotoname = ast.Name(id=None)
        gotolabel = self.c_make_unique_var_name(gotoname)
        body.append(
                self.c_make_if(
                    self.c_make_binop(
                        '!=', 
                        self.c_make_call(
                            self.c_make_id('sth_status_new'),
                            self.c_make_addrof(self.c_make_id(staname.id))),
                        self.c_make_id('STH_OK')),
                    self.c_make_compound([ self.c_make_goto(gotoname) ]), 
                    None))

        # if (sth_main(st, &ret, args) != STH_OK) {
        #   goto stherror;
        # }
        body.append(
                self.c_make_if(
                    self.c_make_binop(
                        '!=', 
                        self.c_make_call(
                            self.c_make_id('sth_main'),
                            self.c_make_expr_list([
                                self.c_make_id(staname.id),
                                self.c_make_addrof(self.c_make_id(sthretname.id)),
                                self.c_make_id(argname.id)])),
                        self.c_make_id('STH_OK')),
                    self.c_make_compound([ self.c_make_goto(gotoname) ]), 
                    None))
        
        # _4 = sthret->value;
        body.append(
                self.c_make_assign(
                    self.c_make_id(retname.id),
                    self.c_make_struct_ref(
                        self.c_make_id(sthretname.id),
                        'value')))

        # if (sthret->free(sthret) != STH_OK) {
        #   goto stherror;
        # }
        body.append(
                self.c_make_if(
                    self.c_make_binop(
                        '!=', 
                        self.c_make_call(
                            self.c_make_struct_ref(
                                self.c_make_id(sthretname.id),
                                'free'),
                            self.c_make_id(sthretname.id)),
                        self.c_make_id('STH_OK')),
                    self.c_make_compound([ self.c_make_goto(gotoname) ]), 
                    None))

        # sth_status_free(_7);
        body.append(
                self.c_make_call(
                    self.c_make_id('sth_status_free'),
                    self.c_make_id(staname.id)))

        # return _4;
        body.append(
                self.c_make_return(
                    self.c_make_id(retname.id)))

        # _8:
        body.append(self.c_make_label(gotoname))

        # fprintf(stderr, "Uncaught exception");
        body.append(
                self.c_make_call(
                    self.c_make_id('fprintf'),
                    self.c_make_expr_list([
                        self.c_make_id('stderr'),
                        self.c_make_constant('"Uncaught exception"',
                            'char*')])))

        # if (st) {
        #   fprintf(stderr, ": %d", st->status);
        # }
        body.append(
                self.c_make_if(
                    self.c_make_id(staname.id),
                    self.c_make_compound([ 
                        self.c_make_call(
                            self.c_make_id('fprintf'),
                            self.c_make_expr_list([
                                self.c_make_id('stderr'),
                                self.c_make_constant('": %d\\n"', 'char*'),
                                self.c_make_struct_ref(
                                    self.c_make_id(staname.id),
                                    'status')])),
                        self.c_make_return(         
                            self.c_make_struct_ref(
                                self.c_make_id(staname.id),
                                'status'))]),
                    self.c_make_compound([ 
                        self.c_make_call(
                            self.c_make_id('fprintf'),
                            self.c_make_expr_list([
                                self.c_make_id('stderr'),
                                self.c_make_constant('"\\n"', 'char*')])),
                        self.c_make_return(
                            self.c_make_constant('-1', 'int'))])))


        fbody = self.c_make_compound(body)

        return self.c_make_func_def(fdecl, fbody)


def translate(tree):
    return Translator().translate(tree)


def unparse(tree):
    preabmle = """#include "sth/sth.h"\n\n"""
    generator = c_generator.CGenerator()
    return preabmle + generator.visit(tree)
