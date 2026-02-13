# ============================================================================
# GAL LANGUAGE SEMANTIC ANALYZER
# ============================================================================
# This module performs semantic analysis on the GAL language after parsing.
# It checks for:
# - Variable declarations and usage
# - Type checking
# - Scope management
# - Function declarations and calls
# - Symbol table management

#wala pa toh eme lang
# ============================================================================

from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass


@dataclass
class Symbol:
    """Represents a symbol in the symbol table"""
    name: str
    type: str  # seed, tree, leaf, branch, vine, etc.
    scope: str  # global, function name, or block identifier
    line: int
    is_constant: bool = False
    is_initialized: bool = False
    value: Any = None


class SymbolTable:
    """Manages symbols across different scopes"""
    
    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Stack of scopes
        self.scope_names: List[str] = ["global"]
        self.functions: Dict[str, Dict] = {}  # Function signatures
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def enter_scope(self, scope_name: str):
        """Enter a new scope"""
        self.scopes.append({})
        self.scope_names.append(scope_name)
    
    def exit_scope(self):
        """Exit the current scope"""
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.scope_names.pop()
    
    def current_scope(self) -> str:
        """Get the current scope name"""
        return self.scope_names[-1]
    
    def declare(self, symbol: Symbol) -> bool:
        """Declare a symbol in the current scope"""
        current = self.scopes[-1]
        
        # Check if already declared in current scope
        if symbol.name in current:
            self.errors.append(
                f"Line {symbol.line}: Variable '{symbol.name}' already declared in this scope"
            )
            return False
        
        current[symbol.name] = symbol
        return True
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in current and enclosing scopes"""
        # Search from innermost to outermost scope
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def declare_function(self, name: str, return_type: str, params: List[Tuple[str, str]], line: int):
        """Declare a function"""
        if name in self.functions:
            self.errors.append(
                f"Line {line}: Function '{name}' already declared"
            )
            return False
        
        self.functions[name] = {
            'return_type': return_type,
            'params': params,
            'line': line
        }
        return True
    
    def get_function(self, name: str) -> Optional[Dict]:
        """Get function information"""
        return self.functions.get(name)


class SemanticAnalyzer:
    """Performs semantic analysis on GAL programs"""
    
    # Type mapping for GAL keywords to internal types
    TYPE_MAP = {
        'seed': 'int',
        'tree': 'float',
        'leaf': 'char',
        'branch': 'bool',
        'vine': 'string',
        'empty': 'void'
    }
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.in_function = False
        self.current_function_return_type = None
        self.in_loop = False
    
    def analyze(self, tokens: List[Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Perform semantic analysis on a list of tokens
        Returns: (success, errors, warnings)
        """
        self.symbol_table = SymbolTable()
        self._analyze_tokens(tokens)
        
        success = len(self.symbol_table.errors) == 0
        return success, self.symbol_table.errors, self.symbol_table.warnings
    
    def _analyze_tokens(self, tokens: List[Any]):
        """Analyze the token stream"""
        i = 0
        while i < len(tokens):
            token = self._get_token(tokens[i])
            
            # Variable declarations
            if token.type in ['seed', 'tree', 'leaf', 'branch', 'vine']:
                i = self._check_variable_declaration(tokens, i)
            
            # Constant declarations
            elif token.type == 'fertile':
                i = self._check_constant_declaration(tokens, i)
            
            # Function declarations
            elif token.type == 'pollinate':
                i = self._check_function_declaration(tokens, i)
            
            # Main function
            elif token.type == 'root':
                i = self._check_main_function(tokens, i)
            
            # Assignments
            elif token.type == 'id':
                i = self._check_identifier_usage(tokens, i)
            
            # Control flow
            elif token.type in ['spring', 'grow', 'cultivate', 'tend', 'harvest']:
                i = self._check_control_flow(tokens, i)
            
            # Loop control
            elif token.type in ['prune', 'skip']:
                i = self._check_loop_control(tokens, i)
            
            # Return statements
            elif token.type == 'reclaim':
                i = self._check_return_statement(tokens, i)
            
            # Scope changes
            elif token.type == '{':
                self.symbol_table.enter_scope(f"block_{token.line}")
            
            elif token.type == '}':
                self.symbol_table.exit_scope()
            
            i += 1
    
    def _get_token(self, token: Any):
        """Normalize token access"""
        if isinstance(token, dict):
            class TokenView:
                def __init__(self, t):
                    self.type = t.get('type', '')
                    self.value = t.get('value', '')
                    self.line = t.get('line', 0)
            return TokenView(token)
        return token
    
    def _check_variable_declaration(self, tokens: List[Any], index: int) -> int:
        """Check variable declaration"""
        token = self._get_token(tokens[index])
        var_type = token.type
        line = token.line
        
        # Next token should be identifier
        if index + 1 < len(tokens):
            next_token = self._get_token(tokens[index + 1])
            if next_token.type == 'id':
                symbol = Symbol(
                    name=next_token.value,
                    type=self.TYPE_MAP.get(var_type, var_type),
                    scope=self.symbol_table.current_scope(),
                    line=line,
                    is_constant=False
                )
                
                # Check if initialized
                if index + 2 < len(tokens):
                    assign_token = self._get_token(tokens[index + 2])
                    if assign_token.type == '=':
                        symbol.is_initialized = True
                
                self.symbol_table.declare(symbol)
                return index + 1
        
        return index
    
    def _check_constant_declaration(self, tokens: List[Any], index: int) -> int:
        """Check constant declaration"""
        # fertile <type> <id> = <value>
        if index + 3 < len(tokens):
            type_token = self._get_token(tokens[index + 1])
            id_token = self._get_token(tokens[index + 2])
            
            if type_token.type in self.TYPE_MAP and id_token.type == 'id':
                if index + 3 < len(tokens):
                    assign_token = self._get_token(tokens[index + 3])
                    if assign_token.type != '=':
                        self.symbol_table.errors.append(
                            f"Line {id_token.line}: Constant must be initialized"
                        )
                
                symbol = Symbol(
                    name=id_token.value,
                    type=self.TYPE_MAP.get(type_token.type, type_token.type),
                    scope=self.symbol_table.current_scope(),
                    line=id_token.line,
                    is_constant=True,
                    is_initialized=True
                )
                self.symbol_table.declare(symbol)
        
        return index
    
    def _check_function_declaration(self, tokens: List[Any], index: int) -> int:
        """Check function declaration"""
        # pollinate <return_type> <id> ( params )
        if index + 2 < len(tokens):
            return_type_token = self._get_token(tokens[index + 1])
            func_name_token = self._get_token(tokens[index + 2])
            
            if func_name_token.type == 'id':
                return_type = self.TYPE_MAP.get(return_type_token.type, return_type_token.type)
                
                # Parse parameters (simplified)
                params = []
                self.symbol_table.declare_function(
                    func_name_token.value,
                    return_type,
                    params,
                    func_name_token.line
                )
                
                # Enter function scope
                self.symbol_table.enter_scope(func_name_token.value)
                self.in_function = True
                self.current_function_return_type = return_type
        
        return index
    
    def _check_main_function(self, tokens: List[Any], index: int) -> int:
        """Check main function declaration"""
        # root ( )
        token = self._get_token(tokens[index])
        self.symbol_table.declare_function('root', 'void', [], token.line)
        self.symbol_table.enter_scope('root')
        self.in_function = True
        self.current_function_return_type = 'void'
        return index
    
    def _check_identifier_usage(self, tokens: List[Any], index: int) -> int:
        """Check if identifier is declared before use"""
        token = self._get_token(tokens[index])
        symbol = self.symbol_table.lookup(token.value)
        
        if symbol is None:
            # Check if it's a function call
            func = self.symbol_table.get_function(token.value)
            if func is None:
                self.symbol_table.errors.append(
                    f"Line {token.line}: Undeclared identifier '{token.value}'"
                )
        else:
            # Check if assigned to constant
            if index + 1 < len(tokens):
                next_token = self._get_token(tokens[index + 1])
                if next_token.type in ['=', '+=', '-=', '*=', '/=', '%=']:
                    if symbol.is_constant:
                        self.symbol_table.errors.append(
                            f"Line {token.line}: Cannot assign to constant '{token.value}'"
                        )
            
            # Warn about uninitialized variables
            if not symbol.is_initialized and symbol.type != 'void':
                self.symbol_table.warnings.append(
                    f"Line {token.line}: Variable '{token.value}' may be uninitialized"
                )
        
        return index
    
    def _check_control_flow(self, tokens: List[Any], index: int) -> int:
        """Check control flow statements"""
        token = self._get_token(tokens[index])
        
        if token.type in ['grow', 'cultivate', 'tend']:
            self.in_loop = True
        
        # Check if the condition is a boolean expression, not a numeric literal
        if token.type in ['spring', 'grow', 'tend', 'bud']:
            # Look for the opening parenthesis
            i = index + 1
            while i < len(tokens) and self._get_token(tokens[i]).type in ['\n', ' ', '\t']:
                i += 1
            
            if i < len(tokens) and self._get_token(tokens[i]).type == '(':
                # Find the condition expression (first token after '(')
                i += 1
                while i < len(tokens) and self._get_token(tokens[i]).type in ['\n', ' ', '\t']:
                    i += 1
                
                if i < len(tokens):
                    cond_token = self._get_token(tokens[i])
                    # Check if it's a numeric literal without any operators
                    if cond_token.type == 'intlit' or cond_token.type == 'dblit':
                        # Look ahead to see if there's a comparison operator
                        next_i = i + 1
                        while next_i < len(tokens) and self._get_token(tokens[next_i]).type in ['\n', ' ', '\t']:
                            next_i += 1
                        
                        if next_i < len(tokens):
                            next_token = self._get_token(tokens[next_i])
                            # If next token is ')' then it's just a literal without comparison
                            if next_token.type == ')':
                                self.symbol_table.errors.append(
                                    f"Line {token.line}: '{token.type}' requires a boolean condition, not a numeric literal"
                                )
        
        return index
    
    def _check_loop_control(self, tokens: List[Any], index: int) -> int:
        """Check loop control statements (prune/skip)"""
        token = self._get_token(tokens[index])
        
        if not self.in_loop:
            keyword = 'break' if token.type == 'prune' else 'continue'
            self.symbol_table.errors.append(
                f"Line {token.line}: '{token.type}' ({keyword}) statement outside loop"
            )
        
        return index
    
    def _check_return_statement(self, tokens: List[Any], index: int) -> int:
        """Check return statement"""
        token = self._get_token(tokens[index])
        
        if not self.in_function:
            self.symbol_table.errors.append(
                f"Line {token.line}: Return statement outside function"
            )
        
        # TODO: Check if return type matches function signature
        
        return index


def analyze_semantics(tokens: List[Any]) -> Dict[str, Any]:
    """
    Main entry point for semantic analysis
    Returns a dictionary with analysis results
    """
    analyzer = SemanticAnalyzer()
    success, errors, warnings = analyzer.analyze(tokens)
    
    return {
        'success': success,
        'errors': errors,
        'warnings': warnings,
        'symbol_table': {
            'variables': [
                {
                    'name': sym.name,
                    'type': sym.type,
                    'scope': sym.scope,
                    'line': sym.line,
                    'is_constant': sym.is_constant
                }
                for scope in analyzer.symbol_table.scopes
                for sym in scope.values()
            ],
            'functions': analyzer.symbol_table.functions
        }
    }
