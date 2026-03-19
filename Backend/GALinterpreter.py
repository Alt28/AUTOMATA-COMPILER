from GALsemantic import (ProgramNode, VariableDeclarationNode, AssignmentNode, BinaryOpNode, FunctionDeclarationNode, 
                          FunctionCallNode, IfStatementNode, ForLoopNode, WhileLoopNode, PrintNode, UnaryOpNode, 
                          FertileDeclarationNode, ReturnNode,  SwitchNode, ContinueNode, BreakNode, ListNode, TaperNode, 
                          TSNode, AppendNode, InsertNode, RemoveNode, CastNode, ListAccessNode, DoWhileLoopNode,
                          MemberAccessNode, BundleDefinitionNode, ArrayMemberAccessNode)

import threading

# Prefer eventlet's cooperative Event so wait_for_input yields to the
# eventlet hub instead of blocking the entire event loop.
try:
    import eventlet.event as _ev
    _USE_EVENTLET = True
except ImportError:
    _USE_EVENTLET = False

class SemanticError(Exception):
    def __init__(self, message,  line):
        super().__init__(message)
        self.message = f"Ln {line} {message}"

    def __str__(self):
        return self.message

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class InterpreterError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        if line is not None:
            self.message = f"Ln {line} {message}"

        else:
            self.message = message
    
    def __str__(self):
        return self.message

class InterpreterInputRequest(Exception):
    def __init__(self, prompt, line):
        self.prompt = prompt
        self.line = line

class Interpreter:
    def __init__(self, socketio=None):
        self.output = []
        self.loop_stack = []
        self.break_flag = False
        self.continue_flag = False
        self.input_required = False
        self.socketio = socketio
        self.input_events = {}
        self.input_values = {}
        self.current_node = None
        self.current_parent = None

        self.variables = {} 
        self.global_variables = {}
        self.functions = {}
        self.scopes = [{}]
        self.current_func_name = None
        self.function_variables = {}
        self.bundle_types = {}  # Stores bundle (struct) type definitions


    ###### VARIABLE ######
    def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
        scope = self.scopes[-1]
        current_func = self.current_func_name
    

        if name not in self.scopes[-1]:
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
            self.global_variables[name] = self.variables[name]
        


    def lookup_variable(self, name):
        for i, scope in enumerate(reversed(self.scopes)):
            if name in scope:
                return scope[name]
        
        if name in self.variables:
            return self.variables[name]

        return f"Semantic Error: Variable '{name}' used before declaration."
    
    def set_variable(self, name, value):
        for i in reversed(range(len(self.scopes))):
            scope = self.scopes[i]
            if name in scope:
                scope[name]["value"] = value
                return  

        return f"Semantic Error: Variable '{name}' not declared in any scope."


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



    #INTERPRETER
    def interpret(self, node):
        if isinstance(node, ProgramNode):
            return self.eval_program(node)
        elif isinstance(node, BundleDefinitionNode):
            return self.eval_bundle_definition(node)
        elif isinstance(node, MemberAccessNode):
            return self.eval_member_access(node)
        elif isinstance(node, ArrayMemberAccessNode):
            return self.eval_array_member_access(node)
        elif isinstance(node, VariableDeclarationNode):
            return self.eval_variable_declaration(node)
        elif isinstance(node, AssignmentNode):
            return self.eval_assignment(node)
        elif isinstance(node, BinaryOpNode):
            value = self.eval_binary_op(node)
            if isinstance(value, int or float):
                if value > 1000000000000000 or value < -9999999999999999:
                    raise InterpreterError(f"Runtime Error: Evaluated number exceeds maximum number of 16 digits", node.line)
            return value
        elif isinstance(node, FunctionDeclarationNode):
            return self.eval_function_declaration(node)
        elif isinstance(node, PrintNode):
            return self.eval_print(node)
        elif isinstance(node, ListNode):
            return self.eval_list(node)
        elif isinstance(node, ListAccessNode):
            return self.eval_list_access(node)
        elif isinstance(node, ReturnNode):
            return self.eval_return(node)
        elif isinstance(node, FunctionCallNode):
            return self.eval_function_call(node)
        elif isinstance(node, AppendNode):
            return self.eval_append(node)
        elif isinstance(node, InsertNode):
            return self.eval_insert(node)
        elif isinstance(node, RemoveNode):
            return self.eval_remove(node)
        elif isinstance(node, UnaryOpNode):
            return self.eval_unaryop(node)
        elif isinstance(node, FertileDeclarationNode):
            return self.eval_sturdy_declaration(node)
        elif isinstance(node, CastNode):
            return self.eval_cast(node)
        elif isinstance(node, TaperNode):
            return self.eval_taper(node)
        elif isinstance(node, TSNode):
            return self.eval_ts(node)
        elif isinstance(node, IfStatementNode):
            return self.eval_if_statement(node)
        elif isinstance(node, ForLoopNode):
            return self.eval_for_loop(node)
        elif isinstance(node, WhileLoopNode):
            return self.eval_while_loop(node)
        elif isinstance(node, DoWhileLoopNode):
            return self.eval_do_while_loop(node)
        elif isinstance(node, BreakNode):
            return self.eval_break(node)
        elif isinstance(node, ContinueNode):
            return self.eval_continue(node)
        elif isinstance(node, SwitchNode):
            return self.eval_switch(node)
        elif node.node_type == "Input":
            return self.eval_input(node)
        elif node.node_type == "Value":
            value = self._parse_literal(node.value)
            return value
        elif node.node_type == "Identifier":
            var_info = self.lookup_variable(node.value)
            if isinstance(var_info, str):
                raise InterpreterError(var_info, node.line)
            return var_info["value"]
        elif node.node_type == "FormattedString":
            return self.eval_formatted_string(node)
        elif node.node_type == "VariableDeclarationList":
            for child in node.children:
                self.eval_variable_declaration(child)
        elif node.node_type == "AssignmentList":
            for child in node.children:
                if isinstance(child, AssignmentNode):
                    self.eval_assignment(child)
                elif isinstance(child, UnaryOpNode):
                    self.eval_unaryop(child)
        elif node.node_type == "List":
            return [self.interpret(child) for child in node.children]
        elif node.node_type == "Block":
            self.eval_block(node)
        else:
            raise Exception(f"Unknown AST node type: {node.node_type}")

    def eval_program(self, node):
        for child in node.children:
            self.interpret(child)

        main_call = FunctionCallNode("root", [], node.line)
        return self.interpret(main_call)

    def eval_variable_declaration(self, node):
        var_type = node.children[0].value
        var_name = node.children[1].value
        value_node = node.children[2] if len(node.children) > 2 else None
        is_list = False
        
        # Default values for uninitialized variables
        default_values = {
            "seed": 0,
            "tree": 0.0,
            "leaf": '',
            "vine": "",
            "branch": False,
        }

        if value_node:
            if value_node.node_type == "List":
                value = []
                if var_type in self.bundle_types:
                    # Bundle array: initialize list of dicts with default member values (recursive for nested)
                    for _ in value_node.children:
                        value.append(self._build_bundle_defaults(var_type))
                else:
                    for val in value_node.children:
                        item = self.interpret(val)
                        if var_type == "seed":
                            if isinstance(item, float):
                                item = int(item)
                        elif var_type == "tree":
                            item = float(item)
                        value.append(item)
                
                is_list = True

            else:
                value = self.interpret(value_node)

                if isinstance(value_node, TaperNode):
                    is_list = True
                if var_type == "seed" and isinstance(value, float):
                    value = int(value)

                if var_type in {"tree", "seed"}:
                    if not isinstance(value, (int, float)):
                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)
                    
                    if isinstance(value, bool):
                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)


                    if var_type == "tree" and isinstance(value, int):
                        value = float(value)
                
                if var_type == "leaf":
                    if not isinstance(value, str):
                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)

                if var_type == "vine":
                    if not isinstance(value, str):
                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)

                if var_type == "branch":
                    if isinstance(value, int) or isinstance(value, float):
                        if value == 0:
                            value = False
                        else:
                            value = True
        else:
            # Uninitialized variable — use default value for the type
            if var_type in self.bundle_types:
                # Bundle variable: initialize with dict of default member values (recursive for nested)
                value = self._build_bundle_defaults(var_type)
            else:
                value = default_values.get(var_type, None)
                    
        #print(f"\nDeclaring variable '{var_name}' of type '{var_type}' with initial value: {value}")
        self.declare_variable(var_name, var_type, value, is_list=is_list)

    def eval_bundle_definition(self, node):
        """Store bundle type definition for later use."""
        self.bundle_types[node.bundle_name] = node.members

    def _build_bundle_defaults(self, bundle_type_name):
        """Recursively build default values for a bundle type, including nested bundles."""
        _member_defaults = {"seed": 0, "tree": 0.0, "leaf": '', "vine": "", "branch": False}
        members = self.bundle_types[bundle_type_name]
        result = {}
        for name, typ in members.items():
            if typ in self.bundle_types:
                result[name] = self._build_bundle_defaults(typ)
            else:
                result[name] = _member_defaults.get(typ, None)
        return result

    def eval_member_access(self, node):
        """Read a bundle member value: p.age or p.addr.zip (nested)"""
        obj_child = node.children[0]
        member_name = node.children[1].value

        if obj_child.node_type == "MemberAccess":
            # Nested: evaluate inner member access first
            bundle_value = self.eval_member_access(obj_child)
        elif obj_child.node_type == "ArrayMemberAccess":
            # Chained after array member: p[0].addr.zip
            bundle_value = self.eval_array_member_access(obj_child)
        else:
            # Simple: obj_child is ASTNode("Object", var_name)
            obj_name = obj_child.value
            var_info = self.lookup_variable(obj_name)
            if isinstance(var_info, str):
                raise InterpreterError(var_info, node.line)
            bundle_value = var_info["value"]

        if not isinstance(bundle_value, dict):
            raise InterpreterError(f"Runtime Error: Value is not a bundle.", node.line)
        if member_name not in bundle_value:
            raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)
        return bundle_value[member_name]

    def eval_array_member_access(self, node):
        """Read a bundle array element member value: p[0].x"""
        list_access_node = node.children[0]
        member_name = node.children[1].value
        bundle_element = self.eval_list_access(list_access_node)
        if not isinstance(bundle_element, dict):
            raise InterpreterError(f"Runtime Error: Array element is not a bundle.", node.line)
        if member_name not in bundle_element:
            raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)
        return bundle_element[member_name]

    def eval_sturdy_declaration(self, node):
        var_type = node.children[0].value
        var_name = node.children[1].value
        value_node = node.children[2]
        value = self.interpret(value_node)
        self.declare_variable(var_name, var_type, value, is_list=False,  is_fertile=True)

    def eval_assignment(self, node):
        target_node = node.children[0]
        value_node = node.children[1]

        if value_node.node_type == "List":
            value = []
            for val in value_node.children:
                item = self.interpret(val)
                value.append(item)
        else:
            value = self.interpret(value_node)
            if isinstance(value_node, AppendNode) or isinstance(value_node, InsertNode) or isinstance(value_node, RemoveNode):
                return

        if target_node.node_type == "ListAccess":
            # Collect all index nodes from outermost to innermost
            indices = []
            current = target_node
            while hasattr(current, 'node_type') and current.node_type == "ListAccess":
                idx = self.interpret(current.children[1].children[0])
                if not isinstance(idx, int):
                    raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{idx}'", node.line)
                indices.append(idx)
                # children[0] is ASTNode("ListName", name_or_node)
                current = current.children[0].value

            # current is now the base variable name (string)
            list_name = current
            list_entry = self.lookup_variable(list_name)
            if isinstance(list_entry, str):
                raise InterpreterError(list_entry, node.line)

            list_value = list_entry["value"]
            if not isinstance(list_value, list):
                raise InterpreterError(f"Runtime Error: Variable '{list_name}' is not a list.", node.line)

            # indices were collected outermost-first, reverse to get innermost-first
            indices.reverse()

            # Navigate to the correct nested list
            target = list_value
            for i, idx in enumerate(indices[:-1]):
                if idx < 0 or idx >= len(target):
                    raise InterpreterError(f"Runtime Error: Index '{idx}' out of bounds for list '{list_name}'.", node.line)
                target = target[idx]
                if not isinstance(target, list):
                    raise InterpreterError(f"Runtime Error: Cannot index into a non-list value.", node.line)

            final_idx = indices[-1]
            if final_idx < 0 or final_idx >= len(target):
                raise InterpreterError(f"Runtime Error: Index '{final_idx}' out of bounds for list '{list_name}'.", node.line)

            target[final_idx] = value

        elif target_node.node_type == "MemberAccess":
            # Bundle member assignment: p.age = 19 or p.addr.zip = 1000
            # Collect the chain of member names from outermost to innermost
            chain = []
            current = target_node
            while hasattr(current, 'node_type') and current.node_type == "MemberAccess":
                chain.append(current.children[1].value)  # member name
                current = current.children[0]  # go deeper

            chain.reverse()  # now ordered from root to leaf

            # current is now ASTNode("Object", var_name) or an ArrayMemberAccessNode
            if hasattr(current, 'node_type') and current.node_type == "ArrayMemberAccess":
                # Chained off array member: p[0].addr.zip = 1000
                bundle_value = self.interpret(current)
                if not isinstance(bundle_value, dict):
                    raise InterpreterError(f"Runtime Error: Value is not a bundle.", node.line)
            else:
                obj_name = current.value
                var_info = self.lookup_variable(obj_name)
                if isinstance(var_info, str):
                    raise InterpreterError(var_info, node.line)
                bundle_value = var_info["value"]
                if not isinstance(bundle_value, dict):
                    raise InterpreterError(f"Runtime Error: Variable '{obj_name}' is not a bundle.", node.line)

            # Navigate to the parent dict (all but last member)
            for member in chain[:-1]:
                if member not in bundle_value:
                    raise InterpreterError(f"Runtime Error: Bundle has no member '{member}'.", node.line)
                bundle_value = bundle_value[member]
                if not isinstance(bundle_value, dict):
                    raise InterpreterError(f"Runtime Error: Member '{member}' is not a bundle.", node.line)

            final_member = chain[-1]
            if final_member not in bundle_value:
                raise InterpreterError(f"Runtime Error: Bundle has no member '{final_member}'.", node.line)

            # Type coercion: find the final member's declared type
            type_chain_current = current
            if hasattr(type_chain_current, 'node_type') and type_chain_current.node_type == "ArrayMemberAccess":
                # For array member chains, walk up to find the variable's bundle type
                la_node = type_chain_current.children[0]
                while hasattr(la_node, 'node_type') and la_node.node_type == "ListAccess":
                    la_node = la_node.children[0].value
                var_type = self.lookup_variable(la_node)["type"] if not isinstance(self.lookup_variable(la_node), str) else None
            else:
                obj_name = type_chain_current.value
                var_info = self.lookup_variable(obj_name)
                var_type = var_info["type"] if not isinstance(var_info, str) else None

            if var_type and var_type in self.bundle_types:
                # Walk through the type definitions to find the final member type
                cur_type = var_type
                for member in chain:
                    if cur_type in self.bundle_types:
                        cur_type = self.bundle_types[cur_type].get(member, cur_type)
                if cur_type == "seed" and isinstance(value, float):
                    value = int(value)
                elif cur_type == "tree" and isinstance(value, int):
                    value = float(value)
                elif cur_type == "branch" and isinstance(value, int):
                    value = True if value != 0 else False

            bundle_value[final_member] = value

        elif target_node.node_type == "ArrayMemberAccess":
            # Bundle array member assignment: p[0].x = 1
            list_access_node = target_node.children[0]
            member_name = target_node.children[1].value
            bundle_element = self.eval_list_access(list_access_node)
            if not isinstance(bundle_element, dict):
                raise InterpreterError(f"Runtime Error: Array element is not a bundle.", node.line)
            if member_name not in bundle_element:
                raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)

            # Type coercion for the member
            current = list_access_node
            while hasattr(current, 'node_type') and current.node_type == "ListAccess":
                current = current.children[0].value
            var_name = current
            var_info = self.lookup_variable(var_name)
            if not isinstance(var_info, str) and var_info["type"] in self.bundle_types:
                member_type = self.bundle_types[var_info["type"]].get(member_name)
                if member_type == "seed" and isinstance(value, float):
                    value = int(value)
                elif member_type == "tree" and isinstance(value, int):
                    value = float(value)
                elif member_type == "branch" and isinstance(value, int):
                    value = True if value != 0 else False

            bundle_element[member_name] = value

        else:
            var_name = target_node.value
            var_info = self.lookup_variable(var_name)
            if isinstance(var_info, str):
                raise InterpreterError(var_info, node.line)

            var_type = var_info["type"]
            if var_type == "seed" and isinstance(value, float):
                value = int(value)
            
            if var_type == "tree" and isinstance(value, int):
                value = float(value)

            if var_type == "branch" and isinstance(value, int):
                value = True if value != 0 else False

            self.set_variable(var_name, value)
            #print(f"\nUpdating variable '{var_name}' of type '{var_type}' with value: {value}")


    def eval_binary_op(self, node):
        left = self.interpret(node.children[0])
        right = self.interpret(node.children[1])
        operator = node.value

        # Handle string concatenation with ` before _parse_literal
        # to preserve whitespace-only vine values like " "
        if operator == '`':
            result = str(left) + str(right)
            return result

        left = self._parse_literal(left)
        right = self._parse_literal(right)

        if operator == '+' and (isinstance(left, str) or isinstance(right, str)):
            result = str(left) + str(right)
            return result

        try:
            if operator == '+':
                if not isinstance(left, float or int) and not isinstance(right, float or int):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        left = 1 if left != "" else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                return left + right
            
            elif operator == '-':
                if not isinstance(left, float or int) and not isinstance(right, float or int):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        left = 1 if left != "" else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                    
                return left - right
            elif operator == '*':
                if not isinstance(left, float or int) and not isinstance(right, float or int):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        left = 1 if left != "" else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                return left * right
            elif operator == '/':
                if not isinstance(left, float or int) and not isinstance(right, float or int):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        left = 1 if left != "" else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                if right == 0:
                    raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)
                return left / right
            elif operator == '%':
                if not isinstance(left, float or int) and not isinstance(right, float or int):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        left = 1 if left != "" else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                if right == 0:
                    raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)
                return left % right
            elif operator == '==':
                return left == right
            elif operator == '!=':
                return left != right
            elif operator == '<':
                if isinstance(left, str):
                    print(left)
                    left = 0 if left == "" else 1
                    print(left)
                if isinstance(right, str):
                    right = 0 if right == "" else 1
                return left < right
            elif operator == '<=':
                if isinstance(left, str):
                    print(left)
                    left = 0 if left == "" else 1
                    print(left)
                if isinstance(right, str):
                    right = 0 if right == "" else 1
                return left <= right
            elif operator == '>':
                if isinstance(left, str):
                    print(left)
                    left = 0 if left == "" else 1
                    print(left)
                if isinstance(right, str):
                    right = 0 if right == "" else 1
                return left > right
            
            elif operator == '>=':
                if isinstance(left, str):
                    print(left)
                    left = 0 if left == "" else 1
                    print(left)
                if isinstance(right, str):
                    right = 0 if right == "" else 1
                return left >= right
            elif operator == '&&':
                if isinstance(left, int) or isinstance(left, float):
                    if left == 0:
                        left = False
                    else:
                        left = True
                elif isinstance(right, int) or isinstance(right, float):
                    if right == 0:
                        right = False
                    else:
                        right = True
                elif isinstance(left, str):
                    left = False if left == "" else True
                elif isinstance(right, str):
                    right = False if right == "" else True

                elif isinstance(left, str) or isinstance(right, str):
                    left = bool(left)
                elif isinstance(left, str) or isinstance(right, str):
                    right = bool(right)

                return bool(left) and bool(right)
            elif operator == '||':
                if isinstance(left, int) or isinstance(left, float):
                    if left == 0:
                        left = False
                    else:
                        left = True
                elif isinstance(right, int) or isinstance(right, float):
                    if right == 0:
                        right = False
                    else:
                        right = True

                elif isinstance(left, str) or isinstance(right, str):
                    left = bool(left)
                elif isinstance(left, str) or isinstance(right, str):
                    right = bool(right)

                return bool(left) or bool(right)
            elif operator == '!':
                return not bool(left)
            elif operator == 'neg':
                return -left
            else:
                raise Exception(f"Unknown operator: {operator}")
        
        except ZeroDivisionError:
            raise InterpreterError("Runtime Error: Division by zero", "")

    def _parse_literal(self, value):

        if isinstance(value, str) and not isinstance(self.lookup_variable(value), str):
            return self.lookup_variable(value)["value"]

        if isinstance(value, (int, float, bool)):
            return value

        if not isinstance(value, str):
            return value

        value = value.strip()

        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]

        if value in ('true', 'sunshine'):
            return True
        if value in ('false', 'frost'):
            return False

        # Handle GAL negative literals: ~20 → -20, ~3.14 → -3.14
        parse_value = value
        if parse_value.startswith('~'):
            parse_value = '-' + parse_value[1:]

        try:
            if '.' in parse_value:
                return float(parse_value)
            return int(parse_value)
        except ValueError:
            return value 
    

    def eval_function_declaration(self, node):
        return_type = node.children[0].value 
        parameters_node = node.children[1]
        func_name = node.value

        params = []
        if parameters_node and len(parameters_node.children) > 0:
            for param in parameters_node.children:
                if not hasattr(param, 'node_type') or param.node_type != 'Parameter':
                    raise Exception(f"Invalid parameter: {param.value}")
                param_type = param.children[0].value
                param_name = param.children[1].value
                params.append({"name": param_name, "type": param_type})

        self.declare_function(func_name, return_type, params, node)

        return None

    def eval_block(self, block_node):
        for statement in block_node.children:
            self.interpret(statement) 
            if self.break_triggered():
                return
            if self.continue_flag:
                return
            
            
    def plant(self, value):
        """GAL output primitive."""
        self.socketio.emit('output', {'output': str(value)})

    # Backward-compatible alias
    def plant_out(self, num):
        self.socketio.emit('output', {'output': str(num)})
        self.output.append(str(num))

    def eval_print(self, node):
        if not node.children:
            return

        first = node.children[0]

        evaluated_first = self.interpret(first)
        if isinstance(evaluated_first, float):
            whole, dot, dec = str(evaluated_first).partition('.')
            dec = dec[:5]
            evaluated_first = float(f"{whole}.{dec}")

        if isinstance(evaluated_first, str) and '{}' in evaluated_first:
            values = []
            for arg in node.children[1:]:
                value = self.interpret(arg)
                if isinstance(value, str) and not isinstance(self.lookup_variable(value), str):
                    value = self.lookup_variable(value)["value"]
                
                if isinstance(value, float):
                    whole, dot, dec = str(value).partition('.')
                    dec = dec[:5]
                    value = float(f"{whole}.{dec}")

                values.append(value)

            try:
                output_str = evaluated_first.format(*values)
            except Exception as e:
                raise Exception(f"Format error in plant(): '{evaluated_first}' with {values}: {e}")

            self.plant(output_str)
            return

        # No {} placeholders — print all arguments separated by spaces (C-style)
        if len(node.children) > 1:
            parts = [str(evaluated_first)]
            for arg in node.children[1:]:
                value = self.interpret(arg)
                if isinstance(value, float):
                    whole, dot, dec = str(value).partition('.')
                    dec = dec[:5]
                    value = float(f"{whole}.{dec}")
                parts.append(str(value))
            self.plant(" ".join(parts))
            return

        self.plant(str(evaluated_first))

    def eval_formatted_string(self, node):
        value = node.value
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        
        # Escape sequences
        value = value.replace(r'\\', '\\')
        value = value.replace(r'\n', '\n')
        value = value.replace(r'\t', '\t')
        value = value.replace(r'\"', '"')
        value = value.replace(r'\{', '{')
        value = value.replace(r'\}', '}')
        value = value.replace(r'\/', '/')
        return value

        
    def eval_list_access(self, node):
        # children[0] is ASTNode("ListName", list_name) where list_name is a string or ListAccessNode
        name_or_node = node.children[0].value
        if hasattr(name_or_node, 'node_type') and name_or_node.node_type == "ListAccess":
            list_value = self.eval_list_access(name_or_node)
            display_name = "nested list"
        else:
            list_name = name_or_node
            list_entry = self.lookup_variable(list_name)
            list_value = list_entry["value"]
            display_name = list_name

        index_node = node.children[1]
        index = self.interpret(index_node.children[0])

        if not isinstance(index, int):
            raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{index}'", node.line)
        
        if not isinstance(list_value, list):
            raise InterpreterError(f"Runtime Error: Cannot index into a non-list value.", node.line)

        if index < 0 or index >= len(list_value):
            raise InterpreterError(f"Runtime Error: Index '{index}' out of bounds for list '{display_name}'.", node.line)

        return list_value[index]
    

    def eval_return(self, node):
        value = self.interpret(node.children[0]) if node.children else None
        raise ReturnValue(value)
    

    def eval_function_call(self, node):
        function_name = node.value
        args = [self.interpret(arg.children[0]) for arg in node.children]

        func_info = self.lookup_function(function_name)
        if isinstance(func_info, str):
            raise InterpreterError(func_info, node.line)

        expected_params = func_info["params"]
        function_node = func_info["node"]

        if len(expected_params) != len(args):
            raise InterpreterError(
                f"Runtime Error: Function '{function_name}' expects {len(expected_params)} argument(s), got {len(args)}.",
                node.line
            )
        
        self.enter_scope()
        
        try:
            for i, param in enumerate(expected_params):
                param_name = param["name"]
                param_type = param["type"]
                arg_value = args[i]
                #print(f"\n[CALL] In function: {function_name} — Argument '{param_name}' of type '{param_type}' with value: {arg_value}")
                self.declare_variable(param_name, param_type, arg_value)

            try:
                self.eval_block(function_node.children[2])

            except ReturnValue as ret:
                return ret.value

            return None

        finally:
            self.exit_scope()
            self.current_func_name = None


    def eval_append(self, node):
        list_name = node.parent.children[0].value
        list_info = self.lookup_variable(list_name)

        for child in node.children:
            value = self.interpret(child)
            list_info["value"].append(value)
            #print(f"\nAppending value '{value}' to list '{list_name}'")

        
    def eval_insert(self, node):
        list_name = node.parent.children[0].value
        list_info = self.lookup_variable(list_name)

        index = self.interpret(node.children[0].children[0])

        if not isinstance(index, int):
            raise InterpreterError("Runtime Error: Insert index must be an integer", node.line)

        if index < 0 or index > len(list_info["value"]):
            raise InterpreterError(f"Runtime Error: Index {index} out of range for insert", node.line)

        for child in node.children[1:]:
            value = self.interpret(child)
            list_info["value"].insert(index, value)
            index += 1
            #print(f"Inserted {value} at index {index} in list '{list_name}': {list_info['value']}")


    def eval_remove(self, node):
        list_name = node.children[0].value
        index_node = node.children[1].children[0]

        list_info = self.lookup_variable(list_name)
        if isinstance(list_info, str):
            raise InterpreterError(list_info, node.line)

        index = self.interpret(index_node)

        if not isinstance(index, int):
            raise InterpreterError("Runtime Error: Remove index must be an integer", node.line)

        if index < 0 or index >= len(list_info["value"]):
            raise InterpreterError(f"Runtime Error: Index {index} out of bounds for remove", node.line)

        removed = list_info["value"].pop(index)
        #print(f"Removed value {removed} from list '{list_name}': {list_info['value']}")

    def eval_unaryop(self, node):
        if not isinstance(node.children[0], ListAccessNode):
            operand_node = node.children[0]
            operand_name = operand_node.value
            var_info = self.lookup_variable(operand_name)

            if node.value == "++":
                if isinstance(var_info, str):
                    raise InterpreterError(var_info, node.line)
                if node.position == "pre":
                    var_info["value"] += 1
                    return var_info["value"]
                else:  # post
                    original = var_info["value"]
                    var_info["value"] += 1
                    return original

            elif node.value == "--":
                if isinstance(var_info, str):
                    raise InterpreterError(var_info, node.line)
                if node.position == "pre":
                    var_info["value"] -= 1
                    return var_info["value"]
                else:  # post
                    original = var_info["value"]
                    var_info["value"] -= 1
                    return original
            
            elif node.value == "-":
                value = self.interpret(operand_node)
                return -value

            elif node.value == "~":
                value = self.interpret(operand_node)
                return -value

            elif node.value == "!":
                value = self.interpret(operand_node)
                return not value
            
        else:
            operand_node = node.children[0]
            list_name = operand_node.children[0].value
            index_node = operand_node.children[1]
            index = self.interpret(index_node.children[0])

            list_entry = self.lookup_variable(list_name)
            if isinstance(list_entry, str):
                raise InterpreterError(list_entry, node.line)

            list_value = list_entry["value"]

            if not isinstance(index, int):
                raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{index}'", node.line)

            if not isinstance(list_value, list):
                raise InterpreterError(f"Runtime Error: Variable '{list_name}' is not a list.", node.line)

            if index < 0 or index >= len(list_value):
                raise InterpreterError(f"Runtime Error: Index '{index}' out of bounds for list '{list_name}'.", node.line)

            if node.value == "++":
                original = list_value[index]
                list_value[index] += 1
                return original if node.position == "post" else list_value[index]

            elif node.value == "--":
                original = list_value[index]
                list_value[index] -= 1
                return original if node.position == "post" else list_value[index]

        
            

        raise InterpreterError(f"Unknown unary operator {node.value}", node.line)
    
    def eval_cast(self, node):
        value = self.interpret(node.children[1])
        cast_type = node.children[0].value

        if cast_type == "seed":
            return int(value)
        elif cast_type == "tree":
            return float(value)
        elif cast_type == "leaf":
            if isinstance(value, int):
                return chr(value)
            return str(value)[0] if value else '\0'
        elif cast_type == "branch":
            return bool(value)
        elif cast_type == "vine":
            return str(value)
        else:
            raise InterpreterError(f"Unknown cast type: {cast_type}", node.line)

    def eval_taper(self, node):
        var_name = node.children[0].value
        var_info = self.lookup_variable(var_name)
        
        if var_info["type"] == "leaf":
            value = list(var_info["value"])
            #print(f"Tapered string '{var_name}' into list: {var_info['value']}")

        return value

    def eval_ts(self, node):
        var_name = node.children[0].value
        var_info = self.lookup_variable(var_name)

        if var_info["is_list"]:
            result = len(var_info["value"])
            #print(f"Tapered list '{var_name}' to its length: {result}")
        
        elif var_info["type"] == "leaf":
            result = len(var_info["value"])
            #print(f"Tapered string '{var_name}' to its length: {result}")
        
        return result

    def eval_if_statement(self, node):
        condition_result = self.interpret(node.children[0].children[0])
        self.enter_scope()


        
        try:
            if condition_result:
                self.eval_block(node.children[1])
            
            else:
                current_node = 2
                while current_node < len(node.children):
                    
                    elif_node = node.children[current_node]

                    if elif_node.node_type == "ElseIfStatement":
                        elif_condition_result = self.interpret(elif_node.children[0].children[0])

                        if not isinstance(elif_condition_result, bool):
                            raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)
                        
                        if elif_condition_result:
                            try:
                                self.enter_scope()
                                #print(f"Executing ElseIf block: {elif_node.line}")
                                self.eval_block(elif_node.children[1])
                            finally:
                                self.exit_scope()
                            return
                        
                    elif elif_node.node_type == "ElseStatement":
                        #print(f"Executing Else block: {elif_node.line}")
                        try:
                            self.enter_scope()
                            self.eval_block(elif_node.children[0])
                        finally:
                            self.exit_scope()
                        return

                    current_node += 1
        finally:
            self.exit_scope()

        return None
    
    def eval_for_loop(self, node):
        self.enter_loop('for')
        self.enter_scope()
        MAX_LOOP_ITERATIONS = 10000
        LOOP_COUNTER = 0

        try:
            instantiate_node = node.children[0]

            if isinstance(instantiate_node, VariableDeclarationNode):
                var_type = instantiate_node.children[0].value
                var_name = instantiate_node.children[1].value
                initial_value_node = self.interpret(instantiate_node.children[2])
                self.declare_variable(var_name, var_type, initial_value_node)

            elif isinstance(instantiate_node, AssignmentNode):
                var_name = instantiate_node.children[0].value
                initial_value_node = self.interpret(instantiate_node.children[1])
                self.lookup_variable(var_name)["value"] = initial_value_node

            condition_node = node.children[1].children[0]
            condition_result = self.interpret(condition_node)

            if not isinstance(condition_result, bool):
                raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)

            while condition_result:
                LOOP_COUNTER += 1
                if LOOP_COUNTER > MAX_LOOP_ITERATIONS:
                    raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)

                
                self.eval_block(node.children[3])

                if self.continue_flag:
                    self.continue_flag = False  

                if self.break_triggered():
                    break
                
                for update_expr in node.children[2].children:
                    self.interpret(update_expr)

                condition_result = self.interpret(condition_node)

        finally:
            self.exit_scope()
            self.exit_loop()


    def eval_while_loop(self, node):
        self.enter_loop('while')
        self.enter_scope()
        MAX_LOOP_ITERATIONS = 10000
        LOOP_COUNTER = 0
        condition_node = node.children[0].children[0]

        try:
            condition_result = self.interpret(condition_node)

            if not isinstance(condition_result, bool):
                raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)

            while condition_result:
                LOOP_COUNTER += 1
                if LOOP_COUNTER > MAX_LOOP_ITERATIONS:
                    raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)

                block_node = node.children[1]
                self.eval_block(block_node)

                if self.continue_flag:
                    self.continue_flag = False

                if self.break_triggered():
                    break

                condition_result = self.interpret(condition_node)

        finally:
            self.exit_loop()
            self.exit_scope()


    def eval_do_while_loop(self, node):
        self.enter_loop('do-while')
        MAX_LOOP_ITERATIONS = 10000
        LOOP_COUNTER = 0
        condition_node = node.children[1].children[0]
        block_node = node.children[0]

        try:
            while True:
                self.eval_block(block_node)
                LOOP_COUNTER += 1
                if LOOP_COUNTER > MAX_LOOP_ITERATIONS:
                    raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)

                if self.continue_flag:
                    self.continue_flag = False

                if self.break_triggered():
                    break

                condition_result = self.interpret(condition_node)

                if not isinstance(condition_result, bool):
                    raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)

                if not condition_result:
                    break
        finally:
            self.exit_loop()

    
    def eval_break(self, node):
        if self.loop_stack:
            self.trigger_break()
        else:
            raise InterpreterError("Runtime Error: Break statement used outside of a loop", node.line)
        
    def trigger_break(self):
        self.break_flag = True

    def break_triggered(self):
        return self.break_flag

    def enter_loop(self, loop_type):
        self.loop_stack.append(loop_type)
        self.break_flag = False
        self.continue_flag = False

    def exit_loop(self):
        if self.loop_stack:
            self.loop_stack.pop()
            self.break_flag = False
            self.continue_flag = False

    def eval_continue(self, node):
        if self.loop_stack:
            self.trigger_continue()
        else:
            raise InterpreterError("Runtime Error: Continue statement used outside of a loop", node.line)
        
    def continue_triggered(self):
        return self.continue_flag
    
    def trigger_continue(self):
        self.continue_flag = True

    def eval_switch(self, node):
        self.enter_loop('switch')
        self.enter_scope()
        switch_expr_node = node.children[0]
        switch_value = self.interpret(switch_expr_node)

        matched_case = False
        break_found = False
        default_case = None

        try:
            for case_node in node.children[1:]:
                label_type = case_node.node_type
                if label_type == "Case":
                    case_value_node = case_node.children[0]
                    block_node = case_node.children[1]
                    case_value = self.interpret(case_value_node)

                    if switch_value == case_value or matched_case:
                        matched_case = True
                        try:
                            self.enter_scope()
                            self.eval_block(block_node)
                            if self.break_triggered():
                                break_found = True
                                break
                        finally:
                            self.exit_scope()
                    
                elif label_type == "Default":
                    default_case = case_node.children[0]
            
            if not matched_case and not break_found and default_case:
                try:
                    self.enter_scope()
                    self.eval_block(default_case)
                finally:
                    self.exit_scope()

        finally:
            self.exit_loop()
            self.exit_scope()


    def emit_input_request(self, var_name, prompt):
        self.socketio.emit('input_required', {'prompt': prompt, 'variable': var_name})

    # Method to capture input from the client
    def provide_input(self, var_name, input_value):
        evt = self.input_events.get(var_name)
        if evt is None:
            # No waiter yet — stash the value for later
            self.input_values[var_name] = input_value
            return
        if _USE_EVENTLET:
            # eventlet.event.Event.send() unblocks the waiting greenlet
            evt.send(input_value)
        else:
            self.input_values[var_name] = input_value
            evt.set()

    # Method to wait for input asynchronously
    def wait_for_input(self, var_name):
        # Check if input was already stashed (provide_input called first)
        if var_name in self.input_values:
            return self.input_values.pop(var_name)

        if _USE_EVENTLET:
            evt = _ev.Event()
            self.input_events[var_name] = evt
            value = evt.wait()          # cooperative yield
            self.input_events.pop(var_name, None)
            return value
        else:
            event = threading.Event()
            self.input_events[var_name] = event
            event.wait()
            value = self.input_values.pop(var_name, None)
            self.input_events.pop(var_name, None)
            return value

    # Modify the eval_input method to use the new input handling
    def eval_input(self, node):
        parent_node = node.parent
        if isinstance(parent_node, VariableDeclarationNode):
            var_name = parent_node.children[1].value
            var_type = parent_node.children[0].value
        
        elif isinstance(parent_node, AssignmentNode):
            target = parent_node.children[0]
            if isinstance(target, ListAccessNode):
                # water(arr[i]) — target is a list access node
                # Walk down to find the base list name
                current = target
                while hasattr(current, 'node_type') and current.node_type == "ListAccess":
                    current = current.children[0].value
                var_name = current if isinstance(current, str) else str(current)
                var_type = self.lookup_variable(var_name)["type"]
            else:
                var_name = target.value
                var_type = self.lookup_variable(var_name)["type"]

        else:
            # Standalone water() / water(type) — extract type from node value
            var_name = "_input"
            if node.value and "(" in node.value:
                inner = node.value.split("(")[1].rstrip(")")
                var_type = inner if inner in {"seed", "tree", "leaf", "branch", "vine"} else "vine"
            else:
                var_type = "vine"

        prompt = f"Input for {var_name}: "  # Create a prompt message for the input
        self.input_required = True


        # Emit the input request to the client
        self.emit_input_request(var_name, prompt)

        # Wait for the input asynchronously
        input_value = self.wait_for_input(var_name)


        self.input_required = False  # Reset the input flag

        if var_type == "seed":
            try:
                if len(input_value.strip('-').lstrip('0')) > 16:
                    raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
                input_value = int(float(input_value))
            except ValueError:
                raise InterpreterError(f"Runtime Error: Expected integer value, got '{input_value}'", node.line)
            
        elif var_type == "tree":
            try:
                if '.' in input_value:
                    integer_part, decimal_part = str(input_value).split('.')
                    if len(integer_part.strip('-').lstrip('0')) > 16:
                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
                    if len(decimal_part.rstrip('0')) > 5:
                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 5 decimal numbers", node.line)
                    
                else:
                    if len(input_value.strip('-').lstrip('0')) > 16:
                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
                
                input_value = float(input_value)
                
                
            except ValueError:
                raise InterpreterError(f"Runtime Error: Expected float value, got '{input_value}'", node.line)
            
        elif var_type == "branch":
            if input_value == "true":
                input_value = True
            elif input_value == "false":
                input_value = False
            else:
                raise InterpreterError(f"Runtime Error: expected branch value, got '{input_value}'", node.line)
            
        elif var_type == "leaf":
            if len(input_value) != 1:
                raise InterpreterError(f"Runtime Error: Expected a single character for leaf, got '{input_value}'", node.line)
            input_value = str(input_value)

        elif var_type == "vine":
            input_value = str(input_value)

        return input_value


