####+

import sth.ast as ast


class Simplifier(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(Simplifier, self).__init__(None)

    def _replace_in_parent(self, old, new):
        parent = self.path[-2]
        for f in parent._fields:
            child = getattr(parent, f)
            if child is old:
                setattr(parent, f, new)
            elif isinstance(child, list):
                child = [ new if c is old else c for c in child ]
                setattr(parent, f, child)

    def _copy_source_attrs(self, src, dsts):
        try:
            dsts[0]
        except:
            dsts = [ dsts ]
        try:
            for d in dsts:
                d.lineno = src.lineno
                d.col_offset = src.col_offset
        except AttributeError: pass

    def visit_augassign(self, node):
        op = ast.BinOp(op=node.op, left=node.target, right=node.value)
        new = ast.Assign(targets=[node.target], value=op)
        self._copy_source_attrs(node, [op, new])
        self._replace_in_parent(node, new)

    def visit_binop(self, node):
        funcname = '__%s__' % node.op.__class__.__name__.lower()[:3]
        func = ast.Attribute(attr=funcname, value=node.left, ctx=None)
        new = ast.Call(args=[node.right], func=func, keywords=[])
        self._copy_source_attrs(node, [func, new])
        self._replace_in_parent(node, new)

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
        self._copy_source_attrs(node, [func, new])
        self._replace_in_parent(node, new)


def simplify(tree):
    Simplifier().visit(tree)
    Simplifier().visit(tree)
    return tree
