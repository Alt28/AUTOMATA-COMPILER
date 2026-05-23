# ============================================================================
# SYMBOL TABLE - Declaration tracker for the AST builder
# ============================================================================
# Extracted from GALsemantic.py during the modular restructure.
# Used by parser/builder.py during AST construction to track variables,
# functions, bundles, and scopes; the populated table is then serialized
# (in parser/parser.py) and passed to semantic/analyzer.py for the second
# semantic pass.
# ============================================================================


class SymbolTable:
    def __init__(self):
        self.variables = {}  # Stores variables
        self.global_variables = {}  # Stores global variables
        self.functions = {}  # Stores function definitions
        self.scopes = [{}]   # Stack of scopes (for local/global tracking)
        self.current_func_name = None
        self.function_variables = {}
        self.bundle_types = {}  # Stores bundle (struct) type definitions

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



# ============================================================================
# BUILD AST + parse_* HELPERS - Moved to parser/builder.py (Phase 5b).
# No re-export here because that would create a circular import:
#     parser.builder imports SymbolTable from here, so we can't also import
#     back from parser.builder.
# External callers should import directly from the new location:
#     from parser.builder import build_ast, symbol_table, analyze_semantics
# ============================================================================



