####+

import sth.ast as ast


class Simplifier(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(Simplifier, self).__init__(None)

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


def simplify(tree):
    Simplifier().visit(tree)
    Simplifier().visit(tree)
    return tree
