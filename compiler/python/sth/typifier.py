####+
#```((mode docu) (post ("replace-variables")))
#\section{\tc{``(file-basename)``}: Typifier}
#
# The typifier adds type information to all relevant nodes of the syntax tree.
# It manipulates the syntax tree in the following ways:
# \begin{itemize}
#
#   \item Scopes holding references to different variables are inserted. Every
#   node is equipped with a \tc{sp} attribute that points to the scope the node
#   belongs to.
#
#   \item All different nodes referencing the same variable are replaced by one
#   node.
#
#   \item Class initializations are replaced by calls to \tc{\_\_new\_\_} and
#   \tc{\_\_init\_\_}.
#
# \end{itemize}
#
# For convenience, the modules \tc{ast}, \tc{types} and \tc{builtins} are used
# without the \tc{sth} prefix.
#```
import collections
from sth import ast, types, builtins
#```
#\subsection{Helpers}
#
# The function \tc{annotation\_to\_type} converts type annotations of arguments
# and functions to Simplethon types. All Simplethon types are subclasses of
# \tc{sth.types.Type}. It is assumed that variable bindings referencing types
# are added to the module namespace.
#
# For simple types function retrieves the type object from the variable 
# binding, for composite types the corresponding type object will be created. 
# Composite types are not supported yet, the code available only serves the 
# purpose to support \tc{List[str]} type annotations.
#```
def annotation_to_type(node, sp):
    if isinstance(node, ast.Subscript):
        return types.List(
                [ node.slice.value.id ])
    elif isinstance(node, ast.Name):
        return sp[node.id].tp.tp
#```
# The \tc{\_ClassHandlingMixin} provides some helper functions for dealing with
# classes. The function \tc{is\_node\_in\_class} tests if the current node is an
# (indirect) child of a class. \tc{get\_class\_tp} returns the type of the class 
# that the current node is an (indirect) child of.
#```
class _ClassHandlingMixin():

    def is_node_in_class(self):
        for n in self.path:
            if isinstance(n, ast.ClassDef):
                return True
        else:
            return False

    def get_class_tp(self):
        for n in reversed(self.path):
            if isinstance(n, ast.ClassDef):
                return getattr(n, 'tp', None)
#```
#\subsection{Adding scope information}
#
# Scopes are managed as a tree of \tc{Scope} objects. This tree is separated
# from the syntax tree. Every node of the syntax tree has a \tc{sp} field that
# points to a \tc{Scope} object in the scope tree. Scopes contain variable
# bindings which in turn consist of two elements: the variable name as key and 
# a corresponding \tc{ast.Name} object as value.
#
# \tc{Scope} objects are dictionaries that are linked to a parent \tc{Scope}
# object (except the root module scope). An entry for a variable in the scope
# tree is requested by its name. If the name cannot be found an attempt is made
# to find the name in the parent scope. This is done recursively until no other
# parent scope is available.
#```
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
#```
# Class definitions are treated separately. Whereas for other nodes that have a
# body (e. g. functions or if statements) every node of the body has to points
# to the same scope, in case of classes every node of the body needs to have
# its own scope.
#```
    def visit_classdef(self, node):
        for n in node.body:
            n.sp = self.Scope(node.sp)
#```
#\subsection{Linking variables}
#
# All variable names in the code are represented by \tc{ast.Name} nodes. In
# this step \tc{ast.Name} nodes in the tree are modified so that all
# \tc{ast.Name} nodes referencing the same variable also are the same
# \tc{ast.Name} object. In this way, adding type information to an
# \tc{ast.Name} object affects all occurences of the node in the tree. In this
# regard, the syntax tree is transformed into a directed acyclic graph.
#```
class LinkVariables(ast.RecursiveNodeVisitor, _ClassHandlingMixin):

    def __init__(self):
        super(LinkVariables, self).__init__(filename=None)
#```
# All available builtin symbols are added to the root module scope.
#
# Furthermore variable bindings for all builtin types are added to the module
# scope. For the types \tc{List} and \tc{str} only dummy bindings without type
# are available at the moment.
#
# Type and builtin bindings have to remain in the module scope, as overwriting
# one of those builtin types only affects the module, but not other modules
# that import the module changing the binding.
#```
    def visit_module(self, node):
        for b in builtins.__builtins__:
            node.sp[b.name] = b.sthname
        for t in ('int', 'float', 'bool'):
            name = self.make_name(t, None)
            name.tp = getattr(types, '%s_' % t).clstp
            node.sp[t] = name
        node.sp['List'] = self.make_name('List', None)
        node.sp['str'] = self.make_name('str', None)
#```
# This method treats assignments that introduce a new variable binding. If the
# name of the variable cannot be resolved through the scope tree, a new
# variable binding is introduced to the current scope.
#
# Assignments that assign to attributes are treated in the \tc{Typify} class,
# where attributes are typified.
#```
    def visit_assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name and name not in node.sp:
                node.sp[name] = node.targets[0]
#```
# Whenever a class definition is encountered, a new binding is created.
# This means that existing class definitions can be overwritten.
#```
    def visit_classdef(self, node):
        node.sp.parent[node.name] = self.make_name(node.name, node)
#```
# For function definitions two kinds of variable bindings are added:
# \begin{enumerate}
#  \item A binding for unbound functions itself is added to the parent scope of 
#  the function. This only occurs for unbound functions. Class methods are not
#  bound and resolved via the scope tree but via the class type object.
#  \item A binding for each argument of the function is added to the scope of
#  the function itself.
# \end{enumerate}
#```
    def visit_functiondef(self, node):
        if not self.is_node_in_class():
            node.sp.parent[node.name] = self.make_name(node.name, node)
        for arg in node.args.args:
            node.sp[arg.arg] = self.make_name(arg.arg, node)
#```
# Finally all name nodes are replaced with the name node of the same name that
# is available through the scope. If no node of the same name can be found in
# the scope this indicates a name error (an undefined variable is used).
#
# Temporary unnamed names (where \tc{node.id} is unset) are not touched. During
# modifying the syntax tree it has to be ensured, that those nodes are
# referenced and used properly.
#```
    def visit_name(self, node):
        try:
            if node.id:
                self.replace_in_parent(node, node.sp[node.id])
        except KeyError:
            raise NameError("name '%s' is not defined" % node.id)
#```
#\subsection{Typify classes and functions}
#
# In this step types of classes and functions (and methods) are created and
# assigned to variable bindings created in the step before.
#```
class CreateClassFunctionTypes(ast.RecursiveNodeVisitor, _ClassHandlingMixin):

    def __init__(self):
        super(CreateClassFunctionTypes, self).__init__(filename=None)
#```
# For class definitions, a new type object is created and assigned to the
# variable binding for the class. The type object will be an instance of
# \tc{types.CustomType}.
#```
    def visit_classdef(self, node):
        node.tp = types.make_class(node.name).clstp
        node.sp[node.name].tp = node.tp
#```
# For function definitions a new type object \tc{types.Function} is created and
# assigned to the variable binding of the function name. The function type also
# comprises type objects for arguments and return values.
#
# In case of unbound methods the type object is additionally added to the 
# existing variable binding in the scope tree. In case of class methods the
# type object is added to the members dictionary of the class type object.
#```
    def visit_functiondef(self, node):
        tp_args = collections.OrderedDict()
        for arg in node.args.args:
            tp_args[arg.arg] = annotation_to_type(arg.annotation, node.sp)
            node.sp[arg.arg].tp = tp_args[arg.arg]
        tp_returns = annotation_to_type(node.returns, node.sp)
        node.tp = types.Function(tp_args, tp_returns)
        if self.is_node_in_class():
            self.get_class_tp().tp.members[node.name] = node.tp
        else:
            node.sp[node.name].tp = node.tp
#```
#\subsection{Reduce implicit class instantiation and initialization}
#
# Class instantiation and initialization in Simplethon is done by just calling
# the class name with arguments of the provided \tc{\_\_init\_\_} method. At
# this point this implicit call to the class name is replaced by two calls to
# the methods \tc{\_\_new\_\_} and \tc{\_\_init\_\_}. The call \tc{\_\_new\_\_}
# allocates memory and returns an uninitialized instance of the class. The call
# to \tc{\_\_init\_\_} initializes the object.
#
# \begin{table}[h]
#  \centering
#  \begin{tabular}{lcl}
#    \ti{p = Point(3, 4)} & $\Rightarrow$ & \ti{p = Point.\_\_new\_\_()} \\
#                         &               & \ti{p.\_\_init\_\_(3, 4)} \\
#  \end{tabular}
# \end{table}
#
# Calls on the right side of assignments have to be treated specially, as the
# identifier on the left side of the assignment has to be used during the
# reduction. If the call is not used in an assignment, the object is assigned
# to an anonymous variable.
#```
class ReduceClassInitialization(ast.RecursiveNodeVisitor, _ClassHandlingMixin):

    def __init__(self):
        super(ReduceClassInitialization, self).__init__(filename=None)

    def _is_class_init(self, call):
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
            try:
                cls = call.sp[call.func.id]
                return cls and isinstance(cls.tp, types.Class)
            except:
                return False

    def visit_assign(self, node):
        if self._is_class_init(node.value):
            self.transform_call(node.value, node.targets[0], node)

    def visit_call(self, node):
        if self._is_class_init(node):
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
        self.copy_source_attrs(parent, [new, init])
        if target:
            new = self.make_assign(obj, new)
        self.replace_in_parent(parent, [new, ast.Expr(value=init)])
#```
#\subsection{Typify constants, calls, assignments and attributes}
#
# In this step type information is added to nodes in the syntax tree. The
# syntax tree is processed bottom up, as in assignments the value has to be
# processed before so that the type information can be passed on to the target.
#```
class Typify(ast.RecursiveNodeVisitor, _ClassHandlingMixin):

    def __init__(self):
        super(Typify, self).__init__(filename=None, bottomup=True)
#```
# For \tc{ast.Num} nodes the types \tc{int} or \tc{float} are used, depending
# on the value.
#```
    def visit_num(self, node):
        if isinstance(node.n, int):
            node.tp = types.int_
        else: 
            node.tp = types.float_
#```
# Only boolean constants (\tc{True} or \tc{False}) are supported at the moment.
#```
    def visit_nameconstant(self, node):
        if isinstance(node.value, bool):
            node.tp = types.bool_
#```
# Calls are typified with the type of their return value.
#```
    def visit_call(self, node):
        if hasattr(node.func, 'tp'):
            node.tp = node.func.tp.returns
#```
# Assignments are processed differently, depending on the type of the target:
# \begin{itemize}
#  \item If the target is an attribute, the assignment is made to a class
#  member. If the attribute name is not yet in the members dictionary of the
#  class of the attribute value, it is added. The type of the value of the
#  assignment is assumed.
#  \item In all other cases, where the target is an \tc{ast.Name}, the type of
#  the target is assumed to be the type of the value if the target has no type
#  assigned to it yet.
# \end{itemize}
#```
    def visit_assign(self, node):
        target = node.targets[0]
        if isinstance(target, ast.Attribute):
            clsmembers = target.value.tp.members
            if not target.attr in clsmembers:
                target.tp = clsmembers[target.attr] = node.value.tp
        else:
            if not hasattr(target, 'tp'):
                target.tp = node.value.tp
#```
# A check has to be made, whether the name of the attribute is present in the
# members dictionary of the class type object. This check fails, if the
# attribute is part of an assignment that initializes a class member. Due to
# the bottom up processing order of nodes, the attribute is processed before th
# assignment and therefore the attribute name is not yet present in the class
# type object members dictionary. In this case, the type information is added
# later during the processing of the parent assignment.
#
# If the attribute is not present in the member dictionary and the attribute
# node is not part the target part of an assignment, an \tc{AttributeError} is
# raised.
#
# In all other cases, the type of the entry in the members dictionary is
# applied to the attribute node.
#```
    def visit_attribute(self, node):
        if not node.attr in node.value.tp.members:
            parent = self.path[-2]
            if isinstance(parent, ast.Assign) and parent.targets[0] != node:
                raise AttributeError("'%s' object has no attribute '%s'" % (
                    node.value.tp.name, node.attr))
        else:
            node.tp = node.value.tp.members[node.attr]
#```
#\subsection{Convert types and report conflicts}
#
# Finally, type conversions are made and type conflicts are identified and
# reported.
#```
class Convert(ast.RecursiveNodeVisitor):

    def __init__(self):
        super(Convert, self).__init__(filename=None, bottomup=True)
#```
# The method \tc{\_adapt\_type} is a helper method that makes type conversions.
# Type conversions are made by invoking conversion methods on the object. The
# name of the conversion method consists of the name of the target type and
# two leading and trailing underscores. 
#
# \begin{table}[h]
#  \centering
#  \begin{tabular}{lcl}
#    \ti{p = True} & $\Rightarrow$ & \ti{p = True} \\
#    \ti{p = 4}    &               & \ti{p = 4 .\_\_bool\_\_()} \\
#  \end{tabular}
# \end{table}
#
#If this method does not exists, a
# \tc{TypeError} is raised.
#```
    def _adapt_type(self, targettp, dest):
        conv = ast.Attribute()
        conv.value = dest
        conv.attr = '__%s__' % (targettp.name)
        try:
            conv.tp = dest.tp.members[conv.attr]
        except KeyError:
            raise TypeError(
                "an object of type '%s' cannot be converted to '%s'" % (
                    dest.tp.name, targettp.name))

        call = ast.Call()
        call.func = conv
        call.args = []
        call.keywords = []
        call.tp = conv.tp.returns

        name = self.make_anonym_assign(call)
        name.tp = call.tp
        return name
#```
# Type conversions can occur at the following places:
#
# \begin{enumerate}
# \item In assignments. If the type of the target does not match the type of
# the value, a conversion attempt is made.
#```
    def visit_assign(self, node):
        target = node.targets[0]
        dest = node.value
        if target.tp != dest.tp:
            node.value = self._adapt_type(target.tp, dest)
#```
# \item In calls. First it is checked, if the number of arguments given to a
# call matches the number of arguments in the corresponding function
# definition. Then conversion attempts are made for arguments of the call when 
# the type of the given argument does not match the type of the corresponding
# argument in the function definition.
#```
    def visit_call(self, node):
        argtps = list(node.func.tp.args.values())
        if isinstance(node.func, ast.Attribute):
            argtps = argtps[1:]
        if len(argtps) != len(node.args):
            self.raise_syntax_error(
                    "%s needs %d arguments, got %d" % (node.func, 
                        len(argtps), len(node.args)))
        node.args = [
                self._adapt_type(argtp, arg) if arg.tp != argtp else arg \
                for arg, argtp in zip(node.args, argtps) ]
#```
# \item In tests of if-statements. Tests in if-statements must be converted
# into boolean types to be resolved.
#```
    def visit_if(self, node):
        if node.test.tp != types.bool_:
            node.test = self._adapt_type(types.bool_, node.test)
#```
# \item In returns. If the type of the value of a return statement does not 
# match the return type of the function definition, a conversion attempt is
# made.
#```
    def visit_return(self, node):
        rettp = None
        for n in reversed(self.path):
            if isinstance(n, ast.FunctionDef):
                rettp = n.tp.returns
        if rettp is node.value is None:
            return
        if rettp != node.value.tp:
            node.value = self._adapt_type(rettp, node.value)
#```
# \end{enumerate}
#
# The interface method typify applies all visitors to a given syntax tree. The
# order of application is crucial.
#```
def typify(tree):
    for cls in (
            AddScopes, 
            LinkVariables, 
            CreateClassFunctionTypes,
            ReduceClassInitialization, 
            Typify, 
            Convert ):
        cls().visit(tree)
    return tree
