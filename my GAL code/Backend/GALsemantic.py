import re

##### ERROR ######
class SemanticError(Exception):
    def __init__(self, message,  line):
        super().__init__(message)
        self.message = f"Ln {line} {message}"

    def __str__(self):
        return self.message


##### SEMANTIC ANALYZER #####
class SemanticAnalyzer:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.visited_nodes = set()


##### AST NODES #####
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


###### SYMBOL TABLE ######

class SymbolTable:
    def __init__(self):
        self.variables = {}  # Stores variables
        self.global_variables = {}  # Stores global variables
        self.functions = {}  # Stores function definitions
        self.scopes = [{}]   # Stack of scopes (for local/global tracking)
        self.current_func_name = None
        self.function_variables = {}

    ###### VARIABLE ######
    def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
        scope = self.scopes[-1]
        current_func = self.current_func_name
    
        #for i, s in enumerate(self.scopes):
            #print(f"[SCOPE {i}] {s}")

        if name in self.functions:
            return f"Semantic Error: Variable '{name}' already declared as a function."

        if current_func:
            if current_func not in self.function_variables:
                self.function_variables[current_func] = set()

            if name in self.function_variables[current_func]:
                return f"Semantic Error: Variable '{name}' already declared in this function."

            self.function_variables[current_func].add(name)

        if self.current_func_name:
            
            scope[name] = {
                "type": type_,  
                "value": value,
                "is_list": is_list,
                "is_fertile": is_fertile
            }
        else:
            if name in self.global_variables:
                return f"Semantic Error: Variable '{name}' already declared."
            
            self.variables[name] = {
                "type": type_,
                "value": value,
                "is_list": is_list,
                "is_fertile": is_fertile
            }
        


    def lookup_variable(self, name):
        for i, scope in enumerate(reversed(self.scopes)):
            if name in scope:
                return scope[name]
        
        if name in self.variables:
            return self.variables[name]

        return f"Semantic Error: Variable '{name}' used before declaration."
    
    def set_variable(self, name, value):
        current_scope = self.scopes[-1]

        if name in current_scope:
            current_scope[name]["value"] = value
        else:
            return f"Semantic Error: Variable '{name}' not declared in the current scope."

    ###### FUNCTION ######
    def declare_function(self, name, return_type, params, node=None):
        if name in self.functions:
            return f"Semantic Error: Function '{name}' already declared."
        self.functions[name] = {"return_type": return_type, "params": params, "node": node}

    def lookup_function(self, name):
        if name in self.functions:
            return self.functions[name]
        return f"Semantic Error: Function '{name}' is not defined."
    

    ###### SCOPE ######
    def enter_scope(self):
        self.scopes.append({})
        

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
        
        if self.current_func_name:
            current_func = self.current_func_name

            if current_func in self.function_variables:
                self.function_variables[current_func].clear()


    def debug_scopes(self):
        print("\n====== SYMBOL TABLE DEBUG ======")
        print("🔹 Local Scopes (Stacked from Global to Inner Scope):")
        for i, scope in enumerate(self.scopes):
            print(f"  Scope {i}: {scope}")
        print("================================\n")


symbol_table = SymbolTable()
semantic_analyzer = SemanticAnalyzer(symbol_table)
context_stack = []

#######################
###### BUILD AST ######
#######################

def build_ast(tokens):
    """Constructs an AST from the token list after LL(1) parsing."""
    root = ProgramNode()
    symbol_table.variables = {}  # Stores variables 
    symbol_table.functions = {}  # Stores function definitions
    symbol_table.scopes = [{}] 
    symbol_table.function_variables = {}
    context_stack = []
    index = 0
    symbol_table.current_func_name = None
    
    while index < len(tokens):
        token = tokens[index]

        # Skip semicolons between top-level declarations
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
            if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty", "seed", "tree", "leaf", "branch", "vine", "empty"}:
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
                raise SemanticError(f"Syntax Error: Expected data type for function declaration after 'pollinate'.", tokens[index].line)

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
            error = f"Syntax Error: Invalid function or variable declaration."
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

    main_func_declared = False

    # Entry point: root()  (legacy alias: skibidi{...})
    if func_name in {"root"}:
        symbol_table.enter_scope()
        index += 1  # consume keyword

        # root() requires empty parameter list
        if tokens[index].type == "(":
            index += 1
            if tokens[index].type != ")":
                raise SemanticError(f"Syntax Error: {func_name}() should not have parameters.", line)
            index += 1
        elif func_name == "root":
            raise SemanticError("Syntax Error: Missing () for root function declaration.", line)

        params_node = ASTNode("Parameters")
        func_node = FunctionDeclarationNode(func_type, func_name, params_node)
        main_func_declared = True

    else:
        if tokens[index].type != "(":
            error = f"Syntax Error: Missing () for function declaration."
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
                    params_node.add_child(param_node)
                    error = symbol_table.declare_variable(param_name, param_type)
                    if error:
                        raise SemanticError(error, line)
                    index += 1

                    if tokens[index].type == ",":
                        index += 1

                else:
                    error = f"Syntax Error: Invalid parameter declaration."
                    raise SemanticError(error, line)

            else:
                index += 1

        symbol_table.declare_function(func_name, func_type, params_node.children)
        index += 1
        func_node = FunctionDeclarationNode(func_type, func_name, params_node)

    if tokens[index].type == "{":
        index += 1
        block_node = ASTNode("Block")
        return_found = False
        
        while tokens[index].type != "}":
            stmt, index = parse_statement(tokens, index, func_type)
            if stmt:
                block_node.add_child(stmt)
                if isinstance(stmt, ReturnNode):
                    return_found = True
        
        if (func_type != "empty" and not return_found) and func_name not in {"root"}:
            raise SemanticError(f"Semantic Error: Function '{func_name}' must return a value of type '{func_type}' at the end.", line)
        
        index += 1
        func_node.add_child(block_node)
        symbol_table.exit_scope()
        symbol_table.current_func_name = None
    else:
        error = f"Syntax Error: Function body must be enclosed in curly braces."
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

                index += 5
                is_list = True
                taper_node = TaperNode(identifier, line=line)
                var_node.add_child(taper_node)

            elif tokens[index].value in {"water"}:
                index += 1
                if tokens[index].type == "(":
                    index += 1
                    # Allow optional type parameter: water() or water(seed)
                    water_type = None
                    if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
                        water_type = tokens[index].value
                        index += 1
                    if tokens[index].type != ")":
                        raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter (e.g., water(seed)).", line)
                    index += 1
                    value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=line)
                else:
                    raise SemanticError(f"Syntax Error: Expected () after water.", line)

                var_node.add_child(value_node)

            elif tokens[index].type == "[":
                is_list = True
                value_node, index = parse_list(tokens, index, var_type)
                var_node.add_child(value_node)

            else:
                value_node, index = parse_expression_type(tokens, index, var_type)
                var_node.add_child(value_node)
   
        else:
            # Uninitialized declaration: vine name; or seed x;
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
    """Advance past any consecutive ';' tokens."""
    while index < len(tokens) and tokens[index].type == ";":
        index += 1
    return index


def parse_statement(tokens, index, func_type = None):
    token = tokens[index]

    # Skip stray semicolons before the actual statement
    if token.type == ";":
        return None, index + 1

    line = token.line

    if token.value in {"seed", "tree", "vine", "leaf", "branch"}:
        # Normalize GAL type keywords to internal types
        var_type = token.value
        var_name = tokens[index + 1].value
        index += 2

        node, index = parse_variable(tokens, index, var_name, var_type)
        return node, index
    
    
    elif token.value == "fertile":
        node, index = parse_fertile(tokens, index)
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

                if is_list:
                    if tokens[index + 1].type == "=":
                        node, index = parse_list_assignment(tokens, index)
                        assignments_node.add_child(node)

                    elif tokens[index + 1].type == "[":
                        
                        list_access_node, index = parse_list_access(tokens, index)
                        
                        if tokens[index + 1].type == "=":
                            index += 2 
                            value_node, index = parse_expression(tokens, index)
                            assign_node = AssignmentNode(list_access_node, value_node, line=tokens[index].line)
                            assignments_node.add_child(assign_node)

                        elif tokens[index + 1].type in {"++", "--"}:
                            
                            if var_type not in {"seed", "tree"}:
                                raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_type} in expression.", line)
                            operator = tokens[index + 1].value
                            unary_node = UnaryOpNode(operator, list_access_node, "post", line=line)
                            index += 2

                            assignments_node.add_child(unary_node)
                            
                        
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


                
                else:
                    raise SemanticError(f"Semantic Error: Unexpected token '{tokens[index].value}' in statement.", line)

            elif tokens[index].value in {"++", "--"}:
                operator = tokens[index].value
                index += 1
                if tokens[index].type == "id":
                    var_name = tokens[index].value
                    var_info = symbol_table.lookup_variable(var_name)
                    if var_info["type"] not in {"seed", "tree"}:
                        raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in expression.", line)
                    
                    if isinstance(var_info, str):
                        raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)

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

    else:
        raise SemanticError(f"Syntax Error: Unexpected token '{token.value}' in statement.", line)


def parse_list_access(tokens, index):
    line = tokens[index].line
    list_name = tokens[index].value

    list_info = symbol_table.lookup_variable(list_name)
    if isinstance(list_info, str):
        raise SemanticError(list_info, line)
    
    if not list_info.get("is_list", False):
        raise SemanticError(f"Semantic Error: Variable '{list_name}' is not a list.", line)
    
    list_type = list_info["type"]
    index += 2 

    index_node, index = parse_expression(tokens, index)

    if tokens[index].type != "]":
        raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
    
    index_wrapper = ASTNode("Index", line=line)
    index_wrapper.add_child(index_node)

    return ListAccessNode(list_name, index_wrapper, line=line), index


def parse_list_assignment(tokens, index):
    """Parses full list assignment, list operations, or function calls on a list."""
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

    # List functions
    if tokens[index].value == "append":
        value_node, index = parse_append(tokens, index, var_name, var_type)

    elif tokens[index].value == "insert":
        value_node, index = parse_insert(tokens, index, var_name, var_type)

    elif tokens[index].value == "remove":
        value_node, index = parse_remove(tokens, index, var_name, var_type)

    # Assignment from another list
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

                    index += 5
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

    # Assignment from list literal
    elif tokens[index].type == "[":
        value_node, index = parse_list(tokens, index, var_type)

    else:
        raise SemanticError(f"Semantic Error: Invalid list assignment.", line)

    return AssignmentNode(var_name, value_node, line=line), index


def parse_expression_type(tokens, index, var_type):
    line = tokens[index].line
    if var_type in {"seed", "tree"}:
        return parse_expression_branch(tokens, index)

    elif var_type == "leaf":
        return parse_expression_branch(tokens, index)

    elif var_type == "vine":
        return parse_expression_branch(tokens, index)
    
    elif var_type == "branch":
        return parse_expression_branch(tokens, index)

    else:
        error = f"Semantic Error: Invalid type for assignment."
        raise SemanticError(error, line)

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

        if isinstance(variable_info, str):
            error = f"Semantic Error: Variable '{tokens[index].value}' used before declaration."
            raise SemanticError(error, line)
        
        if variable_info["type"] != "vine":
            error = f"Semantic Error: Cannot use '{tokens[index].value}' of type {variable_info['type']}. Expected valid vine value.", line
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

        if isinstance(func_info, str):  # Function not found
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

        if not list_info["is_list"]:
            raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

        index += 2
        expr_node, index = parse_expression(tokens, index)

        if tokens[index].type != "]":
            raise SemanticError("Syntax Error: Missing closing bracket.", token.line)

        index_node = ASTNode("Index", line=token.line)
        index_node.add_child(expr_node)

        index += 1
        node = ListAccessNode(list_name, index_node, line=token.line)

    elif tokens[index].type == "id":
        var_name = tokens[index].value
        var_info = symbol_table.lookup_variable(var_name)
        if isinstance(var_info, str):
            raise SemanticError(var_info, line)
        is_list = var_info.get("is_list", False)
        if is_list and tokens[index + 1].type != "[":
            raise SemanticError(f"Semantic Error: List '{tokens[index].value}' must be indexed with '[]'.", line)
        if isinstance(var_info, str):  # Variable not found
            raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)

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

                if isinstance(func_info, str):  # Function not found
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

                if not list_info["is_list"]:
                    raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

                index += 2
                expr_node, index = parse_expression(tokens, index)

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

                if isinstance(var_info, str):  # Variable not found
                    raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)

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
    """Parses an expression with right-to-left associativity for + and -."""
    left_node, index = parse_term(tokens, index)

    while tokens[index].type in {"+", "-"}:
        op = tokens[index].value
        index += 1
        right_node, index = parse_term(tokens, index)
        left_node = BinaryOpNode(left_node, op, right_node)

    return left_node, index

def parse_term(tokens, index):
    """Parses multiplication, division, and modulus with right-to-left associativity."""
    left_node, index = parse_unary(tokens, index)

    while tokens[index].type in {"*", "/", "%"}:
        op = tokens[index].value
        token = tokens[index]
        index += 1
        right_node, index = parse_unary(tokens, index)
        if op in {"/", "%"} and isinstance(right_node, ASTNode) and right_node.node_type == "Value":
            try:
                if float(right_node.value) == 0:
                    raise SemanticError(f"Semantic Error: Division or modulus by zero is undefined.", token.line)
            except ValueError:
                pass
            
        left_node = BinaryOpNode(left_node, op, right_node)

    return left_node, index

def parse_unary(tokens, index):

    if tokens[index].type in {"++", "--", "-"}:
        op = tokens[index].value
        index += 1
        operand, index = parse_unary(tokens, index)
        return UnaryOpNode(op, operand, position="pre", line=tokens[index].line), index

    node, index = parse_factor(tokens, index)

    if index < len(tokens) and tokens[index].type in {"++", "--"} and tokens[index + 1].type != "id":
        op = tokens[index].value
        node = UnaryOpNode(op, node, position="post", line=tokens[index].line)
        index += 1

    return node, index

def parse_cast(tokens, index):
    """Parses explicit type casting for the entire expression inside (type)."""
    token = tokens[index]
    if token.type == "(" and tokens[index + 1].value in {"seed", "tree"}:
        target_type = tokens[index + 1].value
        if tokens[index + 2].type != ")":
            raise SemanticError("Syntax Error: Missing closing parenthesis.", token.line)
        index += 3

        expr_node, index = parse_expression(tokens, index)

        cast_node = CastNode(target_type, expr_node, line=token.line)
        return cast_node, index

    return parse_factor(tokens, index)


def parse_factor(tokens, index):
    """Parses literals, identifiers, parenthesized expressions, and postfix operators."""
    token = tokens[index]

    if token.type == "(" and tokens[index + 1].value in {"seed", "tree"}:
        node, index = parse_cast(tokens, index)
        return node, index

    if token.type == "(":
        index += 1
        node, index = parse_expression(tokens, index)
        if tokens[index].type != ")":
            raise SemanticError("Syntax Error: Missing closing parenthesis.", token.line)
        index += 1  
        return node, index  
    
    if token.type in {"intlit", "dbllit", "chrlit", "stringlit", "sunshine", "frost"}:
        node = ASTNode("Value", token.value)
        index += 1
        return node, index
    
    if token.type == "id" and tokens[index + 1].type == "(":
        func_name = token.value
        func_info = symbol_table.lookup_function(func_name)
        func_return_type = func_info["return_type"]
        func_params = func_info["params"]
        if func_return_type not in {"seed", "tree"}:
            error = f"Semantic Error: Cannot use function '{func_name}' of type {func_return_type} in this expression."
            raise SemanticError(error, token.line)

        node, index = parse_function_call(tokens, index, func_name, func_return_type, func_params)

        return node, index

    elif (
        tokens[index].type == "id" and
        tokens[index + 1].type == "." and
        tokens[index + 2].value == "ts"
    ):
        identifier = tokens[index].value

        identifier_info = symbol_table.lookup_variable(identifier)
        if isinstance(identifier_info, str):
            raise SemanticError(f"Semantic Error: Variable '{identifier}' used before declaration.", token.line)  

        if not identifier_info["is_list"] and identifier_info["type"] != "leaf":
            raise SemanticError(f"Semantic Error: ts() can only be used on lists or strings, but '{identifier}' is of type {identifier_info['type']}.", token.line)
        
        index += 5

        ts_node, index = TSNode(identifier, line=token.line), index
        return ts_node, index


    elif token.type == "id" and tokens[index + 1].type == "[":
        list_name = token.value
        list_info = symbol_table.lookup_variable(list_name)

        if isinstance(list_info, str):
            raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", token.line)

        if not list_info["is_list"]:
            raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

        index += 2
        expr_node, index = parse_expression(tokens, index)

        if tokens[index].type != "]":
            raise SemanticError("Syntax Error: Missing closing bracket.", token.line)

        index_node = ASTNode("Index", line=token.line)
        index_node.add_child(expr_node)

        index += 1
        list_access_node = ListAccessNode(list_name, index_node, line=token.line)
        return list_access_node, index
        

    elif token.type == "id":
        variable_info = symbol_table.lookup_variable(token.value)
        if isinstance(variable_info, str):
            raise SemanticError(variable_info, token.line)
        is_list = variable_info.get("is_list", False)
        if is_list and tokens[index + 1].type != "[":
            raise SemanticError(f"Semantic Error: List '{token.value}' must be indexed with '[]' in expressions.", token.line)
        
        if isinstance(variable_info, str):
            raise SemanticError(f"Semantic Error: Variable '{token.value}' used before declaration.", token.line)
        
        
        node = ASTNode("Value", token.value)
        index += 1  

        if index < len(tokens) and tokens[index].type in {"++", "--"}:
            op = tokens[index].value
            index += 1
            return UnaryOpNode(op, node, position="post", line=token.line), index

        return node, index


    else:
        error = f"Semantic Error: Cannot use '{token.value}' in this expression."
        raise SemanticError(error, token.line)


def parse_expression_branch(tokens, index):
    """Parses logical expressions with &&/|| operators for branch type."""
    line = tokens[index].line
    left_node, index, left_type = parse_equality(tokens, index)

    
    while tokens[index].type in {"&&", "||"}:
        operator = tokens[index].value
        index += 1
        right_node, index, right_type = parse_equality(tokens, index)
        
        

        left_node = BinaryOpNode(left_node, operator, right_node, line=line)
        left_type = "branch"

    return left_node, index


def parse_equality(tokens, index):
    """Parses equality expressions with == or !=."""
    line = tokens[index].line
    left_node, index, left_type = parse_relational(tokens, index)

    while tokens[index].type in {"==", "!="}:
        operator = tokens[index].type
        index += 1
        right_node, index, right_type = parse_relational(tokens, index)
        

        left_node = BinaryOpNode(left_node, operator, right_node, line=line)

        if operator in {"==", "!="}:
            left_type = "branch"

    return left_node, index, left_type


def parse_relational(tokens, index):
    """Parses relational expressions with <, >, <=, >= or ! unary operator."""
    line = tokens[index].line

    if tokens[index].type == "!":
        index += 1
        operand_node, index, operand_type = parse_relational(tokens, index)
        
        if operand_type != "branch":
            raise SemanticError(f"Semantic Error: ! operator can only apply to 'branch' value.", line)

        return UnaryOpNode("!", operand_node, line=line), index, "branch"

    left_node, index, left_type = parse_operand(tokens, index)

    if tokens[index].type in {"<", "<=", ">", ">="}:
        
        
        operator = tokens[index].type
        index += 1
        right_node, index, right_type = parse_operand(tokens, index)

        

        left_node = BinaryOpNode(left_node, operator, right_node, line=line)

        if operator in {"<", "<=", ">", ">="}:
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
    """Determines the parsing function based on the operand type."""
    token = tokens[index]
    line = token.line

    # Handle parentheses
    if token.type == "(":
        if tokens[index+1].value in {"seed", "tree"}:
            expr_type = tokens[index+1].value
            expr_node, index = parse_expression(tokens, index)
            return expr_node, index, expr_type
        
        elif tokens[index + 1].type == "id":
            var_name = tokens[index +1].value
            var_type = var_name["type"]


            is_lwk, index = check_lwk(tokens, index)
            if not is_lwk:
                expr_node, index = parse_expression(tokens, index)
                index -= 1
                expr_type = "seed"
                
            else:
                index += 1
                expr_node, index = parse_expression_branch(tokens, index)
                expr_type = "branch"

            is_lwk, index = check_lwk(tokens, index)
       
        
        index += 1
        return expr_node, index, expr_type

    # Chungus or Chudeluxe (arithmetic types)
    if token.type in {"intlit", "dbllit"}:
        expr_node, index = parse_expression(tokens, index)
        return expr_node, index, infer_literal_type(token.type)

    # Forsencd (String concatenation or manipulation)
    if token.type in {"chrlit", "stringlit"}:
        expr_node, index = parse_expression(tokens, index)
        return expr_node, index, infer_literal_type(token.type)


    # Lwk (Boolean literal)
    if token.type in {"sunshine", "frost"}:
        expr_node, index = parse_expression(tokens, index)
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

        if not list_info["is_list"]:
            raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", token.line)

        index += 2
        expr_node, index = parse_expression(tokens, index)

        if tokens[index].type != "]":
            raise SemanticError("Syntax Error: Missing closing bracket.", token.line)

        index_node = ASTNode("Index", line=token.line)
        index_node.add_child(expr_node)

        index += 1
        list_access_node = ListAccessNode(list_name, index_node, line=token.line)
        return list_access_node, index, list_info["type"]

    # Chungus or Chudeluxe (arithmetic types)
    if token.type in {"intlit", "dbllit", "-"}:
        expr_node, index = parse_expression(tokens, index)
        return expr_node, index, infer_literal_type(token.type)

    # Forsencd (String concatenation or manipulation)
    if token.type == "chrlit":
        expr_node, index = parse_expression_leaf(tokens, index)
        return expr_node, index, infer_literal_type(token.type)

    # Forsen (String literal)
    if token.type == "stringlit":
        return ASTNode("Value", token.value, line=line), index + 1, "vine"

    # Lwk (Boolean literal)
    if token.type in {"sunshine", "frost"}:
        return ASTNode("Value", token.value, line=line), index + 1, "branch"

    # Identifiers (Variables)
    if token.type == "id":
        var_info = symbol_table.lookup_variable(token.value)
        if isinstance(var_info, str):
            raise SemanticError(f"Semantic Error: Variable '{token.value}' used before declaration.", line)
        
        var_type = var_info["type"]
        is_list = var_info.get("is_list", False)

        if is_list and tokens[index + 1].type != "[":
            raise SemanticError(f"Semantic Error: List '{token.value}' must be indexed with '[]' in expressions.", line)
    
        # Dispatch to specific parsers based on type
        if var_type in {"seed", "tree", "branch"}:
            expr_node, index = parse_expression(tokens, index)
            
            return expr_node, index, var_type

        elif var_type == "leaf":
            expr_node, index = parse_expression_leaf(tokens, index)
            return expr_node, index, var_type

        elif var_type in {"vine", "branch"}:
            return ASTNode("Value", token.value, line=line), index + 1, var_type

        else:
            raise SemanticError(f"Semantic Error: Unsupported type '{var_type}'.", line)

    raise SemanticError(f"Semantic Error: Cannot use '{token.value}' in this expression.", line)


def infer_literal_type(token_type):
    """Returns the type string for a given literal token type."""
    if token_type in {"intlit", "-"}:
        return "seed"
    if token_type == "dbllit":
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
        index += 1
        if tokens[index].type == "(":
            index += 1
            # Allow optional type parameter: water() or water(seed)
            water_type = None
            if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
                water_type = tokens[index].value
                index += 1
            if tokens[index].type != ")":
                raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter (e.g., water(seed)).", line)
            index += 1
            value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=line)
        else:
            raise SemanticError(f"Syntax Error: Expected '()' after water.", line)

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
        expected_type = expected_params[i].children[0].value  # Get expected type

        if expected_type in {"seed", "tree"} and arg_type == "seed":
            continue 
        
        if arg_type != expected_type:
            raise SemanticError(f"Semantic Error: Argument {i+1} of '{func_name}' should be '{expected_type}', but got '{arg_type}'.", line)

    return FunctionCallNode(func_name, args_node.children, line=line), index


def parse_water_statement(tokens, index):
    """Parse water(variable); — reads input into an existing variable."""
    line = tokens[index].line
    index += 1  # skip 'water'

    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after water.", line)
    index += 1  # skip '('

    # Case 1: water() or water(data_type) — no variable target (expression form used as statement)
    if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
        water_type = tokens[index].value
        index += 1
        if tokens[index].type != ")":
            raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter or a variable name.", line)
        index += 1  # skip ')'
        if tokens[index].type != ";":
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        index += 1  # skip ';'
        # Standalone typed water with no target — just returns input (discarded)
        input_node = ASTNode("Input", f"water({water_type})", line=line)
        return input_node, index

    elif tokens[index].type == ")":
        # water() with no args
        index += 1  # skip ')'
        if tokens[index].type != ";":
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        index += 1  # skip ';'
        input_node = ASTNode("Input", "water()", line=line)
        return input_node, index

    elif tokens[index].type == "id":
        # water(variable) — read input into variable
        var_name = tokens[index].value
        var_info = symbol_table.lookup_variable(var_name)
        if isinstance(var_info, str):
            raise SemanticError(var_info, line)
        if var_info.get("is_fertile", False):
            raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-assigned a value.", line)
        var_type = var_info["type"]
        index += 1  # skip identifier

        if tokens[index].type != ")":
            raise SemanticError(f"Semantic Error: water() accepts only a single variable name or type parameter.", line)
        index += 1  # skip ')'
        if tokens[index].type != ";":
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        index += 1  # skip ';'

        # Build as: variable = water(type)  — an assignment with Input as the value
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
                expr_node, index = parse_expression(tokens, index)
                args.append(expr_node)
            elif func_info["return_type"] in {"vine"}:
                expr_node, index = parse_expression_vine(tokens, index)
                args.append(expr_node)
            elif func_info["return_type"] in {"leaf"}:
                expr_node, index = parse_expression_leaf(tokens, index)
                args.append(expr_node)
            elif func_info["return_type"] in {"branch"}:
                expr_node, index = parse_expression_branch(tokens, index)
                args.append(expr_node)
            else:
                raise SemanticError(f"Semantic Error: Function '{func_name}' returns invalid type '{func_info['return_type']}'.", line)


        elif tokens[index].type == "id" and tokens[index + 1].type == "[":
            list_name = token.value
            list_info = symbol_table.lookup_variable(list_name)
            list_type = list_info["type"]
            start_index = index

            if isinstance(list_info, str):
                raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", tokens[index].line)

            if not list_info["is_list"]:
                raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", tokens[index].line)

            index += 2
            expr_node, index = parse_expression(tokens, index)

            if tokens[index].type != "]":
                raise SemanticError("Syntax Error: Missing closing bracket.", tokens[index].line)

            index_node = ASTNode("Index", line=tokens[index].line)
            index_node.add_child(expr_node)

            index += 1
            list_access_node = ListAccessNode(list_name, index_node, line=tokens[index].line)

            if list_type in {"seed", "tree"}:
                expr_node, index = parse_expression(tokens, start_index)
                args.append(expr_node)

            elif list_info["is_list"]:
                args.append(list_access_node)
            

        else:   
            arg_info = symbol_table.lookup_variable(identif_name)
            if isinstance(arg_info, str):
                raise SemanticError(f"Semantic Error: Variable '{identif_name}' used before declaration.", line)
            
            if arg_info["type"] in {"leaf"} and tokens[index + 1].type == "+":
                expr_node, index = parse_string_concatenation(tokens, index)
                args.append(expr_node)
            
            elif arg_info["type"] in {"seed", "tree"}:
                expr_node, index = parse_expression(tokens, index)
                args.append(expr_node)
            else:
                index += 1
                args.append(ASTNode("Value", identif_name, line=line))
                
    elif tokens[index].type in {"intlit", "dbllit"}:
        expr_node, index = parse_expression_branch(tokens, index)
        args.append(expr_node)

    elif tokens[index].type in {"sunshine", "frost", "!"}:
        expr_node, index = parse_expression_branch(tokens, index)
        args.append(expr_node)

    elif tokens[index].type in {"chrlit"}:
        expr_node, index = parse_expression_branch(tokens, index)
        args.append(expr_node)

    elif tokens[index].type in {"("}:
        expr_node, index = parse_expression_branch(tokens, index)
        args.append(expr_node)

    elif tokens[index].type in {"++", "--", "-"}:
        expr_node, index = parse_expression(tokens, index)
        args.append(expr_node)

    else:
        raise SemanticError(f"Semantic Error: Expected valid argument in plant statement.", line)

    actual_args = []
    while tokens[index].type == ",":
        index += 1
        
        if tokens[index].type in {"intlit", "dbllit", "-"}:
            arg_node, index = parse_expression_branch(tokens, index)
            actual_args.append(arg_node)


        elif tokens[index].type == "id" and tokens[index + 1].type == "[":
            print(tokens[index].type)
            start_index = index
            list_name = tokens[index].value
            list_info = symbol_table.lookup_variable(list_name)
            list_type = list_info["type"]
            is_list = list_info["is_list"]
            
            if isinstance(list_info, str):
                raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", tokens[index].line)

            if not list_info["is_list"]:
                raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", tokens[index].line)

            index += 2
            expr_node, index = parse_expression_branch(tokens, index)

            if tokens[index].type != "]":
                raise SemanticError("Syntax Error: Missing closing bracket.", tokens[index].line)

            index_node = ASTNode("Index", line=tokens[index].line)
            index_node.add_child(expr_node)

            index += 1
            list_access_node = ListAccessNode(list_name, index_node, line=tokens[index].line)
            
            if list_type in {"seed", "tree"}:
                arg_node, index = parse_expression(tokens, start_index)
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
                expr_node, index = parse_expression(tokens, index_start)
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
                
            if arg_info["type"] in {"seed", "tree"}:
                arg_node, index = parse_expression_branch(tokens, index)
                actual_args.append(arg_node)
                
            else:
                actual_args.append(ASTNode("Value", arg_name, line=line))
                index += 1
            
        elif tokens[index].type in {"("}:
            arg_node, index = parse_expression_branch(tokens, index)
            actual_args.append(arg_node)

        else:
            raise SemanticError(f"Semantic Error: Expected valid argument after ',' in plant statement.", line)

    if placeholder_count > 15:
        raise SemanticError(f"Semantic Error: Exceeded maximum amount of 15 arguments in plant statement.", line)

    # Only enforce placeholder matching when the format string contains {}
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

    while index < len(tokens) and tokens[index].type == "+":
        index += 1
        if tokens[index].type not in {"stringlit", "id"}:
            raise SemanticError(f"Semantic Error: Only values of type vine can be concatenated in plant().", line)

        if tokens[index].type == "id":
            var_name = tokens[index].value
            var_info = symbol_table.lookup_variable(var_name)
            if isinstance(var_info, str):
                raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)
            if var_info["type"] != "leaf":
                raise SemanticError(f"Semantic Error: Variable '{var_name}' with type {var_info['type']} cannot be concatenated in plant().", line)

        format_string = tokens[index].value
        raw_string = format_string.replace("\\{", "").replace("\\}", "")
        
        if "{" in raw_string or "}" in raw_string:
            if raw_string.count("{") != raw_string.count("}"):
                raise SemanticError(f"Semantic Error: Invalid string literal '{format_string}' in plant().", line)
            if "{}" not in raw_string:
                raise SemanticError(f"Syntax Error: Placeholders {{}} must be adjacent within the string literal.", line)
        
        placeholder_count += raw_string.count("{}")
        right_node = ASTNode("FormattedString", tokens[index].value, line=line)
        index += 1

        left_node = BinaryOpNode(left_node, "+", right_node, line=line)

    return left_node, index, placeholder_count


def parse_fertile(tokens, index):
    token = tokens[index]
    line = token.line
    index += 1
    if tokens[index].value not in {"seed", "tree", "vine", "leaf", "branch", "seed", "tree", "vine", "leaf", "branch"}:
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
        "tree": {"dbllit"},
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
    index += 1  # Move past "spring"

    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after 'spring'.", line)
    index += 1

    condition_expr, index = parse_expression_branch(tokens, index)  # Parse branch expression

    
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


    # Else-if chains: bud (<cond>) { ... }
    while tokens[index].value == "bud":
        index += 1

        if tokens[index].type != "(":
            raise SemanticError(f"Syntax Error: Expected '(' after else-if.", line)
        index += 1  

        elseif_node = ASTNode("ElseIfStatement", line=line)

        elseif_condition_expr, index = parse_expression_branch(tokens, index)

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


    # Else: wither { ... }
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

    elif tokens[index].type == "id":
        identifier = tokens[index].value

        if tokens[index+1].type == "(":  # Function call case
            func_info = symbol_table.lookup_function(identifier)

            if isinstance(func_info, str):  # Function not found
                raise SemanticError(f"Semantic Error: Function '{identifier}' is not defined.", line)

            return_type = func_info["return_type"]
            if return_type != func_type:
                raise SemanticError(f"Semantic Error: Function '{identifier}' returns '{return_type}', but expected '{func_type}'.", line)

            return_expr, index = parse_expression_type(tokens, index, func_type)

        else:  # Variable case
            var_info = symbol_table.lookup_variable(identifier)
            if isinstance(var_info, str):
                raise SemanticError(f"Semantic Error: Variable '{identifier}' used before declaration.", line)

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

    condition, index = parse_expression_branch(tokens, index)

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

                if is_list:
                    if tokens[index + 1].type == "=":
                        node, index = parse_list_assignment(tokens, index)
                        assignments_node.add_child(node)

                    elif tokens[index + 1].type == "[":
                        
                        list_access_node, index = parse_list_access(tokens, index)
                        
                        if tokens[index + 1].type == "=":
                            index += 2 
                            value_node, index = parse_expression(tokens, index)
                            assign_node = AssignmentNode(list_access_node, value_node, line=tokens[index].line)
                            assignments_node.add_child(assign_node)
                        else:
                            raise SyntaxError("Expected '=' after list access", tokens[index + 1].line)


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
                    
                
                else:
                    raise SemanticError(f"Semantic Error: Unexpected token '{tokens[index].value}' in statement.", line)

            elif tokens[index].value in {"++", "--"}:
                operator = tokens[index].value
                index += 1
                if tokens[index].type == "id":
                    var_name = tokens[index].value
                    var_info = symbol_table.lookup_variable(var_name)
                    if var_info["type"] not in {"seed", "tree"}:
                        raise SemanticError(f"Semantic Error: Cannot use '{var_name}' of type {var_info['type']} in expression.", line)
                    
                    if isinstance(var_info, str):
                        raise SemanticError(f"Semantic Error: Variable '{var_name}' used before declaration.", line)

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

    condition, index = parse_expression_branch(tokens, index)

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
        raise SemanticError(f"Syntax Error: Expected '{{' after 'while' condition.", line)
    
    return while_node, index

def parse_do(tokens, index, func_type):
    line = tokens[index].line
    index += 1

    symbol_table.enter_scope()
    context_stack.append("DoWhileNode")

    if tokens[index].type != "{":
        raise SemanticError(f"Syntax Error: Expected '{{' after 'do'.", line)
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

    condition, index = parse_expression_branch(tokens, index)

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

    if tokens[index].type == "id":
        var_info = symbol_table.lookup_variable(tokens[index].value)
        if isinstance(var_info, str):
            raise SemanticError(f"Semantic Error: Variable '{tokens[index].value}' used before declaration.", line)
        var_type = var_info["type"]
        if var_type in {"tree"}:
            raise SemanticError(f"Semantic Error: Variable '{tokens[index].value}' with type '{var_type}' cannot be used in harvest statement.", line)
        switch_expr, index = parse_expression_type(tokens, index, var_type)
        

    elif tokens[index].type in {"intlit", "chrlit", "sunshine", "frost"} or tokens[index].type in {"--", "++", "-", "("}:
        switch_expr, index = parse_expression(tokens, index)

    elif tokens[index].type in {"stringlit"}:
        switch_expr, index = parse_expression_vine(tokens, index)

    elif tokens[index].type in {"chrlit"}:
        switch_expr, index = parse_expression_leaf(tokens, index)

    else:
        raise SemanticError(f"Semantic Error: Invalid token '{tokens[index].value}' used in expression.", line)

    if tokens[index].type != ")":
        raise SemanticError(f"Syntax Error: Expected ')' after 'switch' expression.", line)
    index += 1

    if tokens[index].type != "{":
        raise SemanticError(f"Syntax Error: Expected '{{' after 'switch' expression.", line)
    index += 1
    
    symbol_table.enter_scope()

    case_nodes = []
    default_case = None

    while tokens[index].value in {"variety"}:
        case_line = tokens[index].line
        index += 1
        line = tokens[index].line

        if tokens[index].type not in {"chrlit", "stringlit", "sunshine", "frost", "intlit", "dbllit"}:
            raise SemanticError(f"Semantic Error: Expected valid literal value after 'variety'.", line)
        
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
        raise SemanticError(f"Syntax Error: Expected '}}' after switch statement.", line)
        
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

    expr_node, index = parse_expression(tokens, index)
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

    expr_node, index = parse_expression(tokens, index)
    index_value = ASTNode("Index", line=tokens[index].line)
    index_value.add_child(expr_node)
        
    if tokens[index].type != ")":
        raise SemanticError(f"Syntax Error: Expected ')' after remove argument.", line)
    index += 1

    return RemoveNode(var_name, index_value, line=line), index


def is_inside_loop_or_switch_stack():
    return any(ctx in {"WhileNode", "DoWhileNode", "SwitchNode", "ForNode"} for ctx in context_stack)


def analyze_semantics(tokens):
    """
    Public API for the server.  Runs build_ast() and returns a result dict
    with keys: success, errors, warnings, symbol_table, ast.
    """
    try:
        # Filter out newline tokens — the parser skips them but the
        # semantic AST builder does not expect them.
        filtered = [t for t in tokens if t.type != '\n']
        ast = build_ast(filtered)

        # Serialize the symbol table for JSON transport
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
