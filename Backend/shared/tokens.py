

TT_RW_WATER       = 'water'
TT_RW_PLANT       = 'plant'
TT_RW_SEED        = 'seed'
TT_RW_LEAF        = 'leaf'
TT_RW_BRANCH      = 'branch'
TT_RW_TREE        = 'tree'
TT_RW_SPRING      = 'spring'
TT_RW_WITHER      = 'wither'
TT_RW_BUD         = 'bud'
TT_RW_HARVEST     = 'harvest'
TT_RW_GROW        = 'grow'
TT_RW_CULTIVATE   = 'cultivate'
TT_RW_TEND        = 'tend'
TT_RW_EMPTY       = 'empty'
TT_RW_PRUNE       = 'prune'
TT_RW_SKIP        = 'skip'
TT_RW_RECLAIM     = 'reclaim'
TT_RW_ROOT        = 'root'
TT_RW_POLLINATE   = 'pollinate'
TT_RW_VARIETY     = 'variety'
TT_RW_FERTILE     = 'fertile'
TT_RW_SOIL        = 'soil'
TT_RW_BUNDLE      = 'bundle'
TT_RW_VINE        = 'vine'

TT_IDENTIFIER = 'id'
TT_PLUS = '+'
TT_MINUS = '-'
TT_MUL = '*'
TT_DIV = '/'
TT_MOD = '%'
TT_EXP = '**'
TT_EQ = '='
TT_EQTO = '=='
TT_PLUSEQ = '+='
TT_MINUSEQ = '-='
TT_MULTIEQ = '*='
TT_DIVEQ = '/='
TT_MODEQ = '%='
TT_EXPEQ = '**='
TT_CONCAT = '`'
TT_LPAREN = '('
TT_RPAREN = ')'
TT_SEMICOLON = ';'
TT_COMMA = ','
TT_COLON = ':'
TT_BLOCK_START = '{'
TT_BLOCK_END = '}'
TT_LT = '<'
TT_GT = '>'
TT_LTEQ = '<='
TT_GTEQ = '>='
TT_NOTEQ = '!='
TT_EOF = 'EOF'
TT_AND = '&&'
TT_OR = '||'
TT_SINGLE_AND = '&'
TT_SINGLE_OR = '|'
TT_NOT = '!'
TT_INCREMENT = '++'
TT_DECREMENT = '--'
TT_LSQBR = '['
TT_RSQBR = ']'
TT_NEGATIVE = '~'
TT_MEMBER = 'member'
TT_INTEGERLIT = 'intlit'
TT_DOUBLELIT = 'dbllit'
TT_STRINGLIT = 'stringlit'
TT_CHARLIT = 'chrlit'
TT_BOOLLIT_TRUE = 'sunshine'
TT_BOOLLIT_FALSE = 'frost'
TT_STRCTACCESS = '.'
TT_NL = '\n'
TT_DOT = '.'


class Token:

    def __init__(self, type_, value=None, line=1, col=0):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col


def get_token_description(token_type: str, value: str = '') -> str:
    if token_type == 'intlit' and isinstance(value, str) and value.startswith('~'):
        return 'negative integer'
    if token_type == 'dbllit' and isinstance(value, str) and value.startswith('~'):
        return 'negative float'

    descriptions = {
        'water': 'Input Function',
        'plant': 'Output Function',

        'seed': 'Integer Type',
        'leaf': 'Character Type',
        'branch': 't/f',
        'tree': 'Float Type',
        'vine': 'String Type',
        'empty': 'Void Type',

        'spring': 'If Statement',
        'wither': 'Else Statement',
        'bud': 'Else-If Statement',
        'harvest': 'Switch Statement',
        'variety': 'Case Label',
        'soil': 'Default Case',

        'grow': 'While Loop',
        'cultivate': 'For Loop',
        'tend': 'Do-While Loop',
        'prune': 'Break Statement',
        'skip': 'Continue Statement',

        'root': 'Main Function',
        'pollinate': 'Function Declaration',
        'reclaim': 'Return Statement',

        'fertile': 'Constant Declaration',
        'bundle': 'Struct Definition',

        'id': 'Identifier',
        'intlit': 'Integer Literal',
        'dbllit': 'double Literal',
        'stringlit': 'string',
        'chrlit': 'Character',
        'sunshine': 'Boolean True',
        'frost': 'Boolean False',

        '+': 'Plus Operator',
        '-': 'Minus Operator',
        '*': 'Multiply Operator',
        '/': 'Divide Operator',
        '%': 'Modulo Operator',
        '**': 'Power Operator',
        '~': 'Negate Operator',
        '++': 'Increment Operator',
        '--': 'Decrement Operator',

        '=': 'Assign Operator',
        '+=': 'Add-Assign Operator',
        '-=': 'Sub-Assign Operator',
        '*=': 'Mul-Assign Operator',
        '/=': 'Div-Assign Operator',
        '%=': 'Mod-Assign Operator',

        '==': 'Equal Operator',
        '!=': 'Not-Equal Operator',
        '<': 'Less-Than Operator',
        '>': 'Greater-Than Operator',
        '<=': 'Less-Equal Operator',
        '>=': 'Greater-Equal Operator',

        '&&': 'AND Operator',
        '&': 'Invalid Single-Ampersand',
        '||': 'OR Operator',
        '|': 'Invalid Single-Pipe',
        '!': 'NOT Operator',

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

        'member': 'Struct Member',
        'EOF': 'End of File',
        '\n': 'Newline'
    }

    return descriptions.get(token_type, 'Unknown Token')
