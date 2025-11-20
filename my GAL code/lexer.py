#CONSTANTS

ZERO = '0'
DIGIT = '123456789'
ZERODIGIT = ZERO + DIGIT

LOW_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
UPPER_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

ALPHA = LOW_ALPHA + UPPER_ALPHA
ALPHANUM = ALPHA + ZERODIGIT + '_'

# --- DELIMITER SETS ---

space_delim = {' ', '\t', '\n', ';', '{', '(', ','}
delim2 = {';', ':'}
delim3 = {'{', ' ', '('}
delim4 = {':', '('}
delim5 = {'('}
delim6 = {';', ',', '=', '>', '<', '!', '}', ')', '('}  
delim7 = {'('}
delim8 = {';', ' '}  
delim9 = set(ALPHA + '(' + ',' + ';' + ')')  
delim10 = {';', ')'}  
delim11 = {'\n'}  
delim12 = set(ALPHA + ZERODIGIT + ']' + '~')
delim13 = {';', ')', '['}
delim14 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')
delim15 = {'\n', ';', '}', ','}
delim16 = set(ALPHANUM + ')' + '"' + '!' + '(' + '[' + '\'')
delim17 = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}
delim18 = {';', '{', ')', '&', '|', '+', '-', '*', '/', '%'}
delim19 = {';', ',', '}', ')', '=', '>', '<', '!'}
delim20 = set(ALPHA + ZERODIGIT  + '"' + "'" + '{' )
delim21 = set(DIGIT)
delim22 = {',', ';', '(', ')', '{', '[', ']'}
delim23 = {';', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}
delim24 = set(ZERODIGIT + ALPHA + '~' + '(')
idf_delim = { ' ', ',', ';', '(', ')', '{', '}', '[', ']', ':', '+', '-', '*', '/', '%' , '>', '<', '=', '\t', '\n'}
whlnum_delim = { ';', ' ', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', '\t', '\n' }
decim_delim = { '}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ' ', '\t', '\n', ')' }
    # Fix: set() takes a single iterable; combine into one string and use newline '\n'
comment_delim = set(ALPHANUM + ';+-*/%}{()' + '\n')


#TOKENS 

# --- Reserved Words ---
TT_RW_WATER       = 'water'     # Input
TT_RW_PLANT       = 'plant'     # Output
TT_RW_SEED        = 'seed'      # Data Type (int)
TT_RW_LEAF        = 'leaf'      # Data Type (char)
TT_RW_BRANCH      = 'branch'    # Data Type (boolean)
TT_RW_TREE        = 'tree'      # Data Type (double)
TT_RW_SPRING      = 'spring'    # Conditional (if)
TT_RW_WITHER      = 'wither'    # Conditional (else)
TT_RW_BUD         = 'bud'       # Conditional (else-if)
TT_RW_HARVEST     = 'harvest'   # Conditional (switch)
TT_RW_GROW        = 'grow'      # Loop (while)
TT_RW_CULTIVATE   = 'cultivate' # Loop (for)
TT_RW_TEND        = 'tend'      # Loop (do-while)
TT_RW_EMPTY       = 'empty'     # Void type
TT_RW_PRUNE       = 'prune'     # break
TT_RW_SKIP        = 'skip'      # continue
TT_RW_RECLAIM     = 'reclaim'   # return
TT_RW_ROOT        = 'root'      # main
TT_RW_POLLINATE   = 'pollinate' # function
TT_RW_VARIETY     = 'variety'   # case
TT_RW_FERTILE     = 'fertile'   # const
TT_RW_SOIL        = 'soil'      # default
TT_RW_BUNDLE      = 'bundle'    # struct
TT_RW_STRING      = 'string'    # string data type

# --- Literals ---
TT_IDENTIFIER = 'idf'
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
TT_NOT = '!'
TT_INCREMENT = '++'
TT_DECREMENT = '--'
TT_LSQBR = '['
TT_RSQBR = ']'
TT_NEGATIVE = '~'
TT_MEMBER = 'member'
TT_INTEGERLIT = 'intlit'
TT_NEGINTLIT = '~intlit'
TT_DOUBLELIT = 'dbllit'
TT_NEGDOUBLELIT = '~dbllit'
TT_STRINGLIT = 'strnglit'
TT_CHARLIT = 'chrlit'
TT_STRCTACCESS = '.'
TT_NL = '\n'
TT_DOT = '.'


class Position:
    def __init__(self, index, ln, col=0):
        self.index = index
        self.ln = ln
        self.col = col

    def advance(self, current_char): #Advance to the next character
        self.index += 1
        self.col += 1

        if current_char == '\n':
            self.ln +=1
            self.col = 0

        return self
    
    def copy(self): #Returnss the current position(index, line) of the character
        return Position(self.index, self.ln, self.col)
        
#ERROR
class LexicalError:
    def __init__(self, pos, details):
        self.pos = pos
        self.details = details

    def as_string(self): #Returns the error message in string format
        self.details = self.details.replace('\n', '\\n')
        return f"Ln {self.pos.ln}, Col {self.pos.col}: {self.details}"
    

#TOKEN
class Token:
    def __init__(self, type_, value=None, line=1): 
        self.type = type_
        self.value = value
        self.line = line

#LEXER
class Lexer:
    def __init__(self, source_code): 
        self.source_code = source_code
        self.pos = Position(-1, 1, -1)
        self.current_char = None
        self.advance()

    def advance(self): #Advance to the next character
        self.pos.advance(self.current_char)
        self.current_char = self.source_code[self.pos.index] if self.pos.index<len(self.source_code) else None

    def make_tokens(self):
        tokens = [] #List of tokens
        line = 1
        errors = []
        while self.current_char != None:
            if self.current_char in ALPHA:
                ident_str = ''
                pos = self.pos.copy()
                
                # Letter B
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
                                        if self.current_char is not None and self.current_char in space_delim:
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
                            if self.current_char is not None and self.current_char in delim4:
                                tokens.append(Token(TT_RW_BUD, ident_str, line))
                                continue
                            elif self.current_char is not None and self.current_char not in delim4 and self.current_char not in ALPHANUM:
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
                                                    if self.current_char is not None and self.current_char in delim4:
                                                        tokens.append(Token(TT_RW_CULTIVATE, ident_str, line))
                                                        continue
                                                    elif self.current_char is not None and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                    if self.current_char is not None and self.current_char in space_delim:
                                        tokens.append(Token(TT_RW_EMPTY, ident_str, line))
                                        continue
                                    elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                            if self.current_char is None or self.current_char in space_delim:
                                                tokens.append(Token(TT_RW_FERTILE, ident_str, line))
                                                continue
                                            elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                if self.current_char is None or self.current_char in delim4 or self.current_char in space_delim:
                                    tokens.append(Token(TT_RW_GROW, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in delim4 and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                            if self.current_char is not None and self.current_char in delim4:
                                                tokens.append(Token(TT_RW_HARVEST, ident_str, line))
                                                continue
                                            elif self.current_char is not None and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                if self.current_char is None or self.current_char in space_delim:
                                    tokens.append(Token(TT_RW_LEAF, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                    if self.current_char is not None and self.current_char in delim6:
                                        tokens.append(Token(TT_RW_PLANT, ident_str, line))
                                        continue
                                    elif self.current_char is not None and self.current_char not in delim6 and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                                    if self.current_char is not None and self.current_char in space_delim:
                                                        tokens.append(Token(TT_RW_POLLINATE, ident_str, line))
                                                        continue
                                                    elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                    if self.current_char is None or self.current_char in space_delim:
                                        tokens.append(Token(TT_RW_PRUNE, ident_str, line))
                                        continue
                                    elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                            if self.current_char is None or self.current_char in delim8:
                                                tokens.append(Token(TT_RW_RECLAIM, ident_str, line))
                                                continue
                                            elif self.current_char is not None and self.current_char not in delim8 and self.current_char not in ALPHANUM:
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
                                if self.current_char is not None and self.current_char in delim6:
                                    tokens.append(Token(TT_RW_ROOT, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in delim6 and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                if self.current_char is None or self.current_char in space_delim:
                                    tokens.append(Token(TT_RW_SEED, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                if self.current_char is None or self.current_char in space_delim:
                                    tokens.append(Token(TT_RW_SKIP, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                if self.current_char is None or self.current_char in delim2:
                                    tokens.append(Token(TT_RW_SOIL, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in delim2 and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                        if self.current_char is not None and self.current_char in delim6:
                                            tokens.append(Token(TT_RW_SPRING, ident_str, line))
                                            continue
                                        elif self.current_char is not None and self.current_char not in delim6 and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                                if self.current_char is None or self.current_char in space_delim:
                                                    tokens.append(Token(TT_RW_BRANCH, ident_str, line)) # Boolean Literal
                                                    continue
                                                elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                if self.current_char is None or self.current_char in delim3:
                                    tokens.append(Token(TT_RW_TEND, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in delim3 and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                if self.current_char is None or self.current_char in space_delim:
                                    tokens.append(Token(TT_RW_TREE, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                            if self.current_char is None or self.current_char in space_delim:
                                                tokens.append(Token(TT_RW_VARIETY, ident_str, line))
                                                continue
                                            elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                    if self.current_char is not None and self.current_char in delim6:
                                        tokens.append(Token(TT_RW_WATER, ident_str, line))
                                        continue
                                    elif self.current_char is not None and self.current_char not in delim6 and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                        if self.current_char is None or self.current_char in delim3:
                                            tokens.append(Token(TT_RW_WITHER, ident_str, line))
                                            continue
                                        elif self.current_char is not None and self.current_char not in delim3 and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                if self.current_char in '+-*/%':
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
                if self.current_char in '+-*/%':
                    errors.append(LexicalError(pos, f"Consecutive operators '{ident_str}{self.current_char}' are not allowed"))
                    self.advance()  # Consume the operator
                    continue
                # Check for valid delimiter after %
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
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
                    # Check if previous token is an identifier (valid for ++)
                    if len(tokens) > 0 and tokens[-1].type == TT_IDENTIFIER:
                        ident_str += self.current_char
                        self.advance()
                        tokens.append(Token(TT_INCREMENT, ident_str, line))
                        continue
                    else:
                        # ++ not after an identifier is an error
                        errors.append(LexicalError(pos, f"Consecutive operators '{ident_str}{self.current_char}' are not allowed"))
                        self.advance()  # Consume the second +
                        continue
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_PLUSEQ, ident_str, line))
                    continue
                # Check for consecutive operators
                if self.current_char in '+-*/%':
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
            
            elif self.current_char == "=":
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
                    tokens.append(Token(TT_EQTO, ident_str, line))
                    continue
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

            elif self.current_char == "/":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "/": # Single-line comment
                    ident_str += self.current_char
                    self.advance()
                    while self.current_char is not None and self.current_char != "\n":
                        ident_str += self.current_char
                        self.advance()
                    #tokens.append(Token(TT_COMMENT, ident_str, line)) # Comments are skipped
                    continue
                elif self.current_char == "*": # Multi-line comment
                    ident_str += self.current_char
                    self.advance()
                    while self.current_char is not None:
                        if self.current_char == "*" and self.pos.index + 1 < len(self.source_code) and self.source_code[self.pos.index + 1] == "/":
                            ident_str += "*/"
                            self.advance()
                            self.advance()
                            break
                        else:
                            ident_str += self.current_char
                            if self.current_char == "\n":
                                line += 1
                            self.advance()
                    #tokens.append(Token(TT_COMMENT, ident_str, line)) # Comments are skipped
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
                        if len(fractional_part + self.current_char) > 6: 
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

            elif self.current_char in ZERODIGIT:
                dot_count = 0
                ident_str = ""
                pos = self.pos.copy()
                integer_digit_count = 0
                fractional_digit_count = 0
                has_e = False

                # Read integer part
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

                # Check for decimal point
                if self.current_char == "." and integer_digit_count <= 16:
                    dot_count = 1
                    ident_str += self.current_char
                    self.advance()
                    
                    # After a decimal point, there must be at least one digit
                    if self.current_char is None or self.current_char not in ZERODIGIT:
                        errors.append(LexicalError(pos, f"Invalid number '{ident_str}': decimal point must be followed by digits"))
                        continue
                    
                    # Read fractional part
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        fractional_digit_count += 1
                        if fractional_digit_count > 7:
                            errors.append(LexicalError(pos, f"Fractional part exceeds maximum of 7 digits"))
                            # Consume the rest of the invalid number
                            while self.current_char is not None and self.current_char in ZERODIGIT:
                                self.advance()
                            break
                        ident_str += self.current_char
                        self.advance()

                # Only continue if no errors were found
                if integer_digit_count > 16 or fractional_digit_count > 7:
                    continue

                # Only continue if no errors were found
                if integer_digit_count > 16 or fractional_digit_count > 7:
                    continue

                # ADDED: Logic for Scientific Notation
                if self.current_char in 'eE' and dot_count == 1:
                    has_e = True
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char in '+-': # Handle 1.2e-5
                        ident_str += self.current_char
                        self.advance()
                    if self.current_char is None or self.current_char not in ZERODIGIT:
                        errors.append(LexicalError(pos, f"Invalid scientific notation: 'e' must be followed by digits."))
                        continue
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
                        # Check if followed by a letter (identifier starting with number)
                        if self.current_char in ALPHA:
                            errors.append(LexicalError(pos, f"Identifiers cannot start with a number: '{ident_str}{self.current_char}...'"))
                        else:
                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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

            elif self.current_char == '"':
                string = ''
                pos = self.pos.copy()
                escape_character = False
                string += self.current_char
                self.advance()

                escape_characters = {
                    'n': '\n',
                    't': '\t',
                    '{': '\\{',
                    '}': '\\}'
                }

                while self.current_char is not None and (self.current_char != '"' or escape_character):
                    if escape_character:
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
                
                string = string.replace('\n', '\\n')
                tokens.append(Token(TT_STRINGLIT, string, line))
                continue
    
            elif self.current_char == "'":
                string = ''
                char = ''
                pos = self.pos.copy()
                string += self.current_char
                self.advance()
                has_error = False

                while self.current_char is not None and self.current_char != "'":
                    if self.current_char == '\n':
                        break
                    elif self.current_char == '\\':
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
                self.advance()
                errors.append(LexicalError(pos, f"Invalid character '" + char + "'"))
                
                continue
                
        if self.current_char is None:
            tokens.append(Token(TT_EOF, "", line))
        return tokens, errors

    
def run(source_code):
    lexer = Lexer(source_code)
    tokens, error = lexer.make_tokens()
    return tokens, error

# Export a lex() function so server.py can import and use this lexer directly
def lex(source_code):
    lexer = Lexer(source_code)
    tokens, errors = lexer.make_tokens()
    # Convert errors to strings if they are LexicalError objects
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