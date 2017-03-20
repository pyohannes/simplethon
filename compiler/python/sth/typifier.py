####+

import collections
from sth import ast, types, builtins


def annotation_to_type(node):
    # At the moment only support for List[str] types is needed.
    if isinstance(node, ast.Subscript):
        return types.Collection(
                node.value.id,
                [ node.slice.value.id ])
    elif isinstance(node, ast.Name):
        if node.id == 'str':
            return types.str_
        elif node.id == 'int':
            return types.int_
        elif node.id == 'float':
            return types.float_
        elif node.id == 'bool':
            return types.bool_
        else:
            return types.Custom(node.id)


class AddScopes(ast.RecursiveNodeVisitor):

    __scopefields__ = (
            'body', 'orelse')

    class Scope(dict):
        def __init__(self, parent=None):
            self.parent = parent
    
        def __getitem__(self, key):
            try:
                return super(AddScopes.Scope, self).__getitem__(key)
            except KeyError:
                if self.parent is not None:
                    return self.parent[key]
                else:
                    raise

        def __contains__(self, key):
            if not super(AddScopes.Scope, self).__contains__(key):
                return (self.parent is not None) and (key in self.parent)
            return True

    def __init__(self):
        super(AddScopes, self).__init__(filename=None)

    def generic_visit(self, node):
        if not hasattr(node, 'sp'):
            if len(self.path) > 1:
                node.sp = self.path[-2].sp
            else:
                node.sp = self.Scope()
        for m in self.__scopefields__:
            if m in node._fields:
                sp = self.Scope(node.sp)
                for n in getattr(node, m):
                    n.sp = sp
        super(AddScopes, self).generic_visit(node)


class LinkVariables(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(LinkVariables, self).__init__(filename=None)

    def visit_module(self, node):
        for b in builtins.__builtins__:
            node.sp[b.name.id] = b.name

    def visit_assign(self, node):
        name = node.targets[0].id
        if name not in node.sp:
            node.sp[name] = node.targets[0]

    def visit_functiondef(self, node):
        if node.name not in node.sp.parent:
            name = ast.Name()
            name.id = node.name
            self.copy_source_attrs(node, name)
            node.sp.parent[node.name] = name
        for arg in node.args.args:
            name = ast.Name()
            name.id = arg.arg
            self.copy_source_attrs(arg, name)
            node.sp[name.id] = name

    def visit_name(self, node):
        if node.id in node.sp:
            self.replace_in_parent(node, node.sp[node.id])


class TypifyFunctions(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(TypifyFunctions, self).__init__(filename=None, 
                children_first=True)

    def visit_functiondef(self, node):
        tp_args = collections.OrderedDict()
        for arg in node.args.args:
            tp_args[arg.arg] = annotation_to_type(arg.annotation)
            node.sp[arg.arg].tp = tp_args[arg.arg]
        tp_returns = annotation_to_type(node.returns)
        node.tp = types.Function(tp_args, tp_returns)
        node.sp[node.name].tp = node.tp


class Typify(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(Typify, self).__init__(filename=None, children_first=True)

    def visit_num(self, node):
        if isinstance(node.n, int):
            node.tp = types.int_
        else: 
            node.tp = types.float_

    def visit_nameconstant(self, node):
        if isinstance(node.value, bool):
            node.tp = types.bool_

    def visit_call(self, node):
        if hasattr(node.func, 'tp'):
            node.tp = node.func.tp.returns

    def visit_assign(self, node):
        target = node.targets[0]
        if not hasattr(target, 'tp'):
            target.tp = node.value.tp

    def visit_attribute(self, node):
        node.tp = node.value.tp.members[node.attr]


class Convert(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(Convert, self).__init__(filename=None, children_first=True)

    def visit_assign(self, node):
        target = node.targets[0]
        dest = node.value
        if target.tp != dest.tp:
            node.value = self._adapt_type(target.tp, dest)

    def visit_call(self, node):
        argtps = list(node.func.tp.args.values())
        if isinstance(node.func, ast.Attribute):
            argtps = argtps[1:]
        if len(argtps) != len(node.args):
            self.raise_syntax_error(
                    "%s needs %d arguments, got %d" % (node.func, len(argtps),
                        len(node.args)))
        newargs = []
        for arg, argtp in zip(node.args, argtps):
            if arg.tp != argtp:
                newargs.append(self._adapt_type(argtp, arg))
            else:
                newargs.append(arg)
        node.args = newargs

    def visit_return(self, node):
        rettp = None
        for n in reversed(self.path):
            if isinstance(n, ast.FunctionDef):
                rettp = n.tp.returns
        if rettp is node.value is None:
            return
        if rettp != node.value.tp:
            node.value = self._adapt_type(rettp, node.value)

    def _adapt_type(self, targettp, dest):
        conv = ast.Attribute()
        conv.value = dest
        conv.attr = '__%s__' % (targettp.name)
        conv.tp = dest.tp.members[conv.attr]

        call = ast.Call()
        call.func = conv
        call.args = []
        call.keywords = []
        call.tp = conv.tp.returns

        return call


def typify(tree):
    for cls in (
            AddScopes, 
            LinkVariables, 
            TypifyFunctions, 
            Typify, 
            Convert ):
        cls().visit(tree)
    return tree
