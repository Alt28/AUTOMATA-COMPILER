
"""Token constants and Token class used by every compiler stage.

The lexer creates Token(type, value, line, col). The parser and later stages
mostly compare token.type values against these constants.
"""


# --- Reserved Words (Keywords) ---
# AUTO: Sets `TT_RW_WATER`.
TT_RW_WATER       = 'water'     # Input function - reads user input
# AUTO: Sets `TT_RW_PLANT`.
TT_RW_PLANT       = 'plant'     # Output function - prints to console
# AUTO: Sets `TT_RW_SEED`.
TT_RW_SEED        = 'seed'      # Data Type - integer (int)
# AUTO: Sets `TT_RW_LEAF`.
TT_RW_LEAF        = 'leaf'      # Data Type - character (char)
# AUTO: Sets `TT_RW_BRANCH`.
TT_RW_BRANCH      = 'branch'    # Data Type - boolean (true/false)
# AUTO: Sets `TT_RW_TREE`.
TT_RW_TREE        = 'tree'      # Data Type - double/float
# AUTO: Sets `TT_RW_SPRING`.
TT_RW_SPRING      = 'spring'    # Conditional statement - if
# AUTO: Sets `TT_RW_WITHER`.
TT_RW_WITHER      = 'wither'    # Conditional statement - else
# AUTO: Sets `TT_RW_BUD`.
TT_RW_BUD         = 'bud'       # Conditional statement - else-if
# AUTO: Sets `TT_RW_HARVEST`.
TT_RW_HARVEST     = 'harvest'   # Switch statement
# AUTO: Sets `TT_RW_GROW`.
TT_RW_GROW        = 'grow'      # Loop - while
# AUTO: Sets `TT_RW_CULTIVATE`.
TT_RW_CULTIVATE   = 'cultivate' # Loop - for
# AUTO: Sets `TT_RW_TEND`.
TT_RW_TEND        = 'tend'      # Loop - do-while
# AUTO: Sets `TT_RW_EMPTY`.
TT_RW_EMPTY       = 'empty'     # Void return type
# AUTO: Sets `TT_RW_PRUNE`.
TT_RW_PRUNE       = 'prune'     # Break statement - exit loop
# AUTO: Sets `TT_RW_SKIP`.
TT_RW_SKIP        = 'skip'      # Continue statement - skip to next iteration
# AUTO: Sets `TT_RW_RECLAIM`.
TT_RW_RECLAIM     = 'reclaim'   # Return statement - return from function
# AUTO: Sets `TT_RW_ROOT`.
TT_RW_ROOT        = 'root'      # Main function entry point
# AUTO: Sets `TT_RW_POLLINATE`.
TT_RW_POLLINATE   = 'pollinate' # Function declaration
# AUTO: Sets `TT_RW_VARIETY`.
TT_RW_VARIETY     = 'variety'   # Case label in switch statement
# AUTO: Sets `TT_RW_FERTILE`.
TT_RW_FERTILE     = 'fertile'   # Constant declaration
# AUTO: Sets `TT_RW_SOIL`.
TT_RW_SOIL        = 'soil'      # Default case in switch statement
# AUTO: Sets `TT_RW_BUNDLE`.
TT_RW_BUNDLE      = 'bundle'    # Struct definition
# AUTO: Sets `TT_RW_VINE`.
TT_RW_VINE        = 'vine'      # String data type

# --- Operators & Symbols ---
# AUTO: Sets `TT_IDENTIFIER`.
TT_IDENTIFIER = 'id'        # Variable/function names (e.g., myVar, calcTotal)
# AUTO: Sets `TT_PLUS`.
TT_PLUS = '+'               # Addition operator
# AUTO: Sets `TT_MINUS`.
TT_MINUS = '-'              # Subtraction operator
# AUTO: Sets `TT_MUL`.
TT_MUL = '*'                # Multiplication operator
# AUTO: Sets `TT_DIV`.
TT_DIV = '/'                # Division operator
# AUTO: Sets `TT_MOD`.
TT_MOD = '%'                # Modulo operator (remainder)
# AUTO: Sets `TT_EXP`.
TT_EXP = '**'               # Exponentiation operator (power)
# AUTO: Sets `TT_EQ`.
TT_EQ = '='                 # Assignment operator
# AUTO: Executes this statement.
TT_EQTO = '=='              # Equality comparison operator
# AUTO: Adds into `TT_PLUSEQ = '`.
TT_PLUSEQ = '+='            # Add and assign operator
# AUTO: Subtracts from `TT_MINUSEQ = '`.
TT_MINUSEQ = '-='           # Subtract and assign operator
# AUTO: Multiplies into `TT_MULTIEQ = '`.
TT_MULTIEQ = '*='           # Multiply and assign operator
# AUTO: Divides into `TT_DIVEQ = '`.
TT_DIVEQ = '/='             # Divide and assign operator
# AUTO: Sets `TT_MODEQ`.
TT_MODEQ = '%='             # Modulo and assign operator
# AUTO: Multiplies into `TT_EXPEQ = '*`.
TT_EXPEQ = '**='            # Exponent and assign operator (x **= 2 → x = x ** 2)
# AUTO: Sets `TT_CONCAT`.
TT_CONCAT = '`'             # String concatenation operator
# AUTO: Sets `TT_LPAREN`.
TT_LPAREN = '('             # Left parenthesis
# AUTO: Sets `TT_RPAREN`.
TT_RPAREN = ')'             # Right parenthesis
# AUTO: Sets `TT_SEMICOLON`.
TT_SEMICOLON = ';'          # Statement terminator
# AUTO: Sets `TT_COMMA`.
TT_COMMA = ','              # Separator (function args, array elements)
# AUTO: Sets `TT_COLON`.
TT_COLON = ':'              # Colon (used in switch cases)
# AUTO: Sets `TT_BLOCK_START`.
TT_BLOCK_START = '{'        # Block start (scope begin)
# AUTO: Sets `TT_BLOCK_END`.
TT_BLOCK_END = '}'          # Block end (scope close)
# AUTO: Sets `TT_LT`.
TT_LT = '<'                 # Less than comparison
# AUTO: Sets `TT_GT`.
TT_GT = '>'                 # Greater than comparison
# AUTO: Executes this statement.
TT_LTEQ = '<='              # Less than or equal comparison
# AUTO: Executes this statement.
TT_GTEQ = '>='              # Greater than or equal comparison
# AUTO: Executes this statement.
TT_NOTEQ = '!='             # Not equal comparison
# AUTO: Sets `TT_EOF`.
TT_EOF = 'EOF'                  # End of file marker
# AUTO: Sets `TT_AND`.
TT_AND = '&&'                   # Logical AND operator
# AUTO: Sets `TT_OR`.
TT_OR = '||'                    # Logical OR operator
# AUTO: Sets `TT_SINGLE_AND`.
TT_SINGLE_AND = '&'             # Invalid single ampersand
# AUTO: Sets `TT_SINGLE_OR`.
TT_SINGLE_OR = '|'              # Invalid single pipe
# AUTO: Sets `TT_NOT`.
TT_NOT = '!'                    # Logical NOT operator
# AUTO: Sets `TT_INCREMENT`.
TT_INCREMENT = '++'             # Increment operator (e.g., x++)
# AUTO: Sets `TT_DECREMENT`.
TT_DECREMENT = '--'             # Decrement operator (e.g., x--)
# AUTO: Sets `TT_LSQBR`.
TT_LSQBR = '['                  # Left square bracket (array indexing)
# AUTO: Sets `TT_RSQBR`.
TT_RSQBR = ']'                  # Right square bracket
# AUTO: Sets `TT_NEGATIVE`.
TT_NEGATIVE = '~'               # Unary negation operator
# AUTO: Sets `TT_MEMBER`.
TT_MEMBER = 'member'            # Member token for struct access
# AUTO: Sets `TT_INTEGERLIT`.
TT_INTEGERLIT = 'intlit'        # Integer literal token (e.g., 42, 100)
# AUTO: Sets `TT_DOUBLELIT`.
TT_DOUBLELIT = 'dblit'         # Double/float literal token (e.g., 3.14, 2.5)
# AUTO: Sets `TT_STRINGLIT`.
TT_STRINGLIT = 'stringlit'      # String literal token (e.g., "hello")
# AUTO: Sets `TT_CHARLIT`.
TT_CHARLIT = 'chrlit'           # Character literal token (e.g., 'a')
# AUTO: Sets `TT_BOOLLIT_TRUE`.
TT_BOOLLIT_TRUE = 'sunshine'    # Boolean true literal
# AUTO: Sets `TT_BOOLLIT_FALSE`.
TT_BOOLLIT_FALSE = 'frost'      # Boolean false literal
# AUTO: Sets `TT_STRCTACCESS`.
TT_STRCTACCESS = '.'            # Struct member access operator
# AUTO: Sets `TT_NL`.
TT_NL = '\n'                    # Newline token
# AUTO: Sets `TT_DOT`.
TT_DOT = '.'                    # Dot operator (struct access)
# AUTO: Sets `TT_COMMENT`.
TT_COMMENT = 'comment'          # Single-line comment (//...)
# AUTO: Sets `TT_MCOMMENT`.
TT_MCOMMENT = 'mcommentlit'     # Multi-line comment (/*...*/)


# ============================================================================
# TOKEN CLASS - Represents a single token (lexeme)
# ============================================================================
# AUTO: Defines class `Token`.
class Token:
    """Represents a token with type, value, line number, and column number"""

    # AUTO: Defines function `__init__`.
    def __init__(self, type_, value=None, line=1, col=0):
        # LINE: token type is what parser compares, like id/intlit/seed.
        self.type = type_    # Token type (e.g., TT_IDENTIFIER, TT_INTEGERLIT)
        # LINE: token value is the actual lexeme text, like x or 10.
        self.value = value   # Token text/value (e.g., "myVar", "42")
        # LINE: line records where the token starts in source code.
        self.line = line     # Line number where token appears
        # LINE: col records the starting column for error messages.
        self.col = col       # Column number where token starts (0-based)


# ============================================================================
# TOKEN TYPE DESCRIPTIONS - Maps token types to human-readable descriptions
# ============================================================================
# AUTO: Defines function `get_token_description`.
def get_token_description(token_type: str, value: str = '') -> str:
    """Returns a descriptive name for each token type"""
    # Handle negative literals: value starts with ~ but token type is intlit/dbllit
    # LINE: Special description for negative integer literals.
    if token_type == 'intlit' and isinstance(value, str) and value.startswith('~'):
        # AUTO: Returns this result to the caller.
        return 'negative integer'
    # LINE: Special description for negative double literals.
    if token_type == 'dblit' and isinstance(value, str) and value.startswith('~'):
        # AUTO: Returns this result to the caller.
        return 'negative float'

    # LINE: Map token types to human-readable lexeme table labels.
    descriptions = {
        # Reserved Words - I/O
        # AUTO: Executes this statement.
        'water': 'Input Function',
        # AUTO: Executes this statement.
        'plant': 'Output Function',

        # Reserved Words - Data Types
        # AUTO: Executes this statement.
        'seed': 'Integer Type',
        # AUTO: Executes this statement.
        'leaf': 'Character Type',
        # AUTO: Executes this statement.
        'branch': 't/f',
        # AUTO: Executes this statement.
        'tree': 'Float Type',
        # AUTO: Executes this statement.
        'vine': 'String Type',
        # AUTO: Executes this statement.
        'empty': 'Void Type',

        # Reserved Words - Control Flow
        # AUTO: Executes this statement.
        'spring': 'If Statement',
        # AUTO: Executes this statement.
        'wither': 'Else Statement',
        # AUTO: Executes this statement.
        'bud': 'Else-If Statement',
        # AUTO: Executes this statement.
        'harvest': 'Switch Statement',
        # AUTO: Executes this statement.
        'variety': 'Case Label',
        # AUTO: Executes this statement.
        'soil': 'Default Case',

        # Reserved Words - Loops
        # AUTO: Executes this statement.
        'grow': 'While Loop',
        # AUTO: Executes this statement.
        'cultivate': 'For Loop',
        # AUTO: Executes this statement.
        'tend': 'Do-While Loop',
        # AUTO: Executes this statement.
        'prune': 'Break Statement',
        # AUTO: Executes this statement.
        'skip': 'Continue Statement',

        # Reserved Words - Functions
        # AUTO: Executes this statement.
        'root': 'Main Function',
        # AUTO: Executes this statement.
        'pollinate': 'Function Declaration',
        # AUTO: Executes this statement.
        'reclaim': 'Return Statement',

        # Reserved Words - Other
        # AUTO: Executes this statement.
        'fertile': 'Constant Declaration',
        # AUTO: Executes this statement.
        'bundle': 'Struct Definition',

        # Identifiers and Literals
        # AUTO: Executes this statement.
        'id': 'Identifier',
        # AUTO: Executes this statement.
        'intlit': 'Integer Literal',
        # AUTO: Executes this statement.
        'dblit': 'double Literal',
        # AUTO: Executes this statement.
        'stringlit': 'string',
        # AUTO: Executes this statement.
        'chrlit': 'Character',
        # AUTO: Executes this statement.
        'sunshine': 'Boolean True',
        # AUTO: Executes this statement.
        'frost': 'Boolean False',

        # Arithmetic Operators
        # AUTO: Executes this statement.
        '+': 'Plus Operator',
        # AUTO: Executes this statement.
        '-': 'Minus Operator',
        # AUTO: Executes this statement.
        '*': 'Multiply Operator',
        # AUTO: Executes this statement.
        '/': 'Divide Operator',
        # AUTO: Executes this statement.
        '%': 'Modulo Operator',
        # AUTO: Executes this statement.
        '**': 'Power Operator',
        # AUTO: Executes this statement.
        '~': 'Negate Operator',
        # AUTO: Executes this statement.
        '++': 'Increment Operator',
        # AUTO: Executes this statement.
        '--': 'Decrement Operator',

        # Assignment Operators
        # AUTO: Sets `'`.
        '=': 'Assign Operator',
        # AUTO: Adds into `'`.
        '+=': 'Add-Assign Operator',
        # AUTO: Subtracts from `'`.
        '-=': 'Sub-Assign Operator',
        # AUTO: Multiplies into `'`.
        '*=': 'Mul-Assign Operator',
        # AUTO: Divides into `'`.
        '/=': 'Div-Assign Operator',
        # AUTO: Sets `'%`.
        '%=': 'Mod-Assign Operator',

        # Comparison Operators
        # AUTO: Executes this statement.
        '==': 'Equal Operator',
        # AUTO: Executes this statement.
        '!=': 'Not-Equal Operator',
        # AUTO: Executes this statement.
        '<': 'Less-Than Operator',
        # AUTO: Executes this statement.
        '>': 'Greater-Than Operator',
        # AUTO: Executes this statement.
        '<=': 'Less-Equal Operator',
        # AUTO: Executes this statement.
        '>=': 'Greater-Equal Operator',

        # Logical Operators
        # AUTO: Executes this statement.
        '&&': 'AND Operator',
        # AUTO: Executes this statement.
        '&': 'Invalid Single-Ampersand',
        # AUTO: Executes this statement.
        '||': 'OR Operator',
        # AUTO: Executes this statement.
        '|': 'Invalid Single-Pipe',
        # AUTO: Executes this statement.
        '!': 'NOT Operator',

        # Delimiters and Punctuation
        # AUTO: Executes this statement.
        '(': 'Left Parenthesis',
        # AUTO: Executes this statement.
        ')': 'Right Parenthesis',
        # AUTO: Executes this statement.
        '{': 'Left Brace',
        # AUTO: Executes this statement.
        '}': 'Right Brace',
        # AUTO: Executes this statement.
        '[': 'Left Bracket',
        # AUTO: Executes this statement.
        ']': 'Right Bracket',
        # AUTO: Executes this statement.
        ';': 'Semicolon',
        # AUTO: Executes this statement.
        ',': 'Comma',
        # AUTO: Executes this statement.
        ':': 'Colon',
        # AUTO: Executes this statement.
        '.': 'Dot Operator',
        # AUTO: Executes this statement.
        '`': 'Concatenation Operator',

        # Special
        # AUTO: Executes this statement.
        'member': 'Struct Member',
        # AUTO: Executes this statement.
        'EOF': 'End of File',
        # AUTO: Executes this statement.
        '\n': 'Newline',
        # AUTO: Executes this statement.
        'comment': 'comment',
        # AUTO: Executes this statement.
        'mcommentlit': 'multicomment',
    # AUTO: Closes the current grouped code/data.
    }

    # AUTO: Returns this result to the caller.
    return descriptions.get(token_type, 'Unknown Token')
