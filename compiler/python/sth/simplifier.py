####+

import sth.ast as ast


class ReduceOperations(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(ReduceOperations, self).__init__(None)

    def visit_augassign(self, node):
        op = ast.BinOp(op=node.op, left=node.target, right=node.value)
        new = ast.Assign(targets=[node.target], value=op)
        self.copy_source_attrs(node, [op, new])
        self.replace_in_parent(node, new)

    def visit_binop(self, node):
        funcname = '__%s__' % node.op.__class__.__name__.lower()[:3]
        func = ast.Attribute(attr=funcname, value=node.left, ctx=None)
        new = ast.Call(args=[node.right], func=func, keywords=[])
        self.copy_source_attrs(node, [func, new])
        self.replace_in_parent(node, new)

    def visit_compare(self, node):
        names = { 'Eq' : 'eq',
                  'Lt' : 'lt', 
                  'Gt' : 'gt', 
                  'LtE' : 'le', 
                  'GtE' : 'ge', 
                  'NotEq' : 'ne', 
                  }
        funcname = '__%s__' % names[node.ops[0].__class__.__name__]
        func = ast.Attribute(attr=funcname, value=node.left, ctx=None)
        new = ast.Call(args=[node.comparators[0]], func=func, keywords=[])
        self.copy_source_attrs(node, [func, new])
        self.replace_in_parent(node, new)


class ReduceControlStructures(ast.RecursiveNodeVisitor):

    class ReplaceBreakContinue(ast.RecursiveNodeVisitor):

        def __init__(self, break_, continue_):
            super(ReduceControlStructures.ReplaceBreakContinue, self
                    ).__init__(None)
            self.break_ = break_
            self.continue_ = continue_
            self.break_used = self.continue_used = 0

        def visit_break(self, node):
            self._replace_with_goto(node, self.break_)
            self.break_used += 1

        def visit_continue(self, node):
            self._replace_with_goto(node, self.continue_)
            self.continue_used += 1

        def _replace_with_goto(self, node, name):
            jump = self.make_goto(name)
            self.copy_source_attrs(node, jump)
            self.replace_in_parent(node, jump)


    def __init__(self):
        super(ReduceControlStructures, self).__init__(
                None, children_first=True)

    def visit_while(self, node):
        stmts = []

        begin = self.make_anonym_gotolabel(node)

        looptest = ast.If()
        looptest.test = node.test
        looptest.body = node.body
        looptest.body.append(self.make_goto(begin.name))
        looptest.orelse = node.orelse or []
        self.copy_source_attrs(node, looptest)

        break_ = self.make_anonym_gotolabel(node)

        stmts.extend([ begin, looptest ])

        replace_bc = self.ReplaceBreakContinue(break_.name, begin.name)
        replace_bc.visit(node)
        if replace_bc.break_used:
            stmts.extend([ break_, ast.Pass() ])

        self.replace_in_parent(node, stmts)
        self.replace_in_path(node, looptest)
        self.visit_if(looptest) # ensure that the if node will be reduced

    def visit_if(self, node):
        for cls in (ast.Name, ast.NameConstant):
            if isinstance(node.test, cls):
                return
        node.test = self.make_anonym_assign(node.test)


class ReduceNestedCalls(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(ReduceNestedCalls, self).__init__(None, children_first=True)

    def visit_return(self, node):
        if isinstance(node.value, ast.Call):
            node.value = self.make_anonym_assign(node.value)

    def visit_if(self, node):
        if isinstance(node.test, ast.Call):
            node.test = self.make_anonym_assign(node.test)

    def visit_call(self, node):
        node.args = [ 
                self.make_anonym_assign(arg) if isinstance(arg, ast.Call) else arg \
                for arg in node.args ]

        if isinstance(node.func, ast.Attribute) and \
           isinstance(node.func.value, ast.Call):
            node.func.value = self.make_anonym_assign(node.func.value)


def simplify(tree):
    for cls in (
            ReduceOperations,
            ReduceOperations,
            ReduceControlStructures,
            ReduceNestedCalls
            ):
        cls().visit(tree)
    return tree
