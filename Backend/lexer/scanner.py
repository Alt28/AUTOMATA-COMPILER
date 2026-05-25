# ============================================================================
# LEXER SCANNER - The Lexer FSM and the lex() entry point
# ============================================================================
# Extracted from the monolithic Backend/lexer.py during the modular restructure.
# This file contains the Lexer class (character-by-character FSM) plus the
# lex() helper that wraps it. Shared types (Token, Position, LexicalError,
# TT_* constants) live in tokens.py / positions.py / errors.py and are
# imported below. Character / delimiter sets live in delimiters.py.
# ============================================================================
from shared.tokens import *  # noqa: F401,F403  - TT_* constants used heavily by the FSM
from shared.tokens import Token, get_token_description  # noqa: F401  - explicit re-export
from lexer.positions import Position
from lexer.errors import LexicalError
from lexer.delimiters import (
    ZERO, DIGIT, ZERODIGIT, LOW_ALPHA, UPPER_ALPHA, ALPHA, ALPHANUM,
    space_delim, delim2, delim3, delim4, delim5, delim6, delim7, delim8,
    delim9, delim10, delim11, delim12, delim13, delim14, delim15, delim16,
    delim17, delim18, delim19, delim20, delim21, delim22, delim23, delim24,
    idf_delim, whlnum_delim, decim_delim, comment_delim,
)


class Lexer:
    """
    The Lexer class performs lexical analysis on GAL source code.
    It scans character by character and groups them into tokens.
    """
    def __init__(self, source_code): 
        self.source_code = source_code.replace('\r', '')  # Strip carriage returns (Windows \r\n → \n)
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
        tokens = []                                                  # accumulator: every recognized Token is appended here
        line = 1                                                     # running line number (1-indexed for user-facing errors)
        errors = []                                                  # accumulator: every LexicalError encountered is appended here
        pos = self.pos.copy()                                        # snapshot of current pos; reused as fallback for EOF token at end

        # Main loop: drive the FSM one character at a time until source is exhausted (current_char becomes None).
        while self.current_char != None:                             # None sentinel = end of source_code reached

            # =====================================================================
            # KEYWORD & IDENTIFIER RECOGNITION
            # Hand-written transition diagram: each branch matches one keyword.
            # If no keyword path completes, the trailing "else" falls through to
            # generic identifier scanning at the bottom of this if-block.
            # =====================================================================
            if self.current_char in ALPHA:                           # only letters can start a keyword/identifier (digits cannot)
                ident_str = ''                                       # buffer that will hold the lexeme as we walk it character-by-character
                pos = self.pos.copy()                                # capture starting position so error/Token carries the *first* char's line/col

                # --- Letter B: 'branch', 'bud', 'bundle' ---
                if self.current_char == "b":                         # FSM root for words starting with 'b'
                    ident_str += self.current_char                   # buffer the 'b'
                    self.advance()                                   # consume it; current_char now points to the 2nd letter
                    if self.current_char == "r":                     # 'b'+'r' → potentially "branch"
                        ident_str += self.current_char               # buffer the 'r'
                        self.advance()                               # consume 'r'; look at 3rd letter
                        if self.current_char == "a":                 # 'br'+'a' → still on track for "branch"
                            ident_str += self.current_char           # buffer the 'a'
                            self.advance()                           # consume 'a'
                            if self.current_char == "n":             # 'bra'+'n'
                                ident_str += self.current_char       # buffer the 'n'
                                self.advance()                       # consume 'n'
                                if self.current_char == "c":         # 'bran'+'c'
                                    ident_str += self.current_char   # buffer the 'c'
                                    self.advance()                   # consume 'c'
                                    if self.current_char == "h":     # 'branc'+'h' → full keyword spelled out
                                        ident_str += self.current_char  # buffer the trailing 'h'
                                        self.advance()               # consume 'h'; current_char is now whatever comes AFTER "branch"
                                        # Maximal-munch check: only emit BRANCH token if the next char is a legal delimiter.
                                        # Otherwise "branchx" must become an identifier, not keyword+identifier.
                                        if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                            tokens.append(Token(TT_RW_BRANCH, ident_str, line, pos.col))  # emit reserved-word token
                                            continue                 # restart the outer while loop — do NOT fall through to identifier scan
                                        elif self.current_char not in ALPHANUM:  # any non-alphanumeric (e.g. '(', '{') also closes the keyword
                                            tokens.append(Token(TT_RW_BRANCH, ident_str, line, pos.col))  # emit reserved-word token
                                            continue                 # restart the outer while loop
                    elif self.current_char == "u":                       # 'b'+'u' → either "bud" or "bundle"
                        ident_str += self.current_char                   # buffer the 'u'
                        self.advance()                                   # consume 'u'
                        if self.current_char == "d":                     # 'bu'+'d' → potentially "bud"
                            ident_str += self.current_char               # buffer the 'd'
                            self.advance()                               # consume 'd'; check what follows
                            # Maximal-munch: "bud" needs whitespace or delim4 ({':', '('}) to terminate.
                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:
                                tokens.append(Token(TT_RW_BUD, ident_str, line, pos.col))  # emit BUD reserved-word token
                                continue                                 # restart outer loop on next char
                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                # Strict rule: an illegal delimiter after the keyword is a lexical error (not a fallback to identifier).
                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                self.advance()                           # skip the bad char so we don't loop forever
                                continue                                 # back to outer scan
                        elif self.current_char == "n":                   # 'bu'+'n' → potentially "bundle"
                            ident_str += self.current_char               # buffer 'n'
                            self.advance()                               # consume 'n'
                            if self.current_char == "d":                 # 'bun'+'d'
                                ident_str += self.current_char           # buffer 'd'
                                self.advance()                           # consume 'd'
                                if self.current_char == "l":             # 'bund'+'l'
                                    ident_str += self.current_char       # buffer 'l'
                                    self.advance()                       # consume 'l'
                                    if self.current_char == "e":         # 'bundl'+'e' → "bundle" complete
                                        ident_str += self.current_char   # buffer trailing 'e'
                                        self.advance()                   # consume 'e'
                                        if self.current_char is not None and self.current_char in space_delim:  # bundle requires whitespace next
                                            tokens.append(Token(TT_RW_BUNDLE, ident_str, line, pos.col))  # emit BUNDLE token
                                            continue                     # next iteration
                                        elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                            # Anything else (and not a letter that would extend it to an identifier) → illegal delimiter error.
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            self.advance()               # skip bad char
                                            continue                     # restart outer scan

                #Letter C
                elif self.current_char == "c":                           # FSM root for words starting with 'c' (only "cultivate")
                    ident_str += self.current_char                       # buffer 'c'
                    self.advance()                                       # consume 'c'
                    if self.current_char == "u":                         # 'c'+'u' → on track for "cultivate"
                        ident_str += self.current_char                   # buffer 'u'
                        self.advance()                                   # consume 'u'
                        if self.current_char == "l":                     # 'cu'+'l'
                            ident_str += self.current_char               # buffer 'l'
                            self.advance()                               # consume 'l'
                            if self.current_char == "t":                 # 'cul'+'t'
                                ident_str += self.current_char           # buffer 't'
                                self.advance()                           # consume 't'
                                if self.current_char == "i":             # 'cult'+'i'
                                    ident_str += self.current_char       # buffer 'i'
                                    self.advance()                       # consume 'i'
                                    if self.current_char == "v":         # 'culti'+'v'
                                        ident_str += self.current_char   # buffer 'v'
                                        self.advance()                   # consume 'v'
                                        if self.current_char == "a":     # 'cultiv'+'a'
                                            ident_str += self.current_char  # buffer 'a'
                                            self.advance()               # consume 'a'
                                            if self.current_char == "t": # 'cultiva'+'t'
                                                ident_str += self.current_char  # buffer 't'
                                                self.advance()           # consume 't'
                                                if self.current_char == "e":  # 'cultivat'+'e' → "cultivate" complete
                                                    ident_str += self.current_char  # buffer trailing 'e'
                                                    self.advance()       # consume 'e'
                                                    # cultivate (for-loop) requires whitespace or delim4 ({':', '('}) next.
                                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:
                                                        tokens.append(Token(TT_RW_CULTIVATE, ident_str, line, pos.col))  # emit CULTIVATE token
                                                        continue         # next iteration
                                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))  # illegal trailer
                                                        self.advance()   # skip bad char
                                                        continue         # restart outer scan

                # Letter E
                elif self.current_char == "e":                           # FSM root for 'e' (only "empty")
                    ident_str += self.current_char                       # buffer 'e'
                    self.advance()                                       # consume 'e'
                    if self.current_char == "m":                         # 'e'+'m' → potentially "empty"
                        ident_str += self.current_char                   # buffer 'm'
                        self.advance()                                   # consume 'm'
                        if self.current_char == "p":                     # 'em'+'p'
                            ident_str += self.current_char               # buffer 'p'
                            self.advance()                               # consume 'p'
                            if self.current_char == "t":                 # 'emp'+'t'
                                ident_str += self.current_char           # buffer 't'
                                self.advance()                           # consume 't'
                                if self.current_char == "y":             # 'empt'+'y' → "empty" complete
                                    ident_str += self.current_char       # buffer trailing 'y'
                                    self.advance()                       # consume 'y'
                                    # empty is the void return type; whitespace is a valid delimiter.
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                        tokens.append(Token(TT_RW_EMPTY, ident_str, line, pos.col))  # emit EMPTY token
                                        continue                         # next iteration
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))  # illegal trailer
                                        self.advance()                   # skip bad char
                                        continue                         # restart outer scan

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
                                        tokens.append(Token(TT_BOOLLIT_FALSE, ident_str, line, pos.col)) # Boolean Literal
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
                                                tokens.append(Token(TT_RW_FERTILE, ident_str, line, pos.col))
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
                                    tokens.append(Token(TT_RW_GROW, ident_str, line, pos.col))
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
                                                tokens.append(Token(TT_RW_HARVEST, ident_str, line, pos.col))
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
                                # Leaf keyword recognized - emit token
                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                    tokens.append(Token(TT_RW_LEAF, ident_str, line, pos.col))
                                    continue
                                elif self.current_char not in ALPHANUM:
                                    tokens.append(Token(TT_RW_LEAF, ident_str, line, pos.col))
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
                                        tokens.append(Token(TT_RW_PLANT, ident_str, line, pos.col))
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
                                                        tokens.append(Token(TT_RW_POLLINATE, ident_str, line, pos.col))
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
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
                                        tokens.append(Token(TT_RW_PRUNE, ident_str, line, pos.col))
                                        continue
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
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
                                                tokens.append(Token(TT_RW_RECLAIM, ident_str, line, pos.col))
                                                continue
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                self.advance()
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
                                    tokens.append(Token(TT_RW_ROOT, ident_str, line, pos.col))
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
                                # Seed keyword recognized - emit token
                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                    tokens.append(Token(TT_RW_SEED, ident_str, line, pos.col))
                                    continue
                                elif self.current_char not in ALPHANUM:
                                    tokens.append(Token(TT_RW_SEED, ident_str, line, pos.col))
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
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
                                    tokens.append(Token(TT_RW_SKIP, ident_str, line, pos.col))
                                    continue
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
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
                                    tokens.append(Token(TT_RW_SOIL, ident_str, line, pos.col))
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
                                            tokens.append(Token(TT_RW_SPRING, ident_str, line, pos.col))
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
                                                if self.current_char is None or (self.current_char not in ALPHANUM and self.current_char != '_'):
                                                    tokens.append(Token(TT_BOOLLIT_TRUE, ident_str, line, pos.col)) # Boolean Literal
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
                                    tokens.append(Token(TT_RW_TEND, ident_str, line, pos.col))
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
                                # Tree keyword recognized - emit token
                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                    tokens.append(Token(TT_RW_TREE, ident_str, line, pos.col))
                                    continue
                                elif self.current_char not in ALPHANUM:
                                    tokens.append(Token(TT_RW_TREE, ident_str, line, pos.col))
                                    continue

                # Letter V
                elif self.current_char == "v":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "i": # vine
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
                    elif self.current_char == "a": # variety
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
                                            # variety must be followed by expression, not alphanumeric continuation  
                                            if self.current_char is None or self.current_char not in ALPHANUM:
                                                tokens.append(Token(TT_RW_VARIETY, ident_str, line, pos.col))
                                                continue
                                            # If followed by alphanum, continue to identifier parsing

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
                                        tokens.append(Token(TT_RW_WATER, ident_str, line, pos.col))
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
                                            tokens.append(Token(TT_RW_WITHER, ident_str, line, pos.col))
                                            continue
                                        elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim3 and self.current_char not in ALPHANUM:
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            self.advance()
                                            continue

                #Identifier            
                maxIdentifierLength = 15 # Changed from 20 to 15
                while self.current_char is not None and self.current_char in ALPHANUM:
                    ident_str += self.current_char
                    self.advance()

                # Check if identifier exceeds max length
                if len(ident_str) > maxIdentifierLength:
                    # Process in chunks of 15: each 15-char chunk is an error
                    # Only the final remaining chunk (≤14 chars) is valid and added to tokens
                    i = 0
                    remaining = None
                    while i < len(ident_str):
                        # Check if there are at least 15 characters remaining
                        if i + 15 <= len(ident_str):
                            # 15-char chunk: generate error, don't add token
                            errors.append(LexicalError(pos, f"Identifier exceeds maximum length of {maxIdentifierLength} characters"))
                            i += 15
                        else:
                            # Final chunk with 14 or fewer characters: valid token
                            remaining = ident_str[i:]
                            if self.current_char is None or self.current_char in idf_delim:
                                tokens.append(Token(TT_IDENTIFIER, remaining, line, pos.col))
                            elif self.current_char is not None and self.current_char not in idf_delim:
                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after identifier"))
                            break
                    if remaining is None:
                        # Length was exact multiple of 15 — all chars consumed as errors
                        # Still create a token with the last chunk
                        last_chunk = ident_str[i - 15:] if i >= 15 else ident_str
                        if self.current_char is None or self.current_char in idf_delim:
                            tokens.append(Token(TT_IDENTIFIER, last_chunk, line, pos.col))
                    continue
                else:
                    # Identifier is within max length
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
                    # Tokenize -- as DECREMENT operator
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_DECREMENT, ident_str, line, pos.col))
                    continue
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_MINUSEQ, ident_str, line, pos.col))
                    continue
                # Check for valid delimiter after -
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()  # Consume invalid delimiter
                    continue  # Don't add token - eat the error
                tokens.append(Token(TT_MINUS, ident_str, line, pos.col))
                continue
            
            elif self.current_char == "~": # Added for negative prefix
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()

                # If ~ is directly followed by a digit, consume the number as a negative literal
                if self.current_char is not None and self.current_char in ZERODIGIT:
                    # Read integer digits
                    num_str = ""
                    integer_digit_count = 0
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        integer_digit_count += 1
                        num_str += self.current_char
                        self.advance()

                    # Check for decimal point (negative double)
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
                        # Format the double
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
                        # Negative integer
                        if integer_digit_count > 8:
                            errors.append(LexicalError(pos, f"Integer exceeds maximum of 8 digits"))
                            continue
                        num_str = num_str.lstrip("0") or "0"
                        ident_str = "~" + num_str
                        tokens.append(Token(TT_INTEGERLIT, ident_str, line, pos.col))
                        continue

                # ~ not followed by a digit: emit as the arithmetic-negation operator.
                # Permit a directly grouped operand, such as ~(x + 1).
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
                    # Check for consecutive comparison operators
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
                # Check for valid delimiter after %
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ;' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()  # Consume invalid delimiter
                    continue  # Don't add token - eat the error
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
                    # Emit single & token for parser to detect
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
                    tokens.append(Token(TT_EXP, ident_str, line, pos.col))
                    continue
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_MULTIEQ, ident_str, line, pos.col))
                    continue
                # Check for valid delimiter after *
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()  # Consume invalid delimiter
                    continue  # Don't add token - eat the error
                tokens.append(Token(TT_MUL, ident_str, line, pos.col))
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
                tokens.append(Token(TT_COMMA, ident_str, line, pos.col))
                continue
            
            # This entire block is for a token that isn't really a token.
            # The logic for escape sequences is handled *inside* the string and char
            # literal parsers. This block should be removed.
            # elif self.current_char == "\\":
            #     ...
                
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
                    # Emit single | token for parser to detect
                    tokens.append(Token(TT_SINGLE_OR, ident_str, line, pos.col))
                    continue
            
            elif self.current_char == "+":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "+":
                    # Tokenize ++ as INCREMENT operator
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_INCREMENT, ident_str, line, pos.col))
                    continue
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    tokens.append(Token(TT_PLUSEQ, ident_str, line, pos.col))
                    continue
                # Check for valid delimiter after +
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()  # Consume invalid delimiter
                    continue  # Don't add token - eat the error
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
                    
                    # Don't check for third '=' - let it tokenize as separate '=' token
                    # Parser will detect the pattern '==' followed by '='
                    
                    # Prevent consecutive comparison operators (e.g., "< ==" or "> ==")
                    if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:
                        errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                        continue
                    
                    # Valid '==' (equality comparison operator)
                    tokens.append(Token(TT_EQTO, ident_str, line, pos.col))
                    continue
                
                # Single '=' (assignment operator)
                tokens.append(Token(TT_EQ, ident_str, line, pos.col))
                continue

            elif self.current_char == ">":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    # Check for consecutive comparison operators
                    if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:
                        errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                        continue
                    tokens.append(Token(TT_GTEQ, ident_str, line, pos.col))
                    continue
                # Check for consecutive comparison operators
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
                    found_close = False
                    # Consume all characters until closing */
                    while self.current_char is not None:
                        # Check for closing */ sequence
                        if self.current_char == "*" and self.pos.index + 1 < len(self.source_code) and self.source_code[self.pos.index + 1] == "/":
                            ident_str += "*/"
                            self.advance()  # Skip *
                            self.advance()  # Skip /
                            found_close = True
                            break
                        else:
                            ident_str += self.current_char
                            if self.current_char == "\n":  # Track line numbers inside comment
                                line += 1
                            self.advance()
                    # Comments are NOT added to tokens (they are skipped)
                    
                    # Error if comment was never closed
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
                    # Check for valid delimiter after /
                    if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        self.advance()  # Consume invalid delimiter
                        continue  # Don't add token - eat the error
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
                            # Consume remaining digits to avoid cascading errors
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

            # =====================================================================
            # 
            # 
            # =====================================================================
            elif self.current_char in ZERODIGIT:
                dot_count = 0               # Count decimal points (max 1)
                ident_str = ""              # Build the number string
                pos = self.pos.copy()       # Save position for errors
                integer_digit_count = 0     # Count digits before decimal (max 15)
                fractional_digit_count = 0  # Count digits after decimal (max 8)
                has_e = False               # Track if scientific notation (e.g., 1e10)

                
                # Read all digits before decimal point
                while self.current_char is not None and self.current_char in ZERODIGIT:
                    integer_digit_count += 1
                    ident_str += self.current_char
                    self.advance()

                # Step 2: Check for decimal point (converts to double/float)
                if self.current_char == ".":
                    # For decimals, check if integer part exceeds 15 digits
                    if integer_digit_count > 15:
                        # Process integer part in chunks of 15: each 15-digit chunk is an error
                        # Only the final remaining chunk (≤15 digits) continues to decimal processing
                        integer_part = ident_str
                        i = 0
                        while i < len(integer_part):
                            if i + 15 < len(integer_part):
                                # More than 15 digits remain: generate error for this chunk
                                errors.append(LexicalError(pos, f"Integer part of decimal exceeds maximum of 15 digits"))
                                i += 15
                            else:
                                # Final chunk with 15 or fewer digits — valid
                                ident_str = integer_part[i:]
                                break
                        else:
                            # All digits consumed as errors, no valid remainder
                            ident_str = "0"
                    dot_count = 1  # Mark that we found a decimal point
                    ident_str += self.current_char
                    self.advance()
                    
                    # After decimal point, must have at least one digit (e.g., "3." is invalid)
                    if self.current_char is None or self.current_char not in ZERODIGIT:
                        errors.append(LexicalError(pos, f"Invalid number '{ident_str}': decimal point must be followed by digits"))
                        continue
                    
                    # Read fractional part (digits after decimal point)
                    fractional_part = ""
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        fractional_digit_count += 1
                        fractional_part += self.current_char
                        self.advance()
                    
                    # Check if fractional part exceeds 8 digits
                    if fractional_digit_count > 8:
                        # Process in chunks of 8: each 8-digit chunk is an error
                        # Only the final remaining chunk (≤8 digits) is added to the number
                        i = 0
                        final_fractional = ""
                        while i < len(fractional_part):
                            if i + 8 < len(fractional_part):
                                # More than 8 digits remain: generate error for this chunk
                                errors.append(LexicalError(pos, f"Fractional part exceeds maximum of 8 digits"))
                                i += 8
                            else:
                                # Final chunk with 8 or fewer digits — valid
                                final_fractional = fractional_part[i:]
                                break
                        ident_str += final_fractional
                    else:
                        ident_str += fractional_part

                # Handle integers longer than 8 digits
                # Process in chunks of 8: each chunk beyond the valid last ≤8 digits is an error
                if dot_count == 0 and integer_digit_count > 8:
                    i = 0
                    remaining = None
                    while i < len(ident_str):
                        # Check if more than 8 characters remain
                        if i + 8 < len(ident_str):
                            # More than 8 digits remain: generate error for this chunk
                            errors.append(LexicalError(pos, f"Integer exceeds maximum of 8 digits"))
                            i += 8
                        else:
                            # Final chunk with 8 or fewer digits: valid token
                            remaining = ident_str[i:]
                            # Strip leading zeros for the remaining valid portion
                            remaining = remaining.lstrip("0") or "0"
                            tokens.append(Token(TT_INTEGERLIT, remaining, line, pos.col))
                            break
                    if remaining is None:
                        # Safety fallback (should not happen with the corrected condition)
                        tokens.append(Token(TT_INTEGERLIT, "0", line, pos.col))
                    continue
                
                if fractional_digit_count > 8:
                    # Error already reported and fractional part already truncated above.
                    # Fall through to create a token with the truncated valid portion.
                    pass

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
                    # Integer literal - type checking is done by the parser (SYNTAX error)
                    
                    # Check for valid delimiter after integer
                    if self.current_char is not None and self.current_char not in whlnum_delim:
                        # Strip leading zeros and tokenize the valid integer first
                        valid_int = ident_str.lstrip("0") or "0"
                        tokens.append(Token(TT_INTEGERLIT, valid_int, line, pos.col))
                        
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
                                            'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}
                            
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
                                                'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}
                                
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
                            # Invalid delimiter error already added when integer was tokenized
                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                            # Don't consume the character - let the main loop handle it
                        continue
                    
                    ident_str = ident_str.lstrip("0") or "0"
                    tokens.append(Token(TT_INTEGERLIT, ident_str, line, pos.col))
                    continue
                    
                else:  # Float case
                    # Check for valid delimiter after double
                    if self.current_char is not None and self.current_char not in decim_delim:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        self.advance()
                        continue
                    if not has_e: # Only re-format if not scientific notation
                         parts = ident_str.split(".")
                         integer_part = parts[0].lstrip("0") or "0"
                         fractional_part = (parts[1] if len(parts) > 1 else "").rstrip("0") or "0"
                         if fractional_part == "0":
                             ident_str = f"{integer_part}.0" # Keep at least one zero
                         else:
                             ident_str = f"{integer_part}.{fractional_part}"

                    tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))
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
                    '}': '\\}',  # Literal right brace
                    '"': '"',    # Escaped double quote
                    '\\': '\\',  # Escaped backslash
                }

                has_string_error = False
                # Read until closing quote (or end of file)
                while self.current_char is not None and (self.current_char != '"' or escape_character):
                    if escape_character:
                        # Process escape sequence (e.g., \n becomes newline)
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
                    # Consume rest of string to avoid cascading errors
                    while self.current_char is not None and self.current_char != '"':
                        self.advance()
                    if self.current_char == '"':
                        self.advance()
                    continue

                if self.current_char == '"':
                    string += self.current_char
                    self.advance()
                else:
                    # Missing closing quote - report error and skip (don't create token)
                    errors.append(LexicalError(pos, f"Missing closing '\"' for string literal"))
                    continue

                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after string literal '{string}'"))
                    self.advance()
                    continue
            
                # Token stores the REAL characters (like C compilers do).
                # Display escaping is handled separately in the server.
                tokens.append(Token(TT_STRINGLIT, string, line, pos.col))
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
                    # Missing closing quote - report error and skip (don't create token)
                    errors.append(LexicalError(pos, f"Missing closing quote for character literal"))
                    continue

                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{string}'"))
                    self.advance()
                    continue

                # Character literal must contain exactly one character (or one escape sequence)
                # Strip quotes to get inner content
                inner = char.strip()
                if len(inner) == 0:
                    # Empty char literal '' defaults to a space character
                    string = "' '"
                    inner = ' '
                elif inner.startswith('\\') and len(inner) == 2:
                    # Valid escape sequence like \n, \t
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
                # Check for valid delimiter after `
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()
                    continue
                tokens.append(Token(TT_CONCAT, ident_str, line, pos.col))
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
                                        'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}
                        
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
            tokens.append(Token(TT_EOF, "", line, pos.col))
        
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
