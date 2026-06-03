"""Lexer/scanner for GAL source code.

The scanner walks through source_code one character at a time with current_char
and advance(), then produces Token objects plus any LexicalError messages.
"""

# AUTO: Imports names from another module.
from shared.tokens import *  # noqa: F401,F403  - TT_* constants used heavily by the FSM
# AUTO: Imports names from another module.
from shared.tokens import Token, get_token_description  # noqa: F401  - explicit re-export
# AUTO: Imports names from another module.
from lexer.positions import Position
# AUTO: Imports names from another module.
from lexer.errors import LexicalError
# AUTO: Imports names from another module.
from lexer.delimiters import (
    # AUTO: Executes this statement.
    ZERO, DIGIT, ZERODIGIT, LOW_ALPHA, UPPER_ALPHA, ALPHA, ALPHANUM,
    # AUTO: Executes this statement.
    space_delim, delim2, delim3, delim4, delim5, delim6, delim7, delim8,
    # AUTO: Executes this statement.
    delim9, delim10, delim11, delim12, delim13, delim14, delim15, delim16,
    # AUTO: Executes this statement.
    delim17, delim18, delim19, delim20, delim21, delim22, delim23, delim24,
    # AUTO: Executes this statement.
    delim25, delim26,
    # AUTO: Executes this statement.
    idf_delim, whlnum_delim, decim_delim, comment_delim,
    # AUTO: Executes this statement.
    statement_end_delim, open_paren_delim, close_paren_delim,
    # AUTO: Executes this statement.
    open_bracket_delim, close_bracket_delim, block_start_delim,
    # AUTO: Executes this statement.
    block_end_delim, case_colon_delim, after_comma_delim,
# AUTO: Closes the current grouped code/data.
)


# AUTO: Defines class `Lexer`.
class Lexer:
    # AUTO: Defines function `__init__`.
    def __init__(self, source_code): 
        # GUIDE: Normalize Windows newlines so line/column tracking is consistent.
        # source_code is the full text from the editor. The lexer does not
        # understand the whole program at once; it scans this string one
        # character at a time.
        # LINE: Store the editor text and remove '\r' so Windows line endings are stable.
        self.source_code = source_code.replace('\r', '')

        # Position starts before the first character. Calling advance() below
        # moves it to index 0 and loads the first current_char.
        # LINE: Start before the first character so advance() loads index 0.
        self.pos = Position(-1, 1, -1)
        # LINE: current_char holds the one character currently being scanned.
        self.current_char = None
        # LINE: Move to the first character of source_code.
        self.advance()

    # AUTO: Defines function `advance`.
    def advance(self):
        # GUIDE: Move one character forward and update Position before reading again.
        # self.current_char is the character being processed right now.
        # self.pos stores index, line, and column for that character.
        # LINE: Update index, line, and column using the previous character.
        self.pos.advance(self.current_char)

        # If the index is still inside source_code, load the next character.
        # If the index already passed the text length, current_char becomes None,
        # which means the lexer reached end of file.
        # LINE: Load the next character, or set None when the source is finished.
        self.current_char = self.source_code[self.pos.index] if self.pos.index<len(self.source_code) else None

    # AUTO: Defines function `make_tokens`.
    def make_tokens(self):
        # GUIDE: Main finite-state scan; each branch recognizes one token family.
        # tokens collects successful Token objects.
        # errors collects LexicalError objects if a character/token is invalid.
        # LINE: tokens is the output list sent to parser and lexeme table.
        tokens = []
        # LINE: line stores the source line number for each token.
        line = 1
        # LINE: errors stores lexical errors found while scanning.
        errors = []
        # LINE: pos remembers where the current token starts.
        pos = self.pos.copy()

        # This loop continues until advance() reaches the end and sets
        # current_char to None.
        # LINE: Main scanner loop; one token is built each pass.
        while self.current_char != None:

            # AUTO: Checks this condition.
            if self.current_char in ALPHA:
                # GUIDE: Reserved words are checked first; unfinished matches fall back
                # to the identifier collector near the end of this alpha branch.
                # ident_str temporarily stores the letters collected for the
                # current word. Example: reading seed builds "s", "se", "see",
                # "seed" before deciding if it is a reserved word or id.
                # LINE: ident_str builds the word text one character at a time.
                ident_str = ''
                # LINE: Save this word's starting column for token/error reporting.
                pos = self.pos.copy()

                # AUTO: Checks this condition.
                if self.current_char == "b":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "r":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "a":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "n":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "c":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char == "h":
                                        # AUTO: Adds into `ident_str`.
                                        ident_str += self.current_char
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Checks this condition.
                                        if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                            # AUTO: Appends a value to a list.
                                            tokens.append(Token(TT_RW_BRANCH, ident_str, line, pos.col))
                                            # AUTO: Skips to the next loop iteration.
                                            continue
                                        # AUTO: Checks the next alternate condition.
                                        elif self.current_char not in ALPHANUM:
                                            # AUTO: Appends a value to a list.
                                            tokens.append(Token(TT_RW_BRANCH, ident_str, line, pos.col))
                                            # AUTO: Skips to the next loop iteration.
                                            continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "u":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "d":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:
                                # AUTO: Appends a value to a list.
                                tokens.append(Token(TT_RW_BUD, ident_str, line, pos.col))
                                # AUTO: Skips to the next loop iteration.
                                continue
                            # AUTO: Checks the next alternate condition.
                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                # AUTO: Appends a value to a list.
                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Skips to the next loop iteration.
                                continue
                        # AUTO: Checks the next alternate condition.
                        elif self.current_char == "n":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "d":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "l":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char == "e":
                                        # AUTO: Adds into `ident_str`.
                                        ident_str += self.current_char
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Checks this condition.
                                        if self.current_char is not None and self.current_char in space_delim:
                                            # AUTO: Appends a value to a list.
                                            tokens.append(Token(TT_RW_BUNDLE, ident_str, line, pos.col))
                                            # AUTO: Skips to the next loop iteration.
                                            continue
                                        # AUTO: Checks the next alternate condition.
                                        elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                            # AUTO: Appends a value to a list.
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            # AUTO: Calls `self.advance`.
                                            self.advance()
                                            # AUTO: Skips to the next loop iteration.
                                            continue

                # AUTO: Checks the next alternate condition.
                elif self.current_char == "c":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "u":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "l":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "t":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "i":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char == "v":
                                        # AUTO: Adds into `ident_str`.
                                        ident_str += self.current_char
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Checks this condition.
                                        if self.current_char == "a":
                                            # AUTO: Adds into `ident_str`.
                                            ident_str += self.current_char
                                            # AUTO: Calls `self.advance`.
                                            self.advance()
                                            # AUTO: Checks this condition.
                                            if self.current_char == "t":
                                                # AUTO: Adds into `ident_str`.
                                                ident_str += self.current_char
                                                # AUTO: Calls `self.advance`.
                                                self.advance()
                                                # AUTO: Checks this condition.
                                                if self.current_char == "e":
                                                    # AUTO: Adds into `ident_str`.
                                                    ident_str += self.current_char
                                                    # AUTO: Calls `self.advance`.
                                                    self.advance()
                                                    # AUTO: Checks this condition.
                                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:
                                                        # AUTO: Appends a value to a list.
                                                        tokens.append(Token(TT_RW_CULTIVATE, ident_str, line, pos.col))
                                                        # AUTO: Skips to the next loop iteration.
                                                        continue
                                                    # AUTO: Checks the next alternate condition.
                                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                                        # AUTO: Appends a value to a list.
                                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                        # AUTO: Calls `self.advance`.
                                                        self.advance()
                                                        # AUTO: Skips to the next loop iteration.
                                                        continue

                # AUTO: Checks the next alternate condition.
                elif self.current_char == "e":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "m":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "p":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "t":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "y":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                        # AUTO: Appends a value to a list.
                                        tokens.append(Token(TT_RW_EMPTY, ident_str, line, pos.col))
                                        # AUTO: Skips to the next loop iteration.
                                        continue
                                    # AUTO: Checks the next alternate condition.
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                        # AUTO: Appends a value to a list.
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Skips to the next loop iteration.
                                        continue

                # AUTO: Checks the next alternate condition.
                elif self.current_char == "f":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "r":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "o":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "s":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "t":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char is None or (self.current_char not in ALPHANUM and self.current_char != '_'):
                                        # AUTO: Appends a value to a list.
                                        tokens.append(Token(TT_BOOLLIT_FALSE, ident_str, line, pos.col))
                                        # AUTO: Skips to the next loop iteration.
                                        continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "e":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "r":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "t":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "i":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char == "l":
                                        # AUTO: Adds into `ident_str`.
                                        ident_str += self.current_char
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Checks this condition.
                                        if self.current_char == "e":
                                            # AUTO: Adds into `ident_str`.
                                            ident_str += self.current_char
                                            # AUTO: Calls `self.advance`.
                                            self.advance()
                                            # AUTO: Checks this condition.
                                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
                                                # AUTO: Appends a value to a list.
                                                tokens.append(Token(TT_RW_FERTILE, ident_str, line, pos.col))
                                                # AUTO: Skips to the next loop iteration.
                                                continue
                                            # AUTO: Checks the next alternate condition.
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                                # AUTO: Appends a value to a list.
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                # AUTO: Calls `self.advance`.
                                                self.advance()
                                                # AUTO: Skips to the next loop iteration.
                                                continue
                                            
                # AUTO: Checks the next alternate condition.
                elif self.current_char == "g":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "r":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "o":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "w":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4 or self.current_char in space_delim:
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_GROW, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                # AUTO: Checks the next alternate condition.
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                    # AUTO: Appends a value to a list.
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                
                # AUTO: Checks the next alternate condition.
                elif self.current_char == "h":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "a":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "r":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "v":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "e":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char == "s":
                                        # AUTO: Adds into `ident_str`.
                                        ident_str += self.current_char
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Checks this condition.
                                        if self.current_char == "t":
                                            # AUTO: Adds into `ident_str`.
                                            ident_str += self.current_char
                                            # AUTO: Calls `self.advance`.
                                            self.advance()
                                            # AUTO: Checks this condition.
                                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:
                                                # AUTO: Appends a value to a list.
                                                tokens.append(Token(TT_RW_HARVEST, ident_str, line, pos.col))
                                                # AUTO: Skips to the next loop iteration.
                                                continue
                                            # AUTO: Checks the next alternate condition.
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
                                                # AUTO: Appends a value to a list.
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                # AUTO: Calls `self.advance`.
                                                self.advance()
                                                # AUTO: Skips to the next loop iteration.
                                                continue
                                
                # AUTO: Checks the next alternate condition.
                elif self.current_char == "l":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "e":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "a":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "f":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_LEAF, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                # AUTO: Checks the next alternate condition.
                                elif self.current_char not in ALPHANUM:
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_LEAF, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                        
                # AUTO: Checks the next alternate condition.
                elif self.current_char == "p":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "l":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "a":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "n":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "t":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim6:
                                        # AUTO: Appends a value to a list.
                                        tokens.append(Token(TT_RW_PLANT, ident_str, line, pos.col))
                                        # AUTO: Skips to the next loop iteration.
                                        continue
                                    # AUTO: Checks the next alternate condition.
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim6 and self.current_char not in ALPHANUM:
                                        # AUTO: Appends a value to a list.
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Skips to the next loop iteration.
                                        continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "o":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "l":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "l":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "i":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char == "n":
                                        # AUTO: Adds into `ident_str`.
                                        ident_str += self.current_char
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Checks this condition.
                                        if self.current_char == "a":
                                            # AUTO: Adds into `ident_str`.
                                            ident_str += self.current_char
                                            # AUTO: Calls `self.advance`.
                                            self.advance()
                                            # AUTO: Checks this condition.
                                            if self.current_char == "t":
                                                # AUTO: Adds into `ident_str`.
                                                ident_str += self.current_char
                                                # AUTO: Calls `self.advance`.
                                                self.advance()
                                                # AUTO: Checks this condition.
                                                if self.current_char == "e":
                                                    # AUTO: Adds into `ident_str`.
                                                    ident_str += self.current_char
                                                    # AUTO: Calls `self.advance`.
                                                    self.advance()
                                                    # AUTO: Checks this condition.
                                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:
                                                        # AUTO: Appends a value to a list.
                                                        tokens.append(Token(TT_RW_POLLINATE, ident_str, line, pos.col))
                                                        # AUTO: Skips to the next loop iteration.
                                                        continue
                                                    # AUTO: Checks the next alternate condition.
                                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:
                                                        # AUTO: Appends a value to a list.
                                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                        # AUTO: Calls `self.advance`.
                                                        self.advance()
                                                        # AUTO: Skips to the next loop iteration.
                                                        continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "r":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "u":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "n":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "e":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
                                        # AUTO: Appends a value to a list.
                                        tokens.append(Token(TT_RW_PRUNE, ident_str, line, pos.col))
                                        # AUTO: Skips to the next loop iteration.
                                        continue
                                    # AUTO: Checks the next alternate condition.
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                        # AUTO: Appends a value to a list.
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Skips to the next loop iteration.
                                        continue

                # AUTO: Checks the next alternate condition.
                elif self.current_char == "r":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "e":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "c":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "l":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "a":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char == "i":
                                        # AUTO: Adds into `ident_str`.
                                        ident_str += self.current_char
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Checks this condition.
                                        if self.current_char == "m":
                                            # AUTO: Adds into `ident_str`.
                                            ident_str += self.current_char
                                            # AUTO: Calls `self.advance`.
                                            self.advance()
                                            # AUTO: Checks this condition.
                                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
                                                # AUTO: Appends a value to a list.
                                                tokens.append(Token(TT_RW_RECLAIM, ident_str, line, pos.col))
                                                # AUTO: Skips to the next loop iteration.
                                                continue
                                            # AUTO: Checks the next alternate condition.
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                                # AUTO: Appends a value to a list.
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                # AUTO: Calls `self.advance`.
                                                self.advance()
                                                # AUTO: Skips to the next loop iteration.
                                                continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "o":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "o":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "t":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim7:
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_ROOT, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                # AUTO: Checks the next alternate condition.
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim7 and self.current_char not in ALPHANUM:
                                    # AUTO: Appends a value to a list.
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Skips to the next loop iteration.
                                    continue

                # AUTO: Checks the next alternate condition.
                elif self.current_char == "s": 
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "e":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "e":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "d":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_SEED, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                # AUTO: Checks the next alternate condition.
                                elif self.current_char not in ALPHANUM:
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_SEED, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "k":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "i":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "p":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_SKIP, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                # AUTO: Checks the next alternate condition.
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                    # AUTO: Appends a value to a list.
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "o":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "i":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "l":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim2:
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_SOIL, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                # AUTO: Checks the next alternate condition.
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim2 and self.current_char not in ALPHANUM:
                                    # AUTO: Appends a value to a list.
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "p":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "r":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "i":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "n":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char == "g":
                                        # AUTO: Adds into `ident_str`.
                                        ident_str += self.current_char
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Checks this condition.
                                        if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim5:
                                            # AUTO: Appends a value to a list.
                                            tokens.append(Token(TT_RW_SPRING, ident_str, line, pos.col))
                                            # AUTO: Skips to the next loop iteration.
                                            continue
                                        # AUTO: Checks the next alternate condition.
                                        elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim5 and self.current_char not in ALPHANUM:
                                            # AUTO: Appends a value to a list.
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            # AUTO: Calls `self.advance`.
                                            self.advance()
                                            # AUTO: Skips to the next loop iteration.
                                            continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "u":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "n":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "s":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "h":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char == "i":
                                        # AUTO: Adds into `ident_str`.
                                        ident_str += self.current_char
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Checks this condition.
                                        if self.current_char == "n":
                                            # AUTO: Adds into `ident_str`.
                                            ident_str += self.current_char
                                            # AUTO: Calls `self.advance`.
                                            self.advance()
                                            # AUTO: Checks this condition.
                                            if self.current_char == "e":
                                                # AUTO: Adds into `ident_str`.
                                                ident_str += self.current_char
                                                # AUTO: Calls `self.advance`.
                                                self.advance()
                                                # AUTO: Checks this condition.
                                                if self.current_char is None or self.current_char in delim23 or self.current_char in space_delim:
                                                    # AUTO: Appends a value to a list.
                                                    tokens.append(Token(TT_BOOLLIT_TRUE, ident_str, line, pos.col))
                                                    # AUTO: Skips to the next loop iteration.
                                                    continue
                                                # AUTO: Checks the next alternate condition.
                                                elif self.current_char not in ALPHANUM:
                                                    # AUTO: Appends a value to a list.
                                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                    # AUTO: Calls `self.advance`.
                                                    self.advance()
                                                    # AUTO: Skips to the next loop iteration.
                                                    continue

                # AUTO: Checks the next alternate condition.
                elif self.current_char == "t":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "e":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "n":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "d":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim3:
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_TEND, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                # AUTO: Checks the next alternate condition.
                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim3 and self.current_char not in ALPHANUM:
                                    # AUTO: Appends a value to a list.
                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "r":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "e":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "e":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_TREE, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                # AUTO: Checks the next alternate condition.
                                elif self.current_char not in ALPHANUM:
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_TREE, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue

                # AUTO: Checks the next alternate condition.
                elif self.current_char == "v":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "i":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "n":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "e":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_VINE, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                # AUTO: Checks the next alternate condition.
                                elif self.current_char not in ALPHANUM:
                                    # AUTO: Appends a value to a list.
                                    tokens.append(Token(TT_RW_VINE, ident_str, line, pos.col))
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "a":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "r":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "i":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "e":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char == "t":
                                        # AUTO: Adds into `ident_str`.
                                        ident_str += self.current_char
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Checks this condition.
                                        if self.current_char == "y":
                                            # AUTO: Adds into `ident_str`.
                                            ident_str += self.current_char
                                            # AUTO: Calls `self.advance`.
                                            self.advance()
                                            # AUTO: Checks this condition.
                                            if self.current_char is None or self.current_char in space_delim:
                                                # AUTO: Appends a value to a list.
                                                tokens.append(Token(TT_RW_VARIETY, ident_str, line, pos.col))
                                                # AUTO: Skips to the next loop iteration.
                                                continue
                                            # AUTO: Checks the next alternate condition.
                                            elif self.current_char not in ALPHANUM:
                                                # AUTO: Appends a value to a list.
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                # AUTO: Calls `self.advance`.
                                                self.advance()
                                                # AUTO: Skips to the next loop iteration.
                                                continue

                # AUTO: Checks the next alternate condition.
                elif self.current_char == "w":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "a":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "t":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "e":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "r":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim6:
                                        # AUTO: Appends a value to a list.
                                        tokens.append(Token(TT_RW_WATER, ident_str, line, pos.col))
                                        # AUTO: Skips to the next loop iteration.
                                        continue
                                    # AUTO: Checks the next alternate condition.
                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim6 and self.current_char not in ALPHANUM:
                                        # AUTO: Appends a value to a list.
                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Skips to the next loop iteration.
                                        continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == "i":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char == "t":
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "h":
                                # AUTO: Adds into `ident_str`.
                                ident_str += self.current_char
                                # AUTO: Calls `self.advance`.
                                self.advance()
                                # AUTO: Checks this condition.
                                if self.current_char == "e":
                                    # AUTO: Adds into `ident_str`.
                                    ident_str += self.current_char
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                                    # AUTO: Checks this condition.
                                    if self.current_char == "r":
                                        # AUTO: Adds into `ident_str`.
                                        ident_str += self.current_char
                                        # AUTO: Calls `self.advance`.
                                        self.advance()
                                        # AUTO: Checks this condition.
                                        if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim3:
                                            # AUTO: Appends a value to a list.
                                            tokens.append(Token(TT_RW_WITHER, ident_str, line, pos.col))
                                            # AUTO: Skips to the next loop iteration.
                                            continue
                                        # AUTO: Checks the next alternate condition.
                                        elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim3 and self.current_char not in ALPHANUM:
                                            # AUTO: Appends a value to a list.
                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                            # AUTO: Calls `self.advance`.
                                            self.advance()
                                            # AUTO: Skips to the next loop iteration.
                                            continue

                # AUTO: Sets `maxIdentifierLength`.
                maxIdentifierLength = 15
                # LINE: If reserved-word matching failed, collect the rest as an identifier.
                while self.current_char is not None and self.current_char in ALPHANUM:
                    # If the reserved-word checks above did not finish with a
                    # continue, the word is not a reserved word. This loop
                    # collects the rest of the identifier.
                    # Example: "roof" starts through the "root" path, but when
                    # the expected "t" is not found, the remaining "f" is
                    # collected here and the final token becomes id("roof").
                    # LINE: Append the current letter/digit into the identifier text.
                    ident_str += self.current_char
                    # LINE: Move to the next character after adding this one.
                    self.advance()

                # LINE: Check if the finished identifier is too long.
                if len(ident_str) > maxIdentifierLength:
                    # LINE: i marks where the next 15-character chunk starts.
                    i = 0
                    # LINE: remaining becomes the final valid chunk if there is one.
                    remaining = None
                    # LINE: Split very long identifiers into chunks for error reporting.
                    while i < len(ident_str):
                        # AUTO: Checks this condition.
                        if i + 15 <= len(ident_str):
                            # LINE: Report each over-limit chunk as a lexical error.
                            errors.append(LexicalError(pos, f"Identifier exceeds maximum length of {maxIdentifierLength} characters"))
                            # LINE: Skip to the next 15-character chunk.
                            i += 15
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # LINE: Keep the leftover identifier characters after the long chunks.
                            remaining = ident_str[i:]
                            # LINE: Accept leftover only if the next character can legally end an id.
                            if self.current_char is None or self.current_char in idf_delim:
                                # LINE: Add the leftover identifier token to the token list.
                                tokens.append(Token(TT_IDENTIFIER, remaining, line, pos.col))
                            # AUTO: Checks the next alternate condition.
                            elif self.current_char is not None and self.current_char not in idf_delim:
                                # LINE: The character after the id is illegal, so report delimiter error.
                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after identifier"))
                            # AUTO: Stops the nearest loop.
                            break
                    # LINE: If there was no leftover, keep the last collected chunk as identifier output.
                    if remaining is None:
                        # AUTO: Executes this statement.
                        last_chunk = ident_str[i - 15:] if i >= 15 else ident_str
                        # AUTO: Checks this condition.
                        if self.current_char is None or self.current_char in idf_delim:
                            # AUTO: Appends a value to a list.
                            tokens.append(Token(TT_IDENTIFIER, last_chunk, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Runs when previous condition did not pass.
                else:
                    # LINE: Normal identifier path for words within the length limit.
                    if self.current_char is None or self.current_char in idf_delim:
                        # The identifier is complete because the next character
                        # is a valid delimiter like space, semicolon, operator,
                        # parenthesis, or EOF.
                        # LINE: Save the identifier token, like id(num) or id(roof).
                        tokens.append(Token(TT_IDENTIFIER, ident_str, line, pos.col))
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char is not None and self.current_char not in idf_delim and self.current_char not in ALPHANUM:
                        # The collected word is valid, but the next character is
                        # not allowed after an identifier.
                        # LINE: Report invalid delimiter after an identifier.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # LINE: Move past the bad character so scanning can continue.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue

            
            # AUTO: Checks the next alternate condition.
            elif self.current_char == "-":
                # GUIDE: Symbol/operator states validate the next character with
                # delimiter sets so tokens like -=, --, and - are separated.
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char == "-":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim25:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_DECREMENT, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Checks this condition.
                if self.current_char == "=":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim24:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_MINUSEQ, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in delim24:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_MINUS, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue
            
            # AUTO: Checks the next alternate condition.
            elif self.current_char == "~":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()

                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char in ZERODIGIT:
                    # AUTO: Sets `num_str`.
                    num_str = ""
                    # AUTO: Sets `integer_digit_count`.
                    integer_digit_count = 0
                    # AUTO: Repeats while this condition is true.
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        # AUTO: Adds into `integer_digit_count`.
                        integer_digit_count += 1
                        # AUTO: Adds into `num_str`.
                        num_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()

                    # AUTO: Checks this condition.
                    if self.current_char == ".":
                        # AUTO: Adds into `num_str`.
                        num_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char is None or self.current_char not in ZERODIGIT:
                            # AUTO: Appends a value to a list.
                            errors.append(LexicalError(pos, f"Invalid number '~{num_str}': decimal point must be followed by digits"))
                            # AUTO: Skips to the next loop iteration.
                            continue
                        # AUTO: Sets `fractional_digit_count`.
                        fractional_digit_count = 0
                        # AUTO: Repeats while this condition is true.
                        while self.current_char is not None and self.current_char in ZERODIGIT:
                            # AUTO: Adds into `fractional_digit_count`.
                            fractional_digit_count += 1
                            # AUTO: Adds into `num_str`.
                            num_str += self.current_char
                            # AUTO: Calls `self.advance`.
                            self.advance()
                        # AUTO: Checks this condition.
                        if fractional_digit_count > 8:
                            # AUTO: Appends a value to a list.
                            errors.append(LexicalError(pos, f"Fractional part exceeds maximum of 8 digits"))
                            # AUTO: Skips to the next loop iteration.
                            continue
                        # AUTO: Sets `parts`.
                        parts = num_str.split(".")
                        # AUTO: Sets `integer_part`.
                        integer_part = parts[0].lstrip("0") or "0"
                        # AUTO: Sets `fractional_part`.
                        fractional_part = (parts[1] if len(parts) > 1 else "").rstrip("0") or "0"
                        # AUTO: Checks this condition.
                        if fractional_part == "0":
                            # AUTO: Sets `num_str`.
                            num_str = f"{integer_part}.0"
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Sets `num_str`.
                            num_str = f"{integer_part}.{fractional_part}"
                        # AUTO: Sets `ident_str`.
                        ident_str = "~" + num_str
                        # AUTO: Appends a value to a list.
                        tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Checks this condition.
                        if integer_digit_count > 8:
                            # AUTO: Appends a value to a list.
                            errors.append(LexicalError(pos, f"Integer exceeds maximum of 8 digits"))
                            # AUTO: Skips to the next loop iteration.
                            continue
                        # AUTO: Sets `num_str`.
                        num_str = num_str.lstrip("0") or "0"
                        # AUTO: Sets `ident_str`.
                        ident_str = "~" + num_str
                        # AUTO: Appends a value to a list.
                        tokens.append(Token(TT_INTEGERLIT, ident_str, line, pos.col))
                        # AUTO: Skips to the next loop iteration.
                        continue

                # AUTO: Checks the next alternate condition.
                elif self.current_char is None or self.current_char in ALPHANUM + '( \t\n':
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_NEGATIVE, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'."))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
            
            # AUTO: Checks the next alternate condition.
            elif self.current_char == "!":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char == "=":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Consecutive operators '{tokens[-1].value} {ident_str}' are not allowed"))
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim24:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_NOTEQ, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim26:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_NOT, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
            
            # AUTO: Checks the next alternate condition.
            elif self.current_char == "%":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char == "=":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim25:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_MODEQ, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in delim25:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_MOD, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue
    
            # AUTO: Checks the next alternate condition.
            elif self.current_char == "&":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char == "&":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim21:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_AND, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_SINGLE_AND, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                    
            # AUTO: Checks the next alternate condition.
            elif self.current_char == "(":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in open_paren_delim:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_LPAREN, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == ")":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in close_paren_delim:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_RPAREN, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue
                
            # AUTO: Checks the next alternate condition.
            elif self.current_char == "*":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char == "*":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == "=":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char is not None and self.current_char not in delim24:
                            # AUTO: Appends a value to a list.
                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Skips to the next loop iteration.
                            continue
                        # AUTO: Appends a value to a list.
                        tokens.append(Token(TT_EXPEQ, ident_str, line, pos.col))
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim24:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_EXP, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Checks this condition.
                if self.current_char == "=":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim24:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_MULTIEQ, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in delim24:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_MUL, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue
                
            # AUTO: Checks the next alternate condition.
            elif self.current_char == ",":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Checks this condition.
                if len(tokens) > 0 and tokens[-1].type == TT_COMMA:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiters ','"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in after_comma_delim:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after ','"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_COMMA, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue


            # AUTO: Checks the next alternate condition.
            elif self.current_char == ";":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in statement_end_delim:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after ';'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_SEMICOLON, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == "[":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in open_bracket_delim:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '['"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_LSQBR, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == "]":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in close_bracket_delim:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after ']'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_RSQBR, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == "{":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in block_start_delim:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{{'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_BLOCK_START, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == "}":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in block_end_delim:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '}}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_BLOCK_END, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == "|":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char == "|":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim21:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_OR, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_SINGLE_OR, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
            
            # AUTO: Checks the next alternate condition.
            elif self.current_char == "+":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char == "+":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim25:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_INCREMENT, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Checks this condition.
                if self.current_char == "=":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim24:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_PLUSEQ, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in delim24:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_PLUS, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == "<":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char == "=":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim24:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_LTEQ, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in delim24:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_LT, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == "=":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()

                # AUTO: Checks this condition.
                if self.current_char == "=":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()


                    # AUTO: Checks this condition.
                    if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                        # AUTO: Skips to the next loop iteration.
                        continue

                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim24:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue

                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_EQTO, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue

                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in delim24:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_EQ, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == ">":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char == "=":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim24:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_GTEQ, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Checks this condition.
                if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in delim24:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_GT, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue


            # AUTO: Checks the next alternate condition.
            elif self.current_char == '\n':
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Checks this condition.
                if tokens and tokens[-1].type != TT_NL:
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_NL, "\\n", line, pos.col))

                # AUTO: Repeats while this condition is true.
                while self.current_char == '\t' or self.current_char == ' ' or self.current_char == '\n':
                    # AUTO: Checks this condition.
                    if self.current_char == '\t' or self.current_char == ' ':
                        # AUTO: Calls `self.advance`.
                        self.advance()
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Adds into `line`.
                        line += 1
                        # AUTO: Calls `self.advance`.
                        self.advance()

                # AUTO: Skips to the next loop iteration.
                continue
                
            # AUTO: Checks the next alternate condition.
            elif self.current_char == '\t':
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Repeats while this condition is true.
                while self.current_char == '\t':
                    # AUTO: Calls `self.advance`.
                    self.advance()
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == ' ':
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Repeats while this condition is true.
                while self.current_char == ' ':
                    # AUTO: Calls `self.advance`.
                    self.advance()
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == "/":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                
                # AUTO: Checks this condition.
                if self.current_char == "/":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Repeats while this condition is true.
                    while self.current_char is not None and self.current_char != "\n":
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                    # Comments are emitted as tokens so they show up in the
                    # lexeme table, but they are filtered out before parsing
                    # (see strip_comments) so the parser never sees them.
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_COMMENT, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue

                # AUTO: Checks the next alternate condition.
                elif self.current_char == "*":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Sets `found_close`.
                    found_close = False
                    # AUTO: Repeats while this condition is true.
                    while self.current_char is not None:
                        # AUTO: Checks this condition.
                        if self.current_char == "*" and self.pos.index + 1 < len(self.source_code) and self.source_code[self.pos.index + 1] == "/":
                            # AUTO: Adds into `ident_str`.
                            ident_str += "*/"
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Calls `self.advance`.
                            self.advance()
                            # AUTO: Sets `found_close`.
                            found_close = True
                            # AUTO: Stops the nearest loop.
                            break
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Adds into `ident_str`.
                            ident_str += self.current_char
                            # AUTO: Checks this condition.
                            if self.current_char == "\n":
                                # AUTO: Adds into `line`.
                                line += 1
                            # AUTO: Calls `self.advance`.
                            self.advance()

                    # AUTO: Checks this condition.
                    if not found_close:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Missing closing '*/' after '{ident_str}'"))
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # Multi-line comments are emitted for the lexeme table and
                    # filtered out before parsing (see strip_comments).
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_MCOMMENT, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Checks the next alternate condition.
                elif self.current_char == "=":
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim24:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_DIVEQ, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in delim25:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_DIV, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
            
            # AUTO: Checks the next alternate condition.
            elif self.current_char == ".":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char in ALPHA:
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_DOT, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue

                # AUTO: Checks the next alternate condition.
                elif self.current_char is not None and self.current_char in ZERODIGIT:
                    # AUTO: Sets `fractional_part`.
                    fractional_part = ""
                    # AUTO: Sets `overflow`.
                    overflow = False
                    # AUTO: Repeats while this condition is true.
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        # AUTO: Checks this condition.
                        if len(fractional_part + self.current_char) > 8: 
                            # AUTO: Appends a value to a list.
                            errors.append(LexicalError(pos, f"'{ident_str}' exceeds maximum number of decimal places"))
                            # AUTO: Sets `overflow`.
                            overflow = True
                            # AUTO: Repeats while this condition is true.
                            while self.current_char is not None and self.current_char in ZERODIGIT:
                                # AUTO: Calls `self.advance`.
                                self.advance()
                            # AUTO: Stops the nearest loop.
                            break

                        # AUTO: Adds into `fractional_part`.
                        fractional_part += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                    
                    # AUTO: Checks this condition.
                    if overflow:
                        # AUTO: Skips to the next loop iteration.
                        continue
                        
                    # AUTO: Sets `ident_str`.
                    ident_str = f"0.{fractional_part}"
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                    
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
            
            # AUTO: Checks the next alternate condition.
            elif self.current_char == ":":
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in case_colon_delim:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after ':'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_COLON, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char in ZERODIGIT:
                # GUIDE: Numeric literal state collects integers, doubles, and
                # scientific notation before deciding intlit vs dblit.
                # AUTO: Sets `dot_count`.
                dot_count = 0
                # AUTO: Sets `ident_str`.
                ident_str = ""
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Sets `integer_digit_count`.
                integer_digit_count = 0
                # AUTO: Sets `fractional_digit_count`.
                fractional_digit_count = 0
                # AUTO: Sets `has_e`.
                has_e = False

                
                # AUTO: Repeats while this condition is true.
                while self.current_char is not None and self.current_char in ZERODIGIT:
                    # AUTO: Adds into `integer_digit_count`.
                    integer_digit_count += 1
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()

                # AUTO: Checks this condition.
                if self.current_char == ".":
                    # AUTO: Checks this condition.
                    if integer_digit_count > 15:
                        # AUTO: Sets `integer_part`.
                        integer_part = ident_str
                        # AUTO: Sets `i`.
                        i = 0
                        # AUTO: Repeats while this condition is true.
                        while i < len(integer_part):
                            # AUTO: Checks this condition.
                            if i + 15 < len(integer_part):
                                # AUTO: Appends a value to a list.
                                errors.append(LexicalError(pos, f"Integer part of decimal exceeds maximum of 15 digits"))
                                # AUTO: Adds into `i`.
                                i += 15
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Sets `ident_str`.
                                ident_str = integer_part[i:]
                                # AUTO: Stops the nearest loop.
                                break
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Sets `ident_str`.
                            ident_str = "0"
                    # AUTO: Sets `dot_count`.
                    dot_count = 1
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    
                    # AUTO: Checks this condition.
                    if self.current_char is None or self.current_char not in ZERODIGIT:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid number '{ident_str}': decimal point must be followed by digits"))
                        # AUTO: Skips to the next loop iteration.
                        continue
                    
                    # AUTO: Sets `fractional_part`.
                    fractional_part = ""
                    # AUTO: Repeats while this condition is true.
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        # AUTO: Adds into `fractional_digit_count`.
                        fractional_digit_count += 1
                        # AUTO: Adds into `fractional_part`.
                        fractional_part += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                    
                    # AUTO: Checks this condition.
                    if fractional_digit_count > 8:
                        # AUTO: Sets `i`.
                        i = 0
                        # AUTO: Sets `final_fractional`.
                        final_fractional = ""
                        # AUTO: Repeats while this condition is true.
                        while i < len(fractional_part):
                            # AUTO: Checks this condition.
                            if i + 8 < len(fractional_part):
                                # AUTO: Appends a value to a list.
                                errors.append(LexicalError(pos, f"Fractional part exceeds maximum of 8 digits"))
                                # AUTO: Adds into `i`.
                                i += 8
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Sets `final_fractional`.
                                final_fractional = fractional_part[i:]
                                # AUTO: Stops the nearest loop.
                                break
                        # AUTO: Adds into `ident_str`.
                        ident_str += final_fractional
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Adds into `ident_str`.
                        ident_str += fractional_part

                # AUTO: Checks this condition.
                if dot_count == 0 and integer_digit_count > 8:
                    # AUTO: Sets `i`.
                    i = 0
                    # AUTO: Sets `remaining`.
                    remaining = None
                    # AUTO: Repeats while this condition is true.
                    while i < len(ident_str):
                        # AUTO: Checks this condition.
                        if i + 8 < len(ident_str):
                            # AUTO: Appends a value to a list.
                            errors.append(LexicalError(pos, f"Integer exceeds maximum of 8 digits"))
                            # AUTO: Adds into `i`.
                            i += 8
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Sets `remaining`.
                            remaining = ident_str[i:]
                            # AUTO: Sets `remaining`.
                            remaining = remaining.lstrip("0") or "0"
                            # AUTO: Appends a value to a list.
                            tokens.append(Token(TT_INTEGERLIT, remaining, line, pos.col))
                            # AUTO: Stops the nearest loop.
                            break
                    # AUTO: Checks this condition.
                    if remaining is None:
                        # AUTO: Appends a value to a list.
                        tokens.append(Token(TT_INTEGERLIT, "0", line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                
                # AUTO: Checks this condition.
                if fractional_digit_count > 8:
                    # AUTO: Does nothing for this required block.
                    pass

                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char in 'eE' and dot_count == 1:
                    # AUTO: Sets `has_e`.
                    has_e = True
                    # AUTO: Adds into `ident_str`.
                    ident_str += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    
                    # AUTO: Checks this condition.
                    if self.current_char in '+-':
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                    
                    # AUTO: Checks this condition.
                    if self.current_char is None or self.current_char not in ZERODIGIT:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid scientific notation: 'e' must be followed by digits."))
                        # AUTO: Skips to the next loop iteration.
                        continue
                    
                    # AUTO: Repeats while this condition is true.
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        # AUTO: Adds into `ident_str`.
                        ident_str += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()

                # AUTO: Checks this condition.
                if dot_count == 0 and not has_e:
                    
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in whlnum_delim:
                        # AUTO: Sets `valid_int`.
                        valid_int = ident_str.lstrip("0") or "0"
                        # AUTO: Appends a value to a list.
                        tokens.append(Token(TT_INTEGERLIT, valid_int, line, pos.col))
                        
                        # AUTO: Checks this condition.
                        if self.current_char in ALPHA:
                            # AUTO: Sets `temp_str`.
                            temp_str = ''
                            # AUTO: Sets `temp_pos`.
                            temp_pos = self.pos.copy()
                            # AUTO: Sets `temp_char`.
                            temp_char = self.current_char
                            # AUTO: Repeats while this condition is true.
                            while temp_char is not None and temp_char in ALPHANUM:
                                # AUTO: Adds into `temp_str`.
                                temp_str += temp_char
                                # AUTO: Calls `temp_pos.advance`.
                                temp_pos.advance(temp_char)
                                # AUTO: Sets `temp_char`.
                                temp_char = self.source_code[temp_pos.index] if temp_pos.index < len(self.source_code) else None
                            
                            # AUTO: Sets `reserved_words`.
                            reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', 
                                            # AUTO: Executes this statement.
                                            'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', 
                                            # AUTO: Executes this statement.
                                            'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}
                            
                            # AUTO: Checks this condition.
                            if temp_str in reserved_words:
                                # AUTO: Appends a value to a list.
                                errors.append(LexicalError(pos, f"Reserved word cannot start with a number: '{ident_str}{temp_str}'"))
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Appends a value to a list.
                                errors.append(LexicalError(pos, f"Identifiers cannot start with a number: '{ident_str}{self.current_char}...'"))
                            
                            # AUTO: Repeats while this condition is true.
                            while self.current_char is not None and self.current_char in ALPHANUM:
                                # AUTO: Calls `self.advance`.
                                self.advance()
                        # AUTO: Checks the next alternate condition.
                        elif self.current_char == '_':
                            # AUTO: Sets `temp_index`.
                            temp_index = self.pos.index + 1
                            # AUTO: Checks this condition.
                            if temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHA:
                                # AUTO: Sets `temp_str`.
                                temp_str = ''
                                # AUTO: Repeats while this condition is true.
                                while temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHANUM:
                                    # AUTO: Adds into `temp_str`.
                                    temp_str += self.source_code[temp_index]
                                    # AUTO: Adds into `temp_index`.
                                    temp_index += 1
                                
                                # AUTO: Sets `reserved_words`.
                                reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', 
                                                # AUTO: Executes this statement.
                                                'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', 
                                                # AUTO: Executes this statement.
                                                'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}
                                
                                # AUTO: Checks this condition.
                                if temp_str in reserved_words:
                                    # AUTO: Appends a value to a list.
                                    errors.append(LexicalError(pos, f"Reserved word cannot start with a number: '{ident_str}_{temp_str}'"))
                                # AUTO: Runs when previous condition did not pass.
                                else:
                                    # AUTO: Appends a value to a list.
                                    errors.append(LexicalError(pos, f"Identifiers cannot start with a number: '{ident_str}_...'"))
                                
                                # AUTO: Repeats while this condition is true.
                                while self.current_char is not None and self.current_char in ALPHANUM:
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Appends a value to a list.
                                errors.append(LexicalError(pos, f"Underscore cannot be used in numeric literals"))
                                # AUTO: Repeats while this condition is true.
                                while self.current_char is not None and self.current_char in ALPHANUM:
                                    # AUTO: Calls `self.advance`.
                                    self.advance()
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Appends a value to a list.
                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Skips to the next loop iteration.
                        continue
                    
                    # AUTO: Sets `ident_str`.
                    ident_str = ident_str.lstrip("0") or "0"
                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_INTEGERLIT, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue
                    
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char not in decim_delim:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Checks this condition.
                    if not has_e:
                         # AUTO: Sets `parts`.
                         parts = ident_str.split(".")
                         # AUTO: Sets `integer_part`.
                         integer_part = parts[0].lstrip("0") or "0"
                         # AUTO: Sets `fractional_part`.
                         fractional_part = (parts[1] if len(parts) > 1 else "").rstrip("0") or "0"
                         # AUTO: Checks this condition.
                         if fractional_part == "0":
                             # AUTO: Sets `ident_str`.
                             ident_str = f"{integer_part}.0"
                         # AUTO: Runs when previous condition did not pass.
                         else:
                             # AUTO: Sets `ident_str`.
                             ident_str = f"{integer_part}.{fractional_part}"

                    # AUTO: Appends a value to a list.
                    tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))
                    # AUTO: Skips to the next loop iteration.
                    continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == '"':
                # GUIDE: String literals keep the quotes in the token value so the
                # parser sees the whole quoted text as one stringlit token.
                # AUTO: Sets `string`.
                string = ''
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Sets `escape_character`.
                escape_character = False
                # AUTO: Adds into `string`.
                string += self.current_char
                # AUTO: Calls `self.advance`.
                self.advance()

                # AUTO: Sets `escape_characters`.
                escape_characters = {
                    # AUTO: Executes this statement.
                    'n': '\n',
                    # AUTO: Executes this statement.
                    't': '\t',
                    # AUTO: Executes this statement.
                    '{': '\\{',
                    # AUTO: Executes this statement.
                    '}': '\\}',
                    # AUTO: Executes this statement.
                    '"': '"',
                    # AUTO: Executes this statement.
                    '\\': '\\',
                # AUTO: Closes the current grouped code/data.
                }

                # AUTO: Sets `has_string_error`.
                has_string_error = False
                # AUTO: Repeats while this condition is true.
                while self.current_char is not None and (self.current_char != '"' or escape_character):
                    # AUTO: Checks this condition.
                    if escape_character:
                        # AUTO: Checks this condition.
                        if self.current_char in escape_characters:
                            # AUTO: Adds into `string`.
                            string += escape_characters[self.current_char]
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Appends a value to a list.
                            errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}' in string literal"))
                            # AUTO: Sets `has_string_error`.
                            has_string_error = True
                        # AUTO: Sets `escape_character`.
                        escape_character = False
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Checks this condition.
                        if self.current_char == '\\':
                            # AUTO: Sets `escape_character`.
                            escape_character = True
                        # AUTO: Checks the next alternate condition.
                        elif self.current_char == '\n':
                            # AUTO: Stops the nearest loop.
                            break
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Adds into `string`.
                            string += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()

                # AUTO: Checks this condition.
                if has_string_error:
                    # AUTO: Repeats while this condition is true.
                    while self.current_char is not None and self.current_char != '"':
                        # AUTO: Calls `self.advance`.
                        self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char == '"':
                        # AUTO: Calls `self.advance`.
                        self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue

                # AUTO: Checks this condition.
                if self.current_char == '"':
                    # AUTO: Adds into `string`.
                    string += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Missing closing '\"' for string literal"))
                    # AUTO: Skips to the next loop iteration.
                    continue

                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after string literal '{string}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
            
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_STRINGLIT, string, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue
    
            # AUTO: Checks the next alternate condition.
            elif self.current_char == "'":
                # AUTO: Sets `string`.
                string = ''
                # AUTO: Sets `char`.
                char = ''
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Adds into `string`.
                string += self.current_char
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Sets `has_error`.
                has_error = False

                # AUTO: Repeats while this condition is true.
                while self.current_char is not None and self.current_char in ' \t':
                    # AUTO: Adds into `string`.
                    string += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()

                # AUTO: Repeats while this condition is true.
                while self.current_char is not None and self.current_char != "'":
                    # AUTO: Checks this condition.
                    if self.current_char == '\n':
                        # AUTO: Stops the nearest loop.
                        break
                    # AUTO: Checks the next alternate condition.
                    elif self.current_char == '\\':
                        # AUTO: Adds into `string`.
                        string += self.current_char
                        # AUTO: Calls `self.advance`.
                        self.advance()
                        # AUTO: Checks this condition.
                        if self.current_char is None:
                            # AUTO: Stops the nearest loop.
                            break
                        
                        # AUTO: Checks this condition.
                        if self.current_char in "'\\nt": 
                            # AUTO: Adds into `char`.
                            char += f"\\{self.current_char}"
                            # AUTO: Adds into `string`.
                            string += self.current_char
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Appends a value to a list.
                            errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}' in character literal"))
                            # AUTO: Sets `has_error`.
                            has_error = True
                            # AUTO: Repeats while this condition is true.
                            while self.current_char is not None and self.current_char != "'":
                                # AUTO: Calls `self.advance`.
                                self.advance()
                            # AUTO: Checks this condition.
                            if self.current_char == "'":
                                # AUTO: Calls `self.advance`.
                                self.advance()
                            # AUTO: Stops the nearest loop.
                            break
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Adds into `string`.
                        string += self.current_char
                        # AUTO: Adds into `char`.
                        char += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                
                # AUTO: Repeats while this condition is true.
                while len(char) > 0 and char[-1] in ' \t':
                    # AUTO: Sets `char`.
                    char = char[:-1]

                # AUTO: Checks this condition.
                if has_error:
                    # AUTO: Skips to the next loop iteration.
                    continue

                # AUTO: Checks this condition.
                if self.current_char == "'":
                    # AUTO: Adds into `string`.
                    string += self.current_char
                    # AUTO: Calls `self.advance`.
                    self.advance()
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Missing closing quote for character literal"))
                    # AUTO: Skips to the next loop iteration.
                    continue

                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{string}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue

                # AUTO: Sets `inner`.
                inner = char.strip()
                # AUTO: Checks this condition.
                if len(inner) == 0:
                    # AUTO: Sets `string`.
                    string = "' '"
                    # AUTO: Sets `inner`.
                    inner = ' '
                # AUTO: Checks the next alternate condition.
                elif inner.startswith('\\') and len(inner) == 2:
                    # AUTO: Does nothing for this required block.
                    pass
                # AUTO: Checks the next alternate condition.
                elif len(inner) > 1:
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Character literal must contain exactly one character, found '{inner}'"))
                    # AUTO: Skips to the next loop iteration.
                    continue

                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_CHARLIT, string, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Checks the next alternate condition.
            elif self.current_char == '`':
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Sets `ident_str`.
                ident_str = self.current_char
                # AUTO: Calls `self.advance`.
                self.advance()
                # AUTO: Checks this condition.
                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Skips to the next loop iteration.
                    continue
                # AUTO: Appends a value to a list.
                tokens.append(Token(TT_CONCAT, ident_str, line, pos.col))
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Sets `pos`.
                pos = self.pos.copy()
                # AUTO: Sets `char`.
                char = self.current_char
                
                # AUTO: Checks this condition.
                if char == '_':
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Checks this condition.
                    if self.current_char is not None and self.current_char in ALPHA:
                        # AUTO: Sets `temp_str`.
                        temp_str = ''
                        # AUTO: Sets `temp_index`.
                        temp_index = self.pos.index
                        # AUTO: Repeats while this condition is true.
                        while temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHANUM:
                            # AUTO: Adds into `temp_str`.
                            temp_str += self.source_code[temp_index]
                            # AUTO: Adds into `temp_index`.
                            temp_index += 1
                        
                        # AUTO: Sets `reserved_words`.
                        reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', 
                                        # AUTO: Executes this statement.
                                        'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', 
                                        # AUTO: Executes this statement.
                                        'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}
                        
                        # AUTO: Checks this condition.
                        if temp_str in reserved_words:
                            # AUTO: Appends a value to a list.
                            errors.append(LexicalError(pos, f"Reserved word cannot start with a symbol: '_{temp_str}'"))
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Appends a value to a list.
                            errors.append(LexicalError(pos, f"Identifiers cannot start with a symbol: '_...'"))
                        
                        # AUTO: Repeats while this condition is true.
                        while self.current_char is not None and self.current_char in ALPHANUM:
                            # AUTO: Calls `self.advance`.
                            self.advance()
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Appends a value to a list.
                        errors.append(LexicalError(pos, f"Illegal Character '{char}'"))
                        # AUTO: Skips to the next loop iteration.
                        continue
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Calls `self.advance`.
                    self.advance()
                    # AUTO: Appends a value to a list.
                    errors.append(LexicalError(pos, f"Illegal Character '" + char + "'"))
                    # AUTO: Skips to the next loop iteration.
                    continue
                
        # AUTO: Checks this condition.
        if self.current_char is None:
            # LINE: Add EOF so the parser knows the token stream is finished.
            tokens.append(Token(TT_EOF, "", line, pos.col))
        
        # LINE: Return both successful tokens and raw lexical errors.
        return tokens, errors


# AUTO: Defines function `run`.
def run(source_code):
    # GUIDE: Legacy wrapper used by older callers.
    # LINE: Create a lexer object for this source text.
    lexer = Lexer(source_code)
    # LINE: Scan the full source into tokens/errors.
    tokens, error = lexer.make_tokens()
    # LINE: Return the scanner result to the caller.
    return tokens, error

# AUTO: Defines function `lex`.
def lex(source_code):
    # GUIDE: Public lexer API used by server.py before parsing or execution.
    # LINE: Server calls this function with the editor source code.
    lexer = Lexer(source_code)
    # LINE: make_tokens performs the actual character-by-character scan.
    tokens, errors = lexer.make_tokens()

    # Report lexical errors one at a time — only surface the first.
    # The user fixes it, re-runs, and sees the next one (if any).
    # LINE: Convert LexicalError objects into frontend-ready strings.
    str_errors = []
    # AUTO: Checks this condition.
    if errors:
        # LINE: Only send the first lexical error to keep output focused.
        e = errors[0]
        # AUTO: Starts protected code that can catch errors.
        try:
            # AUTO: Checks this condition.
            if hasattr(e, 'as_string') and callable(getattr(e, 'as_string')):
                # LINE: Use the custom formatted message if the error supports it.
                str_errors.append(e.as_string())
            # AUTO: Runs when previous condition did not pass.
            else:
                # LINE: Otherwise use the normal Python string version.
                str_errors.append(str(e))
        # AUTO: Handles the matching error case.
        except Exception:
            # LINE: Fallback if error formatting itself fails.
            str_errors.append(str(e))
    # LINE: Return parser-ready tokens plus frontend-ready lexical error strings.
    return tokens, str_errors
