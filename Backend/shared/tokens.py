

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
TT_RW_VINE        = 'vine'      # String data type

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
TT_EXPEQ = '**='            # Exponent and assign operator (x **= 2 → x = x ** 2)
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
TT_SINGLE_AND = '&'             # Invalid single ampersand
TT_SINGLE_OR = '|'              # Invalid single pipe
TT_NOT = '!'                    # Logical NOT operator
TT_INCREMENT = '++'             # Increment operator (e.g., x++)
TT_DECREMENT = '--'             # Decrement operator (e.g., x--)
TT_LSQBR = '['                  # Left square bracket (array indexing)
TT_RSQBR = ']'                  # Right square bracket
TT_NEGATIVE = '~'               # Unary negation operator
TT_MEMBER = 'member'            # Member token for struct access
TT_INTEGERLIT = 'intlit'        # Integer literal token (e.g., 42, 100)
TT_DOUBLELIT = 'dbllit'         # Double/float literal token (e.g., 3.14, 2.5)
TT_STRINGLIT = 'stringlit'      # String literal token (e.g., "hello")
TT_CHARLIT = 'chrlit'           # Character literal token (e.g., 'a')
TT_BOOLLIT_TRUE = 'sunshine'    # Boolean true literal
TT_BOOLLIT_FALSE = 'frost'      # Boolean false literal
TT_STRCTACCESS = '.'            # Struct member access operator
TT_NL = '\n'                    # Newline token
TT_DOT = '.'                    # Dot operator (struct access)


# ============================================================================
# TOKEN CLASS - Represents a single token (lexeme)
# ============================================================================
class Token:
    """Represents a token with type, value, line number, and column number"""

    def __init__(self, type_, value=None, line=1, col=0):
        self.type = type_    # Token type (e.g., TT_IDENTIFIER, TT_INTEGERLIT)
        self.value = value   # Token text/value (e.g., "myVar", "42")
        self.line = line     # Line number where token appears
        self.col = col       # Column number where token starts (0-based)


# ============================================================================
# TOKEN TYPE DESCRIPTIONS - Maps token types to human-readable descriptions
# ============================================================================
def get_token_description(token_type: str, value: str = '') -> str:
    """Returns a descriptive name for each token type"""
    # Handle negative literals: value starts with ~ but token type is intlit/dbllit
    if token_type == 'intlit' and isinstance(value, str) and value.startswith('~'):
        return 'negative integer'
    if token_type == 'dbllit' and isinstance(value, str) and value.startswith('~'):
        return 'negative float'

    descriptions = {
        # Reserved Words - I/O
        'water': 'Input Function',
        'plant': 'Output Function',

        # Reserved Words - Data Types
        'seed': 'Integer Type',
        'leaf': 'Character Type',
        'branch': 't/f',
        'tree': 'Float Type',
        'vine': 'String Type',
        'empty': 'Void Type',

        # Reserved Words - Control Flow
        'spring': 'If Statement',
        'wither': 'Else Statement',
        'bud': 'Else-If Statement',
        'harvest': 'Switch Statement',
        'variety': 'Case Label',
        'soil': 'Default Case',

        # Reserved Words - Loops
        'grow': 'While Loop',
        'cultivate': 'For Loop',
        'tend': 'Do-While Loop',
        'prune': 'Break Statement',
        'skip': 'Continue Statement',

        # Reserved Words - Functions
        'root': 'Main Function',
        'pollinate': 'Function Declaration',
        'reclaim': 'Return Statement',

        # Reserved Words - Other
        'fertile': 'Constant Declaration',
        'bundle': 'Struct Definition',

        # Identifiers and Literals
        'id': 'Identifier',
        'intlit': 'Integer Literal',
        'dbllit': 'double Literal',
        'stringlit': 'string',
        'chrlit': 'Character',
        'sunshine': 'Boolean True',
        'frost': 'Boolean False',

        # Arithmetic Operators
        '+': 'Plus Operator',
        '-': 'Minus Operator',
        '*': 'Multiply Operator',
        '/': 'Divide Operator',
        '%': 'Modulo Operator',
        '**': 'Power Operator',
        '~': 'Negate Operator',
        '++': 'Increment Operator',
        '--': 'Decrement Operator',

        # Assignment Operators
        '=': 'Assign Operator',
        '+=': 'Add-Assign Operator',
        '-=': 'Sub-Assign Operator',
        '*=': 'Mul-Assign Operator',
        '/=': 'Div-Assign Operator',
        '%=': 'Mod-Assign Operator',

        # Comparison Operators
        '==': 'Equal Operator',
        '!=': 'Not-Equal Operator',
        '<': 'Less-Than Operator',
        '>': 'Greater-Than Operator',
        '<=': 'Less-Equal Operator',
        '>=': 'Greater-Equal Operator',

        # Logical Operators
        '&&': 'AND Operator',
        '&': 'Invalid Single-Ampersand',
        '||': 'OR Operator',
        '|': 'Invalid Single-Pipe',
        '!': 'NOT Operator',

        # Delimiters and Punctuation
        '(': 'Left Parenthesis',
        ')': 'Right Parenthesis',
        '{': 'Left Brace',
        '}': 'Right Brace',
        '[': 'Left Bracket',
        ']': 'Right Bracket',
        ';': 'Semicolon',
        ',': 'Comma',
        ':': 'Colon',
        '.': 'Dot Operator',
        '`': 'Concatenation Operator',

        # Special
        'member': 'Struct Member',
        'EOF': 'End of File',
        '\n': 'Newline'
    }

    return descriptions.get(token_type, 'Unknown Token')
