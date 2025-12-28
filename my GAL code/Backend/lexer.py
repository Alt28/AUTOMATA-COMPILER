# ============================================================================
# GAL LANGUAGE LEXER - Converts source code into tokens
# ============================================================================
# This lexer performs lexical analysis (tokenization) for the GAL language.
# It reads source code character by character and groups them into tokens
# (keywords, identifiers, operators, literals, etc.)
# ============================================================================

#CONSTANTS - Character sets used for token recognition

ZERO = '0'  # Zero digit (special case for leading zeros)
DIGIT = '123456789'  # Non-zero digits
ZERODIGIT = ZERO + DIGIT  # All digits (0-9)

LOW_ALPHA = 'abcdefghijklmnopqrstuvwxyz'  # Lowercase letters
UPPER_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # Uppercase letters

ALPHA = LOW_ALPHA + UPPER_ALPHA  # All letters (a-z, A-Z)
ALPHANUM = ALPHA + ZERODIGIT + '_'  # Letters, digits, and underscore (valid for identifiers)

# --- DELIMITER SETS ---
# Delimiters are characters that can legally appear AFTER certain tokens.
# Different token types have different valid delimiters to ensure proper syntax.

space_delim = {' ', ';', '{'}  # Valid after keywords like 'seed', 'tree', 'leaf'
delim2 = {';', ':'}  # Valid after 'soil' (default case)
delim3 = {'{'}  # Valid after 'tend' (do-while), 'wither' (else)
delim4 = {':', '('}  # Valid after 'bud' (else-if), 'cultivate' (for), 'harvest' (switch)
delim5 = {'('}  # Valid after certain keywords requiring parentheses
delim6 = {';', ',', '=', '>', '<', '!', '}', ')', '('}  # Valid after 'spring', 'plant', 'water'
delim7 = {'('}  # Valid after 'root' (main function)
delim8 = {';'}  # Valid after statements requiring semicolon
delim9 = set(ALPHA + '(' + ',' + ';' + ')')  # Valid for function-related contexts
delim10 = {';', ')'}  # Valid for closing statements
delim11 = {'\n'}  # Newline delimiter
delim12 = set(ALPHA + ZERODIGIT + ']' + '~')  # Valid for array/negation contexts
delim13 = {';', ')', '['}  # Valid for mixed statement endings
delim14 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')  # Valid before literals/blocks
delim15 = {'\n', ';', '}', ','}  # Valid for multi-context endings
delim16 = set(ALPHANUM + ')' + '"' + '!' + '(' + '[' + '\'')  # Valid for expression contexts
delim17 = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}  # Valid for operator contexts
delim18 = {';', '{', ')', '&', '|', '+', '-', '*', '/', '%'}  # Valid for logical/arithmetic contexts
delim19 = {';', ',', '}', ')', '=', '>', '<', '!'}  # Valid for comparison contexts
delim20 = set(ALPHA + ZERODIGIT  + '"' + "'" + '{' )  # Valid before string/char literals
delim21 = set(DIGIT)  # Digit delimiters
delim22 = {',', ';', '(', ')', '{', '[', ']'}  # Valid for punctuation contexts
delim23 = {';', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}  # Valid after literals
delim24 = set(ZERODIGIT + ALPHA + '~' + '(')  # Valid for unary/function contexts
idf_delim = { ' ', ',', ';', '(', ')', '{', '}', '[', ']', ':', '+', '-', '*', '/', '%' , '>', '<', '=', '\t', '\n'}  # Valid after identifiers
whlnum_delim = { ';', ' ', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', '\t', '\n' }  # Valid after integers
decim_delim = { '}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ' ', '\t', '\n', ')' }  # Valid after floats/doubles
comment_delim = set(ALPHANUM + ';+-*/%}{()' + '\n')  # Valid within comments


# ============================================================================
# TOKEN TYPE CONSTANTS - String identifiers for each token type
# ============================================================================

# --- Reserved Words (Keywords) ---
TT_RW_WATER       = 'water'     # Input function - reads user input
TT_RW_PLANT       = 'plant'     # Output function - prints to console
TT_RW_SEED        = 'seed'      # Data Type - integer (int)
TT_RW_LEAF        = 'leaf'      # Data Type - character (char)
TT_RW_BRANCH      = 'branch'    # Data Type - boolean (true/false)
TT_RW_TREE        = 'tree'      # Data Type - double/float
TT_RW_SPRING      = 'spring'    # Conditional statement - if
TT_RW_WITHER      = 'wither'    # Conditional statement - else
TT_RW_BUD         = 'bud'       # Conditional statement - else-if
TT_RW_HARVEST     = 'harvest'   # Switch statement
TT_RW_GROW        = 'grow'      # Loop - while
TT_RW_CULTIVATE   = 'cultivate' # Loop - for
TT_RW_TEND        = 'tend'      # Loop - do-while
TT_RW_EMPTY       = 'empty'     # Void return type
TT_RW_PRUNE       = 'prune'     # Break statement - exit loop
TT_RW_SKIP        = 'skip'      # Continue statement - skip to next iteration
TT_RW_RECLAIM     = 'reclaim'   # Return statement - return from function
TT_RW_ROOT        = 'root'      # Main function entry point
TT_RW_POLLINATE   = 'pollinate' # Function declaration
TT_RW_VARIETY     = 'variety'   # Case label in switch statement
TT_RW_FERTILE     = 'fertile'   # Constant declaration
TT_RW_SOIL        = 'soil'      # Default case in switch statement
TT_RW_BUNDLE      = 'bundle'    # Struct definition
TT_RW_STRING      = 'string'    # String data type

# --- Operators & Symbols ---
TT_IDENTIFIER = 'id'        # Variable/function names (e.g., myVar, calcTotal)
TT_PLUS = '+'               # Addition operator
TT_MINUS = '-'              # Subtraction operator
TT_MUL = '*'                # Multiplication operator
TT_DIV = '/'                # Division operator
TT_MOD = '%'                # Modulo operator (remainder)
TT_EXP = '**'               # Exponentiation operator (power)
TT_EQ = '='                 # Assignment operator
TT_EQTO = '=='              # Equality comparison operator
TT_PLUSEQ = '+='            # Add and assign operator
TT_MINUSEQ = '-='           # Subtract and assign operator
TT_MULTIEQ = '*='           # Multiply and assign operator
TT_DIVEQ = '/='             # Divide and assign operator
TT_MODEQ = '%='             # Modulo and assign operator
TT_CONCAT = '`'             # String concatenation operator
TT_LPAREN = '('             # Left parenthesis
TT_RPAREN = ')'             # Right parenthesis
TT_SEMICOLON = ';'          # Statement terminator
TT_COMMA = ','              # Separator (function args, array elements)
TT_COLON = ':'              # Colon (used in switch cases)
TT_BLOCK_START = '{'        # Block start (scope begin)
TT_BLOCK_END = '}'          # Block end (scope close)
TT_LT = '<'                 # Less than comparison
TT_GT = '>'                 # Greater than comparison
TT_LTEQ = '<='              # Less than or equal comparison
TT_GTEQ = '>='              # Greater than or equal comparison
TT_NOTEQ = '!='             # Not equal comparison
TT_EOF = 'EOF'                  # End of file marker
TT_AND = '&&'                   # Logical AND operator
TT_OR = '||'                    # Logical OR operator
TT_NOT = '!'                    # Logical NOT operator
TT_INCREMENT = '++'             # Increment operator (e.g., x++)
TT_DECREMENT = '--'             # Decrement operator (e.g., x--)
TT_LSQBR = '['                  # Left square bracket (array indexing)
TT_RSQBR = ']'                  # Right square bracket
TT_NEGATIVE = '~'               # Unary negation operator
TT_MEMBER = 'member'            # Member token for struct access
TT_INTEGERLIT = 'intlit'        # Integer literal token (e.g., 42, 100)
TT_NEGINTLIT = '~intlit'        # Negative integer literal token
TT_DOUBLELIT = 'dbllit'         # Double/float literal token (e.g., 3.14, 2.5)
TT_NEGDOUBLELIT = '~dbllit'     # Negative double literal token
TT_STRINGLIT = 'strnglit'       # String literal token (e.g., "hello")
TT_CHARLIT = 'chrlit'           # Character literal token (e.g., 'a')
TT_STRCTACCESS = '.'            # Struct member access operator
TT_NL = '\n'                    # Newline token
TT_DOT = '.'                    # Dot operator (struct access)


# ============================================================================
# POSITION CLASS - Tracks current location in source code
# ============================================================================
class Position:
    """Tracks the position (line, column, index) in the source code for error reporting"""
    def __init__(self, index, ln, col=0):
        self.index = index  # Character index in source code (0-based)
        self.ln = ln        # Line number (1-based)
        self.col = col      # Column number (0-based)

    def advance(self, current_char):
        """Advance to the next character, updating line/column numbers"""
        self.index += 1
        self.col += 1

        if current_char == '\n':  # New line detected
            self.ln += 1
            self.col = 0  # Reset column to start of line

        return self
    
    def copy(self):
        """Returns a copy of the current position (for error tracking)"""
        return Position(self.index, self.ln, self.col)

# ============================================================================
# LEXICAL ERROR CLASS - Represents errors found during tokenization
# ============================================================================
class LexicalError:
    """Stores information about a lexical error (position and description)"""
    def __init__(self, pos, details):
        self.pos = pos          # Position object where error occurred
        self.details = details  # Error description

    def as_string(self):
        """Returns the error message in readable string format"""
        self.details = self.details.replace('\n', '\\n')  # Escape newlines in error message
        return f"Ln {self.pos.ln}, Col {self.pos.col}: {self.details}"

# ============================================================================
# TOKEN CLASS - Represents a single token (lexeme)
# ============================================================================
class Token:
    """Represents a token with type, value, and line number"""
    def __init__(self, type_, value=None, line=1): 
        self.type = type_    # Token type (e.g., TT_IDENTIFIER, TT_INTEGERLIT)
        self.value = value   # Token text/value (e.g., "myVar", "42")
        self.line = line     # Line number where token appears

# ============================================================================
# LEXER CLASS - Main tokenization engine
# ============================================================================
class Lexer:
    """
    The Lexer class performs lexical analysis on GAL source code.
    It scans character by character and groups them into tokens.
    """
    def __init__(self, source_code): 
        self.source_code = source_code     # Input source code string
        self.pos = Position(-1, 1, -1)     # Current position (starts before first char)
        self.current_char = None           # Current character being examined
        self.advance()                     # Move to first character

    def advance(self):
        """Advance to the next character in the source code"""
        self.pos.advance(self.current_char)
        # Get character at current index, or None if at end
        self.current_char = self.source_code[self.pos.index] if self.pos.index<len(self.source_code) else None

    def make_tokens(self):
        """
        Main tokenization method - converts source code into tokens.
        Returns: (tokens, errors) tuple
        - tokens: list of Token objects
        - errors: list of LexicalError objects
        """
        tokens = []  # List to store all tokens found
        line = 1     # Current line number (for token tracking)
        errors = []  # List to store all lexical errors found
        
        # Main loop: process each character until end of file
        while self.current_char != None:
            
            # =====================================================================
            # KEYWORD & IDENTIFIER RECOGNITION
            # Check if current character starts a keyword or identifier (letter)
            # =====================================================================
            if self.current_char in ALPHA:
                ident_str = ''      # String to build the identifier/keyword
                pos = self.pos.copy()  # Save position for error reporting
                
                # --- Letter B: 'branch', 'bud', 'bundle' ---
                if self.current_char == "b":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "r": # branch
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "a":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "n":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "c":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "h":
                                        ident_str += self.current_char
                                        self.advance()
                                        # Branch must be followed by an identifier (variable name)
                                        if self.current_char == ';':
                                            errors.append(LexicalError(pos, f"Expected an identifier after '{ident_str}'"))
                                            self.advance()
                                            continue
                                        elif self.current_char is not None and self.current_char in space_delim:
                                            tokens.append(Token(TT_RW_BRANCH, ident_str, line))
                                            self.advance()
                                            continue
                                        elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            self.advance()
                                            continue
                    elif self.current_char == "u":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "d": # bud
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:
                                tokens.append(Token(TT_RW_BUD, ident_str, line))
                                continue
                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                self.advance()
                                continue
                        elif self.current_char == "n": # bundle
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "d":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "l":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "e":
                                        ident_str += self.current_char
                                        self.advance()
                                        if self.current_char is not None and self.current_char in space_delim: # struct delimiter (was hawk_dlm)
                                            tokens.append(Token(TT_RW_BUNDLE, ident_str, line))
                                            continue
                                        elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            self.advance()
                                            continue
                
                #Letter C
                elif self.current_char == "c":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "u": # cultivate
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "l":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "t":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "i":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "v":
                                        ident_str += self.current_char
                                        self.advance()
                                        if self.current_char == "a":
                                            ident_str += self.current_char
                                            self.advance()
                                            if self.current_char == "t":
                                                ident_str += self.current_char
                                                self.advance()
                                                if self.current_char == "e":
                                                    ident_str += self.current_char
                                                    self.advance()
                                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:
                                                        tokens.append(Token(TT_RW_CULTIVATE, ident_str, line))
                                                        continue
                                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                        self.advance()
                                                        continue
                
                # Letter E
                elif self.current_char == "e":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "m": # empty
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "p":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "t":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "y":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                        tokens.append(Token(TT_RW_EMPTY, ident_str, line))
                                        continue
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        self.advance()
                                        continue

                # Letter F
                elif self.current_char == "f":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "r": # frost
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "o":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "s":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "t":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char is None or (self.current_char not in ALPHANUM and self.current_char != '_'):
                                        tokens.append(Token(TT_RW_BRANCH, ident_str, line)) # Boolean Literal
                                        continue
                                    # If followed by alphanum/underscore, continue to identifier parsing
                    elif self.current_char == "e": # fertile
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "r":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "t":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "i":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "l":
                                        ident_str += self.current_char
                                        self.advance()
                                        if self.current_char == "e":
                                            ident_str += self.current_char
                                            self.advance()
                                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
                                                tokens.append(Token(TT_RW_FERTILE, ident_str, line))
                                                continue
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                self.advance()
                                                continue
                                            
                # Letter G
                elif self.current_char == "g":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "r": # grow
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "o":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "w":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4 or self.current_char in space_delim:
                                    tokens.append(Token(TT_RW_GROW, ident_str, line))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue
                                
                # Letter H
                elif self.current_char == "h":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "a": # harvest
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "r":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "v":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "e":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "s":
                                        ident_str += self.current_char
                                        self.advance()
                                        if self.current_char == "t":
                                            ident_str += self.current_char
                                            self.advance()
                                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:
                                                tokens.append(Token(TT_RW_HARVEST, ident_str, line))
                                                continue
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                self.advance()
                                                continue
                                
                # Letter L
                elif self.current_char == "l":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "e": # leaf
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "a":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "f":
                                ident_str += self.current_char
                                self.advance()
                                # Leaf must be followed by an identifier (variable name)
                                if self.current_char == ';':
                                    errors.append(LexicalError(pos, f"Expected an identifier after '{ident_str}'"))
                                    self.advance()
                                    continue
                                elif self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                    tokens.append(Token(TT_RW_LEAF, ident_str, line))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue
                        
                # Letter P
                elif self.current_char == "p":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "l": # plant
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "a":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "n":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "t":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim6:
                                        tokens.append(Token(TT_RW_PLANT, ident_str, line))
                                        continue
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim6 and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        self.advance()
                                        continue
                    elif self.current_char == "o": # pollinate
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "l":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "l":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "i":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "n":
                                        ident_str += self.current_char
                                        self.advance()
                                        if self.current_char == "a":
                                            ident_str += self.current_char
                                            self.advance()
                                            if self.current_char == "t":
                                                ident_str += self.current_char
                                                self.advance()
                                                if self.current_char == "e":
                                                    ident_str += self.current_char
                                                    self.advance()
                                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                                        tokens.append(Token(TT_RW_POLLINATE, ident_str, line))
                                                        continue
                                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                        self.advance()
                                                        continue
                    elif self.current_char == "r": # prune
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "u":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "n":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "e":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                        tokens.append(Token(TT_RW_PRUNE, ident_str, line))
                                        continue
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        self.advance()
                                        continue

                # Letter R
                elif self.current_char == "r":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "e": # reclaim
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "c":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "l":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "a":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "i":
                                        ident_str += self.current_char
                                        self.advance()
                                        if self.current_char == "m":
                                            ident_str += self.current_char
                                            self.advance()
                                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
                                                tokens.append(Token(TT_RW_RECLAIM, ident_str, line))
                                                continue
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                continue
                    elif self.current_char == "o": # root
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "o":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "t":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim7:
                                    tokens.append(Token(TT_RW_ROOT, ident_str, line))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim7 and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()  # Skip the invalid character
                                    continue

                # Letter S
                elif self.current_char == "s": 
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "e": # seed
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "e":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "d":
                                ident_str += self.current_char
                                self.advance()
                                # Seed must be followed by an identifier (variable name)
                                if self.current_char == ';':
                                    errors.append(LexicalError(pos, f"Expected an identifier after '{ident_str}'"))
                                    self.advance()
                                    continue
                                elif self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                    tokens.append(Token(TT_RW_SEED, ident_str, line))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue
                    elif self.current_char == "k": # skip
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "i":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "p":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                    tokens.append(Token(TT_RW_SKIP, ident_str, line))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue
                    elif self.current_char == "o": # soil
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "i":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "l":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim2:
                                    tokens.append(Token(TT_RW_SOIL, ident_str, line))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim2 and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue
                    elif self.current_char == "p": # spring
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "r":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "i":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "n":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "g":
                                        ident_str += self.current_char
                                        self.advance()
                                        if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim6:
                                            tokens.append(Token(TT_RW_SPRING, ident_str, line))
                                            continue
                                        elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim6 and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            self.advance()
                                            continue
                    elif self.current_char == "u": # sunshine
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "n":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "s":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "h":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "i":
                                        ident_str += self.current_char
                                        self.advance()
                                        if self.current_char == "n":
                                            ident_str += self.current_char
                                            self.advance()
                                            if self.current_char == "e":
                                                ident_str += self.current_char
                                                self.advance()
                                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                                    tokens.append(Token(TT_RW_BRANCH, ident_str, line)) # Boolean Literal
                                                    continue
                                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                    self.advance()
                                                    continue

                # Letter T
                elif self.current_char == "t":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "e": # tend
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "n":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "d":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim3:
                                    tokens.append(Token(TT_RW_TEND, ident_str, line))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim3 and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue
                    elif self.current_char == "r": # tree
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "e":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "e":
                                ident_str += self.current_char
                                self.advance()
                                # Tree must be followed by an identifier (variable name), check if followed by valid start
                                if self.current_char == ';':
                                    errors.append(LexicalError(pos, f"Expected an identifier after '{ident_str}'"))
                                    self.advance()
                                    continue
                                elif self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                    tokens.append(Token(TT_RW_TREE, ident_str, line))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue

                # Letter V
                elif self.current_char == "v":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "a": # variety
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "r":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "i":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "e":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "t":
                                        ident_str += self.current_char
                                        self.advance()
                                        if self.current_char == "y":
                                            ident_str += self.current_char
                                            self.advance()
                                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                                tokens.append(Token(TT_RW_VARIETY, ident_str, line))
                                                continue
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                self.advance()
                                                continue

                # Letter W
                elif self.current_char == "w":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "a": # water
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "t":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "e":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "r":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim6:
                                        tokens.append(Token(TT_RW_WATER, ident_str, line))
                                        continue
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim6 and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        self.advance()
                                        continue
                    elif self.current_char == "i": # wither
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "t":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "h":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "e":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "r":
                                        ident_str += self.current_char
                                        self.advance()
                                        if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim3:
                                            tokens.append(Token(TT_RW_WITHER, ident_str, line))
                                            continue
                                        elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim3 and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            self.advance()
                                            continue

                #Identifier            
                maxIdentifierLength = 16 # Changed from 20 to 16
                while self.current_char is not None and self.current_char in ALPHANUM:
                    if len(ident_str) + 1 > maxIdentifierLength:
                        errors.append(LexicalError(pos, f"Identifier '{ident_str}...' exceeds maximum length of {maxIdentifierLength} characters."))
                        # Consume the rest of the invalid identifier
                        while self.current_char is not None and self.current_char in ALPHANUM:
                            self.advance()
                        break
                    ident_str += self.current_char
                    self.advance()

                if len(ident_str) <= maxIdentifierLength:
                    if self.current_char is None or self.current_char in idf_delim:
                        tokens.append(Token(TT_IDENTIFIER, ident_str, line))
                        continue
                    elif self.current_char is not None and self.current_char not in idf_delim and self.current_char not in ALPHANUM:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                else:
                    # Error was already appended, just continue to next token
                    continue

            
            elif self.current_char == "-":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "-":
                    # Check if previous token is an identifier (valid for --)
                    if len(tokens) > 0 and tokens[-1].type == TT_IDENTIFIER:
                        ident_str += self.current_char
                        self.advance()
                        tokens.append(Token(TT_DECREMENT, ident_str, line))
                        continue
                    else:
                        # -- not after an identifier is an error
                        errors.append(LexicalError(pos, f"Consecutive operators '{ident_str}{self.current_char}' are not allowed"))
                        self.advance()  # Consume the second -
                        continue
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_MINUSEQ, ident_str, line))
                    continue
                # Check for consecutive operators
                if self.current_char is not None and self.current_char in '+-*/%':
                    errors.append(LexicalError(pos, f"Consecutive operators '{ident_str}{self.current_char}' are not allowed"))
                    self.advance()  # Consume the operator
                    continue
                # Check for valid delimiter after -
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
                # Check if previous token was an operator (catch "- -" case with whitespace)
                if len(tokens) > 0 and tokens[-1].type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD]:
                    errors.append(LexicalError(pos, f"Consecutive operators '{tokens[-1].value} {ident_str}' are not allowed"))
                    continue
                tokens.append(Token(TT_MINUS, ident_str, line))
                continue
            
            elif self.current_char == "~": # Added for negative prefix
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                # ~ should be followed by numbers, identifiers, or whitespace (for negation)
                if self.current_char is None or self.current_char in ALPHANUM + ' \t\n':
                    tokens.append(Token(TT_NEGATIVE, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'."))
                    continue
            
            elif self.current_char == "!":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    # Check for consecutive comparison operators
                    if len(tokens) > 0 and tokens[-1].type in ['>', '<', '==', '!=', '>=', '<=']:
                        errors.append(LexicalError(pos, f"Consecutive operators '{tokens[-1].value} {ident_str}' are not allowed"))
                        continue
                    tokens.append(Token(TT_NOTEQ, ident_str, line))
                    continue
                else:
                    tokens.append(Token(TT_NOT, ident_str, line))
                    continue
            
            elif self.current_char == "%":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_MODEQ, ident_str, line))
                    continue
                # Check for consecutive operators
                if self.current_char is not None and self.current_char in '+-*/%':
                    errors.append(LexicalError(pos, f"Consecutive operators '{ident_str}{self.current_char}' are not allowed"))
                    self.advance()  # Consume the operator
                    continue
                # Check for valid delimiter after %
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ;' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
                # Check if previous token was an operator (catch "% +" case with whitespace)
                if len(tokens) > 0 and tokens[-1].type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD]:
                    errors.append(LexicalError(pos, f"Consecutive operators '{tokens[-1].value} {ident_str}' are not allowed"))
                    continue
                tokens.append(Token(TT_MOD, ident_str, line))
                continue
    
            elif self.current_char == "&":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "&":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_AND, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid character '{ident_str}'"))
                    self.advance()
                    continue
                    
            elif self.current_char == "(":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_LPAREN, ident_str, line))
                continue
                
            elif self.current_char == ")":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_RPAREN, ident_str, line))
                continue
                
            elif self.current_char == "*":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "*":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_EXP, ident_str, line))
                    continue
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_MULTIEQ, ident_str, line))
                    continue
                # Check for consecutive operators
                if self.current_char in '+-*/%':
                    errors.append(LexicalError(pos, f"Consecutive operators '{ident_str}{self.current_char}' are not allowed"))
                    self.advance()  # Consume the operator
                    continue
                # Check for valid delimiter after *
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
                # Check if previous token was an operator (catch "* +" case with whitespace)
                if len(tokens) > 0 and tokens[-1].type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD]:
                    errors.append(LexicalError(pos, f"Consecutive operators '{tokens[-1].value} {ident_str}' are not allowed"))
                    continue
                tokens.append(Token(TT_MUL, ident_str, line))
                continue
                
            elif self.current_char == ",":
                ident_str = self.current_char
                pos = self.pos.copy()
                # Check for consecutive commas
                if len(tokens) > 0 and tokens[-1].type == TT_COMMA:
                    errors.append(LexicalError(pos, f"Invalid delimiters ','"))
                    self.advance()
                    continue
                self.advance()
                tokens.append(Token(TT_COMMA, ident_str, line))
                continue
            
            # This entire block is for a token that isn't really a token.
            # The logic for escape sequences is handled *inside* the string and char
            # literal parsers. This block should be removed.
            # elif self.current_char == "\\":
            #     ...
                
            elif self.current_char == ";":
                ident_str = self.current_char
                pos = self.pos.copy()
                # Check if previous token is = (empty assignment like "seed =;")
                if len(tokens) > 0 and tokens[-1].type == '=':
                    errors.append(LexicalError(pos, f"Missing value after '=' operator"))
                    self.advance()
                    continue
                self.advance()
                tokens.append(Token(TT_SEMICOLON, ident_str, line))
                continue
                
            elif self.current_char == "[":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_LSQBR, ident_str, line))
                continue
                
            elif self.current_char == "]":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_RSQBR, ident_str, line))
                continue
                
            elif self.current_char == "{":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_BLOCK_START, ident_str, line))
                continue
                
            elif self.current_char == "}":
                ident_str = self.current_char 
                pos = self.pos.copy() 
                self.advance()
                tokens.append(Token(TT_BLOCK_END, ident_str, line))
                continue

            elif self.current_char == "|":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "|":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_OR, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid character '{ident_str}'"))
                    self.advance()
                    continue
            
            elif self.current_char == "+":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "+":
                    # Check if previous token is an identifier or integer literal (valid for ++)
                    if len(tokens) > 0 and tokens[-1].type in [TT_IDENTIFIER, TT_INTEGERLIT]:
                        ident_str += self.current_char
                        self.advance()
                        tokens.append(Token(TT_INCREMENT, ident_str, line))
                        continue
                    else:
                        # ++ not after an identifier or integer is an error
                        errors.append(LexicalError(pos, f"Consecutive operators '{ident_str}{self.current_char}' are not allowed"))
                        self.advance()  # Consume the second +
                        continue
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_PLUSEQ, ident_str, line))
                    continue
                # Check for consecutive operators
                if self.current_char is not None and self.current_char in '+-*/%':
                    errors.append(LexicalError(pos, f"Consecutive operators '{ident_str}{self.current_char}' are not allowed"))
                    self.advance()  # Consume the operator
                    continue
                # Check for valid delimiter after +
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
                # Check if previous token was an operator (catch "+ +" case with whitespace)
                if len(tokens) > 0 and tokens[-1].type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD]:
                    errors.append(LexicalError(pos, f"Consecutive operators '{tokens[-1].value} {ident_str}' are not allowed"))
                    continue
                tokens.append(Token(TT_PLUS, ident_str, line))
                continue

            elif self.current_char == "<":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    # Check for consecutive comparison operators
                    if len(tokens) > 0 and tokens[-1].type in ['>', '<', '==', '!=', '>=', '<=']:
                        errors.append(LexicalError(pos, f"Consecutive operators '{tokens[-1].value} {ident_str}' are not allowed"))
                        continue
                    tokens.append(Token(TT_LTEQ, ident_str, line))
                    continue
                # Check for consecutive comparison operators
                if len(tokens) > 0 and tokens[-1].type in ['>', '<', '==', '!=', '>=', '<=']:
                    errors.append(LexicalError(pos, f"Consecutive operators '{tokens[-1].value} {ident_str}' are not allowed"))
                    continue
                tokens.append(Token(TT_LT, ident_str, line))
                continue
            
            # =====================================================================
            # EQUALS OPERATOR: = (assignment) or == (equality comparison)
            # =====================================================================
            elif self.current_char == "=":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                
                if self.current_char == "=":  # Check for second '='
                    ident_str += self.current_char
                    self.advance()
                    
                    # Prevent '===' (invalid - GAL only uses '==' for equality)
                    if self.current_char == "=":
                        errors.append(LexicalError(pos, f"Invalid operator '==='. Use '==' for equality comparison"))
                        ident_str += self.current_char
                        self.advance()
                        continue
                    
                    # Prevent consecutive comparison operators (e.g., "< ==" or "> ==")
                    if len(tokens) > 0 and tokens[-1].type in ['>', '<', '==', '!=', '>=', '<=']:
                        errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                        continue
                    
                    # Valid '==' (equality comparison operator)
                    tokens.append(Token(TT_EQTO, ident_str, line))
                    continue
                
                # Single '=' (assignment operator)
                tokens.append(Token(TT_EQ, ident_str, line))
                continue

            elif self.current_char == ">":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    # Check for consecutive comparison operators
                    if len(tokens) > 0 and tokens[-1].type in ['>', '<', '==', '!=', '>=', '<=']:
                        errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                        continue
                    tokens.append(Token(TT_GTEQ, ident_str, line))
                    continue
                # Check for consecutive comparison operators
                if len(tokens) > 0 and tokens[-1].type in ['>', '<', '==', '!=', '>=', '<=']:
                    errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                    continue
                tokens.append(Token(TT_GT, ident_str, line))
                continue


            elif self.current_char == '\n':
                pos = self.pos.copy()
                if tokens and tokens[-1].type != TT_NL:
                    tokens.append(Token(TT_NL, "\\n", line))

                while self.current_char == '\t' or self.current_char == ' ' or self.current_char == '\n':
                    if self.current_char == '\t' or self.current_char == ' ':
                        self.advance()
                    else:
                        line += 1
                        self.advance()

                continue
                
            elif self.current_char == '\t':
                ident_str = self.current_char
                pos = self.pos.copy()
                while self.current_char == '\t':
                    self.advance()
                
            elif self.current_char == ' ':
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                while self.current_char == ' ':
                    self.advance()

            # =====================================================================
            # FORWARD SLASH: / (division), // (comment), /* */ (multi-line comment), /= (divide-assign)
            # =====================================================================
            elif self.current_char == "/":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                
                if self.current_char == "/":  # Single-line comment: // comment text
                    ident_str += self.current_char
                    self.advance()
                    # Consume all characters until end of line or file
                    while self.current_char is not None and self.current_char != "\n":
                        ident_str += self.current_char
                        self.advance()
                    # Comments are NOT added to tokens (they are skipped)
                    continue
                    
                elif self.current_char == "*":  # Multi-line comment: /* comment text */
                    ident_str += self.current_char
                    self.advance()
                    # Consume all characters until closing */
                    while self.current_char is not None:
                        # Check for closing */ sequence
                        if self.current_char == "*" and self.pos.index + 1 < len(self.source_code) and self.source_code[self.pos.index + 1] == "/":
                            ident_str += "*/"
                            self.advance()  # Skip *
                            self.advance()  # Skip /
                            break
                        else:
                            ident_str += self.current_char
                            if self.current_char == "\n":  # Track line numbers inside comment
                                line += 1
                            self.advance()
                    # Comments are NOT added to tokens (they are skipped)
                    
                    # Error if comment was never closed
                    if self.current_char is None:
                        errors.append(LexicalError(pos, f"Missing closing '*/' after '{ident_str}'"))
                        continue
                    continue    
                elif self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_DIVEQ, ident_str, line))
                    continue
                else:
                    # Check for consecutive operators
                    if self.current_char in '+-*/%':
                        errors.append(LexicalError(pos, f"invalid delimiters '{ident_str}{self.current_char}' are not allowed"))
                        self.advance()  # Consume the operator
                        continue
                    # Check for valid delimiter after /
                    if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\'  ' + '\t' + '\n'):
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                    # Check if previous token was an operator (catch "/ +" case with whitespace)
                    if len(tokens) > 0 and tokens[-1].type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD]:
                        errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                        continue
                    tokens.append(Token(TT_DIV, ident_str, line))
                    continue
            
            elif self.current_char == ".":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is not None and self.current_char in ALPHA:
                    tokens.append(Token(TT_DOT, ident_str, line))
                    continue

                elif self.current_char is not None and self.current_char in ZERODIGIT:
                    fractional_part = ""
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        if len(fractional_part + self.current_char) > 8: 
                            errors.append(LexicalError(pos, f"'{ident_str}' exceeds maximum number of decimal places"))
                            break

                        fractional_part += self.current_char
                        self.advance()
                        
                    ident_str = f"0.{fractional_part}"
                    tokens.append(Token(TT_DOUBLELIT, ident_str, line))
                    continue
                    
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()
                    continue
            
            elif self.current_char == ":":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_COLON, ident_str, line))
                continue

            # =====================================================================
            # NUMBER LITERAL PARSING: integers, doubles, scientific notation
            # Examples: 42, 3.14, 1.5e10, 2.3e-5
            # =====================================================================
            elif self.current_char in ZERODIGIT:
                dot_count = 0               # Count decimal points (max 1)
                ident_str = ""              # Build the number string
                pos = self.pos.copy()       # Save position for errors
                integer_digit_count = 0     # Count digits before decimal (max 16)
                fractional_digit_count = 0  # Count digits after decimal (max 8)
                has_e = False               # Track if scientific notation (e.g., 1e10)

                # Step 1: Read integer part (before decimal point)
                while self.current_char is not None and self.current_char in ZERODIGIT:
                    integer_digit_count += 1
                    if integer_digit_count > 16:
                        errors.append(LexicalError(pos, f"Integer part exceeds maximum of 16 digits"))
                        # Consume the rest of the invalid number
                        while self.current_char is not None and self.current_char in ZERODIGIT + ".":
                            self.advance()
                        break
                    ident_str += self.current_char
                    self.advance()

                # Step 2: Check for decimal point (converts to double/float)
                if self.current_char == "." and integer_digit_count <= 16:
                    dot_count = 1  # Mark that we found a decimal point
                    ident_str += self.current_char
                    self.advance()
                    
                    # After decimal point, must have at least one digit (e.g., "3." is invalid)
                    if self.current_char is None or self.current_char not in ZERODIGIT:
                        errors.append(LexicalError(pos, f"Invalid number '{ident_str}': decimal point must be followed by digits"))
                        continue
                    
                    # Read fractional part (digits after decimal point)
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        fractional_digit_count += 1
                        if fractional_digit_count > 8:
                            errors.append(LexicalError(pos, f"Fractional part exceeds maximum of 8 digits"))
                            # Consume the rest of the invalid number
                            while self.current_char is not None and self.current_char in ZERODIGIT:
                                self.advance()
                            break
                        ident_str += self.current_char
                        self.advance()

                # Error check: Skip if digit limits exceeded
                if integer_digit_count > 16 or fractional_digit_count > 8:
                    continue

                # Duplicate check removed (was redundant)
                if integer_digit_count > 16 or fractional_digit_count > 8:
                    continue

                # Step 3: Check for scientific notation (e.g., 1.5e10, 2.3e-5)
                # Only valid for doubles (must have decimal point)
                if self.current_char is not None and self.current_char in 'eE' and dot_count == 1:
                    has_e = True
                    ident_str += self.current_char
                    self.advance()
                    
                    # Handle optional sign after 'e' (e.g., 1.2e-5 or 1.2e+5)
                    if self.current_char in '+-':
                        ident_str += self.current_char
                        self.advance()
                    
                    # Must have digits after 'e' (e.g., "1.5e" is invalid)
                    if self.current_char is None or self.current_char not in ZERODIGIT:
                        errors.append(LexicalError(pos, f"Invalid scientific notation: 'e' must be followed by digits."))
                        continue
                    
                    # Read exponent digits
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        ident_str += self.current_char
                        self.advance()

                if dot_count == 0 and not has_e:
                    # DEBUG: Always show what we have before integer
                    print(f"DEBUG INTEGER CHECK: tokens count={len(tokens)}, integer={ident_str}")
                    if len(tokens) >= 2:
                        print(f"  Last tokens: {[(t.type, t.value) for t in tokens[-min(4, len(tokens)):]]}")
                    
                    # Check if this is after a type declaration for tree (tree only accepts doubles, not integers)
                    type_token = None
                    if len(tokens) >= 3 and tokens[-2].type == 'idf' and tokens[-1].type == '=':
                        type_token = tokens[-3].type
                        print(f"  Pattern 1 matched! type_token={type_token}")
                    elif len(tokens) >= 4 and tokens[-3].type == ':' and tokens[-2].type == 'idf' and tokens[-1].type == '=':
                        type_token = tokens[-4].type
                        print(f"  Pattern 2 matched! type_token={type_token}")
                    elif len(tokens) >= 2 and tokens[-1].type == '=' and tokens[-2].type in ['tree', 'seed', 'branch']:
                        type_token = tokens[-2].type
                        print(f"  Pattern 3 (no identifier) matched! type_token={type_token}")
                    else:
                        print(f"  No pattern matched")
                    
                    if type_token == 'tree':
                        print(f"  REJECTING integer {ident_str} for tree variable")
                        errors.append(LexicalError(pos, f"Tree variables cannot be assigned integer literals. Use double values (e.g., {ident_str}.0)"))
                        continue
                    
                    # Check for valid delimiter after integer
                    if self.current_char is not None and self.current_char not in whlnum_delim:
                        # Check if followed by letter (not underscore or digit)
                        if self.current_char in ALPHA:
                            # Peek ahead to see if it's a reserved word
                            temp_str = ''
                            temp_pos = self.pos.copy()
                            temp_char = self.current_char
                            while temp_char is not None and temp_char in ALPHANUM:
                                temp_str += temp_char
                                temp_pos.advance(temp_char)
                                temp_char = self.source_code[temp_pos.index] if temp_pos.index < len(self.source_code) else None
                            
                            # Check if it's a reserved word
                            reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', 
                                            'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', 
                                            'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'sunshine', 'frost'}
                            
                            if temp_str in reserved_words:
                                errors.append(LexicalError(pos, f"Reserved word cannot start with a number: '{ident_str}{temp_str}'"))
                            else:
                                errors.append(LexicalError(pos, f"Identifiers cannot start with a number: '{ident_str}{self.current_char}...'"))
                            
                            # Consume the rest of the invalid identifier
                            while self.current_char is not None and self.current_char in ALPHANUM:
                                self.advance()
                        elif self.current_char == '_':
                            # Check if underscore is followed by letters (reserved word or identifier)
                            temp_index = self.pos.index + 1
                            if temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHA:
                                # Peek ahead to see if it's a reserved word
                                temp_str = ''
                                while temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHANUM:
                                    temp_str += self.source_code[temp_index]
                                    temp_index += 1
                                
                                reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', 
                                                'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', 
                                                'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'sunshine', 'frost'}
                                
                                if temp_str in reserved_words:
                                    errors.append(LexicalError(pos, f"Reserved word cannot start with a number: '{ident_str}_{temp_str}'"))
                                else:
                                    errors.append(LexicalError(pos, f"Identifiers cannot start with a number: '{ident_str}_...'"))
                                
                                # Consume underscore and the rest
                                while self.current_char is not None and self.current_char in ALPHANUM:
                                    self.advance()
                            else:
                                # Underscore followed by digits - numeric separator error
                                errors.append(LexicalError(pos, f"Underscore cannot be used in numeric literals"))
                                # Consume underscore and any following digits/underscores/letters
                                while self.current_char is not None and self.current_char in ALPHANUM:
                                    self.advance()
                        else:
                            errors.append(LexicalError(pos, f"Illegal Character '{self.current_char}'"))
                            self.advance()
                        continue
                    
                    ident_str = ident_str.lstrip("0") or "0"
                    tokens.append(Token(TT_INTEGERLIT, ident_str, line))
                    continue
                    
                else:  # Float case
                    # Check for valid delimiter after double
                    if self.current_char is not None and self.current_char not in decim_delim:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                    if not has_e: # Only re-format if not scientific notation
                         parts = ident_str.split(".")
                         integer_part = parts[0].lstrip("0") or "0"
                         fractional_part = (parts[1] if len(parts) > 1 else "").rstrip("0") or "0"
                         if fractional_part == "0":
                             ident_str = f"{integer_part}.0" # Keep at least one zero
                         else:
                             ident_str = f"{integer_part}.{fractional_part}"

                    tokens.append(Token(TT_DOUBLELIT, ident_str, line))
                    continue

            # =====================================================================
            # STRING LITERAL PARSING: "hello world"
            # Supports escape sequences: \n (newline), \t (tab), \{ \} (literal braces)
            # =====================================================================
            elif self.current_char == '"':
                string = ''              # Full string including quotes
                pos = self.pos.copy()    # Save position for error reporting
                escape_character = False # Track if we're processing an escape sequence
                string += self.current_char  # Include opening quote
                self.advance()

                # Supported escape sequences
                escape_characters = {
                    'n': '\n',   # Newline
                    't': '\t',   # Tab
                    '{': '\\{',  # Literal left brace
                    '}': '\\}'   # Literal right brace
                }

                # Read until closing quote (or end of file)
                while self.current_char is not None and (self.current_char != '"' or escape_character):
                    if escape_character:
                        # Process escape sequence (e.g., \n becomes newline)
                        string += escape_characters.get(self.current_char, self.current_char)
                        escape_character = False
                    else:
                        if self.current_char == '\\':
                            escape_character = True
                        elif self.current_char == '\n':
                            break
                        else:
                            string += self.current_char
                    self.advance()

                if self.current_char == '"':
                    string += self.current_char
                    self.advance()

                else:
                    errors.append(LexicalError(pos, f"Missing closing '\"' after '{string}'"))
                    continue

                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after string literal '{string}'"))
                    continue
            
                # Check if this is after a type declaration 
                # Pattern 1: tree r = "314"  ->  tokens[-3]='tree', tokens[-2]='idf', tokens[-1]='='
                # Pattern 2: tree: r = "314" ->  tokens[-4]='tree', tokens[-3]=':', tokens[-2]='idf', tokens[-1]='='
                # Pattern 3: tree = "314"    ->  tokens[-2]='tree', tokens[-1]='=' (no identifier, direct assignment)
                
                type_token = None
                if len(tokens) >= 3 and tokens[-2].type == 'idf' and tokens[-1].type == '=':
                    type_token = tokens[-3].type
                elif len(tokens) >= 4 and tokens[-3].type == ':' and tokens[-2].type == 'idf' and tokens[-1].type == '=':
                    type_token = tokens[-4].type
                elif len(tokens) >= 2 and tokens[-1].type == '=' and tokens[-2].type in ['tree', 'seed', 'branch']:
                    type_token = tokens[-2].type
                
                if type_token:
                    if type_token == 'branch':
                        errors.append(LexicalError(pos, f"Branch variables cannot be assigned string literals. Use 'sunshine' (true) or 'frost' (false)"))
                        continue
                    elif type_token == 'seed':
                        errors.append(LexicalError(pos, f"Seed variables cannot be assigned string literals. Use integer values"))
                        continue
                    elif type_token == 'tree':
                        errors.append(LexicalError(pos, f"Tree variables cannot be assigned string literals. Use double values"))
                        continue
            
                # Check if string content (without quotes) is purely numeric
                string_content = string[1:-1] if len(string) >= 2 else ""  # Remove quotes
                # Check if it's a number-like string (only digits, optional decimal point, optional negative sign)
                if string_content and all(c in '0123456789.-+' for c in string_content):
                    # Further check if it looks like a valid number format
                    try:
                        float(string_content)  # If this succeeds, it's a numeric string
                        errors.append(LexicalError(pos, f"String literals cannot contain only numeric values. Found: {string}"))
                        continue
                    except ValueError:
                        pass  # Not a valid number, allow it
                
                # Escape newlines in token value for display
                string = string.replace('\n', '\\n')
                tokens.append(Token(TT_STRINGLIT, string, line))
                continue
    
            # =====================================================================
            # CHARACTER LITERAL PARSING: 'a', '\n', '\t'
            # Single character enclosed in single quotes
            # =====================================================================
            elif self.current_char == "'":
                string = ''          # Full text including quotes (for display)
                char = ''            # Actual character value
                pos = self.pos.copy()
                string += self.current_char  # Include opening quote
                self.advance()
                has_error = False    # Track if an error was already reported

                # Skip leading whitespace
                while self.current_char is not None and self.current_char in ' \t':
                    string += self.current_char
                    self.advance()

                # Read until closing quote (or end of file/line)
                while self.current_char is not None and self.current_char != "'":
                    if self.current_char == '\n':  # Newline breaks character literal
                        break
                    elif self.current_char == '\\':  # Escape sequence
                        # Handle escape sequences for characters
                        string += self.current_char
                        self.advance()
                        if self.current_char is None:
                            break # Will be caught as a missing closing quote
                        
                        # Only allow valid escape sequences
                        if self.current_char in "'\\nt": 
                            char += f"\\{self.current_char}"
                            string += self.current_char
                        else:
                            # Invalid escape sequence - report error
                            errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}' in character literal"))
                            has_error = True
                            # Consume rest of char literal to avoid cascading errors
                            while self.current_char is not None and self.current_char != "'":
                                self.advance()
                            if self.current_char == "'":
                                self.advance()
                            break
                    else:
                        string += self.current_char
                        char += self.current_char
                    self.advance()
                
                # Skip trailing whitespace before closing quote
                while len(char) > 0 and char[-1] in ' \t':
                    char = char[:-1]

                # Skip further processing if we already reported an error
                if has_error:
                    continue

                if self.current_char == "'":
                    string += self.current_char
                    self.advance()
                    
                else:
                    errors.append(LexicalError(pos, f"Missing closing '\'' after '{string}'"))
                    continue

                # Check char length (e.g., 'a' is 1, '\n' is 2 but counts as 1)
                # This logic is simple, a proper check would parse the 'char' string
                if len(char) > 1 and not (len(char) == 2 and char.startswith('\\')):
                    errors.append(LexicalError(pos, f"Character literal '{string}' exceeds maximum length of 1 character."))
                    continue
                elif len(char) == 0:
                     errors.append(LexicalError(pos, f"Empty character literal '{string}'."))
                     continue


                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{string}'"))
                    continue

                # Check if this is after a type declaration 
                type_token = None
                if len(tokens) >= 3 and tokens[-2].type == 'idf' and tokens[-1].type == '=':
                    type_token = tokens[-3].type
                elif len(tokens) >= 4 and tokens[-3].type == ':' and tokens[-2].type == 'idf' and tokens[-1].type == '=':
                    type_token = tokens[-4].type
                elif len(tokens) >= 2 and tokens[-1].type == '=' and tokens[-2].type in ['tree', 'seed', 'branch']:
                    type_token = tokens[-2].type
                
                if type_token:
                    if type_token == 'branch':
                        errors.append(LexicalError(pos, f"Branch variables cannot be assigned character literals. Use 'sunshine' (true) or 'frost' (false)"))
                        continue
                    elif type_token == 'seed':
                        errors.append(LexicalError(pos, f"Seed variables cannot be assigned character literals. Use integer values"))
                        continue
                    elif type_token == 'tree':
                        errors.append(LexicalError(pos, f"Tree variables cannot be assigned character literals. Use double values"))
                        continue

                tokens.append(Token(TT_CHARLIT, string, line))
                continue

            else:
                pos = self.pos.copy()
                char = self.current_char
                
                # Special handling for underscore followed by alphanumeric
                if char == '_':
                    self.advance()
                    # Check if followed by letters (reserved word or identifier)
                    if self.current_char is not None and self.current_char in ALPHA:
                        # Peek ahead to see if it's a reserved word
                        temp_str = ''
                        temp_index = self.pos.index
                        while temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHANUM:
                            temp_str += self.source_code[temp_index]
                            temp_index += 1
                        
                        reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', 
                                        'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', 
                                        'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'sunshine', 'frost'}
                        
                        if temp_str in reserved_words:
                            errors.append(LexicalError(pos, f"Reserved word cannot start with a symbol: '_{temp_str}'"))
                        else:
                            errors.append(LexicalError(pos, f"Identifiers cannot start with a symbol: '_...'"))
                        
                        # Consume the rest
                        while self.current_char is not None and self.current_char in ALPHANUM:
                            self.advance()
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Illegal Character '{char}'"))
                        continue
                else:
                    self.advance()
                    errors.append(LexicalError(pos, f"Illegal Character '" + char + "'"))
                    continue
                
        # End of file reached - add EOF token
        if self.current_char is None:
            tokens.append(Token(TT_EOF, "", line))
        
        return tokens, errors  # Return tuple: (list of tokens, list of errors)

# ============================================================================
# HELPER FUNCTIONS - Public interface for using the lexer
# ============================================================================

def run(source_code):
    """
    Legacy function - runs lexer and returns tokens and errors.
    
    Args:
        source_code (str): GAL source code to tokenize
    
    Returns:
        tuple: (tokens, errors) where both are lists
    """
    lexer = Lexer(source_code)
    tokens, error = lexer.make_tokens()
    return tokens, error

def lex(source_code):
    """
    Main entry point for lexical analysis (used by server.py).
    Tokenizes source code and converts errors to strings.
    
    Args:
        source_code (str): GAL source code to tokenize
    
    Returns:
        tuple: (tokens, str_errors) where:
            - tokens: list of Token objects
            - str_errors: list of error messages as strings
    """
    lexer = Lexer(source_code)
    tokens, errors = lexer.make_tokens()
    
    # Convert LexicalError objects to string messages
    str_errors = []
    for e in errors:
        try:
            if hasattr(e, 'as_string') and callable(getattr(e, 'as_string')):
                str_errors.append(e.as_string())
            else:
                str_errors.append(str(e))
        except Exception:
            str_errors.append(str(e))
    return tokens, str_errors
