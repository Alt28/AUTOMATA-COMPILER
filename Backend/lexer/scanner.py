from shared.tokens import *  # noqa: F401,F403  - TT_* constants used heavily by the FSM
from shared.tokens import Token, get_token_description  # noqa: F401  - explicit re-export
from lexer.positions import Position
from lexer.errors import LexicalError
from lexer.delimiters import (
    ZERO, DIGIT, ZERODIGIT, LOW_ALPHA, UPPER_ALPHA, ALPHA, ALPHANUM,
    space_delim, delim2, delim3, delim4, delim5, delim6, delim7, delim8,
    delim9, delim10, delim11, delim12, delim13, delim14, delim15, delim16,
    delim17, delim18, delim19, delim20, delim21, delim22, delim23, delim24,
    delim25,
    idf_delim, whlnum_delim, decim_delim, comment_delim,
)


class Lexer:
    def __init__(self, source_code): 
        self.source_code = source_code.replace('\r', '')
        self.pos = Position(-1, 1, -1)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.source_code[self.pos.index] if self.pos.index<len(self.source_code) else None

    def make_tokens(self):
        tokens = []
        line = 1
        errors = []
        pos = self.pos.copy()

        while self.current_char != None:

            if self.current_char in ALPHA:
                ident_str = ''
                pos = self.pos.copy()

                if self.current_char == "b":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "r":
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
                                        if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                            tokens.append(Token(TT_RW_BRANCH, ident_str, line, pos.col))
                                            continue
                                        elif self.current_char not in ALPHANUM:
                                            tokens.append(Token(TT_RW_BRANCH, ident_str, line, pos.col))
                                            continue
                    elif self.current_char == "u":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "d":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:
                                tokens.append(Token(TT_RW_BUD, ident_str, line, pos.col))
                                continue
                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                self.advance()
                                continue
                        elif self.current_char == "n":
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
                                        if self.current_char is not None and self.current_char in space_delim:
                                            tokens.append(Token(TT_RW_BUNDLE, ident_str, line, pos.col))
                                            continue
                                        elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            self.advance()
                                            continue

                elif self.current_char == "c":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "u":
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
                                                        tokens.append(Token(TT_RW_CULTIVATE, ident_str, line, pos.col))
                                                        continue
                                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                        self.advance()
                                                        continue

                elif self.current_char == "e":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "m":
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
                                        tokens.append(Token(TT_RW_EMPTY, ident_str, line, pos.col))
                                        continue
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        self.advance()
                                        continue

                elif self.current_char == "f":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "r":
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
                                        tokens.append(Token(TT_BOOLLIT_FALSE, ident_str, line, pos.col))
                                        continue
                    elif self.current_char == "e":
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
                                                tokens.append(Token(TT_RW_FERTILE, ident_str, line, pos.col))
                                                continue
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                self.advance()
                                                continue
                                            
                elif self.current_char == "g":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "r":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "o":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "w":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4 or self.current_char in space_delim:
                                    tokens.append(Token(TT_RW_GROW, ident_str, line, pos.col))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue
                                
                elif self.current_char == "h":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "a":
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
                                                tokens.append(Token(TT_RW_HARVEST, ident_str, line, pos.col))
                                                continue
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                self.advance()
                                                continue
                                
                elif self.current_char == "l":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "e":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "a":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "f":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                    tokens.append(Token(TT_RW_LEAF, ident_str, line, pos.col))
                                    continue
                                elif self.current_char not in ALPHANUM:
                                    tokens.append(Token(TT_RW_LEAF, ident_str, line, pos.col))
                                    continue
                        
                elif self.current_char == "p":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "l":
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
                                        tokens.append(Token(TT_RW_PLANT, ident_str, line, pos.col))
                                        continue
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim6 and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        self.advance()
                                        continue
                    elif self.current_char == "o":
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
                                                        tokens.append(Token(TT_RW_POLLINATE, ident_str, line, pos.col))
                                                        continue
                                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                        self.advance()
                                                        continue
                    elif self.current_char == "r":
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
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
                                        tokens.append(Token(TT_RW_PRUNE, ident_str, line, pos.col))
                                        continue
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        self.advance()
                                        continue

                elif self.current_char == "r":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "e":
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
                                                tokens.append(Token(TT_RW_RECLAIM, ident_str, line, pos.col))
                                                continue
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                self.advance()
                                                continue
                    elif self.current_char == "o":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "o":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "t":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim7:
                                    tokens.append(Token(TT_RW_ROOT, ident_str, line, pos.col))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim7 and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue

                elif self.current_char == "s": 
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "e":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "e":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "d":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                    tokens.append(Token(TT_RW_SEED, ident_str, line, pos.col))
                                    continue
                                elif self.current_char not in ALPHANUM:
                                    tokens.append(Token(TT_RW_SEED, ident_str, line, pos.col))
                                    continue
                    elif self.current_char == "k":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "i":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "p":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
                                    tokens.append(Token(TT_RW_SKIP, ident_str, line, pos.col))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue
                    elif self.current_char == "o":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "i":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "l":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim2:
                                    tokens.append(Token(TT_RW_SOIL, ident_str, line, pos.col))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim2 and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue
                    elif self.current_char == "p":
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
                                        if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim5:
                                            tokens.append(Token(TT_RW_SPRING, ident_str, line, pos.col))
                                            continue
                                        elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim5 and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            self.advance()
                                            continue
                    elif self.current_char == "u":
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
                                                if self.current_char is None or self.current_char in delim23 or self.current_char in space_delim:
                                                    tokens.append(Token(TT_BOOLLIT_TRUE, ident_str, line, pos.col))
                                                    continue
                                                elif self.current_char not in ALPHANUM:
                                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                    self.advance()
                                                    continue

                elif self.current_char == "t":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "e":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "n":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "d":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim3:
                                    tokens.append(Token(TT_RW_TEND, ident_str, line, pos.col))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim3 and self.current_char not in ALPHANUM:
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    self.advance()
                                    continue
                    elif self.current_char == "r":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "e":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "e":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                    tokens.append(Token(TT_RW_TREE, ident_str, line, pos.col))
                                    continue
                                elif self.current_char not in ALPHANUM:
                                    tokens.append(Token(TT_RW_TREE, ident_str, line, pos.col))
                                    continue

                elif self.current_char == "v":
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
                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                    tokens.append(Token(TT_RW_VINE, ident_str, line, pos.col))
                                    continue
                                elif self.current_char not in ALPHANUM:
                                    tokens.append(Token(TT_RW_VINE, ident_str, line, pos.col))
                                    continue
                    elif self.current_char == "a":
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
                                                tokens.append(Token(TT_RW_VARIETY, ident_str, line, pos.col))
                                                continue
                                            elif self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                self.advance()
                                                continue

                elif self.current_char == "w":
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
                                if self.current_char == "r":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim6:
                                        tokens.append(Token(TT_RW_WATER, ident_str, line, pos.col))
                                        continue
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim6 and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        self.advance()
                                        continue
                    elif self.current_char == "i":
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
                                            tokens.append(Token(TT_RW_WITHER, ident_str, line, pos.col))
                                            continue
                                        elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim3 and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            self.advance()
                                            continue

                maxIdentifierLength = 15
                while self.current_char is not None and self.current_char in ALPHANUM:
                    ident_str += self.current_char
                    self.advance()

                if len(ident_str) > maxIdentifierLength:
                    i = 0
                    remaining = None
                    while i < len(ident_str):
                        if i + 15 <= len(ident_str):
                            errors.append(LexicalError(pos, f"Identifier exceeds maximum length of {maxIdentifierLength} characters"))
                            i += 15
                        else:
                            remaining = ident_str[i:]
                            if self.current_char is None or self.current_char in idf_delim:
                                tokens.append(Token(TT_IDENTIFIER, remaining, line, pos.col))
                            elif self.current_char is not None and self.current_char not in idf_delim:
                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after identifier"))
                            break
                    if remaining is None:
                        last_chunk = ident_str[i - 15:] if i >= 15 else ident_str
                        if self.current_char is None or self.current_char in idf_delim:
                            tokens.append(Token(TT_IDENTIFIER, last_chunk, line, pos.col))
                    continue
                else:
                    if self.current_char is None or self.current_char in idf_delim:
                        tokens.append(Token(TT_IDENTIFIER, ident_str, line, pos.col))
                        continue
                    elif self.current_char is not None and self.current_char not in idf_delim and self.current_char not in ALPHANUM:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        self.advance()
                        continue

            
            elif self.current_char == "-":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "-":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is not None and self.current_char not in delim25:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        self.advance()
                        continue
                    tokens.append(Token(TT_DECREMENT, ident_str, line, pos.col))
                    continue
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_MINUSEQ, ident_str, line, pos.col))
                    continue
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()
                    continue
                tokens.append(Token(TT_MINUS, ident_str, line, pos.col))
                continue
            
            elif self.current_char == "~":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()

                if self.current_char is not None and self.current_char in ZERODIGIT:
                    num_str = ""
                    integer_digit_count = 0
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        integer_digit_count += 1
                        num_str += self.current_char
                        self.advance()

                    if self.current_char == ".":
                        num_str += self.current_char
                        self.advance()
                        if self.current_char is None or self.current_char not in ZERODIGIT:
                            errors.append(LexicalError(pos, f"Invalid number '~{num_str}': decimal point must be followed by digits"))
                            continue
                        fractional_digit_count = 0
                        while self.current_char is not None and self.current_char in ZERODIGIT:
                            fractional_digit_count += 1
                            num_str += self.current_char
                            self.advance()
                        if fractional_digit_count > 8:
                            errors.append(LexicalError(pos, f"Fractional part exceeds maximum of 8 digits"))
                            continue
                        parts = num_str.split(".")
                        integer_part = parts[0].lstrip("0") or "0"
                        fractional_part = (parts[1] if len(parts) > 1 else "").rstrip("0") or "0"
                        if fractional_part == "0":
                            num_str = f"{integer_part}.0"
                        else:
                            num_str = f"{integer_part}.{fractional_part}"
                        ident_str = "~" + num_str
                        tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))
                        continue
                    else:
                        if integer_digit_count > 8:
                            errors.append(LexicalError(pos, f"Integer exceeds maximum of 8 digits"))
                            continue
                        num_str = num_str.lstrip("0") or "0"
                        ident_str = "~" + num_str
                        tokens.append(Token(TT_INTEGERLIT, ident_str, line, pos.col))
                        continue

                elif self.current_char is None or self.current_char in ALPHANUM + '( \t\n':
                    tokens.append(Token(TT_NEGATIVE, ident_str, line, pos.col))
                    continue
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'."))
                    self.advance()
                    continue
            
            elif self.current_char == "!":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:
                        errors.append(LexicalError(pos, f"Consecutive operators '{tokens[-1].value} {ident_str}' are not allowed"))
                        continue
                    tokens.append(Token(TT_NOTEQ, ident_str, line, pos.col))
                    continue
                else:
                    tokens.append(Token(TT_NOT, ident_str, line, pos.col))
                    continue
            
            elif self.current_char == "%":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_MODEQ, ident_str, line, pos.col))
                    continue
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ;' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()
                    continue
                tokens.append(Token(TT_MOD, ident_str, line, pos.col))
                continue
    
            elif self.current_char == "&":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "&":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_AND, ident_str, line, pos.col))
                    continue
                else:
                    tokens.append(Token(TT_SINGLE_AND, ident_str, line, pos.col))
                    continue
                    
            elif self.current_char == "(":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_LPAREN, ident_str, line, pos.col))
                continue
                
            elif self.current_char == ")":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_RPAREN, ident_str, line, pos.col))
                continue
                
            elif self.current_char == "*":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "*":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "=":
                        ident_str += self.current_char
                        self.advance()
                        tokens.append(Token(TT_EXPEQ, ident_str, line, pos.col))
                        continue
                    tokens.append(Token(TT_EXP, ident_str, line, pos.col))
                    continue
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_MULTIEQ, ident_str, line, pos.col))
                    continue
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()
                    continue
                tokens.append(Token(TT_MUL, ident_str, line, pos.col))
                continue
                
            elif self.current_char == ",":
                ident_str = self.current_char
                pos = self.pos.copy()
                if len(tokens) > 0 and tokens[-1].type == TT_COMMA:
                    errors.append(LexicalError(pos, f"Invalid delimiters ','"))
                    self.advance()
                    continue
                self.advance()
                tokens.append(Token(TT_COMMA, ident_str, line, pos.col))
                continue
            
                
            elif self.current_char == ";":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_SEMICOLON, ident_str, line, pos.col))
                continue
                
            elif self.current_char == "[":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_LSQBR, ident_str, line, pos.col))
                continue
                
            elif self.current_char == "]":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_RSQBR, ident_str, line, pos.col))
                continue
                
            elif self.current_char == "{":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_BLOCK_START, ident_str, line, pos.col))
                continue
                
            elif self.current_char == "}":
                ident_str = self.current_char 
                pos = self.pos.copy() 
                self.advance()
                tokens.append(Token(TT_BLOCK_END, ident_str, line, pos.col))
                continue

            elif self.current_char == "|":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "|":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_OR, ident_str, line, pos.col))
                    continue
                else:
                    tokens.append(Token(TT_SINGLE_OR, ident_str, line, pos.col))
                    continue
            
            elif self.current_char == "+":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "+":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is not None and self.current_char not in delim25:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        self.advance()
                        continue
                    tokens.append(Token(TT_INCREMENT, ident_str, line, pos.col))
                    continue
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is not None and self.current_char not in delim24:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        self.advance()
                        continue
                    tokens.append(Token(TT_PLUSEQ, ident_str, line, pos.col))
                    continue
                if self.current_char is not None and self.current_char not in delim24:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()
                    continue
                tokens.append(Token(TT_PLUS, ident_str, line, pos.col))
                continue

            elif self.current_char == "<":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_LTEQ, ident_str, line, pos.col))
                    continue
                tokens.append(Token(TT_LT, ident_str, line, pos.col))
                continue
            
            elif self.current_char == "=":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    
                    
                    if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:
                        errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                        continue
                    
                    tokens.append(Token(TT_EQTO, ident_str, line, pos.col))
                    continue
                
                tokens.append(Token(TT_EQ, ident_str, line, pos.col))
                continue

            elif self.current_char == ">":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:
                        errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                        continue
                    tokens.append(Token(TT_GTEQ, ident_str, line, pos.col))
                    continue
                if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:
                    errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                    continue
                tokens.append(Token(TT_GT, ident_str, line, pos.col))
                continue


            elif self.current_char == '\n':
                pos = self.pos.copy()
                if tokens and tokens[-1].type != TT_NL:
                    tokens.append(Token(TT_NL, "\\n", line, pos.col))

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
                continue

            elif self.current_char == ' ':
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                while self.current_char == ' ':
                    self.advance()
                continue

            elif self.current_char == "/":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                
                if self.current_char == "/":
                    ident_str += self.current_char
                    self.advance()
                    while self.current_char is not None and self.current_char != "\n":
                        ident_str += self.current_char
                        self.advance()
                    continue
                    
                elif self.current_char == "*":
                    ident_str += self.current_char
                    self.advance()
                    found_close = False
                    while self.current_char is not None:
                        if self.current_char == "*" and self.pos.index + 1 < len(self.source_code) and self.source_code[self.pos.index + 1] == "/":
                            ident_str += "*/"
                            self.advance()
                            self.advance()
                            found_close = True
                            break
                        else:
                            ident_str += self.current_char
                            if self.current_char == "\n":
                                line += 1
                            self.advance()
                    
                    if not found_close:
                        errors.append(LexicalError(pos, f"Missing closing '*/' after '{ident_str}'"))
                        continue
                    continue    
                elif self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_DIVEQ, ident_str, line, pos.col))
                    continue
                else:
                    if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        self.advance()
                        continue
                    tokens.append(Token(TT_DIV, ident_str, line, pos.col))
                    continue
            
            elif self.current_char == ".":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char is not None and self.current_char in ALPHA:
                    tokens.append(Token(TT_DOT, ident_str, line, pos.col))
                    continue

                elif self.current_char is not None and self.current_char in ZERODIGIT:
                    fractional_part = ""
                    overflow = False
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        if len(fractional_part + self.current_char) > 8: 
                            errors.append(LexicalError(pos, f"'{ident_str}' exceeds maximum number of decimal places"))
                            overflow = True
                            while self.current_char is not None and self.current_char in ZERODIGIT:
                                self.advance()
                            break

                        fractional_part += self.current_char
                        self.advance()
                    
                    if overflow:
                        continue
                        
                    ident_str = f"0.{fractional_part}"
                    tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))
                    continue
                    
                else:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()
                    continue
            
            elif self.current_char == ":":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                tokens.append(Token(TT_COLON, ident_str, line, pos.col))
                continue

            elif self.current_char in ZERODIGIT:
                dot_count = 0
                ident_str = ""
                pos = self.pos.copy()
                integer_digit_count = 0
                fractional_digit_count = 0
                has_e = False

                
                while self.current_char is not None and self.current_char in ZERODIGIT:
                    integer_digit_count += 1
                    ident_str += self.current_char
                    self.advance()

                if self.current_char == ".":
                    if integer_digit_count > 15:
                        integer_part = ident_str
                        i = 0
                        while i < len(integer_part):
                            if i + 15 < len(integer_part):
                                errors.append(LexicalError(pos, f"Integer part of decimal exceeds maximum of 15 digits"))
                                i += 15
                            else:
                                ident_str = integer_part[i:]
                                break
                        else:
                            ident_str = "0"
                    dot_count = 1
                    ident_str += self.current_char
                    self.advance()
                    
                    if self.current_char is None or self.current_char not in ZERODIGIT:
                        errors.append(LexicalError(pos, f"Invalid number '{ident_str}': decimal point must be followed by digits"))
                        continue
                    
                    fractional_part = ""
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        fractional_digit_count += 1
                        fractional_part += self.current_char
                        self.advance()
                    
                    if fractional_digit_count > 8:
                        i = 0
                        final_fractional = ""
                        while i < len(fractional_part):
                            if i + 8 < len(fractional_part):
                                errors.append(LexicalError(pos, f"Fractional part exceeds maximum of 8 digits"))
                                i += 8
                            else:
                                final_fractional = fractional_part[i:]
                                break
                        ident_str += final_fractional
                    else:
                        ident_str += fractional_part

                if dot_count == 0 and integer_digit_count > 8:
                    i = 0
                    remaining = None
                    while i < len(ident_str):
                        if i + 8 < len(ident_str):
                            errors.append(LexicalError(pos, f"Integer exceeds maximum of 8 digits"))
                            i += 8
                        else:
                            remaining = ident_str[i:]
                            remaining = remaining.lstrip("0") or "0"
                            tokens.append(Token(TT_INTEGERLIT, remaining, line, pos.col))
                            break
                    if remaining is None:
                        tokens.append(Token(TT_INTEGERLIT, "0", line, pos.col))
                    continue
                
                if fractional_digit_count > 8:
                    pass

                if self.current_char is not None and self.current_char in 'eE' and dot_count == 1:
                    has_e = True
                    ident_str += self.current_char
                    self.advance()
                    
                    if self.current_char in '+-':
                        ident_str += self.current_char
                        self.advance()
                    
                    if self.current_char is None or self.current_char not in ZERODIGIT:
                        errors.append(LexicalError(pos, f"Invalid scientific notation: 'e' must be followed by digits."))
                        continue
                    
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        ident_str += self.current_char
                        self.advance()

                if dot_count == 0 and not has_e:
                    
                    if self.current_char is not None and self.current_char not in whlnum_delim:
                        valid_int = ident_str.lstrip("0") or "0"
                        tokens.append(Token(TT_INTEGERLIT, valid_int, line, pos.col))
                        
                        if self.current_char in ALPHA:
                            temp_str = ''
                            temp_pos = self.pos.copy()
                            temp_char = self.current_char
                            while temp_char is not None and temp_char in ALPHANUM:
                                temp_str += temp_char
                                temp_pos.advance(temp_char)
                                temp_char = self.source_code[temp_pos.index] if temp_pos.index < len(self.source_code) else None
                            
                            reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', 
                                            'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', 
                                            'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}
                            
                            if temp_str in reserved_words:
                                errors.append(LexicalError(pos, f"Reserved word cannot start with a number: '{ident_str}{temp_str}'"))
                            else:
                                errors.append(LexicalError(pos, f"Identifiers cannot start with a number: '{ident_str}{self.current_char}...'"))
                            
                            while self.current_char is not None and self.current_char in ALPHANUM:
                                self.advance()
                        elif self.current_char == '_':
                            temp_index = self.pos.index + 1
                            if temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHA:
                                temp_str = ''
                                while temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHANUM:
                                    temp_str += self.source_code[temp_index]
                                    temp_index += 1
                                
                                reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', 
                                                'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', 
                                                'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}
                                
                                if temp_str in reserved_words:
                                    errors.append(LexicalError(pos, f"Reserved word cannot start with a number: '{ident_str}_{temp_str}'"))
                                else:
                                    errors.append(LexicalError(pos, f"Identifiers cannot start with a number: '{ident_str}_...'"))
                                
                                while self.current_char is not None and self.current_char in ALPHANUM:
                                    self.advance()
                            else:
                                errors.append(LexicalError(pos, f"Underscore cannot be used in numeric literals"))
                                while self.current_char is not None and self.current_char in ALPHANUM:
                                    self.advance()
                        else:
                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        continue
                    
                    ident_str = ident_str.lstrip("0") or "0"
                    tokens.append(Token(TT_INTEGERLIT, ident_str, line, pos.col))
                    continue
                    
                else:
                    if self.current_char is not None and self.current_char not in decim_delim:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        self.advance()
                        continue
                    if not has_e:
                         parts = ident_str.split(".")
                         integer_part = parts[0].lstrip("0") or "0"
                         fractional_part = (parts[1] if len(parts) > 1 else "").rstrip("0") or "0"
                         if fractional_part == "0":
                             ident_str = f"{integer_part}.0"
                         else:
                             ident_str = f"{integer_part}.{fractional_part}"

                    tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))
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
                    '}': '\\}',
                    '"': '"',
                    '\\': '\\',
                }

                has_string_error = False
                while self.current_char is not None and (self.current_char != '"' or escape_character):
                    if escape_character:
                        if self.current_char in escape_characters:
                            string += escape_characters[self.current_char]
                        else:
                            errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}' in string literal"))
                            has_string_error = True
                        escape_character = False
                    else:
                        if self.current_char == '\\':
                            escape_character = True
                        elif self.current_char == '\n':
                            break
                        else:
                            string += self.current_char
                    self.advance()

                if has_string_error:
                    while self.current_char is not None and self.current_char != '"':
                        self.advance()
                    if self.current_char == '"':
                        self.advance()
                    continue

                if self.current_char == '"':
                    string += self.current_char
                    self.advance()
                else:
                    errors.append(LexicalError(pos, f"Missing closing '\"' for string literal"))
                    continue

                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after string literal '{string}'"))
                    self.advance()
                    continue
            
                tokens.append(Token(TT_STRINGLIT, string, line, pos.col))
                continue
    
            elif self.current_char == "'":
                string = ''
                char = ''
                pos = self.pos.copy()
                string += self.current_char
                self.advance()
                has_error = False

                while self.current_char is not None and self.current_char in ' \t':
                    string += self.current_char
                    self.advance()

                while self.current_char is not None and self.current_char != "'":
                    if self.current_char == '\n':
                        break
                    elif self.current_char == '\\':
                        string += self.current_char
                        self.advance()
                        if self.current_char is None:
                            break
                        
                        if self.current_char in "'\\nt": 
                            char += f"\\{self.current_char}"
                            string += self.current_char
                        else:
                            errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}' in character literal"))
                            has_error = True
                            while self.current_char is not None and self.current_char != "'":
                                self.advance()
                            if self.current_char == "'":
                                self.advance()
                            break
                    else:
                        string += self.current_char
                        char += self.current_char
                    self.advance()
                
                while len(char) > 0 and char[-1] in ' \t':
                    char = char[:-1]

                if has_error:
                    continue

                if self.current_char == "'":
                    string += self.current_char
                    self.advance()
                else:
                    errors.append(LexicalError(pos, f"Missing closing quote for character literal"))
                    continue

                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{string}'"))
                    self.advance()
                    continue

                inner = char.strip()
                if len(inner) == 0:
                    string = "' '"
                    inner = ' '
                elif inner.startswith('\\') and len(inner) == 2:
                    pass
                elif len(inner) > 1:
                    errors.append(LexicalError(pos, f"Character literal must contain exactly one character, found '{inner}'"))
                    continue

                tokens.append(Token(TT_CHARLIT, string, line, pos.col))
                continue

            elif self.current_char == '`':
                pos = self.pos.copy()
                ident_str = self.current_char
                self.advance()
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()
                    continue
                tokens.append(Token(TT_CONCAT, ident_str, line, pos.col))
                continue

            else:
                pos = self.pos.copy()
                char = self.current_char
                
                if char == '_':
                    self.advance()
                    if self.current_char is not None and self.current_char in ALPHA:
                        temp_str = ''
                        temp_index = self.pos.index
                        while temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHANUM:
                            temp_str += self.source_code[temp_index]
                            temp_index += 1
                        
                        reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', 
                                        'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', 
                                        'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}
                        
                        if temp_str in reserved_words:
                            errors.append(LexicalError(pos, f"Reserved word cannot start with a symbol: '_{temp_str}'"))
                        else:
                            errors.append(LexicalError(pos, f"Identifiers cannot start with a symbol: '_...'"))
                        
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
                
        if self.current_char is None:
            tokens.append(Token(TT_EOF, "", line, pos.col))
        
        return tokens, errors


def run(source_code):
    lexer = Lexer(source_code)
    tokens, error = lexer.make_tokens()
    return tokens, error

def lex(source_code):
    lexer = Lexer(source_code)
    tokens, errors = lexer.make_tokens()
    
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
