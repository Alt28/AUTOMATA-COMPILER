import copy
import re

from shared.tokens import *  # noqa: F401,F403 - TT_* constants used throughout parse_*
from semantic.errors import SemanticError
from shared.ast_nodes import *  # noqa: F401,F403 - all AST node classes
from semantic.symbol_table import SymbolTable


class SemanticAnalyzer:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.visited_nodes = set()


symbol_table = SymbolTable()
semantic_analyzer = SemanticAnalyzer(symbol_table)
context_stack = []


def build_ast(tokens):
    root = ProgramNode()
    symbol_table.variables = {}
    symbol_table.functions = {}
    symbol_table.scopes = [{}] 
    symbol_table.function_variables = {}
    symbol_table.bundle_types = {}
    context_stack = []
    index = 0
    symbol_table.current_func_name = None
    
    while index < len(tokens):
        token = tokens[index]

        if token.type == ";":
            index += 1
            continue
        
        if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch"}:
            id_type = token.value
            index += 1
            if tokens[index].type != "id":
                raise SemanticError(f"Semantic Error: Invalid variable declaration.", token.line)
            id_name = tokens[index].value
            index += 1
            node, index = parse_variable(tokens, index, id_name, id_type) 

            if node:
                root.add_child(node)

        elif tokens[index].value == "empty":
            index += 1
            if tokens[index].type == "id":
                func_name = tokens[index].value
                func_type = "empty"
                node, index = parse_function(tokens, index, func_name, func_type)
            else:
                raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
            
            if node:
                root.add_child(node)
            
        elif tokens[index].value in {"pollinate"}:
            index += 1
            if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty"}:
                id_type = tokens[index].value
                index += 1
                if tokens[index].type != "id":
                    raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
                id_name = tokens[index].value
                index += 1
                node, index = parse_function(tokens, index, id_name, id_type)

                if node:
                    root.add_child(node)

            elif tokens[index].type == "id" and tokens[index].value in symbol_table.bundle_types:
                id_type = tokens[index].value
                index += 1
                if tokens[index].type != "id":
                    raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
                id_name = tokens[index].value
                index += 1
                node, index = parse_function(tokens, index, id_name, id_type)

                if node:
                    root.add_child(node)

            else: 
                raise SemanticError(f"Semantic Error: Expected data type for function declaration after 'pollinate'.", tokens[index].line)

        elif token.value == "fertile":
            node, index = parse_fertile(tokens, index)
            if node:
                root.add_child(node)

        elif token.value == "identifier":
            if isinstance(symbol_table.lookup_variable(token.value), str):
                raise SemanticError(f"Semantic Error: Variable '{token.value}' used before declaration.", token.line)
            raise SemanticError(f"Semantic Error: Invalid global statement.", token.line)

        elif token.value in {"root"}:
            func_name = token.value
            func_type = "empty"
            node, index = parse_function(tokens, index, func_name, func_type)

            if node:
                root.add_child(node)

        elif token.value == "bundle":
            bundle_name = tokens[index + 1].value
            index += 2

            if tokens[index].type == "{":
                index += 1
                members = {}
                while tokens[index].type != "}":
                    if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch"}:
                        member_type = tokens[index].value
                        member_name = tokens[index + 1].value
                        if member_name in members:
                            raise SemanticError(f"Semantic Error: Duplicate member '{member_name}' in bundle '{bundle_name}'.", tokens[index].line)
                        members[member_name] = member_type
                        index += 2
                        if tokens[index].type == ";":
                            index += 1
                    elif tokens[index].type == "id" and tokens[index].value in symbol_table.bundle_types:
                        member_type = tokens[index].value
                        member_name = tokens[index + 1].value
                        if member_name in members:
                            raise SemanticError(f"Semantic Error: Duplicate member '{member_name}' in bundle '{bundle_name}'.", tokens[index].line)
                        members[member_name] = member_type
                        index += 2
                        if tokens[index].type == ";":
                            index += 1
                    else:
                        raise SemanticError(f"Semantic Error: Invalid member type '{tokens[index].value}' in bundle definition.", tokens[index].line)
                index += 1

                if bundle_name in symbol_table.bundle_types:
                    raise SemanticError(f"Semantic Error: Bundle type '{bundle_name}' already defined.", token.line)

                symbol_table.bundle_types[bundle_name] = members
                node = BundleDefinitionNode(bundle_name, members, line=token.line)
                root.add_child(node)

            else:
                var_name = tokens[index].value
                index += 1

                if bundle_name not in symbol_table.bundle_types:
                    raise SemanticError(f"Semantic Error: Bundle type '{bundle_name}' is not defined.", token.line)

                members = symbol_table.bundle_types[bundle_name]
                _defaults = {"seed": 0, "tree": 0.0, "leaf": '', "vine": "", "branch": False}
                bundle_value = {name: _defaults.get(typ, None) for name, typ in members.items()}

                error = symbol_table.declare_variable(var_name, bundle_name, value=bundle_value)
                if isinstance(error, str):
                    raise SemanticError(error, token.line)

                node = VariableDeclarationNode(bundle_name, var_name, line=token.line)
                root.add_child(node)

        else:
            if token.type not in {"EOF"}:
                raise SemanticError(f"Semantic Error: Invalid token '{token.value}' used in global statement.", token.line)
            break
    
    return root

def parse_functionOrVariable(tokens, index):
    id_type = tokens[index].value
    line = tokens[index].line

    if tokens[index + 1].type == "id" or tokens[index + 1].value == "root":
        id_name = tokens[index + 1].value
        index += 2
    
        if tokens[index].type == "(":
            node, index = parse_function(tokens, index, id_name, id_type)
        
        elif tokens[index].type == "=":
            node, index = parse_variable(tokens, index, id_name, id_type) 
        
        else:
            error = f"Semantic Error: Invalid function or variable declaration."
            raise SemanticError(error, line)
        
        node.line = line
        return node, index
    
    return None, index

def parse_function(tokens, index, func_name, func_type):
    line = tokens[index].line

    symbol_table.current_func_name = func_name

    if func_name in symbol_table.functions:
        error = f"Semantic Error: '{func_name}' already declared."
        raise SemanticError(error, tokens[index].line)
    
    elif func_name in symbol_table.variables:
        error = f"Semantic Error: '{func_name}' already declared."
        raise SemanticError(error, tokens[index].line)

    if func_name in {"root"}:
        symbol_table.enter_scope()
        index += 1

        if tokens[index].type == "(":
            index += 1
            if tokens[index].type != ")":
                raise SemanticError(f"Semantic Error: {func_name}() should not have parameters.", line)
            index += 1
        elif func_name == "root":
            raise SemanticError("Semantic Error: Missing () for root function declaration.", line)

        params_node = ASTNode("Parameters")
        func_node = FunctionDeclarationNode(func_type, func_name, params_node)

    else:
        if tokens[index].type != "(":
            error = f"Semantic Error: Missing () for function declaration."
            raise SemanticError(error, line)

        params_node = ASTNode("Parameters")
        line = tokens[index].line
        symbol_table.enter_scope()

        while tokens[index].type != ")":
            if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty"}:
                param_type = tokens[index].value
                index += 1
                if tokens[index].type == "id":
                    param_name = tokens[index].value
                    param_node = ASTNode("Parameter")
                    param_node.add_child(ASTNode("Type", param_type))
                    param_node.add_child(ASTNode("Identifier", param_name))
                    index += 1

                    is_list = False
                    if tokens[index].type == "[":
                        index += 1
                        if tokens[index].type != "]":
                            raise SemanticError(f"Semantic Error: Expected ']' after '[' in array parameter.", line)
                        index += 1
                        is_list = True
                        param_node.add_child(ASTNode("ArrayParam", "true"))

                    params_node.add_child(param_node)
                    error = symbol_table.declare_variable(param_name, param_type, is_list=is_list)
                    if error:
                        raise SemanticError(error, line)

                    if tokens[index].type == ",":
                        index += 1

                else:
                    error = f"Semantic Error: Invalid parameter declaration."
                    raise SemanticError(error, line)

            elif tokens[index].type == "id" and tokens[index].value in symbol_table.bundle_types:
                param_type = tokens[index].value
                index += 1
                if tokens[index].type == "id":
                    param_name = tokens[index].value
                    param_node = ASTNode("Parameter")
                    param_node.add_child(ASTNode("Type", param_type))
                    param_node.add_child(ASTNode("Identifier", param_name))
                    params_node.add_child(param_node)
                    error = symbol_table.declare_variable(param_name, param_type)
                    if error:
                        raise SemanticError(error, line)
                    index += 1

                    if tokens[index].type == ",":
                        index += 1
                else:
                    error = f"Semantic Error: Invalid parameter declaration."
                    raise SemanticError(error, line)

            else:
                index += 1

        symbol_table.declare_function(func_name, func_type, params_node.children)
        index += 1
        func_node = FunctionDeclarationNode(func_type, func_name, params_node)

    if tokens[index].type == "{":
        index += 1
        block_node = ASTNode("Block")
        
        while tokens[index].type != "}":
            stmt, index = parse_statement(tokens, index, func_type)
            if stmt:
                block_node.add_child(stmt)

        index += 1
        func_node.add_child(block_node)
        symbol_table.exit_scope()
        symbol_table.current_func_name = None
    else:
        error = f"Semantic Error: Function body must be enclosed in curly braces."
        raise SemanticError(error, line)

    return func_node, index

def parse_variable(tokens, index, var_name, var_type):
    line = tokens[index].line
    var_nodes = []

    while True:
        global_var = symbol_table.variables.get(var_name)
        if global_var and global_var.get("is_fertile"):
            raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-declared.", line)

        is_list = False

        var_node = VariableDeclarationNode(var_type, var_name, line=line)

        if tokens[index].type == "=":
            index += 1

            if (
                var_type == "vine" and
                tokens[index].type == "id" and
                tokens[index + 1].type == "." and
                tokens[index + 2].value == "taper"
            ):
                identifier = tokens[index].value

                identifier_info = symbol_table.lookup_variable(identifier)
                if isinstance(identifier_info, str):
                    raise SemanticError(f"Semantic Error: Variable '{identifier}' used before declaration.", line)

                if identifier_info["type"] != "leaf":
                    raise SemanticError(f"Semantic Error: Cannot use taper function on '{identifier}'. Must be a leaf type identifier.", line)

                index += 3
                is_list = True
                taper_node = TaperNode(identifier, line=line)
                var_node.add_child(taper_node)

            elif tokens[index].type == "[":
                is_list = True
                value_node, index = parse_list(tokens, index, var_type)
                var_node.add_child(value_node)

            elif tokens[index].value == "water":
                water_line = tokens[index].line
                index += 1
                if tokens[index].type != "(":
                    raise SemanticError(f"Semantic Error: Expected '(' after water.", water_line)
                index += 1
                water_type = None
                if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
                    water_type = tokens[index].value
                    index += 1
                if tokens[index].type != ")":
                    raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter (e.g., water(seed)).", water_line)
                index += 1
                if water_type and not _types_compatible(var_type, water_type):
                    raise SemanticError(f"Semantic Error: Type mismatch — cannot assign water({water_type}) to '{var_type}' variable.", water_line)
                value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=water_line)
                var_node.add_child(value_node)

            else:
                value_node, index = parse_expression_type(tokens, index, var_type)
                var_node.add_child(value_node)

        elif tokens[index].type == "[":
            is_list = True
            dimensions = []
            while tokens[index].type == "[":
                index += 1
                dim_size = 0
                if tokens[index].type == "dblit":
                    raise SemanticError(f"Semantic Error: Array size must be of type 'seed' (integer), got 'tree' (float) '{tokens[index].value}'.", line)
                if tokens[index].type == "intlit":
                    dim_size = int(tokens[index].value)
                    index += 1
                if tokens[index].type != "]":
                    raise SemanticError(f"Syntax Error: Expected ']' after list size.", line)
                index += 1
                dimensions.append(dim_size)

            default_literals = {"seed": "0", "tree": "0.0", "leaf": "''", "vine": '""', "branch": "false"}

            def build_list_node(dims):
                node = ASTNode("List", line=line)
                if len(dims) == 1:
                    for _ in range(dims[0]):
                        node.add_child(ASTNode("Value", default_literals.get(var_type, "0"), line=line))
                else:
                    for _ in range(dims[0]):
                        node.add_child(build_list_node(dims[1:]))
                return node

            list_node = build_list_node(dimensions)
            var_node.add_child(list_node)

            if tokens[index].type == "=":
                index += 1
                if tokens[index].type == "{":
                    def parse_init_braces(idx):
                        if tokens[idx].type != "{":
                            raise SemanticError(f"Syntax Error: Expected '{{' in array initialization.", tokens[idx].line)
                        idx += 1
                        items = []
                        while tokens[idx].type != "}":
                            if tokens[idx].type == "{":
                                inner_node, idx = parse_init_braces(idx)
                                items.append(inner_node)
                            else:
                                expr, idx = parse_expression_type(tokens, idx, var_type)
                                items.append(expr)
                            if tokens[idx].type == ",":
                                idx += 1
                        idx += 1
                        return ListNode(elements=items, line=line), idx

                    value_node, index = parse_init_braces(index)
                    var_node.children[-1] = value_node
                else:
                    raise SemanticError(f"Syntax Error: Expected '{{' after '=' in array initialization.", line)
   
        else:
            pass

        error = symbol_table.declare_variable(var_name, var_type, is_list = is_list)

        if isinstance(error, str):
            raise SemanticError(error, line)
        
        var_nodes.append(var_node)

        if tokens[index].type == ",":
            index += 1
            var_name = tokens[index].value
            index += 1
        else:
            break
    
    if len(var_nodes) == 1:
        return var_nodes[0], index
    
    else:
        var_list_node = ASTNode("VariableDeclarationList")
        for node in var_nodes:
            var_list_node.add_child(node)
        return var_list_node, index


def _skip_semicolons(tokens, index):
    while index < len(tokens) and tokens[index].type == ";":
        index += 1
    return index


def parse_statement(tokens, index, func_type = None):
    token = tokens[index]

    if token.type == ";":
        return None, index + 1

    line = token.line

    if token.value in {"seed", "tree", "vine", "leaf", "branch"}:
        var_type = token.value
        var_name = tokens[index + 1].value
        index += 2

        node, index = parse_variable(tokens, index, var_name, var_type)
        return node, index
    
    
    elif token.value == "fertile":
        node, index = parse_fertile(tokens, index)
        return node, index

    elif token.value == "bundle":
        bundle_type_name = tokens[index + 1].value
        if bundle_type_name not in symbol_table.bundle_types:
            raise SemanticError(f"Semantic Error: Bundle type '{bundle_type_name}' is not defined.", token.line)
        var_name = tokens[index + 2].value
        index += 3

        members = symbol_table.bundle_types[bundle_type_name]
        _defaults = {"seed": 0, "tree": 0.0, "leaf": '', "vine": "", "branch": False}

        if tokens[index].type == "[":
            index += 1
            if tokens[index].type == "dblit":
                raise SemanticError(f"Semantic Error: Array size must be of type 'seed' (integer), got 'tree' (float) '{tokens[index].value}'.", token.line)
            array_size = 0
            if tokens[index].type == "intlit":
                array_size = int(tokens[index].value)
                index += 1
            if tokens[index].type != "]":
                raise SemanticError(f"Syntax Error: Expected ']' after array size.", token.line)
            index += 1

            list_node = ASTNode("List", line=token.line)
            for _ in range(array_size):
                bundle_val_node = ASTNode("BundleDefault", line=token.line)
                list_node.add_child(bundle_val_node)

            error = symbol_table.declare_variable(var_name, bundle_type_name, is_list=True)
            if isinstance(error, str):
                raise SemanticError(error, token.line)

            node = VariableDeclarationNode(bundle_type_name, var_name, line=token.line)
            node.add_child(list_node)
            return node, index
        else:
            bundle_value = {name: _defaults.get(typ, None) for name, typ in members.items()}

            error = symbol_table.declare_variable(var_name, bundle_type_name, value=bundle_value)
            if isinstance(error, str):
                raise SemanticError(error, token.line)

            node = VariableDeclarationNode(bundle_type_name, var_name, line=token.line)
            return node, index

    elif token.type == "id" and tokens[index + 1].type == "(":
        if tokens[index + 1].type == "(":
            func_name = token.value
            error = symbol_table.lookup_function(func_name)
            if isinstance(error, str):
                error = symbol_table.lookup_function(func_name)
                raise SemanticError(error, token.line)
            func_type = symbol_table.lookup_function(func_name)["return_type"]
            func_params = symbol_table.lookup_function(func_name)["params"]
            func_call_node, index = parse_function_call(tokens, index, func_name, func_type, func_params)
            return func_call_node, index
        
    elif token.type == "id" or tokens[index].type in {"++", "--"}: 
        assignments_node = ASTNode("AssignmentList")
        while True:

            if tokens[index].type == "id":
                var_info = symbol_table.lookup_variable(tokens[index].value)
                if isinstance(var_info, str):
                    raise SemanticError(var_info, line)

                var_name = tokens[index].value
                var_type = var_info["type"]
                is_list = var_info.get("is_list", False)

                is_fertile = var_info.get("is_fertile", False)

                if is_fertile:
                    raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-assigned a value.", line)

                if is_list or (var_type == "vine" and tokens[index + 1].type == "["):
                    if tokens[index + 1].type == "=":
                        node, index = parse_list_assignment(tokens, index)
                        assignments_node.add_child(node)

                    elif tokens[index + 1].type == "[":
                        
                        list_access_node, index = parse_list_access(tokens, index)

                        if tokens[index + 1].type == "." and var_type in symbol_table.bundle_types:
                            index += 2
                            member_name = tokens[index].value
                            bundle_members = symbol_table.bundle_types[var_type]
                            if member_name not in bundle_members:
                                raise SemanticError(f"Semantic Error: Bundle type '{var_type}' has no member '{member_name}'.", line)
                            member_type = bundle_members[member_name]
                            target = ArrayMemberAccessNode(list_access_node, member_name, line=line)
                            index += 1

                            while tokens[index].type == "." and member_type in symbol_table.bundle_types:
                                next_member = tokens[index + 1].value
                                nested_members = symbol_table.bundle_types[member_type]
                                if next_member not in nested_members:
                                    raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", line)
                                member_type = nested_members[next_member]
                                target = MemberAccessNode(target, next_member, line=line)
                                index += 2

                            if tokens[index].type == "=":
                                index += 1
                                value_node, index = parse_expression_type(tokens, index, member_type)
                                assign_node = AssignmentNode(target, value_node, line=line)
                                assignments_node.add_child(assign_node)
                            elif tokens[index].type in {"+=", "-=", "*=", "/=", "%=", "**="}:
                                if member_type not in {"seed", "tree"}:
                                    raise SemanticError(f"Semantic Error: Compound assignment '{tokens[index].value}' is not valid for '{member_type}' member '{member_name}'.", line)
                                compound_op = tokens[index].value
                                base_op = compound_op[:-1]
                                index += 1
                                rhs_node, index = parse_expression_type(tokens, index, member_type)
                                value_node = BinaryOpNode(target, base_op, rhs_node, line=line)
                                assign_node = AssignmentNode(target, value_node, line=line)
                                assignments_node.add_child(assign_node)
                            else:
                                raise SemanticError(f"Semantic Error: Expected '=' after '{var_name}[...].{member_name}'.", line)

                        elif tokens[index + 1].type == "=":
                            index += 2 
                            if tokens[index].value == "water":
                                water_line = tokens[index].line
                                index += 1
                                if tokens[index].type != "(":
                                    raise SemanticError(f"Syntax Error: Expected '(' after water.", water_line)
                                index += 1
                                water_type = None
                                if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
                                    water_type = tokens[index].value
                                    index += 1
                                if tokens[index].type != ")":
                                    raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter.", water_line)
                                index += 1
                                if water_type and not _types_compatible(var_type, water_type):
                                    raise SemanticError(f"Semantic Error: Type mismatch — cannot assign water({water_type}) to '{var_type}' list element.", water_line)
                                value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=water_line)
                            else:
                                value_node, index = parse_expression_type(tokens, index, var_type)
                            assign_node = AssignmentNode(list_access_node, value_node, line=tokens[index].line)
                            assignments_node.add_child(assign_node)

                        elif tokens[index + 1].type in {"++", "--"}:
                            
                            if var_type not in {"seed", "tree"}:
                                raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_type} in expression.", line)
                            operator = tokens[index + 1].value
                            unary_node = UnaryOpNode(operator, list_access_node, "post", line=line)
                            index += 2

                            assignments_node.add_child(unary_node)
                            
                        
                elif tokens[index + 1].type == ".":
                    obj_name = tokens[index].value
                    member_name = tokens[index + 2].value
                    if var_type not in symbol_table.bundle_types:
                        raise SemanticError(f"Semantic Error: Variable '{obj_name}' is not a bundle type.", line)
                    bundle_members = symbol_table.bundle_types[var_type]
                    if member_name not in bundle_members:
                        raise SemanticError(f"Semantic Error: Bundle type '{var_type}' has no member '{member_name}'.", line)
                    member_type = bundle_members[member_name]
                    index += 3
                    target = MemberAccessNode(obj_name, member_name, line=line)

                    while tokens[index].type == "." and member_type in symbol_table.bundle_types:
                        next_member = tokens[index + 1].value
                        nested_members = symbol_table.bundle_types[member_type]
                        if next_member not in nested_members:
                            raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", line)
                        member_type = nested_members[next_member]
                        target = MemberAccessNode(target, next_member, line=line)
                        index += 2

                    if tokens[index].type == "=":
                        index += 1
                        if tokens[index].value == "water":
                            water_line = tokens[index].line
                            index += 1
                            if tokens[index].type != "(":
                                raise SemanticError(f"Syntax Error: Expected '(' after water.", water_line)
                            index += 1
                            water_type = None
                            if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
                                water_type = tokens[index].value
                                index += 1
                            if tokens[index].type != ")":
                                raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter (e.g., water(seed)).", water_line)
                            index += 1
                            if water_type and not _types_compatible(member_type, water_type):
                                raise SemanticError(f"Semantic Error: Type mismatch — cannot assign water({water_type}) to '{member_type}' member '{member_name}'.", water_line)
                            value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=water_line)
                        else:
                            value_node, index = parse_expression_type(tokens, index, member_type)
                        assign_node = AssignmentNode(target, value_node, line=line)
                        assignments_node.add_child(assign_node)
                    elif tokens[index].type in {"+=", "-=", "*=", "/=", "%=", "**="}:
                        if member_type not in {"seed", "tree"}:
                            raise SemanticError(f"Semantic Error: Compound assignment '{tokens[index].value}' is not valid for '{member_type}' member '{member_name}'.", line)
                        compound_op = tokens[index].value
                        base_op = compound_op[:-1]
                        index += 1
                        rhs_node, index = parse_expression_type(tokens, index, member_type)
                        value_node = BinaryOpNode(target, base_op, rhs_node, line=line)
                        assign_node = AssignmentNode(target, value_node, line=line)
                        assignments_node.add_child(assign_node)
                    elif tokens[index].type in {"++", "--"}:
                        if member_type not in {"seed", "tree"}:
                            raise SemanticError(f"Semantic Error: Cannot apply '{tokens[index].value}' to member '{member_name}' of type '{member_type}'.", line)
                        operator = tokens[index].value
                        index += 1
                        assignments_node.add_child(UnaryOpNode(operator, target, "post", line=line))
                    else:
                        raise SemanticError(f"Semantic Error: Expected '=' after '{obj_name}.{member_name}'.", line)

                elif tokens[index + 1].type == "=":
                    var_name = token.value
                    error = symbol_table.lookup_variable(var_name)
                    if isinstance(error, str):
                        raise SemanticError(error, token.line)

                    index += 2
                    node, index = parse_assignment(tokens, index, token.value, symbol_table.lookup_variable(token.value)["type"])
                    assignments_node.add_child(node)

                elif tokens[index + 1].type in {"++", "--"}:
                    var_info = symbol_table.lookup_variable(tokens[index].value)
                    
                    if isinstance(var_info, str):
                        raise SemanticError(var_info, line)
                    
                    if var_info["type"] not in {"seed", "tree"}:
                        raise SemanticError(f"Semantic Error: Cannot use '{token.value}' of type {var_info['type']} in expression.", line)
                    operand = ASTNode("Identifier", token.value, line=line)
                    operator = tokens[index + 1].value
                    index += 2
                    assignments_node.add_child(UnaryOpNode(operator, operand, "post", line=line))

                elif tokens[index + 1].type in {"+=", "-=", "*=", "/=", "%=", "**="}:
                    compound_op = tokens[index + 1].value
                    base_op = compound_op[:-1]
                    cur_var_name = tokens[index].value
                    cur_var_info = symbol_table.lookup_variable(cur_var_name)
                    if isinstance(cur_var_info, str):
                        raise SemanticError(cur_var_info, line)
                    if cur_var_info.get("is_fertile", False):
                        raise SemanticError(f"Semantic Error: Variable '{cur_var_name}' is declared as fertile and cannot be re-assigned a value.", line)
                    cur_var_type = cur_var_info["type"]
                    if cur_var_type not in {"seed", "tree"}:
                        raise SemanticError(f"Semantic Error: Cannot use compound assignment on '{cur_var_name}' of type '{cur_var_type}'.", line)
                    if base_op == "%" and cur_var_type != "seed":
                        raise SemanticError(
                            f"Semantic Error: Modulo operator '%' requires 'seed' (integer) operands, "
                            f"but '{cur_var_name}' is of type 'tree'.",
                            line,
                        )
                    index += 2
                    rhs_node, index, rhs_type = parse_expression(tokens, index)
                    if rhs_type not in {"seed", "tree"}:
                        raise SemanticError(
                            f"Semantic Error: Cannot use '{base_op}=' with right-hand side of type '{rhs_type}'. Expected 'seed' or 'tree'.",
                            line,
                        )
                    lhs_node = ASTNode("Identifier", cur_var_name, line=line)
                    value_node = BinaryOpNode(lhs_node, base_op, rhs_node, line=line)
                    assign_node = AssignmentNode(cur_var_name, value_node, line=line)
                    assignments_node.add_child(assign_node)

                
                else:
                    raise SemanticError(f"Semantic Error: Unexpected token '{tokens[index].value}' in statement.", line)

            elif tokens[index].value in {"++", "--"}:
                operator = tokens[index].value
                index += 1
                if tokens[index].type == "id":
                    var_name = tokens[index].value
                    var_info = symbol_table.lookup_variable(var_name)
                    if isinstance(var_info, str):
                        raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)

                    if tokens[index + 1].type == "[":
                        if var_info["type"] not in {"seed", "tree"}:
                            raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in expression.", line)
                        list_access_node, index = parse_list_access(tokens, index)
                        index += 1
                        assignments_node.add_child(UnaryOpNode(operator, list_access_node, "pre", line=line))

                    elif tokens[index + 1].type == ".":
                        obj_name = tokens[index].value
                        if var_info["type"] not in symbol_table.bundle_types:
                            raise SemanticError(f"Semantic Error: Variable '{obj_name}' is not a bundle type.", line)
                        member_name = tokens[index + 2].value
                        bundle_members = symbol_table.bundle_types[var_info["type"]]
                        if member_name not in bundle_members:
                            raise SemanticError(f"Semantic Error: Bundle type '{var_info['type']}' has no member '{member_name}'.", line)
                        member_type = bundle_members[member_name]
                        index += 3
                        target = MemberAccessNode(obj_name, member_name, line=line)
                        while tokens[index].type == "." and member_type in symbol_table.bundle_types:
                            next_member = tokens[index + 1].value
                            nested_members = symbol_table.bundle_types[member_type]
                            if next_member not in nested_members:
                                raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", line)
                            member_type = nested_members[next_member]
                            target = MemberAccessNode(target, next_member, line=line)
                            index += 2
                        if member_type not in {"seed", "tree"}:
                            raise SemanticError(f"Semantic Error: Cannot apply '{operator}' to member '{member_name}' of type '{member_type}'.", line)
                        assignments_node.add_child(UnaryOpNode(operator, target, "pre", line=line))

                    else:
                        if var_info["type"] not in {"seed", "tree"}:
                            raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in expression.", line)
                        operand = ASTNode("Identifier", tokens[index].value, line=line)
                        index += 1
                        assignments_node.add_child(UnaryOpNode(operator, operand, "pre", line=line))

                else:
                    raise SemanticError(f"Syntax Error: Expected identifier after '{operator}'.", line)

            if tokens[index].type == ",":
                index += 1
                token = tokens[index]
                continue

            else:
                break
            
        if len(assignments_node.children) > 1:
            return assignments_node, index
        
        else:
            return assignments_node.children[0], index


    elif token.value in {"plant"}:
        node, index = parse_print(tokens, index)
        return node, index

    elif token.value == "water":
        node, index = parse_water_statement(tokens, index)
        return node, index

    elif token.value == "spring":
        node, index = parse_if(tokens, index, func_type)
        return node, index

    elif token.value in {"reclaim"}:
        node, index = parse_return(tokens, index, func_type)
        return node, index 
    
    elif token.value == "cultivate":
        node, index = parse_for(tokens, index, func_type)
        return node, index

    elif token.value in {"grow"}:
        node, index = parse_while(tokens, index, func_type)
        return node, index
    
    elif token.value in {"tend"}:
        node, index = parse_do(tokens, index, func_type)
        return node, index
    
    elif token.value in {"harvest"}:
        node, index = parse_switch(tokens, index, func_type)
        return node, index
    
    elif token.value in {"prune"}:
        if not is_inside_loop_or_switch_stack():
            raise SemanticError(f"Semantic Error: 'prune' statement used outside a loop or switch statement.", line)
        node = BreakNode(line)
        index += 1
        return node, index
        
    elif token.value in {"skip"}:
        if not is_inside_loop_or_switch_stack():
            raise SemanticError(f"Semantic Error: 'skip' statement used outside a loop or switch statement.", line)
        node = ContinueNode(line)
        index += 1
        return node, index

    elif token.value in {"variety", "soil"}:
        raise SemanticError(f"Semantic Error: '{token.value}' statement used outside a 'harvest' block.", line)

    elif token.type == "{":
        index += 1
        block_node = ASTNode("Block", line=line)
        while tokens[index].type != "}":
            stmt, index = parse_statement(tokens, index, func_type)
            if stmt:
                block_node.add_child(stmt)
        index += 1
        return block_node, index

    else:
        raise SemanticError(f"Syntax Error: Unexpected token '{token.value}' in statement.", line)


def parse_list_access(tokens, index):
    line = tokens[index].line
    list_name = tokens[index].value

    list_info = symbol_table.lookup_variable(list_name)
    if isinstance(list_info, str):
        raise SemanticError(list_info, line)
    
    if not list_info.get("is_list", False) and list_info.get("type") != "vine":
        raise SemanticError(f"Semantic Error: Variable '{list_name}' is not a list.", line)
    
    list_type = list_info["type"]
    index += 2 

    index_node, index, idx_type = parse_equality(tokens, index)

    if idx_type is not None and idx_type != "seed":
        raise SemanticError(
            f"Semantic Error: List index must be of type 'seed', got '{idx_type}'.",
            line,
        )

    if tokens[index].type != "]":
        raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
    
    index_wrapper = ASTNode("Index", line=line)
    index_wrapper.add_child(index_node)

    node = ListAccessNode(list_name, index_wrapper, line=line)

    while tokens[index + 1].type == "[":
        index += 2
        inner_index_node, index, inner_idx_type = parse_equality(tokens, index)
        if inner_idx_type is not None and inner_idx_type != "seed":
            raise SemanticError(
                f"Semantic Error: List index must be of type 'seed', got '{inner_idx_type}'.",
                line,
            )
        if tokens[index].type != "]":
            raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
        inner_wrapper = ASTNode("Index", line=line)
        inner_wrapper.add_child(inner_index_node)
        node = ListAccessNode(node, inner_wrapper, line=line)

    return node, index


def parse_list_assignment(tokens, index):
    line = tokens[index].line
    var_name = tokens[index].value

    var_info = symbol_table.lookup_variable(var_name)
    if isinstance(var_info, str):
        raise SemanticError(var_info, line)
    
    if not var_info.get("is_list", False):
        raise SemanticError(f"Semantic Error: '{var_name}' is not a list.", line)
    
    var_type = var_info["type"] 

    index += 2

    if var_info.get("is_fertile", False):
        raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile.", line)

    if tokens[index].value == "append":
        value_node, index = parse_append(tokens, index, var_name, var_type)

    elif tokens[index].value == "insert":
        value_node, index = parse_insert(tokens, index, var_name, var_type)

    elif tokens[index].value == "remove":
        value_node, index = parse_remove(tokens, index, var_name, var_type)

    elif tokens[index].type == "id":
        source_var = tokens[index].value
        source_info = symbol_table.lookup_variable(source_var)
        if isinstance(source_info, str):
            raise SemanticError(f"Semantic Error: Variable '{source_var}' used before declaration.", line)

        if source_info["is_list"] == False and tokens[index + 1].type != ".":
            raise SemanticError(f"Semantic Error: Cannot assign non-list '{source_var}' to list '{var_name}'.", line)

        source_type = source_info["type"]

        if var_type == "vine":
            if source_type == "leaf" and tokens[index + 1].type == ".":
                if (
                    tokens[index].type == "id" and
                    tokens[index + 1].type == "." and
                    tokens[index + 2].value == "taper"
                ):
                    if source_info["type"] != "leaf":
                        raise SemanticError(f"Semantic Error: Cannot use taper function on '{source_var}'. Must be a leaf type identifier.", line)

                    index += 3
                    is_list = True
                    taper_node = TaperNode(source_var, line=line)
                    value_node = ASTNode("Value", source_var, line=line)
                    value_node.add_child(taper_node)

            elif source_type == "leaf" and tokens[index + 1].type != ".":
                raise SemanticError(f"Semantic Error: Cannot assign non-list '{source_var}' to list '{var_name}'.", line)

        elif var_type != source_type:
            if not (var_type in {"seed", "tree"} and source_type in {"seed", "tree"}):
                raise SemanticError(
                    f"Semantic Error: Cannot assign list of '{source_type}' type to list of '{var_type}' type.", line
                )
            
        else:
            value_node = ASTNode("Value", source_var, line=line)
            index += 1

    elif tokens[index].type == "[":
        value_node, index = parse_list(tokens, index, var_type)

    else:
        raise SemanticError(f"Semantic Error: Invalid list assignment.", line)

    return AssignmentNode(var_name, value_node, line=line), index


def _types_compatible(declared, inferred):
    if declared == inferred:
        return True
    if declared in {"seed", "tree"} and inferred in {"seed", "tree"}:
        return True
    return False


def parse_expression_type(tokens, index, var_type):
    line = tokens[index].line

    if var_type not in {"seed", "tree", "vine", "leaf", "branch"} and var_type not in symbol_table.bundle_types:
        raise SemanticError("Semantic Error: Invalid type for assignment.", line)

    node, index, expr_type = parse_assignment_expression(tokens, index)

    if expr_type is None:
        raise SemanticError(
            "Semantic Error: Could not determine the type of the expression.",
            line,
        )
    if not _types_compatible(var_type, expr_type):
        raise SemanticError(
            f"Semantic Error: Type mismatch — cannot assign '{expr_type}' value to '{var_type}' variable.",
            line,
        )

    return node, index

def parse_expression_vine(tokens, index):
    line = tokens[index].line
    token = tokens[index]
    if tokens[index].type == "id" and tokens[index + 1].type == "(":
        func_name = tokens[index].value
        func_info = symbol_table.lookup_function(func_name)
        func_return_type = func_info["return_type"]
        func_params = func_info["params"]
        
        if func_return_type not in {"vine"}:
            error = f"Semantic Error: Cannot use function '{func_name}' of type {func_return_type}. Expected valid vine value."
            raise SemanticError(error, line)
        index += 1
        return parse_function_call(tokens, index, func_name, func_return_type, func_params)
    
    elif tokens[index].type == "id":
        variable_info = symbol_table.lookup_variable(tokens[index].value)
        if isinstance(variable_info, str):
            raise SemanticError(variable_info, line)

        is_list = variable_info.get("is_list", False)

        if is_list and tokens[index + 1].type != "[":
            raise SemanticError(f"Semantic Error: List '{token.value}' must be indexed with '[]'.", line)

        if variable_info["type"] != "vine":
            error = f"Semantic Error: Cannot use '{tokens[index].value}' of type {variable_info['type']}. Expected valid vine value."
            raise SemanticError(error, line)

        node = ASTNode("Value", tokens[index].value)
        index += 1
        return node, index

    elif tokens[index].type == "stringlit":
        node = ASTNode("Value", tokens[index].value)
        index += 1
        return node, index

    else:
        error = f"Semantic Error: Expected valid vine value."
        raise SemanticError(error, line) 

def parse_expression_leaf(tokens, index):
    line = tokens[index].line  
    token = tokens[index]

    if tokens[index].type not in {"chrlit", "id", "stringlit"}:
        raise SemanticError(f"Semantic Error: Expected valid leaf value.", line)

    if tokens[index].type == "id" and tokens[index + 1].type == "(":
        func_name = tokens[index].value
        func_info = symbol_table.lookup_function(func_name)

        if isinstance(func_info, str):
            raise SemanticError(f"Semantic Error: Function '{func_name}' is not defined.", line)

        func_return_type = func_info["return_type"]
        if func_return_type not in {"vine", "leaf"}:
            raise SemanticError(f"Semantic Error: Cannot use function '{func_name}' of type '{func_return_type}'. Expected valid leaf value.", line)

        node, index = parse_function_call(tokens, index, func_name, func_return_type, func_info["params"])


    elif token.type == "id" and tokens[index + 1].type == "[":
        list_name = token.value
        list_info = symbol_table.lookup_variable(list_name)

        if isinstance(list_info, str):
            raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", token.line)

        if not list_info["is_list"] and list_info.get("type") != "vine":
            raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

        index += 2
        expr_node, index, _ = parse_expression(tokens, index)

        if tokens[index].type != "]":
            raise SemanticError("Syntax Error: Missing closing bracket.", token.line)

        index_node = ASTNode("Index", line=token.line)
        index_node.add_child(expr_node)

        index += 1
        node = ListAccessNode(list_name, index_node, line=token.line)

        while index < len(tokens) and tokens[index].type == "[":
            index += 1
            inner_expr, index, _ = parse_expression(tokens, index)
            if tokens[index].type != "]":
                raise SemanticError("Syntax Error: Missing closing bracket.", token.line)
            inner_index = ASTNode("Index", line=token.line)
            inner_index.add_child(inner_expr)
            index += 1
            node = ListAccessNode(node, inner_index, line=token.line)

    elif tokens[index].type == "id":
        var_name = tokens[index].value
        var_info = symbol_table.lookup_variable(var_name)
        if isinstance(var_info, str):
            raise SemanticError(var_info, line)
        is_list = var_info.get("is_list", False)
        if is_list and tokens[index + 1].type != "[":
            raise SemanticError(f"Semantic Error: List '{tokens[index].value}' must be indexed with '[]'.", line)

        if var_info["type"] not in {"vine", "leaf"}:
            raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']}. Expected valid leaf value.", line)

        node = ASTNode("Value", var_name, line=line)
        index += 1  

    elif tokens[index].type in {"chrlit", "stringlit"}:
        node = ASTNode("Value", tokens[index].value, line=line)
        index += 1 

    left_node = node

    if tokens[index].type in {"+", "-", "*", "/", "%", "<", ">", "<=", ">=", "==", "!="}:
        while tokens[index].type in {"+", "-", "*", "/", "%"}:
            op = tokens[index].value  
            index += 1 

            if tokens[index].type == "id" and tokens[index + 1].type == "(":
                func_name = tokens[index].value
                func_info = symbol_table.lookup_function(func_name)

                if isinstance(func_info, str):
                    raise SemanticError(f"Semantic Error: Function '{func_name}' is not defined.", line)

                func_return_type = func_info["return_type"]
                if func_return_type not in {"vine", "leaf"}:
                    raise SemanticError(f"Semantic Error: Cannot use function '{func_name}' of type '{func_return_type}'. Expected valid leaf value", line)

                right_node, index = parse_function_call(tokens, index, func_name, func_return_type, func_info["params"])

            elif tokens[index].type == "id" and tokens[index + 1].type == "[":
                list_name = tokens[index].value
                list_info = symbol_table.lookup_variable(list_name)

                if isinstance(list_info, str):
                    raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", token.line)

                if not list_info["is_list"] and list_info.get("type") != "vine":
                    raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

                index += 2
                expr_node, index, _ = parse_expression(tokens, index)

                if tokens[index].type != "]":
                    raise SemanticError("Syntax Error: Missing closing bracket.", token.line)

                index_node = ASTNode("Index", line=token.line)
                index_node.add_child(expr_node)

                index += 1
                right_node = ListAccessNode(list_name, index_node, line=token.line)


            elif tokens[index].type == "id":
                var_name = tokens[index].value
                var_info = symbol_table.lookup_variable(var_name)
                if isinstance(var_info, str):
                    raise SemanticError(var_info, line)
                is_list = var_info.get("is_list", False)

                if is_list and tokens[index + 1].type != "[":
                    raise SemanticError(f"Semantic Error: List '{token.value}' must be indexed with '[]' in expressions.", line)

                if var_info["type"] not in {"vine", "leaf"}:
                    raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in this expression.", line)

                right_node = ASTNode("Value", var_name, line=line)
                index += 1 

            else:
                right_node = ASTNode("Value", tokens[index].value, line=line)
                index += 1  

            left_node = BinaryOpNode(left_node, op, right_node, line=line)
    
    return left_node, index 


def parse_expression(tokens, index):
    left_node, index, left_type = parse_term(tokens, index)

    while tokens[index].type in {"+", "-", "`"}:
        op = tokens[index].value
        token = tokens[index]

        if op == "`":
            if left_type not in {"vine", "leaf"}:
                raise SemanticError(
                    f"Semantic Error: Cannot concatenate - left operand is of type '{left_type}', expected 'vine' or 'leaf'.",
                    token.line,
                )
            index += 1
            right_node, index, right_type = parse_term(tokens, index)
            if right_type not in {"vine", "leaf"}:
                raise SemanticError(
                    f"Semantic Error: Cannot concatenate - right operand is of type '{right_type}', expected 'vine' or 'leaf'.",
                    token.line,
                )
            left_node = BinaryOpNode(left_node, op, right_node)
            left_type = "vine"
        else:
            if left_type not in {"seed", "tree"}:
                raise SemanticError(
                    f"Semantic Error: Cannot use '{op}' on type '{left_type}'. Expected 'seed' or 'tree'.",
                    token.line,
                )
            index += 1
            right_node, index, right_type = parse_term(tokens, index)
            if right_type not in {"seed", "tree"}:
                raise SemanticError(
                    f"Semantic Error: Cannot use '{op}' on type '{right_type}'. Expected 'seed' or 'tree'.",
                    token.line,
                )
            left_node = BinaryOpNode(left_node, op, right_node)
            if left_type == "tree" or right_type == "tree":
                left_type = "tree"

    return left_node, index, left_type

def parse_term(tokens, index):
    left_node, index, left_type = parse_power(tokens, index)

    while tokens[index].type in {"*", "/", "%"}:
        op = tokens[index].value
        token = tokens[index]

        if left_type not in {"seed", "tree"}:
            raise SemanticError(
                f"Semantic Error: Cannot use '{op}' on type '{left_type}'. Expected 'seed' or 'tree'.",
                token.line,
            )

        if op == "%":
            if left_type == "tree":
                raise SemanticError(
                    "Semantic Error: Modulo operator '%' requires 'seed' (integer) operands, "
                    "but found 'tree' (decimal) value.",
                    token.line,
                )

        index += 1
        right_node, index, right_type = parse_power(tokens, index)

        if right_type not in {"seed", "tree"}:
            raise SemanticError(
                f"Semantic Error: Cannot use '{op}' on type '{right_type}'. Expected 'seed' or 'tree'.",
                token.line,
            )

        if op == "%" and right_type == "tree":
            raise SemanticError(
                "Semantic Error: Modulo operator '%' requires 'seed' (integer) operands, "
                "but found 'tree' (decimal) value.",
                token.line,
            )

        if op in {"/", "%"} and isinstance(right_node, ASTNode) and right_node.node_type == "Value":
            try:
                if float(right_node.value) == 0:
                    raise SemanticError(f"Semantic Error: Division or modulus by zero is undefined.", token.line)
            except ValueError:
                pass
            
        left_node = BinaryOpNode(left_node, op, right_node)
        if left_type == "tree" or right_type == "tree":
            left_type = "tree"

    return left_node, index, left_type

def parse_power(tokens, index):
    left_node, index, left_type = parse_unary(tokens, index)

    if tokens[index].type == "**":
        op = tokens[index].value
        token = tokens[index]

        if left_type not in {"seed", "tree"}:
            raise SemanticError(
                f"Semantic Error: Cannot use '{op}' on type '{left_type}'. Expected 'seed' or 'tree'.",
                token.line,
            )

        index += 1
        right_node, index, right_type = parse_power(tokens, index)

        if right_type not in {"seed", "tree"}:
            raise SemanticError(
                f"Semantic Error: Cannot use '{op}' on type '{right_type}'. Expected 'seed' or 'tree'.",
                token.line,
            )

        left_node = BinaryOpNode(left_node, op, right_node, line=token.line)
        if left_type == "tree" or right_type == "tree":
            left_type = "tree"

    return left_node, index, left_type

def parse_unary(tokens, index):

    if tokens[index].type in {"++", "--", "-", "~"}:
        op = tokens[index].value
        index += 1
        operand, index, operand_type = parse_unary(tokens, index)
        if op in {"++", "--", "-"} and operand_type not in {"seed", "tree"}:
            raise SemanticError(
                f"Semantic Error: Cannot use '{op}' on type '{operand_type}'. Expected 'seed' or 'tree'.",
                tokens[index - 1].line,
            )
        if op == "~" and operand_type not in {"seed", "tree"}:
            raise SemanticError(
                f"Semantic Error: Arithmetic negation '~' requires a numeric 'seed' or 'tree' operand, got '{operand_type}'.",
                tokens[index - 1].line,
            )
        return UnaryOpNode(op, operand, position="pre", line=tokens[index].line), index, operand_type

    node, index, factor_type = parse_factor(tokens, index)

    if index < len(tokens) and tokens[index].type in {"++", "--"} and tokens[index + 1].type != "id":
        op = tokens[index].value
        if factor_type not in {"seed", "tree"}:
            raise SemanticError(
                f"Semantic Error: Cannot use '{op}' on type '{factor_type}'. Expected 'seed' or 'tree'.",
                tokens[index].line,
            )
        node = UnaryOpNode(op, node, position="post", line=tokens[index].line)
        index += 1

    return node, index, factor_type

def parse_cast(tokens, index):
    token = tokens[index]
    cast_types = {"seed", "tree", "leaf", "branch", "vine"}
    if token.type == "(" and tokens[index + 1].value in cast_types:
        target_type = tokens[index + 1].value
        if tokens[index + 2].type != ")":
            raise SemanticError("Syntax Error: Missing closing parenthesis.", token.line)
        index += 3

        expr_node, index, _ = parse_expression(tokens, index)

        cast_node = CastNode(target_type, expr_node, line=token.line)
        return cast_node, index, target_type

    return parse_factor(tokens, index)


def parse_factor(tokens, index):
    token = tokens[index]

    if token.type == "(" and tokens[index + 1].value in {"seed", "tree", "leaf", "branch", "vine"}:
        node, index, cast_type = parse_cast(tokens, index)
        return node, index, cast_type

    if token.type == "(":
        index += 1
        node, index, inner_type = parse_expression_branch(tokens, index)
        if tokens[index].type != ")":
            raise SemanticError("Syntax Error: Missing closing parenthesis.", token.line)
        index += 1  
        return node, index, inner_type
    
    if token.type in {"intlit", "dblit", "chrlit", "stringlit", "sunshine", "frost"}:
        node = ASTNode("Value", token.value)
        index += 1
        return node, index, infer_literal_type(token.type)

    if token.value == "water":
        raise SemanticError(f"Semantic Error: water() is an I/O statement, not an expression. It cannot be used inside an expression.", token.line)

    if token.type == "id" and tokens[index + 1].type == "(":
        func_name = token.value
        func_info = symbol_table.lookup_function(func_name)
        if isinstance(func_info, str):
            raise SemanticError(f"Semantic Error: Function '{func_name}' is not declared.", token.line)
        func_return_type = func_info["return_type"]
        func_params = func_info["params"]
        node, index = parse_function_call(tokens, index, func_name, func_return_type, func_params)

        return node, index, func_return_type

    elif (
        tokens[index].type == "id" and
        tokens[index + 1].type == "." and
        tokens[index + 2].value == "ts"
    ):
        identifier = tokens[index].value

        identifier_info = symbol_table.lookup_variable(identifier)
        if isinstance(identifier_info, str):
            raise SemanticError(f"Semantic Error: Variable '{identifier}' used before declaration.", token.line)  

        if not identifier_info["is_list"] and identifier_info["type"] not in ("leaf", "vine"):
            raise SemanticError(f"Semantic Error: ts() can only be used on lists or strings, but '{identifier}' is of type {identifier_info['type']}.", token.line)
        
        index += 3

        ts_node, index = TSNode(identifier, line=token.line), index
        return ts_node, index, "seed"

    elif (
        tokens[index].type == "id" and
        tokens[index + 1].type == "." and
        tokens[index + 2].value in ("wilt", "bloom")
    ):
        func_name = tokens[index + 2].value
        identifier = tokens[index].value

        identifier_info = symbol_table.lookup_variable(identifier)
        if isinstance(identifier_info, str):
            raise SemanticError(f"Semantic Error: Variable '{identifier}' used before declaration.", token.line)

        if identifier_info["type"] != "vine":
            raise SemanticError(f"Semantic Error: {func_name}() can only be used on vine (string) variables, but '{identifier}' is of type {identifier_info['type']}.", token.line)

        index += 3

        if func_name == "wilt":
            node = SoilNode(identifier, line=token.line)
        else:
            node = BloomNode(identifier, line=token.line)
        return node, index, "vine"

    elif (
        tokens[index].type == "id" and
        tokens[index + 1].type == "."
    ):
        obj_name = tokens[index].value
        member_name = tokens[index + 2].value

        var_info = symbol_table.lookup_variable(obj_name)
        if isinstance(var_info, str):
            raise SemanticError(f"Semantic Error: Variable '{obj_name}' used before declaration.", token.line)

        var_type = var_info["type"]
        if var_type not in symbol_table.bundle_types:
            raise SemanticError(f"Semantic Error: Variable '{obj_name}' is not a bundle type.", token.line)

        bundle_members = symbol_table.bundle_types[var_type]
        if member_name not in bundle_members:
            raise SemanticError(f"Semantic Error: Bundle type '{var_type}' has no member '{member_name}'.", token.line)

        member_type = bundle_members[member_name]
        index += 3
        node = MemberAccessNode(obj_name, member_name, line=token.line)

        while index < len(tokens) and tokens[index].type == "." and member_type in symbol_table.bundle_types:
            next_member = tokens[index + 1].value
            nested_members = symbol_table.bundle_types[member_type]
            if next_member not in nested_members:
                raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", token.line)
            member_type = nested_members[next_member]
            node = MemberAccessNode(node, next_member, line=token.line)
            index += 2

        return node, index, member_type


    elif token.type == "id" and tokens[index + 1].type == "[":
        list_name = token.value
        list_info = symbol_table.lookup_variable(list_name)

        if isinstance(list_info, str):
            raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", token.line)

        if not list_info["is_list"] and list_info.get("type") != "vine":
            raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

        index += 2
        expr_node, index, _ = parse_expression(tokens, index)

        if tokens[index].type != "]":
            raise SemanticError("Syntax Error: Missing closing bracket.", token.line)

        index_node = ASTNode("Index", line=token.line)
        index_node.add_child(expr_node)

        index += 1
        list_access_node = ListAccessNode(list_name, index_node, line=token.line)

        while index < len(tokens) and tokens[index].type == "[":
            index += 1
            inner_expr, index, _ = parse_expression(tokens, index)
            if tokens[index].type != "]":
                raise SemanticError("Syntax Error: Missing closing bracket.", token.line)
            inner_index = ASTNode("Index", line=token.line)
            inner_index.add_child(inner_expr)
            index += 1
            list_access_node = ListAccessNode(list_access_node, inner_index, line=token.line)

        if index < len(tokens) and tokens[index].type == "." and list_info["type"] in symbol_table.bundle_types:
            index += 1
            member_name = tokens[index].value
            bundle_members = symbol_table.bundle_types[list_info["type"]]
            if member_name not in bundle_members:
                raise SemanticError(f"Semantic Error: Bundle type '{list_info['type']}' has no member '{member_name}'.", token.line)
            member_type = bundle_members[member_name]
            index += 1
            node = ArrayMemberAccessNode(list_access_node, member_name, line=token.line)

            while index < len(tokens) and tokens[index].type == "." and member_type in symbol_table.bundle_types:
                next_member = tokens[index + 1].value
                nested_members = symbol_table.bundle_types[member_type]
                if next_member not in nested_members:
                    raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", token.line)
                member_type = nested_members[next_member]
                node = MemberAccessNode(node, next_member, line=token.line)
                index += 2

            return node, index, member_type

        return list_access_node, index, list_info["type"]
        

    elif token.type == "id":
        variable_info = symbol_table.lookup_variable(token.value)
        if isinstance(variable_info, str):
            raise SemanticError(variable_info, token.line)
        is_list = variable_info.get("is_list", False)
        if is_list and tokens[index + 1].type != "[":
            raise SemanticError(f"Semantic Error: List '{token.value}' must be indexed with '[]' in expressions.", token.line)

        var_type = variable_info["type"]
        
        node = ASTNode("Value", token.value)
        index += 1  

        if index < len(tokens) and tokens[index].type in {"++", "--"}:
            op = tokens[index].value
            index += 1
            return UnaryOpNode(op, node, position="post", line=token.line), index, var_type

        return node, index, var_type


    else:
        if token.type in {";", "}", ")", ","}:
            error = f"Semantic Error: Expected an expression before '{token.value}'."
        else:
            error = f"Semantic Error: Cannot use '{token.value}' in this expression."
        raise SemanticError(error, token.line)


def _assignment_root_name(node):
    if node.node_type in {"Identifier", "Value", "Object", "ListName"}:
        if isinstance(node.value, ASTNode):
            return _assignment_root_name(node.value)
        return node.value
    if node.node_type in {"ListAccess", "MemberAccess", "ArrayMemberAccess"}:
        return _assignment_root_name(node.children[0])
    return None


def _assignment_target(node, line):
    root_name = _assignment_root_name(node)
    valid_node_types = {"Value", "Identifier", "ListAccess", "MemberAccess", "ArrayMemberAccess"}
    var_info = symbol_table.lookup_variable(root_name) if root_name is not None else None

    if node.node_type not in valid_node_types or isinstance(var_info, str) or var_info is None:
        raise SemanticError(
            "Semantic Error: Left-hand side of assignment expression must be a modifiable variable, list element, or bundle member.",
            line,
        )
    if var_info.get("is_fertile", False):
        raise SemanticError(
            f"Semantic Error: Variable '{root_name}' is declared as fertile and cannot be re-assigned a value.",
            line,
        )

    if node.node_type == "Value":
        node = ASTNode("Identifier", node.value, line=line)
    return node


def parse_assignment_expression(tokens, index):
    line = tokens[index].line
    left_node, index, left_type = parse_logical_expression(tokens, index)
    if tokens[index].type not in {"=", "+=", "-=", "*=", "/=", "%="}:
        return left_node, index, left_type

    operator = tokens[index].type
    target = _assignment_target(left_node, line)
    index += 1
    right_node, index, right_type = parse_assignment_expression(tokens, index)

    if operator == "=":
        if not _types_compatible(left_type, right_type):
            raise SemanticError(
                f"Semantic Error: Type mismatch - cannot assign '{right_type}' value to '{left_type}' variable.",
                line,
            )
        value_node = right_node
    else:
        if left_type not in {"seed", "tree"} or right_type not in {"seed", "tree"}:
            raise SemanticError(
                f"Semantic Error: Compound assignment '{operator}' requires numeric 'seed' or 'tree' operands.",
                line,
            )
        if operator == "%=" and left_type != "seed":
            raise SemanticError(
                "Semantic Error: Modulo assignment '%=' requires a 'seed' (integer) left-hand side.",
                line,
            )
        value_node = BinaryOpNode(copy.deepcopy(target), operator[0], right_node, line=line)

    return AssignmentNode(target, value_node, line=line), index, left_type


def parse_expression_branch(tokens, index):
    return parse_assignment_expression(tokens, index)


def parse_logical_expression(tokens, index):
    line = tokens[index].line
    left_node, index, left_type = parse_equality(tokens, index)

    
    while tokens[index].type in {"&&", "||"}:
        operator = tokens[index].value
        index += 1
        right_node, index, right_type = parse_equality(tokens, index)

        if left_type in {"vine", "leaf"} or right_type in {"vine", "leaf"}:
            raise SemanticError(
                f"Semantic Error: Logical operator '{operator}' is not valid for string or leaf operands.",
                line,
            )

        left_node = BinaryOpNode(left_node, operator, right_node, line=line)
        left_type = "branch"

    return left_node, index, left_type


def parse_equality(tokens, index):
    line = tokens[index].line
    left_node, index, left_type = parse_relational(tokens, index)

    while tokens[index].type in {"==", "!="}:
        operator = tokens[index].type
        index += 1
        right_node, index, right_type = parse_relational(tokens, index)

        if left_type is None or right_type is None:
            raise SemanticError(
                "Semantic Error: Could not determine the type of an operand in equality check.",
                line,
            )
        numeric = {"seed", "tree"}
        if left_type != right_type and not (left_type in numeric and right_type in numeric):
            raise SemanticError(
                f"Semantic Error: Cannot compare '{left_type}' with '{right_type}' using '{operator}'.",
                line,
            )

        left_node = BinaryOpNode(left_node, operator, right_node, line=line)
        left_type = "branch"

    return left_node, index, left_type


def parse_relational(tokens, index):
    line = tokens[index].line

    if tokens[index].type == "!":
        index += 1
        operand_node, index, operand_type = parse_relational(tokens, index)
        
        if operand_type != "branch":
            raise SemanticError(f"Semantic Error: ! operator can only apply to 'branch' value.", line)

        return UnaryOpNode("!", operand_node, line=line), index, "branch"

    left_node, index, left_type = parse_expression(tokens, index)

    if tokens[index].type in {"<", "<=", ">", ">="}:
        operator = tokens[index].type
        index += 1
        right_node, index, right_type = parse_expression(tokens, index)

        if left_type == "vine" or right_type == "vine":
            raise SemanticError(
                f"Semantic Error: Relational operator '{operator}' is not valid for string operands. Use '==' or '!='.",
                line,
            )

        if left_type and right_type:
            numeric = {"seed", "tree"}
            if left_type in numeric and right_type not in numeric:
                raise SemanticError(
                    f"Semantic Error: Cannot compare '{left_type}' with '{right_type}' using '{operator}'.",
                    line,
                )
            if left_type not in numeric and right_type in numeric:
                raise SemanticError(
                    f"Semantic Error: Cannot compare '{left_type}' with '{right_type}' using '{operator}'.",
                    line,
                )
            if left_type != right_type and not (left_type in numeric and right_type in numeric):
                raise SemanticError(
                    f"Semantic Error: Cannot compare '{left_type}' with '{right_type}' using '{operator}'.",
                    line,
                )

        left_node = BinaryOpNode(left_node, operator, right_node, line=line)
        left_type = "branch"

        return left_node, index, left_type
    
    return left_node, index, left_type


def check_lwk(tokens, index):
    start_index = index 
    op_found = False

    while tokens[index].type != ")":
        index += 1
        if tokens[index].type in {"<", "<=", ">", ">=", "==", "!=", "&&", "||", "sunshine", "frost"}:
            op_found = True
        if tokens[index].type == "id":
            var_info = symbol_table.lookup_variable(tokens[index].value)
            if isinstance(var_info, str):
                raise SemanticError(f"Semantic Error: Variable '{tokens[index].value}' used before declaration.", tokens[index].line)
            if var_info["type"] == "branch":
                op_found = True
        

    if tokens[index].type in {"<", "<=", ">", ">=", "==", "!=", "&&", "||"}:
        op_found = True

    return op_found, start_index

def parse_operand(tokens, index):
    token = tokens[index]
    line = token.line

    if token.value == "water":
        raise SemanticError(f"Semantic Error: water() is an I/O statement, not an expression. It cannot be used inside an expression.", token.line)

    if token.type == "(":
        if tokens[index+1].value in {"seed", "tree"}:
            expr_type = tokens[index+1].value
            expr_node, index, _ = parse_expression(tokens, index)
            return expr_node, index, expr_type
        
        elif tokens[index + 1].type == "id":
            var_name = tokens[index +1].value
            var_info = symbol_table.lookup_variable(var_name)
            if isinstance(var_info, str):
                var_type = None
            else:
                var_type = var_info["type"]


            is_lwk, index = check_lwk(tokens, index)
            if not is_lwk:
                expr_node, index, _ = parse_expression(tokens, index)
                index -= 1
                expr_type = "seed"
                
            else:
                index += 1
                expr_node, index, _ = parse_expression_branch(tokens, index)
                expr_type = "branch"

            is_lwk, index = check_lwk(tokens, index)
       
        
        index += 1
        return expr_node, index, expr_type

    if token.type in {"intlit", "dblit"}:
        expr_node, index, _ = parse_expression(tokens, index)
        return expr_node, index, infer_literal_type(token.type)

    if token.type in {"chrlit", "stringlit"}:
        expr_node, index, _ = parse_expression(tokens, index)
        return expr_node, index, infer_literal_type(token.type)


    if token.type in {"sunshine", "frost"}:
        expr_node, index, _ = parse_expression(tokens, index)
        return expr_node, index, infer_literal_type(token.type)

    if token.type == "id" and tokens[index + 1].type == "(":
        func_name = tokens[index].value
        func_info = symbol_table.lookup_function(func_name)

        if isinstance(func_info, str):
            raise SemanticError(f"Semantic Error: Function '{func_name}' is not declared.", line)
        
        func_return_type = func_info["return_type"]
        func_params = func_info["params"]

        func_node, index = parse_function_call(tokens, index, func_name, func_return_type, func_params)
        return func_node, index, func_return_type
    
    if token.type == "id" and tokens[index + 1].type == "[":
        list_name = token.value
        list_info = symbol_table.lookup_variable(list_name)

        if isinstance(list_info, str):
            raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", token.line)

        if not list_info["is_list"] and list_info.get("type") != "vine":
            raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

        expr_node, index, expr_type = parse_expression(tokens, index)
        return expr_node, index, expr_type

    if token.type in {"intlit", "dblit"}:
        expr_node, index, _ = parse_expression(tokens, index)
        return expr_node, index, infer_literal_type(token.type)

    if token.type == "chrlit":
        expr_node, index = parse_expression_leaf(tokens, index)
        return expr_node, index, infer_literal_type(token.type)

    if token.type == "stringlit":
        return ASTNode("Value", token.value, line=line), index + 1, "vine"

    if token.type in {"sunshine", "frost"}:
        return ASTNode("Value", token.value, line=line), index + 1, "branch"

    if token.type == "id" and tokens[index + 1].type == ".":
        var_info = symbol_table.lookup_variable(token.value)
        if not isinstance(var_info, str) and var_info["type"] in symbol_table.bundle_types:
            expr_node, index, expr_type = parse_expression(tokens, index)
            return expr_node, index, expr_type

    if token.type == "id":
        var_info = symbol_table.lookup_variable(token.value)
        if isinstance(var_info, str):
            raise SemanticError(f"Semantic Error: Variable '{token.value}' used before declaration.", line)
        
        var_type = var_info["type"]
        is_list = var_info.get("is_list", False)

        if is_list and tokens[index + 1].type != "[":
            if tokens[index + 1].type in {"+", "-", "*", "/", "%", "**", "==", "!=", ">", "<", ">=", "<="}:
                op_token = tokens[index + 1]
                if index + 2 < len(tokens) and tokens[index + 2].type == "id":
                    rhs_info = symbol_table.lookup_variable(tokens[index + 2].value)
                    if not isinstance(rhs_info, str) and rhs_info.get("is_list", False):
                        raise SemanticError(
                            f"Semantic Error: Cannot use '{op_token.value}' operator on arrays '{token.value}' and '{tokens[index + 2].value}'. Arrays must be indexed with '[]'.",
                            line,
                        )
            raise SemanticError(f"Semantic Error: List '{token.value}' must be indexed with '[]' in expressions.", line)
    
        if var_type in {"seed", "tree", "branch"}:
            expr_node, index, _ = parse_expression(tokens, index)
            
            return expr_node, index, var_type

        elif var_type == "leaf":
            expr_node, index = parse_expression_leaf(tokens, index)
            return expr_node, index, var_type

        elif var_type == "vine":
            expr_node, index, _ = parse_expression(tokens, index)
            return expr_node, index, "vine"

        elif var_type == "branch":
            return ASTNode("Value", token.value, line=line), index + 1, var_type

        elif var_type in symbol_table.bundle_types:
            expr_node, index, _ = parse_expression(tokens, index)
            return expr_node, index, var_type

        else:
            raise SemanticError(f"Semantic Error: Unsupported type '{var_type}'.", line)

    if token.type in {";", "}", ")", ","}:
        raise SemanticError(f"Semantic Error: Expected an expression before '{token.value}'.", line)
    raise SemanticError(f"Semantic Error: Cannot use '{token.value}' in this expression.", line)


def infer_literal_type(token_type):
    if token_type == "intlit":
        return "seed"
    if token_type == "dblit":
        return "tree"
    if token_type == "stringlit":
        return "vine"
    if token_type == "chrlit":
        return "leaf"
    if token_type in {"sunshine", "frost"}:
        return "branch"
    return None

def parse_assignment(tokens, index, var_name, var_type):
    line = tokens[index].line

    var_info = symbol_table.lookup_variable(var_name)
    if var_info and var_info["is_fertile"]:
        raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile.", line)

    if tokens[index].value == "water":
        water_line = tokens[index].line
        index += 1
        if tokens[index].type != "(":
            raise SemanticError(f"Syntax Error: Expected '(' after water.", water_line)
        index += 1
        water_type = None
        if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
            water_type = tokens[index].value
            index += 1
        if tokens[index].type != ")":
            raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter (e.g., water(seed)).", water_line)
        index += 1
        if water_type and not _types_compatible(var_type, water_type):
            raise SemanticError(f"Semantic Error: Type mismatch — cannot assign water({water_type}) to '{var_type}' variable.", water_line)
        value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=water_line)
    else:
        value_node, index = parse_expression_type(tokens, index, var_type)

    assignment_node = AssignmentNode(var_name, value_node, line=line)

    return assignment_node, index


def parse_function_call(tokens, index, func_name, func_type, func_params):
    line = tokens[index].line
    
    index += 2
    args_node = ASTNode("Arguments")
    provided_args = []  
    expected_params = func_params  
    
    while tokens[index].type != ")":
        if len(provided_args) >= len(expected_params):
            raise SemanticError(f"Semantic Error: Too many arguments in function call '{func_name}'.", line)

        expected_type = expected_params[len(provided_args)].children[0].value 
        
        expected_param = expected_params[len(provided_args)]
        is_array_param = any(child.node_type == "ArrayParam" for child in expected_param.children)

        if is_array_param:
            if tokens[index].type != "id":
                raise SemanticError(f"Semantic Error: Expected array variable for parameter {len(provided_args) + 1} of '{func_name}'.", line)
            arg_name = tokens[index].value
            arg_info = symbol_table.lookup_variable(arg_name)
            if isinstance(arg_info, str):
                raise SemanticError(arg_info, line)
            if not arg_info.get("is_list", False):
                raise SemanticError(f"Semantic Error: Argument '{arg_name}' is not an array. Parameter {len(provided_args) + 1} of '{func_name}' expects an array.", line)
            if arg_info["type"] != expected_type:
                raise SemanticError(f"Semantic Error: Array argument '{arg_name}' is of type '{arg_info['type']}', but parameter expects '{expected_type}'.", line)
            expr_node = ASTNode("Identifier", arg_name, line=line)
            index += 1
        else:
            expr_node, index = parse_expression_type(tokens, index, expected_type)

        arg_node = ASTNode("Argument")
        arg_node.add_child(expr_node)
        args_node.add_child(arg_node)

        provided_args.append((arg_node, expected_type))

   
        if tokens[index].type == ",":
            index += 1 

    index += 1 

    if tokens[index].type in {"++", "--"}:
        raise SemanticError(f"Semantic Error: Unary operators cannot be applied to function calls.", line)

    if len(provided_args) != len(expected_params):
        raise SemanticError(f"Semantic Error: Function '{func_name}' expects {len(expected_params)} arguments, but {len(provided_args)} were provided.", line)

    for i, (arg_node, arg_type) in enumerate(provided_args):
        expected_type = expected_params[i].children[0].value

        if expected_type in {"seed", "tree"} and arg_type == "seed":
            continue 
        
        if arg_type != expected_type:
            raise SemanticError(f"Semantic Error: Argument {i+1} of '{func_name}' should be '{expected_type}', but got '{arg_type}'.", line)

    return FunctionCallNode(func_name, args_node.children, line=line), index


def parse_water_statement(tokens, index):
    line = tokens[index].line
    index += 1

    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after water.", line)
    index += 1

    if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
        water_type = tokens[index].value
        index += 1
        if tokens[index].type != ")":
            raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter or a variable name.", line)
        index += 1
        if tokens[index].type != ";":
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        index += 1
        input_node = ASTNode("Input", f"water({water_type})", line=line)
        return input_node, index

    elif tokens[index].type == ")":
        index += 1
        if tokens[index].type != ";":
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        index += 1
        input_node = ASTNode("Input", "water()", line=line)
        return input_node, index

    elif tokens[index].type == "id":
        var_name = tokens[index].value
        var_info = symbol_table.lookup_variable(var_name)
        if isinstance(var_info, str):
            raise SemanticError(var_info, line)
        if var_info.get("is_fertile", False):
            raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-assigned a value.", line)
        var_type = var_info["type"]
        index += 1

        if tokens[index].type == "[":
            if not var_info.get("is_list", False) and var_info.get("type") != "vine":
                raise SemanticError(f"Semantic Error: Variable '{var_name}' is not a list.", line)
            index += 1
            index_expr, index, idx_type = parse_equality(tokens, index)
            if idx_type is not None and idx_type != "seed":
                raise SemanticError(f"Semantic Error: List index must be of type 'seed', got '{idx_type}'.", line)
            if tokens[index].type != "]":
                raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
            index += 1

            index_wrapper = ASTNode("Index", line=line)
            index_wrapper.add_child(index_expr)
            list_access_node = ListAccessNode(var_name, index_wrapper, line=line)

            while tokens[index].type == "[":
                index += 1
                inner_expr, index, inner_type = parse_equality(tokens, index)
                if inner_type is not None and inner_type != "seed":
                    raise SemanticError(f"Semantic Error: List index must be of type 'seed', got '{inner_type}'.", line)
                if tokens[index].type != "]":
                    raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
                index += 1
                inner_wrapper = ASTNode("Index", line=line)
                inner_wrapper.add_child(inner_expr)
                list_access_node = ListAccessNode(list_access_node, inner_wrapper, line=line)

            if tokens[index].type != ")":
                raise SemanticError(f"Semantic Error: Expected ')' after water(arr[i]).", line)
            index += 1
            if tokens[index].type != ";":
                raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
            index += 1
            input_node = ASTNode("Input", f"water({var_type})", line=line)
            assignment_node = AssignmentNode(list_access_node, input_node, line=line)
            return assignment_node, index

        if tokens[index].type != ")":
            raise SemanticError(f"Semantic Error: water() accepts only a single variable name or type parameter.", line)
        index += 1
        if tokens[index].type != ";":
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        index += 1

        input_node = ASTNode("Input", f"water({var_type})", line=line)
        value_ident = ASTNode("Identifier", var_name, line=line)
        assignment_node = AssignmentNode(var_name, input_node, line=line)
        return assignment_node, index

    else:
        raise SemanticError(f"Semantic Error: Invalid argument to water(). Expected a variable name or type.", line)


def parse_print(tokens, index):
    line = tokens[index].line
    index += 1

    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after plant statement.", line)
    index += 1
    token = tokens[index]

    args = []
    placeholder_count = 0

    if tokens[index].type == "stringlit":
        format_node, index, placeholder_count = parse_string_concatenation(tokens, index) 
        args.append(format_node)


    elif tokens[index].type == "id":
        identif_name = tokens[index].value

        if tokens[index + 1].type == "(":
            func_name = identif_name
            func_info = symbol_table.lookup_function(func_name)
            if isinstance(func_info, str):
                raise SemanticError(f"Semantic Error: Function '{func_name}' is not defined.", line)
            if func_info["return_type"] in {"seed", "tree"}:
                expr_node, index, _ = parse_expression(tokens, index)
                args.append(expr_node)
            elif func_info["return_type"] in {"vine"}:
                expr_node, index = parse_expression_vine(tokens, index)
                args.append(expr_node)
            elif func_info["return_type"] in {"leaf"}:
                expr_node, index = parse_expression_leaf(tokens, index)
                args.append(expr_node)
            elif func_info["return_type"] in {"branch"}:
                expr_node, index, _ = parse_expression_branch(tokens, index)
                args.append(expr_node)
            else:
                raise SemanticError(f"Semantic Error: Function '{func_name}' returns invalid type '{func_info['return_type']}'.", line)


        elif tokens[index].type == "id" and tokens[index + 1].type == "[":
            list_name = token.value
            list_info = symbol_table.lookup_variable(list_name)

            if isinstance(list_info, str):
                raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", tokens[index].line)

            list_type = list_info["type"]
            start_index = index

            if not list_info["is_list"] and list_info.get("type") != "vine":
                raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", tokens[index].line)

            index += 2
            expr_node, index, _ = parse_expression(tokens, index)

            if tokens[index].type != "]":
                raise SemanticError("Syntax Error: Missing closing bracket.", tokens[index].line)

            index_node = ASTNode("Index", line=tokens[index].line)
            index_node.add_child(expr_node)

            index += 1
            list_access_node = ListAccessNode(list_name, index_node, line=tokens[index].line)

            if list_type in {"seed", "tree"} or list_type in symbol_table.bundle_types:
                expr_node, index, _ = parse_expression(tokens, start_index)
                args.append(expr_node)

            elif list_info["is_list"]:
                args.append(list_access_node)
            

        else:   
            arg_info = symbol_table.lookup_variable(identif_name)
            if isinstance(arg_info, str):
                raise SemanticError(f"Semantic Error: Variable '{identif_name}' used before declaration.", line)
            
            if tokens[index + 1].type == "." and arg_info["type"] in symbol_table.bundle_types:
                expr_node, index, _ = parse_expression(tokens, index)
                args.append(expr_node)

            elif arg_info["type"] in {"vine", "leaf"} and tokens[index + 1].type == "`":
                expr_node, index, _ = parse_expression_branch(tokens, index)
                args.append(expr_node)
            
            elif arg_info["type"] in {"seed", "tree"}:
                expr_node, index, _ = parse_expression_branch(tokens, index)
                args.append(expr_node)
            else:
                index += 1
                args.append(ASTNode("Value", identif_name, line=line))
                
    elif tokens[index].type in {"intlit", "dblit"}:
        expr_node, index, _ = parse_expression_branch(tokens, index)
        args.append(expr_node)

    elif tokens[index].type in {"sunshine", "frost", "!"}:
        expr_node, index, _ = parse_expression_branch(tokens, index)
        args.append(expr_node)

    elif tokens[index].type in {"chrlit"}:
        expr_node, index, _ = parse_expression_branch(tokens, index)
        args.append(expr_node)

    elif tokens[index].type in {"("}:
        expr_node, index, _ = parse_expression_branch(tokens, index)
        args.append(expr_node)

    elif tokens[index].type in {"++", "--", "-"}:
        expr_node, index, _ = parse_expression(tokens, index)
        args.append(expr_node)

    else:
        raise SemanticError(f"Semantic Error: Expected valid argument in plant statement.", line)

    actual_args = []
    while tokens[index].type == ",":
        index += 1
        
        if tokens[index].type in {"intlit", "dblit", "-"}:
            arg_node, index, _ = parse_expression_branch(tokens, index)
            actual_args.append(arg_node)


        elif tokens[index].type == "id" and tokens[index + 1].type == "[":
            start_index = index
            list_name = tokens[index].value
            list_info = symbol_table.lookup_variable(list_name)
            list_type = list_info["type"]
            is_list = list_info["is_list"]
            
            if isinstance(list_info, str):
                raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", tokens[index].line)

            if not list_info["is_list"] and list_info.get("type") != "vine":
                raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", tokens[index].line)

            index += 2
            expr_node, index, _ = parse_expression_branch(tokens, index)

            if tokens[index].type != "]":
                raise SemanticError("Syntax Error: Missing closing bracket.", tokens[index].line)

            index_node = ASTNode("Index", line=tokens[index].line)
            index_node.add_child(expr_node)

            index += 1
            list_access_node = ListAccessNode(list_name, index_node, line=tokens[index].line)
            
            if list_type in {"seed", "tree"}:
                arg_node, index, _ = parse_expression(tokens, start_index)
                actual_args.append(arg_node)
                
            elif is_list:
                actual_args.append(list_access_node)
            

        elif tokens[index].type == "id" and tokens[index+1].type == "(":
            func_name = tokens[index].value
            func_info = symbol_table.lookup_function(func_name)
            index_start = index

            if isinstance(func_info, str):
                raise SemanticError(f"Semantic Error: Function '{func_name}' is not declared.", line)
            
            func_return_type = func_info["return_type"]
            func_params = func_info["params"]

            func_node, index = parse_function_call(tokens, index, func_name, func_return_type, func_params)
            if func_return_type in {"seed", "tree"}:
                expr_node, index, _ = parse_expression(tokens, index_start)
                actual_args.append(expr_node)

            else:
                actual_args.append(func_node)
            
            
        elif tokens[index].type == "id":
            arg_name = tokens[index].value
            arg_info = symbol_table.lookup_variable(arg_name)
            
            if isinstance(arg_info, str):
                raise SemanticError(f"Semantic Error: Variable '{arg_name}' used before declaration.", line)
            
            if arg_info["is_list"]:
                if tokens[index + 1].type != "[":
                    raise SemanticError(f"Semantic Error: List '{arg_name}' must be indexed with '[]' in expressions.", line)
                
            if tokens[index + 1].type == "." and arg_info["type"] in symbol_table.bundle_types:
                arg_node, index, _ = parse_expression(tokens, index)
                actual_args.append(arg_node)

            elif arg_info["type"] in {"seed", "tree"}:
                arg_node, index, _ = parse_expression_branch(tokens, index)
                actual_args.append(arg_node)

            elif arg_info["type"] in {"vine", "leaf"} and tokens[index + 1].type == "`":
                arg_node, index, _ = parse_expression_branch(tokens, index)
                actual_args.append(arg_node)
                
            else:
                actual_args.append(ASTNode("Value", arg_name, line=line))
                index += 1
            
        elif tokens[index].type in {"("}:
            arg_node, index, _ = parse_expression_branch(tokens, index)
            actual_args.append(arg_node)

        elif tokens[index].type == "stringlit":
            arg_node, index, _ = parse_string_concatenation(tokens, index)
            actual_args.append(arg_node)

        elif tokens[index].type in {"chrlit"}:
            arg_node, index, _ = parse_expression_branch(tokens, index)
            actual_args.append(arg_node)

        elif tokens[index].type in {"sunshine", "frost", "!"}:
            arg_node, index, _ = parse_expression_branch(tokens, index)
            actual_args.append(arg_node)

        elif tokens[index].type in {"++", "--"}:
            arg_node, index, _ = parse_expression(tokens, index)
            actual_args.append(arg_node)

        else:
            raise SemanticError(f"Semantic Error: Expected valid argument after ',' in plant statement.", line)

    if placeholder_count > 15:
        raise SemanticError(f"Semantic Error: Exceeded maximum amount of 15 arguments in plant statement.", line)

    if placeholder_count > 0 and placeholder_count != len(actual_args):
        raise SemanticError(f"Semantic Error: Found {len(actual_args)} argument(s). Expected {placeholder_count} argument(s).", line)
    
    args.extend(actual_args)

    if tokens[index].type != ")":
        raise SemanticError(f"Semantic Error: Expected ')' after {tokens[index-1].value} in plant statement.", line)
    index += 1

    return PrintNode(args, line=line), index

def parse_string_concatenation(tokens, index):
    line = tokens[index].line

    if tokens[index].type != "stringlit":
        raise SemanticError(f"Semantic Error: String concatenation must start with a string literal.", line)
    
    format_string = tokens[index].value
    raw_string = format_string.replace("\\{", "").replace("\\}", "")
    if "{" in raw_string or "}" in raw_string:
        if raw_string.count("{") != raw_string.count("}"):
            raise SemanticError(f"Semantic Error: Invalid string literal '{format_string}' in plant().", line)
        matches = re.findall(r"\{[^}]*\}", raw_string)

        for match in matches:
            if match != "{}":
                raise SemanticError(f"Syntax Error: Placeholders {{}} must be adjacent to each other within the string literal.", line)

    placeholder_count = raw_string.count("{}")
    left_node = ASTNode("FormattedString", tokens[index].value, line=line)
    index += 1

    while index < len(tokens) and tokens[index].type == "`":
        concat_op = tokens[index].value
        index += 1
        if tokens[index].type not in {"stringlit", "chrlit", "id"}:
            raise SemanticError(f"Semantic Error: Only values of type vine or leaf can be concatenated in plant().", line)

        if tokens[index].type == "id":
            var_name = tokens[index].value
            var_info = symbol_table.lookup_variable(var_name)
            if isinstance(var_info, str):
                raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)
            if var_info["type"] not in {"vine", "leaf"}:
                raise SemanticError(f"Semantic Error: Variable '{var_name}' with type {var_info['type']} cannot be concatenated in plant().", line)

        format_string = tokens[index].value
        raw_string = format_string.replace("\\{", "").replace("\\}", "")
        
        if "{" in raw_string or "}" in raw_string:
            if raw_string.count("{") != raw_string.count("}"):
                raise SemanticError(f"Semantic Error: Invalid string literal '{format_string}' in plant().", line)
            if "{}" not in raw_string:
                raise SemanticError(f"Syntax Error: Placeholders {{}} must be adjacent within the string literal.", line)
        
        placeholder_count += raw_string.count("{}")
        if tokens[index].type == "id":
            right_node = ASTNode("Identifier", tokens[index].value, line=line)
        elif tokens[index].type == "chrlit":
            right_node = ASTNode("Value", tokens[index].value, line=line)
        else:
            right_node = ASTNode("FormattedString", tokens[index].value, line=line)
        index += 1

        left_node = BinaryOpNode(left_node, concat_op, right_node, line=line)

    return left_node, index, placeholder_count


def parse_fertile(tokens, index):
    token = tokens[index]
    line = token.line
    index += 1
    if tokens[index].value not in {"seed", "tree", "vine", "leaf", "branch"}:
        raise SemanticError(f"Semantic Error: Invalid fertile variable type '{tokens[index].value}'.", line)
    
    var_type = tokens[index].value
    index += 1  

    if tokens[index].type != "id":
        raise SemanticError(f"Syntax Error: Expected identifier after '{var_type}'.", line)
    
    var_name = tokens[index].value
    index += 1

    if tokens[index].type != "=":
        raise SemanticError(f"Semantic Error: Fertile variables must be initialized.", line)
    index += 1

    expected_literals = {
        "seed": {"intlit"},
        "tree": {"dblit"},
        "vine": {"stringlit"},
        "leaf": {"chrlit"},
        "branch": {"sunshine", "frost"}
    }
    
    if tokens[index].type not in expected_literals[var_type]:
        raise SemanticError(f"Semantic Error: '{var_name}' must be initialized with a {var_type} literal.", line)

    value_node = ASTNode("Value", tokens[index].value, line=line)
    index += 1

    if tokens[index].type == ",":
        raise SemanticError(f"Semantic Error: Multiple fertile declaration is not allowed.", line)

    error = symbol_table.declare_variable(var_name, var_type, value=value_node, is_list=False, is_fertile=True)
    if isinstance(error, str):
        raise SemanticError(error, line)

    return FertileDeclarationNode(var_type, var_name, value_node, line=line), index

def parse_if(tokens, index, func_type):
    line = tokens[index].line
    index += 1

    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after 'spring'.", line)
    index += 1

    condition_expr, index, cond_type = parse_expression_branch(tokens, index)

    if cond_type != "branch":
        raise SemanticError(f"Semantic Error: spring condition must be branch, got {cond_type}.", line)
    
    if tokens[index].type != ")":
        raise SemanticError(f"Syntax Error: Expected ')' after 'spring' condition.", line)
    
    index += 1  

    symbol_table.enter_scope()
    
    condition_node = ASTNode("Condition", line=line)
    condition_node.add_child(condition_expr)

    if_node = IfStatementNode(condition_node, line=line)
    
    if tokens[index].type == "{":
        index += 1

        block_node = ASTNode("Block", line=line)

        while tokens[index].type != "}":
            stmt, index = parse_statement(tokens, index, func_type)
            if stmt:
                block_node.add_child(stmt)

        if tokens[index].type != "}":
            raise SemanticError(f"Syntax Error: Expected '}}' after 'spring' block.", line)
        index += 1
        symbol_table.exit_scope()
        if_node.add_child(block_node)

    else:
        raise SemanticError(f"Syntax Error: Expected '{{' after 'spring' condition.", line)


    while tokens[index].value == "bud":
        index += 1

        if tokens[index].type != "(":
            raise SemanticError(f"Syntax Error: Expected '(' after else-if.", line)
        index += 1  

        elseif_node = ASTNode("ElseIfStatement", line=line)

        elseif_condition_expr, index, elseif_cond_type = parse_expression_branch(tokens, index)

        if elseif_cond_type != "branch":
            raise SemanticError(f"Semantic Error: bud condition must be branch, got {elseif_cond_type}.", line)

        if tokens[index].type != ")":
            raise SemanticError(f"Syntax Error: Expected ')' after else-if condition.", line)
        index += 1 

        symbol_table.enter_scope()

        elseif_condition_node = ASTNode("Condition", line=line)
        elseif_condition_node.add_child(elseif_condition_expr)
        elseif_node.add_child(elseif_condition_node)

        if tokens[index].type == "{":
            index += 1

            elseif_block_node = ASTNode("Block", line=line)

            while tokens[index].type != "}":
                stmt, index = parse_statement(tokens, index, func_type)
                if stmt:
                    elseif_block_node.add_child(stmt)

            elseif_node.add_child(elseif_block_node)
            index += 1

            symbol_table.exit_scope()
            if_node.add_child(elseif_node)

        else:
            raise SemanticError(f"Syntax Error: Expected '{{' after else-if condition.", line)


    if tokens[index].value == "wither":
        index += 1

        if tokens[index].type == "{":
            index += 1
            symbol_table.enter_scope()

            else_node = ASTNode("ElseStatement", line=line)
            else_block_node = ASTNode("Block", line=line)

            while tokens[index].type != "}":
                stmt, index = parse_statement(tokens, index, func_type)
                if stmt:
                    else_block_node.add_child(stmt)

            index += 1
            symbol_table.exit_scope()
            else_node.add_child(else_block_node)
            if_node.add_child(else_node)
    return if_node, index


def parse_return(tokens, index, func_type):
    line = tokens[index].line
    index += 1

    if func_type == "empty":
        if tokens[index].type not in {"}", ";"}:
            raise SemanticError(f"Semantic Error: empty function must not return any value.", line)
        return ReturnNode(None, line=line), index

    if tokens[index].type in {";", "}"}:
        raise SemanticError(f"Semantic Error: Function expects to return a '{func_type}' value, but 'reclaim' has no return expression.", line)

    elif tokens[index].type == "id":
        identifier = tokens[index].value

        if tokens[index+1].type == "(":
            func_info = symbol_table.lookup_function(identifier)

            if isinstance(func_info, str):
                raise SemanticError(f"Semantic Error: Function '{identifier}' is not defined.", line)

            return_type = func_info["return_type"]
            if return_type != func_type:
                raise SemanticError(f"Semantic Error: Function '{identifier}' returns '{return_type}', but expected '{func_type}'.", line)

            return_expr, index = parse_expression_type(tokens, index, func_type)

        else:
            var_info = symbol_table.lookup_variable(identifier)
            if isinstance(var_info, str):
                raise SemanticError(f"Semantic Error: Variable '{identifier}' used before declaration.", line)

            is_member_access = var_info["type"] in symbol_table.bundle_types and tokens[index+1].type == "."
            if not is_member_access:
                if var_info["type"] not in [func_type, "seed", "tree"] and var_info["type"] != "seed" and var_info["type"] != "tree":                
                    raise SemanticError(f"Semantic Error: Variable '{identifier}' is of type '{var_info['type']}'. Expected return value: '{func_type}'.", line)

            return_expr, index = parse_expression_type(tokens, index, func_type)

    else:  
        return_expr, index = parse_expression_type(tokens, index, func_type)

    return ReturnNode(return_expr, line=line), index


def parse_for(tokens, index, func_type):
    line = tokens[index].line
    index += 1
    context_stack.append("ForNode")
    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after 'cultivate'.", line)
    index += 1

    if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "seed", "tree", "vine", "leaf", "branch"}:
        var_type = tokens[index].value
        var_name = tokens[index + 1].value
        index += 2

        initialization, index = parse_variable(tokens, index, var_name, var_type)

    elif tokens[index].type == "id":
        identifier_name = tokens[index].value
        var_info = symbol_table.lookup_variable(identifier_name)
        if isinstance(var_info, str):
            raise SemanticError(f"Semantic Error: Variable '{identifier_name}' used before declaration.", line)
        index += 1
        if tokens[index].type != "=":
            raise SemanticError(f"Syntax Error: Expected '=' after for loop identifier.", line)
        index += 1
        initialization, index = parse_assignment(tokens, index, identifier_name, var_info["type"])
        
    if tokens[index].type != ";":
        raise SemanticError(f"Syntax Error: Expected ';' after for loop initialization.", line)
    index += 1

    condition, index, cond_type = parse_expression_branch(tokens, index)

    if cond_type != "branch":
        raise SemanticError(f"Semantic Error: cultivate condition must be branch, got {cond_type}.", line)

    condition_node = ASTNode("Condition", line=line)
    condition_node.add_child(condition)

    if tokens[index].type != ";":
        raise SemanticError(f"Syntax Error: Expected ';' after for loop condition.", line)
    index += 1
    update_node = ASTNode("Update", line=line)

    while True:
        update, index = parse_update(tokens, index)
        update_node.add_child(update)
        if tokens[index].type == ",":
            index += 1
            continue
        else:
            break

    if tokens[index].type != ")":
        raise SemanticError(f"Syntax Error: Expected ')' after for loop update.", line)
    index += 1

    symbol_table.enter_scope()

    for_node = ForLoopNode(initialization, condition_node, update_node, line=line)

    if tokens[index].type == "{":
        index += 1

        block_node = ASTNode("Block", line=line)

        while tokens[index].type != "}":

            stmt, index = parse_statement(tokens, index, func_type)
            if stmt:
                block_node.add_child(stmt)

        index += 1
        

        symbol_table.exit_scope()
        context_stack.pop()

        for_node.add_child(block_node)
    
    else:
        raise SemanticError(f"Syntax Error: Expected '{{' after for loop condition.", line)
    
    return for_node, index

def parse_update(tokens, index):
    line = tokens[index].line

    if tokens[index].type == "id" or tokens[index].type in {"++", "--"}: 
        assignments_node = ASTNode("AssignmentList")
        while True:

            if tokens[index].type == "id":
                var_info = symbol_table.lookup_variable(tokens[index].value)
                if isinstance(var_info, str):
                    raise SemanticError(var_info, line)

                var_name = tokens[index].value
                var_type = var_info["type"]
                is_list = var_info.get("is_list", False)

                is_fertile = var_info.get("is_fertile", False)

                if is_fertile:
                    raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-assigned a value.", line)

                if is_list or (var_type == "vine" and tokens[index + 1].type == "["):
                    if tokens[index + 1].type == "=":
                        node, index = parse_list_assignment(tokens, index)
                        assignments_node.add_child(node)

                    elif tokens[index + 1].type == "[":

                        list_access_node, index = parse_list_access(tokens, index)

                        if tokens[index + 1].type == "=":
                            index += 2
                            value_node, index = parse_expression_type(tokens, index, var_type)
                            assign_node = AssignmentNode(list_access_node, value_node, line=tokens[index].line)
                            assignments_node.add_child(assign_node)
                        elif tokens[index + 1].type in {"++", "--"}:
                            if var_type not in {"seed", "tree"}:
                                raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_type} in expression.", line)
                            operator = tokens[index + 1].value
                            index += 2
                            assignments_node.add_child(UnaryOpNode(operator, list_access_node, "post", line=line))
                        else:
                            raise SemanticError("Semantic Error: Expected '=' or '++'/'--' after list access.", tokens[index + 1].line)


                elif tokens[index + 1].type in {"++", "--"}:
                    var_info = symbol_table.lookup_variable(tokens[index].value)
                    
                    if isinstance(var_info, str):
                        raise SemanticError(var_info, line)
                    
                    if var_info["type"] not in {"seed", "tree"}:
                        raise SemanticError(f"Semantic Error: Cannot use '{tokens[index].value}' of type {var_info['type']} in expression.", line)
                    operand = ASTNode("Identifier", tokens[index].value, line=line)
                    operator = tokens[index + 1].value
                    index += 2
                    assignments_node.add_child(UnaryOpNode(operator, operand, "post", line=line))

                elif tokens[index + 1].type == "=":
                    var_name = tokens[index].value
                    error = symbol_table.lookup_variable(var_name)
                    
                    if isinstance(error, str):
                        raise SemanticError(error, tokens[index].line)

                    index += 2
                    node, index = parse_assignment(tokens, index, var_name, error['type'])
                    assignments_node.add_child(node)

                elif tokens[index + 1].type in {"+=", "-=", "*=", "/=", "%=", "**="}:
                    compound_op = tokens[index + 1].value
                    base_op = compound_op[:-1]
                    cur_var_name = tokens[index].value
                    cur_var_info = symbol_table.lookup_variable(cur_var_name)
                    if isinstance(cur_var_info, str):
                        raise SemanticError(cur_var_info, line)
                    if cur_var_info.get("is_fertile", False):
                        raise SemanticError(f"Semantic Error: Variable '{cur_var_name}' is declared as fertile and cannot be re-assigned a value.", line)
                    cur_var_type = cur_var_info["type"]
                    if cur_var_type not in {"seed", "tree"}:
                        raise SemanticError(f"Semantic Error: Cannot use compound assignment on '{cur_var_name}' of type '{cur_var_type}'.", line)
                    if base_op == "%" and cur_var_type != "seed":
                        raise SemanticError(
                            f"Semantic Error: Modulo operator '%' requires 'seed' (integer) operands, "
                            f"but '{cur_var_name}' is of type 'tree'.",
                            line,
                        )
                    index += 2
                    rhs_node, index, rhs_type = parse_expression(tokens, index)
                    if rhs_type not in {"seed", "tree"}:
                        raise SemanticError(
                            f"Semantic Error: Cannot use '{base_op}=' with right-hand side of type '{rhs_type}'. Expected 'seed' or 'tree'.",
                            line,
                        )
                    lhs_node = ASTNode("Identifier", cur_var_name, line=line)
                    value_node = BinaryOpNode(lhs_node, base_op, rhs_node, line=line)
                    assign_node = AssignmentNode(cur_var_name, value_node, line=line)
                    assignments_node.add_child(assign_node)
                    
                
                else:
                    raise SemanticError(f"Semantic Error: Unexpected token '{tokens[index].value}' in statement.", line)

            elif tokens[index].value in {"++", "--"}:
                operator = tokens[index].value
                index += 1
                if tokens[index].type == "id":
                    var_name = tokens[index].value
                    var_info = symbol_table.lookup_variable(var_name)
                    if isinstance(var_info, str):
                        raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)

                    if tokens[index + 1].type == "[":
                        if var_info["type"] not in {"seed", "tree"}:
                            raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in expression.", line)
                        list_access_node, index = parse_list_access(tokens, index)
                        index += 1
                        assignments_node.add_child(UnaryOpNode(operator, list_access_node, "pre", line=line))

                    elif tokens[index + 1].type == ".":
                        obj_name = tokens[index].value
                        if var_info["type"] not in symbol_table.bundle_types:
                            raise SemanticError(f"Semantic Error: Variable '{obj_name}' is not a bundle type.", line)
                        member_name = tokens[index + 2].value
                        bundle_members = symbol_table.bundle_types[var_info["type"]]
                        if member_name not in bundle_members:
                            raise SemanticError(f"Semantic Error: Bundle type '{var_info['type']}' has no member '{member_name}'.", line)
                        member_type = bundle_members[member_name]
                        index += 3
                        target = MemberAccessNode(obj_name, member_name, line=line)
                        while tokens[index].type == "." and member_type in symbol_table.bundle_types:
                            next_member = tokens[index + 1].value
                            nested_members = symbol_table.bundle_types[member_type]
                            if next_member not in nested_members:
                                raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", line)
                            member_type = nested_members[next_member]
                            target = MemberAccessNode(target, next_member, line=line)
                            index += 2
                        if member_type not in {"seed", "tree"}:
                            raise SemanticError(f"Semantic Error: Cannot apply '{operator}' to member '{member_name}' of type '{member_type}'.", line)
                        assignments_node.add_child(UnaryOpNode(operator, target, "pre", line=line))

                    else:
                        if var_info["type"] not in {"seed", "tree"}:
                            raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in expression.", line)
                        operand = ASTNode("Identifier", tokens[index].value, line=line)
                        index += 1
                        assignments_node.add_child(UnaryOpNode(operator, operand, "pre", line=line))

                else:
                    raise SemanticError(f"Syntax Error: Expected identifier after '{operator}'.", line)

            if tokens[index].type == ",":
                index += 1
                token = tokens[index]
                continue

            else:
                break
            
        if len(assignments_node.children) > 1:
            return assignments_node, index
        
        else:
            return assignments_node.children[0], index
            
    
    elif tokens[index].type in {"++", "--"}:
        operator = tokens[index].value
        index += 1

        if tokens[index].type == "id":
            var_name = symbol_table.lookup_variable(tokens[index].value)
            if isinstance(var_name, str):
                raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)
            
            operand = ASTNode("Identifier", tokens[index].value, line=line)
            index += 1

            return UnaryOpNode(operator, operand, "pre", line=line), index
        
    raise SemanticError(f"Semantic Error: Invalid update statement.", line)
    
def parse_while(tokens, index, func_type):
    line = tokens[index].line
    index += 1
    context_stack.append("WhileNode")
    
    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after 'grow'.", line)
    index += 1

    condition, index, cond_type = parse_expression_branch(tokens, index)

    if cond_type != "branch":
        raise SemanticError(f"Semantic Error: grow condition must be branch, got {cond_type}.", line)

    if tokens[index].type != ")":
        raise SemanticError(f"Syntax Error: Expected ')' after 'grow' condition.", line)
    
    index += 1

    symbol_table.enter_scope()

    condition_node = ASTNode("Condition", line=line)
    condition_node.add_child(condition)
    while_node = WhileLoopNode(condition_node, line=line)

    if tokens[index].type == "{":
        index += 1

        block_node = ASTNode("Block", line=line)

        while tokens[index].type != "}":

            stmt, index = parse_statement(tokens, index, func_type)
            if stmt:
                block_node.add_child(stmt)

        index += 1
        symbol_table.exit_scope()
        context_stack.pop()

        while_node.add_child(block_node)
    
    else:
        raise SemanticError(f"Syntax Error: Expected '{{' after 'grow' condition.", line)
    
    return while_node, index

def parse_do(tokens, index, func_type):
    line = tokens[index].line
    index += 1

    symbol_table.enter_scope()
    context_stack.append("DoWhileNode")

    if tokens[index].type != "{":
        raise SemanticError(f"Syntax Error: Expected '{{' after 'tend'.", line)
    index += 1

    block_node = ASTNode("Block", line=line)

    while tokens[index].type != "}":

        stmt, index = parse_statement(tokens, index, func_type)
        if stmt:
            block_node.add_child(stmt)
        

    index += 1

    if tokens[index].value not in {"grow"}:
        raise SemanticError(f"Syntax Error: Expected 'grow' after 'tend' block.", line)
    index += 1

    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after 'grow'.", line)
    index += 1

    condition, index, cond_type = parse_expression_branch(tokens, index)

    if cond_type != "branch":
        raise SemanticError(f"Semantic Error: tend condition must be branch, got {cond_type}.", line)

    if tokens[index].type != ")":
        raise SemanticError(f"Syntax Error: Expected ')' after 'grow' condition.", line)
    index += 1

    do_node = DoWhileLoopNode(condition, line=line)

    condition_node = ASTNode("Condition", line=line)
    condition_node.add_child(condition)

    do_node.add_child(block_node)
    do_node.add_child(condition_node)

    symbol_table.exit_scope()
    context_stack.pop()
    return do_node, index


def parse_switch(tokens, index, func_type):
    line = tokens[index].line
    index += 1
    context_stack.append("SwitchNode")

    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after 'harvest'.", line)
    index += 1

    switch_type = None

    if tokens[index].type == "id":
        var_info = symbol_table.lookup_variable(tokens[index].value)
        if isinstance(var_info, str):
            raise SemanticError(f"Semantic Error: Variable '{tokens[index].value}' used before declaration.", line)
        var_type = var_info["type"]
        if var_type in {"vine", "tree"}:
            raise SemanticError(f"Semantic Error: 'harvest' expression must be 'seed'/'leaf'/'branch', not '{var_type}'.", line)
        switch_type = var_type
        switch_expr, index = parse_expression_type(tokens, index, var_type)
        

    elif tokens[index].type in {"intlit", "chrlit", "sunshine", "frost"} or tokens[index].type in {"--", "++", "-", "("}:
        if tokens[index].type == "intlit" or tokens[index].type in {"--", "++", "-"}:
            switch_type = "seed"
        elif tokens[index].type == "chrlit":
            switch_type = "leaf"
        elif tokens[index].type in {"sunshine", "frost"}:
            switch_type = "branch"
        elif tokens[index].type == "(":
            switch_type = "seed"
        switch_expr, index, _ = parse_expression(tokens, index)

    elif tokens[index].type in {"stringlit"}:
        raise SemanticError(f"Semantic Error: 'harvest' expression must be 'seed'/'leaf'/'branch', not 'vine'.", line)

    elif tokens[index].type in {"dblit"}:
        raise SemanticError(f"Semantic Error: 'harvest' expression must be 'seed'/'leaf'/'branch', not 'tree'.", line)

    else:
        raise SemanticError(f"Semantic Error: Invalid token '{tokens[index].value}' used in expression.", line)

    if tokens[index].type != ")":
        raise SemanticError(f"Syntax Error: Expected ')' after 'harvest' expression.", line)
    index += 1

    if tokens[index].type != "{":
        raise SemanticError(f"Syntax Error: Expected '{{' after 'harvest' expression.", line)
    index += 1
    
    symbol_table.enter_scope()

    case_nodes = []
    default_case = None
    seen_case_values = set()

    while tokens[index].value in {"variety"}:
        case_line = tokens[index].line
        index += 1
        line = tokens[index].line

        if tokens[index].type not in {"chrlit", "stringlit", "sunshine", "frost", "intlit", "dblit"}:
            raise SemanticError(f"Semantic Error: Expected valid literal value after 'variety'.", line)

        lit_type_map = {
            "intlit": "seed",
            "dblit": "tree",
            "stringlit": "vine",
            "chrlit": "leaf",
            "sunshine": "branch",
            "frost": "branch",
        }
        lit_type = lit_type_map.get(tokens[index].type)
        if switch_type and lit_type and lit_type != switch_type:
            raise SemanticError(
                f"Semantic Error: 'variety' value type mismatch — expected '{switch_type}' but got '{lit_type}' ('{tokens[index].value}').",
                tokens[index].line,
            )

        case_val_key = tokens[index].value
        if case_val_key in seen_case_values:
            raise SemanticError(
                f"Semantic Error: Duplicate 'variety' value '{case_val_key}' in 'harvest'.",
                tokens[index].line,
            )
        seen_case_values.add(case_val_key)

        case_value = ASTNode("Value", tokens[index].value, line=case_line)
        index += 1

        if tokens[index].type != ":":
            raise SemanticError(f"Syntax Error: Expected ':' after 'variety' value.", line)
        index += 1

        case_block = ASTNode("Block", line=case_line)
        getout_node = None

        while tokens[index].value not in {"variety", "soil"} and tokens[index].type != "}":

            stmt, index = parse_statement(tokens, index, func_type)
            if stmt:
                case_block.add_child(stmt)

        if getout_node:
            if tokens[index].value not in {"variety", "soil"} and tokens[index].type != "}":
                raise SemanticError(f"Semantic Error: Unexpected statement after 'prune' in case block.", tokens[index].line)
            case_block.add_child(getout_node) 


        case_node = ASTNode("Case", line=case_line)
        case_node.add_child(case_value)
        case_node.add_child(case_block)
        case_nodes.append(case_node)

    if tokens[index].value in {"soil"}:
        line = tokens[index].line
        index += 1
             
        if tokens[index].type != ":":
            raise SemanticError(f"Syntax Error: Expected ':' after 'soil'.", line)
        index += 1
        
        default_block = ASTNode("Block", line=line)
        getout_node = None

        while tokens[index].type != "}":

            stmt, index = parse_statement(tokens, index, func_type)
            if stmt:
                default_block.add_child(stmt)

        if getout_node:
            if tokens[index].type != "}":
                raise SemanticError(f"Semantic Error: Unexpected statement after 'prune' in default block.", tokens[index].line)
            default_block.add_child(getout_node)


        default_case = ASTNode("Default", line=line)
        default_case.add_child(default_block)

    if tokens[index].type != "}":
        raise SemanticError(f"Syntax Error: Expected '}}' after 'harvest' statement.", line)
        
    index += 1

    symbol_table.exit_scope()
    context_stack.pop()

    return SwitchNode(switch_expr, case_nodes, default_case, line=line), index


def parse_list(tokens, index, expected_type):
    line = tokens[index].line
    if tokens[index].type != "[":
        raise SemanticError(f"Semantic Error: Expected '[' for list declaration.", line)
    index += 1
    
    elements = []

    if tokens[index].type == "]":
        index += 1
        return ListNode(elements=[], line=line), index
    
    while tokens[index].type != "]":
        expr, index = parse_expression_type(tokens, index, expected_type)
        elements.append(expr)

        if tokens[index].type == ",":
            index += 1
    
    if tokens[index].type != "]":
        raise SemanticError(f"Syntax Error: Expected ']' after list elements.", line)

    index += 1

    return ListNode(elements = elements, line = line), index

def parse_append(tokens, index, var_name, expected_type):

    line = tokens[index].line

    if tokens[index].value != "append":
        raise SemanticError(f"Semantic Error: Expected 'append'.", line)
    
    index += 1
    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after 'append'.", line)
    index += 1

    elements = []
    while tokens[index].type != ")":
        elem, index = parse_expression_type(tokens, index, expected_type)
        elements.append(elem)

        if tokens[index].type == ",":
            index += 1

    if tokens[index].type != ")":
        raise SemanticError(f"Syntax Error: Expected ')' after append arguments.", line)
    index += 1  

    return AppendNode(elements, line=line), index

def parse_insert(tokens, index, var_name, expected_type):
    line = tokens[index].line

    if tokens[index].value != "insert":
        raise SemanticError(f"Semantic Error: Expected 'insert'.", line)

    index += 1
    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after 'insert'.", line)
    index += 1

    expr_node, index, idx_type = parse_equality(tokens, index)
    if idx_type is not None and idx_type != "seed":
        raise SemanticError(
            f"Semantic Error: List index must be of type 'seed', got '{idx_type}'.",
            line,
        )
    index_value = ASTNode("Index", line=tokens[index].line)
    index_value.add_child(expr_node)

    if tokens[index].type != ",":
        raise SemanticError(f"Syntax Error: Expected ',' after index in 'insert'.", line)
    index += 1  

    elements = []

    while tokens[index].type != ")":
        elem, index = parse_expression_type(tokens, index, expected_type)
        elements.append(elem)

        if tokens[index].type == ",":
            index += 1

    if tokens[index].type != ")":
        raise SemanticError(f"Syntax Error: Expected ')' after insert arguments.", line)
    index += 1

    return InsertNode(index_value, elements, line=line), index

def parse_remove(tokens, index, var_name, expected_type):
    line = tokens[index].line

    if tokens[index].value != "remove":
        raise SemanticError(f"Semantic Error: Expected 'remove'.", line)

    index += 1
    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after 'remove'.", line)
    index += 1

    expr_node, index, idx_type = parse_equality(tokens, index)
    if idx_type is not None and idx_type != "seed":
        raise SemanticError(
            f"Semantic Error: List index must be of type 'seed', got '{idx_type}'.",
            line,
        )
    index_value = ASTNode("Index", line=tokens[index].line)
    index_value.add_child(expr_node)
        
    if tokens[index].type != ")":
        raise SemanticError(f"Syntax Error: Expected ')' after remove argument.", line)
    index += 1

    return RemoveNode(var_name, index_value, line=line), index


def is_inside_loop_or_switch_stack():
    return any(ctx in {"WhileNode", "DoWhileNode", "SwitchNode", "ForNode"} for ctx in context_stack)


def analyze_semantics(tokens):
    try:
        filtered = [t for t in tokens if t.type != '\n']
        ast = build_ast(filtered)

        st = {
            "variables": [
                {
                    "name": name,
                    "type": info["type"],
                    "scope": "global",
                    "is_list": info.get("is_list", False),
                    "is_constant": info.get("is_fertile", False),
                }
                for name, info in symbol_table.variables.items()
            ],
            "functions": {
                name: {
                    "return_type": info["return_type"],
                    "params": [
                        {
                            "type": p.children[0].value if p.children else "unknown",
                            "name": p.children[1].value if len(p.children) > 1 else "unknown",
                        }
                        for p in info["params"]
                    ] if info["params"] else [],
                }
                for name, info in symbol_table.functions.items()
            },
        }

        return {
            "success": True,
            "errors": [],
            "warnings": [],
            "symbol_table": st,
            "ast": ast,
        }

    except SemanticError as e:
        return {
            "success": False,
            "errors": [str(e)],
            "warnings": [],
            "symbol_table": {},
            "ast": None,
        }


