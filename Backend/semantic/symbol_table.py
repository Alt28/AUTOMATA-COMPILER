

# AUTO: Defines class `SymbolTable`.
class SymbolTable:
    # AUTO: Defines function `__init__`.
    def __init__(self):
        # AUTO: Sets `self.variables`.
        self.variables = {}
        # AUTO: Sets `self.global_variables`.
        self.global_variables = {}
        # AUTO: Sets `self.functions`.
        self.functions = {}
        # AUTO: Sets `self.scopes`.
        self.scopes = [{}]
        # AUTO: Sets `self.current_func_name`.
        self.current_func_name = None
        # AUTO: Sets `self.function_variables`.
        self.function_variables = {}
        # AUTO: Sets `self.bundle_types`.
        self.bundle_types = {}

    # AUTO: Defines function `declare_variable`.
    def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
        # AUTO: Sets `scope`.
        scope = self.scopes[-1]
        # AUTO: Sets `current_func`.
        current_func = self.current_func_name
    

        # AUTO: Checks this condition.
        if name in self.functions:
            # AUTO: Returns this result to the caller.
            return f"Semantic Error: Variable '{name}' already declared as a function."

        # AUTO: Checks this condition.
        if current_func:
            # AUTO: Checks this condition.
            if current_func not in self.function_variables:
                # AUTO: Sets `self.function_variables[current_func]`.
                self.function_variables[current_func] = set()

            # AUTO: Checks this condition.
            if name in self.function_variables[current_func]:
                # AUTO: Returns this result to the caller.
                return f"Semantic Error: Variable '{name}' already declared in this function."

            # AUTO: Calls `self.function_variables[current_func].add`.
            self.function_variables[current_func].add(name)

        # AUTO: Checks this condition.
        if self.current_func_name:
            
            # AUTO: Sets `scope[name]`.
            scope[name] = {
                # AUTO: Executes this statement.
                "type": type_,  
                # AUTO: Executes this statement.
                "value": value,
                # AUTO: Executes this statement.
                "is_list": is_list,
                # AUTO: Executes this statement.
                "is_fertile": is_fertile
            # AUTO: Closes the current grouped code/data.
            }
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Checks this condition.
            if name in self.global_variables:
                # AUTO: Returns this result to the caller.
                return f"Semantic Error: Variable '{name}' already declared."
            
            # AUTO: Sets `self.variables[name]`.
            self.variables[name] = {
                # AUTO: Executes this statement.
                "type": type_,
                # AUTO: Executes this statement.
                "value": value,
                # AUTO: Executes this statement.
                "is_list": is_list,
                # AUTO: Executes this statement.
                "is_fertile": is_fertile
            # AUTO: Closes the current grouped code/data.
            }
        

    # AUTO: Defines function `lookup_variable`.
    def lookup_variable(self, name):
        # AUTO: Starts a loop over these values.
        for i, scope in enumerate(reversed(self.scopes)):
            # AUTO: Checks this condition.
            if name in scope:
                # AUTO: Returns this result to the caller.
                return scope[name]
        
        # AUTO: Checks this condition.
        if name in self.variables:
            # AUTO: Returns this result to the caller.
            return self.variables[name]

        # AUTO: Returns this result to the caller.
        return f"Semantic Error: Variable '{name}' used before declaration."
    
    # AUTO: Defines function `set_variable`.
    def set_variable(self, name, value):
        # AUTO: Sets `current_scope`.
        current_scope = self.scopes[-1]

        # AUTO: Checks this condition.
        if name in current_scope:
            # AUTO: Sets `current_scope[name]["value"]`.
            current_scope[name]["value"] = value
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Returns this result to the caller.
            return f"Semantic Error: Variable '{name}' not declared in the current scope."

    # AUTO: Defines function `declare_function`.
    def declare_function(self, name, return_type, params, node=None):
        # AUTO: Checks this condition.
        if name in self.functions:
            # AUTO: Returns this result to the caller.
            return f"Semantic Error: Function '{name}' already declared."
        # AUTO: Sets `self.functions[name]`.
        self.functions[name] = {"return_type": return_type, "params": params, "node": node}

    # AUTO: Defines function `lookup_function`.
    def lookup_function(self, name):
        # AUTO: Checks this condition.
        if name in self.functions:
            # AUTO: Returns this result to the caller.
            return self.functions[name]
        # AUTO: Returns this result to the caller.
        return f"Semantic Error: Function '{name}' is not defined."
    

    # AUTO: Defines function `enter_scope`.
    def enter_scope(self):
        # AUTO: Appends a value to a list.
        self.scopes.append({})
        

    # AUTO: Defines function `exit_scope`.
    def exit_scope(self):
        # AUTO: Checks this condition.
        if len(self.scopes) > 1:
            # AUTO: Removes and returns an item.
            self.scopes.pop()
        
        # AUTO: Checks this condition.
        if self.current_func_name:
            # AUTO: Sets `current_func`.
            current_func = self.current_func_name

            # AUTO: Checks this condition.
            if current_func in self.function_variables:
                # AUTO: Calls `self.function_variables[current_func].clear`.
                self.function_variables[current_func].clear()


    # AUTO: Defines function `debug_scopes`.
    def debug_scopes(self):
        # AUTO: Calls `print`.
        print("\n====== SYMBOL TABLE DEBUG ======")
        # AUTO: Calls `print`.
        print("🔹 Local Scopes (Stacked from Global to Inner Scope):")
        # AUTO: Starts a loop over these values.
        for i, scope in enumerate(self.scopes):
            # AUTO: Calls `print`.
            print(f"  Scope {i}: {scope}")
        # AUTO: Calls `print`.
        print("================================\n")


