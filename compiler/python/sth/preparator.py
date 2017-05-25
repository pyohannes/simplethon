####+

import collections
from sth import ast, types


class InitializeConstants(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(InitializeConstants, self).__init__(None)

    def _make_constant_init(self, node, tp, value):
        func = self.make_name('sth_%s_new' % node.tp.name, node)
        func.tp = types.Function(collections.OrderedDict(), tp)
        call = ast.Call(func=func, keywords=[], args=[])
        call.tp = call.func.tp.returns
        name = self.make_anonym_assign(call)
        name.tp = node.tp
        attr = self.make_attr(name, 'value')
        ass = self.make_assign(attr, value)
        self.add_in_parent_stmt_list(ass)
        self.replace_in_parent(node, name)

    def visit_num(self, node):
        self._make_constant_init(node, types.int_, node)

    def visit_nameconstant(self, node):
        if isinstance(node.value, bool):
            value = ast.Num(n=1 if node.value else 0)
            self._make_constant_init(node, types.bool_, value)


class RemoveExpr(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(RemoveExpr, self).__init__(None)

    def visit_expr(self, node):
        self.replace_in_parent(node, node.value)


class FunctionArgumentsInStatus(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(FunctionArgumentsInStatus, self).__init__(None)
        self._statusobj = None
        self._gotoreturn = None
        self._statustp = self.make_name('SthStatus', None)
        self.STH_OK = self.make_name('STH_OK', None)
        self.STH_OK.tp = types.Custom('SthRet')

    def visit_functiondef(self, node):
        # initialize status object
        self._statusobj = self.make_name(None, node)
        self._statusobj.tp = types.Custom('SthStatus')
        self._gotoreturn = ast.Goto(name=self.make_name(None, node))

        # add arguments
        for pos, arg in enumerate(node.args.args):
            retval = self.make_attr(
                    self._statusobj, 'current_frame', 'arg_values', 
                    slice=ast.Num(n=pos))
            ass = self.make_assign(node.sp[arg.arg], retval)
            node.body.insert(pos, ass)

        # replace arguments
        statusarg = ast.arg(arg=self._statusobj, annotation=self._statustp)
        node.args.args = [ statusarg ]

        # add final return
        statusret = self.make_attr(self._statusobj, 'status')
        ret = ast.Return(value=statusret)
        ret.noprepare= True # avoid translating this return during further
                            # preparation
        gotol = ast.GotoLabel(name=self._gotoreturn.name)
        node.body.extend([ gotol, ret ])

    def visit_assign(self, node):
        if isinstance(node.value, ast.Call):
            self.visit_call(node.value, assign=node)
            node.value = None
            self.replace_in_parent(node, [])

    def make_funcall(self, funcname, args):
        if isinstance(funcname, str):
            funcname = self.make_name(funcname, None)
        newf_call = ast.Call(func=funcname, keywords=[], args=args)
        comp = ast.Compare(left=newf_call, ops=[ ast.NotEq() ], 
                comparators=[ self.STH_OK ])
        return ast.If(test=comp, body=self._gotoreturn, orelse=None)

    def visit_call(self, node, assign=None):
        stmts = []
        
        # new frame 
        newf_args = [
                self._statusobj,
                ast.Num(n=len(node.func.tp.args)),
                ast.Num(n=1 if node.func.tp.returns else 0) ]
        stmts.append(self.make_funcall('sth_frame_new', newf_args))

        # set arguments, add self in case of class invocations
        args = node.args
        if isinstance(node.func, ast.Attribute):
            args.insert(0, node.func.value)
        for index, arg in enumerate(args):
            argval = self.make_attr(
                    self._statusobj, 'current_frame', 'arg_values', 
                    slice=ast.Num(n=index))
            stmts.append(self.make_assign(argval, arg))

        # call function
        stmts.append(self.make_funcall(node.func, [ self._statusobj ]))

        # set target
        if assign:
            retval = self.make_attr(
                    self._statusobj, 'current_frame', 'return_values', 
                    slice=ast.Num(n=0))
            stmts.append(self.make_assign(assign.targets, retval))

        # free frame 
        stmts.append(self.make_funcall('sth_frame_free', [ self._statusobj ]))

        self.replace_in_parent(assign or node, stmts)

    def visit_return(self, node):
        if not getattr(node, 'noprepare', False):
            retval = self.make_attr(
                    self._statusobj, 'current_frame', 'return_values', 
                    slice=ast.Num(n=0))
            ass = self.make_assign(retval, node.value)
            self.replace_in_parent(node, [ ass, self._gotoreturn ])


def prepare(tree):
    for cls in (
            InitializeConstants,
            RemoveExpr, # needed to avoid superfluous empty lines
            FunctionArgumentsInStatus
            ):
        cls().visit(tree)
    return tree
