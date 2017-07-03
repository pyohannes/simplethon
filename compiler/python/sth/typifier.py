####+

import collections
from sth import ast, types, builtins


def annotation_to_type(node, sp):
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
            return sp[node.id].tp


class _ClassHandlingMixin():

    def is_node_in_class(self):
        return self.get_class_tp()

    def get_class_tp(self):
        for n in reversed(self.path):
            if isinstance(n, ast.ClassDef):
                return getattr(n, 'tp', None)


class AddScopes(ast.RecursiveNodeVisitor):

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
        fname = 'visit_%s' % node.__class__.__name__.lower()
        if hasattr(self, fname):
            getattr(self, fname)(node)
        else:
            self.visit_default(node)

    def visit_classdef(self, node):
        for n in node.body:
            n.sp = self.Scope(node.sp)

    def visit_default(self, node):
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


class LinkVariables(ast.RecursiveNodeVisitor, _ClassHandlingMixin):

    def __init__(self):
        super(LinkVariables, self).__init__(filename=None)

    def visit_module(self, node):
        for b in builtins.__builtins__:
            node.sp[b.name] = b.sthname

    def visit_assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name and name not in node.sp:
                node.sp[name] = node.targets[0]

    def visit_classdef(self, node):
        if node.name not in node.sp.parent:
            node.sp.parent[node.name] = self.make_name(node.name, node)

    def visit_functiondef(self, node):
        if node.name not in node.sp.parent:
            node.sp.parent[node.name] = self.make_name(node.name, node)
        for arg in node.args.args:
            node.sp[arg.arg] = self.make_name(arg.arg, node)

    def visit_name(self, node):
        if node.id in node.sp:
            self.replace_in_parent(node, node.sp[node.id])


class TypifyClasses(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(TypifyClasses, self).__init__(filename=None)

    def visit_classdef(self, node):
        node.tp = types.make_class(node.name)
        node.sp[node.name].tp = node.tp


class TypifyFunctions(ast.RecursiveNodeVisitor, _ClassHandlingMixin):

    def __init__(self):
        super(TypifyFunctions, self).__init__(filename=None)

    def visit_functiondef(self, node):
        tp_args = collections.OrderedDict()
        for arg in node.args.args:
            tp_args[arg.arg] = annotation_to_type(arg.annotation, node.sp)
            node.sp[arg.arg].tp = tp_args[arg.arg]
        tp_returns = annotation_to_type(node.returns, node.sp)
        node.tp = types.Function(tp_args, tp_returns)
        if self.is_node_in_class():
            self.get_class_tp().members[node.name] = node.tp
        else:
            node.sp[node.name].tp = node.tp


class ConvertClassInit(ast.RecursiveNodeVisitor, _ClassHandlingMixin):

    def __init__(self):
        super(ConvertClassInit, self).__init__(filename=None)

    def is_class_init(self, call):
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
            try:
                cls = call.sp[call.func.id]
                return cls and isinstance(cls.tp, types.Custom)
            except:
                return False

    def visit_assign(self, node):
        if self.is_class_init(node.value):
            self.transform_call(node.value, node.targets[0], node)

    def visit_call(self, node):
        if self.is_class_init(node):
            self.transform_call(node, None, node)

    def transform_call(self, call, target, parent):
        cls = parent.sp[call.func.id]
        if target is None:
            obj = self.make_name(None, None)
        else:
            obj = target
        new = ast.Call(
                func=self.make_attr(cls, '__new__'),
                args=[],
                keywords=[],
                ctx=None)
        init = ast.Call(
                func=self.make_attr(obj, '__init__'),
                args=call.args,
                keywords=[],
                ctx=None)
        init.tp = init.func.tp = cls.tp.members['__init__']
        new.tp = new.func.tp = cls.tp.members['__new__']
        obj.tp = cls.tp
        self.copy_source_attrs(parent, [new, init])
        if not target:
            self.replace_in_parent(parent, [new, ast.Expr(value=init)])
        else:
            ass = self.make_assign(obj, new)
            self.replace_in_parent(parent, [ass, ast.Expr(value=init)])


class Typify(ast.RecursiveNodeVisitor, _ClassHandlingMixin):

    def __init__(self):
        super(Typify, self).__init__(filename=None, bottomup=True)

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

    #def visit_assign(self, node):
    #    target = node.targets[0]
    #    if not hasattr(target, 'tp') and hasattr(node.value, 'tp'):
    #        target.tp = node.value.tp

    def visit_assign(self, node):
        target = node.targets[0]
        if isinstance(target, ast.Attribute):
            if not target.attr in target.value.tp.members:
                target.value.tp.members[target.attr] = node.value.tp
        else:
            if not hasattr(target, 'tp'):
                target.tp = node.value.tp

    def visit_attribute(self, node):
        # Resolving the type of an attribute can be delayed. This can happen
        # for attribute definitions, where due to the bottom-up analysis the
        # attribute is only available after the parent (ast.Assign) has been
        # resolved.
        # The type is set in TypifyClassMemberInit.
        if node.attr in node.value.tp.members:
            node.tp = node.value.tp.members[node.attr]


class TypifyClassMemberInit(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(TypifyClassMemberInit, self).__init__(filename=None, bottomup=True)

    def visit_attribute(self, node):
        node.tp = node.value.tp.members[node.attr]


class Convert(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(Convert, self).__init__(filename=None, bottomup=True)

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
        node.args = [
                self._adapt_type(argtp, arg) if arg.tp != argtp else arg \
                for arg, argtp in zip(node.args, argtps) ]

    def visit_if(self, node):
        if node.test.tp != types.bool_:
            node.test = self._adapt_type(types.bool_, node.test)

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

        name = self.make_anonym_assign(call)
        name.tp = call.tp
        return name


def typify(tree):
    for cls in (
            AddScopes, 
            LinkVariables, 
            TypifyClasses, 
            TypifyFunctions, 
            ConvertClassInit, 
            Typify, 
            TypifyClassMemberInit, 
            Convert ):
        cls().visit(tree)
    return tree
