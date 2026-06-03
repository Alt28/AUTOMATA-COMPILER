"""AST builder and early semantic checks for GAL.

parser.py proves token order first. This file then builds AST nodes, fills the
symbol table, and catches declaration/type errors that need context.
"""

# AUTO: Imports a module used by this file.
import copy
# AUTO: Imports a module used by this file.
import re

# AUTO: Imports names from another module.
from shared.tokens import *  # noqa: F401,F403 - TT_* constants used throughout parse_*
# AUTO: Imports names from another module.
from semantic.errors import SemanticError
# AUTO: Imports names from another module.
from shared.ast_nodes import *  # noqa: F401,F403 - all AST node classes
# AUTO: Imports names from another module.
from semantic.symbol_table import SymbolTable


# AUTO: Defines class `SemanticAnalyzer`.
class SemanticAnalyzer:
    # AUTO: Defines function `__init__`.
    def __init__(self, symbol_table):
        # AUTO: Sets `self.symbol_table`.
        self.symbol_table = symbol_table
        # AUTO: Sets `self.visited_nodes`.
        self.visited_nodes = set()


# AUTO: Sets `symbol_table`.
symbol_table = SymbolTable()
# AUTO: Sets `semantic_analyzer`.
semantic_analyzer = SemanticAnalyzer(symbol_table)
# AUTO: Sets `context_stack`.
context_stack = []


# AUTO: Defines function `build_ast`.
def build_ast(tokens):
    # GUIDE: Entry point after syntax success; reset compiler state, then build the
    # ProgramNode from globals, pollinate functions, and root().
    # root is the top AST node. Every global declaration/function/root becomes
    # a child of this ProgramNode.
    # LINE: Create the main AST container that will hold the whole program.
    root = ProgramNode()

    # Reset symbol table state so each compile/run starts clean.
    # LINE: Clear global variables from any previous run.
    symbol_table.variables = {}
    # LINE: Clear stored functions from any previous run.
    symbol_table.functions = {}
    # LINE: Reset scope stack to one global scope.
    symbol_table.scopes = [{}] 
    # LINE: Clear per-function variable records.
    symbol_table.function_variables = {}
    # LINE: Clear bundle/struct type definitions.
    symbol_table.bundle_types = {}
    # LINE: Reset builder context tracking.
    context_stack = []
    # LINE: index points to the current token being converted to AST.
    index = 0
    # LINE: No function is active before parsing top-level code.
    symbol_table.current_func_name = None
    
    # LINE: Walk through all tokens until EOF/global parsing is finished.
    while index < len(tokens):
        # token is the current token being converted into an AST construct.
        # index moves forward as each parse_* helper consumes tokens.
        # LINE: Read the current token at this index.
        token = tokens[index]

        # LINE: Ignore extra semicolons at global level.
        if token.type == ";":
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Skips to the next loop iteration.
            continue
        
        # LINE: Top-level data type means global variable declaration.
        if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch"}:
            # Global variable declaration such as: seed x = 10;
            # LINE: Save declared type, such as seed or vine.
            id_type = token.value
            # LINE: Move to the variable name token.
            index += 1
            # LINE: Variable declaration must be followed by an identifier.
            if tokens[index].type != "id":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Invalid variable declaration.", token.line)
            # LINE: Save the variable name.
            id_name = tokens[index].value
            # LINE: Move after the identifier before parsing initializer/array tail.
            index += 1
            # LINE: Build a VariableDeclarationNode and update index to the next token.
            node, index = parse_variable(tokens, index, id_name, id_type) 

            # LINE: Add the global declaration node under ProgramNode.
            if node:
                # AUTO: Calls `root.add_child`.
                root.add_child(node)

        # LINE: empty starts an empty-return function declaration.
        elif tokens[index].value == "empty":
            # Empty-return function declaration without pollinate prefix.
            # AUTO: Adds into `index`.
            index += 1
            # LINE: Function name must come after empty.
            if tokens[index].type == "id":
                # AUTO: Sets `func_name`.
                func_name = tokens[index].value
                # AUTO: Sets `func_type`.
                func_type = "empty"
                # LINE: Build the function AST node.
                node, index = parse_function(tokens, index, func_name, func_type)
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
            
            # LINE: Store function declaration under ProgramNode.
            if node:
                # AUTO: Calls `root.add_child`.
                root.add_child(node)
            
        # LINE: pollinate starts a typed function declaration.
        elif tokens[index].value in {"pollinate"}:
            # Function declaration such as: pollinate seed add(seed a, seed b) { ... }
            # LINE: Move from pollinate to the return type.
            index += 1
            # LINE: Built-in return type path.
            if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty"}:
                # AUTO: Sets `id_type`.
                id_type = tokens[index].value
                # AUTO: Adds into `index`.
                index += 1
                # LINE: Function return type must be followed by function name.
                if tokens[index].type != "id":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
                # AUTO: Sets `id_name`.
                id_name = tokens[index].value
                # AUTO: Adds into `index`.
                index += 1
                # LINE: Parse parameters and function body.
                node, index = parse_function(tokens, index, id_name, id_type)

                # LINE: Store function declaration under ProgramNode.
                if node:
                    # AUTO: Calls `root.add_child`.
                    root.add_child(node)

            # LINE: Bundle return type path, like pollinate Student make().
            elif tokens[index].type == "id" and tokens[index].value in symbol_table.bundle_types:
                # AUTO: Sets `id_type`.
                id_type = tokens[index].value
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Checks this condition.
                if tokens[index].type != "id":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
                # AUTO: Sets `id_name`.
                id_name = tokens[index].value
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Sets `node, index`.
                node, index = parse_function(tokens, index, id_name, id_type)

                # AUTO: Checks this condition.
                if node:
                    # AUTO: Calls `root.add_child`.
                    root.add_child(node)

            # AUTO: Runs when previous condition did not pass.
            else: 
                # LINE: pollinate must be followed by a valid return type.
                raise SemanticError(f"Semantic Error: Expected data type for function declaration after 'pollinate'.", tokens[index].line)

        # LINE: fertile starts a constant declaration.
        elif token.value == "fertile":
            # Constant/global fertile declaration.
            # AUTO: Sets `node, index`.
            node, index = parse_fertile(tokens, index)
            # AUTO: Checks this condition.
            if node:
                # AUTO: Calls `root.add_child`.
                root.add_child(node)

        # LINE: Raw identifier at global level is invalid unless handled by another rule.
        elif token.value == "identifier":
            # AUTO: Checks this condition.
            if isinstance(symbol_table.lookup_variable(token.value), str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Variable '{token.value}' used before declaration.", token.line)
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Invalid global statement.", token.line)

        # LINE: root token starts the required main function.
        elif token.value in {"root"}:
            # AUTO: Sets `func_name`.
            func_name = token.value
            # AUTO: Sets `func_type`.
            func_type = "empty"
            # LINE: Build root as an empty-return FunctionDeclarationNode.
            node, index = parse_function(tokens, index, func_name, func_type)

            # AUTO: Checks this condition.
            if node:
                # AUTO: Calls `root.add_child`.
                root.add_child(node)

        # LINE: bundle either defines a bundle type or declares a bundle variable.
        elif token.value == "bundle":
            # AUTO: Sets `bundle_name`.
            bundle_name = tokens[index + 1].value
            # AUTO: Adds into `index`.
            index += 2

            # LINE: bundle Name { ... } defines a new bundle type.
            if tokens[index].type == "{":
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Sets `members`.
                members = {}
                # LINE: Collect bundle members until closing brace.
                while tokens[index].type != "}":
                    # AUTO: Checks this condition.
                    if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch"}:
                        # AUTO: Sets `member_type`.
                        member_type = tokens[index].value
                        # AUTO: Sets `member_name`.
                        member_name = tokens[index + 1].value
                        # AUTO: Checks this condition.
                        if member_name in members:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Duplicate member '{member_name}' in bundle '{bundle_name}'.", tokens[index].line)
                        # AUTO: Sets `members[member_name]`.
                        members[member_name] = member_type
                        # AUTO: Adds into `index`.
                        index += 2
                        # AUTO: Checks this condition.
                        if tokens[index].type == ";":
                            # AUTO: Adds into `index`.
                            index += 1
                    # AUTO: Checks the next alternate condition.
                    elif tokens[index].type == "id" and tokens[index].value in symbol_table.bundle_types:
                        # AUTO: Sets `member_type`.
                        member_type = tokens[index].value
                        # AUTO: Sets `member_name`.
                        member_name = tokens[index + 1].value
                        # AUTO: Checks this condition.
                        if member_name in members:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Duplicate member '{member_name}' in bundle '{bundle_name}'.", tokens[index].line)
                        # AUTO: Sets `members[member_name]`.
                        members[member_name] = member_type
                        # AUTO: Adds into `index`.
                        index += 2
                        # AUTO: Checks this condition.
                        if tokens[index].type == ";":
                            # AUTO: Adds into `index`.
                            index += 1
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Invalid member type '{tokens[index].value}' in bundle definition.", tokens[index].line)
                # AUTO: Adds into `index`.
                index += 1

                # AUTO: Checks this condition.
                if bundle_name in symbol_table.bundle_types:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Bundle type '{bundle_name}' already defined.", token.line)

                # LINE: Save the bundle type into the symbol table.
                symbol_table.bundle_types[bundle_name] = members
                # LINE: Create AST node for the bundle definition.
                node = BundleDefinitionNode(bundle_name, members, line=token.line)
                # AUTO: Calls `root.add_child`.
                root.add_child(node)

            # AUTO: Runs when previous condition did not pass.
            else:
                # LINE: bundle Name var; declares a variable of bundle type Name.
                var_name = tokens[index].value
                # AUTO: Adds into `index`.
                index += 1

                # AUTO: Checks this condition.
                if bundle_name not in symbol_table.bundle_types:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Bundle type '{bundle_name}' is not defined.", token.line)

                # AUTO: Sets `members`.
                members = symbol_table.bundle_types[bundle_name]
                # AUTO: Sets `_defaults`.
                _defaults = {"seed": 0, "tree": 0.0, "leaf": '', "vine": "", "branch": False}
                # AUTO: Sets `bundle_value`.
                bundle_value = {name: _defaults.get(typ, None) for name, typ in members.items()}

                # AUTO: Sets `error`.
                error = symbol_table.declare_variable(var_name, bundle_name, value=bundle_value)
                # AUTO: Checks this condition.
                if isinstance(error, str):
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(error, token.line)

                # AUTO: Sets `node`.
                node = VariableDeclarationNode(bundle_name, var_name, line=token.line)
                # AUTO: Calls `root.add_child`.
                root.add_child(node)

        # AUTO: Runs when previous condition did not pass.
        else:
            # LINE: Any other top-level token is invalid except EOF.
            if token.type not in {"EOF"}:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Invalid token '{token.value}' used in global statement.", token.line)
            # AUTO: Stops the nearest loop.
            break
    
    # LINE: Return the complete ProgramNode AST to parser.py.
    return root

# AUTO: Defines function `parse_functionOrVariable`.
def parse_functionOrVariable(tokens, index):
    # AUTO: Sets `id_type`.
    id_type = tokens[index].value
    # AUTO: Sets `line`.
    line = tokens[index].line

    # AUTO: Checks this condition.
    if tokens[index + 1].type == "id" or tokens[index + 1].value == "root":
        # AUTO: Sets `id_name`.
        id_name = tokens[index + 1].value
        # AUTO: Adds into `index`.
        index += 2
    
        # AUTO: Checks this condition.
        if tokens[index].type == "(":
            # AUTO: Sets `node, index`.
            node, index = parse_function(tokens, index, id_name, id_type)
        
        # AUTO: Checks the next alternate condition.
        elif tokens[index].type == "=":
            # AUTO: Sets `node, index`.
            node, index = parse_variable(tokens, index, id_name, id_type) 
        
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Sets `error`.
            error = f"Semantic Error: Invalid function or variable declaration."
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(error, line)
        
        # AUTO: Sets `node.line`.
        node.line = line
        # AUTO: Returns this result to the caller.
        return node, index
    
    # AUTO: Returns this result to the caller.
    return None, index

# AUTO: Defines function `parse_function`.
def parse_function(tokens, index, func_name, func_type):
    # LINE: Start parsing a function/root declaration from the current index.
    line = tokens[index].line

    # LINE: Remember which function is being built for declaration checks.
    symbol_table.current_func_name = func_name

    # LINE: Function names cannot be duplicated.
    if func_name in symbol_table.functions:
        # AUTO: Sets `error`.
        error = f"Semantic Error: '{func_name}' already declared."
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(error, tokens[index].line)
    
    # AUTO: Checks the next alternate condition.
    elif func_name in symbol_table.variables:
        # AUTO: Sets `error`.
        error = f"Semantic Error: '{func_name}' already declared."
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(error, tokens[index].line)

    # LINE: root has special rules: no parameters and empty return.
    if func_name in {"root"}:
        # LINE: Create a new function scope for declarations inside root.
        symbol_table.enter_scope()
        # AUTO: Adds into `index`.
        index += 1

        # LINE: root must have parentheses.
        if tokens[index].type == "(":
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Checks this condition.
            if tokens[index].type != ")":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: {func_name}() should not have parameters.", line)
            # AUTO: Adds into `index`.
            index += 1
        # AUTO: Checks the next alternate condition.
        elif func_name == "root":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError("Semantic Error: Missing () for root function declaration.", line)

        # LINE: root has an empty parameter container.
        params_node = ASTNode("Parameters")
        # LINE: Create FunctionDeclarationNode for root.
        func_node = FunctionDeclarationNode(func_type, func_name, params_node)

    # AUTO: Runs when previous condition did not pass.
    else:
        # LINE: Normal pollinate functions must start with '(' after the name.
        if tokens[index].type != "(":
            # AUTO: Sets `error`.
            error = f"Semantic Error: Missing () for function declaration."
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(error, line)

        # AUTO: Sets `params_node`.
        params_node = ASTNode("Parameters")
        # AUTO: Sets `line`.
        line = tokens[index].line
        # AUTO: Calls `symbol_table.enter_scope`.
        symbol_table.enter_scope()

        # AUTO: Repeats while this condition is true.
        while tokens[index].type != ")":
            # AUTO: Checks this condition.
            if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty"}:
                # AUTO: Sets `param_type`.
                param_type = tokens[index].value
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Checks this condition.
                if tokens[index].type == "id":
                    # AUTO: Sets `param_name`.
                    param_name = tokens[index].value
                    # AUTO: Sets `param_node`.
                    param_node = ASTNode("Parameter")
                    # AUTO: Calls `param_node.add_child`.
                    param_node.add_child(ASTNode("Type", param_type))
                    # AUTO: Calls `param_node.add_child`.
                    param_node.add_child(ASTNode("Identifier", param_name))
                    # AUTO: Adds into `index`.
                    index += 1

                    # AUTO: Sets `is_list`.
                    is_list = False
                    # AUTO: Checks this condition.
                    if tokens[index].type == "[":
                        # AUTO: Adds into `index`.
                        index += 1
                        # AUTO: Checks this condition.
                        if tokens[index].type != "]":
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Expected ']' after '[' in array parameter.", line)
                        # AUTO: Adds into `index`.
                        index += 1
                        # AUTO: Sets `is_list`.
                        is_list = True
                        # AUTO: Calls `param_node.add_child`.
                        param_node.add_child(ASTNode("ArrayParam", "true"))

                    # AUTO: Calls `params_node.add_child`.
                    params_node.add_child(param_node)
                    # AUTO: Sets `error`.
                    error = symbol_table.declare_variable(param_name, param_type, is_list=is_list)
                    # AUTO: Checks this condition.
                    if error:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(error, line)

                    # AUTO: Checks this condition.
                    if tokens[index].type == ",":
                        # AUTO: Adds into `index`.
                        index += 1

                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Sets `error`.
                    error = f"Semantic Error: Invalid parameter declaration."
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(error, line)

            # AUTO: Checks the next alternate condition.
            elif tokens[index].type == "id" and tokens[index].value in symbol_table.bundle_types:
                # AUTO: Sets `param_type`.
                param_type = tokens[index].value
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Checks this condition.
                if tokens[index].type == "id":
                    # AUTO: Sets `param_name`.
                    param_name = tokens[index].value
                    # AUTO: Sets `param_node`.
                    param_node = ASTNode("Parameter")
                    # AUTO: Calls `param_node.add_child`.
                    param_node.add_child(ASTNode("Type", param_type))
                    # AUTO: Calls `param_node.add_child`.
                    param_node.add_child(ASTNode("Identifier", param_name))
                    # AUTO: Calls `params_node.add_child`.
                    params_node.add_child(param_node)
                    # AUTO: Sets `error`.
                    error = symbol_table.declare_variable(param_name, param_type)
                    # AUTO: Checks this condition.
                    if error:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(error, line)
                    # AUTO: Adds into `index`.
                    index += 1

                    # AUTO: Checks this condition.
                    if tokens[index].type == ",":
                        # AUTO: Adds into `index`.
                        index += 1
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Sets `error`.
                    error = f"Semantic Error: Invalid parameter declaration."
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(error, line)

            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Adds into `index`.
                index += 1

        # AUTO: Calls `symbol_table.declare_function`.
        symbol_table.declare_function(func_name, func_type, params_node.children)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `func_node`.
        func_node = FunctionDeclarationNode(func_type, func_name, params_node)

    # AUTO: Checks this condition.
    if tokens[index].type == "{":
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `block_node`.
        block_node = ASTNode("Block")
        
        # AUTO: Repeats while this condition is true.
        while tokens[index].type != "}":
            # AUTO: Sets `stmt, index`.
            stmt, index = parse_statement(tokens, index, func_type)
            # AUTO: Checks this condition.
            if stmt:
                # AUTO: Calls `block_node.add_child`.
                block_node.add_child(stmt)

        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Calls `func_node.add_child`.
        func_node.add_child(block_node)
        # AUTO: Calls `symbol_table.exit_scope`.
        symbol_table.exit_scope()
        # AUTO: Sets `symbol_table.current_func_name`.
        symbol_table.current_func_name = None
    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Sets `error`.
        error = f"Semantic Error: Function body must be enclosed in curly braces."
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(error, line)

    # AUTO: Returns this result to the caller.
    return func_node, index

# AUTO: Defines function `parse_variable`.
def parse_variable(tokens, index, var_name, var_type):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Sets `var_nodes`.
    var_nodes = []

    # AUTO: Repeats while this condition is true.
    while True:
        # AUTO: Sets `global_var`.
        global_var = symbol_table.variables.get(var_name)
        # AUTO: Checks this condition.
        if global_var and global_var.get("is_fertile"):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-declared.", line)

        # AUTO: Sets `is_list`.
        is_list = False

        # AUTO: Sets `var_node`.
        var_node = VariableDeclarationNode(var_type, var_name, line=line)

        # AUTO: Checks this condition.
        if tokens[index].type == "=":
            # AUTO: Adds into `index`.
            index += 1

            # AUTO: Checks this condition.
            if tokens[index].type == "[":
                # AUTO: Sets `is_list`.
                is_list = True
                # AUTO: Sets `value_node, index`.
                value_node, index = parse_list(tokens, index, var_type)
                # AUTO: Calls `var_node.add_child`.
                var_node.add_child(value_node)

            # AUTO: Checks the next alternate condition.
            elif tokens[index].value == "water":
                # AUTO: Sets `water_line`.
                water_line = tokens[index].line
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Checks this condition.
                if tokens[index].type != "(":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Expected '(' after water.", water_line)
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Sets `water_type`.
                water_type = None
                # AUTO: Checks this condition.
                if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
                    # AUTO: Sets `water_type`.
                    water_type = tokens[index].value
                    # AUTO: Adds into `index`.
                    index += 1
                # AUTO: Checks this condition.
                if tokens[index].type != ")":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter (e.g., water(seed)).", water_line)
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Checks this condition.
                if water_type and not _types_compatible(var_type, water_type):
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Type mismatch — cannot assign water({water_type}) to '{var_type}' variable.", water_line)
                # AUTO: Sets `value_node`.
                value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=water_line)
                # AUTO: Calls `var_node.add_child`.
                var_node.add_child(value_node)

            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Sets `value_node, index`.
                value_node, index = parse_expression_type(tokens, index, var_type)
                # AUTO: Calls `var_node.add_child`.
                var_node.add_child(value_node)

        # AUTO: Checks the next alternate condition.
        elif tokens[index].type == "[":
            # AUTO: Sets `is_list`.
            is_list = True
            # AUTO: Sets `dimensions`.
            dimensions = []
            # AUTO: Repeats while this condition is true.
            while tokens[index].type == "[":
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Sets `dim_size`.
                dim_size = 0
                # AUTO: Checks this condition.
                if tokens[index].type == "dblit":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Array size must be of type 'seed' (integer), got 'tree' (float) '{tokens[index].value}'.", line)
                # AUTO: Checks this condition.
                if tokens[index].type == "intlit":
                    # AUTO: Sets `dim_size`.
                    dim_size = int(tokens[index].value)
                    # AUTO: Adds into `index`.
                    index += 1
                # AUTO: Checks this condition.
                if tokens[index].type != "]":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Syntax Error: Expected ']' after list size.", line)
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Appends a value to a list.
                dimensions.append(dim_size)

            # AUTO: Sets `default_literals`.
            default_literals = {"seed": "0", "tree": "0.0", "leaf": "''", "vine": '""', "branch": "false"}

            # AUTO: Defines function `build_list_node`.
            def build_list_node(dims):
                # AUTO: Sets `node`.
                node = ASTNode("List", line=line)
                # AUTO: Checks this condition.
                if len(dims) == 1:
                    # AUTO: Starts a loop over these values.
                    for _ in range(dims[0]):
                        # AUTO: Sets `node.add_child(ASTNode("Value", default_literals.get(var_type, "0"), line`.
                        node.add_child(ASTNode("Value", default_literals.get(var_type, "0"), line=line))
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Starts a loop over these values.
                    for _ in range(dims[0]):
                        # AUTO: Calls `node.add_child`.
                        node.add_child(build_list_node(dims[1:]))
                # AUTO: Returns this result to the caller.
                return node

            # AUTO: Sets `list_node`.
            list_node = build_list_node(dimensions)
            # AUTO: Calls `var_node.add_child`.
            var_node.add_child(list_node)

            # AUTO: Checks this condition.
            if tokens[index].type == "=":
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Checks this condition.
                if tokens[index].type == "{":
                    # AUTO: Defines function `parse_init_braces`.
                    def parse_init_braces(idx):
                        # AUTO: Checks this condition.
                        if tokens[idx].type != "{":
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Syntax Error: Expected '{{' in array initialization.", tokens[idx].line)
                        # AUTO: Adds into `idx`.
                        idx += 1
                        # AUTO: Sets `items`.
                        items = []
                        # AUTO: Repeats while this condition is true.
                        while tokens[idx].type != "}":
                            # AUTO: Checks this condition.
                            if tokens[idx].type == "{":
                                # AUTO: Sets `inner_node, idx`.
                                inner_node, idx = parse_init_braces(idx)
                                # AUTO: Appends a value to a list.
                                items.append(inner_node)
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Sets `expr, idx`.
                                expr, idx = parse_expression_type(tokens, idx, var_type)
                                # AUTO: Appends a value to a list.
                                items.append(expr)
                            # AUTO: Checks this condition.
                            if tokens[idx].type == ",":
                                # AUTO: Adds into `idx`.
                                idx += 1
                        # AUTO: Adds into `idx`.
                        idx += 1
                        # AUTO: Returns this result to the caller.
                        return ListNode(elements=items, line=line), idx

                    # AUTO: Sets `value_node, index`.
                    value_node, index = parse_init_braces(index)
                    # AUTO: Sets `var_node.children[-1]`.
                    var_node.children[-1] = value_node
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Syntax Error: Expected '{{' after '=' in array initialization.", line)
   
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Does nothing for this required block.
            pass

        # AUTO: Sets `error`.
        error = symbol_table.declare_variable(var_name, var_type, is_list = is_list)

        # AUTO: Checks this condition.
        if isinstance(error, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(error, line)
        
        # AUTO: Appends a value to a list.
        var_nodes.append(var_node)

        # AUTO: Checks this condition.
        if tokens[index].type == ",":
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `var_name`.
            var_name = tokens[index].value
            # AUTO: Adds into `index`.
            index += 1
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Stops the nearest loop.
            break
    
    # AUTO: Checks this condition.
    if len(var_nodes) == 1:
        # AUTO: Returns this result to the caller.
        return var_nodes[0], index
    
    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Sets `var_list_node`.
        var_list_node = ASTNode("VariableDeclarationList")
        # AUTO: Starts a loop over these values.
        for node in var_nodes:
            # AUTO: Calls `var_list_node.add_child`.
            var_list_node.add_child(node)
        # AUTO: Returns this result to the caller.
        return var_list_node, index


# AUTO: Defines function `_skip_semicolons`.
def _skip_semicolons(tokens, index):
    # AUTO: Repeats while this condition is true.
    while index < len(tokens) and tokens[index].type == ";":
        # AUTO: Adds into `index`.
        index += 1
    # AUTO: Returns this result to the caller.
    return index


# AUTO: Defines function `parse_statement`.
def parse_statement(tokens, index, func_type = None):
    # GUIDE: Central dispatcher for executable statements inside function/root blocks.
    # It routes by the current token: assignment, plant/water, loop, branch, etc.
    # This function receives the current token index and returns:
    # (AST node for that statement, next token index after the statement).
    # AUTO: Sets `token`.
    token = tokens[index]

    # AUTO: Checks this condition.
    if token.type == ";":
        # Empty statement; consume only the semicolon.
        # AUTO: Returns this result to the caller.
        return None, index + 1

    # AUTO: Sets `line`.
    line = token.line

    # AUTO: Checks this condition.
    if token.value in {"seed", "tree", "vine", "leaf", "branch"}:
        # Local variable declaration such as: seed count = 0;
        # AUTO: Sets `var_type`.
        var_type = token.value
        # AUTO: Sets `var_name`.
        var_name = tokens[index + 1].value
        # AUTO: Adds into `index`.
        index += 2

        # AUTO: Sets `node, index`.
        node, index = parse_variable(tokens, index, var_name, var_type)
        # AUTO: Returns this result to the caller.
        return node, index
    
    
    # AUTO: Checks the next alternate condition.
    elif token.value == "fertile":
        # Constant declaration; parse_fertile also records it as non-reassignable.
        # AUTO: Sets `node, index`.
        node, index = parse_fertile(tokens, index)
        # AUTO: Returns this result to the caller.
        return node, index

    # AUTO: Checks the next alternate condition.
    elif token.value == "bundle":
        # Bundle variable declaration such as: bundle Student s;
        # AUTO: Sets `bundle_type_name`.
        bundle_type_name = tokens[index + 1].value
        # AUTO: Checks this condition.
        if bundle_type_name not in symbol_table.bundle_types:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Bundle type '{bundle_type_name}' is not defined.", token.line)
        # AUTO: Sets `var_name`.
        var_name = tokens[index + 2].value
        # AUTO: Adds into `index`.
        index += 3

        # AUTO: Sets `members`.
        members = symbol_table.bundle_types[bundle_type_name]
        # AUTO: Sets `_defaults`.
        _defaults = {"seed": 0, "tree": 0.0, "leaf": '', "vine": "", "branch": False}

        # AUTO: Checks this condition.
        if tokens[index].type == "[":
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Checks this condition.
            if tokens[index].type == "dblit":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Array size must be of type 'seed' (integer), got 'tree' (float) '{tokens[index].value}'.", token.line)
            # AUTO: Sets `array_size`.
            array_size = 0
            # AUTO: Checks this condition.
            if tokens[index].type == "intlit":
                # AUTO: Sets `array_size`.
                array_size = int(tokens[index].value)
                # AUTO: Adds into `index`.
                index += 1
            # AUTO: Checks this condition.
            if tokens[index].type != "]":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Syntax Error: Expected ']' after array size.", token.line)
            # AUTO: Adds into `index`.
            index += 1

            # AUTO: Sets `list_node`.
            list_node = ASTNode("List", line=token.line)
            # AUTO: Starts a loop over these values.
            for _ in range(array_size):
                # AUTO: Sets `bundle_val_node`.
                bundle_val_node = ASTNode("BundleDefault", line=token.line)
                # AUTO: Calls `list_node.add_child`.
                list_node.add_child(bundle_val_node)

            # AUTO: Sets `error`.
            error = symbol_table.declare_variable(var_name, bundle_type_name, is_list=True)
            # AUTO: Checks this condition.
            if isinstance(error, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(error, token.line)

            # AUTO: Sets `node`.
            node = VariableDeclarationNode(bundle_type_name, var_name, line=token.line)
            # AUTO: Calls `node.add_child`.
            node.add_child(list_node)
            # AUTO: Returns this result to the caller.
            return node, index
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Sets `bundle_value`.
            bundle_value = {name: _defaults.get(typ, None) for name, typ in members.items()}

            # AUTO: Sets `error`.
            error = symbol_table.declare_variable(var_name, bundle_type_name, value=bundle_value)
            # AUTO: Checks this condition.
            if isinstance(error, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(error, token.line)

            # AUTO: Sets `node`.
            node = VariableDeclarationNode(bundle_type_name, var_name, line=token.line)
            # AUTO: Returns this result to the caller.
            return node, index

    # AUTO: Checks the next alternate condition.
    elif token.type == "id" and tokens[index + 1].type == "(":
        # Identifier followed by '(' is a function call statement.
        # AUTO: Checks this condition.
        if tokens[index + 1].type == "(":
            # AUTO: Sets `func_name`.
            func_name = token.value
            # AUTO: Sets `error`.
            error = symbol_table.lookup_function(func_name)
            # AUTO: Checks this condition.
            if isinstance(error, str):
                # AUTO: Sets `error`.
                error = symbol_table.lookup_function(func_name)
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(error, token.line)
            # AUTO: Sets `func_type`.
            func_type = symbol_table.lookup_function(func_name)["return_type"]  # type: ignore
            # AUTO: Sets `func_params`.
            func_params = symbol_table.lookup_function(func_name)["params"]  # type: ignore
            # AUTO: Sets `func_call_node, index`.
            func_call_node, index = parse_function_call(tokens, index, func_name, func_type, func_params)
            # AUTO: Returns this result to the caller.
            return func_call_node, index
        
    # AUTO: Checks the next alternate condition.
    elif token.type == "id" or tokens[index].type in {"++", "--"}: 
        # Identifier-start statements include assignments, array/member access,
        # function-like list operations, and prefix/postfix ++/--.
        # AUTO: Sets `assignments_node`.
        assignments_node = ASTNode("AssignmentList")
        # AUTO: Repeats while this condition is true.
        while True:

            # AUTO: Checks this condition.
            if tokens[index].type == "id":
                # AUTO: Sets `var_info`.
                var_info = symbol_table.lookup_variable(tokens[index].value)
                # AUTO: Checks this condition.
                if isinstance(var_info, str):
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(var_info, line)

                # AUTO: Sets `var_name`.
                var_name = tokens[index].value
                # AUTO: Sets `var_type`.
                var_type = var_info["type"]
                # AUTO: Sets `is_list`.
                is_list = var_info.get("is_list", False)

                # AUTO: Sets `is_fertile`.
                is_fertile = var_info.get("is_fertile", False)

                # AUTO: Checks this condition.
                if is_fertile:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-assigned a value.", line)

                # AUTO: Checks this condition.
                if is_list or (var_type == "vine" and tokens[index + 1].type == "["):
                    # AUTO: Checks this condition.
                    if tokens[index + 1].type == "=":
                        # AUTO: Sets `node, index`.
                        node, index = parse_list_assignment(tokens, index)
                        # AUTO: Calls `assignments_node.add_child`.
                        assignments_node.add_child(node)

                    # AUTO: Checks the next alternate condition.
                    elif tokens[index + 1].type == "[":
                        
                        # AUTO: Sets `list_access_node, index`.
                        list_access_node, index = parse_list_access(tokens, index)

                        # AUTO: Checks this condition.
                        if tokens[index + 1].type == "." and var_type in symbol_table.bundle_types:
                            # AUTO: Adds into `index`.
                            index += 2
                            # AUTO: Sets `member_name`.
                            member_name = tokens[index].value
                            # AUTO: Sets `bundle_members`.
                            bundle_members = symbol_table.bundle_types[var_type]
                            # AUTO: Checks this condition.
                            if member_name not in bundle_members:
                                # AUTO: Stops this flow by raising an error.
                                raise SemanticError(f"Semantic Error: Bundle type '{var_type}' has no member '{member_name}'.", line)
                            # AUTO: Sets `member_type`.
                            member_type = bundle_members[member_name]
                            # AUTO: Sets `target`.
                            target = ArrayMemberAccessNode(list_access_node, member_name, line=line)
                            # AUTO: Adds into `index`.
                            index += 1

                            # AUTO: Repeats while this condition is true.
                            while tokens[index].type == "." and member_type in symbol_table.bundle_types:
                                # AUTO: Sets `next_member`.
                                next_member = tokens[index + 1].value
                                # AUTO: Sets `nested_members`.
                                nested_members = symbol_table.bundle_types[member_type]
                                # AUTO: Checks this condition.
                                if next_member not in nested_members:
                                    # AUTO: Stops this flow by raising an error.
                                    raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", line)
                                # AUTO: Sets `member_type`.
                                member_type = nested_members[next_member]
                                # AUTO: Sets `target`.
                                target = MemberAccessNode(target, next_member, line=line)
                                # AUTO: Adds into `index`.
                                index += 2

                            # AUTO: Checks this condition.
                            if tokens[index].type == "=":
                                # AUTO: Adds into `index`.
                                index += 1
                                # AUTO: Sets `value_node, index`.
                                value_node, index = parse_expression_type(tokens, index, member_type)
                                # AUTO: Sets `assign_node`.
                                assign_node = AssignmentNode(target, value_node, line=line)
                                # AUTO: Calls `assignments_node.add_child`.
                                assignments_node.add_child(assign_node)
                            # AUTO: Checks the next alternate condition.
                            elif tokens[index].type in {"+=", "-=", "*=", "/=", "%=", "**="}:
                                # AUTO: Checks this condition.
                                if member_type not in {"seed", "tree"}:
                                    # AUTO: Stops this flow by raising an error.
                                    raise SemanticError(f"Semantic Error: Compound assignment '{tokens[index].value}' is not valid for '{member_type}' member '{member_name}'.", line)
                                # AUTO: Sets `compound_op`.
                                compound_op = tokens[index].value
                                # AUTO: Sets `base_op`.
                                base_op = compound_op[:-1]
                                # AUTO: Adds into `index`.
                                index += 1
                                # AUTO: Sets `rhs_node, index`.
                                rhs_node, index = parse_expression_type(tokens, index, member_type)
                                # AUTO: Sets `value_node`.
                                value_node = BinaryOpNode(target, base_op, rhs_node, line=line)
                                # AUTO: Sets `assign_node`.
                                assign_node = AssignmentNode(target, value_node, line=line)
                                # AUTO: Calls `assignments_node.add_child`.
                                assignments_node.add_child(assign_node)
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Stops this flow by raising an error.
                                raise SemanticError(f"Semantic Error: Expected '=' after '{var_name}[...].{member_name}'.", line)

                        # AUTO: Checks the next alternate condition.
                        elif tokens[index + 1].type == "=":
                            # AUTO: Adds into `index`.
                            index += 2 
                            # AUTO: Checks this condition.
                            if tokens[index].value == "water":
                                # AUTO: Sets `water_line`.
                                water_line = tokens[index].line
                                # AUTO: Adds into `index`.
                                index += 1
                                # AUTO: Checks this condition.
                                if tokens[index].type != "(":
                                    # AUTO: Stops this flow by raising an error.
                                    raise SemanticError(f"Syntax Error: Expected '(' after water.", water_line)
                                # AUTO: Adds into `index`.
                                index += 1
                                # AUTO: Sets `water_type`.
                                water_type = None
                                # AUTO: Checks this condition.
                                if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
                                    # AUTO: Sets `water_type`.
                                    water_type = tokens[index].value
                                    # AUTO: Adds into `index`.
                                    index += 1
                                # AUTO: Checks this condition.
                                if tokens[index].type != ")":
                                    # AUTO: Stops this flow by raising an error.
                                    raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter.", water_line)
                                # AUTO: Adds into `index`.
                                index += 1
                                # AUTO: Checks this condition.
                                if water_type and not _types_compatible(var_type, water_type):
                                    # AUTO: Stops this flow by raising an error.
                                    raise SemanticError(f"Semantic Error: Type mismatch — cannot assign water({water_type}) to '{var_type}' list element.", water_line)
                                # AUTO: Sets `value_node`.
                                value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=water_line)
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Sets `value_node, index`.
                                value_node, index = parse_expression_type(tokens, index, var_type)
                            # AUTO: Sets `assign_node`.
                            assign_node = AssignmentNode(list_access_node, value_node, line=tokens[index].line)
                            # AUTO: Calls `assignments_node.add_child`.
                            assignments_node.add_child(assign_node)

                        # AUTO: Checks the next alternate condition.
                        elif tokens[index + 1].type in {"++", "--"}:
                            
                            # AUTO: Checks this condition.
                            if var_type not in {"seed", "tree"}:
                                # AUTO: Stops this flow by raising an error.
                                raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_type} in expression.", line)
                            # AUTO: Sets `operator`.
                            operator = tokens[index + 1].value
                            # AUTO: Sets `unary_node`.
                            unary_node = UnaryOpNode(operator, list_access_node, "post", line=line)
                            # AUTO: Adds into `index`.
                            index += 2

                            # AUTO: Calls `assignments_node.add_child`.
                            assignments_node.add_child(unary_node)
                            
                        
                # AUTO: Checks the next alternate condition.
                elif tokens[index + 1].type == ".":
                    # AUTO: Sets `obj_name`.
                    obj_name = tokens[index].value
                    # AUTO: Sets `member_name`.
                    member_name = tokens[index + 2].value
                    # AUTO: Checks this condition.
                    if var_type not in symbol_table.bundle_types:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Variable '{obj_name}' is not a bundle type.", line)
                    # AUTO: Sets `bundle_members`.
                    bundle_members = symbol_table.bundle_types[var_type]
                    # AUTO: Checks this condition.
                    if member_name not in bundle_members:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Bundle type '{var_type}' has no member '{member_name}'.", line)
                    # AUTO: Sets `member_type`.
                    member_type = bundle_members[member_name]
                    # AUTO: Adds into `index`.
                    index += 3
                    # AUTO: Sets `target`.
                    target = MemberAccessNode(obj_name, member_name, line=line)

                    # AUTO: Repeats while this condition is true.
                    while tokens[index].type == "." and member_type in symbol_table.bundle_types:
                        # AUTO: Sets `next_member`.
                        next_member = tokens[index + 1].value
                        # AUTO: Sets `nested_members`.
                        nested_members = symbol_table.bundle_types[member_type]
                        # AUTO: Checks this condition.
                        if next_member not in nested_members:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", line)
                        # AUTO: Sets `member_type`.
                        member_type = nested_members[next_member]
                        # AUTO: Sets `target`.
                        target = MemberAccessNode(target, next_member, line=line)
                        # AUTO: Adds into `index`.
                        index += 2

                    # AUTO: Checks this condition.
                    if tokens[index].type == "=":
                        # AUTO: Adds into `index`.
                        index += 1
                        # AUTO: Checks this condition.
                        if tokens[index].value == "water":
                            # AUTO: Sets `water_line`.
                            water_line = tokens[index].line
                            # AUTO: Adds into `index`.
                            index += 1
                            # AUTO: Checks this condition.
                            if tokens[index].type != "(":
                                # AUTO: Stops this flow by raising an error.
                                raise SemanticError(f"Syntax Error: Expected '(' after water.", water_line)
                            # AUTO: Adds into `index`.
                            index += 1
                            # AUTO: Sets `water_type`.
                            water_type = None
                            # AUTO: Checks this condition.
                            if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
                                # AUTO: Sets `water_type`.
                                water_type = tokens[index].value
                                # AUTO: Adds into `index`.
                                index += 1
                            # AUTO: Checks this condition.
                            if tokens[index].type != ")":
                                # AUTO: Stops this flow by raising an error.
                                raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter (e.g., water(seed)).", water_line)
                            # AUTO: Adds into `index`.
                            index += 1
                            # AUTO: Checks this condition.
                            if water_type and not _types_compatible(member_type, water_type):
                                # AUTO: Stops this flow by raising an error.
                                raise SemanticError(f"Semantic Error: Type mismatch — cannot assign water({water_type}) to '{member_type}' member '{member_name}'.", water_line)
                            # AUTO: Sets `value_node`.
                            value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=water_line)
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Sets `value_node, index`.
                            value_node, index = parse_expression_type(tokens, index, member_type)
                        # AUTO: Sets `assign_node`.
                        assign_node = AssignmentNode(target, value_node, line=line)
                        # AUTO: Calls `assignments_node.add_child`.
                        assignments_node.add_child(assign_node)
                    # AUTO: Checks the next alternate condition.
                    elif tokens[index].type in {"+=", "-=", "*=", "/=", "%=", "**="}:
                        # AUTO: Checks this condition.
                        if member_type not in {"seed", "tree"}:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Compound assignment '{tokens[index].value}' is not valid for '{member_type}' member '{member_name}'.", line)
                        # AUTO: Sets `compound_op`.
                        compound_op = tokens[index].value
                        # AUTO: Sets `base_op`.
                        base_op = compound_op[:-1]
                        # AUTO: Adds into `index`.
                        index += 1
                        # AUTO: Sets `rhs_node, index`.
                        rhs_node, index = parse_expression_type(tokens, index, member_type)
                        # AUTO: Sets `value_node`.
                        value_node = BinaryOpNode(target, base_op, rhs_node, line=line)
                        # AUTO: Sets `assign_node`.
                        assign_node = AssignmentNode(target, value_node, line=line)
                        # AUTO: Calls `assignments_node.add_child`.
                        assignments_node.add_child(assign_node)
                    # AUTO: Checks the next alternate condition.
                    elif tokens[index].type in {"++", "--"}:
                        # AUTO: Checks this condition.
                        if member_type not in {"seed", "tree"}:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Cannot apply '{tokens[index].value}' to member '{member_name}' of type '{member_type}'.", line)
                        # AUTO: Sets `operator`.
                        operator = tokens[index].value
                        # AUTO: Adds into `index`.
                        index += 1
                        # AUTO: Sets `assignments_node.add_child(UnaryOpNode(operator, target, "post", line`.
                        assignments_node.add_child(UnaryOpNode(operator, target, "post", line=line))
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Expected '=' after '{obj_name}.{member_name}'.", line)

                # AUTO: Checks the next alternate condition.
                elif tokens[index + 1].type == "=":
                    # AUTO: Sets `var_name`.
                    var_name = token.value
                    # AUTO: Sets `var_info`.
                    var_info = symbol_table.lookup_variable(var_name)
                    # AUTO: Checks this condition.
                    if isinstance(var_info, str):
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(var_info, token.line)

                    # AUTO: Adds into `index`.
                    index += 2
                    # AUTO: Sets `node, index`.
                    node, index = parse_assignment(tokens, index, token.value, var_info["type"])
                    # AUTO: Calls `assignments_node.add_child`.
                    assignments_node.add_child(node)

                # AUTO: Checks the next alternate condition.
                elif tokens[index + 1].type in {"++", "--"}:
                    # AUTO: Sets `var_info`.
                    var_info = symbol_table.lookup_variable(tokens[index].value)
                    
                    # AUTO: Checks this condition.
                    if isinstance(var_info, str):
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(var_info, line)
                    
                    # AUTO: Checks this condition.
                    if var_info["type"] not in {"seed", "tree"}:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Cannot use '{token.value}' of type {var_info['type']} in expression.", line)
                    # AUTO: Sets `operand`.
                    operand = ASTNode("Identifier", token.value, line=line)
                    # AUTO: Sets `operator`.
                    operator = tokens[index + 1].value
                    # AUTO: Adds into `index`.
                    index += 2
                    # AUTO: Sets `assignments_node.add_child(UnaryOpNode(operator, operand, "post", line`.
                    assignments_node.add_child(UnaryOpNode(operator, operand, "post", line=line))

                # AUTO: Checks the next alternate condition.
                elif tokens[index + 1].type in {"+=", "-=", "*=", "/=", "%=", "**="}:
                    # AUTO: Sets `compound_op`.
                    compound_op = tokens[index + 1].value
                    # AUTO: Sets `base_op`.
                    base_op = compound_op[:-1]
                    # AUTO: Sets `cur_var_name`.
                    cur_var_name = tokens[index].value
                    # AUTO: Sets `cur_var_info`.
                    cur_var_info = symbol_table.lookup_variable(cur_var_name)
                    # AUTO: Checks this condition.
                    if isinstance(cur_var_info, str):
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(cur_var_info, line)
                    # AUTO: Checks this condition.
                    if cur_var_info.get("is_fertile", False):
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Variable '{cur_var_name}' is declared as fertile and cannot be re-assigned a value.", line)
                    # AUTO: Sets `cur_var_type`.
                    cur_var_type = cur_var_info["type"]
                    # AUTO: Checks this condition.
                    if cur_var_type not in {"seed", "tree"}:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Cannot use compound assignment on '{cur_var_name}' of type '{cur_var_type}'.", line)
                    # AUTO: Checks this condition.
                    if base_op == "%" and cur_var_type != "seed":
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(
                            # AUTO: Executes this statement.
                            f"Semantic Error: Modulo operator '%' requires 'seed' (integer) operands, "
                            # AUTO: Executes this statement.
                            f"but '{cur_var_name}' is of type 'tree'.",
                            # AUTO: Executes this statement.
                            line,
                        # AUTO: Closes the current grouped code/data.
                        )
                    # AUTO: Adds into `index`.
                    index += 2
                    # AUTO: Sets `rhs_node, index, rhs_type`.
                    rhs_node, index, rhs_type = parse_expression(tokens, index)
                    # AUTO: Checks this condition.
                    if rhs_type not in {"seed", "tree"}:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(
                            # AUTO: Sets `f"Semantic Error: Cannot use '{base_op}`.
                            f"Semantic Error: Cannot use '{base_op}=' with right-hand side of type '{rhs_type}'. Expected 'seed' or 'tree'.",
                            # AUTO: Executes this statement.
                            line,
                        # AUTO: Closes the current grouped code/data.
                        )
                    # AUTO: Sets `lhs_node`.
                    lhs_node = ASTNode("Identifier", cur_var_name, line=line)
                    # AUTO: Sets `value_node`.
                    value_node = BinaryOpNode(lhs_node, base_op, rhs_node, line=line)
                    # AUTO: Sets `assign_node`.
                    assign_node = AssignmentNode(cur_var_name, value_node, line=line)
                    # AUTO: Calls `assignments_node.add_child`.
                    assignments_node.add_child(assign_node)

                
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Unexpected token '{tokens[index].value}' in statement.", line)

            # AUTO: Checks the next alternate condition.
            elif tokens[index].value in {"++", "--"}:
                # AUTO: Sets `operator`.
                operator = tokens[index].value
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Checks this condition.
                if tokens[index].type == "id":
                    # AUTO: Sets `var_name`.
                    var_name = tokens[index].value
                    # AUTO: Sets `var_info`.
                    var_info = symbol_table.lookup_variable(var_name)
                    # AUTO: Checks this condition.
                    if isinstance(var_info, str):
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)

                    # AUTO: Checks this condition.
                    if tokens[index + 1].type == "[":
                        # AUTO: Checks this condition.
                        if var_info["type"] not in {"seed", "tree"}:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in expression.", line)
                        # AUTO: Sets `list_access_node, index`.
                        list_access_node, index = parse_list_access(tokens, index)
                        # AUTO: Adds into `index`.
                        index += 1
                        # AUTO: Sets `assignments_node.add_child(UnaryOpNode(operator, list_access_node, "pre", line`.
                        assignments_node.add_child(UnaryOpNode(operator, list_access_node, "pre", line=line))

                    # AUTO: Checks the next alternate condition.
                    elif tokens[index + 1].type == ".":
                        # AUTO: Sets `obj_name`.
                        obj_name = tokens[index].value
                        # AUTO: Checks this condition.
                        if var_info["type"] not in symbol_table.bundle_types:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Variable '{obj_name}' is not a bundle type.", line)
                        # AUTO: Sets `member_name`.
                        member_name = tokens[index + 2].value
                        # AUTO: Sets `bundle_members`.
                        bundle_members = symbol_table.bundle_types[var_info["type"]]
                        # AUTO: Checks this condition.
                        if member_name not in bundle_members:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Bundle type '{var_info['type']}' has no member '{member_name}'.", line)
                        # AUTO: Sets `member_type`.
                        member_type = bundle_members[member_name]
                        # AUTO: Adds into `index`.
                        index += 3
                        # AUTO: Sets `target`.
                        target = MemberAccessNode(obj_name, member_name, line=line)
                        # AUTO: Repeats while this condition is true.
                        while tokens[index].type == "." and member_type in symbol_table.bundle_types:
                            # AUTO: Sets `next_member`.
                            next_member = tokens[index + 1].value
                            # AUTO: Sets `nested_members`.
                            nested_members = symbol_table.bundle_types[member_type]
                            # AUTO: Checks this condition.
                            if next_member not in nested_members:
                                # AUTO: Stops this flow by raising an error.
                                raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", line)
                            # AUTO: Sets `member_type`.
                            member_type = nested_members[next_member]
                            # AUTO: Sets `target`.
                            target = MemberAccessNode(target, next_member, line=line)
                            # AUTO: Adds into `index`.
                            index += 2
                        # AUTO: Checks this condition.
                        if member_type not in {"seed", "tree"}:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Cannot apply '{operator}' to member '{member_name}' of type '{member_type}'.", line)
                        # AUTO: Sets `assignments_node.add_child(UnaryOpNode(operator, target, "pre", line`.
                        assignments_node.add_child(UnaryOpNode(operator, target, "pre", line=line))

                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Checks this condition.
                        if var_info["type"] not in {"seed", "tree"}:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in expression.", line)
                        # AUTO: Sets `operand`.
                        operand = ASTNode("Identifier", tokens[index].value, line=line)
                        # AUTO: Adds into `index`.
                        index += 1
                        # AUTO: Sets `assignments_node.add_child(UnaryOpNode(operator, operand, "pre", line`.
                        assignments_node.add_child(UnaryOpNode(operator, operand, "pre", line=line))

                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Syntax Error: Expected identifier after '{operator}'.", line)

            # AUTO: Checks this condition.
            if tokens[index].type == ",":
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Sets `token`.
                token = tokens[index]
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Stops the nearest loop.
                break
            
        # AUTO: Checks this condition.
        if len(assignments_node.children) > 1:
            # AUTO: Returns this result to the caller.
            return assignments_node, index
        
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Returns this result to the caller.
            return assignments_node.children[0], index


    # AUTO: Checks the next alternate condition.
    elif token.value in {"plant"}:
        # plant(...) output statement.
        # AUTO: Sets `node, index`.
        node, index = parse_print(tokens, index)
        # AUTO: Returns this result to the caller.
        return node, index

    # AUTO: Checks the next alternate condition.
    elif token.value == "water":
        # water(...) input statement.
        # AUTO: Sets `node, index`.
        node, index = parse_water_statement(tokens, index)
        # AUTO: Returns this result to the caller.
        return node, index

    # AUTO: Checks the next alternate condition.
    elif token.value == "spring":
        # spring/bud/wither conditional chain.
        # AUTO: Sets `node, index`.
        node, index = parse_if(tokens, index, func_type)
        # AUTO: Returns this result to the caller.
        return node, index

    # AUTO: Checks the next alternate condition.
    elif token.value in {"reclaim"}:
        # reclaim; or reclaim expression; returns from the current function.
        # AUTO: Sets `node, index`.
        node, index = parse_return(tokens, index, func_type)
        # AUTO: Returns this result to the caller.
        return node, index 
    
    # AUTO: Checks the next alternate condition.
    elif token.value == "cultivate":
        # cultivate loop.
        # AUTO: Sets `node, index`.
        node, index = parse_for(tokens, index, func_type)
        # AUTO: Returns this result to the caller.
        return node, index

    # AUTO: Checks the next alternate condition.
    elif token.value in {"grow"}:
        # grow while-loop.
        # AUTO: Sets `node, index`.
        node, index = parse_while(tokens, index, func_type)
        # AUTO: Returns this result to the caller.
        return node, index
    
    # AUTO: Checks the next alternate condition.
    elif token.value in {"tend"}:
        # tend do-while loop.
        # AUTO: Sets `node, index`.
        node, index = parse_do(tokens, index, func_type)
        # AUTO: Returns this result to the caller.
        return node, index
    
    # AUTO: Checks the next alternate condition.
    elif token.value in {"harvest"}:
        # harvest switch-like statement.
        # AUTO: Sets `node, index`.
        node, index = parse_switch(tokens, index, func_type)
        # AUTO: Returns this result to the caller.
        return node, index
    
    # AUTO: Checks the next alternate condition.
    elif token.value in {"prune"}:
        # AUTO: Checks this condition.
        if not is_inside_loop_or_switch_stack():
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: 'prune' statement used outside a loop or switch statement.", line)
        # AUTO: Sets `node`.
        node = BreakNode(line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Returns this result to the caller.
        return node, index
        
    # AUTO: Checks the next alternate condition.
    elif token.value in {"skip"}:
        # AUTO: Checks this condition.
        if not is_inside_loop_or_switch_stack():
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: 'skip' statement used outside a loop or switch statement.", line)
        # AUTO: Sets `node`.
        node = ContinueNode(line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Returns this result to the caller.
        return node, index

    # AUTO: Checks the next alternate condition.
    elif token.value in {"variety", "soil"}:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: '{token.value}' statement used outside a 'harvest' block.", line)

    # AUTO: Checks the next alternate condition.
    elif token.type == "{":
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `block_node`.
        block_node = ASTNode("Block", line=line)
        # AUTO: Repeats while this condition is true.
        while tokens[index].type != "}":
            # AUTO: Sets `stmt, index`.
            stmt, index = parse_statement(tokens, index, func_type)
            # AUTO: Checks this condition.
            if stmt:
                # AUTO: Calls `block_node.add_child`.
                block_node.add_child(stmt)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Returns this result to the caller.
        return block_node, index

    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Unexpected token '{token.value}' in statement.", line)


# AUTO: Defines function `parse_list_access`.
def parse_list_access(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Sets `list_name`.
    list_name = tokens[index].value

    # AUTO: Sets `list_info`.
    list_info = symbol_table.lookup_variable(list_name)
    # AUTO: Checks this condition.
    if isinstance(list_info, str):
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(list_info, line)
    
    # AUTO: Checks this condition.
    if not list_info.get("is_list", False) and list_info.get("type") != "vine":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Variable '{list_name}' is not a list.", line)
    
    # AUTO: Sets `list_type`.
    list_type = list_info["type"]
    # AUTO: Adds into `index`.
    index += 2 

    # AUTO: Sets `index_node, index, idx_type`.
    index_node, index, idx_type = parse_equality(tokens, index)

    # AUTO: Checks this condition.
    if idx_type is not None and idx_type != "seed":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(
            # AUTO: Executes this statement.
            f"Semantic Error: List index must be of type 'seed', got '{idx_type}'.",
            # AUTO: Executes this statement.
            line,
        # AUTO: Closes the current grouped code/data.
        )

    # AUTO: Checks this condition.
    if tokens[index].type != "]":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
    
    # AUTO: Sets `index_wrapper`.
    index_wrapper = ASTNode("Index", line=line)
    # AUTO: Calls `index_wrapper.add_child`.
    index_wrapper.add_child(index_node)

    # AUTO: Sets `node`.
    node = ListAccessNode(list_name, index_wrapper, line=line)

    # AUTO: Repeats while this condition is true.
    while tokens[index + 1].type == "[":
        # AUTO: Adds into `index`.
        index += 2
        # AUTO: Sets `inner_index_node, index, inner_idx_type`.
        inner_index_node, index, inner_idx_type = parse_equality(tokens, index)
        # AUTO: Checks this condition.
        if inner_idx_type is not None and inner_idx_type != "seed":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: List index must be of type 'seed', got '{inner_idx_type}'.",
                # AUTO: Executes this statement.
                line,
            # AUTO: Closes the current grouped code/data.
            )
        # AUTO: Checks this condition.
        if tokens[index].type != "]":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
        # AUTO: Sets `inner_wrapper`.
        inner_wrapper = ASTNode("Index", line=line)
        # AUTO: Calls `inner_wrapper.add_child`.
        inner_wrapper.add_child(inner_index_node)
        # AUTO: Sets `node`.
        node = ListAccessNode(node, inner_wrapper, line=line)

    # AUTO: Returns this result to the caller.
    return node, index


# AUTO: Defines function `parse_list_assignment`.
def parse_list_assignment(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Sets `var_name`.
    var_name = tokens[index].value

    # AUTO: Sets `var_info`.
    var_info = symbol_table.lookup_variable(var_name)
    # AUTO: Checks this condition.
    if isinstance(var_info, str):
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(var_info, line)
    
    # AUTO: Checks this condition.
    if not var_info.get("is_list", False):
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: '{var_name}' is not a list.", line)
    
    # AUTO: Sets `var_type`.
    var_type = var_info["type"] 

    # AUTO: Adds into `index`.
    index += 2

    # AUTO: Checks this condition.
    if var_info.get("is_fertile", False):
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile.", line)

    # AUTO: Checks this condition.
    if tokens[index].value == "append":
        # AUTO: Sets `value_node, index`.
        value_node, index = parse_append(tokens, index, var_name, var_type)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].value == "insert":
        # AUTO: Sets `value_node, index`.
        value_node, index = parse_insert(tokens, index, var_name, var_type)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].value == "remove":
        # AUTO: Sets `value_node, index`.
        value_node, index = parse_remove(tokens, index, var_name, var_type)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type == "id":
        # AUTO: Sets `source_var`.
        source_var = tokens[index].value
        # AUTO: Sets `source_info`.
        source_info = symbol_table.lookup_variable(source_var)
        # AUTO: Checks this condition.
        if isinstance(source_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Variable '{source_var}' used before declaration.", line)

        # AUTO: Checks this condition.
        if source_info["is_list"] == False and tokens[index + 1].type != ".":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Cannot assign non-list '{source_var}' to list '{var_name}'.", line)

        # AUTO: Sets `source_type`.
        source_type = source_info["type"]

        # AUTO: Checks this condition.
        if source_type == "leaf" and tokens[index + 1].type == ".":
            # AUTO: Sets `member_name`.
            member_name = tokens[index + 2].value
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Unsupported member access '{source_var}.{member_name}'.", line)

        # AUTO: Checks this condition.
        if source_type == "leaf" and tokens[index + 1].type != ".":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Cannot assign non-list '{source_var}' to list '{var_name}'.", line)

        # AUTO: Checks this condition.
        if var_type != source_type:
            # AUTO: Checks this condition.
            if not (var_type in {"seed", "tree"} and source_type in {"seed", "tree"}):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(
                    # AUTO: Executes this statement.
                    f"Semantic Error: Cannot assign list of '{source_type}' type to list of '{var_type}' type.", line
                # AUTO: Closes the current grouped code/data.
                )

        # AUTO: Sets `value_node`.
        value_node = ASTNode("Value", source_var, line=line)
        # AUTO: Adds into `index`.
        index += 1

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type == "[":
        # AUTO: Sets `value_node, index`.
        value_node, index = parse_list(tokens, index, var_type)

    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Invalid list assignment.", line)

    # AUTO: Returns this result to the caller.
    return AssignmentNode(var_name, value_node, line=line), index


# AUTO: Defines function `_types_compatible`.
def _types_compatible(declared, inferred):
    # AUTO: Checks this condition.
    if declared == inferred:
        # AUTO: Returns this result to the caller.
        return True
    # AUTO: Checks this condition.
    if declared in {"seed", "tree"} and inferred in {"seed", "tree"}:
        # AUTO: Returns this result to the caller.
        return True
    # AUTO: Returns this result to the caller.
    return False


# AUTO: Defines function `parse_expression_type`.
def parse_expression_type(tokens, index, var_type):
    # AUTO: Sets `line`.
    line = tokens[index].line

    # AUTO: Checks this condition.
    if var_type not in {"seed", "tree", "vine", "leaf", "branch"} and var_type not in symbol_table.bundle_types:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError("Semantic Error: Invalid type for assignment.", line)

    # AUTO: Sets `node, index, expr_type`.
    node, index, expr_type = parse_assignment_expression(tokens, index)

    # AUTO: Checks this condition.
    if expr_type is None:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(
            # AUTO: Executes this statement.
            "Semantic Error: Could not determine the type of the expression.",
            # AUTO: Executes this statement.
            line,
        # AUTO: Closes the current grouped code/data.
        )
    # AUTO: Checks this condition.
    if not _types_compatible(var_type, expr_type):
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(
            # AUTO: Executes this statement.
            f"Semantic Error: Type mismatch — cannot assign '{expr_type}' value to '{var_type}' variable.",
            # AUTO: Executes this statement.
            line,
        # AUTO: Closes the current grouped code/data.
        )

    # AUTO: Returns this result to the caller.
    return node, index

# AUTO: Defines function `parse_expression_vine`.
def parse_expression_vine(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Sets `token`.
    token = tokens[index]
    # AUTO: Checks this condition.
    if tokens[index].type == "id" and tokens[index + 1].type == "(":
        # AUTO: Sets `func_name`.
        func_name = tokens[index].value
        # AUTO: Sets `func_info`.
        func_info = symbol_table.lookup_function(func_name)
        # AUTO: Sets `func_return_type`.
        func_return_type = func_info["return_type"]  # type: ignore
        # AUTO: Sets `func_params`.
        func_params = func_info["params"]  # type: ignore
        
        # AUTO: Checks this condition.
        if func_return_type not in {"vine"}:
            # AUTO: Sets `error`.
            error = f"Semantic Error: Cannot use function '{func_name}' of type {func_return_type}. Expected valid vine value."
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(error, line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Returns this result to the caller.
        return parse_function_call(tokens, index, func_name, func_return_type, func_params)
    
    # AUTO: Checks the next alternate condition.
    elif tokens[index].type == "id":
        # AUTO: Sets `variable_info`.
        variable_info = symbol_table.lookup_variable(tokens[index].value)
        # AUTO: Checks this condition.
        if isinstance(variable_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(variable_info, line)

        # AUTO: Sets `is_list`.
        is_list = variable_info.get("is_list", False)

        # AUTO: Checks this condition.
        if is_list and tokens[index + 1].type != "[":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: List '{token.value}' must be indexed with '[]'.", line)

        # AUTO: Checks this condition.
        if variable_info["type"] != "vine":
            # AUTO: Sets `error`.
            error = f"Semantic Error: Cannot use '{tokens[index].value}' of type {variable_info['type']}. Expected valid vine value."
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(error, line)

        # AUTO: Sets `node`.
        node = ASTNode("Value", tokens[index].value)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Returns this result to the caller.
        return node, index

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type == "stringlit":
        # AUTO: Sets `node`.
        node = ASTNode("Value", tokens[index].value)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Returns this result to the caller.
        return node, index

    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Sets `error`.
        error = f"Semantic Error: Expected valid vine value."
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(error, line) 

# AUTO: Defines function `parse_expression_leaf`.
def parse_expression_leaf(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line  
    # AUTO: Sets `token`.
    token = tokens[index]

    # AUTO: Checks this condition.
    if tokens[index].type not in {"chrlit", "id", "stringlit"}:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Expected valid leaf value.", line)

    # AUTO: Checks this condition.
    if tokens[index].type == "id" and tokens[index + 1].type == "(":
        # AUTO: Sets `func_name`.
        func_name = tokens[index].value
        # AUTO: Sets `func_info`.
        func_info = symbol_table.lookup_function(func_name)

        # AUTO: Checks this condition.
        if isinstance(func_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Function '{func_name}' is not defined.", line)

        # AUTO: Sets `func_return_type`.
        func_return_type = func_info["return_type"]
        # AUTO: Checks this condition.
        if func_return_type not in {"vine", "leaf"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Cannot use function '{func_name}' of type '{func_return_type}'. Expected valid leaf value.", line)

        # AUTO: Sets `node, index`.
        node, index = parse_function_call(tokens, index, func_name, func_return_type, func_info["params"])


    # AUTO: Checks the next alternate condition.
    elif token.type == "id" and tokens[index + 1].type == "[":
        # AUTO: Sets `list_name`.
        list_name = token.value
        # AUTO: Sets `list_info`.
        list_info = symbol_table.lookup_variable(list_name)

        # AUTO: Checks this condition.
        if isinstance(list_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", token.line)

        # AUTO: Checks this condition.
        if not list_info["is_list"] and list_info.get("type") != "vine":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

        # AUTO: Adds into `index`.
        index += 2
        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression(tokens, index)

        # AUTO: Checks this condition.
        if tokens[index].type != "]":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError("Syntax Error: Missing closing bracket.", token.line)

        # AUTO: Sets `index_node`.
        index_node = ASTNode("Index", line=token.line)
        # AUTO: Calls `index_node.add_child`.
        index_node.add_child(expr_node)

        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `node`.
        node = ListAccessNode(list_name, index_node, line=token.line)

        # AUTO: Repeats while this condition is true.
        while index < len(tokens) and tokens[index].type == "[":
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `inner_expr, index, _`.
            inner_expr, index, _ = parse_expression(tokens, index)
            # AUTO: Checks this condition.
            if tokens[index].type != "]":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError("Syntax Error: Missing closing bracket.", token.line)
            # AUTO: Sets `inner_index`.
            inner_index = ASTNode("Index", line=token.line)
            # AUTO: Calls `inner_index.add_child`.
            inner_index.add_child(inner_expr)
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `node`.
            node = ListAccessNode(node, inner_index, line=token.line)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type == "id":
        # AUTO: Sets `var_name`.
        var_name = tokens[index].value
        # AUTO: Sets `var_info`.
        var_info = symbol_table.lookup_variable(var_name)
        # AUTO: Checks this condition.
        if isinstance(var_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(var_info, line)
        # AUTO: Sets `is_list`.
        is_list = var_info.get("is_list", False)
        # AUTO: Checks this condition.
        if is_list and tokens[index + 1].type != "[":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: List '{tokens[index].value}' must be indexed with '[]'.", line)

        # AUTO: Checks this condition.
        if var_info["type"] not in {"vine", "leaf"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']}. Expected valid leaf value.", line)

        # AUTO: Sets `node`.
        node = ASTNode("Value", var_name, line=line)
        # AUTO: Adds into `index`.
        index += 1  

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type in {"chrlit", "stringlit"}:
        # AUTO: Sets `node`.
        node = ASTNode("Value", tokens[index].value, line=line)
        # AUTO: Adds into `index`.
        index += 1 

    # AUTO: Sets `left_node`.
    left_node = node

    # AUTO: Checks this condition.
    if tokens[index].type in {"+", "-", "*", "/", "%", "<", ">", "<=", ">=", "==", "!="}:
        # AUTO: Repeats while this condition is true.
        while tokens[index].type in {"+", "-", "*", "/", "%"}:
            # AUTO: Sets `op`.
            op = tokens[index].value  
            # AUTO: Adds into `index`.
            index += 1 

            # AUTO: Checks this condition.
            if tokens[index].type == "id" and tokens[index + 1].type == "(":
                # AUTO: Sets `func_name`.
                func_name = tokens[index].value
                # AUTO: Sets `func_info`.
                func_info = symbol_table.lookup_function(func_name)

                # AUTO: Checks this condition.
                if isinstance(func_info, str):
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Function '{func_name}' is not defined.", line)

                # AUTO: Sets `func_return_type`.
                func_return_type = func_info["return_type"]
                # AUTO: Checks this condition.
                if func_return_type not in {"vine", "leaf"}:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Cannot use function '{func_name}' of type '{func_return_type}'. Expected valid leaf value", line)

                # AUTO: Sets `right_node, index`.
                right_node, index = parse_function_call(tokens, index, func_name, func_return_type, func_info["params"])

            # AUTO: Checks the next alternate condition.
            elif tokens[index].type == "id" and tokens[index + 1].type == "[":
                # AUTO: Sets `list_name`.
                list_name = tokens[index].value
                # AUTO: Sets `list_info`.
                list_info = symbol_table.lookup_variable(list_name)

                # AUTO: Checks this condition.
                if isinstance(list_info, str):
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", token.line)

                # AUTO: Checks this condition.
                if not list_info["is_list"] and list_info.get("type") != "vine":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

                # AUTO: Adds into `index`.
                index += 2
                # AUTO: Sets `expr_node, index, _`.
                expr_node, index, _ = parse_expression(tokens, index)

                # AUTO: Checks this condition.
                if tokens[index].type != "]":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError("Syntax Error: Missing closing bracket.", token.line)

                # AUTO: Sets `index_node`.
                index_node = ASTNode("Index", line=token.line)
                # AUTO: Calls `index_node.add_child`.
                index_node.add_child(expr_node)

                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Sets `right_node`.
                right_node = ListAccessNode(list_name, index_node, line=token.line)


            # AUTO: Checks the next alternate condition.
            elif tokens[index].type == "id":
                # AUTO: Sets `var_name`.
                var_name = tokens[index].value
                # AUTO: Sets `var_info`.
                var_info = symbol_table.lookup_variable(var_name)
                # AUTO: Checks this condition.
                if isinstance(var_info, str):
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(var_info, line)
                # AUTO: Sets `is_list`.
                is_list = var_info.get("is_list", False)

                # AUTO: Checks this condition.
                if is_list and tokens[index + 1].type != "[":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: List '{token.value}' must be indexed with '[]' in expressions.", line)

                # AUTO: Checks this condition.
                if var_info["type"] not in {"vine", "leaf"}:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in this expression.", line)

                # AUTO: Sets `right_node`.
                right_node = ASTNode("Value", var_name, line=line)
                # AUTO: Adds into `index`.
                index += 1 

            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Sets `right_node`.
                right_node = ASTNode("Value", tokens[index].value, line=line)
                # AUTO: Adds into `index`.
                index += 1  

            # AUTO: Sets `left_node`.
            left_node = BinaryOpNode(left_node, op, right_node, line=line)
    
    # AUTO: Returns this result to the caller.
    return left_node, index 


# AUTO: Defines function `parse_expression`.
def parse_expression(tokens, index):
    # GUIDE: Arithmetic/string expression level. Lower-level functions handle
    # multiplication, exponent, unary operators, literals, calls, and grouping.
    # AUTO: Sets `left_node, index, left_type`.
    left_node, index, left_type = parse_term(tokens, index)

    # AUTO: Repeats while this condition is true.
    while tokens[index].type in {"+", "-", "`"}:
        # AUTO: Sets `op`.
        op = tokens[index].value
        # AUTO: Sets `token`.
        token = tokens[index]

        # AUTO: Checks this condition.
        if op == "`":
            # AUTO: Checks this condition.
            if left_type not in {"vine", "leaf"}:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(
                    # AUTO: Executes this statement.
                    f"Semantic Error: Cannot concatenate - left operand is of type '{left_type}', expected 'vine' or 'leaf'.",
                    # AUTO: Executes this statement.
                    token.line,
                # AUTO: Closes the current grouped code/data.
                )
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `right_node, index, right_type`.
            right_node, index, right_type = parse_term(tokens, index)
            # AUTO: Checks this condition.
            if right_type not in {"vine", "leaf"}:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(
                    # AUTO: Executes this statement.
                    f"Semantic Error: Cannot concatenate - right operand is of type '{right_type}', expected 'vine' or 'leaf'.",
                    # AUTO: Executes this statement.
                    token.line,
                # AUTO: Closes the current grouped code/data.
                )
            # AUTO: Sets `left_node`.
            left_node = BinaryOpNode(left_node, op, right_node)
            # AUTO: Sets `left_type`.
            left_type = "vine"
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Checks this condition.
            if left_type not in {"seed", "tree"}:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(
                    # AUTO: Executes this statement.
                    f"Semantic Error: Cannot use '{op}' on type '{left_type}'. Expected 'seed' or 'tree'.",
                    # AUTO: Executes this statement.
                    token.line,
                # AUTO: Closes the current grouped code/data.
                )
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `right_node, index, right_type`.
            right_node, index, right_type = parse_term(tokens, index)
            # AUTO: Checks this condition.
            if right_type not in {"seed", "tree"}:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(
                    # AUTO: Executes this statement.
                    f"Semantic Error: Cannot use '{op}' on type '{right_type}'. Expected 'seed' or 'tree'.",
                    # AUTO: Executes this statement.
                    token.line,
                # AUTO: Closes the current grouped code/data.
                )
            # AUTO: Sets `left_node`.
            left_node = BinaryOpNode(left_node, op, right_node)
            # AUTO: Checks this condition.
            if left_type == "tree" or right_type == "tree":
                # AUTO: Sets `left_type`.
                left_type = "tree"

    # AUTO: Returns this result to the caller.
    return left_node, index, left_type

# AUTO: Defines function `parse_term`.
def parse_term(tokens, index):
    # AUTO: Sets `left_node, index, left_type`.
    left_node, index, left_type = parse_power(tokens, index)

    # AUTO: Repeats while this condition is true.
    while tokens[index].type in {"*", "/", "%"}:
        # AUTO: Sets `op`.
        op = tokens[index].value
        # AUTO: Sets `token`.
        token = tokens[index]

        # AUTO: Checks this condition.
        if left_type not in {"seed", "tree"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Cannot use '{op}' on type '{left_type}'. Expected 'seed' or 'tree'.",
                # AUTO: Executes this statement.
                token.line,
            # AUTO: Closes the current grouped code/data.
            )

        # AUTO: Checks this condition.
        if op == "%":
            # AUTO: Checks this condition.
            if left_type == "tree":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(
                    # AUTO: Executes this statement.
                    "Semantic Error: Modulo operator '%' requires 'seed' (integer) operands, "
                    # AUTO: Executes this statement.
                    "but found 'tree' (decimal) value.",
                    # AUTO: Executes this statement.
                    token.line,
                # AUTO: Closes the current grouped code/data.
                )

        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `right_node, index, right_type`.
        right_node, index, right_type = parse_power(tokens, index)

        # AUTO: Checks this condition.
        if right_type not in {"seed", "tree"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Cannot use '{op}' on type '{right_type}'. Expected 'seed' or 'tree'.",
                # AUTO: Executes this statement.
                token.line,
            # AUTO: Closes the current grouped code/data.
            )

        # AUTO: Checks this condition.
        if op == "%" and right_type == "tree":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                "Semantic Error: Modulo operator '%' requires 'seed' (integer) operands, "
                # AUTO: Executes this statement.
                "but found 'tree' (decimal) value.",
                # AUTO: Executes this statement.
                token.line,
            # AUTO: Closes the current grouped code/data.
            )

        # AUTO: Checks this condition.
        if op in {"/", "%"} and isinstance(right_node, ASTNode) and right_node.node_type == "Value":
            # AUTO: Starts protected code that can catch errors.
            try:
                # AUTO: Checks this condition.
                if float(right_node.value) == 0:  # type: ignore
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Division or modulus by zero is undefined.", token.line)
            # AUTO: Handles the matching error case.
            except ValueError:
                # AUTO: Does nothing for this required block.
                pass
            
        # AUTO: Sets `left_node`.
        left_node = BinaryOpNode(left_node, op, right_node)
        # AUTO: Checks this condition.
        if left_type == "tree" or right_type == "tree":
            # AUTO: Sets `left_type`.
            left_type = "tree"

    # AUTO: Returns this result to the caller.
    return left_node, index, left_type

# AUTO: Defines function `parse_power`.
def parse_power(tokens, index):
    # AUTO: Sets `left_node, index, left_type`.
    left_node, index, left_type = parse_unary(tokens, index)

    # AUTO: Checks this condition.
    if tokens[index].type == "**":
        # AUTO: Sets `op`.
        op = tokens[index].value
        # AUTO: Sets `token`.
        token = tokens[index]

        # AUTO: Checks this condition.
        if left_type not in {"seed", "tree"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Cannot use '{op}' on type '{left_type}'. Expected 'seed' or 'tree'.",
                # AUTO: Executes this statement.
                token.line,
            # AUTO: Closes the current grouped code/data.
            )

        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `right_node, index, right_type`.
        right_node, index, right_type = parse_power(tokens, index)

        # AUTO: Checks this condition.
        if right_type not in {"seed", "tree"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Cannot use '{op}' on type '{right_type}'. Expected 'seed' or 'tree'.",
                # AUTO: Executes this statement.
                token.line,
            # AUTO: Closes the current grouped code/data.
            )

        # AUTO: Sets `left_node`.
        left_node = BinaryOpNode(left_node, op, right_node, line=token.line)
        # AUTO: Checks this condition.
        if left_type == "tree" or right_type == "tree":
            # AUTO: Sets `left_type`.
            left_type = "tree"

    # AUTO: Returns this result to the caller.
    return left_node, index, left_type

# AUTO: Defines function `parse_unary`.
def parse_unary(tokens, index):

    # AUTO: Checks this condition.
    if tokens[index].type in {"++", "--", "-", "~"}:
        # AUTO: Sets `op`.
        op = tokens[index].value
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `operand, index, operand_type`.
        operand, index, operand_type = parse_unary(tokens, index)
        # AUTO: Checks this condition.
        if op in {"++", "--", "-"} and operand_type not in {"seed", "tree"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Cannot use '{op}' on type '{operand_type}'. Expected 'seed' or 'tree'.",
                # AUTO: Executes this statement.
                tokens[index - 1].line,
            # AUTO: Closes the current grouped code/data.
            )
        # AUTO: Checks this condition.
        if op == "~" and operand_type not in {"seed", "tree"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Arithmetic negation '~' requires a numeric 'seed' or 'tree' operand, got '{operand_type}'.",
                # AUTO: Executes this statement.
                tokens[index - 1].line,
            # AUTO: Closes the current grouped code/data.
            )
        # AUTO: Returns this result to the caller.
        return UnaryOpNode(op, operand, position="pre", line=tokens[index].line), index, operand_type

    # AUTO: Sets `node, index, factor_type`.
    node, index, factor_type = parse_factor(tokens, index)

    # AUTO: Checks this condition.
    if index < len(tokens) and tokens[index].type in {"++", "--"} and tokens[index + 1].type != "id":
        # AUTO: Sets `op`.
        op = tokens[index].value
        # AUTO: Checks this condition.
        if factor_type not in {"seed", "tree"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Cannot use '{op}' on type '{factor_type}'. Expected 'seed' or 'tree'.",
                # AUTO: Executes this statement.
                tokens[index].line,
            # AUTO: Closes the current grouped code/data.
            )
        # AUTO: Sets `node`.
        node = UnaryOpNode(op, node, position="post", line=tokens[index].line)
        # AUTO: Adds into `index`.
        index += 1

    # AUTO: Returns this result to the caller.
    return node, index, factor_type

# AUTO: Defines function `parse_cast`.
def parse_cast(tokens, index):
    # AUTO: Sets `token`.
    token = tokens[index]
    # AUTO: Sets `cast_types`.
    cast_types = {"seed", "tree", "leaf", "branch", "vine"}
    # AUTO: Checks this condition.
    if token.type == "(" and tokens[index + 1].value in cast_types:
        # AUTO: Sets `target_type`.
        target_type = tokens[index + 1].value
        # AUTO: Checks this condition.
        if tokens[index + 2].type != ")":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError("Syntax Error: Missing closing parenthesis.", token.line)
        # AUTO: Adds into `index`.
        index += 3

        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression(tokens, index)

        # AUTO: Sets `cast_node`.
        cast_node = CastNode(target_type, expr_node, line=token.line)
        # AUTO: Returns this result to the caller.
        return cast_node, index, target_type

    # AUTO: Returns this result to the caller.
    return parse_factor(tokens, index)


# AUTO: Defines function `parse_factor`.
def parse_factor(tokens, index):
    # AUTO: Sets `token`.
    token = tokens[index]

    # AUTO: Checks this condition.
    if token.type == "(" and tokens[index + 1].value in {"seed", "tree", "leaf", "branch", "vine"}:
        # AUTO: Sets `node, index, cast_type`.
        node, index, cast_type = parse_cast(tokens, index)
        # AUTO: Returns this result to the caller.
        return node, index, cast_type

    # AUTO: Checks this condition.
    if token.type == "(":
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `node, index, inner_type`.
        node, index, inner_type = parse_expression_branch(tokens, index)
        # AUTO: Checks this condition.
        if tokens[index].type != ")":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError("Syntax Error: Missing closing parenthesis.", token.line)
        # AUTO: Adds into `index`.
        index += 1  
        # AUTO: Returns this result to the caller.
        return node, index, inner_type
    
    # AUTO: Checks this condition.
    if token.type in {"intlit", "dblit", "chrlit", "stringlit", "sunshine", "frost"}:
        # AUTO: Sets `node`.
        node = ASTNode("Value", token.value)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Returns this result to the caller.
        return node, index, infer_literal_type(token.type)

    # AUTO: Checks this condition.
    if token.value == "water":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: water() is an I/O statement, not an expression. It cannot be used inside an expression.", token.line)

    # AUTO: Checks this condition.
    if token.type == "id" and tokens[index + 1].type == "(":
        # AUTO: Sets `func_name`.
        func_name = token.value
        # AUTO: Sets `func_info`.
        func_info = symbol_table.lookup_function(func_name)
        # AUTO: Checks this condition.
        if isinstance(func_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Function '{func_name}' is not declared.", token.line)
        # AUTO: Sets `func_return_type`.
        func_return_type = func_info["return_type"]
        # AUTO: Sets `func_params`.
        func_params = func_info["params"]
        # AUTO: Sets `node, index`.
        node, index = parse_function_call(tokens, index, func_name, func_return_type, func_params)

        # AUTO: Returns this result to the caller.
        return node, index, func_return_type

    # AUTO: Checks the next alternate condition.
    elif (
        # AUTO: Executes this statement.
        tokens[index].type == "id" and
        # AUTO: Executes this statement.
        tokens[index + 1].type == "." and
        # AUTO: Calls `in`.
        tokens[index + 2].value in ("wilt", "bloom")
    # AUTO: Closes the current grouped code/data.
    ):
        # AUTO: Sets `func_name`.
        func_name = tokens[index + 2].value
        # AUTO: Sets `identifier`.
        identifier = tokens[index].value

        # AUTO: Sets `identifier_info`.
        identifier_info = symbol_table.lookup_variable(identifier)
        # AUTO: Checks this condition.
        if isinstance(identifier_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Variable '{identifier}' used before declaration.", token.line)

        # AUTO: Checks this condition.
        if identifier_info["type"] != "vine":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: {func_name}() can only be used on vine (string) variables, but '{identifier}' is of type {identifier_info['type']}.", token.line)

        # AUTO: Adds into `index`.
        index += 3

        # AUTO: Checks this condition.
        if func_name == "wilt":
            # AUTO: Sets `node`.
            node = SoilNode(identifier, line=token.line)
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Sets `node`.
            node = BloomNode(identifier, line=token.line)
        # AUTO: Returns this result to the caller.
        return node, index, "vine"

    # AUTO: Checks the next alternate condition.
    elif (
        # AUTO: Executes this statement.
        tokens[index].type == "id" and
        # AUTO: Executes this statement.
        tokens[index + 1].type == "."
    # AUTO: Closes the current grouped code/data.
    ):
        # AUTO: Sets `obj_name`.
        obj_name = tokens[index].value
        # AUTO: Sets `member_name`.
        member_name = tokens[index + 2].value

        # AUTO: Sets `var_info`.
        var_info = symbol_table.lookup_variable(obj_name)
        # AUTO: Checks this condition.
        if isinstance(var_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Variable '{obj_name}' used before declaration.", token.line)

        # AUTO: Sets `var_type`.
        var_type = var_info["type"]
        # AUTO: Checks this condition.
        if var_type not in symbol_table.bundle_types:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Variable '{obj_name}' is not a bundle type.", token.line)

        # AUTO: Sets `bundle_members`.
        bundle_members = symbol_table.bundle_types[var_type]
        # AUTO: Checks this condition.
        if member_name not in bundle_members:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Bundle type '{var_type}' has no member '{member_name}'.", token.line)

        # AUTO: Sets `member_type`.
        member_type = bundle_members[member_name]
        # AUTO: Adds into `index`.
        index += 3
        # AUTO: Sets `node`.
        node = MemberAccessNode(obj_name, member_name, line=token.line)

        # AUTO: Repeats while this condition is true.
        while index < len(tokens) and tokens[index].type == "." and member_type in symbol_table.bundle_types:
            # AUTO: Sets `next_member`.
            next_member = tokens[index + 1].value
            # AUTO: Sets `nested_members`.
            nested_members = symbol_table.bundle_types[member_type]
            # AUTO: Checks this condition.
            if next_member not in nested_members:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", token.line)
            # AUTO: Sets `member_type`.
            member_type = nested_members[next_member]
            # AUTO: Sets `node`.
            node = MemberAccessNode(node, next_member, line=token.line)
            # AUTO: Adds into `index`.
            index += 2

        # AUTO: Returns this result to the caller.
        return node, index, member_type


    # AUTO: Checks the next alternate condition.
    elif token.type == "id" and tokens[index + 1].type == "[":
        # AUTO: Sets `list_name`.
        list_name = token.value
        # AUTO: Sets `list_info`.
        list_info = symbol_table.lookup_variable(list_name)

        # AUTO: Checks this condition.
        if isinstance(list_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", token.line)

        # AUTO: Checks this condition.
        if not list_info["is_list"] and list_info.get("type") != "vine":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

        # AUTO: Adds into `index`.
        index += 2
        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression(tokens, index)

        # AUTO: Checks this condition.
        if tokens[index].type != "]":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError("Syntax Error: Missing closing bracket.", token.line)

        # AUTO: Sets `index_node`.
        index_node = ASTNode("Index", line=token.line)
        # AUTO: Calls `index_node.add_child`.
        index_node.add_child(expr_node)

        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `list_access_node`.
        list_access_node = ListAccessNode(list_name, index_node, line=token.line)

        # AUTO: Repeats while this condition is true.
        while index < len(tokens) and tokens[index].type == "[":
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `inner_expr, index, _`.
            inner_expr, index, _ = parse_expression(tokens, index)
            # AUTO: Checks this condition.
            if tokens[index].type != "]":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError("Syntax Error: Missing closing bracket.", token.line)
            # AUTO: Sets `inner_index`.
            inner_index = ASTNode("Index", line=token.line)
            # AUTO: Calls `inner_index.add_child`.
            inner_index.add_child(inner_expr)
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `list_access_node`.
            list_access_node = ListAccessNode(list_access_node, inner_index, line=token.line)

        # AUTO: Checks this condition.
        if index < len(tokens) and tokens[index].type == "." and list_info["type"] in symbol_table.bundle_types:
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `member_name`.
            member_name = tokens[index].value
            # AUTO: Sets `bundle_members`.
            bundle_members = symbol_table.bundle_types[list_info["type"]]
            # AUTO: Checks this condition.
            if member_name not in bundle_members:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Bundle type '{list_info['type']}' has no member '{member_name}'.", token.line)
            # AUTO: Sets `member_type`.
            member_type = bundle_members[member_name]
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `node`.
            node = ArrayMemberAccessNode(list_access_node, member_name, line=token.line)

            # AUTO: Repeats while this condition is true.
            while index < len(tokens) and tokens[index].type == "." and member_type in symbol_table.bundle_types:
                # AUTO: Sets `next_member`.
                next_member = tokens[index + 1].value
                # AUTO: Sets `nested_members`.
                nested_members = symbol_table.bundle_types[member_type]
                # AUTO: Checks this condition.
                if next_member not in nested_members:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", token.line)
                # AUTO: Sets `member_type`.
                member_type = nested_members[next_member]
                # AUTO: Sets `node`.
                node = MemberAccessNode(node, next_member, line=token.line)
                # AUTO: Adds into `index`.
                index += 2

            # AUTO: Returns this result to the caller.
            return node, index, member_type

        # AUTO: Returns this result to the caller.
        return list_access_node, index, list_info["type"]
        

    # AUTO: Checks the next alternate condition.
    elif token.type == "id":
        # AUTO: Sets `variable_info`.
        variable_info = symbol_table.lookup_variable(token.value)
        # AUTO: Checks this condition.
        if isinstance(variable_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(variable_info, token.line)
        # AUTO: Sets `is_list`.
        is_list = variable_info.get("is_list", False)
        # AUTO: Checks this condition.
        if is_list and tokens[index + 1].type != "[":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: List '{token.value}' must be indexed with '[]' in expressions.", token.line)

        # AUTO: Sets `var_type`.
        var_type = variable_info["type"]
        
        # AUTO: Sets `node`.
        node = ASTNode("Value", token.value)
        # AUTO: Adds into `index`.
        index += 1  

        # AUTO: Checks this condition.
        if index < len(tokens) and tokens[index].type in {"++", "--"}:
            # AUTO: Sets `op`.
            op = tokens[index].value
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Returns this result to the caller.
            return UnaryOpNode(op, node, position="post", line=token.line), index, var_type

        # AUTO: Returns this result to the caller.
        return node, index, var_type


    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Checks this condition.
        if token.type in {";", "}", ")", ","}:
            # AUTO: Sets `error`.
            error = f"Semantic Error: Expected an expression before '{token.value}'."
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Sets `error`.
            error = f"Semantic Error: Cannot use '{token.value}' in this expression."
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(error, token.line)


# AUTO: Defines function `_assignment_root_name`.
def _assignment_root_name(node):
    # AUTO: Checks this condition.
    if node.node_type in {"Identifier", "Value", "Object", "ListName"}:
        # AUTO: Checks this condition.
        if isinstance(node.value, ASTNode):
            # AUTO: Returns this result to the caller.
            return _assignment_root_name(node.value)
        # AUTO: Returns this result to the caller.
        return node.value
    # AUTO: Checks this condition.
    if node.node_type in {"ListAccess", "MemberAccess", "ArrayMemberAccess"}:
        # AUTO: Returns this result to the caller.
        return _assignment_root_name(node.children[0])
    # AUTO: Returns this result to the caller.
    return None


# AUTO: Defines function `_assignment_target`.
def _assignment_target(node, line):
    # AUTO: Sets `root_name`.
    root_name = _assignment_root_name(node)
    # AUTO: Sets `valid_node_types`.
    valid_node_types = {"Value", "Identifier", "ListAccess", "MemberAccess", "ArrayMemberAccess"}
    # AUTO: Sets `var_info`.
    var_info = symbol_table.lookup_variable(root_name) if root_name is not None else None

    # AUTO: Checks this condition.
    if node.node_type not in valid_node_types or isinstance(var_info, str) or var_info is None:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(
            # AUTO: Executes this statement.
            "Semantic Error: Left-hand side of assignment expression must be a modifiable variable, list element, or bundle member.",
            # AUTO: Executes this statement.
            line,
        # AUTO: Closes the current grouped code/data.
        )
    # AUTO: Checks this condition.
    if var_info.get("is_fertile", False):
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(
            # AUTO: Executes this statement.
            f"Semantic Error: Variable '{root_name}' is declared as fertile and cannot be re-assigned a value.",
            # AUTO: Executes this statement.
            line,
        # AUTO: Closes the current grouped code/data.
        )

    # AUTO: Checks this condition.
    if node.node_type == "Value":
        # AUTO: Sets `node`.
        node = ASTNode("Identifier", node.value, line=line)
    # AUTO: Returns this result to the caller.
    return node


# AUTO: Defines function `parse_assignment_expression`.
def parse_assignment_expression(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Sets `left_node, index, left_type`.
    left_node, index, left_type = parse_logical_expression(tokens, index)
    # AUTO: Checks this condition.
    if tokens[index].type not in {"=", "+=", "-=", "*=", "/=", "%="}:
        # AUTO: Returns this result to the caller.
        return left_node, index, left_type

    # AUTO: Sets `operator`.
    operator = tokens[index].type
    # AUTO: Sets `target`.
    target = _assignment_target(left_node, line)
    # AUTO: Adds into `index`.
    index += 1
    # AUTO: Sets `right_node, index, right_type`.
    right_node, index, right_type = parse_assignment_expression(tokens, index)

    # AUTO: Checks this condition.
    if operator == "=":
        # AUTO: Checks this condition.
        if not _types_compatible(left_type, right_type):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Type mismatch - cannot assign '{right_type}' value to '{left_type}' variable.",
                # AUTO: Executes this statement.
                line,
            # AUTO: Closes the current grouped code/data.
            )
        # AUTO: Sets `value_node`.
        value_node = right_node
    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Checks this condition.
        if left_type not in {"seed", "tree"} or right_type not in {"seed", "tree"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Compound assignment '{operator}' requires numeric 'seed' or 'tree' operands.",
                # AUTO: Executes this statement.
                line,
            # AUTO: Closes the current grouped code/data.
            )
        # AUTO: Checks this condition.
        if operator == "%=" and left_type != "seed":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Sets `"Semantic Error: Modulo assignment '%`.
                "Semantic Error: Modulo assignment '%=' requires a 'seed' (integer) left-hand side.",
                # AUTO: Executes this statement.
                line,
            # AUTO: Closes the current grouped code/data.
            )
        # AUTO: Sets `value_node`.
        value_node = BinaryOpNode(copy.deepcopy(target), operator[0], right_node, line=line)

    # AUTO: Returns this result to the caller.
    return AssignmentNode(target, value_node, line=line), index, left_type


# AUTO: Defines function `parse_expression_branch`.
def parse_expression_branch(tokens, index):
    # AUTO: Returns this result to the caller.
    return parse_assignment_expression(tokens, index)


# AUTO: Defines function `parse_logical_expression`.
def parse_logical_expression(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Sets `left_node, index, left_type`.
    left_node, index, left_type = parse_equality(tokens, index)

    
    # AUTO: Repeats while this condition is true.
    while tokens[index].type in {"&&", "||"}:
        # AUTO: Sets `operator`.
        operator = tokens[index].value
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `right_node, index, right_type`.
        right_node, index, right_type = parse_equality(tokens, index)

        # AUTO: Checks this condition.
        if left_type in {"vine", "leaf"} or right_type in {"vine", "leaf"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Logical operator '{operator}' is not valid for string or leaf operands.",
                # AUTO: Executes this statement.
                line,
            # AUTO: Closes the current grouped code/data.
            )

        # AUTO: Sets `left_node`.
        left_node = BinaryOpNode(left_node, operator, right_node, line=line)
        # AUTO: Sets `left_type`.
        left_type = "branch"

    # AUTO: Returns this result to the caller.
    return left_node, index, left_type


# AUTO: Defines function `parse_equality`.
def parse_equality(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Sets `left_node, index, left_type`.
    left_node, index, left_type = parse_relational(tokens, index)

    # AUTO: Repeats while this condition is true.
    while tokens[index].type in {"==", "!="}:
        # AUTO: Sets `operator`.
        operator = tokens[index].type
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `right_node, index, right_type`.
        right_node, index, right_type = parse_relational(tokens, index)

        # AUTO: Checks this condition.
        if left_type is None or right_type is None:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                "Semantic Error: Could not determine the type of an operand in equality check.",
                # AUTO: Executes this statement.
                line,
            # AUTO: Closes the current grouped code/data.
            )
        # AUTO: Sets `numeric`.
        numeric = {"seed", "tree"}
        # AUTO: Checks this condition.
        if left_type != right_type and not (left_type in numeric and right_type in numeric):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Cannot compare '{left_type}' with '{right_type}' using '{operator}'.",
                # AUTO: Executes this statement.
                line,
            # AUTO: Closes the current grouped code/data.
            )

        # AUTO: Sets `left_node`.
        left_node = BinaryOpNode(left_node, operator, right_node, line=line)
        # AUTO: Sets `left_type`.
        left_type = "branch"

    # AUTO: Returns this result to the caller.
    return left_node, index, left_type


# AUTO: Defines function `parse_relational`.
def parse_relational(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line

    # AUTO: Checks this condition.
    if tokens[index].type == "!":
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `operand_node, index, operand_type`.
        operand_node, index, operand_type = parse_relational(tokens, index)
        
        # AUTO: Checks this condition.
        if operand_type != "branch":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: ! operator can only apply to 'branch' value.", line)

        # AUTO: Returns this result to the caller.
        return UnaryOpNode("!", operand_node, line=line), index, "branch"

    # AUTO: Sets `left_node, index, left_type`.
    left_node, index, left_type = parse_expression(tokens, index)

    # AUTO: Checks this condition.
    if tokens[index].type in {"<", "<=", ">", ">="}:
        # AUTO: Sets `operator`.
        operator = tokens[index].type
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `right_node, index, right_type`.
        right_node, index, right_type = parse_expression(tokens, index)

        # AUTO: Checks this condition.
        if left_type == "vine" or right_type == "vine":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Relational operator '{operator}' is not valid for string operands. Use '==' or '!='.",
                # AUTO: Executes this statement.
                line,
            # AUTO: Closes the current grouped code/data.
            )

        # AUTO: Checks this condition.
        if left_type and right_type:
            # AUTO: Sets `numeric`.
            numeric = {"seed", "tree"}
            # AUTO: Checks this condition.
            if left_type in numeric and right_type not in numeric:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(
                    # AUTO: Executes this statement.
                    f"Semantic Error: Cannot compare '{left_type}' with '{right_type}' using '{operator}'.",
                    # AUTO: Executes this statement.
                    line,
                # AUTO: Closes the current grouped code/data.
                )
            # AUTO: Checks this condition.
            if left_type not in numeric and right_type in numeric:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(
                    # AUTO: Executes this statement.
                    f"Semantic Error: Cannot compare '{left_type}' with '{right_type}' using '{operator}'.",
                    # AUTO: Executes this statement.
                    line,
                # AUTO: Closes the current grouped code/data.
                )
            # AUTO: Checks this condition.
            if left_type != right_type and not (left_type in numeric and right_type in numeric):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(
                    # AUTO: Executes this statement.
                    f"Semantic Error: Cannot compare '{left_type}' with '{right_type}' using '{operator}'.",
                    # AUTO: Executes this statement.
                    line,
                # AUTO: Closes the current grouped code/data.
                )

        # AUTO: Sets `left_node`.
        left_node = BinaryOpNode(left_node, operator, right_node, line=line)
        # AUTO: Sets `left_type`.
        left_type = "branch"

        # AUTO: Returns this result to the caller.
        return left_node, index, left_type
    
    # AUTO: Returns this result to the caller.
    return left_node, index, left_type


# AUTO: Defines function `check_lwk`.
def check_lwk(tokens, index):
    # AUTO: Sets `start_index`.
    start_index = index 
    # AUTO: Sets `op_found`.
    op_found = False

    # AUTO: Repeats while this condition is true.
    while tokens[index].type != ")":
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Checks this condition.
        if tokens[index].type in {"<", "<=", ">", ">=", "==", "!=", "&&", "||", "sunshine", "frost"}:
            # AUTO: Sets `op_found`.
            op_found = True
        # AUTO: Checks this condition.
        if tokens[index].type == "id":
            # AUTO: Sets `var_info`.
            var_info = symbol_table.lookup_variable(tokens[index].value)
            # AUTO: Checks this condition.
            if isinstance(var_info, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Variable '{tokens[index].value}' used before declaration.", tokens[index].line)
            # AUTO: Checks this condition.
            if var_info["type"] == "branch":
                # AUTO: Sets `op_found`.
                op_found = True
        

    # AUTO: Checks this condition.
    if tokens[index].type in {"<", "<=", ">", ">=", "==", "!=", "&&", "||"}:
        # AUTO: Sets `op_found`.
        op_found = True

    # AUTO: Returns this result to the caller.
    return op_found, start_index

# AUTO: Defines function `parse_operand`.
def parse_operand(tokens, index):
    # AUTO: Sets `token`.
    token = tokens[index]
    # AUTO: Sets `line`.
    line = token.line

    # AUTO: Checks this condition.
    if token.value == "water":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: water() is an I/O statement, not an expression. It cannot be used inside an expression.", token.line)

    # AUTO: Checks this condition.
    if token.type == "(":
        # AUTO: Checks this condition.
        if tokens[index+1].value in {"seed", "tree"}:
            # AUTO: Sets `expr_type`.
            expr_type = tokens[index+1].value
            # AUTO: Sets `expr_node, index, _`.
            expr_node, index, _ = parse_expression(tokens, index)
            # AUTO: Returns this result to the caller.
            return expr_node, index, expr_type
        
        # AUTO: Checks the next alternate condition.
        elif tokens[index + 1].type == "id":
            # AUTO: Sets `var_name`.
            var_name = tokens[index +1].value
            # AUTO: Sets `var_info`.
            var_info = symbol_table.lookup_variable(var_name)
            # AUTO: Checks this condition.
            if isinstance(var_info, str):
                # AUTO: Sets `var_type`.
                var_type = None
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Sets `var_type`.
                var_type = var_info["type"]


            # AUTO: Sets `is_lwk, index`.
            is_lwk, index = check_lwk(tokens, index)
            # AUTO: Checks this condition.
            if not is_lwk:
                # AUTO: Sets `expr_node, index, _`.
                expr_node, index, _ = parse_expression(tokens, index)
                # AUTO: Subtracts from `index`.
                index -= 1
                # AUTO: Sets `expr_type`.
                expr_type = "seed"
                
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Sets `expr_node, index, _`.
                expr_node, index, _ = parse_expression_branch(tokens, index)
                # AUTO: Sets `expr_type`.
                expr_type = "branch"

            # AUTO: Sets `is_lwk, index`.
            is_lwk, index = check_lwk(tokens, index)
       
        
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Returns this result to the caller.
        return expr_node, index, expr_type

    # AUTO: Checks this condition.
    if token.type in {"intlit", "dblit"}:
        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression(tokens, index)
        # AUTO: Returns this result to the caller.
        return expr_node, index, infer_literal_type(token.type)

    # AUTO: Checks this condition.
    if token.type in {"chrlit", "stringlit"}:
        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression(tokens, index)
        # AUTO: Returns this result to the caller.
        return expr_node, index, infer_literal_type(token.type)


    # AUTO: Checks this condition.
    if token.type in {"sunshine", "frost"}:
        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression(tokens, index)
        # AUTO: Returns this result to the caller.
        return expr_node, index, infer_literal_type(token.type)

    # AUTO: Checks this condition.
    if token.type == "id" and tokens[index + 1].type == "(":
        # AUTO: Sets `func_name`.
        func_name = tokens[index].value
        # AUTO: Sets `func_info`.
        func_info = symbol_table.lookup_function(func_name)

        # AUTO: Checks this condition.
        if isinstance(func_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Function '{func_name}' is not declared.", line)
        
        # AUTO: Sets `func_return_type`.
        func_return_type = func_info["return_type"]
        # AUTO: Sets `func_params`.
        func_params = func_info["params"]

        # AUTO: Sets `func_node, index`.
        func_node, index = parse_function_call(tokens, index, func_name, func_return_type, func_params)
        # AUTO: Returns this result to the caller.
        return func_node, index, func_return_type
    
    # AUTO: Checks this condition.
    if token.type == "id" and tokens[index + 1].type == "[":
        # AUTO: Sets `list_name`.
        list_name = token.value
        # AUTO: Sets `list_info`.
        list_info = symbol_table.lookup_variable(list_name)

        # AUTO: Checks this condition.
        if isinstance(list_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", token.line)

        # AUTO: Checks this condition.
        if not list_info["is_list"] and list_info.get("type") != "vine":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

        # AUTO: Sets `expr_node, index, expr_type`.
        expr_node, index, expr_type = parse_expression(tokens, index)
        # AUTO: Returns this result to the caller.
        return expr_node, index, expr_type

    # AUTO: Checks this condition.
    if token.type in {"intlit", "dblit"}:
        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression(tokens, index)
        # AUTO: Returns this result to the caller.
        return expr_node, index, infer_literal_type(token.type)

    # AUTO: Checks this condition.
    if token.type == "chrlit":
        # AUTO: Sets `expr_node, index`.
        expr_node, index = parse_expression_leaf(tokens, index)
        # AUTO: Returns this result to the caller.
        return expr_node, index, infer_literal_type(token.type)

    # AUTO: Checks this condition.
    if token.type == "stringlit":
        # AUTO: Returns this result to the caller.
        return ASTNode("Value", token.value, line=line), index + 1, "vine"

    # AUTO: Checks this condition.
    if token.type in {"sunshine", "frost"}:
        # AUTO: Returns this result to the caller.
        return ASTNode("Value", token.value, line=line), index + 1, "branch"

    # AUTO: Checks this condition.
    if token.type == "id" and tokens[index + 1].type == ".":
        # AUTO: Sets `var_info`.
        var_info = symbol_table.lookup_variable(token.value)
        # AUTO: Checks this condition.
        if not isinstance(var_info, str) and var_info["type"] in symbol_table.bundle_types:
            # AUTO: Sets `expr_node, index, expr_type`.
            expr_node, index, expr_type = parse_expression(tokens, index)
            # AUTO: Returns this result to the caller.
            return expr_node, index, expr_type

    # AUTO: Checks this condition.
    if token.type == "id":
        # AUTO: Sets `var_info`.
        var_info = symbol_table.lookup_variable(token.value)
        # AUTO: Checks this condition.
        if isinstance(var_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Variable '{token.value}' used before declaration.", line)
        
        # AUTO: Sets `var_type`.
        var_type = var_info["type"]
        # AUTO: Sets `is_list`.
        is_list = var_info.get("is_list", False)

        # AUTO: Checks this condition.
        if is_list and tokens[index + 1].type != "[":
            # AUTO: Checks this condition.
            if tokens[index + 1].type in {"+", "-", "*", "/", "%", "**", "==", "!=", ">", "<", ">=", "<="}:
                # AUTO: Sets `op_token`.
                op_token = tokens[index + 1]
                # AUTO: Checks this condition.
                if index + 2 < len(tokens) and tokens[index + 2].type == "id":
                    # AUTO: Sets `rhs_info`.
                    rhs_info = symbol_table.lookup_variable(tokens[index + 2].value)
                    # AUTO: Checks this condition.
                    if not isinstance(rhs_info, str) and rhs_info.get("is_list", False):
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(
                            # AUTO: Executes this statement.
                            f"Semantic Error: Cannot use '{op_token.value}' operator on arrays '{token.value}' and '{tokens[index + 2].value}'. Arrays must be indexed with '[]'.",
                            # AUTO: Executes this statement.
                            line,
                        # AUTO: Closes the current grouped code/data.
                        )
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: List '{token.value}' must be indexed with '[]' in expressions.", line)
    
        # AUTO: Checks this condition.
        if var_type in {"seed", "tree", "branch"}:
            # AUTO: Sets `expr_node, index, _`.
            expr_node, index, _ = parse_expression(tokens, index)
            
            # AUTO: Returns this result to the caller.
            return expr_node, index, var_type

        # AUTO: Checks the next alternate condition.
        elif var_type == "leaf":
            # AUTO: Sets `expr_node, index`.
            expr_node, index = parse_expression_leaf(tokens, index)
            # AUTO: Returns this result to the caller.
            return expr_node, index, var_type

        # AUTO: Checks the next alternate condition.
        elif var_type == "vine":
            # AUTO: Sets `expr_node, index, _`.
            expr_node, index, _ = parse_expression(tokens, index)
            # AUTO: Returns this result to the caller.
            return expr_node, index, "vine"

        # AUTO: Checks the next alternate condition.
        elif var_type == "branch":
            # AUTO: Returns this result to the caller.
            return ASTNode("Value", token.value, line=line), index + 1, var_type

        # AUTO: Checks the next alternate condition.
        elif var_type in symbol_table.bundle_types:
            # AUTO: Sets `expr_node, index, _`.
            expr_node, index, _ = parse_expression(tokens, index)
            # AUTO: Returns this result to the caller.
            return expr_node, index, var_type

        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Unsupported type '{var_type}'.", line)

    # AUTO: Checks this condition.
    if token.type in {";", "}", ")", ","}:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Expected an expression before '{token.value}'.", line)
    # AUTO: Stops this flow by raising an error.
    raise SemanticError(f"Semantic Error: Cannot use '{token.value}' in this expression.", line)


# AUTO: Defines function `infer_literal_type`.
def infer_literal_type(token_type):
    # AUTO: Checks this condition.
    if token_type == "intlit":
        # AUTO: Returns this result to the caller.
        return "seed"
    # AUTO: Checks this condition.
    if token_type == "dblit":
        # AUTO: Returns this result to the caller.
        return "tree"
    # AUTO: Checks this condition.
    if token_type == "stringlit":
        # AUTO: Returns this result to the caller.
        return "vine"
    # AUTO: Checks this condition.
    if token_type == "chrlit":
        # AUTO: Returns this result to the caller.
        return "leaf"
    # AUTO: Checks this condition.
    if token_type in {"sunshine", "frost"}:
        # AUTO: Returns this result to the caller.
        return "branch"
    # AUTO: Returns this result to the caller.
    return None

# AUTO: Defines function `parse_assignment`.
def parse_assignment(tokens, index, var_name, var_type):
    # AUTO: Sets `line`.
    line = tokens[index].line

    # AUTO: Sets `var_info`.
    var_info = symbol_table.lookup_variable(var_name)
    # AUTO: Checks this condition.
    if var_info and var_info["is_fertile"]:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile.", line)

    # AUTO: Checks this condition.
    if tokens[index].value == "water":
        # AUTO: Sets `water_line`.
        water_line = tokens[index].line
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Checks this condition.
        if tokens[index].type != "(":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected '(' after water.", water_line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `water_type`.
        water_type = None
        # AUTO: Checks this condition.
        if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
            # AUTO: Sets `water_type`.
            water_type = tokens[index].value
            # AUTO: Adds into `index`.
            index += 1
        # AUTO: Checks this condition.
        if tokens[index].type != ")":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter (e.g., water(seed)).", water_line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Checks this condition.
        if water_type and not _types_compatible(var_type, water_type):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Type mismatch — cannot assign water({water_type}) to '{var_type}' variable.", water_line)
        # AUTO: Sets `value_node`.
        value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=water_line)
    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Sets `value_node, index`.
        value_node, index = parse_expression_type(tokens, index, var_type)

    # AUTO: Sets `assignment_node`.
    assignment_node = AssignmentNode(var_name, value_node, line=line)

    # AUTO: Returns this result to the caller.
    return assignment_node, index


# AUTO: Defines function `parse_function_call`.
def parse_function_call(tokens, index, func_name, func_type, func_params):
    # AUTO: Sets `line`.
    line = tokens[index].line
    
    # AUTO: Adds into `index`.
    index += 2
    # AUTO: Sets `args_node`.
    args_node = ASTNode("Arguments")
    # AUTO: Sets `provided_args`.
    provided_args = []  
    # AUTO: Sets `expected_params`.
    expected_params = func_params  
    
    # AUTO: Repeats while this condition is true.
    while tokens[index].type != ")":
        # AUTO: Checks this condition.
        if len(provided_args) >= len(expected_params):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Too many arguments in function call '{func_name}'.", line)

        # AUTO: Sets `expected_type`.
        expected_type = expected_params[len(provided_args)].children[0].value 
        
        # AUTO: Sets `expected_param`.
        expected_param = expected_params[len(provided_args)]
        # AUTO: Calls `any`.
        is_array_param = any(child.node_type == "ArrayParam" for child in expected_param.children)

        # AUTO: Checks this condition.
        if is_array_param:
            # AUTO: Checks this condition.
            if tokens[index].type != "id":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Expected array variable for parameter {len(provided_args) + 1} of '{func_name}'.", line)
            # AUTO: Sets `arg_name`.
            arg_name = tokens[index].value
            # AUTO: Sets `arg_info`.
            arg_info = symbol_table.lookup_variable(arg_name)
            # AUTO: Checks this condition.
            if isinstance(arg_info, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(arg_info, line)
            # AUTO: Checks this condition.
            if not arg_info.get("is_list", False):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Argument '{arg_name}' is not an array. Parameter {len(provided_args) + 1} of '{func_name}' expects an array.", line)
            # AUTO: Checks this condition.
            if arg_info["type"] != expected_type:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Array argument '{arg_name}' is of type '{arg_info['type']}', but parameter expects '{expected_type}'.", line)
            # AUTO: Sets `expr_node`.
            expr_node = ASTNode("Identifier", arg_name, line=line)
            # AUTO: Adds into `index`.
            index += 1
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Sets `expr_node, index`.
            expr_node, index = parse_expression_type(tokens, index, expected_type)

        # AUTO: Sets `arg_node`.
        arg_node = ASTNode("Argument")
        # AUTO: Calls `arg_node.add_child`.
        arg_node.add_child(expr_node)
        # AUTO: Calls `args_node.add_child`.
        args_node.add_child(arg_node)

        # AUTO: Appends a value to a list.
        provided_args.append((arg_node, expected_type))

   
        # AUTO: Checks this condition.
        if tokens[index].type == ",":
            # AUTO: Adds into `index`.
            index += 1 

    # AUTO: Adds into `index`.
    index += 1 

    # AUTO: Checks this condition.
    if tokens[index].type in {"++", "--"}:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Unary operators cannot be applied to function calls.", line)

    # AUTO: Checks this condition.
    if len(provided_args) != len(expected_params):
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Function '{func_name}' expects {len(expected_params)} arguments, but {len(provided_args)} were provided.", line)

    # AUTO: Starts a loop over these values.
    for i, (arg_node, arg_type) in enumerate(provided_args):
        # AUTO: Sets `expected_type`.
        expected_type = expected_params[i].children[0].value

        # AUTO: Checks this condition.
        if expected_type in {"seed", "tree"} and arg_type == "seed":
            # AUTO: Skips to the next loop iteration.
            continue 
        
        # AUTO: Checks this condition.
        if arg_type != expected_type:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Argument {i+1} of '{func_name}' should be '{expected_type}', but got '{arg_type}'.", line)

    # AUTO: Returns this result to the caller.
    return FunctionCallNode(func_name, args_node.children, line=line), index


# AUTO: Defines function `parse_water_statement`.
def parse_water_statement(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Checks this condition.
    if tokens[index].type != "(":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '(' after water.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Checks this condition.
    if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
        # AUTO: Sets `water_type`.
        water_type = tokens[index].value
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Checks this condition.
        if tokens[index].type != ")":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter or a variable name.", line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Checks this condition.
        if tokens[index].type != ";":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `input_node`.
        input_node = ASTNode("Input", f"water({water_type})", line=line)
        # AUTO: Returns this result to the caller.
        return input_node, index

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type == ")":
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Checks this condition.
        if tokens[index].type != ";":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `input_node`.
        input_node = ASTNode("Input", "water()", line=line)
        # AUTO: Returns this result to the caller.
        return input_node, index

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type == "id":
        # AUTO: Sets `var_name`.
        var_name = tokens[index].value
        # AUTO: Sets `var_info`.
        var_info = symbol_table.lookup_variable(var_name)
        # AUTO: Checks this condition.
        if isinstance(var_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(var_info, line)
        # AUTO: Checks this condition.
        if var_info.get("is_fertile", False):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-assigned a value.", line)
        # AUTO: Sets `var_type`.
        var_type = var_info["type"]
        # AUTO: Adds into `index`.
        index += 1

        # AUTO: Checks this condition.
        if tokens[index].type == "[":
            # AUTO: Checks this condition.
            if not var_info.get("is_list", False) and var_info.get("type") != "vine":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Variable '{var_name}' is not a list.", line)
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `index_expr, index, idx_type`.
            index_expr, index, idx_type = parse_equality(tokens, index)
            # AUTO: Checks this condition.
            if idx_type is not None and idx_type != "seed":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: List index must be of type 'seed', got '{idx_type}'.", line)
            # AUTO: Checks this condition.
            if tokens[index].type != "]":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
            # AUTO: Adds into `index`.
            index += 1

            # AUTO: Sets `index_wrapper`.
            index_wrapper = ASTNode("Index", line=line)
            # AUTO: Calls `index_wrapper.add_child`.
            index_wrapper.add_child(index_expr)
            # AUTO: Sets `list_access_node`.
            list_access_node = ListAccessNode(var_name, index_wrapper, line=line)

            # AUTO: Repeats while this condition is true.
            while tokens[index].type == "[":
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Sets `inner_expr, index, inner_type`.
                inner_expr, index, inner_type = parse_equality(tokens, index)
                # AUTO: Checks this condition.
                if inner_type is not None and inner_type != "seed":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: List index must be of type 'seed', got '{inner_type}'.", line)
                # AUTO: Checks this condition.
                if tokens[index].type != "]":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Sets `inner_wrapper`.
                inner_wrapper = ASTNode("Index", line=line)
                # AUTO: Calls `inner_wrapper.add_child`.
                inner_wrapper.add_child(inner_expr)
                # AUTO: Sets `list_access_node`.
                list_access_node = ListAccessNode(list_access_node, inner_wrapper, line=line)

            # AUTO: Checks this condition.
            if tokens[index].type != ")":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Expected ')' after water(arr[i]).", line)
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Checks this condition.
            if tokens[index].type != ";":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `input_node`.
            input_node = ASTNode("Input", f"water({var_type})", line=line)
            # AUTO: Sets `assignment_node`.
            assignment_node = AssignmentNode(list_access_node, input_node, line=line)
            # AUTO: Returns this result to the caller.
            return assignment_node, index

        # AUTO: Checks this condition.
        if tokens[index].type != ")":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: water() accepts only a single variable name or type parameter.", line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Checks this condition.
        if tokens[index].type != ";":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        # AUTO: Adds into `index`.
        index += 1

        # AUTO: Sets `input_node`.
        input_node = ASTNode("Input", f"water({var_type})", line=line)
        # AUTO: Sets `value_ident`.
        value_ident = ASTNode("Identifier", var_name, line=line)
        # AUTO: Sets `assignment_node`.
        assignment_node = AssignmentNode(var_name, input_node, line=line)
        # AUTO: Returns this result to the caller.
        return assignment_node, index

    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Invalid argument to water(). Expected a variable name or type.", line)


# AUTO: Defines function `parse_print`.
def parse_print(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Checks this condition.
    if tokens[index].type != "(":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '(' after plant statement.", line)
    # AUTO: Adds into `index`.
    index += 1
    # AUTO: Sets `token`.
    token = tokens[index]

    # AUTO: Sets `args`.
    args = []
    # AUTO: Sets `placeholder_count`.
    placeholder_count = 0

    # AUTO: Checks this condition.
    if tokens[index].type == "stringlit":
        # AUTO: Sets `format_node, index, placeholder_count`.
        format_node, index, placeholder_count = parse_string_concatenation(tokens, index) 
        # AUTO: Appends a value to a list.
        args.append(format_node)


    # AUTO: Checks the next alternate condition.
    elif tokens[index].type == "id":
        # AUTO: Sets `identif_name`.
        identif_name = tokens[index].value

        # AUTO: Checks this condition.
        if tokens[index + 1].type == "(":
            # AUTO: Sets `func_name`.
            func_name = identif_name
            # AUTO: Sets `func_info`.
            func_info = symbol_table.lookup_function(func_name)
            # AUTO: Checks this condition.
            if isinstance(func_info, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Function '{func_name}' is not defined.", line)
            # AUTO: Checks this condition.
            if func_info["return_type"] in {"seed", "tree"}:
                # AUTO: Sets `expr_node, index, _`.
                expr_node, index, _ = parse_expression(tokens, index)
                # AUTO: Appends a value to a list.
                args.append(expr_node)
            # AUTO: Checks the next alternate condition.
            elif func_info["return_type"] in {"vine"}:
                # AUTO: Sets `expr_node, index`.
                expr_node, index = parse_expression_vine(tokens, index)
                # AUTO: Appends a value to a list.
                args.append(expr_node)
            # AUTO: Checks the next alternate condition.
            elif func_info["return_type"] in {"leaf"}:
                # AUTO: Sets `expr_node, index`.
                expr_node, index = parse_expression_leaf(tokens, index)
                # AUTO: Appends a value to a list.
                args.append(expr_node)
            # AUTO: Checks the next alternate condition.
            elif func_info["return_type"] in {"branch"}:
                # AUTO: Sets `expr_node, index, _`.
                expr_node, index, _ = parse_expression_branch(tokens, index)
                # AUTO: Appends a value to a list.
                args.append(expr_node)
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Function '{func_name}' returns invalid type '{func_info['return_type']}'.", line)


        # AUTO: Checks the next alternate condition.
        elif tokens[index].type == "id" and tokens[index + 1].type == "[":
            # AUTO: Sets `list_name`.
            list_name = token.value
            # AUTO: Sets `list_info`.
            list_info = symbol_table.lookup_variable(list_name)

            # AUTO: Checks this condition.
            if isinstance(list_info, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", tokens[index].line)

            # AUTO: Sets `list_type`.
            list_type = list_info["type"]
            # AUTO: Sets `start_index`.
            start_index = index

            # AUTO: Checks this condition.
            if not list_info["is_list"] and list_info.get("type") != "vine":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", tokens[index].line)

            # AUTO: Adds into `index`.
            index += 2
            # AUTO: Sets `expr_node, index, _`.
            expr_node, index, _ = parse_expression(tokens, index)

            # AUTO: Checks this condition.
            if tokens[index].type != "]":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError("Syntax Error: Missing closing bracket.", tokens[index].line)

            # AUTO: Sets `index_node`.
            index_node = ASTNode("Index", line=tokens[index].line)
            # AUTO: Calls `index_node.add_child`.
            index_node.add_child(expr_node)

            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `list_access_node`.
            list_access_node = ListAccessNode(list_name, index_node, line=tokens[index].line)

            # AUTO: Checks this condition.
            if list_type in {"seed", "tree"} or list_type in symbol_table.bundle_types:
                # AUTO: Sets `expr_node, index, _`.
                expr_node, index, _ = parse_expression(tokens, start_index)
                # AUTO: Appends a value to a list.
                args.append(expr_node)

            # AUTO: Checks the next alternate condition.
            elif list_info["is_list"]:
                # AUTO: Appends a value to a list.
                args.append(list_access_node)
            

        # AUTO: Runs when previous condition did not pass.
        else:   
            # AUTO: Sets `arg_info`.
            arg_info = symbol_table.lookup_variable(identif_name)
            # AUTO: Checks this condition.
            if isinstance(arg_info, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Variable '{identif_name}' used before declaration.", line)
            
            # AUTO: Checks this condition.
            if tokens[index + 1].type == "." and arg_info["type"] in symbol_table.bundle_types:
                # AUTO: Sets `expr_node, index, _`.
                expr_node, index, _ = parse_expression(tokens, index)
                # AUTO: Appends a value to a list.
                args.append(expr_node)

            # AUTO: Checks the next alternate condition.
            elif arg_info["type"] in {"vine", "leaf"} and tokens[index + 1].type == "`":
                # AUTO: Sets `expr_node, index, _`.
                expr_node, index, _ = parse_expression_branch(tokens, index)
                # AUTO: Appends a value to a list.
                args.append(expr_node)
            
            # AUTO: Checks the next alternate condition.
            elif arg_info["type"] in {"seed", "tree"}:
                # AUTO: Sets `expr_node, index, _`.
                expr_node, index, _ = parse_expression_branch(tokens, index)
                # AUTO: Appends a value to a list.
                args.append(expr_node)
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Sets `args.append(ASTNode("Value", identif_name, line`.
                args.append(ASTNode("Value", identif_name, line=line))
                
    # AUTO: Checks the next alternate condition.
    elif tokens[index].type in {"intlit", "dblit"}:
        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression_branch(tokens, index)
        # AUTO: Appends a value to a list.
        args.append(expr_node)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type in {"sunshine", "frost", "!"}:
        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression_branch(tokens, index)
        # AUTO: Appends a value to a list.
        args.append(expr_node)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type in {"chrlit"}:
        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression_branch(tokens, index)
        # AUTO: Appends a value to a list.
        args.append(expr_node)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type in {"("}:
        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression_branch(tokens, index)
        # AUTO: Appends a value to a list.
        args.append(expr_node)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type in {"++", "--", "-"}:
        # AUTO: Sets `expr_node, index, _`.
        expr_node, index, _ = parse_expression(tokens, index)
        # AUTO: Appends a value to a list.
        args.append(expr_node)

    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Expected valid argument in plant statement.", line)

    # AUTO: Sets `actual_args`.
    actual_args = []
    # AUTO: Repeats while this condition is true.
    while tokens[index].type == ",":
        # AUTO: Adds into `index`.
        index += 1
        
        # AUTO: Checks this condition.
        if tokens[index].type in {"intlit", "dblit", "-"}:
            # AUTO: Sets `arg_node, index, _`.
            arg_node, index, _ = parse_expression_branch(tokens, index)
            # AUTO: Appends a value to a list.
            actual_args.append(arg_node)


        # AUTO: Checks the next alternate condition.
        elif tokens[index].type == "id" and tokens[index + 1].type == "[":
            # AUTO: Sets `start_index`.
            start_index = index
            # AUTO: Sets `list_name`.
            list_name = tokens[index].value
            # AUTO: Sets `list_info`.
            list_info = symbol_table.lookup_variable(list_name)
            # AUTO: Sets `list_type`.
            list_type = list_info["type"]
            # AUTO: Sets `is_list`.
            is_list = list_info["is_list"]
            
            # AUTO: Checks this condition.
            if isinstance(list_info, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", tokens[index].line)

            # AUTO: Checks this condition.
            if not list_info["is_list"] and list_info.get("type") != "vine":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", tokens[index].line)

            # AUTO: Adds into `index`.
            index += 2
            # AUTO: Sets `expr_node, index, _`.
            expr_node, index, _ = parse_expression_branch(tokens, index)

            # AUTO: Checks this condition.
            if tokens[index].type != "]":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError("Syntax Error: Missing closing bracket.", tokens[index].line)

            # AUTO: Sets `index_node`.
            index_node = ASTNode("Index", line=tokens[index].line)
            # AUTO: Calls `index_node.add_child`.
            index_node.add_child(expr_node)

            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Sets `list_access_node`.
            list_access_node = ListAccessNode(list_name, index_node, line=tokens[index].line)
            
            # AUTO: Checks this condition.
            if list_type in {"seed", "tree"}:
                # AUTO: Sets `arg_node, index, _`.
                arg_node, index, _ = parse_expression(tokens, start_index)
                # AUTO: Appends a value to a list.
                actual_args.append(arg_node)
                
            # AUTO: Checks the next alternate condition.
            elif is_list:
                # AUTO: Appends a value to a list.
                actual_args.append(list_access_node)
            

        # AUTO: Checks the next alternate condition.
        elif tokens[index].type == "id" and tokens[index+1].type == "(":
            # AUTO: Sets `func_name`.
            func_name = tokens[index].value
            # AUTO: Sets `func_info`.
            func_info = symbol_table.lookup_function(func_name)
            # AUTO: Sets `index_start`.
            index_start = index

            # AUTO: Checks this condition.
            if isinstance(func_info, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Function '{func_name}' is not declared.", line)
            
            # AUTO: Sets `func_return_type`.
            func_return_type = func_info["return_type"]
            # AUTO: Sets `func_params`.
            func_params = func_info["params"]

            # AUTO: Sets `func_node, index`.
            func_node, index = parse_function_call(tokens, index, func_name, func_return_type, func_params)
            # AUTO: Checks this condition.
            if func_return_type in {"seed", "tree"}:
                # AUTO: Sets `expr_node, index, _`.
                expr_node, index, _ = parse_expression(tokens, index_start)
                # AUTO: Appends a value to a list.
                actual_args.append(expr_node)

            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Appends a value to a list.
                actual_args.append(func_node)
            
            
        # AUTO: Checks the next alternate condition.
        elif tokens[index].type == "id":
            # AUTO: Sets `arg_name`.
            arg_name = tokens[index].value
            # AUTO: Sets `arg_info`.
            arg_info = symbol_table.lookup_variable(arg_name)
            
            # AUTO: Checks this condition.
            if isinstance(arg_info, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Variable '{arg_name}' used before declaration.", line)
            
            # AUTO: Checks this condition.
            if arg_info["is_list"]:
                # AUTO: Checks this condition.
                if tokens[index + 1].type != "[":
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: List '{arg_name}' must be indexed with '[]' in expressions.", line)
                
            # AUTO: Checks this condition.
            if tokens[index + 1].type == "." and arg_info["type"] in symbol_table.bundle_types:
                # AUTO: Sets `arg_node, index, _`.
                arg_node, index, _ = parse_expression(tokens, index)
                # AUTO: Appends a value to a list.
                actual_args.append(arg_node)

            # AUTO: Checks the next alternate condition.
            elif arg_info["type"] in {"seed", "tree"}:
                # AUTO: Sets `arg_node, index, _`.
                arg_node, index, _ = parse_expression_branch(tokens, index)
                # AUTO: Appends a value to a list.
                actual_args.append(arg_node)

            # AUTO: Checks the next alternate condition.
            elif arg_info["type"] in {"vine", "leaf"} and tokens[index + 1].type == "`":
                # AUTO: Sets `arg_node, index, _`.
                arg_node, index, _ = parse_expression_branch(tokens, index)
                # AUTO: Appends a value to a list.
                actual_args.append(arg_node)
                
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Sets `actual_args.append(ASTNode("Value", arg_name, line`.
                actual_args.append(ASTNode("Value", arg_name, line=line))
                # AUTO: Adds into `index`.
                index += 1
            
        # AUTO: Checks the next alternate condition.
        elif tokens[index].type in {"("}:
            # AUTO: Sets `arg_node, index, _`.
            arg_node, index, _ = parse_expression_branch(tokens, index)
            # AUTO: Appends a value to a list.
            actual_args.append(arg_node)

        # AUTO: Checks the next alternate condition.
        elif tokens[index].type == "stringlit":
            # AUTO: Sets `arg_node, index, _`.
            arg_node, index, _ = parse_string_concatenation(tokens, index)
            # AUTO: Appends a value to a list.
            actual_args.append(arg_node)

        # AUTO: Checks the next alternate condition.
        elif tokens[index].type in {"chrlit"}:
            # AUTO: Sets `arg_node, index, _`.
            arg_node, index, _ = parse_expression_branch(tokens, index)
            # AUTO: Appends a value to a list.
            actual_args.append(arg_node)

        # AUTO: Checks the next alternate condition.
        elif tokens[index].type in {"sunshine", "frost", "!"}:
            # AUTO: Sets `arg_node, index, _`.
            arg_node, index, _ = parse_expression_branch(tokens, index)
            # AUTO: Appends a value to a list.
            actual_args.append(arg_node)

        # AUTO: Checks the next alternate condition.
        elif tokens[index].type in {"++", "--"}:
            # AUTO: Sets `arg_node, index, _`.
            arg_node, index, _ = parse_expression(tokens, index)
            # AUTO: Appends a value to a list.
            actual_args.append(arg_node)

        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Expected valid argument after ',' in plant statement.", line)

    # AUTO: Checks this condition.
    if placeholder_count > 15:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Exceeded maximum amount of 15 arguments in plant statement.", line)

    # AUTO: Checks this condition.
    if placeholder_count > 0 and placeholder_count != len(actual_args):
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Found {len(actual_args)} argument(s). Expected {placeholder_count} argument(s).", line)
    
    # AUTO: Calls `args.extend`.
    args.extend(actual_args)

    # AUTO: Checks this condition.
    if tokens[index].type != ")":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Expected ')' after {tokens[index-1].value} in plant statement.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Returns this result to the caller.
    return PrintNode(args, line=line), index

# AUTO: Defines function `parse_string_concatenation`.
def parse_string_concatenation(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line

    # AUTO: Checks this condition.
    if tokens[index].type != "stringlit":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: String concatenation must start with a string literal.", line)
    
    # AUTO: Sets `format_string`.
    format_string = tokens[index].value
    # AUTO: Sets `raw_string`.
    raw_string = format_string.replace("\\{", "").replace("\\}", "")
    # AUTO: Checks this condition.
    if "{" in raw_string or "}" in raw_string:
        # AUTO: Checks this condition.
        if raw_string.count("{") != raw_string.count("}"):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Invalid string literal '{format_string}' in plant().", line)
        # AUTO: Sets `matches`.
        matches = re.findall(r"\{[^}]*\}", raw_string)

        # AUTO: Starts a loop over these values.
        for match in matches:
            # AUTO: Checks this condition.
            if match != "{}":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Syntax Error: Placeholders {{}} must be adjacent to each other within the string literal.", line)

    # AUTO: Sets `placeholder_count`.
    placeholder_count = raw_string.count("{}")
    # AUTO: Sets `left_node`.
    left_node = ASTNode("FormattedString", tokens[index].value, line=line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Repeats while this condition is true.
    while index < len(tokens) and tokens[index].type == "`":
        # AUTO: Sets `concat_op`.
        concat_op = tokens[index].value
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Checks this condition.
        if tokens[index].type not in {"stringlit", "chrlit", "id"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Only values of type vine or leaf can be concatenated in plant().", line)

        # AUTO: Checks this condition.
        if tokens[index].type == "id":
            # AUTO: Sets `var_name`.
            var_name = tokens[index].value
            # AUTO: Sets `var_info`.
            var_info = symbol_table.lookup_variable(var_name)
            # AUTO: Checks this condition.
            if isinstance(var_info, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)
            # AUTO: Checks this condition.
            if var_info["type"] not in {"vine", "leaf"}:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Variable '{var_name}' with type {var_info['type']} cannot be concatenated in plant().", line)

        # AUTO: Sets `format_string`.
        format_string = tokens[index].value
        # AUTO: Sets `raw_string`.
        raw_string = format_string.replace("\\{", "").replace("\\}", "")
        
        # AUTO: Checks this condition.
        if "{" in raw_string or "}" in raw_string:
            # AUTO: Checks this condition.
            if raw_string.count("{") != raw_string.count("}"):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Invalid string literal '{format_string}' in plant().", line)
            # AUTO: Checks this condition.
            if "{}" not in raw_string:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Syntax Error: Placeholders {{}} must be adjacent within the string literal.", line)
        
        # AUTO: Adds into `placeholder_count`.
        placeholder_count += raw_string.count("{}")
        # AUTO: Checks this condition.
        if tokens[index].type == "id":
            # AUTO: Sets `right_node`.
            right_node = ASTNode("Identifier", tokens[index].value, line=line)
        # AUTO: Checks the next alternate condition.
        elif tokens[index].type == "chrlit":
            # AUTO: Sets `right_node`.
            right_node = ASTNode("Value", tokens[index].value, line=line)
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Sets `right_node`.
            right_node = ASTNode("FormattedString", tokens[index].value, line=line)
        # AUTO: Adds into `index`.
        index += 1

        # AUTO: Sets `left_node`.
        left_node = BinaryOpNode(left_node, concat_op, right_node, line=line)

    # AUTO: Returns this result to the caller.
    return left_node, index, placeholder_count


# AUTO: Defines function `parse_fertile`.
def parse_fertile(tokens, index):
    # AUTO: Sets `token`.
    token = tokens[index]
    # AUTO: Sets `line`.
    line = token.line
    # AUTO: Adds into `index`.
    index += 1
    # AUTO: Checks this condition.
    if tokens[index].value not in {"seed", "tree", "vine", "leaf", "branch"}:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Invalid fertile variable type '{tokens[index].value}'.", line)
    
    # AUTO: Sets `var_type`.
    var_type = tokens[index].value
    # AUTO: Adds into `index`.
    index += 1  

    # AUTO: Checks this condition.
    if tokens[index].type != "id":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected identifier after '{var_type}'.", line)
    
    # AUTO: Sets `var_name`.
    var_name = tokens[index].value
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Checks this condition.
    if tokens[index].type != "=":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Fertile variables must be initialized.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Sets `expected_literals`.
    expected_literals = {
        # AUTO: Executes this statement.
        "seed": {"intlit"},
        # AUTO: Executes this statement.
        "tree": {"dblit"},
        # AUTO: Executes this statement.
        "vine": {"stringlit"},
        # AUTO: Executes this statement.
        "leaf": {"chrlit"},
        # AUTO: Executes this statement.
        "branch": {"sunshine", "frost"}
    # AUTO: Closes the current grouped code/data.
    }
    
    # AUTO: Checks this condition.
    if tokens[index].type not in expected_literals[var_type]:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: '{var_name}' must be initialized with a {var_type} literal.", line)

    # AUTO: Sets `value_node`.
    value_node = ASTNode("Value", tokens[index].value, line=line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Checks this condition.
    if tokens[index].type == ",":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Multiple fertile declaration is not allowed.", line)

    # AUTO: Sets `error`.
    error = symbol_table.declare_variable(var_name, var_type, value=value_node, is_list=False, is_fertile=True)
    # AUTO: Checks this condition.
    if isinstance(error, str):
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(error, line)

    # AUTO: Returns this result to the caller.
    return FertileDeclarationNode(var_type, var_name, value_node, line=line), index

# AUTO: Defines function `parse_if`.
def parse_if(tokens, index, func_type):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Checks this condition.
    if tokens[index].type != "(":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '(' after 'spring'.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Sets `condition_expr, index, cond_type`.
    condition_expr, index, cond_type = parse_expression_branch(tokens, index)

    # AUTO: Checks this condition.
    if cond_type != "branch":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: spring condition must be branch, got {cond_type}.", line)
    
    # AUTO: Checks this condition.
    if tokens[index].type != ")":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ')' after 'spring' condition.", line)
    
    # AUTO: Adds into `index`.
    index += 1  

    # AUTO: Calls `symbol_table.enter_scope`.
    symbol_table.enter_scope()
    
    # AUTO: Sets `condition_node`.
    condition_node = ASTNode("Condition", line=line)
    # AUTO: Calls `condition_node.add_child`.
    condition_node.add_child(condition_expr)

    # AUTO: Sets `if_node`.
    if_node = IfStatementNode(condition_node, line=line)
    
    # AUTO: Checks this condition.
    if tokens[index].type == "{":
        # AUTO: Adds into `index`.
        index += 1

        # AUTO: Sets `block_node`.
        block_node = ASTNode("Block", line=line)

        # AUTO: Repeats while this condition is true.
        while tokens[index].type != "}":
            # AUTO: Sets `stmt, index`.
            stmt, index = parse_statement(tokens, index, func_type)
            # AUTO: Checks this condition.
            if stmt:
                # AUTO: Calls `block_node.add_child`.
                block_node.add_child(stmt)

        # AUTO: Checks this condition.
        if tokens[index].type != "}":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected '}}' after 'spring' block.", line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Calls `symbol_table.exit_scope`.
        symbol_table.exit_scope()
        # AUTO: Calls `if_node.add_child`.
        if_node.add_child(block_node)

    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '{{' after 'spring' condition.", line)


    # AUTO: Repeats while this condition is true.
    while tokens[index].value == "bud":
        # AUTO: Adds into `index`.
        index += 1

        # AUTO: Checks this condition.
        if tokens[index].type != "(":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected '(' after else-if.", line)
        # AUTO: Adds into `index`.
        index += 1  

        # AUTO: Sets `elseif_node`.
        elseif_node = ASTNode("ElseIfStatement", line=line)

        # AUTO: Sets `elseif_condition_expr, index, elseif_cond_type`.
        elseif_condition_expr, index, elseif_cond_type = parse_expression_branch(tokens, index)

        # AUTO: Checks this condition.
        if elseif_cond_type != "branch":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: bud condition must be branch, got {elseif_cond_type}.", line)

        # AUTO: Checks this condition.
        if tokens[index].type != ")":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected ')' after else-if condition.", line)
        # AUTO: Adds into `index`.
        index += 1 

        # AUTO: Calls `symbol_table.enter_scope`.
        symbol_table.enter_scope()

        # AUTO: Sets `elseif_condition_node`.
        elseif_condition_node = ASTNode("Condition", line=line)
        # AUTO: Calls `elseif_condition_node.add_child`.
        elseif_condition_node.add_child(elseif_condition_expr)
        # AUTO: Calls `elseif_node.add_child`.
        elseif_node.add_child(elseif_condition_node)

        # AUTO: Checks this condition.
        if tokens[index].type == "{":
            # AUTO: Adds into `index`.
            index += 1

            # AUTO: Sets `elseif_block_node`.
            elseif_block_node = ASTNode("Block", line=line)

            # AUTO: Repeats while this condition is true.
            while tokens[index].type != "}":
                # AUTO: Sets `stmt, index`.
                stmt, index = parse_statement(tokens, index, func_type)
                # AUTO: Checks this condition.
                if stmt:
                    # AUTO: Calls `elseif_block_node.add_child`.
                    elseif_block_node.add_child(stmt)

            # AUTO: Calls `elseif_node.add_child`.
            elseif_node.add_child(elseif_block_node)
            # AUTO: Adds into `index`.
            index += 1

            # AUTO: Calls `symbol_table.exit_scope`.
            symbol_table.exit_scope()
            # AUTO: Calls `if_node.add_child`.
            if_node.add_child(elseif_node)

        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected '{{' after else-if condition.", line)


    # AUTO: Checks this condition.
    if tokens[index].value == "wither":
        # AUTO: Adds into `index`.
        index += 1

        # AUTO: Checks this condition.
        if tokens[index].type == "{":
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Calls `symbol_table.enter_scope`.
            symbol_table.enter_scope()

            # AUTO: Sets `else_node`.
            else_node = ASTNode("ElseStatement", line=line)
            # AUTO: Sets `else_block_node`.
            else_block_node = ASTNode("Block", line=line)

            # AUTO: Repeats while this condition is true.
            while tokens[index].type != "}":
                # AUTO: Sets `stmt, index`.
                stmt, index = parse_statement(tokens, index, func_type)
                # AUTO: Checks this condition.
                if stmt:
                    # AUTO: Calls `else_block_node.add_child`.
                    else_block_node.add_child(stmt)

            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Calls `symbol_table.exit_scope`.
            symbol_table.exit_scope()
            # AUTO: Calls `else_node.add_child`.
            else_node.add_child(else_block_node)
            # AUTO: Calls `if_node.add_child`.
            if_node.add_child(else_node)
    # AUTO: Returns this result to the caller.
    return if_node, index


# AUTO: Defines function `parse_return`.
def parse_return(tokens, index, func_type):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Checks this condition.
    if func_type == "empty":
        # AUTO: Checks this condition.
        if tokens[index].type not in {"}", ";"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: empty function must not return any value.", line)
        # AUTO: Returns this result to the caller.
        return ReturnNode(None, line=line), index

    # AUTO: Checks this condition.
    if tokens[index].type in {";", "}"}:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Function expects to return a '{func_type}' value, but 'reclaim' has no return expression.", line)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type == "id":
        # AUTO: Sets `identifier`.
        identifier = tokens[index].value

        # AUTO: Checks this condition.
        if tokens[index+1].type == "(":
            # AUTO: Sets `func_info`.
            func_info = symbol_table.lookup_function(identifier)

            # AUTO: Checks this condition.
            if isinstance(func_info, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Function '{identifier}' is not defined.", line)

            # AUTO: Returns this result to the caller.
            return_type = func_info["return_type"]
            # AUTO: Checks this condition.
            if return_type != func_type:
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Function '{identifier}' returns '{return_type}', but expected '{func_type}'.", line)

            # AUTO: Returns this result to the caller.
            return_expr, index = parse_expression_type(tokens, index, func_type)

        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Sets `var_info`.
            var_info = symbol_table.lookup_variable(identifier)
            # AUTO: Checks this condition.
            if isinstance(var_info, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Variable '{identifier}' used before declaration.", line)

            # AUTO: Executes this statement.
            is_member_access = var_info["type"] in symbol_table.bundle_types and tokens[index+1].type == "."
            # AUTO: Checks this condition.
            if not is_member_access:
                # AUTO: Checks this condition.
                if var_info["type"] not in [func_type, "seed", "tree"] and var_info["type"] != "seed" and var_info["type"] != "tree":                
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Variable '{identifier}' is of type '{var_info['type']}'. Expected return value: '{func_type}'.", line)

            # AUTO: Returns this result to the caller.
            return_expr, index = parse_expression_type(tokens, index, func_type)

    # AUTO: Runs when previous condition did not pass.
    else:  
        # AUTO: Returns this result to the caller.
        return_expr, index = parse_expression_type(tokens, index, func_type)

    # AUTO: Returns this result to the caller.
    return ReturnNode(return_expr, line=line), index


# AUTO: Defines function `parse_for`.
def parse_for(tokens, index, func_type):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Adds into `index`.
    index += 1
    # AUTO: Appends a value to a list.
    context_stack.append("ForNode")
    # AUTO: Checks this condition.
    if tokens[index].type != "(":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '(' after 'cultivate'.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Checks this condition.
    if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "seed", "tree", "vine", "leaf", "branch"}:
        # AUTO: Sets `var_type`.
        var_type = tokens[index].value
        # AUTO: Sets `var_name`.
        var_name = tokens[index + 1].value
        # AUTO: Adds into `index`.
        index += 2

        # AUTO: Sets `initialization, index`.
        initialization, index = parse_variable(tokens, index, var_name, var_type)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type == "id":
        # AUTO: Sets `identifier_name`.
        identifier_name = tokens[index].value
        # AUTO: Sets `var_info`.
        var_info = symbol_table.lookup_variable(identifier_name)
        # AUTO: Checks this condition.
        if isinstance(var_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Variable '{identifier_name}' used before declaration.", line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Checks this condition.
        if tokens[index].type != "=":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected '=' after for loop identifier.", line)
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `initialization, index`.
        initialization, index = parse_assignment(tokens, index, identifier_name, var_info["type"])
        
    # AUTO: Checks this condition.
    if tokens[index].type != ";":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ';' after for loop initialization.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Sets `condition, index, cond_type`.
    condition, index, cond_type = parse_expression_branch(tokens, index)

    # AUTO: Checks this condition.
    if cond_type != "branch":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: cultivate condition must be branch, got {cond_type}.", line)

    # AUTO: Sets `condition_node`.
    condition_node = ASTNode("Condition", line=line)
    # AUTO: Calls `condition_node.add_child`.
    condition_node.add_child(condition)

    # AUTO: Checks this condition.
    if tokens[index].type != ";":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ';' after for loop condition.", line)
    # AUTO: Adds into `index`.
    index += 1
    # AUTO: Sets `update_node`.
    update_node = ASTNode("Update", line=line)

    # AUTO: Repeats while this condition is true.
    while True:
        # AUTO: Sets `update, index`.
        update, index = parse_update(tokens, index)
        # AUTO: Calls `update_node.add_child`.
        update_node.add_child(update)
        # AUTO: Checks this condition.
        if tokens[index].type == ",":
            # AUTO: Adds into `index`.
            index += 1
            # AUTO: Skips to the next loop iteration.
            continue
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Stops the nearest loop.
            break

    # AUTO: Checks this condition.
    if tokens[index].type != ")":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ')' after for loop update.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Calls `symbol_table.enter_scope`.
    symbol_table.enter_scope()

    # AUTO: Sets `for_node`.
    for_node = ForLoopNode(initialization, condition_node, update_node, line=line)

    # AUTO: Checks this condition.
    if tokens[index].type == "{":
        # AUTO: Adds into `index`.
        index += 1

        # AUTO: Sets `block_node`.
        block_node = ASTNode("Block", line=line)

        # AUTO: Repeats while this condition is true.
        while tokens[index].type != "}":

            # AUTO: Sets `stmt, index`.
            stmt, index = parse_statement(tokens, index, func_type)
            # AUTO: Checks this condition.
            if stmt:
                # AUTO: Calls `block_node.add_child`.
                block_node.add_child(stmt)

        # AUTO: Adds into `index`.
        index += 1
        

        # AUTO: Calls `symbol_table.exit_scope`.
        symbol_table.exit_scope()
        # AUTO: Removes and returns an item.
        context_stack.pop()

        # AUTO: Calls `for_node.add_child`.
        for_node.add_child(block_node)
    
    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '{{' after for loop condition.", line)
    
    # AUTO: Returns this result to the caller.
    return for_node, index

# AUTO: Defines function `parse_update`.
def parse_update(tokens, index):
    # AUTO: Sets `line`.
    line = tokens[index].line

    # AUTO: Checks this condition.
    if tokens[index].type == "id" or tokens[index].type in {"++", "--"}: 
        # AUTO: Sets `assignments_node`.
        assignments_node = ASTNode("AssignmentList")
        # AUTO: Repeats while this condition is true.
        while True:

            # AUTO: Checks this condition.
            if tokens[index].type == "id":
                # AUTO: Sets `var_info`.
                var_info = symbol_table.lookup_variable(tokens[index].value)
                # AUTO: Checks this condition.
                if isinstance(var_info, str):
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(var_info, line)

                # AUTO: Sets `var_name`.
                var_name = tokens[index].value
                # AUTO: Sets `var_type`.
                var_type = var_info["type"]
                # AUTO: Sets `is_list`.
                is_list = var_info.get("is_list", False)

                # AUTO: Sets `is_fertile`.
                is_fertile = var_info.get("is_fertile", False)

                # AUTO: Checks this condition.
                if is_fertile:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-assigned a value.", line)

                # AUTO: Checks this condition.
                if is_list or (var_type == "vine" and tokens[index + 1].type == "["):
                    # AUTO: Checks this condition.
                    if tokens[index + 1].type == "=":
                        # AUTO: Sets `node, index`.
                        node, index = parse_list_assignment(tokens, index)
                        # AUTO: Calls `assignments_node.add_child`.
                        assignments_node.add_child(node)

                    # AUTO: Checks the next alternate condition.
                    elif tokens[index + 1].type == "[":

                        # AUTO: Sets `list_access_node, index`.
                        list_access_node, index = parse_list_access(tokens, index)

                        # AUTO: Checks this condition.
                        if tokens[index + 1].type == "=":
                            # AUTO: Adds into `index`.
                            index += 2
                            # AUTO: Sets `value_node, index`.
                            value_node, index = parse_expression_type(tokens, index, var_type)
                            # AUTO: Sets `assign_node`.
                            assign_node = AssignmentNode(list_access_node, value_node, line=tokens[index].line)
                            # AUTO: Calls `assignments_node.add_child`.
                            assignments_node.add_child(assign_node)
                        # AUTO: Checks the next alternate condition.
                        elif tokens[index + 1].type in {"++", "--"}:
                            # AUTO: Checks this condition.
                            if var_type not in {"seed", "tree"}:
                                # AUTO: Stops this flow by raising an error.
                                raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_type} in expression.", line)
                            # AUTO: Sets `operator`.
                            operator = tokens[index + 1].value
                            # AUTO: Adds into `index`.
                            index += 2
                            # AUTO: Sets `assignments_node.add_child(UnaryOpNode(operator, list_access_node, "post", line`.
                            assignments_node.add_child(UnaryOpNode(operator, list_access_node, "post", line=line))
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError("Semantic Error: Expected '=' or '++'/'--' after list access.", tokens[index + 1].line)


                # AUTO: Checks the next alternate condition.
                elif tokens[index + 1].type in {"++", "--"}:
                    # AUTO: Sets `var_info`.
                    var_info = symbol_table.lookup_variable(tokens[index].value)
                    
                    # AUTO: Checks this condition.
                    if isinstance(var_info, str):
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(var_info, line)
                    
                    # AUTO: Checks this condition.
                    if var_info["type"] not in {"seed", "tree"}:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Cannot use '{tokens[index].value}' of type {var_info['type']} in expression.", line)
                    # AUTO: Sets `operand`.
                    operand = ASTNode("Identifier", tokens[index].value, line=line)
                    # AUTO: Sets `operator`.
                    operator = tokens[index + 1].value
                    # AUTO: Adds into `index`.
                    index += 2
                    # AUTO: Sets `assignments_node.add_child(UnaryOpNode(operator, operand, "post", line`.
                    assignments_node.add_child(UnaryOpNode(operator, operand, "post", line=line))

                # AUTO: Checks the next alternate condition.
                elif tokens[index + 1].type == "=":
                    # AUTO: Sets `var_name`.
                    var_name = tokens[index].value
                    # AUTO: Sets `var_info`.
                    var_info = symbol_table.lookup_variable(var_name)
                    
                    # AUTO: Checks this condition.
                    if isinstance(var_info, str):
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(var_info, tokens[index].line)

                    # AUTO: Adds into `index`.
                    index += 2
                    # AUTO: Sets `node, index`.
                    node, index = parse_assignment(tokens, index, var_name, var_info["type"])
                    # AUTO: Calls `assignments_node.add_child`.
                    assignments_node.add_child(node)

                # AUTO: Checks the next alternate condition.
                elif tokens[index + 1].type in {"+=", "-=", "*=", "/=", "%=", "**="}:
                    # AUTO: Sets `compound_op`.
                    compound_op = tokens[index + 1].value
                    # AUTO: Sets `base_op`.
                    base_op = compound_op[:-1]
                    # AUTO: Sets `cur_var_name`.
                    cur_var_name = tokens[index].value
                    # AUTO: Sets `cur_var_info`.
                    cur_var_info = symbol_table.lookup_variable(cur_var_name)
                    # AUTO: Checks this condition.
                    if isinstance(cur_var_info, str):
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(cur_var_info, line)
                    # AUTO: Checks this condition.
                    if cur_var_info.get("is_fertile", False):
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Variable '{cur_var_name}' is declared as fertile and cannot be re-assigned a value.", line)
                    # AUTO: Sets `cur_var_type`.
                    cur_var_type = cur_var_info["type"]
                    # AUTO: Checks this condition.
                    if cur_var_type not in {"seed", "tree"}:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Cannot use compound assignment on '{cur_var_name}' of type '{cur_var_type}'.", line)
                    # AUTO: Checks this condition.
                    if base_op == "%" and cur_var_type != "seed":
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(
                            # AUTO: Executes this statement.
                            f"Semantic Error: Modulo operator '%' requires 'seed' (integer) operands, "
                            # AUTO: Executes this statement.
                            f"but '{cur_var_name}' is of type 'tree'.",
                            # AUTO: Executes this statement.
                            line,
                        # AUTO: Closes the current grouped code/data.
                        )
                    # AUTO: Adds into `index`.
                    index += 2
                    # AUTO: Sets `rhs_node, index, rhs_type`.
                    rhs_node, index, rhs_type = parse_expression(tokens, index)
                    # AUTO: Checks this condition.
                    if rhs_type not in {"seed", "tree"}:
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(
                            # AUTO: Sets `f"Semantic Error: Cannot use '{base_op}`.
                            f"Semantic Error: Cannot use '{base_op}=' with right-hand side of type '{rhs_type}'. Expected 'seed' or 'tree'.",
                            # AUTO: Executes this statement.
                            line,
                        # AUTO: Closes the current grouped code/data.
                        )
                    # AUTO: Sets `lhs_node`.
                    lhs_node = ASTNode("Identifier", cur_var_name, line=line)
                    # AUTO: Sets `value_node`.
                    value_node = BinaryOpNode(lhs_node, base_op, rhs_node, line=line)
                    # AUTO: Sets `assign_node`.
                    assign_node = AssignmentNode(cur_var_name, value_node, line=line)
                    # AUTO: Calls `assignments_node.add_child`.
                    assignments_node.add_child(assign_node)
                    
                
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Semantic Error: Unexpected token '{tokens[index].value}' in statement.", line)

            # AUTO: Checks the next alternate condition.
            elif tokens[index].value in {"++", "--"}:
                # AUTO: Sets `operator`.
                operator = tokens[index].value
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Checks this condition.
                if tokens[index].type == "id":
                    # AUTO: Sets `var_name`.
                    var_name = tokens[index].value
                    # AUTO: Sets `var_info`.
                    var_info = symbol_table.lookup_variable(var_name)
                    # AUTO: Checks this condition.
                    if isinstance(var_info, str):
                        # AUTO: Stops this flow by raising an error.
                        raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)

                    # AUTO: Checks this condition.
                    if tokens[index + 1].type == "[":
                        # AUTO: Checks this condition.
                        if var_info["type"] not in {"seed", "tree"}:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in expression.", line)
                        # AUTO: Sets `list_access_node, index`.
                        list_access_node, index = parse_list_access(tokens, index)
                        # AUTO: Adds into `index`.
                        index += 1
                        # AUTO: Sets `assignments_node.add_child(UnaryOpNode(operator, list_access_node, "pre", line`.
                        assignments_node.add_child(UnaryOpNode(operator, list_access_node, "pre", line=line))

                    # AUTO: Checks the next alternate condition.
                    elif tokens[index + 1].type == ".":
                        # AUTO: Sets `obj_name`.
                        obj_name = tokens[index].value
                        # AUTO: Checks this condition.
                        if var_info["type"] not in symbol_table.bundle_types:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Variable '{obj_name}' is not a bundle type.", line)
                        # AUTO: Sets `member_name`.
                        member_name = tokens[index + 2].value
                        # AUTO: Sets `bundle_members`.
                        bundle_members = symbol_table.bundle_types[var_info["type"]]
                        # AUTO: Checks this condition.
                        if member_name not in bundle_members:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Bundle type '{var_info['type']}' has no member '{member_name}'.", line)
                        # AUTO: Sets `member_type`.
                        member_type = bundle_members[member_name]
                        # AUTO: Adds into `index`.
                        index += 3
                        # AUTO: Sets `target`.
                        target = MemberAccessNode(obj_name, member_name, line=line)
                        # AUTO: Repeats while this condition is true.
                        while tokens[index].type == "." and member_type in symbol_table.bundle_types:
                            # AUTO: Sets `next_member`.
                            next_member = tokens[index + 1].value
                            # AUTO: Sets `nested_members`.
                            nested_members = symbol_table.bundle_types[member_type]
                            # AUTO: Checks this condition.
                            if next_member not in nested_members:
                                # AUTO: Stops this flow by raising an error.
                                raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", line)
                            # AUTO: Sets `member_type`.
                            member_type = nested_members[next_member]
                            # AUTO: Sets `target`.
                            target = MemberAccessNode(target, next_member, line=line)
                            # AUTO: Adds into `index`.
                            index += 2
                        # AUTO: Checks this condition.
                        if member_type not in {"seed", "tree"}:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Cannot apply '{operator}' to member '{member_name}' of type '{member_type}'.", line)
                        # AUTO: Sets `assignments_node.add_child(UnaryOpNode(operator, target, "pre", line`.
                        assignments_node.add_child(UnaryOpNode(operator, target, "pre", line=line))

                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Checks this condition.
                        if var_info["type"] not in {"seed", "tree"}:
                            # AUTO: Stops this flow by raising an error.
                            raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in expression.", line)
                        # AUTO: Sets `operand`.
                        operand = ASTNode("Identifier", tokens[index].value, line=line)
                        # AUTO: Adds into `index`.
                        index += 1
                        # AUTO: Sets `assignments_node.add_child(UnaryOpNode(operator, operand, "pre", line`.
                        assignments_node.add_child(UnaryOpNode(operator, operand, "pre", line=line))

                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Stops this flow by raising an error.
                    raise SemanticError(f"Syntax Error: Expected identifier after '{operator}'.", line)

            # AUTO: Checks this condition.
            if tokens[index].type == ",":
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Sets `token`.
                token = tokens[index]
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Stops the nearest loop.
                break
            
        # AUTO: Checks this condition.
        if len(assignments_node.children) > 1:
            # AUTO: Returns this result to the caller.
            return assignments_node, index
        
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Returns this result to the caller.
            return assignments_node.children[0], index
            
    
    # AUTO: Checks the next alternate condition.
    elif tokens[index].type in {"++", "--"}:
        # AUTO: Sets `operator`.
        operator = tokens[index].value
        # AUTO: Adds into `index`.
        index += 1

        # AUTO: Checks this condition.
        if tokens[index].type == "id":
            # AUTO: Sets `var_name`.
            var_name = symbol_table.lookup_variable(tokens[index].value)
            # AUTO: Checks this condition.
            if isinstance(var_name, str):
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)
            
            # AUTO: Sets `operand`.
            operand = ASTNode("Identifier", tokens[index].value, line=line)
            # AUTO: Adds into `index`.
            index += 1

            # AUTO: Returns this result to the caller.
            return UnaryOpNode(operator, operand, "pre", line=line), index
        
    # AUTO: Stops this flow by raising an error.
    raise SemanticError(f"Semantic Error: Invalid update statement.", line)
    
# AUTO: Defines function `parse_while`.
def parse_while(tokens, index, func_type):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Adds into `index`.
    index += 1
    # AUTO: Appends a value to a list.
    context_stack.append("WhileNode")
    
    # AUTO: Checks this condition.
    if tokens[index].type != "(":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '(' after 'grow'.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Sets `condition, index, cond_type`.
    condition, index, cond_type = parse_expression_branch(tokens, index)

    # AUTO: Checks this condition.
    if cond_type != "branch":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: grow condition must be branch, got {cond_type}.", line)

    # AUTO: Checks this condition.
    if tokens[index].type != ")":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ')' after 'grow' condition.", line)
    
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Calls `symbol_table.enter_scope`.
    symbol_table.enter_scope()

    # AUTO: Sets `condition_node`.
    condition_node = ASTNode("Condition", line=line)
    # AUTO: Calls `condition_node.add_child`.
    condition_node.add_child(condition)
    # AUTO: Sets `while_node`.
    while_node = WhileLoopNode(condition_node, line=line)

    # AUTO: Checks this condition.
    if tokens[index].type == "{":
        # AUTO: Adds into `index`.
        index += 1

        # AUTO: Sets `block_node`.
        block_node = ASTNode("Block", line=line)

        # AUTO: Repeats while this condition is true.
        while tokens[index].type != "}":

            # AUTO: Sets `stmt, index`.
            stmt, index = parse_statement(tokens, index, func_type)
            # AUTO: Checks this condition.
            if stmt:
                # AUTO: Calls `block_node.add_child`.
                block_node.add_child(stmt)

        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Calls `symbol_table.exit_scope`.
        symbol_table.exit_scope()
        # AUTO: Removes and returns an item.
        context_stack.pop()

        # AUTO: Calls `while_node.add_child`.
        while_node.add_child(block_node)
    
    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '{{' after 'grow' condition.", line)
    
    # AUTO: Returns this result to the caller.
    return while_node, index

# AUTO: Defines function `parse_do`.
def parse_do(tokens, index, func_type):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Calls `symbol_table.enter_scope`.
    symbol_table.enter_scope()
    # AUTO: Appends a value to a list.
    context_stack.append("DoWhileNode")

    # AUTO: Checks this condition.
    if tokens[index].type != "{":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '{{' after 'tend'.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Sets `block_node`.
    block_node = ASTNode("Block", line=line)

    # AUTO: Repeats while this condition is true.
    while tokens[index].type != "}":

        # AUTO: Sets `stmt, index`.
        stmt, index = parse_statement(tokens, index, func_type)
        # AUTO: Checks this condition.
        if stmt:
            # AUTO: Calls `block_node.add_child`.
            block_node.add_child(stmt)
        

    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Checks this condition.
    if tokens[index].value not in {"grow"}:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected 'grow' after 'tend' block.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Checks this condition.
    if tokens[index].type != "(":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '(' after 'grow'.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Sets `condition, index, cond_type`.
    condition, index, cond_type = parse_expression_branch(tokens, index)

    # AUTO: Checks this condition.
    if cond_type != "branch":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: tend condition must be branch, got {cond_type}.", line)

    # AUTO: Checks this condition.
    if tokens[index].type != ")":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ')' after 'grow' condition.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Sets `do_node`.
    do_node = DoWhileLoopNode(condition, line=line)

    # AUTO: Sets `condition_node`.
    condition_node = ASTNode("Condition", line=line)
    # AUTO: Calls `condition_node.add_child`.
    condition_node.add_child(condition)

    # AUTO: Calls `do_node.add_child`.
    do_node.add_child(block_node)
    # AUTO: Calls `do_node.add_child`.
    do_node.add_child(condition_node)

    # AUTO: Calls `symbol_table.exit_scope`.
    symbol_table.exit_scope()
    # AUTO: Removes and returns an item.
    context_stack.pop()
    # AUTO: Returns this result to the caller.
    return do_node, index


# AUTO: Defines function `parse_switch`.
def parse_switch(tokens, index, func_type):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Adds into `index`.
    index += 1
    # AUTO: Appends a value to a list.
    context_stack.append("SwitchNode")

    # AUTO: Checks this condition.
    if tokens[index].type != "(":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '(' after 'harvest'.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Sets `switch_type`.
    switch_type = None

    # AUTO: Checks this condition.
    if tokens[index].type == "id":
        # AUTO: Sets `var_info`.
        var_info = symbol_table.lookup_variable(tokens[index].value)
        # AUTO: Checks this condition.
        if isinstance(var_info, str):
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Variable '{tokens[index].value}' used before declaration.", line)
        # AUTO: Sets `var_type`.
        var_type = var_info["type"]
        # AUTO: Checks this condition.
        if var_type in {"vine", "tree"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: 'harvest' expression must be 'seed'/'leaf'/'branch', not '{var_type}'.", line)
        # AUTO: Sets `switch_type`.
        switch_type = var_type
        # AUTO: Sets `switch_expr, index`.
        switch_expr, index = parse_expression_type(tokens, index, var_type)
        

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type in {"intlit", "chrlit", "sunshine", "frost"} or tokens[index].type in {"--", "++", "-", "("}:
        # AUTO: Checks this condition.
        if tokens[index].type == "intlit" or tokens[index].type in {"--", "++", "-"}:
            # AUTO: Sets `switch_type`.
            switch_type = "seed"
        # AUTO: Checks the next alternate condition.
        elif tokens[index].type == "chrlit":
            # AUTO: Sets `switch_type`.
            switch_type = "leaf"
        # AUTO: Checks the next alternate condition.
        elif tokens[index].type in {"sunshine", "frost"}:
            # AUTO: Sets `switch_type`.
            switch_type = "branch"
        # AUTO: Checks the next alternate condition.
        elif tokens[index].type == "(":
            # AUTO: Sets `switch_type`.
            switch_type = "seed"
        # AUTO: Sets `switch_expr, index, _`.
        switch_expr, index, _ = parse_expression(tokens, index)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type in {"stringlit"}:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: 'harvest' expression must be 'seed'/'leaf'/'branch', not 'vine'.", line)

    # AUTO: Checks the next alternate condition.
    elif tokens[index].type in {"dblit"}:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: 'harvest' expression must be 'seed'/'leaf'/'branch', not 'tree'.", line)

    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Invalid token '{tokens[index].value}' used in expression.", line)

    # AUTO: Checks this condition.
    if tokens[index].type != ")":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ')' after 'harvest' expression.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Checks this condition.
    if tokens[index].type != "{":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '{{' after 'harvest' expression.", line)
    # AUTO: Adds into `index`.
    index += 1
    
    # AUTO: Calls `symbol_table.enter_scope`.
    symbol_table.enter_scope()

    # AUTO: Sets `case_nodes`.
    case_nodes = []
    # AUTO: Sets `default_case`.
    default_case = None
    # AUTO: Sets `seen_case_values`.
    seen_case_values = set()

    # AUTO: Repeats while this condition is true.
    while tokens[index].value in {"variety"}:
        # AUTO: Sets `case_line`.
        case_line = tokens[index].line
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Sets `line`.
        line = tokens[index].line

        # AUTO: Checks this condition.
        if tokens[index].type not in {"chrlit", "stringlit", "sunshine", "frost", "intlit", "dblit"}:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Semantic Error: Expected valid literal value after 'variety'.", line)

        # AUTO: Sets `lit_type_map`.
        lit_type_map = {
            # AUTO: Executes this statement.
            "intlit": "seed",
            # AUTO: Executes this statement.
            "dblit": "tree",
            # AUTO: Executes this statement.
            "stringlit": "vine",
            # AUTO: Executes this statement.
            "chrlit": "leaf",
            # AUTO: Executes this statement.
            "sunshine": "branch",
            # AUTO: Executes this statement.
            "frost": "branch",
        # AUTO: Closes the current grouped code/data.
        }
        # AUTO: Sets `lit_type`.
        lit_type = lit_type_map.get(tokens[index].type)
        # AUTO: Checks this condition.
        if switch_type and lit_type and lit_type != switch_type:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: 'variety' value type mismatch — expected '{switch_type}' but got '{lit_type}' ('{tokens[index].value}').",
                # AUTO: Executes this statement.
                tokens[index].line,
            # AUTO: Closes the current grouped code/data.
            )

        # AUTO: Sets `case_val_key`.
        case_val_key = tokens[index].value
        # AUTO: Checks this condition.
        if case_val_key in seen_case_values:
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(
                # AUTO: Executes this statement.
                f"Semantic Error: Duplicate 'variety' value '{case_val_key}' in 'harvest'.",
                # AUTO: Executes this statement.
                tokens[index].line,
            # AUTO: Closes the current grouped code/data.
            )
        # AUTO: Calls `seen_case_values.add`.
        seen_case_values.add(case_val_key)

        # AUTO: Sets `case_value`.
        case_value = ASTNode("Value", tokens[index].value, line=case_line)
        # AUTO: Adds into `index`.
        index += 1

        # AUTO: Checks this condition.
        if tokens[index].type != ":":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected ':' after 'variety' value.", line)
        # AUTO: Adds into `index`.
        index += 1

        # AUTO: Sets `case_block`.
        case_block = ASTNode("Block", line=case_line)
        # AUTO: Sets `getout_node`.
        getout_node = None

        # AUTO: Repeats while this condition is true.
        while tokens[index].value not in {"variety", "soil"} and tokens[index].type != "}":

            # AUTO: Sets `stmt, index`.
            stmt, index = parse_statement(tokens, index, func_type)
            # AUTO: Checks this condition.
            if stmt:
                # AUTO: Calls `case_block.add_child`.
                case_block.add_child(stmt)

        # AUTO: Checks this condition.
        if getout_node:
            # AUTO: Checks this condition.
            if tokens[index].value not in {"variety", "soil"} and tokens[index].type != "}":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Unexpected statement after 'prune' in case block.", tokens[index].line)
            # AUTO: Calls `case_block.add_child`.
            case_block.add_child(getout_node) 


        # AUTO: Sets `case_node`.
        case_node = ASTNode("Case", line=case_line)
        # AUTO: Calls `case_node.add_child`.
        case_node.add_child(case_value)
        # AUTO: Calls `case_node.add_child`.
        case_node.add_child(case_block)
        # AUTO: Appends a value to a list.
        case_nodes.append(case_node)

    # AUTO: Checks this condition.
    if tokens[index].value in {"soil"}:
        # AUTO: Sets `line`.
        line = tokens[index].line
        # AUTO: Adds into `index`.
        index += 1
             
        # AUTO: Checks this condition.
        if tokens[index].type != ":":
            # AUTO: Stops this flow by raising an error.
            raise SemanticError(f"Syntax Error: Expected ':' after 'soil'.", line)
        # AUTO: Adds into `index`.
        index += 1
        
        # AUTO: Sets `default_block`.
        default_block = ASTNode("Block", line=line)
        # AUTO: Sets `getout_node`.
        getout_node = None

        # AUTO: Repeats while this condition is true.
        while tokens[index].type != "}":

            # AUTO: Sets `stmt, index`.
            stmt, index = parse_statement(tokens, index, func_type)
            # AUTO: Checks this condition.
            if stmt:
                # AUTO: Calls `default_block.add_child`.
                default_block.add_child(stmt)

        # AUTO: Checks this condition.
        if getout_node:
            # AUTO: Checks this condition.
            if tokens[index].type != "}":
                # AUTO: Stops this flow by raising an error.
                raise SemanticError(f"Semantic Error: Unexpected statement after 'prune' in default block.", tokens[index].line)
            # AUTO: Calls `default_block.add_child`.
            default_block.add_child(getout_node)


        # AUTO: Sets `default_case`.
        default_case = ASTNode("Default", line=line)
        # AUTO: Calls `default_case.add_child`.
        default_case.add_child(default_block)

    # AUTO: Checks this condition.
    if tokens[index].type != "}":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '}}' after 'harvest' statement.", line)
        
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Calls `symbol_table.exit_scope`.
    symbol_table.exit_scope()
    # AUTO: Removes and returns an item.
    context_stack.pop()

    # AUTO: Returns this result to the caller.
    return SwitchNode(switch_expr, case_nodes, default_case, line=line), index


# AUTO: Defines function `parse_list`.
def parse_list(tokens, index, expected_type):
    # AUTO: Sets `line`.
    line = tokens[index].line
    # AUTO: Checks this condition.
    if tokens[index].type != "[":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Expected '[' for list declaration.", line)
    # AUTO: Adds into `index`.
    index += 1
    
    # AUTO: Sets `elements`.
    elements = []

    # AUTO: Checks this condition.
    if tokens[index].type == "]":
        # AUTO: Adds into `index`.
        index += 1
        # AUTO: Returns this result to the caller.
        return ListNode(elements=[], line=line), index
    
    # AUTO: Repeats while this condition is true.
    while tokens[index].type != "]":
        # AUTO: Sets `expr, index`.
        expr, index = parse_expression_type(tokens, index, expected_type)
        # AUTO: Appends a value to a list.
        elements.append(expr)

        # AUTO: Checks this condition.
        if tokens[index].type == ",":
            # AUTO: Adds into `index`.
            index += 1
    
    # AUTO: Checks this condition.
    if tokens[index].type != "]":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ']' after list elements.", line)

    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Returns this result to the caller.
    return ListNode(elements = elements, line = line), index

# AUTO: Defines function `parse_append`.
def parse_append(tokens, index, var_name, expected_type):

    # AUTO: Sets `line`.
    line = tokens[index].line

    # AUTO: Checks this condition.
    if tokens[index].value != "append":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Expected 'append'.", line)
    
    # AUTO: Adds into `index`.
    index += 1
    # AUTO: Checks this condition.
    if tokens[index].type != "(":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '(' after 'append'.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Sets `elements`.
    elements = []
    # AUTO: Repeats while this condition is true.
    while tokens[index].type != ")":
        # AUTO: Sets `elem, index`.
        elem, index = parse_expression_type(tokens, index, expected_type)
        # AUTO: Appends a value to a list.
        elements.append(elem)

        # AUTO: Checks this condition.
        if tokens[index].type == ",":
            # AUTO: Adds into `index`.
            index += 1

    # AUTO: Checks this condition.
    if tokens[index].type != ")":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ')' after append arguments.", line)
    # AUTO: Adds into `index`.
    index += 1  

    # AUTO: Returns this result to the caller.
    return AppendNode(elements, line=line), index

# AUTO: Defines function `parse_insert`.
def parse_insert(tokens, index, var_name, expected_type):
    # AUTO: Sets `line`.
    line = tokens[index].line

    # AUTO: Checks this condition.
    if tokens[index].value != "insert":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Expected 'insert'.", line)

    # AUTO: Adds into `index`.
    index += 1
    # AUTO: Checks this condition.
    if tokens[index].type != "(":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '(' after 'insert'.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Sets `expr_node, index, idx_type`.
    expr_node, index, idx_type = parse_equality(tokens, index)
    # AUTO: Checks this condition.
    if idx_type is not None and idx_type != "seed":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(
            # AUTO: Executes this statement.
            f"Semantic Error: List index must be of type 'seed', got '{idx_type}'.",
            # AUTO: Executes this statement.
            line,
        # AUTO: Closes the current grouped code/data.
        )
    # AUTO: Sets `index_value`.
    index_value = ASTNode("Index", line=tokens[index].line)
    # AUTO: Calls `index_value.add_child`.
    index_value.add_child(expr_node)

    # AUTO: Checks this condition.
    if tokens[index].type != ",":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ',' after index in 'insert'.", line)
    # AUTO: Adds into `index`.
    index += 1  

    # AUTO: Sets `elements`.
    elements = []

    # AUTO: Repeats while this condition is true.
    while tokens[index].type != ")":
        # AUTO: Sets `elem, index`.
        elem, index = parse_expression_type(tokens, index, expected_type)
        # AUTO: Appends a value to a list.
        elements.append(elem)

        # AUTO: Checks this condition.
        if tokens[index].type == ",":
            # AUTO: Adds into `index`.
            index += 1

    # AUTO: Checks this condition.
    if tokens[index].type != ")":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ')' after insert arguments.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Returns this result to the caller.
    return InsertNode(index_value, elements, line=line), index

# AUTO: Defines function `parse_remove`.
def parse_remove(tokens, index, var_name, expected_type):
    # AUTO: Sets `line`.
    line = tokens[index].line

    # AUTO: Checks this condition.
    if tokens[index].value != "remove":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Semantic Error: Expected 'remove'.", line)

    # AUTO: Adds into `index`.
    index += 1
    # AUTO: Checks this condition.
    if tokens[index].type != "(":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected '(' after 'remove'.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Sets `expr_node, index, idx_type`.
    expr_node, index, idx_type = parse_equality(tokens, index)
    # AUTO: Checks this condition.
    if idx_type is not None and idx_type != "seed":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(
            # AUTO: Executes this statement.
            f"Semantic Error: List index must be of type 'seed', got '{idx_type}'.",
            # AUTO: Executes this statement.
            line,
        # AUTO: Closes the current grouped code/data.
        )
    # AUTO: Sets `index_value`.
    index_value = ASTNode("Index", line=tokens[index].line)
    # AUTO: Calls `index_value.add_child`.
    index_value.add_child(expr_node)
        
    # AUTO: Checks this condition.
    if tokens[index].type != ")":
        # AUTO: Stops this flow by raising an error.
        raise SemanticError(f"Syntax Error: Expected ')' after remove argument.", line)
    # AUTO: Adds into `index`.
    index += 1

    # AUTO: Returns this result to the caller.
    return RemoveNode(var_name, index_value, line=line), index


# AUTO: Defines function `is_inside_loop_or_switch_stack`.
def is_inside_loop_or_switch_stack():
    # AUTO: Returns this result to the caller.
    return any(ctx in {"WhileNode", "DoWhileNode", "SwitchNode", "ForNode"} for ctx in context_stack)


# AUTO: Defines function `analyze_semantics`.
def analyze_semantics(tokens):
    # GUIDE: Compatibility wrapper kept for older server paths; current server flow
    # normally uses LL1Parser.parse_and_build() then semantic.validate_ast().
    # AUTO: Starts protected code that can catch errors.
    try:
        # AUTO: Sets `filtered`.
        filtered = [t for t in tokens if t.type not in ('\n', 'comment', 'mcommentlit')]
        # AUTO: Sets `ast`.
        ast = build_ast(filtered)

        # AUTO: Sets `st`.
        st = {
            # AUTO: Executes this statement.
            "variables": [
                # AUTO: Executes this statement.
                {
                    # AUTO: Executes this statement.
                    "name": name,
                    # AUTO: Executes this statement.
                    "type": info["type"],
                    # AUTO: Executes this statement.
                    "scope": "global",
                    # AUTO: Calls `info.get`.
                    "is_list": info.get("is_list", False),
                    # AUTO: Calls `info.get`.
                    "is_constant": info.get("is_fertile", False),
                # AUTO: Closes the current grouped code/data.
                }
                # AUTO: Starts a loop over these values.
                for name, info in symbol_table.variables.items()
            # AUTO: Closes the current grouped code/data.
            ],
            # AUTO: Executes this statement.
            "functions": {
                # AUTO: Executes this statement.
                name: {
                    # AUTO: Executes this statement.
                    "return_type": info["return_type"],
                    # AUTO: Executes this statement.
                    "params": [
                        # AUTO: Executes this statement.
                        {
                            # AUTO: Executes this statement.
                            "type": p.children[0].value if p.children else "unknown",
                            # AUTO: Executes this statement.
                            "name": p.children[1].value if len(p.children) > 1 else "unknown",
                        # AUTO: Closes the current grouped code/data.
                        }
                        # AUTO: Starts a loop over these values.
                        for p in info["params"]
                    # AUTO: Closes the current grouped code/data.
                    ] if info["params"] else [],
                # AUTO: Closes the current grouped code/data.
                }
                # AUTO: Starts a loop over these values.
                for name, info in symbol_table.functions.items()
            # AUTO: Closes the current grouped code/data.
            },
        # AUTO: Closes the current grouped code/data.
        }

        # AUTO: Returns this result to the caller.
        return {
            # AUTO: Executes this statement.
            "success": True,
            # AUTO: Executes this statement.
            "errors": [],
            # AUTO: Executes this statement.
            "warnings": [],
            # AUTO: Executes this statement.
            "symbol_table": st,
            # AUTO: Executes this statement.
            "ast": ast,
        # AUTO: Closes the current grouped code/data.
        }

    # AUTO: Handles the matching error case.
    except SemanticError as e:
        # AUTO: Returns this result to the caller.
        return {
            # AUTO: Executes this statement.
            "success": False,
            # AUTO: Executes this statement.
            "errors": [str(e)],
            # AUTO: Executes this statement.
            "warnings": [],
            # AUTO: Executes this statement.
            "symbol_table": {},
            # AUTO: Executes this statement.
            "ast": None,
        # AUTO: Closes the current grouped code/data.
        }
