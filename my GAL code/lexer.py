#CONSTANTS

ALPHA_LOWER = 'abcdefghijklmnopqrstuvwxyz'
ALPHA_UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPHA = ALPHA_LOWER + ALPHA_UPPER
ZERO = '0'
DIGITS = '123456789'
NUM = ZERO + DIGITS
ALPHANUM = ALPHA + NUM
PUNCTUATIONS = '!@#$%^&*()-_=+[]}{|:;’”,<>.?/ \\x'
ASCII = ALPHANUM + PUNCTUATIONS
NOT_OPER = '!'
ARITH_OPER = '+-/*%'
RELAT_OPER = '<>='
OPER = ARITH_OPER + RELAT_OPER + NOT_OPER

#DELIMITERS (Copied from original, assumed to be correct for new keywords)

clbra_dlm = ' =\n)\t,;' + OPER
clcur_dlm = ' \n)}\t,' + ALPHANUM
clpar_dlm = ' \n}{)&|}\t.,(];' + OPER + ALPHANUM
com_dlm   = ' (' # Delimiter for keywords like plant, water, etc.
comma_dlm = ' "\t-!\'(' + ALPHANUM
convert_dlm = ' )\t,\n' + OPER # Delimiter for data types like seed, tree
comnt_dlm = ' \n\t' + ASCII
endln_dlm = ' \n\t'
esc_dlm =   ' "\t'+ ASCII
equal_dlm = ' [(-"+\t!\'' + ALPHANUM
hawk_dlm =  ' \n{\t' # Delimiter for conditional/loop keywords like spring, grow
identif_dlm = ' \n)(&|;[],.\t{' + OPER
lit_dlm =   ' ,):\n;\t/+-%*]' + OPER
lwk_dlm =   ' \n&|=)\t],:;!' + RELAT_OPER # Delimiter for boolean literals
minus_dlm = ' -()\t' + ALPHANUM
npc_dlm =   ' :\t' # Delimiter for 'soil' (default)
not_dlm =   ' =(\t' + ALPHA
opbra_dlm = ' "]\t!\'+-' + ALPHANUM
opcur_dlm = ' \n\t}' + ALPHANUM
operator_dlm = ' (\t!' + ALPHANUM
arith_operator_dlm = ' (\t' + ALPHANUM
oppar_dlm = ' )("-\t!\'+-' + ALPHANUM
plus_dlm =  ' ("+)\t' + ALPHANUM
relat_dlm = ' ("\t!' + ALPHANUM
scolon_dlm = ' +-\t' + ALPHANUM
spc_dlm =   ' \t' # Generic space delimiter
unary_dlm = ' )\t\n,' + OPER

#TOKENS (Aligned with GrowALanguage PDF)

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

# --- Literals ---
TT_SEED         = 'seed_lit'        # Integer literal '3'
TT_TREE         = 'tree_lit'        # Decimal literal '3.14'
TT_LEAF         = 'leaf_lit'        # Char literal 'a'
TT_STRING       = 'string_lit'      # String literal "hello"
TT_BRANCH       = 'branch_lit'      # Boolean literal 'sunshine' or 'frost'

# --- Operators ---
TT_PLUS         = '+'       # '+'
TT_MINUS        = '-'       # '-'
TT_MUL          = '*'       # '*'
TT_DIV          = '/'       # '/'
TT_MOD          = '%'       # '%'
TT_IS           = '='       # '='
TT_TILDE        = '~'       # '~' (Negative prefix)

TT_EQ           = '=='      # '=='  
TT_NEQ          = '!='      # '!='
TT_INC          = '++'      # '++'
TT_DEC          = '--'      # '--'

TT_NOT          = '!'       # '!'
TT_AND          = '&&'      # '&&'
TT_OR           = '||'      # '||'
TT_LT           = '<'       # '<'
TT_GT           = '>'       # '>'
TT_LTE          = '<='      # '<='
TT_GTE          = '>='      # '>='

# --- Symbols ---
TT_OPPAR        = '('       # '('
TT_CLPAR        = ')'       # ')'
TT_OPBRA        = '['       # '['
TT_CLBRA        = ']'       # ']'
TT_OPCUR        = '{'       # '{'
TT_CLCUR        = '}'       # '}'
TT_SEMICOL      = ';'       # ';'
TT_COL          = ':'       # ':'
TT_COMMA        = ','       # ','
TT_DOT          = '.'       # '.'
TT_DBLQT        = '"'       # '"'
TT_QT           = "'"       # "'"

# --- Others ---
TT_SPC          = ' '       # ' '
TT_NL           = 'nl'      # New Line
TT_TAB          = '\t'      # Tab
TT_EOF          = 'EOF'     # End of File

TT_KEYWORD      = 'keyword' # Keywords (generic, unused)
TT_IDENTIFIER   = 'identifier' # Identifiers

TT_ESCAPESEQUENCE = 'escapesequence' # Escape Sequence
TT_COMMENT      = 'comment' # Comments


class Position:
    def __init__(self, index, ln):
        self.index = index
        self.ln = ln

    def advance(self, current_char): #Advance to the next character
        self.index += 1

        if current_char == '\n':
            self.ln +=1

        return self
    
    def copy(self): #Returnss the current position(index, line) of the character
        return Position(self.index, self.ln)
        
#ERROR
class LexicalError:
    def __init__(self, pos, details):
        self.pos = pos
        self.details = details

    def as_string(self): #Returns the error message in string format
        self.details = self.details.replace('\n', '\\n')
        return f"Ln {self.pos.ln} Lexical Error: {self.details}"
    

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
        self.pos = Position(-1, 1)
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
                                        if self.current_char is not None and self.current_char in convert_dlm:
                                            tokens.append(Token(TT_RW_BRANCH, ident_str, line))
                                            continue
                                        elif self.current_char is not None and self.current_char not in convert_dlm and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            continue
                    elif self.current_char == "u":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "d": # bud
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char is not None and self.current_char in hawk_dlm:
                                tokens.append(Token(TT_RW_BUD, ident_str, line))
                                continue
                            elif self.current_char is not None and self.current_char not in hawk_dlm and self.current_char not in ALPHANUM:
                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                        if self.current_char is not None and self.current_char in hawk_dlm: # struct delimiter
                                            tokens.append(Token(TT_RW_BUNDLE, ident_str, line))
                                            continue
                                        elif self.current_char is not None and self.current_char not in hawk_dlm and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                                                    if self.current_char is not None and self.current_char in hawk_dlm:
                                                        tokens.append(Token(TT_RW_CULTIVATE, ident_str, line))
                                                        continue
                                                    elif self.current_char is not None and self.current_char not in hawk_dlm and self.current_char not in ALPHANUM:
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
                                    if self.current_char is not None and self.current_char in spc_dlm:
                                        tokens.append(Token(TT_RW_EMPTY, ident_str, line))
                                        continue
                                    elif self.current_char is not None and self.current_char not in spc_dlm and self.current_char not in ALPHANUM:
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
                                    if self.current_char is None or self.current_char in lwk_dlm:
                                        tokens.append(Token(TT_BRANCH, ident_str, line)) # Boolean Literal
                                        continue
                                    elif self.current_char is not None and self.current_char not in lwk_dlm and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        continue
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
                                            if self.current_char is None or self.current_char in spc_dlm:
                                                tokens.append(Token(TT_RW_FERTILE, ident_str, line))
                                                continue
                                            elif self.current_char is not None and self.current_char not in spc_dlm and self.current_char not in ALPHANUM:
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
                                if self.current_char is not None and self.current_char in hawk_dlm:
                                    tokens.append(Token(TT_RW_GROW, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in hawk_dlm and self.current_char not in ALPHANUM:
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
                                            if self.current_char is not None and self.current_char in hawk_dlm:
                                                tokens.append(Token(TT_RW_HARVEST, ident_str, line))
                                                continue
                                            elif self.current_char is not None and self.current_char not in hawk_dlm and self.current_char not in ALPHANUM:
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
                                if self.current_char is None or self.current_char in convert_dlm:
                                    tokens.append(Token(TT_RW_LEAF, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in convert_dlm and self.current_char not in ALPHANUM:
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
                                    if self.current_char is not None and self.current_char in com_dlm:
                                        tokens.append(Token(TT_RW_PLANT, ident_str, line))
                                        continue
                                    elif self.current_char is not None and self.current_char not in com_dlm and self.current_char not in ALPHANUM:
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
                                                    if self.current_char is not None and self.current_char in spc_dlm:
                                                        tokens.append(Token(TT_RW_POLLINATE, ident_str, line))
                                                        continue
                                                    elif self.current_char is not None and self.current_char not in spc_dlm and self.current_char not in ALPHANUM:
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
                                    if self.current_char is None or self.current_char in endln_dlm:
                                        tokens.append(Token(TT_RW_PRUNE, ident_str, line))
                                        continue
                                    elif self.current_char is not None and self.current_char not in endln_dlm and self.current_char not in ALPHANUM:
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
                                            if self.current_char is None or self.current_char in endln_dlm:
                                                tokens.append(Token(TT_RW_RECLAIM, ident_str, line))
                                                continue
                                            elif self.current_char is not None and self.current_char not in endln_dlm and self.current_char not in ALPHANUM:
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
                                if self.current_char is not None and self.current_char in com_dlm:
                                    tokens.append(Token(TT_RW_ROOT, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in com_dlm and self.current_char not in ALPHANUM:
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
                                if self.current_char is None or self.current_char in convert_dlm:
                                    tokens.append(Token(TT_RW_SEED, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in convert_dlm and self.current_char not in ALPHANUM:
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
                                if self.current_char is None or self.current_char in endln_dlm:
                                    tokens.append(Token(TT_RW_SKIP, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in endln_dlm and self.current_char not in ALPHANUM:
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
                                if self.current_char is None or self.current_char in npc_dlm:
                                    tokens.append(Token(TT_RW_SOIL, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in npc_dlm and self.current_char not in ALPHANUM:
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
                                        if self.current_char is not None and self.current_char in hawk_dlm:
                                            tokens.append(Token(TT_RW_SPRING, ident_str, line))
                                            continue
                                        elif self.current_char is not None and self.current_char not in hawk_dlm and self.current_char not in ALPHANUM:
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
                                                if self.current_char is None or self.current_char in lwk_dlm:
                                                    tokens.append(Token(TT_BRANCH, ident_str, line)) # Boolean Literal
                                                    continue
                                                elif self.current_char is not None and self.current_char not in lwk_dlm and self.current_char not in ALPHANUM:
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
                                if self.current_char is not None and self.current_char in hawk_dlm:
                                    tokens.append(Token(TT_RW_TEND, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in hawk_dlm and self.current_char not in ALPHANUM:
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
                                if self.current_char is None or self.current_char in convert_dlm:
                                    tokens.append(Token(TT_RW_TREE, ident_str, line))
                                    continue
                                elif self.current_char is not None and self.current_char not in convert_dlm and self.current_char not in ALPHANUM:
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
                                            if self.current_char is None or self.current_char in spc_dlm:
                                                tokens.append(Token(TT_RW_VARIETY, ident_str, line))
                                                continue
                                            elif self.current_char is not None and self.current_char not in spc_dlm and self.current_char not in ALPHANUM:
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
                                    if self.current_char is not None and self.current_char in com_dlm:
                                        tokens.append(Token(TT_RW_WATER, ident_str, line))
                                        continue
                                    elif self.current_char is not None and self.current_char not in com_dlm and self.current_char not in ALPHANUM:
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
                                        if self.current_char is not None and self.current_char in hawk_dlm:
                                            tokens.append(Token(TT_RW_WITHER, ident_str, line))
                                            continue
                                        elif self.current_char is not None and self.current_char not in hawk_dlm and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            continue

                #Identifier            
                maxIdentifierLength = 16 # Changed from 20 to 16
                while self.current_char is not None and self.current_char in ALPHANUM + "_":
                    if len(ident_str) + 1 > maxIdentifierLength:
                        errors.append(LexicalError(pos, f"Identifier '{ident_str}...' exceeds maximum length of {maxIdentifierLength} characters."))
                        # Consume the rest of the invalid identifier
                        while self.current_char is not None and self.current_char in ALPHANUM + "_":
                            self.advance()
                        break
                    ident_str += self.current_char
                    self.advance()

                if len(ident_str) <= maxIdentifierLength:
                    if self.current_char is None or self.current_char in identif_dlm:
                        tokens.append(Token(TT_IDENTIFIER, ident_str, line))
                        continue
                    elif self.current_char is not None and self.current_char not in identif_dlm and self.current_char not in ALPHANUM:
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
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in unary_dlm:
                        tokens.append(Token(TT_DEC, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        self.advance()
                        continue
                elif self.current_char is not None and self.current_char in minus_dlm:
                    tokens.append(Token(TT_MINUS, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
            
            elif self.current_char == "~": # Added for negative prefix
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is not None and self.current_char in operator_dlm: # Assumes it's an operator
                    tokens.append(Token(TT_TILDE, ident_str, line))
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
                    if self.current_char is not None and self.current_char in relat_dlm:
                        tokens.append(Token(TT_NEQ, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                elif self.current_char is not None and self.current_char in not_dlm:
                    tokens.append(Token(TT_NOT, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
            
            elif self.current_char == "%":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is not None and self.current_char in arith_operator_dlm:
                    tokens.append(Token(TT_MOD, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
    
            elif self.current_char == "&":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "&":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is not None and self.current_char in operator_dlm:
                        tokens.append(Token(TT_AND, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                else:
                    errors.append(LexicalError(pos, f"Invalid character '{ident_str}'"))
                    self.advance()
                    continue
                    
            elif self.current_char == "(":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is not None and self.current_char in oppar_dlm:
                    tokens.append(Token(TT_OPPAR, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
                
            elif self.current_char == ")":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is None or self.current_char in clpar_dlm:
                    tokens.append(Token(TT_CLPAR, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
                
            elif self.current_char == "*":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is None or self.current_char in arith_operator_dlm:
                    tokens.append(Token(TT_MUL, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
                
            elif self.current_char == ",":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is not None and self.current_char in comma_dlm:
                    tokens.append(Token(TT_COMMA, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
            
            elif self.current_char == "\\":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "\"":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in esc_dlm:
                        tokens.append(Token(TT_ESCAPESEQUENCE, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                elif self.current_char == "/":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in esc_dlm:
                        tokens.append(Token(TT_ESCAPESEQUENCE, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                elif self.current_char == "{":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in esc_dlm:
                        tokens.append(Token(TT_ESCAPESEQUENCE, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                elif self.current_char == "}":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in esc_dlm:
                        tokens.append(Token(TT_ESCAPESEQUENCE, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                elif self.current_char == "n":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in esc_dlm:
                        tokens.append(Token(TT_ESCAPESEQUENCE, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                elif self.current_char == "t":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in esc_dlm:
                        tokens.append(Token(TT_ESCAPESEQUENCE, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                else:
                    errors.append(LexicalError(pos, f"Invalid character '{ident_str}'"))
                    self.advance()
                    continue    
                
            elif self.current_char == ";":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is not None and self.current_char in scolon_dlm:
                    tokens.append(Token(TT_SEMICOL, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
                
            elif self.current_char == "[":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is not None and self.current_char in opbra_dlm:
                    tokens.append(Token(TT_OPBRA, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
                
            elif self.current_char == "]":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is None or self.current_char in clbra_dlm:
                    tokens.append(Token(TT_CLBRA, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
                
            elif self.current_char == "{":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is not None and self.current_char in opcur_dlm:
                    tokens.append(Token(TT_OPCUR, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
                
            elif self.current_char == "}":
                ident_str = self.current_char 
                pos = self.pos.copy() 
                self.advance()
                if self.current_char is None or self.current_char in clcur_dlm:
                    tokens.append(Token(TT_CLCUR, ident_str, line))
                    continue
                else: 
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue

            elif self.current_char == "|":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "|":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is not None and self.current_char in operator_dlm:
                        tokens.append(Token(TT_OR, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is None or self.current_char in unary_dlm:
                        tokens.append(Token(TT_INC, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                elif self.current_char is not None and self.current_char in plus_dlm:
                    tokens.append(Token(TT_PLUS, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue

            elif self.current_char == "<":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is not None and self.current_char in arith_operator_dlm:
                        tokens.append(Token(TT_LTE, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                elif self.current_char is not None and self.current_char in arith_operator_dlm:
                    tokens.append(Token(TT_LT, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
            
            elif self.current_char == "=":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is not None and self.current_char in relat_dlm:
                        tokens.append(Token(TT_EQ, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                elif self.current_char is not None and self.current_char in equal_dlm:
                    tokens.append(Token(TT_IS, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue

            elif self.current_char == ">":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is not None and self.current_char in arith_operator_dlm:
                        tokens.append(Token(TT_GTE, ident_str, line))
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                elif self.current_char is not None and self.current_char in arith_operator_dlm:
                    tokens.append(Token(TT_GT, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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
                elif self.current_char is not None and self.current_char in arith_operator_dlm:
                    tokens.append(Token(TT_DIV, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue
            
            elif self.current_char == ".":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is not None and self.current_char in ALPHA:
                    tokens.append(Token(TT_DOT, ident_str, line))
                    continue

                elif self.current_char is not None and self.current_char in NUM:
                    fractional_part = ""
                    while self.current_char is not None and self.current_char in NUM :
                        if len(fractional_part + self.current_char) > 6: # PDF specifies max 6 digits right
                            errors.append(LexicalError(pos, f"'{ident_str}' exceeds maximum number of decimal places"))
                            break

                        fractional_part += self.current_char
                        self.advance()
                        
                    ident_str = f"0.{fractional_part}"
                    
                    if self.current_char is None or self.current_char in lit_dlm:
                        tokens.append(Token(TT_TREE, ident_str, line)) # Changed to TT_TREE
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                    
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()
                    continue
            
            elif self.current_char == ":":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is None or self.current_char in endln_dlm:
                    tokens.append(Token(TT_COL, ident_str, line))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    continue

            elif self.current_char in NUM:
                dot_count = 0
                ident_str = ""
                pos = self.pos.copy()
                digitCount = 0
                has_e = False

                while self.current_char is not None and self.current_char in NUM + ".":
                    if self.current_char == ".":
                        if dot_count == 1:
                            break
                        dot_count += 1

                    digitCount += 1
                    if digitCount > 16: # Using 16 as a general max length
                        break
                    ident_str += self.current_char
                    if digitCount <= 16:
                        self.advance()

                # ADDED: Logic for Scientific Notation
                if self.current_char in 'eE' and dot_count == 1:
                    has_e = True
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char in '+-': # Handle 1.2e-5
                        ident_str += self.current_char
                        self.advance()
                    if self.current_char is None or self.current_char not in NUM:
                        errors.append(LexicalError(pos, f"Invalid scientific notation: 'e' must be followed by digits."))
                        continue
                    while self.current_char is not None and self.current_char in NUM:
                        ident_str += self.current_char
                        self.advance()

                if dot_count == 0 and not has_e: 
                    ident_str = ident_str.lstrip("0") or "0"
                    if digitCount > 16: 
                        errors.append(LexicalError(pos, f"'{ident_str}' exceeds maximum number of characters"))
                        continue
                    
                    if self.current_char is None or self.current_char in lit_dlm:
                        tokens.append(Token(TT_SEED, ident_str, line)) # Changed to TT_SEED
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                    
                else:  # Float case
                    if not has_e: # Only re-format if not scientific notation
                         parts = ident_str.split(".")
                         integer_part = parts[0].lstrip("0") or "0"
                         fractional_part = (parts[1] if len(parts) > 1 else "").rstrip("0") or "0"
                         if fractional_part == "0":
                             ident_str = f"{integer_part}.0" # Keep at least one zero
                         else:
                             ident_str = f"{integer_part}.{fractional_part}"

                    if digitCount > 16:
                        errors.append(LexicalError(pos, f"'{ident_str}' exceeds maximum number of characters"))
                        continue

                    if self.current_char is None or self.current_char in lit_dlm:
                        tokens.append(Token(TT_TREE, ident_str, line)) # Changed to TT_TREE
                        continue
                    else:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
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

                if self.current_char is not None and self.current_char not in lit_dlm:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after string literal '{string}'"))
                    continue
            
                string = string.replace('\n', '\\n')
                tokens.append(Token(TT_STRING, string, line)) # Changed to TT_STRING
                continue
    
            elif self.current_char == "'":
                string = ''
                char = ''
                pos = self.pos.copy()
                string += self.current_char
                self.advance()

                while self.current_char is not None and self.current_char != "'":
                    if self.current_char == '\n':
                        break
                    elif self.current_char == '\\':
                        break
                    else:
                        string += self.current_char
                        char += self.current_char
                    self.advance()

                if self.current_char == "'":
                    string += self.current_char
                    self.advance()
                    
                else:
                    errors.append(LexicalError(pos, f"Missing closing '\'' after '{string}'"))
                    continue

                if len(char) > 1:
                    errors.append(LexicalError(pos, f"Character literal '{string}' exceeds maximum length of 1 character."))
                    continue

                if self.current_char is not None and self.current_char not in lit_dlm:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{string}'"))
                    continue

                tokens.append(Token(TT_LEAF, string, line)) # Changed to TT_LEAF
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
