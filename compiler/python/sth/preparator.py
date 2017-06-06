####+

import collections
from sth import ast, types


class InitializeConstants(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(InitializeConstants, self).__init__(None)

    def _make_constant_init(self, node, tp, value):
        func = self.make_name('sth_%s_new' % node.tp.name, node)
        func.tp = types.Function(collections.OrderedDict(), tp)
        call = ast.Call(func=func, keywords=[], args=[value])
        call.tp = call.func.tp.returns
        name = self.make_anonym_assign(call)
        name.tp = node.tp
        self.replace_in_parent(node, name)

    def visit_num(self, node):
        self._make_constant_init(node, types.int_, node)

    def visit_nameconstant(self, node):
        if isinstance(node.value, bool):
            val = ast.Name('Sth_True' if node.value else 'Sth_False', node)
            val.tp = node.tp
            self.replace_in_parent(node, val)


class BoolIfAttrs(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(BoolIfAttrs, self).__init__(None)

    def visit_if(self, node):
        if isinstance(node.test, ast.Name):
            tp = node.test.tp
            node.test = self.make_attr(node.test, 'value')
            node.test.tp = tp



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
        self._gotoreturn = self.make_goto(self.make_name(None, node))
        self._returnobj = self.make_name(None, node)
        self._returnobjptr = self.make_pointer(self._returnobj, node)
        if node.tp.returns:
            self._returnobjptr.tp = self._returnobj.tp = node.tp.returns
        else:
            self._returnobjptr.tp = self._returnobj.tp = types.craw
        returntp = self.make_name(self._returnobj.tp.name, node)

        # add SthStatus and return object
        statusarg = ast.arg(arg=self._statusobj, annotation=self._statustp)
        returnarg = ast.arg(arg=self._returnobjptr, annotation=returntp)
        node.args.args.insert(0, statusarg)
        node.args.args.insert(1, returnarg)

        # add final return
        statusret = self.make_attr(self._statusobj, 'status')
        ret = self.make_return(statusret, noprepare=True)
        gotol = ast.GotoLabel(name=self._gotoreturn.value.name)
        node.body.extend([ gotol, ret ])

    def visit_assign(self, node):
        if isinstance(node.value, ast.Call):
            self.visit_call(node.value, assign=node)
            node.value = None
            self.replace_in_parent(node, [])

    def make_return(self, value, noprepare=False):
        ret = ast.Return(value=value)
        if noprepare:
            ret.noprepare = True
        return ret

    def make_assign(self, targets, value, noprepare=False):
        ass = super(FunctionArgumentsInStatus, self).make_assign(targets, 
                value)
        if noprepare:
            ass.noprepare = True
        return ass

    def make_funcall(self, funcname, args, noprepare=False, expr=False):
        if isinstance(funcname, str):
            funcname = self.make_name(funcname, None)
        call = ast.Call(func=funcname, keywords=[], args=args)
        if noprepare:
            call.noprepare = True
        if expr:
            call = ast.Expr(value=call)
        return call

    def make_checked_funcall(self, funcname, args):
        newf_call = self.make_funcall(funcname, args)
        comp = ast.Compare(left=newf_call, ops=[ ast.NotEq() ], 
                comparators=[ self.STH_OK ])
        return ast.If(test=comp, body=[self._gotoreturn], orelse=None)

    def generic_visit(self, node):
        if not getattr(node, 'noprepare', False):
            super(FunctionArgumentsInStatus, self).generic_visit(node)

    def visit_call(self, node, assign=None):
        # set arguments, add self in case of class invocations
        node.args.insert(0, self._statusobj)
        if assign:
            retobj = assign.targets[0]
        else:
            retobj = self.make_name(None, node)
            retobj.tp = types.craw
        node.args.insert(1, self.make_dereference(retobj, node))
        if isinstance(node.func, ast.Attribute):
            node.args.insert(2, node.func.value)

        # call function
        call = self.make_checked_funcall(node.func, node.args)

        self.replace_in_parent(assign or node, call)

    def visit_return(self, node):
        target = self.make_pointer(self._returnobj, node)
        target.tp = self._returnobj.tp
        retass = self.make_assign(target, node.value)
        self.replace_in_parent(node, [ retass, self._gotoreturn ])


def prepare(tree):
    for cls in (
            BoolIfAttrs,
            InitializeConstants,
            FunctionArgumentsInStatus
            ):
        cls().visit(tree)
    return tree
