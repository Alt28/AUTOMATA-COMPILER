class LexerError(Exception):
    """Custom exception for lexical errors."""
    def __init__(self, message, line, column):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return f"Lexical Error at line {self.line}, column {self.column}: {self.message}"

# --- Token Types (GrowALanguage) ---

# Data Types
TT_SEED = 'seed'      # int [cite: 205, 1048]
TT_TREE = 'tree'      # double [cite: 207, 1048]
TT_BRANCH = 'branch'  # boolean [cite: 211, 1048]
TT_LEAF = 'leaf'      # char [cite: 209, 1048]
TT_EMPTY = 'empty'    # void [cite: 797, 1056]

# I/O
TT_WATER = 'water'    # input [cite: 855, 1048]
TT_PLANT = 'plant'    # output [cite: 856, 1048]

# Control Flow - Conditionals
TT_SPRING = 'spring'  # if [cite: 612, 1048]
TT_BUD = 'bud'        # else-if [cite: 613, 1048]
TT_WITHER = 'wither'  # else [cite: 614, 1048]

# Control Flow - Switch
TT_HARVEST = 'harvest' # switch [cite: 691, 1048]
TT_VARIETY = 'variety' # case [cite: 692, 1056]
TT_SOIL = 'soil'     # default [cite: 693, 1056]

# Control Flow - Loops
TT_GROW = 'grow'         # while [cite: 659, 1048]
TT_CULTIVATE = 'cultivate' # for [cite: 661, 1048]
TT_TEND = 'tend'         # do-while [cite: 663]

# Control Flow - Loop Control
TT_PRUNE = 'prune'    # break [cite: 677, 1056]
TT_SKIP = 'skip'      # continue [cite: 677, 1056]

# Functions & Main
TT_ROOT = 'root'         # main [cite: 156, 1056]
TT_POLLINATE = 'pollinate' # function [cite: 164, 1056]
TT_RECLAIM = 'reclaim'     # return [cite: 165, 1056]

# Literals & Constants
TT_FERTILE = 'fertile'   # const [cite: 883, 1056]
TT_SUNSHINE = 'sunshine' # true [cite: 756, 1056]
TT_FROST = 'frost'       # false [cite: 757, 1056]

# Structs
TT_BUNDLE = 'bundle'     # struct [cite: 964, 1056]

# General
TT_IDENTIFIER = 'id'

# Operators and Delimiters
TT_PLUS = '+'
TT_MINUS = '-'
TT_MUL = '*'
TT_DIV = '/'
TT_MOD = '%'
TT_EQ = '=' 
TT_EQTO = '=='
TT_PLUSEQ = '+='
TT_MINUSEQ = '-='
TT_MULTIEQ = '*='
TT_DIVEQ = '/='
TT_MODEQ = '%='
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
TT_NOT = '!'
TT_INCREMENT = '++'
TT_DECREMENT = '--'
TT_LSQBR = '['
TT_RSQBR = ']'
TT_NEGATIVE = '~' # For negative number literals [cite: 219, 986]
TT_SEEDLIT = 'seedlit'     # Integer literal
TT_TREELIT = 'treelit'     # Double literal
TT_STRINGLIT = 'strnglit' 
TT_LEAFLIT = 'leaflit'     # Char literal
TT_STRCTACCESS = '.'


# --- Character Sets (Based on RE1 & RE2 from old file, still applicable) ---
ZERO = {'0'}
DIGIT = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
DIGITZERO = DIGIT | ZERO
LOWALPHA = set("abcdefghijklmnopqrstuvwxyz")
UPALPHA = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
ALPHA = LOWALPHA | UPALPHA
ALPHA_NUMERIC = ALPHA | DIGITZERO
NEWLINE = {'\n'}
TAB = {'\t'}
WHITESPACE = {' ', '\t', '\n'}

# Delimiter sets based on old file's TDs. These are generally tied to
# operators and literals, not keywords, so they remain relevant.
DEL1 = WHITESPACE
DEL2 = {';'}
DEL3 = WHITESPACE | {'{'}
DEL4 = set()
DEL5 = WHITESPACE | {'('}
DEL6 = WHITESPACE | {',', ';', '=', '>', '<', '!'}
DEL7 = {'('}
DEL8 = WHITESPACE | {';'}
DEL9 = WHITESPACE | ALPHA | {'(', ',', ';', ')'}
DEL11 = WHITESPACE | NEWLINE
DEL12 = ALPHA | DIGITZERO | {']', '~'}
DEL13 = WHITESPACE | {';', '{', ')', ']', '<', '>', '=', '|', '&', '+', '-', '/', '*', '%', ',', '\n'}
DEL14 = WHITESPACE | NEWLINE | {'"', "'", '{'} | ALPHA | DIGITZERO
DEL15 = WHITESPACE | NEWLINE | {'}'}
DEL16 = ALPHA | DIGITZERO | {'"', '(', ')'}
DEL17 = WHITESPACE | {';', ',', '}', ')', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', '['} 
DEL18 = WHITESPACE | {';', '{', ')', '&', '|', '+', '-', '*', '/', '%'} 
DEL19 = WHITESPACE | {',', '}', ')', '=', '>', '<', '!'} 
DEL20 = WHITESPACE | ALPHA | DIGITZERO | {'"', "'", '{'} 
DEL21_for_tilde_op = WHITESPACE | ALPHA | DIGITZERO | {'(', ';', '{', '}'} 
DEL22 = WHITESPACE | {',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'} 
DEL23 = WHITESPACE | {';', ',', '}', ')', '=', '>', '<', '!', '&', '|'} 
DEL24 = WHITESPACE | DIGITZERO | ALPHA | {'~', '('}
DEL25 = WHITESPACE | DIGITZERO | ALPHA | {'~', '"', "'"} 
DEL26 = WHITESPACE | {';', ',', '}', ')', '=', '>', '<', '!', ':'} 
DEL27 = WHITESPACE | {'"'} 
DEL28 = WHITESPACE | DIGITZERO | ALPHA | {'"', "'", '{'} 

# PDF specifies identifiers can contain underscores [cite: 247]
IDENTIFIER_CHARS = ALPHA_NUMERIC | {'_'}
CHAR_CONTENT_CHARS = {chr(i) for i in range(32, 127) if chr(i) not in {"'", '\\'}}
STRING_CONTENT_CHARS = {chr(i) for i in range(32, 127) if chr(i) not in {'"', '\\'}}


class Token:
    def __init__(self, type, value=None, line=0, column=0):
        self.type = type; self.value = value; self.line = line; self.column = column
    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, line {self.line}, col {self.column})'

# --- Simple, reliable scanner to replace broken state machine for lex() ---

_KW_SET = {
    TT_WATER, TT_PLANT, TT_SEED, TT_LEAF, TT_BRANCH, TT_TREE, TT_SPRING, TT_WITHER, TT_BUD,
    TT_HARVEST, TT_GROW, TT_CULTIVATE, TT_TEND, TT_SUNSHINE, TT_FROST, TT_EMPTY, TT_PRUNE,
    TT_SKIP, TT_RECLAIM, TT_ROOT, TT_POLLINATE, TT_VARIETY, TT_FERTILE, TT_SOIL, TT_BUNDLE
}

_SYM2 = {
    TT_EQTO, TT_PLUSEQ, TT_MINUSEQ, TT_MULTIEQ, TT_DIVEQ, TT_MODEQ, TT_LTEQ, TT_GTEQ,
    TT_NOTEQ, TT_INCREMENT, TT_DECREMENT, TT_AND, TT_OR
}

_SYM1 = {
    TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EQ, TT_LPAREN, TT_RPAREN, TT_SEMICOLON,
    TT_COMMA, TT_COLON, TT_BLOCK_START, TT_BLOCK_END, TT_LT, TT_GT, TT_LSQBR, TT_RSQBR,
    TT_NOT, TT_STRCTACCESS
}

def _is_ident_start(ch: str) -> bool:
    return ch.isalpha() or ch == '_'

def _is_ident_part(ch: str) -> bool:
    return ch.isalnum() or ch == '_'

class Lexer:
    def __init__(self, text):
        self.text = text; self.pos = -1; self.current_char = None
        self.line = 1; self.column = 0; self.advance()

    def advance(self):
        if self.current_char == '\n': self.line += 1; self.column = 0
        self.pos += 1
        if self.pos < len(self.text): self.current_char = self.text[self.pos]; self.column += 1
        else: self.current_char = None

    def peek(self, offset=1):
        peek_pos = self.pos + offset
        return self.text[peek_pos] if peek_pos < len(self.text) else None

    def step_back(self):
        # This implementation of step_back seems complex and potentially buggy.
        # A simple pos -= 1, column -= 1 is usually sufficient if line handling
        # is done carefully. However, I will leave the user's logic as-is.
        if self.pos < 0: return
        self.pos -= 1
        if self.pos >=0:
             self.current_char = self.text[self.pos]
             if self.current_char != '\n': self.column -=1
             if self.column < 1 and self.current_char != '\n' : self.column =1 
        else: self.current_char = None; self.pos = -1; self.column = 0

    def make_tokens(self):
        tokens = []; errors = []; state = 0; lexeme = ""
        start_line = 1; start_column = 0
        
        # Keyword mapping from GrowALanguage PDF [cite: 1048, 1056]
        keywords = {
            "water": TT_WATER,
            "plant": TT_PLANT,
            "seed": TT_SEED,
            "leaf": TT_LEAF,
            "branch": TT_BRANCH,
            "tree": TT_TREE,
            "spring": TT_SPRING,
            "wither": TT_WITHER,
            "bud": TT_BUD,
            "harvest": TT_HARVEST,
            "grow": TT_GROW,
            "cultivate": TT_CULTIVATE,
            "tend": TT_TEND,
            "sunshine": TT_SUNSHINE,
            "frost": TT_FROST,
            "empty": TT_EMPTY,
            "prune": TT_PRUNE,
            "skip": TT_SKIP,
            "reclaim": TT_RECLAIM,
            "root": TT_ROOT,
            "pollinate": TT_POLLINATE,
            "variety": TT_VARIETY,
            "fertile": TT_FERTILE,
            "soil": TT_SOIL,
            "bundle": TT_BUNDLE
        }

        while self.current_char is not None or state != 0:
            if state == 0: # Initial state dispatch
                lexeme = ""; start_line = self.line; start_column = self.column
                if self.current_char is None: break
                if self.current_char in WHITESPACE: self.advance(); continue
                
                # --- MODIFIED: Comment Logic for // and /* */ ---
                if self.current_char == '/':
                    if self.peek() == '/': # Single-line comment [cite: 293]
                        state = 502; self.advance(); self.advance(); continue
                    elif self.peek() == '*': # Multi-line comment [cite: 295]
                        state = 500; self.advance(); self.advance(); continue
                    else: # Division operator
                        state = 116; lexeme += self.current_char; self.advance(); continue
                # --- END MODIFICATION ---

                # --- MODIFIED: Simplified Keyword/Identifier Logic ---
                # All words (keywords or identifiers) are handled by state 180.
                if self.current_char in ALPHA: 
                    state = 180; lexeme += self.current_char; self.advance(); continue
                # --- END MODIFICATION ---

                elif self.current_char == '~': # Negative number prefix [cite: 219]
                    if self.peek() in DIGITZERO: # Check if part of a number
                        state = 195; lexeme += self.current_char; self.advance(); continue
                    else: # Standalone tilde (if it were an operator)
                        # PDF only lists ~ as part of negative number literals [cite: 986, 1090]
                        errors.append(LexerError(f"Stray '~' operator. Used only for negative numbers.", start_line, start_column))
                        self.advance(); state = 0; continue
                elif self.current_char in DIGITZERO: # Number starting with digit
                    state = 195; lexeme += self.current_char; self.advance(); continue
                
                elif self.current_char == '"': state = 167; lexeme += self.current_char; self.advance(); continue # String
                elif self.current_char == "'": state = 163; lexeme += self.current_char; self.advance(); continue # Char
                
                elif self.current_char == '+': state = 100; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == '-': state = 106; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == '*': state = 112; lexeme += self.current_char; self.advance(); continue
                # Division is handled above with comments
                elif self.current_char == '%': state = 120; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == '=': state = 125; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == '>': state = 129; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == '<': state = 133; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == '!': state = 137; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == ':': state = 141; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == ';': state = 143; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == '[': state = 145; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == ']': state = 147; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == '{': state = 149; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == '}': state = 151; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == '(': state = 153; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == ')': state = 155; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == ',': state = 157; lexeme += self.current_char; self.advance(); continue
                elif self.current_char == '&': state = 170; lexeme += self.current_char; self.advance(); continue # &&
                elif self.current_char == '|': state = 173; lexeme += self.current_char; self.advance(); continue # ||
                elif self.current_char == '.': state = 176; lexeme += self.current_char; self.advance(); continue # .
                
                # --- REMOVED: ` (concat) and # (comment) ---
                
                else:
                    errors.append(LexerError(f"Illegal character: '{self.current_char}'", start_line, start_column))
                    self.advance(); state = 0; continue
            
            # --- REMOVED: Keyword Trie States (1-99) ---
            # This entire block (elif state == 1 ... elif state == 99)
            # has been removed. All keywords are now handled by state 180.
            
            # --- Operator States (TD3: 100-124) ---
            # This logic is sound and maps to GrowALanguage operators
            elif state == 100: # lexeme is "+"
                if self.current_char == '=': state = 102; lexeme += self.current_char; self.advance()
                elif self.current_char == '+': state = 104; lexeme += self.current_char; self.advance()
                elif self.current_char is None or self.current_char in DEL24: state = 101; 
                else: errors.append(LexerError(f"Invalid char after '+'", self.line, self.column)); state = 0; self.advance()
            elif state == 101: tokens.append(Token(TT_PLUS, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            elif state == 102: # lexeme is "+="
                if self.current_char is None or self.current_char in DEL24: state = 103; 
                else: errors.append(LexerError(f"Invalid char after '+='", self.line, self.column)); state = 0; self.advance()
            elif state == 103: tokens.append(Token(TT_PLUSEQ, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            elif state == 104: # lexeme is "++"
                if self.current_char is None or self.current_char in DEL9: state = 105; 
                else: errors.append(LexerError(f"Invalid char after '++'", self.line, self.column)); state = 0; self.advance()
            elif state == 105: tokens.append(Token(TT_INCREMENT, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()

            elif state == 106: # lexeme is "-"
                if self.current_char == '=': state = 108; lexeme += self.current_char; self.advance()
                elif self.current_char == '-': state = 110; lexeme += self.current_char; self.advance()
                elif self.current_char is None or self.current_char in DEL24: state = 107; 
                else: errors.append(LexerError(f"Invalid char after '-'", self.line, self.column)); state = 0; self.advance()
            elif state == 107: tokens.append(Token(TT_MINUS, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            elif state == 108: # lexeme is "-="
                if self.current_char is None or self.current_char in DEL24: state = 109; 
                else: errors.append(LexerError(f"Invalid char after '-='", self.line, self.column)); state = 0; self.advance()
            elif state == 109: tokens.append(Token(TT_MINUSEQ, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            elif state == 110: # lexeme is "--"
                if self.current_char is None or self.current_char in DEL9: state = 111; 
                else: errors.append(LexerError(f"Invalid char after '--'", self.line, self.column)); state = 0; self.advance()
            elif state == 111: tokens.append(Token(TT_DECREMENT, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            
            elif state == 112: # lexeme is "*"
                if self.current_char == '=': state = 114; lexeme += self.current_char; self.advance()
                # --- REMOVED: ** (TT_EXP) logic ---
                elif self.current_char is None or self.current_char in DEL24: state = 113; 
                else: errors.append(LexerError(f"Invalid char after '*'", self.line, self.column)); state = 0; self.advance()
            elif state == 113: tokens.append(Token(TT_MUL, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            elif state == 114: # lexeme is "*="
                if self.current_char is None or self.current_char in DEL24: state = 115; 
                else: errors.append(LexerError(f"Invalid char after '*='", self.line, self.column)); state = 0; self.advance()
            elif state == 115: tokens.append(Token(TT_MULTIEQ, lexeme, start_line, start_column)); state = 0;
            if self.current_char is not None: self.step_back()
            
            elif state == 116: # lexeme is "/"
                if self.current_char == '=': state = 118; lexeme += self.current_char; self.advance()
                elif self.current_char is None or self.current_char in DEL24: state = 117; 
                else: errors.append(LexerError(f"Invalid char after '/'", self.line, self.column)); state = 0; self.advance()
            elif state == 117: tokens.append(Token(TT_DIV, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            elif state == 118: # lexeme is "/="
                if self.current_char is None or self.current_char in DEL24: state = 119; 
                else: errors.append(LexerError(f"Invalid char after '/='", self.line, self.column)); state = 0; self.advance()
            elif state == 119: tokens.append(Token(TT_DIVEQ, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()

            elif state == 120: # lexeme is "%"
                if self.current_char == '=': state = 123; lexeme += self.current_char; self.advance()
                elif self.current_char is None or self.current_char in DEL24: state = 121; 
                else: errors.append(LexerError(f"Invalid char after '%'", self.line, self.column)); state = 0; self.advance()
            elif state == 121: tokens.append(Token(TT_MOD, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            elif state == 123: # lexeme is "%="
                if self.current_char is None or self.current_char in DEL24: state = 124; 
                else: errors.append(LexerError(f"Invalid char after '%='", self.line, self.column)); state = 0; self.advance()
            elif state == 124: tokens.append(Token(TT_MODEQ, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()

            # --- Operator States (TD4: 125-150) ---
            # This logic is sound and maps to GrowALanguage operators
            elif state == 125: # lexeme is "="
                if self.current_char == '=': state = 127; lexeme += self.current_char; self.advance()
                elif self.current_char is None or self.current_char in DEL28: state = 126; 
                else: errors.append(LexerError(f"Invalid char after '='", self.line, self.column)); state = 0; self.advance()
            elif state == 126: tokens.append(Token(TT_EQ, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            elif state == 127: # lexeme is "=="
                if self.current_char is None or self.current_char in DEL25: state = 128; 
                else: errors.append(LexerError(f"Invalid char after '=='", self.line, self.column)); state = 0; self.advance()
            elif state == 128: tokens.append(Token(TT_EQTO, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()

            elif state == 129: # lexeme is ">"
                if self.current_char == '=': state = 131; lexeme += self.current_char; self.advance()
                elif self.current_char is None or self.current_char in DEL25: state = 130; 
                else: errors.append(LexerError(f"Invalid char after '>'", self.line, self.column)); state = 0; self.advance()
            elif state == 130: tokens.append(Token(TT_GT, lexeme, start_line, start_column)); state = 0;
            if self.current_char is not None: self.step_back()
            elif state == 131: # lexeme is ">="
                if self.current_char is None or self.current_char in DEL25: state = 132; 
                else: errors.append(LexerError(f"Invalid char after '>='", self.line, self.column)); state = 0; self.advance()
            elif state == 132: tokens.append(Token(TT_GTEQ, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            
            elif state == 133: # lexeme is "<"
                if self.current_char == '=': state = 135; lexeme += self.current_char; self.advance()
                elif self.current_char is None or self.current_char in DEL25: state = 134; 
                else: errors.append(LexerError(f"Invalid char after '<'", self.line, self.column)); state = 0; self.advance()
            elif state == 134: tokens.append(Token(TT_LT, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            elif state == 135: # lexeme is "<="
                if self.current_char is None or self.current_char in DEL25: state = 136; 
                else: errors.append(LexerError(f"Invalid char after '<='", self.line, self.column)); state = 0; self.advance()
            elif state == 136: tokens.append(Token(TT_LTEQ, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()

            elif state == 137: # lexeme is "!"
                if self.current_char == '=': state = 139; lexeme += self.current_char; self.advance()
                elif self.current_char is None or self.current_char in DEL25: state = 138; 
                else: errors.append(LexerError(f"Invalid char after '!'", self.line, self.column)); state = 0; self.advance()
            elif state == 138: tokens.append(Token(TT_NOT, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            elif state == 139: # lexeme is "!="
                if self.current_char is None or self.current_char in DEL25: state = 140; 
                else: errors.append(LexerError(f"Invalid char after '!='", self.line, self.column)); state = 0; self.advance()
            elif state == 140: tokens.append(Token(TT_NOTEQ, lexeme, start_line, start_column)); state = 0;
            if self.current_char is not None: self.step_back()

            elif state == 141: # lexeme is ":"
                if self.current_char is None or self.current_char in DEL11: state = 142;
                else: errors.append(LexerError(f"Invalid char after ':'", self.line, self.column)); state = 0; self.advance()
            elif state == 142: tokens.append(Token(TT_COLON, lexeme, start_line, start_column)); state = 0;
            if self.current_char is not None: self.step_back()
            
            elif state == 143: # lexeme is ";"
                if self.current_char is None or self.current_char in DEL11: state = 144;
                else: errors.append(LexerError(f"Invalid char after ';'", self.line, self.column)); state = 0; self.advance()
            elif state == 144: tokens.append(Token(TT_SEMICOLON, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()

            elif state == 145: # lexeme is "["
                if self.current_char is None or self.current_char in DEL12: state = 146;
                else: errors.append(LexerError(f"Invalid char after '['", self.line, self.column)); state = 0; self.advance()
            elif state == 146: tokens.append(Token(TT_LSQBR, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            
            elif state == 147: # lexeme is "]"
                if self.current_char is None or self.current_char in DEL13: state = 148;
                else: errors.append(LexerError(f"Invalid char after ']'", self.line, self.column)); state = 0; self.advance()
            elif state == 148: tokens.append(Token(TT_RSQBR, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()

            elif state == 149: # lexeme is "{"
                if self.current_char is None or self.current_char in DEL14: state = 150;
                else: errors.append(LexerError(f"Invalid char after '{{'", self.line, self.column)); state = 0; self.advance()
            elif state == 150: tokens.append(Token(TT_BLOCK_START, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            
            # --- TD5 Specific States (151-160) ---
            # This logic is sound and maps to GrowALanguage symbols
            elif state == 151: # lexeme is "}"
                if self.current_char is None or self.current_char in DEL15: state = 152
                else: errors.append(LexerError(f"Invalid char after '}}'", self.line, self.column)); state = 0; self.advance()
            elif state == 152: tokens.append(Token(TT_BLOCK_END, lexeme, start_line, start_column)); state = 0;
            if self.current_char is not None: self.step_back()
            
            elif state == 153: # lexeme is "("
                if self.current_char is None or self.current_char in DEL16: state = 154
                else: errors.append(LexerError(f"Invalid char after '('", self.line, self.column)); state = 0; self.advance()
            elif state == 154: tokens.append(Token(TT_LPAREN, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            
            elif state == 155: # lexeme is ")"
                if self.current_char is None or self.current_char in DEL18: state = 156 
                else: errors.append(LexerError(f"Invalid char after ')'", self.line, self.column)); state = 0; self.advance()
            elif state == 156: tokens.append(Token(TT_RPAREN, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            
            elif state == 157: # lexeme is ","
                if self.current_char is None or self.current_char in DEL20: state = 158
                else: errors.append(LexerError(f"Invalid char after ','", self.line, self.column)); state = 0; self.advance()
            elif state == 158: tokens.append(Token(TT_COMMA, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            
            # This state (159) was for a standalone '~' operator, which GrowALanguage
            # does not have (it's a number prefix). This state will no longer be reached
            # because state 0 directs '~' to state 195 (number) or throws an error.
            elif state == 159: # lexeme is "~" (standalone operator)
                if self.current_char is None or self.current_char in DEL21_for_tilde_op: state = 160
                else: errors.append(LexerError(f"Invalid char after '~' operator", self.line, self.column)); state = 0; self.advance()
            elif state == 160: tokens.append(Token(TT_NEGATIVE, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            
            # --- REMOVED: Internal keyword trie states (701-706, 800-801) ---


            # --- Comment, Char/String Literal, Identifier, Number states ---

            # --- REMOVED: '#' Comment state (161-162) ---

            # ''' Char Literal (TD5: 163-166)
            elif state == 163: 
                if self.current_char == '\\': state = 900; lexeme += self.current_char; self.advance()
                elif self.current_char is not None and self.current_char in CHAR_CONTENT_CHARS:
                    state = 164; lexeme += self.current_char; self.advance()
                elif self.current_char == "'": errors.append(LexerError("Empty character literal", start_line, start_column)); state = 0; self.advance()
                else: errors.append(LexerError(f"Invalid character in char literal: {self.current_char}", start_line, start_column)); state = 0; self.advance()
            elif state == 900: # Escape in char
                valid_escapes = {"'": "'", "\\": "\\", "n": "\n", "t": "\t", "0": "\0"}
                if self.current_char is not None and self.current_char in valid_escapes:
                    lexeme += self.current_char; state = 164; self.advance()
                else: errors.append(LexerError(f"Invalid escape sequence: \\{self.current_char}", start_line, start_column)); state = 0; self.advance()
            elif state == 164: 
                if self.current_char == "'": state = 165; lexeme += self.current_char; self.advance()
                else: errors.append(LexerError(f"Unclosed character literal, expected '", start_line, start_column)); state = 0; self.advance()
            elif state == 165: 
                if self.current_char is None or self.current_char in DEL26: state = 166
                else: errors.append(LexerError(f"Invalid delimiter after char literal: {self.current_char}", self.line, self.column)); state = 0; self.advance()
            elif state == 166:
                val = lexeme[1:-1]; actual_val = ""
                if len(val) == 2 and val[0] == '\\': 
                    escape_map = {"'": "'", "\\": "\\", "n": "\n", "t": "\t", "0": "\0"}
                    actual_val = escape_map.get(val[1], val[1]) 
                elif len(val) == 1: actual_val = val
                else: errors.append(LexerError(f"Invalid char literal content: {val}", start_line, start_column));
                # --- MODIFIED: Use TT_LEAFLIT ---
                if not errors or actual_val: tokens.append(Token(TT_LEAFLIT, actual_val, start_line, start_column)); 
                state = 0; 
                if self.current_char is not None: self.step_back()
            
            # '"' String Literal (TD5: 167-169)
            elif state == 167: 
                if self.current_char == '"': state = 168; lexeme += self.current_char; self.advance()
                elif self.current_char == '\\': state = 901; lexeme += self.current_char; self.advance()
                elif self.current_char is not None and self.current_char != '\n': lexeme += self.current_char; self.advance()
                elif self.current_char == '\n': errors.append(LexerError("Newline in string literal", start_line, start_column)); state = 0; self.advance()
                elif self.current_char is None: errors.append(LexerError("Unterminated string literal (EOF)", start_line, start_column)); state = 0
                else: errors.append(LexerError(f"Unexpected char in string: {self.current_char}", start_line, start_column)); state = 0; self.advance()
            elif state == 901: # Escape in string
                valid_escapes = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t', '0': '\0'}
                if self.current_char is not None and self.current_char in valid_escapes:
                    lexeme += self.current_char; state = 167; self.advance()
                else: errors.append(LexerError(f"Invalid string escape sequence: \\{self.current_char}", start_line, start_column)); state = 167; self.advance()
            elif state == 168: 
                if self.current_char is None or self.current_char in DEL19: state = 169
                else: errors.append(LexerError(f"Invalid delimiter after string literal: {self.current_char}", self.line, self.column)); state = 0; self.advance()
            elif state == 169:
                raw_val = lexeme[1:-1]; actual_val = ""; i = 0
                while i < len(raw_val):
                    if raw_val[i] == '\\':
                        if i + 1 < len(raw_val):
                            esc_char = raw_val[i+1]
                            escape_map = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t', '0': '\0'}
                            actual_val += escape_map.get(esc_char, esc_char) 
                            i += 2
                        else: actual_val += raw_val[i]; i+=1 
                    else: actual_val += raw_val[i]; i+=1
                tokens.append(Token(TT_STRINGLIT, actual_val, start_line, start_column)); state = 0; 
                if self.current_char is not None: self.step_back()

            # TD5 &&, ||, .
            elif state == 170: # lexeme is "&"
                if self.current_char == '&': state = 171; lexeme += self.current_char; self.advance()
                else: errors.append(LexerError("Expected '&' for '&&', found single '&'", self.line, self.column)); state = 0; self.advance()
            elif state == 171: # lexeme is "&&"
                if self.current_char is None or self.current_char in DEL25: state = 172
                else: errors.append(LexerError(f"Invalid char after '&&'", self.line, self.column)); state = 0; self.advance()
            elif state == 172: tokens.append(Token(TT_AND, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            
            elif state == 173: # lexeme is "|"
                if self.current_char == '|': state = 174; lexeme += self.current_char; self.advance()
                else: errors.append(LexerError("Expected '|' for '||', found single '|'", self.line, self.column)); state = 0; self.advance()
            elif state == 174: # lexeme is "||"
                if self.current_char is None or self.current_char in DEL25: state = 175
                else: errors.append(LexerError(f"Invalid char after '||'", self.line, self.column)); state = 0; self.advance()
            elif state == 175: tokens.append(Token(TT_OR, lexeme, start_line, start_column)); state = 0; 
            if self.current_char is not None: self.step_back()
            
            elif state == 176: # lexeme is "." (Struct Access) [cite: 970]
                # This is a single-character token. Tokenize immediately.
                tokens.append(Token(TT_STRCTACCESS, lexeme, start_line, start_column))
                state = 0
                # No advance() or step_back() needed, the current char is the *next* token
            
            # --- REMOVED: State 178-179 for ` (concat) ---


            # --- Identifier State (TD6: 180) ---
            elif state == 180: 
                if self.current_char is not None and self.current_char in IDENTIFIER_CHARS:
                    # --- MODIFIED: Max length 16  ---
                    if len(lexeme) < 16: 
                        lexeme += self.current_char; self.advance()
                    else:
                        # Identifier is too long, log error and consume rest of it
                        errors.append(LexerError(f"Identifier '{lexeme}...' exceeds max length 16", start_line, start_column))
                        while self.current_char is not None and self.current_char in IDENTIFIER_CHARS: self.advance()
                        state = 0 
                elif self.current_char is None or self.current_char in DEL22: 
                    # End of identifier, check if it's a keyword
                    token_type = keywords.get(lexeme, TT_IDENTIFIER)
                    tokens.append(Token(token_type, lexeme, start_line, start_column))
                    state = 0 
                    if self.current_char is not None: self.step_back() # Delimiter might start next token
                else: 
                    errors.append(LexerError(f"Invalid char '{self.current_char}' in identifier '{lexeme}'", self.line, self.column)); state = 0; self.advance()

            # --- Number Literal States (TD7: 195-222) ---
            # This logic correctly handles integers (seed), doubles (tree), and ~ prefix
            elif state == 195: 
                if lexeme == "~" and not (self.current_char in DIGITZERO): 
                    errors.append(LexerError("Stray '~'; not a valid number prefix here.", start_line, start_column)); state = 0; continue
                elif self.current_char in DIGITZERO: lexeme += self.current_char; state = 196; self.advance()
                elif self.current_char == '.': 
                     if lexeme == "~" and self.peek() not in DIGITZERO : errors.append(LexerError("Digit expected after '~.'", start_line, start_column)); state = 0; self.advance()
                     else: lexeme += self.current_char; state = 213; self.advance() 
                elif self.current_char is None or self.current_char in DEL23: 
                    # --- MODIFIED: Use TT_SEEDLIT ---
                    tokens.append(Token(TT_SEEDLIT, lexeme, start_line, start_column)); state = 0;
                    if self.current_char is not None: self.step_back()
                else: errors.append(LexerError(f"Invalid char '{self.current_char}' starting number '{lexeme}'", self.line, self.column)); state = 0; self.advance()
            
            # Integer part (up to 15 digits in old file, fine)
            elif state >= 196 and state <= 209: 
                if self.current_char in DIGITZERO: lexeme += self.current_char; state += 1; self.advance()
                elif self.current_char == '.': lexeme += self.current_char; state = 213; self.advance()
                elif self.current_char is None or self.current_char in DEL23: state = 212; 
                else: errors.append(LexerError(f"Invalid char '{self.current_char}' in integer part '{lexeme}'", self.line, self.column)); state = 0; self.advance()
            elif state == 210: 
                if self.current_char in DIGITZERO: lexeme += self.current_char; state = 211; self.advance()
                elif self.current_char == '.': lexeme += self.current_char; state = 213; self.advance()
                elif self.current_char is None or self.current_char in DEL23: state = 212; 
                else: errors.append(LexerError(f"Invalid char '{self.current_char}' in integer part '{lexeme}'", self.line, self.column)); state = 0; self.advance()
            elif state == 211: 
                if self.current_char == '.': lexeme += self.current_char; state = 213; self.advance()
                elif self.current_char is None or self.current_char in DEL23: state = 212; 
                else: errors.append(LexerError(f"Expected '.' or delimiter after integer part, got '{self.current_char}'", self.line, self.column)); state = 0; self.advance()
            
            elif state == 212: # Final state for Integer
                # --- MODIFIED: Use TT_SEEDLIT ---
                tokens.append(Token(TT_SEEDLIT, lexeme, start_line, start_column)); state = 0; 
                if self.current_char is not None: self.step_back()

            # Fractional part
            elif state == 213: 
                if self.current_char in DIGITZERO: lexeme += self.current_char; state = 214; self.advance()
                elif self.current_char is None or self.current_char in DEL17:
                    # Handle case like "1." (if allowed)
                    if lexeme.endswith('.'): 
                        errors.append(LexerError(f"Malformed double ending with dot: '{lexeme}'", self.line, self.column)); state = 0;
                        if self.current_char is not None: self.step_back()
                    else: errors.append(LexerError(f"Digit expected after '.', got '{self.current_char}'", self.line, self.column)); state = 0; self.advance()
                else: errors.append(LexerError(f"Digit expected after '.', got '{self.current_char}'", self.line, self.column)); state = 0; self.advance()
            
            elif state >= 214 and state <= 220: # 7 digits after decimal
                if self.current_char in DIGITZERO: lexeme += self.current_char; state += 1; self.advance()
                elif self.current_char is None or self.current_char in DEL17: state = 222; 
                else: errors.append(LexerError(f"Invalid char '{self.current_char}' in fractional part '{lexeme}'", self.line, self.column)); state = 0; self.advance()
            
            elif state == 221: # 8th digit after decimal
                if self.current_char in DIGITZERO: 
                    lexeme += self.current_char; self.advance() 
                    if self.current_char is None or self.current_char in DEL17: state = 222; 
                    else: errors.append(LexerError(f"Expected delimiter DEL17 after fractional part, got '{self.current_char}'", self.line, self.column)); state = 0 
                elif self.current_char is None or self.current_char in DEL17: state = 222
                else: errors.append(LexerError(f"Invalid char '{self.current_char}' in fractional part '{lexeme}'", self.line, self.column)); state = 0; self.advance()
            
            elif state == 222: # Final state for Double
                # --- MODIFIED: Use TT_TREELIT ---
                tokens.append(Token(TT_TREELIT, lexeme, start_line, start_column)); state = 0; 
                if self.current_char is not None: self.step_back()
            
            
            # --- ADDED: New Comment States ---
            elif state == 500: # Inside multi-line comment /* ... */
                if self.current_char is None:
                    errors.append(LexerError("Unterminated multi-line comment", start_line, start_column))
                    state = 0 # EOF
                elif self.current_char == '*' and self.peek() == '/':
                    self.advance(); self.advance() # Consume */
                    state = 0 # End of comment
                else:
                    self.advance() # Consume character
            
            elif state == 502: # Inside single-line comment // ...
                if self.current_char == '\n' or self.current_char is None:
                    state = 0 # End of comment
                else:
                    self.advance() # Consume character
            
            # --- End of new states ---
            
            else: # Unhandled state
                if state != 0:
                    errors.append(LexerError(f"Lexer in unhandled state {state} for lexeme '{lexeme}' with char '{self.current_char}'", self.line, self.column))
                    if self.current_char is not None: self.advance()
                    state = 0

        if not tokens or tokens[-1].type != TT_EOF:
             tokens.append(Token(TT_EOF, 'EOF', self.line, self.column if self.current_char else self.column))
        return tokens, errors

def lex(source_code: str):
    """Lightweight scanner producing tokens compatible with this file's token constants.
    Returns (tokens, errors), where tokens are instances of Token.
    """
    s = source_code
    i = 0
    n = len(s)
    line = 1
    col = 1
    tokens = []
    errors = []

    def peek(offset=0):
        j = i + offset
        return s[j] if 0 <= j < n else ''

    def advance(k=1):
        nonlocal i, line, col
        for _ in range(k):
            if i < n:
                if s[i] == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
            i += 1

    while i < n:
        ch = peek()
        # whitespace
        if ch.isspace():
            advance()
            continue

        # comments // or /* */
        if ch == '/' and peek(1) == '/':
            advance(2)
            while i < n and peek() not in ('\n','\r'):
                advance()
            continue
        if ch == '/' and peek(1) == '*':
            start_line, start_col = line, col
            advance(2)
            closed = False
            while i < n:
                if peek() == '*' and peek(1) == '/':
                    advance(2)
                    closed = True
                    break
                advance()
            if not closed:
                errors.append(f"Lexical Error at line {start_line}, column {start_col}: Unterminated block comment")
            continue

        start_line, start_col = line, col

        # identifiers / keywords
        if _is_ident_start(ch):
            ident = []
            while _is_ident_part(peek()):
                ident.append(peek())
                advance()
            name = ''.join(ident)
            tok_type = name if name in _KW_SET else TT_IDENTIFIER
            tokens.append(Token(tok_type, name, start_line, start_col))
            continue

        # numbers (optional ~ for negative)
        sign = ''
        if ch == TT_NEGATIVE and peek(1).isdigit():
            sign = '-'
            advance()
            ch = peek()
        if ch.isdigit():
            num = []
            while peek().isdigit():
                num.append(peek())
                advance()
            if peek() == '.':
                num.append('.')
                advance()
                if not peek().isdigit():
                    errors.append(f"Lexical Error at line {start_line}, column {start_col}: Digit expected after '.'")
                while peek().isdigit():
                    num.append(peek())
                    advance()
                tokens.append(Token(TT_TREELIT, sign + ''.join(num), start_line, start_col))
            else:
                tokens.append(Token(TT_SEEDLIT, sign + ''.join(num), start_line, start_col))
            continue

        # string literal
        if ch == '"':
            advance()  # skip opening
            chars = []
            ok = False
            while i < n:
                c = peek()
                if c == '"':
                    advance()
                    ok = True
                    break
                if c == '\n':
                    break
                if c == '\\':
                    advance()
                    esc = peek()
                    mapping = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t', '0': '\0'}
                    chars.append(mapping.get(esc, esc))
                    advance()
                else:
                    chars.append(c)
                    advance()
            if not ok:
                errors.append(f"Lexical Error at line {start_line}, column {start_col}: Unterminated string literal")
            else:
                tokens.append(Token(TT_STRINGLIT, ''.join(chars), start_line, start_col))
            continue

        # char literal
        if ch == "'":
            advance()
            c = peek()
            if c == '\\':
                advance()
                esc = peek()
                mapping = {"'": "'", "\\": "\\", 'n': '\n', 't': '\t', '0': '\0'}
                val = mapping.get(esc, esc)
                advance()
            else:
                val = c
                advance()
            if peek() != "'":
                errors.append(f"Lexical Error at line {start_line}, column {start_col}: Unterminated character literal")
            else:
                advance()
                tokens.append(Token(TT_LEAFLIT, val, start_line, start_col))
            continue

        # two-char operators
        two = ch + peek(1)
        if two in _SYM2:
            tokens.append(Token(two, two, start_line, start_col))
            advance(2)
            continue

        # single-char symbols
        if ch in _SYM1:
            tokens.append(Token(ch, ch, start_line, start_col))
            advance()
            continue

        errors.append(f"Lexical Error at line {start_line}, column {start_col}: Illegal character: '{ch}'")
        advance()

    tokens.append(Token(TT_EOF, 'EOF', line, col))
    return tokens, errors