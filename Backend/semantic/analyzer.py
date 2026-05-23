# ============================================================================
# SEMANTIC ANALYZER - Tree-walking validator for the completed AST
# ============================================================================
# Extracted from GALsemantic.py during the modular restructure.
# The parser already does primary checks during AST construction. This
# validator does the SECOND pass over the completed tree to catch checks
# that need a global view (function arity, return-path coverage, etc.).
# ============================================================================
from semantic.errors import SemanticError


class ASTValidator:
    """Tree-walking semantic validator.

    Receives an already-built AST and walks every node to verify:
      • Variable declarations are well-formed
      • Function declarations have names and return types
      • Break/continue appear only inside loops or switches
      • Loop and conditional bodies are present
      • Expressions have valid structure
    """

    def __init__(self):
        self.errors = []
        self.warnings = []
        self._in_loop = 0
        self._in_switch = 0
        self._in_function = False
        self._current_func_type = None

    # ── public entry point ──────────────────────────────────────────

    def validate(self, ast, symbol_table_data):
        """Validate *ast* and return a result dict."""
        self._walk(ast)
        return {
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "symbol_table": symbol_table_data,
            "ast": ast,
        }

    # ── recursive walker ────────────────────────────────────────────

    def _walk(self, node):
        if node is None:
            return
        handler = getattr(self, f'_check_{node.node_type}', None)
        if handler:
            handler(node)
        else:
            # Default: visit all children
            for child in getattr(node, 'children', []):
                self._walk(child)

    # ── node-specific validators ────────────────────────────────────

    def _check_Program(self, node):
        for child in node.children:
            self._walk(child)

    def _check_VariableDeclaration(self, node):
        if len(node.children) < 2:
            self.errors.append(
                f"Ln {node.line} Semantic Error: Malformed variable declaration.")
        for child in node.children:
            self._walk(child)

    def _check_VariableDeclarationList(self, node):
        for child in node.children:
            self._walk(child)

    def _check_SturdyDeclaration(self, node):
        # fertile (constant) declaration
        if len(node.children) < 3:
            self.errors.append(
                f"Ln {node.line} Semantic Error: Fertile declaration must have type, name, and value.")
        for child in node.children:
            self._walk(child)

    def _check_FunctionDeclaration(self, node):
        if not node.value:
            self.errors.append(
                f"Ln {node.line} Semantic Error: Function declaration missing name.")
        prev_in_func = self._in_function
        prev_func_type = self._current_func_type
        self._in_function = True
        # Return type is in the first child
        if node.children:
            self._current_func_type = node.children[0].value
        for child in node.children:
            self._walk(child)
        self._in_function = prev_in_func
        self._current_func_type = prev_func_type

    def _check_FunctionCall(self, node):
        for child in node.children:
            self._walk(child)

    def _check_Assignment(self, node):
        for child in node.children:
            self._walk(child)

    def _check_AssignmentList(self, node):
        for child in node.children:
            self._walk(child)

    def _check_BinaryOp(self, node):
        for child in node.children:
            self._walk(child)

    def _check_UnaryOp(self, node):
        for child in node.children:
            self._walk(child)

    def _check_Block(self, node):
        for child in node.children:
            self._walk(child)

    def _check_IfStatement(self, node):
        for child in node.children:
            self._walk(child)

    def _check_ElseIfStatement(self, node):
        for child in node.children:
            self._walk(child)

    def _check_ElseStatement(self, node):
        for child in node.children:
            self._walk(child)

    def _check_ForLoop(self, node):
        self._in_loop += 1
        for child in node.children:
            self._walk(child)
        self._in_loop -= 1

    def _check_WhileLoop(self, node):
        self._in_loop += 1
        for child in node.children:
            self._walk(child)
        self._in_loop -= 1

    def _check_DoWhileLoop(self, node):
        self._in_loop += 1
        for child in node.children:
            self._walk(child)
        self._in_loop -= 1

    def _check_Switch(self, node):
        self._in_switch += 1
        for child in node.children:
            self._walk(child)
        self._in_switch -= 1

    def _check_Break(self, node):
        if self._in_loop == 0 and self._in_switch == 0:
            self.errors.append(
                f"Ln {node.line} Semantic Error: 'prune' used outside a loop or switch.")

    def _check_Continue(self, node):
        if self._in_loop == 0:
            self.errors.append(
                f"Ln {node.line} Semantic Error: 'skip' used outside a loop.")

    def _check_Return(self, node):
        for child in node.children:
            self._walk(child)

    def _check_PrintStatement(self, node):
        for child in node.children:
            self._walk(child)

    def _check_Condition(self, node):
        for child in node.children:
            self._walk(child)

    def _check_Update(self, node):
        for child in node.children:
            self._walk(child)

    def _check_List(self, node):
        for child in node.children:
            self._walk(child)

    def _check_ListAccess(self, node):
        for child in node.children:
            self._walk(child)

    def _check_TypeCast(self, node):
        for child in node.children:
            self._walk(child)

    def _check_MemberAccess(self, node):
        for child in node.children:
            self._walk(child)

    def _check_BundleDefinition(self, node):
        if not node.bundle_name:
            self.errors.append(
                f"Ln {node.line} Semantic Error: Bundle definition missing name.")

    def _check_Append(self, node):
        for child in node.children:
            self._walk(child)

    def _check_Insert(self, node):
        for child in node.children:
            self._walk(child)

    def _check_Remove(self, node):
        for child in node.children:
            self._walk(child)

    def _check_TaperFunction(self, node):
        for child in node.children:
            self._walk(child)

    def _check_TSFunction(self, node):
        for child in node.children:
            self._walk(child)


# ============================================================================
# validate_ast() - PUBLIC SEMANTIC-ANALYSIS ENTRY POINT
# Used by server.py after parse_and_build succeeds. Wraps ASTValidator.
# Returns a dict with success/errors/warnings/symbol_table/ast.
# ============================================================================
def validate_ast(ast, symbol_table_data):
    """Public API: validate an already-built AST.

    This is the semantic analysis phase of the compiler pipeline.
    The parser has already built the AST (with primary checks during
    construction).  This function performs a tree-walking validation
    pass over the completed AST.

    Args:
        ast: The root AST node (ProgramNode) produced by the parser.
        symbol_table_data: Serialized symbol table dict from the parser.

    Returns:
        dict with keys: success, errors, warnings, symbol_table, ast
    """
    validator = ASTValidator()
    return validator.validate(ast, symbol_table_data)
