
"""AST node classes shared by the parser, semantic validator, and interpreter.

Each class represents one language construct after parsing, for example a
VariableDeclarationNode, BinaryOpNode, FunctionCallNode, or WhileLoopNode.
"""


# AUTO: Defines class `ASTNode`.
class ASTNode:
    # AUTO: Defines function `__init__`.
    def __init__(self, node_type, value=None, line=None):
        # LINE: node_type tells semantic/interpreter what this AST node represents.
        self.node_type = node_type
        # LINE: value stores the node's main text/value, like an operator or name.
        self.value = value
        # LINE: children stores nested AST nodes under this node.
        self.children = []
        # LINE: parent points back to the surrounding AST node.
        self.parent = None
        # LINE: line stores the original source line for error messages.
        self.line = line

    # AUTO: Defines function `add_child`.
    def add_child(self, child):
        # GUIDE: Parent links let later stages know the surrounding construct,
        # for example water() can see whether it belongs to an assignment.
        # AUTO: Sets `child.parent`.
        child.parent = self
        # AUTO: Appends a value to a list.
        self.children.append(child)

    # AUTO: Defines function `print_tree`.
    def print_tree(self, level=0):
        # AUTO: Sets `indent`.
        indent = ' ' * (level * 3)
        # AUTO: Calls `print`.
        print(f"{indent}╚═{self.node_type}: {self.value if self.value else ''}")
        # AUTO: Starts a loop over these values.
        for child in self.children:
            # AUTO: Calls `child.print_tree`.
            child.print_tree(level + 1)
        

# AUTO: Defines class `ProgramNode`.
class ProgramNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, line=None):
        # LINE: ProgramNode is the root container for the whole AST.
        super().__init__("Program", line=line)

# AUTO: Defines class `VariableDeclarationNode`.
class VariableDeclarationNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, var_type, var_name, value=None, line=None):
        # LINE: VariableDeclaration represents code like seed x = 10;
        super().__init__("VariableDeclaration", line=line)
        # LINE: First child stores declared type.
        self.add_child(ASTNode("Type", var_type, line=line))
        # LINE: Second child stores variable name.
        self.add_child(ASTNode("Identifier", var_name, line=line))
        # AUTO: Checks this condition.
        if value:
            # LINE: Optional third child stores initializer expression.
            self.add_child(value)

# AUTO: Defines class `AssignmentNode`.
class AssignmentNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, target, value, line=None):
        # LINE: Assignment represents code like x = y + 1;
        super().__init__("Assignment", line=line)
        # AUTO: Checks this condition.
        if isinstance(target, str):
            # LINE: Simple target names are wrapped as Identifier nodes.
            self.add_child(ASTNode("Identifier", target, line=line))
        # AUTO: Runs when previous condition did not pass.
        else:
            # LINE: Complex targets are already AST nodes, like array/member access.
            self.add_child(target)
        # LINE: Second child stores the RHS expression/value.
        self.add_child(value)
        

# AUTO: Defines class `BinaryOpNode`.
class BinaryOpNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, left, operator, right, line=None):
        # LINE: BinaryOp stores operator in value with left/right children.
        super().__init__("BinaryOp", operator, line=line)
        # AUTO: Calls `self.add_child`.
        self.add_child(left)
        # AUTO: Calls `self.add_child`.
        self.add_child(right)

# AUTO: Defines class `FunctionDeclarationNode`.
class FunctionDeclarationNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, return_type, name, params, line=None):
        # LINE: FunctionDeclaration stores function name in value.
        super().__init__("FunctionDeclaration", name, line=line)
        # LINE: First child stores return type.
        self.add_child(ASTNode("ReturnType", return_type, line=line))
        # LINE: Second child stores parameters.
        self.add_child(params)

# AUTO: Defines class `FunctionCallNode`.
class FunctionCallNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, name, args, line=None):
        # LINE: FunctionCall stores called function name in value.
        super().__init__("FunctionCall", name, line=line)
        # LINE: Each argument becomes a child.
        for arg in args:
            # AUTO: Calls `self.add_child`.
            self.add_child(arg)

# AUTO: Defines class `IfStatementNode`.
class IfStatementNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, condition, line=None):
        # AUTO: Sets `super().__init__("IfStatement", line`.
        super().__init__("IfStatement", line=line)
        # AUTO: Calls `self.add_child`.
        self.add_child(condition)

# AUTO: Defines class `ForLoopNode`.
class ForLoopNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, initialization, condition, update, line=None):
        # AUTO: Sets `super().__init__("ForLoop", line`.
        super().__init__("ForLoop", line=line)  
        # AUTO: Calls `self.add_child`.
        self.add_child(initialization)
        # AUTO: Calls `self.add_child`.
        self.add_child(condition)
        # AUTO: Calls `self.add_child`.
        self.add_child(update)

# AUTO: Defines class `WhileLoopNode`.
class WhileLoopNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, condition, line=None):
        # AUTO: Sets `super().__init__("WhileLoop", line`.
        super().__init__("WhileLoop", line=line)  
        # AUTO: Calls `self.add_child`.
        self.add_child(condition)

# AUTO: Defines class `DoWhileLoopNode`.
class DoWhileLoopNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, condition, line=None):
        # AUTO: Sets `super().__init__("DoWhileLoop", line`.
        super().__init__("DoWhileLoop", line=line)

# AUTO: Defines class `PrintNode`.
class PrintNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, args, line=None):
        # AUTO: Sets `super().__init__("PrintStatement", line`.
        super().__init__("PrintStatement", line=line) 
        # AUTO: Starts a loop over these values.
        for arg in args:
            # AUTO: Calls `self.add_child`.
            self.add_child(arg)

# AUTO: Defines class `UnaryOpNode`.
class UnaryOpNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, operator, operand, position="pre", line=None):
        # AUTO: Sets `super().__init__("UnaryOp", operator, line`.
        super().__init__("UnaryOp", operator, line=line)
        # AUTO: Sets `self.position`.
        self.position = position
        # AUTO: Calls `self.add_child`.
        self.add_child(operand)

# AUTO: Defines class `FertileDeclarationNode`.
class FertileDeclarationNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, var_type, var_name, value, line=None):
        # AUTO: Sets `super().__init__("SturdyDeclaration", line`.
        super().__init__("SturdyDeclaration", line=line)
        # AUTO: Sets `self.add_child(ASTNode("Type", var_type, line`.
        self.add_child(ASTNode("Type", var_type, line=line))
        # AUTO: Sets `self.add_child(ASTNode("Identifier", var_name, line`.
        self.add_child(ASTNode("Identifier", var_name, line=line))
        # AUTO: Calls `self.add_child`.
        self.add_child(value)

# AUTO: Defines class `ReturnNode`.
class ReturnNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, return_value=None, line=None):
        # AUTO: Sets `super().__init__("Return", line`.
        super().__init__("Return", line=line)
        # AUTO: Checks this condition.
        if return_value:
            # AUTO: Calls `self.add_child`.
            self.add_child(return_value)

# AUTO: Defines class `UpdateNode`.
class UpdateNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, operator, operand, prefix = True, line=None):
        # AUTO: Sets `super().__init__("Update", line`.
        super().__init__("Update", line=line)
        # AUTO: Sets `self.prefix`.
        self.prefix = prefix
        # AUTO: Calls `self.add_child`.
        self.add_child(operand)
        # AUTO: Calls `self.add_child`.
        self.add_child(operator)

# AUTO: Defines class `SwitchNode`.
class SwitchNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, expression, cases, default_case, line=None):
        # AUTO: Sets `super().__init__("Switch", line`.
        super().__init__("Switch", line=line)
        # AUTO: Calls `self.add_child`.
        self.add_child(expression)
        # AUTO: Starts a loop over these values.
        for case in cases:
            # AUTO: Calls `self.add_child`.
            self.add_child(case)
        # AUTO: Checks this condition.
        if default_case is not None:
            # AUTO: Calls `self.add_child`.
            self.add_child(default_case)

# AUTO: Defines class `ContinueNode`.
class ContinueNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, line=None):
        # AUTO: Sets `super().__init__("Continue", line`.
        super().__init__("Continue", line=line)

# AUTO: Defines class `BreakNode`.
class BreakNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, line=None):
        # AUTO: Sets `super().__init__("Break", line`.
        super().__init__("Break", line=line)

# AUTO: Defines class `ListNode`.
class ListNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, line=None, elements=None):
        # AUTO: Sets `super().__init__("List", line`.
        super().__init__("List", line=line)
        # AUTO: Sets `self.elements`.
        self.elements = elements or []
        # AUTO: Starts a loop over these values.
        for element in self.elements:
            # AUTO: Calls `self.add_child`.
            self.add_child(element)

# AUTO: Defines class `SoilNode`.
class SoilNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, variable_name, line=None):
        # AUTO: Sets `super().__init__("SoilFunction", line`.
        super().__init__("SoilFunction", line=line)
        # AUTO: Sets `self.add_child(ASTNode("Identifier", variable_name, line`.
        self.add_child(ASTNode("Identifier", variable_name, line=line))

# AUTO: Defines class `BloomNode`.
class BloomNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, variable_name, line=None):
        # AUTO: Sets `super().__init__("BloomFunction", line`.
        super().__init__("BloomFunction", line=line)
        # AUTO: Sets `self.add_child(ASTNode("Identifier", variable_name, line`.
        self.add_child(ASTNode("Identifier", variable_name, line=line))

# AUTO: Defines class `AppendNode`.
class AppendNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, elements, line=None):
        # AUTO: Sets `super().__init__("Append", line`.
        super().__init__("Append", line=line)
        # AUTO: Starts a loop over these values.
        for elem in elements:
            # AUTO: Calls `self.add_child`.
            self.add_child(elem)

# AUTO: Defines class `InsertNode`.
class InsertNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, index, elements, line=None):
        # AUTO: Sets `super().__init__("Insert", line`.
        super().__init__("Insert", line=line)
        # AUTO: Calls `self.add_child`.
        self.add_child(index)
        # AUTO: Starts a loop over these values.
        for elem in elements:
            # AUTO: Calls `self.add_child`.
            self.add_child(elem)

# AUTO: Defines class `RemoveNode`.
class RemoveNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, value, index, line=None):
        # AUTO: Sets `super().__init__("Remove", line`.
        super().__init__("Remove", line=line)
        # AUTO: Sets `self.add_child(ASTNode("Identifier", value, line`.
        self.add_child(ASTNode("Identifier", value, line=line))
        # AUTO: Calls `self.add_child`.
        self.add_child(index)

# AUTO: Defines class `CastNode`.
class CastNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, target_type, expression, line=None):
        # AUTO: Sets `super().__init__("TypeCast", line`.
        super().__init__("TypeCast", line=line)
        # AUTO: Sets `self.add_child(ASTNode("TargetType", target_type, line`.
        self.add_child(ASTNode("TargetType", target_type, line=line))
        # AUTO: Calls `self.add_child`.
        self.add_child(expression)


# AUTO: Defines class `ListAccessNode`.
class ListAccessNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, list_name, index_expr, line=None):
        # AUTO: Sets `super().__init__("ListAccess", line`.
        super().__init__("ListAccess", line=line)
        # AUTO: Sets `self.add_child(ASTNode("ListName", list_name, line`.
        self.add_child(ASTNode("ListName", list_name, line=line))
        # AUTO: Calls `self.add_child`.
        self.add_child(index_expr)


# AUTO: Defines class `MemberAccessNode`.
class MemberAccessNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, object_name, member_name, line=None):
        # AUTO: Sets `super().__init__("MemberAccess", line`.
        super().__init__("MemberAccess", line=line)
        # AUTO: Checks this condition.
        if isinstance(object_name, ASTNode):
            # AUTO: Calls `self.add_child`.
            self.add_child(object_name)
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Sets `self.add_child(ASTNode("Object", object_name, line`.
            self.add_child(ASTNode("Object", object_name, line=line))
        # AUTO: Sets `self.add_child(ASTNode("Member", member_name, line`.
        self.add_child(ASTNode("Member", member_name, line=line))


# AUTO: Defines class `ArrayMemberAccessNode`.
class ArrayMemberAccessNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, list_access_node, member_name, line=None):
        # AUTO: Sets `super().__init__("ArrayMemberAccess", line`.
        super().__init__("ArrayMemberAccess", line=line)
        # AUTO: Calls `self.add_child`.
        self.add_child(list_access_node)
        # AUTO: Sets `self.add_child(ASTNode("Member", member_name, line`.
        self.add_child(ASTNode("Member", member_name, line=line))


# AUTO: Defines class `BundleDefinitionNode`.
class BundleDefinitionNode(ASTNode):
    # AUTO: Defines function `__init__`.
    def __init__(self, bundle_name, members, line=None):
        # AUTO: Sets `super().__init__("BundleDefinition", line`.
        super().__init__("BundleDefinition", line=line)
        # AUTO: Sets `self.bundle_name`.
        self.bundle_name = bundle_name
        # AUTO: Sets `self.members`.
        self.members = members

