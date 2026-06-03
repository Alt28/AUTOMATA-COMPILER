"""Final AST validation pass for GAL.

builder.py already catches many declaration/type issues while creating the AST.
This validator walks the finished AST and checks rules that are easier to see
from the tree structure, such as prune/skip placement.
"""

# AUTO: Imports names from another module.
from semantic.errors import SemanticError


# AUTO: Defines class `ASTValidator`.
class ASTValidator:

    # AUTO: Defines function `__init__`.
    def __init__(self):
        # GUIDE: Context counters tell checks if they are inside a loop,
        # switch, or function while walking nested AST nodes.
        # AUTO: Sets `self.errors`.
        self.errors = []
        # AUTO: Sets `self.warnings`.
        self.warnings = []
        # AUTO: Sets `self._in_loop`.
        self._in_loop = 0
        # AUTO: Sets `self._in_switch`.
        self._in_switch = 0
        # AUTO: Sets `self._in_function`.
        self._in_function = False
        # AUTO: Sets `self._current_func_type`.
        self._current_func_type = None


    # AUTO: Defines function `validate`.
    def validate(self, ast, symbol_table_data):
        # Start walking from the ProgramNode. Every checker can add messages
        # into self.errors; no errors means semantic validation succeeds.
        # LINE: Begin recursive semantic walk from the AST root.
        self._walk(ast)
        # LINE: Return validation result plus errors/warnings/symbol table.
        return {
            # LINE: success is true only when no semantic errors were collected.
            "success": len(self.errors) == 0,
            # AUTO: Executes this statement.
            "errors": self.errors,
            # AUTO: Executes this statement.
            "warnings": self.warnings,
            # AUTO: Executes this statement.
            "symbol_table": symbol_table_data,
            # AUTO: Executes this statement.
            "ast": ast,
        # AUTO: Closes the current grouped code/data.
        }


    # AUTO: Defines function `_walk`.
    def _walk(self, node):
        # GUIDE: Dynamic dispatch; Program calls _check_Program, Break calls
        # _check_Break, and unknown node types simply recurse into children.
        # LINE: Nothing to check for missing/empty AST node.
        if node is None:
            # AUTO: Returns this result to the caller.
            return
        # LINE: Find checker method based on node type, like _check_Break.
        handler = getattr(self, f'_check_{node.node_type}', None)
        # LINE: If checker exists, run that specific semantic rule.
        if handler:
            # AUTO: Calls `handler`.
            handler(node)
        # AUTO: Runs when previous condition did not pass.
        else:
            # LINE: Otherwise keep walking through this node's children.
            for child in getattr(node, 'children', []):
                # AUTO: Calls `self._walk`.
                self._walk(child)


    # AUTO: Defines function `_check_Program`.
    def _check_Program(self, node):
        # LINE: ProgramNode validates by checking each top-level child.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_VariableDeclaration`.
    def _check_VariableDeclaration(self, node):
        # LINE: VariableDeclaration must at least contain type and name.
        if len(node.children) < 2:
            # AUTO: Appends a value to a list.
            self.errors.append(
                # AUTO: Executes this statement.
                f"SEMANTIC error line {node.line}: Malformed variable declaration.")
        # LINE: Continue validating initializer/children.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_VariableDeclarationList`.
    def _check_VariableDeclarationList(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_SturdyDeclaration`.
    def _check_SturdyDeclaration(self, node):
        # AUTO: Checks this condition.
        if len(node.children) < 3:
            # AUTO: Appends a value to a list.
            self.errors.append(
                # AUTO: Executes this statement.
                f"SEMANTIC error line {node.line}: Fertile declaration must have type, name, and value.")
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_FunctionDeclaration`.
    def _check_FunctionDeclaration(self, node):
        # LINE: FunctionDeclaration must have a function name in node.value.
        if not node.value:
            # AUTO: Appends a value to a list.
            self.errors.append(
                # AUTO: Executes this statement.
                f"SEMANTIC error line {node.line}: Function declaration missing name.")
        # LINE: Save previous function context before entering this function.
        prev_in_func = self._in_function
        # AUTO: Sets `prev_func_type`.
        prev_func_type = self._current_func_type
        # LINE: Mark validator as currently inside a function.
        self._in_function = True
        # AUTO: Checks this condition.
        if node.children:
            # LINE: First child stores return type.
            self._current_func_type = node.children[0].value
        # LINE: Validate parameters/body/children inside the function.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)
        # LINE: Restore previous context after leaving function.
        self._in_function = prev_in_func
        # AUTO: Sets `self._current_func_type`.
        self._current_func_type = prev_func_type

    # AUTO: Defines function `_check_FunctionCall`.
    def _check_FunctionCall(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_Assignment`.
    def _check_Assignment(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_AssignmentList`.
    def _check_AssignmentList(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_BinaryOp`.
    def _check_BinaryOp(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_UnaryOp`.
    def _check_UnaryOp(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_Block`.
    def _check_Block(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_IfStatement`.
    def _check_IfStatement(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_ElseIfStatement`.
    def _check_ElseIfStatement(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_ElseStatement`.
    def _check_ElseStatement(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_ForLoop`.
    def _check_ForLoop(self, node):
        # Enter loop context so prune/skip inside this block are legal.
        # LINE: Increase loop depth before checking cultivate body.
        self._in_loop += 1
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)
        # Leave loop context after all nested children are checked.
        # LINE: Decrease loop depth after cultivate body is checked.
        self._in_loop -= 1

    # AUTO: Defines function `_check_WhileLoop`.
    def _check_WhileLoop(self, node):
        # Same context rule as cultivate: grow allows prune/skip inside.
        # LINE: Increase loop depth before checking grow body.
        self._in_loop += 1
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)
        # LINE: Decrease loop depth after grow body.
        self._in_loop -= 1

    # AUTO: Defines function `_check_DoWhileLoop`.
    def _check_DoWhileLoop(self, node):
        # AUTO: Adds into `self._in_loop`.
        self._in_loop += 1
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)
        # AUTO: Subtracts from `self._in_loop`.
        self._in_loop -= 1

    # AUTO: Defines function `_check_Switch`.
    def _check_Switch(self, node):
        # LINE: harvest/variety context allows prune inside switch cases.
        self._in_switch += 1
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)
        # LINE: Leave switch context after all cases are checked.
        self._in_switch -= 1

    # AUTO: Defines function `_check_Break`.
    def _check_Break(self, node):
        # prune is valid only while the walker is inside a loop or harvest.
        # LINE: If no loop/switch context, prune is illegal.
        if self._in_loop == 0 and self._in_switch == 0:
            # AUTO: Appends a value to a list.
            self.errors.append(
                # AUTO: Executes this statement.
                f"SEMANTIC error line {node.line}: 'prune' used outside a loop or switch.")

    # AUTO: Defines function `_check_Continue`.
    def _check_Continue(self, node):
        # skip is valid only while the walker is inside a loop.
        # LINE: If no loop context, skip is illegal.
        if self._in_loop == 0:
            # AUTO: Appends a value to a list.
            self.errors.append(
                # AUTO: Executes this statement.
                f"SEMANTIC error line {node.line}: 'skip' used outside a loop.")

    # AUTO: Defines function `_check_Return`.
    def _check_Return(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_PrintStatement`.
    def _check_PrintStatement(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_Condition`.
    def _check_Condition(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_Update`.
    def _check_Update(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_List`.
    def _check_List(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_ListAccess`.
    def _check_ListAccess(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_TypeCast`.
    def _check_TypeCast(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_MemberAccess`.
    def _check_MemberAccess(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_BundleDefinition`.
    def _check_BundleDefinition(self, node):
        # AUTO: Checks this condition.
        if not node.bundle_name:
            # AUTO: Appends a value to a list.
            self.errors.append(
                # AUTO: Executes this statement.
                f"SEMANTIC error line {node.line}: Bundle definition missing name.")

    # AUTO: Defines function `_check_Append`.
    def _check_Append(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_Insert`.
    def _check_Insert(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

    # AUTO: Defines function `_check_Remove`.
    def _check_Remove(self, node):
        # AUTO: Starts a loop over these values.
        for child in node.children:
            # AUTO: Calls `self._walk`.
            self._walk(child)

# AUTO: Defines function `validate_ast`.
def validate_ast(ast, symbol_table_data):
    # LINE: Create a fresh validator for this compile/run.
    validator = ASTValidator()
    # LINE: Run validator and return its result.
    return validator.validate(ast, symbol_table_data)
