# ============================================================================
# AST NODE CLASSES - The shape of every node in the GAL syntax tree
# ============================================================================
# Extracted from GALsemantic.py during the modular restructure.
# Every compiler phase after parsing consumes these node types:
#   - parser/builder.py constructs them
#   - semantic/analyzer.py validates them
#   - icg/generator.py walks them to emit TAC
#   - interpreter/ evaluates them
#
# Named ast_nodes.py (not ast.py / not in an ast/ folder) so it does not
# shadow Python's stdlib "ast" module — many third-party libraries
# (flask, eventlet, werkzeug) call into stdlib ast and would break if
# we hijacked the name.
# ============================================================================


# ============================================================================
# AST NODE CLASSES
# Each node has:
#   - node_type   : a string label (e.g. "Program", "VariableDeclaration")
#   - value       : the node's primary data (function name, operator, etc.)
#   - children    : list of child ASTNodes
#   - line        : source line for error reporting
#   - parent      : back-pointer for traversals (set by add_child)
# Subclasses below define convenient constructors for each AST shape.
# ============================================================================
class ASTNode:
    def __init__(self, node_type, value=None, line=None):
        self.node_type = node_type  # Type of node (e.g., 'VariableDeclaration', 'BinaryOp')
        self.value = value  # E.g. variable name, operator, etc.
        self.children = []  # List of child nodes
        self.parent = None  # Reference to parent node
        self.line = line

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def print_tree(self, level=0):
        """Pretty-print the AST."""
        indent = ' ' * (level * 3)
        print(f"{indent}╚═{self.node_type}: {self.value if self.value else ''}")
        for child in self.children:
            child.print_tree(level + 1)
        

class ProgramNode(ASTNode):
    def __init__(self, line=None):
        super().__init__("Program", line=line)

class VariableDeclarationNode(ASTNode):
    def __init__(self, var_type, var_name, value=None, line=None):
        super().__init__("VariableDeclaration", line=line)
        self.add_child(ASTNode("Type", var_type, line=line))
        self.add_child(ASTNode("Identifier", var_name, line=line))
        if value:
            self.add_child(value)

class AssignmentNode(ASTNode):
    def __init__(self, target, value, line=None):
        super().__init__("Assignment", line=line)
        if isinstance(target, str):
            self.add_child(ASTNode("Identifier", target, line=line))
        else:
            self.add_child(target)
        self.add_child(value)
        

class BinaryOpNode(ASTNode):
    def __init__(self, left, operator, right, line=None):
        super().__init__("BinaryOp", operator, line=line)
        self.add_child(left)
        self.add_child(right)

class FunctionDeclarationNode(ASTNode):
    def __init__(self, return_type, name, params, line=None):
        super().__init__("FunctionDeclaration", name, line=line)
        self.add_child(ASTNode("ReturnType", return_type, line=line))
        self.add_child(params)

class FunctionCallNode(ASTNode):
    def __init__(self, name, args, line=None):
        super().__init__("FunctionCall", name, line=line)
        for arg in args:
            self.add_child(arg)

class IfStatementNode(ASTNode):
    def __init__(self, condition, line=None):
        super().__init__("IfStatement", line=line)
        self.add_child(condition)

class ForLoopNode(ASTNode):
    def __init__(self, initialization, condition, update, line=None):
        super().__init__("ForLoop", line=line)  
        self.add_child(initialization)
        self.add_child(condition)
        self.add_child(update)

class WhileLoopNode(ASTNode):
    def __init__(self, condition, line=None):
        super().__init__("WhileLoop", line=line)  
        self.add_child(condition)

class DoWhileLoopNode(ASTNode):
    def __init__(self, condition, line=None):
        super().__init__("DoWhileLoop", line=line)
        #self.add_child(condition)

class PrintNode(ASTNode):
    def __init__(self, args, line=None):
        super().__init__("PrintStatement", line=line) 
        for arg in args:
            self.add_child(arg)

class UnaryOpNode(ASTNode):
    def __init__(self, operator, operand, position="pre", line=None):
        super().__init__("UnaryOp", operator, line=line)
        self.position = position
        self.add_child(operand)

class FertileDeclarationNode(ASTNode):
    def __init__(self, var_type, var_name, value, line=None):
        super().__init__("SturdyDeclaration", line=line)
        self.add_child(ASTNode("Type", var_type, line=line))
        self.add_child(ASTNode("Identifier", var_name, line=line))
        self.add_child(value)

class ReturnNode(ASTNode):
    def __init__(self, return_value=None, line=None):
        super().__init__("Return", line=line)
        if return_value:
            self.add_child(return_value)

class UpdateNode(ASTNode):
    def __init__(self, operator, operand, prefix = True, line=None):
        super().__init__("Update", line=line)
        self.prefix = prefix
        self.add_child(operand)
        self.add_child(operator)

class SwitchNode(ASTNode):
    def __init__(self, expression, cases, default_case, line=None):
        super().__init__("Switch", line=line)
        self.add_child(expression)
        for case in cases:
            self.add_child(case)
        if default_case is not None:
            self.add_child(default_case)

class ContinueNode(ASTNode):
    def __init__(self, line=None):
        super().__init__("Continue", line=line)

class BreakNode(ASTNode):
    def __init__(self, line=None):
        super().__init__("Break", line=line)

class ListNode(ASTNode):
    def __init__(self, line=None, elements = None):
        super().__init__("List", line=line)
        self.elements = elements
        for element in elements:
            self.add_child(element)

class TaperNode(ASTNode):
    def __init__(self, variable_name, line=None):
        super().__init__("TaperFunction", line=line)
        self.add_child(ASTNode("Identifier", variable_name, line=line))

class TSNode(ASTNode):
    def __init__(self, variable_name, line=None):
        super().__init__("TSFunction", line=line)
        self.add_child(ASTNode("Identifier", variable_name, line=line))

class SoilNode(ASTNode):
    def __init__(self, variable_name, line=None):
        super().__init__("SoilFunction", line=line)
        self.add_child(ASTNode("Identifier", variable_name, line=line))

class BloomNode(ASTNode):
    def __init__(self, variable_name, line=None):
        super().__init__("BloomFunction", line=line)
        self.add_child(ASTNode("Identifier", variable_name, line=line))

class AppendNode(ASTNode):
    def __init__(self, elements, line=None):
        super().__init__("Append", line=line)
        for elem in elements:
            self.add_child(elem)

class InsertNode(ASTNode):
    def __init__(self, index, elements, line=None):
        super().__init__("Insert", line=line)
        self.add_child(index)
        for elem in elements:
            self.add_child(elem)

class RemoveNode(ASTNode):
    def __init__(self, value, index, line=None):
        super().__init__("Remove", line=line)
        self.add_child(ASTNode("Identifier", value, line=line))
        self.add_child(index)

class CastNode(ASTNode):
    def __init__(self, target_type, expression, line=None):
        super().__init__("TypeCast", line=line)
        self.add_child(ASTNode("TargetType", target_type, line=line))
        self.add_child(expression)


class ListAccessNode(ASTNode):
    def __init__(self, list_name, index_expr, line=None):
        super().__init__("ListAccess", line=line)
        self.add_child(ASTNode("ListName", list_name, line=line))
        self.add_child(index_expr)


class MemberAccessNode(ASTNode):
    """Represents bundle member access: p.age or p.addr.zip (nested)"""
    def __init__(self, object_name, member_name, line=None):
        super().__init__("MemberAccess", line=line)
        if isinstance(object_name, ASTNode):
            self.add_child(object_name)  # Nested MemberAccessNode for chained access
        else:
            self.add_child(ASTNode("Object", object_name, line=line))
        self.add_child(ASTNode("Member", member_name, line=line))


class ArrayMemberAccessNode(ASTNode):
    """Represents bundle array element member access: p[0].x"""
    def __init__(self, list_access_node, member_name, line=None):
        super().__init__("ArrayMemberAccess", line=line)
        self.add_child(list_access_node)
        self.add_child(ASTNode("Member", member_name, line=line))


class BundleDefinitionNode(ASTNode):
    """Represents a bundle (struct) type definition."""
    def __init__(self, bundle_name, members, line=None):
        super().__init__("BundleDefinition", line=line)
        self.bundle_name = bundle_name
        self.members = members  # dict: {member_name: member_type}

