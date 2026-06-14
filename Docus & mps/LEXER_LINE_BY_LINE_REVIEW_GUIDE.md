# Lexer Line-by-Line Review Guide

Generated: 2026-06-07 16:56:11

Source file: `Backend/lexer/scanner.py`
Total lines explained: 2988

## Purpose
This document explains the lexer file line by line. The lexer receives the full source code string, scans it one character at a time, builds tokens, and records lexical errors when invalid characters or delimiters appear.

## Important Variables
- `self.source_code`: the full editor code after removing `\r`.
- `self.current_char`: the single character currently being scanned.
- `self.pos`: position tracker for index, line, and column.
- `ident_str`: temporary text for the token currently being built.
- `tokens`: list of successful Token objects.
- `errors`: list of LexicalError objects.

## Line-by-Line Explanation

| Line | Code | Explanation |
|---:|---|---|
| 1 | `"""Lexer/scanner for GAL source code.` | Starts or ends a module/function documentation string. |
| 2 | `` | Blank separator line used to visually separate code blocks. |
| 3 | `The scanner walks through source_code one character at a time with current_char` | Executes this Python statement as part of the lexer logic. |
| 4 | `and advance(), then produces Token objects plus any LexicalError messages.` | Executes this Python statement as part of the lexer logic. |
| 5 | `"""` | Starts or ends a module/function documentation string. |
| 6 | `` | Blank separator line used to visually separate code blocks. |
| 7 | `# AUTO: Imports names from another module.` | Comment/guideline: AUTO: Imports names from another module. |
| 8 | `from shared.tokens import *  # noqa: F401,F403  - TT_* constants used heavily by the FSM` | Imports a module, class, constant, or helper used by the lexer. |
| 9 | `# AUTO: Imports names from another module.` | Comment/guideline: AUTO: Imports names from another module. |
| 10 | `from shared.tokens import Token, get_token_description  # noqa: F401  - explicit re-export` | Imports a module, class, constant, or helper used by the lexer. |
| 11 | `# AUTO: Imports names from another module.` | Comment/guideline: AUTO: Imports names from another module. |
| 12 | `from lexer.positions import Position` | Imports a module, class, constant, or helper used by the lexer. |
| 13 | `# AUTO: Imports names from another module.` | Comment/guideline: AUTO: Imports names from another module. |
| 14 | `from lexer.errors import LexicalError` | Imports a module, class, constant, or helper used by the lexer. |
| 15 | `# AUTO: Imports names from another module.` | Comment/guideline: AUTO: Imports names from another module. |
| 16 | `from lexer.delimiters import (` | Imports a module, class, constant, or helper used by the lexer. |
| 17 | `    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 18 | `    ZERO, DIGIT, ZERODIGIT, LOW_ALPHA, UPPER_ALPHA, ALPHA, ALPHANUM,` | Executes this Python statement as part of the lexer logic. |
| 19 | `    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 20 | `    space_delim, delim2, delim3, delim4, delim5, delim6, delim7, delim8,` | Executes this Python statement as part of the lexer logic. |
| 21 | `    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 22 | `    delim9, delim10, delim11, delim12, delim13, delim14, delim15, delim16,` | Executes this Python statement as part of the lexer logic. |
| 23 | `    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 24 | `    delim17, delim18, delim19, delim20, delim21, delim22, delim23, delim24,` | Executes this Python statement as part of the lexer logic. |
| 25 | `    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 26 | `    delim25, delim26,` | Executes this Python statement as part of the lexer logic. |
| 27 | `    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 28 | `    idf_delim, whlnum_delim, decim_delim, comment_delim,` | Executes this Python statement as part of the lexer logic. |
| 29 | `    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 30 | `    statement_end_delim, open_paren_delim, close_paren_delim,` | Executes this Python statement as part of the lexer logic. |
| 31 | `    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 32 | `    open_bracket_delim, close_bracket_delim, block_start_delim,` | Executes this Python statement as part of the lexer logic. |
| 33 | `    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 34 | `    block_end_delim, case_colon_delim, after_comma_delim,` | Executes this Python statement as part of the lexer logic. |
| 35 | `# AUTO: Closes the current grouped code/data.` | Comment/guideline: AUTO: Closes the current grouped code/data. |
| 36 | `)` | Closes a grouped expression, list, dictionary, tuple, call, or block. |
| 37 | `` | Blank separator line used to visually separate code blocks. |
| 38 | `` | Blank separator line used to visually separate code blocks. |
| 39 | `# AUTO: Defines class `Lexer`.` | Comment/guideline: AUTO: Defines class `Lexer`. |
| 40 | `class Lexer:` | Defines the Lexer class. |
| 41 | `    # AUTO: Defines function `__init__`.` | Comment/guideline: AUTO: Defines function `__init__`. |
| 42 | `    def __init__(self, source_code): ` | Defines the __init__ function/method. |
| 43 | `        # GUIDE: Normalize Windows newlines so line/column tracking is consistent.` | Comment/guideline: GUIDE: Normalize Windows newlines so line/column tracking is consistent. |
| 44 | `        # source_code is the full text from the editor. The lexer does not` | Comment/guideline: source_code is the full text from the editor. The lexer does not |
| 45 | `        # understand the whole program at once; it scans this string one` | Comment/guideline: understand the whole program at once; it scans this string one |
| 46 | `        # character at a time.` | Comment/guideline: character at a time. |
| 47 | `        # LINE: Store the editor text and remove '\r' so Windows line endings are stable.` | Comment/guideline: LINE: Store the editor text and remove '\r' so Windows line endings are stable. |
| 48 | `        self.source_code = source_code.replace('\r', '')` | Stores the full editor source and removes Windows carriage returns (\r). |
| 49 | `` | Blank separator line used to visually separate code blocks. |
| 50 | `        # Position starts before the first character. Calling advance() below` | Comment/guideline: Position starts before the first character. Calling advance() below |
| 51 | `        # moves it to index 0 and loads the first current_char.` | Comment/guideline: moves it to index 0 and loads the first current_char. |
| 52 | `        # LINE: Start before the first character so advance() loads index 0.` | Comment/guideline: LINE: Start before the first character so advance() loads index 0. |
| 53 | `        self.pos = Position(-1, 1, -1)` | Creates the position tracker for index, line, and column. |
| 54 | `        # LINE: current_char holds the one character currently being scanned.` | Comment/guideline: LINE: current_char holds the one character currently being scanned. |
| 55 | `        self.current_char = None` | Initializes the currently scanned character before loading the first source character. |
| 56 | `        # LINE: Move to the first character of source_code.` | Comment/guideline: LINE: Move to the first character of source_code. |
| 57 | `        self.advance()` | Moves the lexer to the next character in the source code. |
| 58 | `` | Blank separator line used to visually separate code blocks. |
| 59 | `    # AUTO: Defines function `advance`.` | Comment/guideline: AUTO: Defines function `advance`. |
| 60 | `    def advance(self):` | Defines the advance function/method. |
| 61 | `        # GUIDE: Move one character forward and update Position before reading again.` | Comment/guideline: GUIDE: Move one character forward and update Position before reading again. |
| 62 | `        # self.current_char is the character being processed right now.` | Comment/guideline: self.current_char is the character being processed right now. |
| 63 | `        # self.pos stores index, line, and column for that character.` | Comment/guideline: self.pos stores index, line, and column for that character. |
| 64 | `        # LINE: Update index, line, and column using the previous character.` | Comment/guideline: LINE: Update index, line, and column using the previous character. |
| 65 | `        self.pos.advance(self.current_char)` | Moves the position tracker forward using the previous character. |
| 66 | `` | Blank separator line used to visually separate code blocks. |
| 67 | `        # If the index is still inside source_code, load the next character.` | Comment/guideline: If the index is still inside source_code, load the next character. |
| 68 | `        # If the index already passed the text length, current_char becomes None,` | Comment/guideline: If the index already passed the text length, current_char becomes None, |
| 69 | `        # which means the lexer reached end of file.` | Comment/guideline: which means the lexer reached end of file. |
| 70 | `        # LINE: Load the next character, or set None when the source is finished.` | Comment/guideline: LINE: Load the next character, or set None when the source is finished. |
| 71 | `        self.current_char = self.source_code[self.pos.index] if self.pos.index<len(self.source_code) else None` | Loads the next character from source_code, or None when the lexer reaches EOF. |
| 72 | `` | Blank separator line used to visually separate code blocks. |
| 73 | `    # AUTO: Defines function `make_tokens`.` | Comment/guideline: AUTO: Defines function `make_tokens`. |
| 74 | `    def make_tokens(self):` | Defines the make_tokens function/method. |
| 75 | `        # GUIDE: Main finite-state scan; each branch recognizes one token family.` | Comment/guideline: GUIDE: Main finite-state scan; each branch recognizes one token family. |
| 76 | `        # tokens collects successful Token objects.` | Comment/guideline: tokens collects successful Token objects. |
| 77 | `        # errors collects LexicalError objects if a character/token is invalid.` | Comment/guideline: errors collects LexicalError objects if a character/token is invalid. |
| 78 | `        # LINE: tokens is the output list sent to parser and lexeme table.` | Comment/guideline: LINE: tokens is the output list sent to parser and lexeme table. |
| 79 | `        tokens = []` | Creates the list that will store successful Token objects. |
| 80 | `        # LINE: line stores the source line number for each token.` | Comment/guideline: LINE: line stores the source line number for each token. |
| 81 | `        line = 1` | Starts line numbering at line 1 for token/error reporting. |
| 82 | `        # LINE: errors stores lexical errors found while scanning.` | Comment/guideline: LINE: errors stores lexical errors found while scanning. |
| 83 | `        errors = []` | Creates the list that will store lexical errors. |
| 84 | `        # LINE: pos remembers where the current token starts.` | Comment/guideline: LINE: pos remembers where the current token starts. |
| 85 | `        pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 86 | `` | Blank separator line used to visually separate code blocks. |
| 87 | `        # This loop continues until advance() reaches the end and sets` | Comment/guideline: This loop continues until advance() reaches the end and sets |
| 88 | `        # current_char to None.` | Comment/guideline: current_char to None. |
| 89 | `        # LINE: Main scanner loop; one token is built each pass.` | Comment/guideline: LINE: Main scanner loop; one token is built each pass. |
| 90 | `        while self.current_char != None:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 91 | `` | Blank separator line used to visually separate code blocks. |
| 92 | `            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 93 | `            if self.current_char in ALPHA:` | Checks if the current character starts a word/reserved word/identifier. |
| 94 | `                # GUIDE: Reserved words are checked first; unfinished matches fall back` | Comment/guideline: GUIDE: Reserved words are checked first; unfinished matches fall back |
| 95 | `                # to the identifier collector near the end of this alpha branch.` | Comment/guideline: to the identifier collector near the end of this alpha branch. |
| 96 | `                # ident_str temporarily stores the letters collected for the` | Comment/guideline: ident_str temporarily stores the letters collected for the |
| 97 | `                # current word. Example: reading seed builds "s", "se", "see",` | Comment/guideline: current word. Example: reading seed builds "s", "se", "see", |
| 98 | `                # "seed" before deciding if it is a reserved word or id.` | Comment/guideline: "seed" before deciding if it is a reserved word or id. |
| 99 | `                # LINE: ident_str builds the word text one character at a time.` | Comment/guideline: LINE: ident_str builds the word text one character at a time. |
| 100 | `                ident_str = ''` | Starts an empty lexeme string for building a token text. |
| 101 | `                # LINE: Save this word's starting column for token/error reporting.` | Comment/guideline: LINE: Save this word's starting column for token/error reporting. |
| 102 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 103 | `` | Blank separator line used to visually separate code blocks. |
| 104 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 105 | `                if self.current_char == "b":` | Checks whether the current character matches "b" so the lexer can choose that token branch. |
| 106 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 107 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 108 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 109 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 110 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 111 | `                    if self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 112 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 113 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 114 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 115 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 116 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 117 | `                        if self.current_char == "a":` | Checks whether the current character matches "a" so the lexer can choose that token branch. |
| 118 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 119 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 120 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 121 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 122 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 123 | `                            if self.current_char == "n":` | Checks whether the current character matches "n" so the lexer can choose that token branch. |
| 124 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 125 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 126 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 127 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 128 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 129 | `                                if self.current_char == "c":` | Checks whether the current character matches "c" so the lexer can choose that token branch. |
| 130 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 131 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 132 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 133 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 134 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 135 | `                                    if self.current_char == "h":` | Checks whether the current character matches "h" so the lexer can choose that token branch. |
| 136 | `                                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 137 | `                                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 138 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 139 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 140 | `                                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 141 | `                                        if self.current_char is None or self.current_char in space_delim or self.current_char == ';':` | Checks whether the current character matches ';' so the lexer can choose that token branch. |
| 142 | `                                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 143 | `                                            tokens.append(Token(TT_RW_BRANCH, ident_str, line, pos.col))` | Creates and appends a TT_RW_BRANCH token to the token list. |
| 144 | `                                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 145 | `                                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 146 | `                                        # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 147 | `                                        elif self.current_char not in ALPHANUM:` | Conditional check that decides which lexer path or validation rule runs next. |
| 148 | `                                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 149 | `                                            tokens.append(Token(TT_RW_BRANCH, ident_str, line, pos.col))` | Creates and appends a TT_RW_BRANCH token to the token list. |
| 150 | `                                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 151 | `                                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 152 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 153 | `                    elif self.current_char == "u":` | Checks whether the current character matches "u" so the lexer can choose that token branch. |
| 154 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 155 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 156 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 157 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 158 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 159 | `                        if self.current_char == "d":` | Checks whether the current character matches "d" so the lexer can choose that token branch. |
| 160 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 161 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 162 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 163 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 164 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 165 | `                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:` | Conditional check that decides which lexer path or validation rule runs next. |
| 166 | `                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 167 | `                                tokens.append(Token(TT_RW_BUD, ident_str, line, pos.col))` | Creates and appends a TT_RW_BUD token to the token list. |
| 168 | `                                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 169 | `                                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 170 | `                            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 171 | `                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 172 | `                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 173 | `                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 174 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 175 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 176 | `                                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 177 | `                                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 178 | `                        # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 179 | `                        elif self.current_char == "n":` | Checks whether the current character matches "n" so the lexer can choose that token branch. |
| 180 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 181 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 182 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 183 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 184 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 185 | `                            if self.current_char == "d":` | Checks whether the current character matches "d" so the lexer can choose that token branch. |
| 186 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 187 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 188 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 189 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 190 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 191 | `                                if self.current_char == "l":` | Checks whether the current character matches "l" so the lexer can choose that token branch. |
| 192 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 193 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 194 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 195 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 196 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 197 | `                                    if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 198 | `                                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 199 | `                                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 200 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 201 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 202 | `                                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 203 | `                                        if self.current_char is not None and self.current_char in space_delim:` | Conditional check that decides which lexer path or validation rule runs next. |
| 204 | `                                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 205 | `                                            tokens.append(Token(TT_RW_BUNDLE, ident_str, line, pos.col))` | Creates and appends a TT_RW_BUNDLE token to the token list. |
| 206 | `                                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 207 | `                                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 208 | `                                        # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 209 | `                                        elif self.current_char is not None and self.current_char not in space_delim and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 210 | `                                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 211 | `                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 212 | `                                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 213 | `                                            self.advance()` | Moves the lexer to the next character in the source code. |
| 214 | `                                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 215 | `                                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 216 | `` | Blank separator line used to visually separate code blocks. |
| 217 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 218 | `                elif self.current_char == "c":` | Checks whether the current character matches "c" so the lexer can choose that token branch. |
| 219 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 220 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 221 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 222 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 223 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 224 | `                    if self.current_char == "u":` | Checks whether the current character matches "u" so the lexer can choose that token branch. |
| 225 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 226 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 227 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 228 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 229 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 230 | `                        if self.current_char == "l":` | Checks whether the current character matches "l" so the lexer can choose that token branch. |
| 231 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 232 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 233 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 234 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 235 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 236 | `                            if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 237 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 238 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 239 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 240 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 241 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 242 | `                                if self.current_char == "i":` | Checks whether the current character matches "i" so the lexer can choose that token branch. |
| 243 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 244 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 245 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 246 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 247 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 248 | `                                    if self.current_char == "v":` | Checks whether the current character matches "v" so the lexer can choose that token branch. |
| 249 | `                                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 250 | `                                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 251 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 252 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 253 | `                                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 254 | `                                        if self.current_char == "a":` | Checks whether the current character matches "a" so the lexer can choose that token branch. |
| 255 | `                                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 256 | `                                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 257 | `                                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 258 | `                                            self.advance()` | Moves the lexer to the next character in the source code. |
| 259 | `                                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 260 | `                                            if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 261 | `                                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 262 | `                                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 263 | `                                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 264 | `                                                self.advance()` | Moves the lexer to the next character in the source code. |
| 265 | `                                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 266 | `                                                if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 267 | `                                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 268 | `                                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 269 | `                                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 270 | `                                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 271 | `                                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 272 | `                                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:` | Conditional check that decides which lexer path or validation rule runs next. |
| 273 | `                                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 274 | `                                                        tokens.append(Token(TT_RW_CULTIVATE, ident_str, line, pos.col))` | Creates and appends a TT_RW_CULTIVATE token to the token list. |
| 275 | `                                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 276 | `                                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 277 | `                                                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 278 | `                                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 279 | `                                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 280 | `                                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 281 | `                                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 282 | `                                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 283 | `                                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 284 | `                                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 285 | `` | Blank separator line used to visually separate code blocks. |
| 286 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 287 | `                elif self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 288 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 289 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 290 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 291 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 292 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 293 | `                    if self.current_char == "m":` | Checks whether the current character matches "m" so the lexer can choose that token branch. |
| 294 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 295 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 296 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 297 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 298 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 299 | `                        if self.current_char == "p":` | Checks whether the current character matches "p" so the lexer can choose that token branch. |
| 300 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 301 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 302 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 303 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 304 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 305 | `                            if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 306 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 307 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 308 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 309 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 310 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 311 | `                                if self.current_char == "y":` | Checks whether the current character matches "y" so the lexer can choose that token branch. |
| 312 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 313 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 314 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 315 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 316 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 317 | `                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:` | Conditional check that decides which lexer path or validation rule runs next. |
| 318 | `                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 319 | `                                        tokens.append(Token(TT_RW_EMPTY, ident_str, line, pos.col))` | Creates and appends a TT_RW_EMPTY token to the token list. |
| 320 | `                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 321 | `                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 322 | `                                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 323 | `                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 324 | `                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 325 | `                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 326 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 327 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 328 | `                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 329 | `                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 330 | `` | Blank separator line used to visually separate code blocks. |
| 331 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 332 | `                elif self.current_char == "f":` | Checks whether the current character matches "f" so the lexer can choose that token branch. |
| 333 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 334 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 335 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 336 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 337 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 338 | `                    if self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 339 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 340 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 341 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 342 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 343 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 344 | `                        if self.current_char == "o":` | Checks whether the current character matches "o" so the lexer can choose that token branch. |
| 345 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 346 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 347 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 348 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 349 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 350 | `                            if self.current_char == "s":` | Checks whether the current character matches "s" so the lexer can choose that token branch. |
| 351 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 352 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 353 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 354 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 355 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 356 | `                                if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 357 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 358 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 359 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 360 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 361 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 362 | `                                    if self.current_char is None or (self.current_char not in ALPHANUM and self.current_char != '_'):` | Conditional check that decides which lexer path or validation rule runs next. |
| 363 | `                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 364 | `                                        tokens.append(Token(TT_BOOLLIT_FALSE, ident_str, line, pos.col))` | Creates and appends a TT_BOOLLIT_FALSE token to the token list. |
| 365 | `                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 366 | `                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 367 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 368 | `                    elif self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 369 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 370 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 371 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 372 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 373 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 374 | `                        if self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 375 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 376 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 377 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 378 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 379 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 380 | `                            if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 381 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 382 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 383 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 384 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 385 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 386 | `                                if self.current_char == "i":` | Checks whether the current character matches "i" so the lexer can choose that token branch. |
| 387 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 388 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 389 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 390 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 391 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 392 | `                                    if self.current_char == "l":` | Checks whether the current character matches "l" so the lexer can choose that token branch. |
| 393 | `                                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 394 | `                                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 395 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 396 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 397 | `                                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 398 | `                                        if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 399 | `                                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 400 | `                                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 401 | `                                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 402 | `                                            self.advance()` | Moves the lexer to the next character in the source code. |
| 403 | `                                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 404 | `                                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:` | Conditional check that decides which lexer path or validation rule runs next. |
| 405 | `                                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 406 | `                                                tokens.append(Token(TT_RW_FERTILE, ident_str, line, pos.col))` | Creates and appends a TT_RW_FERTILE token to the token list. |
| 407 | `                                                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 408 | `                                                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 409 | `                                            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 410 | `                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 411 | `                                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 412 | `                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 413 | `                                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 414 | `                                                self.advance()` | Moves the lexer to the next character in the source code. |
| 415 | `                                                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 416 | `                                                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 417 | `                                            ` | Blank separator line used to visually separate code blocks. |
| 418 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 419 | `                elif self.current_char == "g":` | Checks whether the current character matches "g" so the lexer can choose that token branch. |
| 420 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 421 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 422 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 423 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 424 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 425 | `                    if self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 426 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 427 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 428 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 429 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 430 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 431 | `                        if self.current_char == "o":` | Checks whether the current character matches "o" so the lexer can choose that token branch. |
| 432 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 433 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 434 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 435 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 436 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 437 | `                            if self.current_char == "w":` | Checks whether the current character matches "w" so the lexer can choose that token branch. |
| 438 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 439 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 440 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 441 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 442 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 443 | `                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4 or self.current_char in space_delim:` | Conditional check that decides which lexer path or validation rule runs next. |
| 444 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 445 | `                                    tokens.append(Token(TT_RW_GROW, ident_str, line, pos.col))` | Creates and appends a TT_RW_GROW token to the token list. |
| 446 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 447 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 448 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 449 | `                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in space_delim and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 450 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 451 | `                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 452 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 453 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 454 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 455 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 456 | `                                ` | Blank separator line used to visually separate code blocks. |
| 457 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 458 | `                elif self.current_char == "h":` | Checks whether the current character matches "h" so the lexer can choose that token branch. |
| 459 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 460 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 461 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 462 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 463 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 464 | `                    if self.current_char == "a":` | Checks whether the current character matches "a" so the lexer can choose that token branch. |
| 465 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 466 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 467 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 468 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 469 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 470 | `                        if self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 471 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 472 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 473 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 474 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 475 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 476 | `                            if self.current_char == "v":` | Checks whether the current character matches "v" so the lexer can choose that token branch. |
| 477 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 478 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 479 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 480 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 481 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 482 | `                                if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 483 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 484 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 485 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 486 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 487 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 488 | `                                    if self.current_char == "s":` | Checks whether the current character matches "s" so the lexer can choose that token branch. |
| 489 | `                                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 490 | `                                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 491 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 492 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 493 | `                                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 494 | `                                        if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 495 | `                                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 496 | `                                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 497 | `                                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 498 | `                                            self.advance()` | Moves the lexer to the next character in the source code. |
| 499 | `                                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 500 | `                                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:` | Conditional check that decides which lexer path or validation rule runs next. |
| 501 | `                                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 502 | `                                                tokens.append(Token(TT_RW_HARVEST, ident_str, line, pos.col))` | Creates and appends a TT_RW_HARVEST token to the token list. |
| 503 | `                                                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 504 | `                                                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 505 | `                                            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 506 | `                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 507 | `                                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 508 | `                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 509 | `                                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 510 | `                                                self.advance()` | Moves the lexer to the next character in the source code. |
| 511 | `                                                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 512 | `                                                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 513 | `                                ` | Blank separator line used to visually separate code blocks. |
| 514 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 515 | `                elif self.current_char == "l":` | Checks whether the current character matches "l" so the lexer can choose that token branch. |
| 516 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 517 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 518 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 519 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 520 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 521 | `                    if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 522 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 523 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 524 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 525 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 526 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 527 | `                        if self.current_char == "a":` | Checks whether the current character matches "a" so the lexer can choose that token branch. |
| 528 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 529 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 530 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 531 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 532 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 533 | `                            if self.current_char == "f":` | Checks whether the current character matches "f" so the lexer can choose that token branch. |
| 534 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 535 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 536 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 537 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 538 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 539 | `                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':` | Checks whether the current character matches ';' so the lexer can choose that token branch. |
| 540 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 541 | `                                    tokens.append(Token(TT_RW_LEAF, ident_str, line, pos.col))` | Creates and appends a TT_RW_LEAF token to the token list. |
| 542 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 543 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 544 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 545 | `                                elif self.current_char not in ALPHANUM:` | Conditional check that decides which lexer path or validation rule runs next. |
| 546 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 547 | `                                    tokens.append(Token(TT_RW_LEAF, ident_str, line, pos.col))` | Creates and appends a TT_RW_LEAF token to the token list. |
| 548 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 549 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 550 | `                        ` | Blank separator line used to visually separate code blocks. |
| 551 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 552 | `                elif self.current_char == "p":` | Checks whether the current character matches "p" so the lexer can choose that token branch. |
| 553 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 554 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 555 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 556 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 557 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 558 | `                    if self.current_char == "l":` | Checks whether the current character matches "l" so the lexer can choose that token branch. |
| 559 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 560 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 561 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 562 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 563 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 564 | `                        if self.current_char == "a":` | Checks whether the current character matches "a" so the lexer can choose that token branch. |
| 565 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 566 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 567 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 568 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 569 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 570 | `                            if self.current_char == "n":` | Checks whether the current character matches "n" so the lexer can choose that token branch. |
| 571 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 572 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 573 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 574 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 575 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 576 | `                                if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 577 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 578 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 579 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 580 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 581 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 582 | `                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim6:` | Conditional check that decides which lexer path or validation rule runs next. |
| 583 | `                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 584 | `                                        tokens.append(Token(TT_RW_PLANT, ident_str, line, pos.col))` | Creates and appends a TT_RW_PLANT token to the token list. |
| 585 | `                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 586 | `                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 587 | `                                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 588 | `                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim6 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 589 | `                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 590 | `                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 591 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 592 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 593 | `                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 594 | `                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 595 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 596 | `                    elif self.current_char == "o":` | Checks whether the current character matches "o" so the lexer can choose that token branch. |
| 597 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 598 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 599 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 600 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 601 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 602 | `                        if self.current_char == "l":` | Checks whether the current character matches "l" so the lexer can choose that token branch. |
| 603 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 604 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 605 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 606 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 607 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 608 | `                            if self.current_char == "l":` | Checks whether the current character matches "l" so the lexer can choose that token branch. |
| 609 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 610 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 611 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 612 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 613 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 614 | `                                if self.current_char == "i":` | Checks whether the current character matches "i" so the lexer can choose that token branch. |
| 615 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 616 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 617 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 618 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 619 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 620 | `                                    if self.current_char == "n":` | Checks whether the current character matches "n" so the lexer can choose that token branch. |
| 621 | `                                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 622 | `                                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 623 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 624 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 625 | `                                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 626 | `                                        if self.current_char == "a":` | Checks whether the current character matches "a" so the lexer can choose that token branch. |
| 627 | `                                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 628 | `                                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 629 | `                                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 630 | `                                            self.advance()` | Moves the lexer to the next character in the source code. |
| 631 | `                                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 632 | `                                            if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 633 | `                                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 634 | `                                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 635 | `                                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 636 | `                                                self.advance()` | Moves the lexer to the next character in the source code. |
| 637 | `                                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 638 | `                                                if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 639 | `                                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 640 | `                                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 641 | `                                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 642 | `                                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 643 | `                                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 644 | `                                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in space_delim:` | Conditional check that decides which lexer path or validation rule runs next. |
| 645 | `                                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 646 | `                                                        tokens.append(Token(TT_RW_POLLINATE, ident_str, line, pos.col))` | Creates and appends a TT_RW_POLLINATE token to the token list. |
| 647 | `                                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 648 | `                                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 649 | `                                                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 650 | `                                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in space_delim and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 651 | `                                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 652 | `                                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 653 | `                                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 654 | `                                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 655 | `                                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 656 | `                                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 657 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 658 | `                    elif self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 659 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 660 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 661 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 662 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 663 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 664 | `                        if self.current_char == "u":` | Checks whether the current character matches "u" so the lexer can choose that token branch. |
| 665 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 666 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 667 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 668 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 669 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 670 | `                            if self.current_char == "n":` | Checks whether the current character matches "n" so the lexer can choose that token branch. |
| 671 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 672 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 673 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 674 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 675 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 676 | `                                if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 677 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 678 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 679 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 680 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 681 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 682 | `                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:` | Conditional check that decides which lexer path or validation rule runs next. |
| 683 | `                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 684 | `                                        tokens.append(Token(TT_RW_PRUNE, ident_str, line, pos.col))` | Creates and appends a TT_RW_PRUNE token to the token list. |
| 685 | `                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 686 | `                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 687 | `                                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 688 | `                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 689 | `                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 690 | `                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 691 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 692 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 693 | `                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 694 | `                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 695 | `` | Blank separator line used to visually separate code blocks. |
| 696 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 697 | `                elif self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 698 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 699 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 700 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 701 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 702 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 703 | `                    if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 704 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 705 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 706 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 707 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 708 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 709 | `                        if self.current_char == "c":` | Checks whether the current character matches "c" so the lexer can choose that token branch. |
| 710 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 711 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 712 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 713 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 714 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 715 | `                            if self.current_char == "l":` | Checks whether the current character matches "l" so the lexer can choose that token branch. |
| 716 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 717 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 718 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 719 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 720 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 721 | `                                if self.current_char == "a":` | Checks whether the current character matches "a" so the lexer can choose that token branch. |
| 722 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 723 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 724 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 725 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 726 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 727 | `                                    if self.current_char == "i":` | Checks whether the current character matches "i" so the lexer can choose that token branch. |
| 728 | `                                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 729 | `                                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 730 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 731 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 732 | `                                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 733 | `                                        if self.current_char == "m":` | Checks whether the current character matches "m" so the lexer can choose that token branch. |
| 734 | `                                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 735 | `                                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 736 | `                                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 737 | `                                            self.advance()` | Moves the lexer to the next character in the source code. |
| 738 | `                                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 739 | `                                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:` | Conditional check that decides which lexer path or validation rule runs next. |
| 740 | `                                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 741 | `                                                tokens.append(Token(TT_RW_RECLAIM, ident_str, line, pos.col))` | Creates and appends a TT_RW_RECLAIM token to the token list. |
| 742 | `                                                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 743 | `                                                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 744 | `                                            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 745 | `                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 746 | `                                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 747 | `                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 748 | `                                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 749 | `                                                self.advance()` | Moves the lexer to the next character in the source code. |
| 750 | `                                                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 751 | `                                                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 752 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 753 | `                    elif self.current_char == "o":` | Checks whether the current character matches "o" so the lexer can choose that token branch. |
| 754 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 755 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 756 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 757 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 758 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 759 | `                        if self.current_char == "o":` | Checks whether the current character matches "o" so the lexer can choose that token branch. |
| 760 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 761 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 762 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 763 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 764 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 765 | `                            if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 766 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 767 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 768 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 769 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 770 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 771 | `                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim7:` | Conditional check that decides which lexer path or validation rule runs next. |
| 772 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 773 | `                                    tokens.append(Token(TT_RW_ROOT, ident_str, line, pos.col))` | Creates and appends a TT_RW_ROOT token to the token list. |
| 774 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 775 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 776 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 777 | `                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim7 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 778 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 779 | `                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 780 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 781 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 782 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 783 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 784 | `` | Blank separator line used to visually separate code blocks. |
| 785 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 786 | `                elif self.current_char == "s": ` | Checks whether the current character matches "s" so the lexer can choose that token branch. |
| 787 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 788 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 789 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 790 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 791 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 792 | `                    if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 793 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 794 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 795 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 796 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 797 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 798 | `                        if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 799 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 800 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 801 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 802 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 803 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 804 | `                            if self.current_char == "d":` | Checks whether the current character matches "d" so the lexer can choose that token branch. |
| 805 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 806 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 807 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 808 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 809 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 810 | `                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':` | Checks whether the current character matches ';' so the lexer can choose that token branch. |
| 811 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 812 | `                                    tokens.append(Token(TT_RW_SEED, ident_str, line, pos.col))` | Creates and appends a TT_RW_SEED token to the token list. |
| 813 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 814 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 815 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 816 | `                                elif self.current_char not in ALPHANUM:` | Conditional check that decides which lexer path or validation rule runs next. |
| 817 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 818 | `                                    tokens.append(Token(TT_RW_SEED, ident_str, line, pos.col))` | Creates and appends a TT_RW_SEED token to the token list. |
| 819 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 820 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 821 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 822 | `                    elif self.current_char == "k":` | Checks whether the current character matches "k" so the lexer can choose that token branch. |
| 823 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 824 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 825 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 826 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 827 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 828 | `                        if self.current_char == "i":` | Checks whether the current character matches "i" so the lexer can choose that token branch. |
| 829 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 830 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 831 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 832 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 833 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 834 | `                            if self.current_char == "p":` | Checks whether the current character matches "p" so the lexer can choose that token branch. |
| 835 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 836 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 837 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 838 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 839 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 840 | `                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:` | Conditional check that decides which lexer path or validation rule runs next. |
| 841 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 842 | `                                    tokens.append(Token(TT_RW_SKIP, ident_str, line, pos.col))` | Creates and appends a TT_RW_SKIP token to the token list. |
| 843 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 844 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 845 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 846 | `                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 847 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 848 | `                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 849 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 850 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 851 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 852 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 853 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 854 | `                    elif self.current_char == "o":` | Checks whether the current character matches "o" so the lexer can choose that token branch. |
| 855 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 856 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 857 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 858 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 859 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 860 | `                        if self.current_char == "i":` | Checks whether the current character matches "i" so the lexer can choose that token branch. |
| 861 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 862 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 863 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 864 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 865 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 866 | `                            if self.current_char == "l":` | Checks whether the current character matches "l" so the lexer can choose that token branch. |
| 867 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 868 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 869 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 870 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 871 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 872 | `                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim2:` | Conditional check that decides which lexer path or validation rule runs next. |
| 873 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 874 | `                                    tokens.append(Token(TT_RW_SOIL, ident_str, line, pos.col))` | Creates and appends a TT_RW_SOIL token to the token list. |
| 875 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 876 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 877 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 878 | `                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim2 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 879 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 880 | `                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 881 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 882 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 883 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 884 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 885 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 886 | `                    elif self.current_char == "p":` | Checks whether the current character matches "p" so the lexer can choose that token branch. |
| 887 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 888 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 889 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 890 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 891 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 892 | `                        if self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 893 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 894 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 895 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 896 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 897 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 898 | `                            if self.current_char == "i":` | Checks whether the current character matches "i" so the lexer can choose that token branch. |
| 899 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 900 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 901 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 902 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 903 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 904 | `                                if self.current_char == "n":` | Checks whether the current character matches "n" so the lexer can choose that token branch. |
| 905 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 906 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 907 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 908 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 909 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 910 | `                                    if self.current_char == "g":` | Checks whether the current character matches "g" so the lexer can choose that token branch. |
| 911 | `                                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 912 | `                                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 913 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 914 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 915 | `                                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 916 | `                                        if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim5:` | Conditional check that decides which lexer path or validation rule runs next. |
| 917 | `                                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 918 | `                                            tokens.append(Token(TT_RW_SPRING, ident_str, line, pos.col))` | Creates and appends a TT_RW_SPRING token to the token list. |
| 919 | `                                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 920 | `                                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 921 | `                                        # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 922 | `                                        elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim5 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 923 | `                                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 924 | `                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 925 | `                                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 926 | `                                            self.advance()` | Moves the lexer to the next character in the source code. |
| 927 | `                                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 928 | `                                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 929 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 930 | `                    elif self.current_char == "u":` | Checks whether the current character matches "u" so the lexer can choose that token branch. |
| 931 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 932 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 933 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 934 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 935 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 936 | `                        if self.current_char == "n":` | Checks whether the current character matches "n" so the lexer can choose that token branch. |
| 937 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 938 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 939 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 940 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 941 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 942 | `                            if self.current_char == "s":` | Checks whether the current character matches "s" so the lexer can choose that token branch. |
| 943 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 944 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 945 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 946 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 947 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 948 | `                                if self.current_char == "h":` | Checks whether the current character matches "h" so the lexer can choose that token branch. |
| 949 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 950 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 951 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 952 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 953 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 954 | `                                    if self.current_char == "i":` | Checks whether the current character matches "i" so the lexer can choose that token branch. |
| 955 | `                                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 956 | `                                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 957 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 958 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 959 | `                                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 960 | `                                        if self.current_char == "n":` | Checks whether the current character matches "n" so the lexer can choose that token branch. |
| 961 | `                                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 962 | `                                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 963 | `                                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 964 | `                                            self.advance()` | Moves the lexer to the next character in the source code. |
| 965 | `                                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 966 | `                                            if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 967 | `                                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 968 | `                                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 969 | `                                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 970 | `                                                self.advance()` | Moves the lexer to the next character in the source code. |
| 971 | `                                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 972 | `                                                if self.current_char is None or self.current_char in delim23 or self.current_char in space_delim:` | Conditional check that decides which lexer path or validation rule runs next. |
| 973 | `                                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 974 | `                                                    tokens.append(Token(TT_BOOLLIT_TRUE, ident_str, line, pos.col))` | Creates and appends a TT_BOOLLIT_TRUE token to the token list. |
| 975 | `                                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 976 | `                                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 977 | `                                                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 978 | `                                                elif self.current_char not in ALPHANUM:` | Conditional check that decides which lexer path or validation rule runs next. |
| 979 | `                                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 980 | `                                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 981 | `                                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 982 | `                                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 983 | `                                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 984 | `                                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 985 | `` | Blank separator line used to visually separate code blocks. |
| 986 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 987 | `                elif self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 988 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 989 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 990 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 991 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 992 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 993 | `                    if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 994 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 995 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 996 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 997 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 998 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 999 | `                        if self.current_char == "n":` | Checks whether the current character matches "n" so the lexer can choose that token branch. |
| 1000 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1001 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1002 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1003 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 1004 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1005 | `                            if self.current_char == "d":` | Checks whether the current character matches "d" so the lexer can choose that token branch. |
| 1006 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1007 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1008 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1009 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 1010 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1011 | `                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim3:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1012 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1013 | `                                    tokens.append(Token(TT_RW_TEND, ident_str, line, pos.col))` | Creates and appends a TT_RW_TEND token to the token list. |
| 1014 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1015 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1016 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1017 | `                                elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim3 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1018 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1019 | `                                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1020 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1021 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1022 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1023 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1024 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1025 | `                    elif self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 1026 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1027 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1028 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1029 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1030 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1031 | `                        if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 1032 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1033 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1034 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1035 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 1036 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1037 | `                            if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 1038 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1039 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1040 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1041 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 1042 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1043 | `                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':` | Checks whether the current character matches ';' so the lexer can choose that token branch. |
| 1044 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1045 | `                                    tokens.append(Token(TT_RW_TREE, ident_str, line, pos.col))` | Creates and appends a TT_RW_TREE token to the token list. |
| 1046 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1047 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1048 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1049 | `                                elif self.current_char not in ALPHANUM:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1050 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1051 | `                                    tokens.append(Token(TT_RW_TREE, ident_str, line, pos.col))` | Creates and appends a TT_RW_TREE token to the token list. |
| 1052 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1053 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1054 | `` | Blank separator line used to visually separate code blocks. |
| 1055 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1056 | `                elif self.current_char == "v":` | Checks whether the current character matches "v" so the lexer can choose that token branch. |
| 1057 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1058 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1059 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1060 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1061 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1062 | `                    if self.current_char == "i":` | Checks whether the current character matches "i" so the lexer can choose that token branch. |
| 1063 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1064 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1065 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1066 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1067 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1068 | `                        if self.current_char == "n":` | Checks whether the current character matches "n" so the lexer can choose that token branch. |
| 1069 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1070 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1071 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1072 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 1073 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1074 | `                            if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 1075 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1076 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1077 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1078 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 1079 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1080 | `                                if self.current_char is None or self.current_char in space_delim or self.current_char == ';':` | Checks whether the current character matches ';' so the lexer can choose that token branch. |
| 1081 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1082 | `                                    tokens.append(Token(TT_RW_VINE, ident_str, line, pos.col))` | Creates and appends a TT_RW_VINE token to the token list. |
| 1083 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1084 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1085 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1086 | `                                elif self.current_char not in ALPHANUM:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1087 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1088 | `                                    tokens.append(Token(TT_RW_VINE, ident_str, line, pos.col))` | Creates and appends a TT_RW_VINE token to the token list. |
| 1089 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1090 | `                                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1091 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1092 | `                    elif self.current_char == "a":` | Checks whether the current character matches "a" so the lexer can choose that token branch. |
| 1093 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1094 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1095 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1096 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1097 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1098 | `                        if self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 1099 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1100 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1101 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1102 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 1103 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1104 | `                            if self.current_char == "i":` | Checks whether the current character matches "i" so the lexer can choose that token branch. |
| 1105 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1106 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1107 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1108 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 1109 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1110 | `                                if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 1111 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1112 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1113 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1114 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1115 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1116 | `                                    if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 1117 | `                                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1118 | `                                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1119 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1120 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1121 | `                                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1122 | `                                        if self.current_char == "y":` | Checks whether the current character matches "y" so the lexer can choose that token branch. |
| 1123 | `                                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1124 | `                                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1125 | `                                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1126 | `                                            self.advance()` | Moves the lexer to the next character in the source code. |
| 1127 | `                                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1128 | `                                            if self.current_char is None or self.current_char in space_delim:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1129 | `                                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1130 | `                                                tokens.append(Token(TT_RW_VARIETY, ident_str, line, pos.col))` | Creates and appends a TT_RW_VARIETY token to the token list. |
| 1131 | `                                                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1132 | `                                                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1133 | `                                            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1134 | `                                            elif self.current_char not in ALPHANUM:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1135 | `                                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1136 | `                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1137 | `                                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1138 | `                                                self.advance()` | Moves the lexer to the next character in the source code. |
| 1139 | `                                                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1140 | `                                                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1141 | `` | Blank separator line used to visually separate code blocks. |
| 1142 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1143 | `                elif self.current_char == "w":` | Checks whether the current character matches "w" so the lexer can choose that token branch. |
| 1144 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1145 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1146 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1147 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1148 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1149 | `                    if self.current_char == "a":` | Checks whether the current character matches "a" so the lexer can choose that token branch. |
| 1150 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1151 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1152 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1153 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1154 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1155 | `                        if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 1156 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1157 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1158 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1159 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 1160 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1161 | `                            if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 1162 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1163 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1164 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1165 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 1166 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1167 | `                                if self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 1168 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1169 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1170 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1171 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1172 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1173 | `                                    if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim6:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1174 | `                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1175 | `                                        tokens.append(Token(TT_RW_WATER, ident_str, line, pos.col))` | Creates and appends a TT_RW_WATER token to the token list. |
| 1176 | `                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1177 | `                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1178 | `                                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1179 | `                                    elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim6 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1180 | `                                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1181 | `                                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1182 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1183 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1184 | `                                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1185 | `                                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1186 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1187 | `                    elif self.current_char == "i":` | Checks whether the current character matches "i" so the lexer can choose that token branch. |
| 1188 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1189 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1190 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1191 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1192 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1193 | `                        if self.current_char == "t":` | Checks whether the current character matches "t" so the lexer can choose that token branch. |
| 1194 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1195 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1196 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1197 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 1198 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1199 | `                            if self.current_char == "h":` | Checks whether the current character matches "h" so the lexer can choose that token branch. |
| 1200 | `                                # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1201 | `                                ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1202 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1203 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 1204 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1205 | `                                if self.current_char == "e":` | Checks whether the current character matches "e" so the lexer can choose that token branch. |
| 1206 | `                                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1207 | `                                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1208 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1209 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1210 | `                                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1211 | `                                    if self.current_char == "r":` | Checks whether the current character matches "r" so the lexer can choose that token branch. |
| 1212 | `                                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1213 | `                                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1214 | `                                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1215 | `                                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1216 | `                                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1217 | `                                        if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim3:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1218 | `                                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1219 | `                                            tokens.append(Token(TT_RW_WITHER, ident_str, line, pos.col))` | Creates and appends a TT_RW_WITHER token to the token list. |
| 1220 | `                                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1221 | `                                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1222 | `                                        # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1223 | `                                        elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim3 and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1224 | `                                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1225 | `                                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1226 | `                                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1227 | `                                            self.advance()` | Moves the lexer to the next character in the source code. |
| 1228 | `                                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1229 | `                                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1230 | `` | Blank separator line used to visually separate code blocks. |
| 1231 | `                # AUTO: Sets `maxIdentifierLength`.` | Comment/guideline: AUTO: Sets `maxIdentifierLength`. |
| 1232 | `                maxIdentifierLength = 15` | Assigns a value to a variable or object attribute used by the lexer. |
| 1233 | `                # LINE: If reserved-word matching failed, collect the rest as an identifier.` | Comment/guideline: LINE: If reserved-word matching failed, collect the rest as an identifier. |
| 1234 | `                while self.current_char is not None and self.current_char in ALPHANUM:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 1235 | `                    # If the reserved-word checks above did not finish with a` | Comment/guideline: If the reserved-word checks above did not finish with a |
| 1236 | `                    # continue, the word is not a reserved word. This loop` | Comment/guideline: continue, the word is not a reserved word. This loop |
| 1237 | `                    # collects the rest of the identifier.` | Comment/guideline: collects the rest of the identifier. |
| 1238 | `                    # Example: "roof" starts through the "root" path, but when` | Comment/guideline: Example: "roof" starts through the "root" path, but when |
| 1239 | `                    # the expected "t" is not found, the remaining "f" is` | Comment/guideline: the expected "t" is not found, the remaining "f" is |
| 1240 | `                    # collected here and the final token becomes id("roof").` | Comment/guideline: collected here and the final token becomes id("roof"). |
| 1241 | `                    # LINE: Append the current letter/digit into the identifier text.` | Comment/guideline: LINE: Append the current letter/digit into the identifier text. |
| 1242 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1243 | `                    # LINE: Move to the next character after adding this one.` | Comment/guideline: LINE: Move to the next character after adding this one. |
| 1244 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1245 | `` | Blank separator line used to visually separate code blocks. |
| 1246 | `                # LINE: Check if the finished identifier is too long.` | Comment/guideline: LINE: Check if the finished identifier is too long. |
| 1247 | `                if len(ident_str) > maxIdentifierLength:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1248 | `                    # LINE: i marks where the next 15-character chunk starts.` | Comment/guideline: LINE: i marks where the next 15-character chunk starts. |
| 1249 | `                    i = 0` | Assigns a value to a variable or object attribute used by the lexer. |
| 1250 | `                    # LINE: remaining becomes the final valid chunk if there is one.` | Comment/guideline: LINE: remaining becomes the final valid chunk if there is one. |
| 1251 | `                    remaining = None` | Assigns a value to a variable or object attribute used by the lexer. |
| 1252 | `                    # LINE: Split very long identifiers into chunks for error reporting.` | Comment/guideline: LINE: Split very long identifiers into chunks for error reporting. |
| 1253 | `                    while i < len(ident_str):` | Loop that repeats until its condition becomes false. |
| 1254 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1255 | `                        if i + 15 <= len(ident_str):` | Conditional check that decides which lexer path or validation rule runs next. |
| 1256 | `                            # LINE: Report each over-limit chunk as a lexical error.` | Comment/guideline: LINE: Report each over-limit chunk as a lexical error. |
| 1257 | `                            errors.append(LexicalError(pos, f"Identifier exceeds maximum length of {maxIdentifierLength} characters"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1258 | `                            # LINE: Skip to the next 15-character chunk.` | Comment/guideline: LINE: Skip to the next 15-character chunk. |
| 1259 | `                            i += 15` | Updates an existing value by adding or appending something to it. |
| 1260 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 1261 | `                        else:` | Fallback path when the previous if/elif condition did not match. |
| 1262 | `                            # LINE: Keep the leftover identifier characters after the long chunks.` | Comment/guideline: LINE: Keep the leftover identifier characters after the long chunks. |
| 1263 | `                            remaining = ident_str[i:]` | Assigns a value to a variable or object attribute used by the lexer. |
| 1264 | `                            # LINE: Accept leftover only if the next character can legally end an id.` | Comment/guideline: LINE: Accept leftover only if the next character can legally end an id. |
| 1265 | `                            if self.current_char is None or self.current_char in idf_delim:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1266 | `                                # LINE: Add the leftover identifier token to the token list.` | Comment/guideline: LINE: Add the leftover identifier token to the token list. |
| 1267 | `                                tokens.append(Token(TT_IDENTIFIER, remaining, line, pos.col))` | Creates and appends a TT_IDENTIFIER token to the token list. |
| 1268 | `                            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1269 | `                            elif self.current_char is not None and self.current_char not in idf_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1270 | `                                # LINE: The character after the id is illegal, so report delimiter error.` | Comment/guideline: LINE: The character after the id is illegal, so report delimiter error. |
| 1271 | `                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after identifier"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1272 | `                            # AUTO: Stops the nearest loop.` | Comment/guideline: AUTO: Stops the nearest loop. |
| 1273 | `                            break` | Stops the nearest loop. |
| 1274 | `                    # LINE: If there was no leftover, keep the last collected chunk as identifier output.` | Comment/guideline: LINE: If there was no leftover, keep the last collected chunk as identifier output. |
| 1275 | `                    if remaining is None:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1276 | `                        # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 1277 | `                        last_chunk = ident_str[i - 15:] if i >= 15 else ident_str` | Assigns a value to a variable or object attribute used by the lexer. |
| 1278 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1279 | `                        if self.current_char is None or self.current_char in idf_delim:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1280 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1281 | `                            tokens.append(Token(TT_IDENTIFIER, last_chunk, line, pos.col))` | Creates and appends a TT_IDENTIFIER token to the token list. |
| 1282 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1283 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1284 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 1285 | `                else:` | Fallback path when the previous if/elif condition did not match. |
| 1286 | `                    # LINE: Normal identifier path for words within the length limit.` | Comment/guideline: LINE: Normal identifier path for words within the length limit. |
| 1287 | `                    if self.current_char is None or self.current_char in idf_delim:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1288 | `                        # The identifier is complete because the next character` | Comment/guideline: The identifier is complete because the next character |
| 1289 | `                        # is a valid delimiter like space, semicolon, operator,` | Comment/guideline: is a valid delimiter like space, semicolon, operator, |
| 1290 | `                        # parenthesis, or EOF.` | Comment/guideline: parenthesis, or EOF. |
| 1291 | `                        # LINE: Save the identifier token, like id(num) or id(roof).` | Comment/guideline: LINE: Save the identifier token, like id(num) or id(roof). |
| 1292 | `                        tokens.append(Token(TT_IDENTIFIER, ident_str, line, pos.col))` | Creates and appends a TT_IDENTIFIER token to the token list. |
| 1293 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1294 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1295 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1296 | `                    elif self.current_char is not None and self.current_char not in idf_delim and self.current_char not in ALPHANUM:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1297 | `                        # The collected word is valid, but the next character is` | Comment/guideline: The collected word is valid, but the next character is |
| 1298 | `                        # not allowed after an identifier.` | Comment/guideline: not allowed after an identifier. |
| 1299 | `                        # LINE: Report invalid delimiter after an identifier.` | Comment/guideline: LINE: Report invalid delimiter after an identifier. |
| 1300 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1301 | `                        # LINE: Move past the bad character so scanning can continue.` | Comment/guideline: LINE: Move past the bad character so scanning can continue. |
| 1302 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1303 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1304 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1305 | `` | Blank separator line used to visually separate code blocks. |
| 1306 | `            ` | Blank separator line used to visually separate code blocks. |
| 1307 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1308 | `            elif self.current_char == "-":` | Checks whether the current character matches "-" so the lexer can choose that token branch. |
| 1309 | `                # GUIDE: Symbol/operator states validate the next character with` | Comment/guideline: GUIDE: Symbol/operator states validate the next character with |
| 1310 | `                # delimiter sets so tokens like -=, --, and - are separated.` | Comment/guideline: delimiter sets so tokens like -=, --, and - are separated. |
| 1311 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1312 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1313 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1314 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1315 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1316 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1317 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1318 | `                if self.current_char == "-":` | Checks whether the current character matches "-" so the lexer can choose that token branch. |
| 1319 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1320 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1321 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1322 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1323 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1324 | `                    if self.current_char is not None and self.current_char not in delim25:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1325 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1326 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1327 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1328 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1329 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1330 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1331 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1332 | `                    tokens.append(Token(TT_DECREMENT, ident_str, line, pos.col))` | Creates and appends a TT_DECREMENT token to the token list. |
| 1333 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1334 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1335 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1336 | `                if self.current_char == "=":` | Checks whether the current character matches "=" so the lexer can choose that token branch. |
| 1337 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1338 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1339 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1340 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1341 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1342 | `                    if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1343 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1344 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1345 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1346 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1347 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1348 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1349 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1350 | `                    tokens.append(Token(TT_MINUSEQ, ident_str, line, pos.col))` | Creates and appends a TT_MINUSEQ token to the token list. |
| 1351 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1352 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1353 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1354 | `                if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1355 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1356 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1357 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1358 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1359 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1360 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1361 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1362 | `                tokens.append(Token(TT_MINUS, ident_str, line, pos.col))` | Creates and appends a TT_MINUS token to the token list. |
| 1363 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1364 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1365 | `            ` | Blank separator line used to visually separate code blocks. |
| 1366 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1367 | `            elif self.current_char == "~":` | Checks whether the current character matches "~" so the lexer can choose that token branch. |
| 1368 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1369 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1370 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1371 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1372 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1373 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1374 | `` | Blank separator line used to visually separate code blocks. |
| 1375 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1376 | `                if self.current_char is not None and self.current_char in ZERODIGIT:` | Checks if the current character starts a numeric literal. |
| 1377 | `                    # AUTO: Sets `num_str`.` | Comment/guideline: AUTO: Sets `num_str`. |
| 1378 | `                    num_str = ""` | Assigns a value to a variable or object attribute used by the lexer. |
| 1379 | `                    # AUTO: Sets `integer_digit_count`.` | Comment/guideline: AUTO: Sets `integer_digit_count`. |
| 1380 | `                    integer_digit_count = 0` | Assigns a value to a variable or object attribute used by the lexer. |
| 1381 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 1382 | `                    while self.current_char is not None and self.current_char in ZERODIGIT:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 1383 | `                        # AUTO: Adds into `integer_digit_count`.` | Comment/guideline: AUTO: Adds into `integer_digit_count`. |
| 1384 | `                        integer_digit_count += 1` | Counts one more digit in the integer part of a number. |
| 1385 | `                        # AUTO: Adds into `num_str`.` | Comment/guideline: AUTO: Adds into `num_str`. |
| 1386 | `                        num_str += self.current_char` | Adds the current digit/character to the numeric literal text. |
| 1387 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1388 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1389 | `` | Blank separator line used to visually separate code blocks. |
| 1390 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1391 | `                    if self.current_char == ".":` | Checks whether the current character matches "." so the lexer can choose that token branch. |
| 1392 | `                        # AUTO: Adds into `num_str`.` | Comment/guideline: AUTO: Adds into `num_str`. |
| 1393 | `                        num_str += self.current_char` | Adds the current digit/character to the numeric literal text. |
| 1394 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1395 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1396 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1397 | `                        if self.current_char is None or self.current_char not in ZERODIGIT:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1398 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1399 | `                            errors.append(LexicalError(pos, f"Invalid number '~{num_str}': decimal point must be followed by digits"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1400 | `                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1401 | `                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1402 | `                        # AUTO: Sets `fractional_digit_count`.` | Comment/guideline: AUTO: Sets `fractional_digit_count`. |
| 1403 | `                        fractional_digit_count = 0` | Assigns a value to a variable or object attribute used by the lexer. |
| 1404 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 1405 | `                        while self.current_char is not None and self.current_char in ZERODIGIT:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 1406 | `                            # AUTO: Adds into `fractional_digit_count`.` | Comment/guideline: AUTO: Adds into `fractional_digit_count`. |
| 1407 | `                            fractional_digit_count += 1` | Counts one more digit in the fractional part of a decimal number. |
| 1408 | `                            # AUTO: Adds into `num_str`.` | Comment/guideline: AUTO: Adds into `num_str`. |
| 1409 | `                            num_str += self.current_char` | Adds the current digit/character to the numeric literal text. |
| 1410 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1411 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 1412 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1413 | `                        if fractional_digit_count > 8:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1414 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1415 | `                            errors.append(LexicalError(pos, f"Fractional part exceeds maximum of 8 digits"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1416 | `                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1417 | `                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1418 | `                        # AUTO: Sets `parts`.` | Comment/guideline: AUTO: Sets `parts`. |
| 1419 | `                        parts = num_str.split(".")` | Assigns a value to a variable or object attribute used by the lexer. |
| 1420 | `                        # AUTO: Sets `integer_part`.` | Comment/guideline: AUTO: Sets `integer_part`. |
| 1421 | `                        integer_part = parts[0].lstrip("0") or "0"` | Assigns a value to a variable or object attribute used by the lexer. |
| 1422 | `                        # AUTO: Sets `fractional_part`.` | Comment/guideline: AUTO: Sets `fractional_part`. |
| 1423 | `                        fractional_part = (parts[1] if len(parts) > 1 else "").rstrip("0") or "0"` | Assigns a value to a variable or object attribute used by the lexer. |
| 1424 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1425 | `                        if fractional_part == "0":` | Conditional check that decides which lexer path or validation rule runs next. |
| 1426 | `                            # AUTO: Sets `num_str`.` | Comment/guideline: AUTO: Sets `num_str`. |
| 1427 | `                            num_str = f"{integer_part}.0"` | Assigns a value to a variable or object attribute used by the lexer. |
| 1428 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 1429 | `                        else:` | Fallback path when the previous if/elif condition did not match. |
| 1430 | `                            # AUTO: Sets `num_str`.` | Comment/guideline: AUTO: Sets `num_str`. |
| 1431 | `                            num_str = f"{integer_part}.{fractional_part}"` | Assigns a value to a variable or object attribute used by the lexer. |
| 1432 | `                        # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1433 | `                        ident_str = "~" + num_str` | Assigns a value to a variable or object attribute used by the lexer. |
| 1434 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1435 | `                        tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))` | Creates and appends a TT_DOUBLELIT token to the token list. |
| 1436 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1437 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1438 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 1439 | `                    else:` | Fallback path when the previous if/elif condition did not match. |
| 1440 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1441 | `                        if integer_digit_count > 8:` | Conditional check that decides which lexer path or validation rule runs next. |
| 1442 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1443 | `                            errors.append(LexicalError(pos, f"Integer exceeds maximum of 8 digits"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1444 | `                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1445 | `                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1446 | `                        # AUTO: Sets `num_str`.` | Comment/guideline: AUTO: Sets `num_str`. |
| 1447 | `                        num_str = num_str.lstrip("0") or "0"` | Assigns a value to a variable or object attribute used by the lexer. |
| 1448 | `                        # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1449 | `                        ident_str = "~" + num_str` | Assigns a value to a variable or object attribute used by the lexer. |
| 1450 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1451 | `                        tokens.append(Token(TT_INTEGERLIT, ident_str, line, pos.col))` | Creates and appends a TT_INTEGERLIT token to the token list. |
| 1452 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1453 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1454 | `` | Blank separator line used to visually separate code blocks. |
| 1455 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1456 | `                elif self.current_char is None or self.current_char in ALPHANUM + '( \t\n':` | Checks if the current character starts a word/reserved word/identifier. |
| 1457 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1458 | `                    tokens.append(Token(TT_NEGATIVE, ident_str, line, pos.col))` | Creates and appends a TT_NEGATIVE token to the token list. |
| 1459 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1460 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1461 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 1462 | `                else:` | Fallback path when the previous if/elif condition did not match. |
| 1463 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1464 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'."))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1465 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1466 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1467 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1468 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1469 | `            ` | Blank separator line used to visually separate code blocks. |
| 1470 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1471 | `            elif self.current_char == "!":` | Checks whether the current character matches "!" so the lexer can choose that token branch. |
| 1472 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1473 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1474 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1475 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1476 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1477 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1478 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1479 | `                if self.current_char == "=":` | Checks whether the current character matches "=" so the lexer can choose that token branch. |
| 1480 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1481 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1482 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1483 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1484 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1485 | `                    if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:` | Looks at the previous token to reject invalid adjacent operators or punctuation. |
| 1486 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1487 | `                        errors.append(LexicalError(pos, f"Consecutive operators '{tokens[-1].value} {ident_str}' are not allowed"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1488 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1489 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1490 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1491 | `                    if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1492 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1493 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1494 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1495 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1496 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1497 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1498 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1499 | `                    tokens.append(Token(TT_NOTEQ, ident_str, line, pos.col))` | Creates and appends a TT_NOTEQ token to the token list. |
| 1500 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1501 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1502 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 1503 | `                else:` | Fallback path when the previous if/elif condition did not match. |
| 1504 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1505 | `                    if self.current_char is not None and self.current_char not in delim26:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1506 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1507 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1508 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1509 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1510 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1511 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1512 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1513 | `                    tokens.append(Token(TT_NOT, ident_str, line, pos.col))` | Creates and appends a TT_NOT token to the token list. |
| 1514 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1515 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1516 | `            ` | Blank separator line used to visually separate code blocks. |
| 1517 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1518 | `            elif self.current_char == "%":` | Checks whether the current character matches "%" so the lexer can choose that token branch. |
| 1519 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1520 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1521 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1522 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1523 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1524 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1525 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1526 | `                if self.current_char == "=":` | Checks whether the current character matches "=" so the lexer can choose that token branch. |
| 1527 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1528 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1529 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1530 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1531 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1532 | `                    if self.current_char is not None and self.current_char not in delim25:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1533 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1534 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1535 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1536 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1537 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1538 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1539 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1540 | `                    tokens.append(Token(TT_MODEQ, ident_str, line, pos.col))` | Creates and appends a TT_MODEQ token to the token list. |
| 1541 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1542 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1543 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1544 | `                if self.current_char is not None and self.current_char not in delim25:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1545 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1546 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1547 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1548 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1549 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1550 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1551 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1552 | `                tokens.append(Token(TT_MOD, ident_str, line, pos.col))` | Creates and appends a TT_MOD token to the token list. |
| 1553 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1554 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1555 | `    ` | Blank separator line used to visually separate code blocks. |
| 1556 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1557 | `            elif self.current_char == "&":` | Checks whether the current character matches "&" so the lexer can choose that token branch. |
| 1558 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1559 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1560 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1561 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1562 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1563 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1564 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1565 | `                if self.current_char == "&":` | Checks whether the current character matches "&" so the lexer can choose that token branch. |
| 1566 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1567 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1568 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1569 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1570 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1571 | `                    if self.current_char is not None and self.current_char not in delim21:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1572 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1573 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1574 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1575 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1576 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1577 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1578 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1579 | `                    tokens.append(Token(TT_AND, ident_str, line, pos.col))` | Creates and appends a TT_AND token to the token list. |
| 1580 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1581 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1582 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 1583 | `                else:` | Fallback path when the previous if/elif condition did not match. |
| 1584 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1585 | `                    tokens.append(Token(TT_SINGLE_AND, ident_str, line, pos.col))` | Creates and appends a TT_SINGLE_AND token to the token list. |
| 1586 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1587 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1588 | `                    ` | Blank separator line used to visually separate code blocks. |
| 1589 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1590 | `            elif self.current_char == "(":` | Checks whether the current character matches "(" so the lexer can choose that token branch. |
| 1591 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1592 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1593 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1594 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1595 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1596 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1597 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1598 | `                if self.current_char is not None and self.current_char not in open_paren_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1599 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1600 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1601 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1602 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1603 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1604 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1605 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1606 | `                tokens.append(Token(TT_LPAREN, ident_str, line, pos.col))` | Creates and appends a TT_LPAREN token to the token list. |
| 1607 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1608 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1609 | `` | Blank separator line used to visually separate code blocks. |
| 1610 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1611 | `            elif self.current_char == ")":` | Checks whether the current character matches ")" so the lexer can choose that token branch. |
| 1612 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1613 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1614 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1615 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1616 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1617 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1618 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1619 | `                if self.current_char is not None and self.current_char not in close_paren_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1620 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1621 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1622 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1623 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1624 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1625 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1626 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1627 | `                tokens.append(Token(TT_RPAREN, ident_str, line, pos.col))` | Creates and appends a TT_RPAREN token to the token list. |
| 1628 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1629 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1630 | `                ` | Blank separator line used to visually separate code blocks. |
| 1631 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1632 | `            elif self.current_char == "*":` | Checks whether the current character matches "*" so the lexer can choose that token branch. |
| 1633 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1634 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1635 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1636 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1637 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1638 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1639 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1640 | `                if self.current_char == "*":` | Checks whether the current character matches "*" so the lexer can choose that token branch. |
| 1641 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1642 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1643 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1644 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1645 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1646 | `                    if self.current_char == "=":` | Checks whether the current character matches "=" so the lexer can choose that token branch. |
| 1647 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1648 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1649 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1650 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1651 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1652 | `                        if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1653 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1654 | `                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1655 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1656 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 1657 | `                            # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1658 | `                            continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1659 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1660 | `                        tokens.append(Token(TT_EXPEQ, ident_str, line, pos.col))` | Creates and appends a TT_EXPEQ token to the token list. |
| 1661 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1662 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1663 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1664 | `                    if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1665 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1666 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1667 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1668 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1669 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1670 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1671 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1672 | `                    tokens.append(Token(TT_EXP, ident_str, line, pos.col))` | Creates and appends a TT_EXP token to the token list. |
| 1673 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1674 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1675 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1676 | `                if self.current_char == "=":` | Checks whether the current character matches "=" so the lexer can choose that token branch. |
| 1677 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1678 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1679 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1680 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1681 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1682 | `                    if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1683 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1684 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1685 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1686 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1687 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1688 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1689 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1690 | `                    tokens.append(Token(TT_MULTIEQ, ident_str, line, pos.col))` | Creates and appends a TT_MULTIEQ token to the token list. |
| 1691 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1692 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1693 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1694 | `                if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1695 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1696 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1697 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1698 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1699 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1700 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1701 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1702 | `                tokens.append(Token(TT_MUL, ident_str, line, pos.col))` | Creates and appends a TT_MUL token to the token list. |
| 1703 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1704 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1705 | `                ` | Blank separator line used to visually separate code blocks. |
| 1706 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1707 | `            elif self.current_char == ",":` | Checks whether the current character matches "," so the lexer can choose that token branch. |
| 1708 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1709 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1710 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1711 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1712 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1713 | `                if len(tokens) > 0 and tokens[-1].type == TT_COMMA:` | Looks at the previous token to reject invalid adjacent operators or punctuation. |
| 1714 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1715 | `                    errors.append(LexicalError(pos, f"Invalid delimiters ','"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1716 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1717 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1718 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1719 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1720 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1721 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1722 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1723 | `                if self.current_char is not None and self.current_char not in after_comma_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1724 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1725 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after ','"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1726 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1727 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1728 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1729 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1730 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1731 | `                tokens.append(Token(TT_COMMA, ident_str, line, pos.col))` | Creates and appends a TT_COMMA token to the token list. |
| 1732 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1733 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1734 | `` | Blank separator line used to visually separate code blocks. |
| 1735 | `` | Blank separator line used to visually separate code blocks. |
| 1736 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1737 | `            elif self.current_char == ";":` | Checks whether the current character matches ";" so the lexer can choose that token branch. |
| 1738 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1739 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1740 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1741 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1742 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1743 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1744 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1745 | `                if self.current_char is not None and self.current_char not in statement_end_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1746 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1747 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after ';'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1748 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1749 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1750 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1751 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1752 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1753 | `                tokens.append(Token(TT_SEMICOLON, ident_str, line, pos.col))` | Creates and appends a TT_SEMICOLON token to the token list. |
| 1754 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1755 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1756 | `` | Blank separator line used to visually separate code blocks. |
| 1757 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1758 | `            elif self.current_char == "[":` | Checks whether the current character matches "[" so the lexer can choose that token branch. |
| 1759 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1760 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1761 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1762 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1763 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1764 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1765 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1766 | `                if self.current_char is not None and self.current_char not in open_bracket_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1767 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1768 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '['"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1769 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1770 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1771 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1772 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1773 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1774 | `                tokens.append(Token(TT_LSQBR, ident_str, line, pos.col))` | Creates and appends a TT_LSQBR token to the token list. |
| 1775 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1776 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1777 | `` | Blank separator line used to visually separate code blocks. |
| 1778 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1779 | `            elif self.current_char == "]":` | Checks whether the current character matches "]" so the lexer can choose that token branch. |
| 1780 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1781 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1782 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1783 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1784 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1785 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1786 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1787 | `                if self.current_char is not None and self.current_char not in close_bracket_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1788 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1789 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after ']'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1790 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1791 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1792 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1793 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1794 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1795 | `                tokens.append(Token(TT_RSQBR, ident_str, line, pos.col))` | Creates and appends a TT_RSQBR token to the token list. |
| 1796 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1797 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1798 | `` | Blank separator line used to visually separate code blocks. |
| 1799 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1800 | `            elif self.current_char == "{":` | Checks whether the current character matches "{" so the lexer can choose that token branch. |
| 1801 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1802 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1803 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1804 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1805 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1806 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1807 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1808 | `                if self.current_char is not None and self.current_char not in block_start_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1809 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1810 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{{'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1811 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1812 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1813 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1814 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1815 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1816 | `                tokens.append(Token(TT_BLOCK_START, ident_str, line, pos.col))` | Creates and appends a TT_BLOCK_START token to the token list. |
| 1817 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1818 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1819 | `` | Blank separator line used to visually separate code blocks. |
| 1820 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1821 | `            elif self.current_char == "}":` | Checks whether the current character matches "}" so the lexer can choose that token branch. |
| 1822 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1823 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1824 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1825 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1826 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1827 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1828 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1829 | `                if self.current_char is not None and self.current_char not in block_end_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1830 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1831 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '}}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1832 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1833 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1834 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1835 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1836 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1837 | `                tokens.append(Token(TT_BLOCK_END, ident_str, line, pos.col))` | Creates and appends a TT_BLOCK_END token to the token list. |
| 1838 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1839 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1840 | `` | Blank separator line used to visually separate code blocks. |
| 1841 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1842 | `            elif self.current_char == "\|":` | Checks whether the current character matches "\|" so the lexer can choose that token branch. |
| 1843 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1844 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1845 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1846 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1847 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1848 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1849 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1850 | `                if self.current_char == "\|":` | Checks whether the current character matches "\|" so the lexer can choose that token branch. |
| 1851 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1852 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1853 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1854 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1855 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1856 | `                    if self.current_char is not None and self.current_char not in delim21:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1857 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1858 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1859 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1860 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1861 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1862 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1863 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1864 | `                    tokens.append(Token(TT_OR, ident_str, line, pos.col))` | Creates and appends a TT_OR token to the token list. |
| 1865 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1866 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1867 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 1868 | `                else:` | Fallback path when the previous if/elif condition did not match. |
| 1869 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1870 | `                    tokens.append(Token(TT_SINGLE_OR, ident_str, line, pos.col))` | Creates and appends a TT_SINGLE_OR token to the token list. |
| 1871 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1872 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1873 | `            ` | Blank separator line used to visually separate code blocks. |
| 1874 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1875 | `            elif self.current_char == "+":` | Checks whether the current character matches "+" so the lexer can choose that token branch. |
| 1876 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1877 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1878 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1879 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1880 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1881 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1882 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1883 | `                if self.current_char == "+":` | Checks whether the current character matches "+" so the lexer can choose that token branch. |
| 1884 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1885 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1886 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1887 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1888 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1889 | `                    if self.current_char is not None and self.current_char not in delim25:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1890 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1891 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1892 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1893 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1894 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1895 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1896 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1897 | `                    tokens.append(Token(TT_INCREMENT, ident_str, line, pos.col))` | Creates and appends a TT_INCREMENT token to the token list. |
| 1898 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1899 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1900 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1901 | `                if self.current_char == "=":` | Checks whether the current character matches "=" so the lexer can choose that token branch. |
| 1902 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1903 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1904 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1905 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1906 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1907 | `                    if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1908 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1909 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1910 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1911 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1912 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1913 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1914 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1915 | `                    tokens.append(Token(TT_PLUSEQ, ident_str, line, pos.col))` | Creates and appends a TT_PLUSEQ token to the token list. |
| 1916 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1917 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1918 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1919 | `                if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1920 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1921 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1922 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1923 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1924 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1925 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1926 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1927 | `                tokens.append(Token(TT_PLUS, ident_str, line, pos.col))` | Creates and appends a TT_PLUS token to the token list. |
| 1928 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1929 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1930 | `` | Blank separator line used to visually separate code blocks. |
| 1931 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1932 | `            elif self.current_char == "<":` | Checks whether the current character matches "<" so the lexer can choose that token branch. |
| 1933 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1934 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1935 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1936 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1937 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1938 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1939 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1940 | `                if self.current_char == "=":` | Checks whether the current character matches "=" so the lexer can choose that token branch. |
| 1941 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1942 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1943 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1944 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1945 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1946 | `                    if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1947 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1948 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1949 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1950 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 1951 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1952 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1953 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1954 | `                    tokens.append(Token(TT_LTEQ, ident_str, line, pos.col))` | Creates and appends a TT_LTEQ token to the token list. |
| 1955 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1956 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1957 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1958 | `                if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1959 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1960 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1961 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1962 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1963 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1964 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1965 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1966 | `                tokens.append(Token(TT_LT, ident_str, line, pos.col))` | Creates and appends a TT_LT token to the token list. |
| 1967 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1968 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1969 | `` | Blank separator line used to visually separate code blocks. |
| 1970 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 1971 | `            elif self.current_char == "=":` | Checks whether the current character matches "=" so the lexer can choose that token branch. |
| 1972 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 1973 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 1974 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 1975 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 1976 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1977 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 1978 | `` | Blank separator line used to visually separate code blocks. |
| 1979 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1980 | `                if self.current_char == "=":` | Checks whether the current character matches "=" so the lexer can choose that token branch. |
| 1981 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 1982 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 1983 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1984 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 1985 | `` | Blank separator line used to visually separate code blocks. |
| 1986 | `` | Blank separator line used to visually separate code blocks. |
| 1987 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1988 | `                    if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:` | Looks at the previous token to reject invalid adjacent operators or punctuation. |
| 1989 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1990 | `                        errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1991 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 1992 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 1993 | `` | Blank separator line used to visually separate code blocks. |
| 1994 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 1995 | `                    if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 1996 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 1997 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 1998 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 1999 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2000 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2001 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2002 | `` | Blank separator line used to visually separate code blocks. |
| 2003 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2004 | `                    tokens.append(Token(TT_EQTO, ident_str, line, pos.col))` | Creates and appends a TT_EQTO token to the token list. |
| 2005 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2006 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2007 | `` | Blank separator line used to visually separate code blocks. |
| 2008 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2009 | `                if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 2010 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2011 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2012 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2013 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2014 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2015 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2016 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2017 | `                tokens.append(Token(TT_EQ, ident_str, line, pos.col))` | Creates and appends a TT_EQ token to the token list. |
| 2018 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2019 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2020 | `` | Blank separator line used to visually separate code blocks. |
| 2021 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2022 | `            elif self.current_char == ">":` | Checks whether the current character matches ">" so the lexer can choose that token branch. |
| 2023 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2024 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 2025 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2026 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2027 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2028 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 2029 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2030 | `                if self.current_char == "=":` | Checks whether the current character matches "=" so the lexer can choose that token branch. |
| 2031 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2032 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 2033 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2034 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2035 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2036 | `                    if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:` | Looks at the previous token to reject invalid adjacent operators or punctuation. |
| 2037 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2038 | `                        errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2039 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2040 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2041 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2042 | `                    if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 2043 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2044 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2045 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2046 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2047 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2048 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2049 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2050 | `                    tokens.append(Token(TT_GTEQ, ident_str, line, pos.col))` | Creates and appends a TT_GTEQ token to the token list. |
| 2051 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2052 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2053 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2054 | `                if len(tokens) > 0 and tokens[-1].type in [TT_GT, TT_LT, TT_EQTO, TT_NOTEQ, TT_GTEQ, TT_LTEQ]:` | Looks at the previous token to reject invalid adjacent operators or punctuation. |
| 2055 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2056 | `                    errors.append(LexicalError(pos, f"invalid delimiters '{tokens[-1].value} {ident_str}' are not allowed"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2057 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2058 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2059 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2060 | `                if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 2061 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2062 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2063 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2064 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2065 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2066 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2067 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2068 | `                tokens.append(Token(TT_GT, ident_str, line, pos.col))` | Creates and appends a TT_GT token to the token list. |
| 2069 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2070 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2071 | `` | Blank separator line used to visually separate code blocks. |
| 2072 | `` | Blank separator line used to visually separate code blocks. |
| 2073 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2074 | `            elif self.current_char == '\n':` | Checks whether the current character matches '\n' so the lexer can choose that token branch. |
| 2075 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2076 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2077 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2078 | `                if tokens and tokens[-1].type != TT_NL:` | Looks at the previous token to reject invalid adjacent operators or punctuation. |
| 2079 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2080 | `                    tokens.append(Token(TT_NL, "\\n", line, pos.col))` | Creates and appends a TT_NL token to the token list. |
| 2081 | `` | Blank separator line used to visually separate code blocks. |
| 2082 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2083 | `                while self.current_char == '\t' or self.current_char == ' ' or self.current_char == '\n':` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2084 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2085 | `                    if self.current_char == '\t' or self.current_char == ' ':` | Checks whether the current character matches '\t' so the lexer can choose that token branch. |
| 2086 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2087 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2088 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2089 | `                    else:` | Fallback path when the previous if/elif condition did not match. |
| 2090 | `                        # AUTO: Adds into `line`.` | Comment/guideline: AUTO: Adds into `line`. |
| 2091 | `                        line += 1` | Updates an existing value by adding or appending something to it. |
| 2092 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2093 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2094 | `` | Blank separator line used to visually separate code blocks. |
| 2095 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2096 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2097 | `                ` | Blank separator line used to visually separate code blocks. |
| 2098 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2099 | `            elif self.current_char == '\t':` | Checks whether the current character matches '\t' so the lexer can choose that token branch. |
| 2100 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2101 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 2102 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2103 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2104 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2105 | `                while self.current_char == '\t':` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2106 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2107 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2108 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2109 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2110 | `` | Blank separator line used to visually separate code blocks. |
| 2111 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2112 | `            elif self.current_char == ' ':` | Checks whether the current character matches ' ' so the lexer can choose that token branch. |
| 2113 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2114 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 2115 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2116 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2117 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2118 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 2119 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2120 | `                while self.current_char == ' ':` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2121 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2122 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2123 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2124 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2125 | `` | Blank separator line used to visually separate code blocks. |
| 2126 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2127 | `            elif self.current_char == "/":` | Checks whether the current character matches "/" so the lexer can choose that token branch. |
| 2128 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2129 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 2130 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2131 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2132 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2133 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 2134 | `                ` | Blank separator line used to visually separate code blocks. |
| 2135 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2136 | `                if self.current_char == "/":` | Checks whether the current character matches "/" so the lexer can choose that token branch. |
| 2137 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2138 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 2139 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2140 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2141 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2142 | `                    while self.current_char is not None and self.current_char != "\n":` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2143 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2144 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 2145 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2146 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2147 | `                    # Comments are emitted as tokens so they show up in the` | Comment/guideline: Comments are emitted as tokens so they show up in the |
| 2148 | `                    # lexeme table, but they are filtered out before parsing` | Comment/guideline: lexeme table, but they are filtered out before parsing |
| 2149 | `                    # (see strip_comments) so the parser never sees them.` | Comment/guideline: (see strip_comments) so the parser never sees them. |
| 2150 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2151 | `                    tokens.append(Token(TT_COMMENT, ident_str, line, pos.col))` | Creates and appends a TT_COMMENT token to the token list. |
| 2152 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2153 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2154 | `` | Blank separator line used to visually separate code blocks. |
| 2155 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2156 | `                elif self.current_char == "*":` | Checks whether the current character matches "*" so the lexer can choose that token branch. |
| 2157 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2158 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 2159 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2160 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2161 | `                    # AUTO: Sets `found_close`.` | Comment/guideline: AUTO: Sets `found_close`. |
| 2162 | `                    found_close = False` | Assigns a value to a variable or object attribute used by the lexer. |
| 2163 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2164 | `                    while self.current_char is not None:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2165 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2166 | `                        if self.current_char == "*" and self.pos.index + 1 < len(self.source_code) and self.source_code[self.pos.index + 1] == "/":` | Checks whether the current character matches "*" so the lexer can choose that token branch. |
| 2167 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2168 | `                            ident_str += "*/"` | Updates an existing value by adding or appending something to it. |
| 2169 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2170 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 2171 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2172 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 2173 | `                            # AUTO: Sets `found_close`.` | Comment/guideline: AUTO: Sets `found_close`. |
| 2174 | `                            found_close = True` | Assigns a value to a variable or object attribute used by the lexer. |
| 2175 | `                            # AUTO: Stops the nearest loop.` | Comment/guideline: AUTO: Stops the nearest loop. |
| 2176 | `                            break` | Stops the nearest loop. |
| 2177 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2178 | `                        else:` | Fallback path when the previous if/elif condition did not match. |
| 2179 | `                            # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2180 | `                            ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 2181 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2182 | `                            if self.current_char == "\n":` | Checks whether the current character matches "\n" so the lexer can choose that token branch. |
| 2183 | `                                # AUTO: Adds into `line`.` | Comment/guideline: AUTO: Adds into `line`. |
| 2184 | `                                line += 1` | Updates an existing value by adding or appending something to it. |
| 2185 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2186 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 2187 | `` | Blank separator line used to visually separate code blocks. |
| 2188 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2189 | `                    if not found_close:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2190 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2191 | `                        errors.append(LexicalError(pos, f"Missing closing '*/' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2192 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2193 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2194 | `                    # Multi-line comments are emitted for the lexeme table and` | Comment/guideline: Multi-line comments are emitted for the lexeme table and |
| 2195 | `                    # filtered out before parsing (see strip_comments).` | Comment/guideline: filtered out before parsing (see strip_comments). |
| 2196 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2197 | `                    tokens.append(Token(TT_MCOMMENT, ident_str, line, pos.col))` | Creates and appends a TT_MCOMMENT token to the token list. |
| 2198 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2199 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2200 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2201 | `                elif self.current_char == "=":` | Checks whether the current character matches "=" so the lexer can choose that token branch. |
| 2202 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2203 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 2204 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2205 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2206 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2207 | `                    if self.current_char is not None and self.current_char not in delim24:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 2208 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2209 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2210 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2211 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2212 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2213 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2214 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2215 | `                    tokens.append(Token(TT_DIVEQ, ident_str, line, pos.col))` | Creates and appends a TT_DIVEQ token to the token list. |
| 2216 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2217 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2218 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2219 | `                else:` | Fallback path when the previous if/elif condition did not match. |
| 2220 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2221 | `                    if self.current_char is not None and self.current_char not in delim25:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 2222 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2223 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2224 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2225 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2226 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2227 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2228 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2229 | `                    tokens.append(Token(TT_DIV, ident_str, line, pos.col))` | Creates and appends a TT_DIV token to the token list. |
| 2230 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2231 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2232 | `            ` | Blank separator line used to visually separate code blocks. |
| 2233 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2234 | `            elif self.current_char == ".":` | Checks whether the current character matches "." so the lexer can choose that token branch. |
| 2235 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2236 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 2237 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2238 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2239 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2240 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 2241 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2242 | `                if self.current_char is not None and self.current_char in ALPHA:` | Checks if the current character starts a word/reserved word/identifier. |
| 2243 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2244 | `                    tokens.append(Token(TT_DOT, ident_str, line, pos.col))` | Creates and appends a TT_DOT token to the token list. |
| 2245 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2246 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2247 | `` | Blank separator line used to visually separate code blocks. |
| 2248 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2249 | `                elif self.current_char is not None and self.current_char in ZERODIGIT:` | Checks if the current character starts a numeric literal. |
| 2250 | `                    # AUTO: Sets `fractional_part`.` | Comment/guideline: AUTO: Sets `fractional_part`. |
| 2251 | `                    fractional_part = ""` | Assigns a value to a variable or object attribute used by the lexer. |
| 2252 | `                    # AUTO: Sets `overflow`.` | Comment/guideline: AUTO: Sets `overflow`. |
| 2253 | `                    overflow = False` | Assigns a value to a variable or object attribute used by the lexer. |
| 2254 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2255 | `                    while self.current_char is not None and self.current_char in ZERODIGIT:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2256 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2257 | `                        if len(fractional_part + self.current_char) > 8: ` | Conditional check that decides which lexer path or validation rule runs next. |
| 2258 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2259 | `                            errors.append(LexicalError(pos, f"'{ident_str}' exceeds maximum number of decimal places"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2260 | `                            # AUTO: Sets `overflow`.` | Comment/guideline: AUTO: Sets `overflow`. |
| 2261 | `                            overflow = True` | Assigns a value to a variable or object attribute used by the lexer. |
| 2262 | `                            # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2263 | `                            while self.current_char is not None and self.current_char in ZERODIGIT:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2264 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2265 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 2266 | `                            # AUTO: Stops the nearest loop.` | Comment/guideline: AUTO: Stops the nearest loop. |
| 2267 | `                            break` | Stops the nearest loop. |
| 2268 | `` | Blank separator line used to visually separate code blocks. |
| 2269 | `                        # AUTO: Adds into `fractional_part`.` | Comment/guideline: AUTO: Adds into `fractional_part`. |
| 2270 | `                        fractional_part += self.current_char` | Updates an existing value by adding or appending something to it. |
| 2271 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2272 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2273 | `                    ` | Blank separator line used to visually separate code blocks. |
| 2274 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2275 | `                    if overflow:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2276 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2277 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2278 | `                        ` | Blank separator line used to visually separate code blocks. |
| 2279 | `                    # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2280 | `                    ident_str = f"0.{fractional_part}"` | Assigns a value to a variable or object attribute used by the lexer. |
| 2281 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2282 | `                    tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))` | Creates and appends a TT_DOUBLELIT token to the token list. |
| 2283 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2284 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2285 | `                    ` | Blank separator line used to visually separate code blocks. |
| 2286 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2287 | `                else:` | Fallback path when the previous if/elif condition did not match. |
| 2288 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2289 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2290 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2291 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2292 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2293 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2294 | `            ` | Blank separator line used to visually separate code blocks. |
| 2295 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2296 | `            elif self.current_char == ":":` | Checks whether the current character matches ":" so the lexer can choose that token branch. |
| 2297 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2298 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 2299 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2300 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2301 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2302 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 2303 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2304 | `                if self.current_char is not None and self.current_char not in case_colon_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 2305 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2306 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after ':'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2307 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2308 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2309 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2310 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2311 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2312 | `                tokens.append(Token(TT_COLON, ident_str, line, pos.col))` | Creates and appends a TT_COLON token to the token list. |
| 2313 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2314 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2315 | `` | Blank separator line used to visually separate code blocks. |
| 2316 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2317 | `            elif self.current_char in ZERODIGIT:` | Checks if the current character starts a numeric literal. |
| 2318 | `                # GUIDE: Numeric literal state collects integers, doubles, and` | Comment/guideline: GUIDE: Numeric literal state collects integers, doubles, and |
| 2319 | `                # scientific notation before deciding intlit vs dblit.` | Comment/guideline: scientific notation before deciding intlit vs dblit. |
| 2320 | `                # AUTO: Sets `dot_count`.` | Comment/guideline: AUTO: Sets `dot_count`. |
| 2321 | `                dot_count = 0` | Assigns a value to a variable or object attribute used by the lexer. |
| 2322 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2323 | `                ident_str = ""` | Starts an empty lexeme string for building a token text. |
| 2324 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2325 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2326 | `                # AUTO: Sets `integer_digit_count`.` | Comment/guideline: AUTO: Sets `integer_digit_count`. |
| 2327 | `                integer_digit_count = 0` | Assigns a value to a variable or object attribute used by the lexer. |
| 2328 | `                # AUTO: Sets `fractional_digit_count`.` | Comment/guideline: AUTO: Sets `fractional_digit_count`. |
| 2329 | `                fractional_digit_count = 0` | Assigns a value to a variable or object attribute used by the lexer. |
| 2330 | `                # AUTO: Sets `has_e`.` | Comment/guideline: AUTO: Sets `has_e`. |
| 2331 | `                has_e = False` | Assigns a value to a variable or object attribute used by the lexer. |
| 2332 | `` | Blank separator line used to visually separate code blocks. |
| 2333 | `                ` | Blank separator line used to visually separate code blocks. |
| 2334 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2335 | `                while self.current_char is not None and self.current_char in ZERODIGIT:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2336 | `                    # AUTO: Adds into `integer_digit_count`.` | Comment/guideline: AUTO: Adds into `integer_digit_count`. |
| 2337 | `                    integer_digit_count += 1` | Counts one more digit in the integer part of a number. |
| 2338 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2339 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 2340 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2341 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2342 | `` | Blank separator line used to visually separate code blocks. |
| 2343 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2344 | `                if self.current_char == ".":` | Checks whether the current character matches "." so the lexer can choose that token branch. |
| 2345 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2346 | `                    if integer_digit_count > 15:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2347 | `                        # AUTO: Sets `integer_part`.` | Comment/guideline: AUTO: Sets `integer_part`. |
| 2348 | `                        integer_part = ident_str` | Assigns a value to a variable or object attribute used by the lexer. |
| 2349 | `                        # AUTO: Sets `i`.` | Comment/guideline: AUTO: Sets `i`. |
| 2350 | `                        i = 0` | Assigns a value to a variable or object attribute used by the lexer. |
| 2351 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2352 | `                        while i < len(integer_part):` | Loop that repeats until its condition becomes false. |
| 2353 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2354 | `                            if i + 15 < len(integer_part):` | Conditional check that decides which lexer path or validation rule runs next. |
| 2355 | `                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2356 | `                                errors.append(LexicalError(pos, f"Integer part of decimal exceeds maximum of 15 digits"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2357 | `                                # AUTO: Adds into `i`.` | Comment/guideline: AUTO: Adds into `i`. |
| 2358 | `                                i += 15` | Updates an existing value by adding or appending something to it. |
| 2359 | `                            # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2360 | `                            else:` | Fallback path when the previous if/elif condition did not match. |
| 2361 | `                                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2362 | `                                ident_str = integer_part[i:]` | Assigns a value to a variable or object attribute used by the lexer. |
| 2363 | `                                # AUTO: Stops the nearest loop.` | Comment/guideline: AUTO: Stops the nearest loop. |
| 2364 | `                                break` | Stops the nearest loop. |
| 2365 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2366 | `                        else:` | Fallback path when the previous if/elif condition did not match. |
| 2367 | `                            # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2368 | `                            ident_str = "0"` | Assigns a value to a variable or object attribute used by the lexer. |
| 2369 | `                    # AUTO: Sets `dot_count`.` | Comment/guideline: AUTO: Sets `dot_count`. |
| 2370 | `                    dot_count = 1` | Assigns a value to a variable or object attribute used by the lexer. |
| 2371 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2372 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 2373 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2374 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2375 | `                    ` | Blank separator line used to visually separate code blocks. |
| 2376 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2377 | `                    if self.current_char is None or self.current_char not in ZERODIGIT:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2378 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2379 | `                        errors.append(LexicalError(pos, f"Invalid number '{ident_str}': decimal point must be followed by digits"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2380 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2381 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2382 | `                    ` | Blank separator line used to visually separate code blocks. |
| 2383 | `                    # AUTO: Sets `fractional_part`.` | Comment/guideline: AUTO: Sets `fractional_part`. |
| 2384 | `                    fractional_part = ""` | Assigns a value to a variable or object attribute used by the lexer. |
| 2385 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2386 | `                    while self.current_char is not None and self.current_char in ZERODIGIT:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2387 | `                        # AUTO: Adds into `fractional_digit_count`.` | Comment/guideline: AUTO: Adds into `fractional_digit_count`. |
| 2388 | `                        fractional_digit_count += 1` | Counts one more digit in the fractional part of a decimal number. |
| 2389 | `                        # AUTO: Adds into `fractional_part`.` | Comment/guideline: AUTO: Adds into `fractional_part`. |
| 2390 | `                        fractional_part += self.current_char` | Updates an existing value by adding or appending something to it. |
| 2391 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2392 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2393 | `                    ` | Blank separator line used to visually separate code blocks. |
| 2394 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2395 | `                    if fractional_digit_count > 8:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2396 | `                        # AUTO: Sets `i`.` | Comment/guideline: AUTO: Sets `i`. |
| 2397 | `                        i = 0` | Assigns a value to a variable or object attribute used by the lexer. |
| 2398 | `                        # AUTO: Sets `final_fractional`.` | Comment/guideline: AUTO: Sets `final_fractional`. |
| 2399 | `                        final_fractional = ""` | Assigns a value to a variable or object attribute used by the lexer. |
| 2400 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2401 | `                        while i < len(fractional_part):` | Loop that repeats until its condition becomes false. |
| 2402 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2403 | `                            if i + 8 < len(fractional_part):` | Conditional check that decides which lexer path or validation rule runs next. |
| 2404 | `                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2405 | `                                errors.append(LexicalError(pos, f"Fractional part exceeds maximum of 8 digits"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2406 | `                                # AUTO: Adds into `i`.` | Comment/guideline: AUTO: Adds into `i`. |
| 2407 | `                                i += 8` | Updates an existing value by adding or appending something to it. |
| 2408 | `                            # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2409 | `                            else:` | Fallback path when the previous if/elif condition did not match. |
| 2410 | `                                # AUTO: Sets `final_fractional`.` | Comment/guideline: AUTO: Sets `final_fractional`. |
| 2411 | `                                final_fractional = fractional_part[i:]` | Assigns a value to a variable or object attribute used by the lexer. |
| 2412 | `                                # AUTO: Stops the nearest loop.` | Comment/guideline: AUTO: Stops the nearest loop. |
| 2413 | `                                break` | Stops the nearest loop. |
| 2414 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2415 | `                        ident_str += final_fractional` | Updates an existing value by adding or appending something to it. |
| 2416 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2417 | `                    else:` | Fallback path when the previous if/elif condition did not match. |
| 2418 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2419 | `                        ident_str += fractional_part` | Updates an existing value by adding or appending something to it. |
| 2420 | `` | Blank separator line used to visually separate code blocks. |
| 2421 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2422 | `                if dot_count == 0 and integer_digit_count > 8:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2423 | `                    # AUTO: Sets `i`.` | Comment/guideline: AUTO: Sets `i`. |
| 2424 | `                    i = 0` | Assigns a value to a variable or object attribute used by the lexer. |
| 2425 | `                    # AUTO: Sets `remaining`.` | Comment/guideline: AUTO: Sets `remaining`. |
| 2426 | `                    remaining = None` | Assigns a value to a variable or object attribute used by the lexer. |
| 2427 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2428 | `                    while i < len(ident_str):` | Loop that repeats until its condition becomes false. |
| 2429 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2430 | `                        if i + 8 < len(ident_str):` | Conditional check that decides which lexer path or validation rule runs next. |
| 2431 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2432 | `                            errors.append(LexicalError(pos, f"Integer exceeds maximum of 8 digits"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2433 | `                            # AUTO: Adds into `i`.` | Comment/guideline: AUTO: Adds into `i`. |
| 2434 | `                            i += 8` | Updates an existing value by adding or appending something to it. |
| 2435 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2436 | `                        else:` | Fallback path when the previous if/elif condition did not match. |
| 2437 | `                            # AUTO: Sets `remaining`.` | Comment/guideline: AUTO: Sets `remaining`. |
| 2438 | `                            remaining = ident_str[i:]` | Assigns a value to a variable or object attribute used by the lexer. |
| 2439 | `                            # AUTO: Sets `remaining`.` | Comment/guideline: AUTO: Sets `remaining`. |
| 2440 | `                            remaining = remaining.lstrip("0") or "0"` | Assigns a value to a variable or object attribute used by the lexer. |
| 2441 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2442 | `                            tokens.append(Token(TT_INTEGERLIT, remaining, line, pos.col))` | Creates and appends a TT_INTEGERLIT token to the token list. |
| 2443 | `                            # AUTO: Stops the nearest loop.` | Comment/guideline: AUTO: Stops the nearest loop. |
| 2444 | `                            break` | Stops the nearest loop. |
| 2445 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2446 | `                    if remaining is None:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2447 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2448 | `                        tokens.append(Token(TT_INTEGERLIT, "0", line, pos.col))` | Creates and appends a TT_INTEGERLIT token to the token list. |
| 2449 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2450 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2451 | `                ` | Blank separator line used to visually separate code blocks. |
| 2452 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2453 | `                if fractional_digit_count > 8:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2454 | `                    # AUTO: Does nothing for this required block.` | Comment/guideline: AUTO: Does nothing for this required block. |
| 2455 | `                    pass` | Executes this Python statement as part of the lexer logic. |
| 2456 | `` | Blank separator line used to visually separate code blocks. |
| 2457 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2458 | `                if self.current_char is not None and self.current_char in 'eE' and dot_count == 1:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2459 | `                    # AUTO: Sets `has_e`.` | Comment/guideline: AUTO: Sets `has_e`. |
| 2460 | `                    has_e = True` | Assigns a value to a variable or object attribute used by the lexer. |
| 2461 | `                    # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2462 | `                    ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 2463 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2464 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2465 | `                    ` | Blank separator line used to visually separate code blocks. |
| 2466 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2467 | `                    if self.current_char in '+-':` | Conditional check that decides which lexer path or validation rule runs next. |
| 2468 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2469 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 2470 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2471 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2472 | `                    ` | Blank separator line used to visually separate code blocks. |
| 2473 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2474 | `                    if self.current_char is None or self.current_char not in ZERODIGIT:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2475 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2476 | `                        errors.append(LexicalError(pos, f"Invalid scientific notation: 'e' must be followed by digits."))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2477 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2478 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2479 | `                    ` | Blank separator line used to visually separate code blocks. |
| 2480 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2481 | `                    while self.current_char is not None and self.current_char in ZERODIGIT:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2482 | `                        # AUTO: Adds into `ident_str`.` | Comment/guideline: AUTO: Adds into `ident_str`. |
| 2483 | `                        ident_str += self.current_char` | Adds the current character to the lexeme currently being built. |
| 2484 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2485 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2486 | `` | Blank separator line used to visually separate code blocks. |
| 2487 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2488 | `                if dot_count == 0 and not has_e:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2489 | `                    ` | Blank separator line used to visually separate code blocks. |
| 2490 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2491 | `                    if self.current_char is not None and self.current_char not in whlnum_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 2492 | `                        # AUTO: Sets `valid_int`.` | Comment/guideline: AUTO: Sets `valid_int`. |
| 2493 | `                        valid_int = ident_str.lstrip("0") or "0"` | Assigns a value to a variable or object attribute used by the lexer. |
| 2494 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2495 | `                        tokens.append(Token(TT_INTEGERLIT, valid_int, line, pos.col))` | Creates and appends a TT_INTEGERLIT token to the token list. |
| 2496 | `                        ` | Blank separator line used to visually separate code blocks. |
| 2497 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2498 | `                        if self.current_char in ALPHA:` | Checks if the current character starts a word/reserved word/identifier. |
| 2499 | `                            # AUTO: Sets `temp_str`.` | Comment/guideline: AUTO: Sets `temp_str`. |
| 2500 | `                            temp_str = ''` | Assigns a value to a variable or object attribute used by the lexer. |
| 2501 | `                            # AUTO: Sets `temp_pos`.` | Comment/guideline: AUTO: Sets `temp_pos`. |
| 2502 | `                            temp_pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2503 | `                            # AUTO: Sets `temp_char`.` | Comment/guideline: AUTO: Sets `temp_char`. |
| 2504 | `                            temp_char = self.current_char` | Assigns a value to a variable or object attribute used by the lexer. |
| 2505 | `                            # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2506 | `                            while temp_char is not None and temp_char in ALPHANUM:` | Loop that repeats until its condition becomes false. |
| 2507 | `                                # AUTO: Adds into `temp_str`.` | Comment/guideline: AUTO: Adds into `temp_str`. |
| 2508 | `                                temp_str += temp_char` | Updates an existing value by adding or appending something to it. |
| 2509 | `                                # AUTO: Calls `temp_pos.advance`.` | Comment/guideline: AUTO: Calls `temp_pos.advance`. |
| 2510 | `                                temp_pos.advance(temp_char)` | Executes this Python statement as part of the lexer logic. |
| 2511 | `                                # AUTO: Sets `temp_char`.` | Comment/guideline: AUTO: Sets `temp_char`. |
| 2512 | `                                temp_char = self.source_code[temp_pos.index] if temp_pos.index < len(self.source_code) else None` | Assigns a value to a variable or object attribute used by the lexer. |
| 2513 | `                            ` | Blank separator line used to visually separate code blocks. |
| 2514 | `                            # AUTO: Sets `reserved_words`.` | Comment/guideline: AUTO: Sets `reserved_words`. |
| 2515 | `                            reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', ` | Assigns a value to a variable or object attribute used by the lexer. |
| 2516 | `                                            # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2517 | `                                            'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', ` | Executes this Python statement as part of the lexer logic. |
| 2518 | `                                            # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2519 | `                                            'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}` | Executes this Python statement as part of the lexer logic. |
| 2520 | `                            ` | Blank separator line used to visually separate code blocks. |
| 2521 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2522 | `                            if temp_str in reserved_words:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2523 | `                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2524 | `                                errors.append(LexicalError(pos, f"Reserved word cannot start with a number: '{ident_str}{temp_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2525 | `                            # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2526 | `                            else:` | Fallback path when the previous if/elif condition did not match. |
| 2527 | `                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2528 | `                                errors.append(LexicalError(pos, f"Identifiers cannot start with a number: '{ident_str}{self.current_char}...'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2529 | `                            ` | Blank separator line used to visually separate code blocks. |
| 2530 | `                            # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2531 | `                            while self.current_char is not None and self.current_char in ALPHANUM:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2532 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2533 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 2534 | `                        # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2535 | `                        elif self.current_char == '_':` | Checks whether the current character matches '_' so the lexer can choose that token branch. |
| 2536 | `                            # AUTO: Sets `temp_index`.` | Comment/guideline: AUTO: Sets `temp_index`. |
| 2537 | `                            temp_index = self.pos.index + 1` | Assigns a value to a variable or object attribute used by the lexer. |
| 2538 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2539 | `                            if temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHA:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2540 | `                                # AUTO: Sets `temp_str`.` | Comment/guideline: AUTO: Sets `temp_str`. |
| 2541 | `                                temp_str = ''` | Assigns a value to a variable or object attribute used by the lexer. |
| 2542 | `                                # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2543 | `                                while temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHANUM:` | Loop that repeats until its condition becomes false. |
| 2544 | `                                    # AUTO: Adds into `temp_str`.` | Comment/guideline: AUTO: Adds into `temp_str`. |
| 2545 | `                                    temp_str += self.source_code[temp_index]` | Updates an existing value by adding or appending something to it. |
| 2546 | `                                    # AUTO: Adds into `temp_index`.` | Comment/guideline: AUTO: Adds into `temp_index`. |
| 2547 | `                                    temp_index += 1` | Updates an existing value by adding or appending something to it. |
| 2548 | `                                ` | Blank separator line used to visually separate code blocks. |
| 2549 | `                                # AUTO: Sets `reserved_words`.` | Comment/guideline: AUTO: Sets `reserved_words`. |
| 2550 | `                                reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', ` | Assigns a value to a variable or object attribute used by the lexer. |
| 2551 | `                                                # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2552 | `                                                'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', ` | Executes this Python statement as part of the lexer logic. |
| 2553 | `                                                # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2554 | `                                                'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}` | Executes this Python statement as part of the lexer logic. |
| 2555 | `                                ` | Blank separator line used to visually separate code blocks. |
| 2556 | `                                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2557 | `                                if temp_str in reserved_words:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2558 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2559 | `                                    errors.append(LexicalError(pos, f"Reserved word cannot start with a number: '{ident_str}_{temp_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2560 | `                                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2561 | `                                else:` | Fallback path when the previous if/elif condition did not match. |
| 2562 | `                                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2563 | `                                    errors.append(LexicalError(pos, f"Identifiers cannot start with a number: '{ident_str}_...'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2564 | `                                ` | Blank separator line used to visually separate code blocks. |
| 2565 | `                                # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2566 | `                                while self.current_char is not None and self.current_char in ALPHANUM:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2567 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2568 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2569 | `                            # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2570 | `                            else:` | Fallback path when the previous if/elif condition did not match. |
| 2571 | `                                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2572 | `                                errors.append(LexicalError(pos, f"Underscore cannot be used in numeric literals"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2573 | `                                # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2574 | `                                while self.current_char is not None and self.current_char in ALPHANUM:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2575 | `                                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2576 | `                                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2577 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2578 | `                        else:` | Fallback path when the previous if/elif condition did not match. |
| 2579 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2580 | `                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2581 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2582 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2583 | `                    ` | Blank separator line used to visually separate code blocks. |
| 2584 | `                    # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2585 | `                    ident_str = ident_str.lstrip("0") or "0"` | Assigns a value to a variable or object attribute used by the lexer. |
| 2586 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2587 | `                    tokens.append(Token(TT_INTEGERLIT, ident_str, line, pos.col))` | Creates and appends a TT_INTEGERLIT token to the token list. |
| 2588 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2589 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2590 | `                    ` | Blank separator line used to visually separate code blocks. |
| 2591 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2592 | `                else:` | Fallback path when the previous if/elif condition did not match. |
| 2593 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2594 | `                    if self.current_char is not None and self.current_char not in decim_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 2595 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2596 | `                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2597 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2598 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2599 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2600 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2601 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2602 | `                    if not has_e:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2603 | `                         # AUTO: Sets `parts`.` | Comment/guideline: AUTO: Sets `parts`. |
| 2604 | `                         parts = ident_str.split(".")` | Assigns a value to a variable or object attribute used by the lexer. |
| 2605 | `                         # AUTO: Sets `integer_part`.` | Comment/guideline: AUTO: Sets `integer_part`. |
| 2606 | `                         integer_part = parts[0].lstrip("0") or "0"` | Assigns a value to a variable or object attribute used by the lexer. |
| 2607 | `                         # AUTO: Sets `fractional_part`.` | Comment/guideline: AUTO: Sets `fractional_part`. |
| 2608 | `                         fractional_part = (parts[1] if len(parts) > 1 else "").rstrip("0") or "0"` | Assigns a value to a variable or object attribute used by the lexer. |
| 2609 | `                         # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2610 | `                         if fractional_part == "0":` | Conditional check that decides which lexer path or validation rule runs next. |
| 2611 | `                             # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2612 | `                             ident_str = f"{integer_part}.0"` | Assigns a value to a variable or object attribute used by the lexer. |
| 2613 | `                         # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2614 | `                         else:` | Fallback path when the previous if/elif condition did not match. |
| 2615 | `                             # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2616 | `                             ident_str = f"{integer_part}.{fractional_part}"` | Assigns a value to a variable or object attribute used by the lexer. |
| 2617 | `` | Blank separator line used to visually separate code blocks. |
| 2618 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2619 | `                    tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))` | Creates and appends a TT_DOUBLELIT token to the token list. |
| 2620 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2621 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2622 | `` | Blank separator line used to visually separate code blocks. |
| 2623 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2624 | `            elif self.current_char == '"':` | Checks whether the current character matches '" so the lexer can choose that token branch. |
| 2625 | `                # GUIDE: String literals keep the quotes in the token value so the` | Comment/guideline: GUIDE: String literals keep the quotes in the token value so the |
| 2626 | `                # parser sees the whole quoted text as one stringlit token.` | Comment/guideline: parser sees the whole quoted text as one stringlit token. |
| 2627 | `                # AUTO: Sets `string`.` | Comment/guideline: AUTO: Sets `string`. |
| 2628 | `                string = ''` | Creates an empty Python string used to collect a GAL string literal. |
| 2629 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2630 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2631 | `                # AUTO: Sets `escape_character`.` | Comment/guideline: AUTO: Sets `escape_character`. |
| 2632 | `                escape_character = False` | Assigns a value to a variable or object attribute used by the lexer. |
| 2633 | `                # AUTO: Adds into `string`.` | Comment/guideline: AUTO: Adds into `string`. |
| 2634 | `                string += self.current_char` | Adds the current character to the string literal being collected. |
| 2635 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2636 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 2637 | `` | Blank separator line used to visually separate code blocks. |
| 2638 | `                # AUTO: Sets `escape_characters`.` | Comment/guideline: AUTO: Sets `escape_characters`. |
| 2639 | `                escape_characters = {` | Assigns a value to a variable or object attribute used by the lexer. |
| 2640 | `                    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2641 | `                    'n': '\n',` | Executes this Python statement as part of the lexer logic. |
| 2642 | `                    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2643 | `                    't': '\t',` | Executes this Python statement as part of the lexer logic. |
| 2644 | `                    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2645 | `                    '{': '\\{',` | Executes this Python statement as part of the lexer logic. |
| 2646 | `                    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2647 | `                    '}': '\\}',` | Executes this Python statement as part of the lexer logic. |
| 2648 | `                    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2649 | `                    '"': '"',` | Executes this Python statement as part of the lexer logic. |
| 2650 | `                    # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2651 | `                    '\\': '\\',` | Executes this Python statement as part of the lexer logic. |
| 2652 | `                # AUTO: Closes the current grouped code/data.` | Comment/guideline: AUTO: Closes the current grouped code/data. |
| 2653 | `                }` | Closes a grouped expression, list, dictionary, tuple, call, or block. |
| 2654 | `` | Blank separator line used to visually separate code blocks. |
| 2655 | `                # AUTO: Sets `has_string_error`.` | Comment/guideline: AUTO: Sets `has_string_error`. |
| 2656 | `                has_string_error = False` | Assigns a value to a variable or object attribute used by the lexer. |
| 2657 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2658 | `                while self.current_char is not None and (self.current_char != '"' or escape_character):` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2659 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2660 | `                    if escape_character:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2661 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2662 | `                        if self.current_char in escape_characters:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2663 | `                            # AUTO: Adds into `string`.` | Comment/guideline: AUTO: Adds into `string`. |
| 2664 | `                            string += escape_characters[self.current_char]` | Updates an existing value by adding or appending something to it. |
| 2665 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2666 | `                        else:` | Fallback path when the previous if/elif condition did not match. |
| 2667 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2668 | `                            errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}' in string literal"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2669 | `                            # AUTO: Sets `has_string_error`.` | Comment/guideline: AUTO: Sets `has_string_error`. |
| 2670 | `                            has_string_error = True` | Assigns a value to a variable or object attribute used by the lexer. |
| 2671 | `                        # AUTO: Sets `escape_character`.` | Comment/guideline: AUTO: Sets `escape_character`. |
| 2672 | `                        escape_character = False` | Assigns a value to a variable or object attribute used by the lexer. |
| 2673 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2674 | `                    else:` | Fallback path when the previous if/elif condition did not match. |
| 2675 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2676 | `                        if self.current_char == '\\':` | Checks whether the current character matches '\\' so the lexer can choose that token branch. |
| 2677 | `                            # AUTO: Sets `escape_character`.` | Comment/guideline: AUTO: Sets `escape_character`. |
| 2678 | `                            escape_character = True` | Assigns a value to a variable or object attribute used by the lexer. |
| 2679 | `                        # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2680 | `                        elif self.current_char == '\n':` | Checks whether the current character matches '\n' so the lexer can choose that token branch. |
| 2681 | `                            # AUTO: Stops the nearest loop.` | Comment/guideline: AUTO: Stops the nearest loop. |
| 2682 | `                            break` | Stops the nearest loop. |
| 2683 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2684 | `                        else:` | Fallback path when the previous if/elif condition did not match. |
| 2685 | `                            # AUTO: Adds into `string`.` | Comment/guideline: AUTO: Adds into `string`. |
| 2686 | `                            string += self.current_char` | Adds the current character to the string literal being collected. |
| 2687 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2688 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2689 | `` | Blank separator line used to visually separate code blocks. |
| 2690 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2691 | `                if has_string_error:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2692 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2693 | `                    while self.current_char is not None and self.current_char != '"':` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2694 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2695 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2696 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2697 | `                    if self.current_char == '"':` | Checks whether the current character matches '" so the lexer can choose that token branch. |
| 2698 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2699 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2700 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2701 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2702 | `` | Blank separator line used to visually separate code blocks. |
| 2703 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2704 | `                if self.current_char == '"':` | Checks whether the current character matches '" so the lexer can choose that token branch. |
| 2705 | `                    # AUTO: Adds into `string`.` | Comment/guideline: AUTO: Adds into `string`. |
| 2706 | `                    string += self.current_char` | Adds the current character to the string literal being collected. |
| 2707 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2708 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2709 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2710 | `                else:` | Fallback path when the previous if/elif condition did not match. |
| 2711 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2712 | `                    errors.append(LexicalError(pos, f"Missing closing '\"' for string literal"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2713 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2714 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2715 | `` | Blank separator line used to visually separate code blocks. |
| 2716 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2717 | `                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 2718 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2719 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after string literal '{string}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2720 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2721 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2722 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2723 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2724 | `            ` | Blank separator line used to visually separate code blocks. |
| 2725 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2726 | `                tokens.append(Token(TT_STRINGLIT, string, line, pos.col))` | Creates and appends a TT_STRINGLIT token to the token list. |
| 2727 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2728 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2729 | `    ` | Blank separator line used to visually separate code blocks. |
| 2730 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2731 | `            elif self.current_char == "'":` | Checks whether the current character matches "' so the lexer can choose that token branch. |
| 2732 | `                # AUTO: Sets `string`.` | Comment/guideline: AUTO: Sets `string`. |
| 2733 | `                string = ''` | Creates an empty Python string used to collect a GAL string literal. |
| 2734 | `                # AUTO: Sets `char`.` | Comment/guideline: AUTO: Sets `char`. |
| 2735 | `                char = ''` | Assigns a value to a variable or object attribute used by the lexer. |
| 2736 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2737 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2738 | `                # AUTO: Adds into `string`.` | Comment/guideline: AUTO: Adds into `string`. |
| 2739 | `                string += self.current_char` | Adds the current character to the string literal being collected. |
| 2740 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2741 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 2742 | `                # AUTO: Sets `has_error`.` | Comment/guideline: AUTO: Sets `has_error`. |
| 2743 | `                has_error = False` | Assigns a value to a variable or object attribute used by the lexer. |
| 2744 | `` | Blank separator line used to visually separate code blocks. |
| 2745 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2746 | `                while self.current_char is not None and self.current_char in ' \t':` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2747 | `                    # AUTO: Adds into `string`.` | Comment/guideline: AUTO: Adds into `string`. |
| 2748 | `                    string += self.current_char` | Adds the current character to the string literal being collected. |
| 2749 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2750 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2751 | `` | Blank separator line used to visually separate code blocks. |
| 2752 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2753 | `                while self.current_char is not None and self.current_char != "'":` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2754 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2755 | `                    if self.current_char == '\n':` | Checks whether the current character matches '\n' so the lexer can choose that token branch. |
| 2756 | `                        # AUTO: Stops the nearest loop.` | Comment/guideline: AUTO: Stops the nearest loop. |
| 2757 | `                        break` | Stops the nearest loop. |
| 2758 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2759 | `                    elif self.current_char == '\\':` | Checks whether the current character matches '\\' so the lexer can choose that token branch. |
| 2760 | `                        # AUTO: Adds into `string`.` | Comment/guideline: AUTO: Adds into `string`. |
| 2761 | `                        string += self.current_char` | Adds the current character to the string literal being collected. |
| 2762 | `                        # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2763 | `                        self.advance()` | Moves the lexer to the next character in the source code. |
| 2764 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2765 | `                        if self.current_char is None:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2766 | `                            # AUTO: Stops the nearest loop.` | Comment/guideline: AUTO: Stops the nearest loop. |
| 2767 | `                            break` | Stops the nearest loop. |
| 2768 | `                        ` | Blank separator line used to visually separate code blocks. |
| 2769 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2770 | `                        if self.current_char in "'\\nt": ` | Conditional check that decides which lexer path or validation rule runs next. |
| 2771 | `                            # AUTO: Adds into `char`.` | Comment/guideline: AUTO: Adds into `char`. |
| 2772 | `                            char += f"\\{self.current_char}"` | Updates an existing value by adding or appending something to it. |
| 2773 | `                            # AUTO: Adds into `string`.` | Comment/guideline: AUTO: Adds into `string`. |
| 2774 | `                            string += self.current_char` | Adds the current character to the string literal being collected. |
| 2775 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2776 | `                        else:` | Fallback path when the previous if/elif condition did not match. |
| 2777 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2778 | `                            errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}' in character literal"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2779 | `                            # AUTO: Sets `has_error`.` | Comment/guideline: AUTO: Sets `has_error`. |
| 2780 | `                            has_error = True` | Assigns a value to a variable or object attribute used by the lexer. |
| 2781 | `                            # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2782 | `                            while self.current_char is not None and self.current_char != "'":` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2783 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2784 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 2785 | `                            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2786 | `                            if self.current_char == "'":` | Checks whether the current character matches "' so the lexer can choose that token branch. |
| 2787 | `                                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2788 | `                                self.advance()` | Moves the lexer to the next character in the source code. |
| 2789 | `                            # AUTO: Stops the nearest loop.` | Comment/guideline: AUTO: Stops the nearest loop. |
| 2790 | `                            break` | Stops the nearest loop. |
| 2791 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2792 | `                    else:` | Fallback path when the previous if/elif condition did not match. |
| 2793 | `                        # AUTO: Adds into `string`.` | Comment/guideline: AUTO: Adds into `string`. |
| 2794 | `                        string += self.current_char` | Adds the current character to the string literal being collected. |
| 2795 | `                        # AUTO: Adds into `char`.` | Comment/guideline: AUTO: Adds into `char`. |
| 2796 | `                        char += self.current_char` | Updates an existing value by adding or appending something to it. |
| 2797 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2798 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2799 | `                ` | Blank separator line used to visually separate code blocks. |
| 2800 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2801 | `                while len(char) > 0 and char[-1] in ' \t':` | Loop that repeats until its condition becomes false. |
| 2802 | `                    # AUTO: Sets `char`.` | Comment/guideline: AUTO: Sets `char`. |
| 2803 | `                    char = char[:-1]` | Assigns a value to a variable or object attribute used by the lexer. |
| 2804 | `` | Blank separator line used to visually separate code blocks. |
| 2805 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2806 | `                if has_error:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2807 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2808 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2809 | `` | Blank separator line used to visually separate code blocks. |
| 2810 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2811 | `                if self.current_char == "'":` | Checks whether the current character matches "' so the lexer can choose that token branch. |
| 2812 | `                    # AUTO: Adds into `string`.` | Comment/guideline: AUTO: Adds into `string`. |
| 2813 | `                    string += self.current_char` | Adds the current character to the string literal being collected. |
| 2814 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2815 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2816 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2817 | `                else:` | Fallback path when the previous if/elif condition did not match. |
| 2818 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2819 | `                    errors.append(LexicalError(pos, f"Missing closing quote for character literal"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2820 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2821 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2822 | `` | Blank separator line used to visually separate code blocks. |
| 2823 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2824 | `                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:` | Delimiter validation: reports an error if the next character is not allowed after the token. |
| 2825 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2826 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{string}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2827 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2828 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2829 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2830 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2831 | `` | Blank separator line used to visually separate code blocks. |
| 2832 | `                # AUTO: Sets `inner`.` | Comment/guideline: AUTO: Sets `inner`. |
| 2833 | `                inner = char.strip()` | Assigns a value to a variable or object attribute used by the lexer. |
| 2834 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2835 | `                if len(inner) == 0:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2836 | `                    # AUTO: Sets `string`.` | Comment/guideline: AUTO: Sets `string`. |
| 2837 | `                    string = "' '"` | Assigns a value to a variable or object attribute used by the lexer. |
| 2838 | `                    # AUTO: Sets `inner`.` | Comment/guideline: AUTO: Sets `inner`. |
| 2839 | `                    inner = ' '` | Assigns a value to a variable or object attribute used by the lexer. |
| 2840 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2841 | `                elif inner.startswith('\\') and len(inner) == 2:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2842 | `                    # AUTO: Does nothing for this required block.` | Comment/guideline: AUTO: Does nothing for this required block. |
| 2843 | `                    pass` | Executes this Python statement as part of the lexer logic. |
| 2844 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2845 | `                elif len(inner) > 1:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2846 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2847 | `                    errors.append(LexicalError(pos, f"Character literal must contain exactly one character, found '{inner}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2848 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2849 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2850 | `` | Blank separator line used to visually separate code blocks. |
| 2851 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2852 | `                tokens.append(Token(TT_CHARLIT, string, line, pos.col))` | Creates and appends a TT_CHARLIT token to the token list. |
| 2853 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2854 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2855 | `` | Blank separator line used to visually separate code blocks. |
| 2856 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline: AUTO: Checks the next alternate condition. |
| 2857 | `            elif self.current_char == '`':` | Checks whether the current character matches '`' so the lexer can choose that token branch. |
| 2858 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2859 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2860 | `                # AUTO: Sets `ident_str`.` | Comment/guideline: AUTO: Sets `ident_str`. |
| 2861 | `                ident_str = self.current_char` | Starts the lexeme text with the current character. |
| 2862 | `                # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2863 | `                self.advance()` | Moves the lexer to the next character in the source code. |
| 2864 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2865 | `                if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):` | Conditional check that decides which lexer path or validation rule runs next. |
| 2866 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2867 | `                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2868 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2869 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2870 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2871 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2872 | `                # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2873 | `                tokens.append(Token(TT_CONCAT, ident_str, line, pos.col))` | Creates and appends a TT_CONCAT token to the token list. |
| 2874 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2875 | `                continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2876 | `` | Blank separator line used to visually separate code blocks. |
| 2877 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2878 | `            else:` | Fallback path when the previous if/elif condition did not match. |
| 2879 | `                # AUTO: Sets `pos`.` | Comment/guideline: AUTO: Sets `pos`. |
| 2880 | `                pos = self.pos.copy()` | Saves the starting position of the token being built. |
| 2881 | `                # AUTO: Sets `char`.` | Comment/guideline: AUTO: Sets `char`. |
| 2882 | `                char = self.current_char` | Assigns a value to a variable or object attribute used by the lexer. |
| 2883 | `                ` | Blank separator line used to visually separate code blocks. |
| 2884 | `                # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2885 | `                if char == '_':` | Conditional check that decides which lexer path or validation rule runs next. |
| 2886 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2887 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2888 | `                    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2889 | `                    if self.current_char is not None and self.current_char in ALPHA:` | Checks if the current character starts a word/reserved word/identifier. |
| 2890 | `                        # AUTO: Sets `temp_str`.` | Comment/guideline: AUTO: Sets `temp_str`. |
| 2891 | `                        temp_str = ''` | Assigns a value to a variable or object attribute used by the lexer. |
| 2892 | `                        # AUTO: Sets `temp_index`.` | Comment/guideline: AUTO: Sets `temp_index`. |
| 2893 | `                        temp_index = self.pos.index` | Assigns a value to a variable or object attribute used by the lexer. |
| 2894 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2895 | `                        while temp_index < len(self.source_code) and self.source_code[temp_index] in ALPHANUM:` | Loop that repeats until its condition becomes false. |
| 2896 | `                            # AUTO: Adds into `temp_str`.` | Comment/guideline: AUTO: Adds into `temp_str`. |
| 2897 | `                            temp_str += self.source_code[temp_index]` | Updates an existing value by adding or appending something to it. |
| 2898 | `                            # AUTO: Adds into `temp_index`.` | Comment/guideline: AUTO: Adds into `temp_index`. |
| 2899 | `                            temp_index += 1` | Updates an existing value by adding or appending something to it. |
| 2900 | `                        ` | Blank separator line used to visually separate code blocks. |
| 2901 | `                        # AUTO: Sets `reserved_words`.` | Comment/guideline: AUTO: Sets `reserved_words`. |
| 2902 | `                        reserved_words = {'water', 'plant', 'seed', 'leaf', 'branch', 'tree', 'spring', 'wither', 'bud', ` | Assigns a value to a variable or object attribute used by the lexer. |
| 2903 | `                                        # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2904 | `                                        'harvest', 'grow', 'cultivate', 'tend', 'empty', 'prune', 'skip', 'reclaim', ` | Executes this Python statement as part of the lexer logic. |
| 2905 | `                                        # AUTO: Executes this statement.` | Comment/guideline: AUTO: Executes this statement. |
| 2906 | `                                        'root', 'pollinate', 'variety', 'fertile', 'soil', 'bundle', 'string', 'vine', 'sunshine', 'frost'}` | Executes this Python statement as part of the lexer logic. |
| 2907 | `                        ` | Blank separator line used to visually separate code blocks. |
| 2908 | `                        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2909 | `                        if temp_str in reserved_words:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2910 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2911 | `                            errors.append(LexicalError(pos, f"Reserved word cannot start with a symbol: '_{temp_str}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2912 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2913 | `                        else:` | Fallback path when the previous if/elif condition did not match. |
| 2914 | `                            # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2915 | `                            errors.append(LexicalError(pos, f"Identifiers cannot start with a symbol: '_...'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2916 | `                        ` | Blank separator line used to visually separate code blocks. |
| 2917 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline: AUTO: Repeats while this condition is true. |
| 2918 | `                        while self.current_char is not None and self.current_char in ALPHANUM:` | Loop that keeps consuming characters while the current character satisfies the condition. |
| 2919 | `                            # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2920 | `                            self.advance()` | Moves the lexer to the next character in the source code. |
| 2921 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2922 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2923 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2924 | `                    else:` | Fallback path when the previous if/elif condition did not match. |
| 2925 | `                        # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2926 | `                        errors.append(LexicalError(pos, f"Illegal Character '{char}'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2927 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2928 | `                        continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2929 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2930 | `                else:` | Fallback path when the previous if/elif condition did not match. |
| 2931 | `                    # AUTO: Calls `self.advance`.` | Comment/guideline: AUTO: Calls `self.advance`. |
| 2932 | `                    self.advance()` | Moves the lexer to the next character in the source code. |
| 2933 | `                    # AUTO: Appends a value to a list.` | Comment/guideline: AUTO: Appends a value to a list. |
| 2934 | `                    errors.append(LexicalError(pos, f"Illegal Character '" + char + "'"))` | Creates and stores a lexical error message for an invalid character, delimiter, or malformed token. |
| 2935 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline: AUTO: Skips to the next loop iteration. |
| 2936 | `                    continue` | Skips the rest of the current loop pass and returns to the main scanner loop. |
| 2937 | `                ` | Blank separator line used to visually separate code blocks. |
| 2938 | `        # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2939 | `        if self.current_char is None:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2940 | `            # LINE: Add EOF so the parser knows the token stream is finished.` | Comment/guideline: LINE: Add EOF so the parser knows the token stream is finished. |
| 2941 | `            tokens.append(Token(TT_EOF, "", line, pos.col))` | Creates and appends a TT_EOF token to the token list. |
| 2942 | `        ` | Blank separator line used to visually separate code blocks. |
| 2943 | `        # LINE: Return both successful tokens and raw lexical errors.` | Comment/guideline: LINE: Return both successful tokens and raw lexical errors. |
| 2944 | `        return tokens, errors` | Returns the raw token list and LexicalError objects from make_tokens(). |
| 2945 | `` | Blank separator line used to visually separate code blocks. |
| 2946 | `` | Blank separator line used to visually separate code blocks. |
| 2947 | `# AUTO: Defines function `run`.` | Comment/guideline: AUTO: Defines function `run`. |
| 2948 | `def run(source_code):` | Defines the run function/method. |
| 2949 | `    # GUIDE: Legacy wrapper used by older callers.` | Comment/guideline: GUIDE: Legacy wrapper used by older callers. |
| 2950 | `    # LINE: Create a lexer object for this source text.` | Comment/guideline: LINE: Create a lexer object for this source text. |
| 2951 | `    lexer = Lexer(source_code)` | Assigns a value to a variable or object attribute used by the lexer. |
| 2952 | `    # LINE: Scan the full source into tokens/errors.` | Comment/guideline: LINE: Scan the full source into tokens/errors. |
| 2953 | `    tokens, error = lexer.make_tokens()` | Assigns a value to a variable or object attribute used by the lexer. |
| 2954 | `    # LINE: Return the scanner result to the caller.` | Comment/guideline: LINE: Return the scanner result to the caller. |
| 2955 | `    return tokens, error` | Returns the computed value/result to the caller. |
| 2956 | `` | Blank separator line used to visually separate code blocks. |
| 2957 | `# AUTO: Defines function `lex`.` | Comment/guideline: AUTO: Defines function `lex`. |
| 2958 | `def lex(source_code):` | Defines the lex function/method. |
| 2959 | `    # GUIDE: Public lexer API used by server.py before parsing or execution.` | Comment/guideline: GUIDE: Public lexer API used by server.py before parsing or execution. |
| 2960 | `    # LINE: Server calls this function with the editor source code.` | Comment/guideline: LINE: Server calls this function with the editor source code. |
| 2961 | `    lexer = Lexer(source_code)` | Assigns a value to a variable or object attribute used by the lexer. |
| 2962 | `    # LINE: make_tokens performs the actual character-by-character scan.` | Comment/guideline: LINE: make_tokens performs the actual character-by-character scan. |
| 2963 | `    tokens, errors = lexer.make_tokens()` | Assigns a value to a variable or object attribute used by the lexer. |
| 2964 | `` | Blank separator line used to visually separate code blocks. |
| 2965 | `    # Report lexical errors one at a time — only surface the first.` | Comment/guideline: Report lexical errors one at a time — only surface the first. |
| 2966 | `    # The user fixes it, re-runs, and sees the next one (if any).` | Comment/guideline: The user fixes it, re-runs, and sees the next one (if any). |
| 2967 | `    # LINE: Convert LexicalError objects into frontend-ready strings.` | Comment/guideline: LINE: Convert LexicalError objects into frontend-ready strings. |
| 2968 | `    str_errors = []` | Creates the list that will store lexical errors. |
| 2969 | `    # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2970 | `    if errors:` | Conditional check that decides which lexer path or validation rule runs next. |
| 2971 | `        # LINE: Only send the first lexical error to keep output focused.` | Comment/guideline: LINE: Only send the first lexical error to keep output focused. |
| 2972 | `        e = errors[0]` | Assigns a value to a variable or object attribute used by the lexer. |
| 2973 | `        # AUTO: Starts protected code that can catch errors.` | Comment/guideline: AUTO: Starts protected code that can catch errors. |
| 2974 | `        try:` | Starts a protected block where errors can be caught. |
| 2975 | `            # AUTO: Checks this condition.` | Comment/guideline: AUTO: Checks this condition. |
| 2976 | `            if hasattr(e, 'as_string') and callable(getattr(e, 'as_string')):` | Conditional check that decides which lexer path or validation rule runs next. |
| 2977 | `                # LINE: Use the custom formatted message if the error supports it.` | Comment/guideline: LINE: Use the custom formatted message if the error supports it. |
| 2978 | `                str_errors.append(e.as_string())` | Executes this Python statement as part of the lexer logic. |
| 2979 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline: AUTO: Runs when previous condition did not pass. |
| 2980 | `            else:` | Fallback path when the previous if/elif condition did not match. |
| 2981 | `                # LINE: Otherwise use the normal Python string version.` | Comment/guideline: LINE: Otherwise use the normal Python string version. |
| 2982 | `                str_errors.append(str(e))` | Executes this Python statement as part of the lexer logic. |
| 2983 | `        # AUTO: Handles the matching error case.` | Comment/guideline: AUTO: Handles the matching error case. |
| 2984 | `        except Exception:` | Handles an error raised inside the matching try block. |
| 2985 | `            # LINE: Fallback if error formatting itself fails.` | Comment/guideline: LINE: Fallback if error formatting itself fails. |
| 2986 | `            str_errors.append(str(e))` | Executes this Python statement as part of the lexer logic. |
| 2987 | `    # LINE: Return parser-ready tokens plus frontend-ready lexical error strings.` | Comment/guideline: LINE: Return parser-ready tokens plus frontend-ready lexical error strings. |
| 2988 | `    return tokens, str_errors` | Returns parser-ready tokens and frontend-ready lexical error strings. |

## Example Program

```gal
pollinate seed timesThree(seed n) {
    reclaim n * 3;
}
	
root() {
    seed value = 0;
	seed i;
    cultivate  (i = 1; i <= 4; i++) {
        value = timesThree(i);
        spring (value % 2 == 0) {
            plant("Even product:",value);
        } wither {
            plant("Odd  product:",value);
        }
    }

    reclaim;
}
```

## Sample Lexer Simulation
### Entry and setup
- lex(source_code) creates Lexer(source_code), then make_tokens() scans the whole source one character at a time.
- self.current_char always holds the one character currently being processed. self.advance() moves to the next character.
- tokens stores successful Token objects. errors stores LexicalError objects.

### Line 1: pollinate seed timesThree(seed n) {
- p starts the reserved-word path and matches pollinate, then appends TT_RW_POLLINATE.
- seed is matched as a data-type reserved word.
- timesThree is not a reserved word, so the reserved-word path falls back to the identifier collector and appends TT_IDENTIFIER.
- (, ), and { are handled by their own symbol branches. The space and tab characters are skipped as whitespace.

### Line 2: reclaim n * 3;
- reclaim is recognized as a reserved word and appended as TT_RW_RECLAIM.
- n becomes an identifier token.
- * enters the asterisk branch. The lexer checks if the next character is another * or =. Here it is whitespace, so it appends TT_MUL.
- 3 enters the number branch and becomes TT_INTEGERLIT. The following semicolon is only checked as a delimiter, then tokenized on the next loop pass.

### Root declarations
- root is recognized as the main-function reserved word.
- seed value = 0; becomes seed, id(value), =, intlit(0), semicolon.
- seed i; becomes seed, id(i), semicolon. The tab before seed is skipped.

### Cultivate loop line
- cultivate becomes TT_RW_CULTIVATE.
- i = 1 becomes id(i), =, intlit(1).
- i <= 4 becomes id(i), <=, intlit(4).
- i++ becomes id(i), ++. The lexer checks +, sees another +, and emits increment.

### Loop body and conditional
- value = timesThree(i); is tokenized as id(value), =, id(timesThree), (, id(i), ), semicolon. The lexer does not know it is a function call yet.
- spring (value % 2 == 0) creates spring, (, id(value), %, intlit(2), ==, intlit(0), ), {.
- plant("Even product:",value); creates plant, (, one stringlit token, comma, id(value), ), semicolon.
- } wither { creates }, wither, {. Spaces are skipped.
- plant("Odd  product:",value); keeps the two spaces inside the string literal because they are part of the quoted text.

### End of file
- Each closing brace is tokenized as TT_BLOCK_END.
- reclaim; in root becomes reclaim and semicolon.
- When current_char becomes None, the lexer appends EOF so the parser knows the token stream is finished.

## Actual Token Table

Lexical errors: `[]`

| No. | Line | Col | Token Type | Value |
|---:|---:|---:|---|---|
| 1 | 1 | 0 | `pollinate` | `pollinate` |
| 2 | 1 | 10 | `seed` | `seed` |
| 3 | 1 | 15 | `id` | `timesThree` |
| 4 | 1 | 25 | `(` | `(` |
| 5 | 1 | 26 | `seed` | `seed` |
| 6 | 1 | 31 | `id` | `n` |
| 7 | 1 | 32 | `)` | `)` |
| 8 | 1 | 34 | `{` | `{` |
| 9 | 1 | 35 | `\n` | `\n` |
| 10 | 2 | 4 | `reclaim` | `reclaim` |
| 11 | 2 | 12 | `id` | `n` |
| 12 | 2 | 14 | `*` | `*` |
| 13 | 2 | 16 | `intlit` | `3` |
| 14 | 2 | 17 | `;` | `;` |
| 15 | 2 | 18 | `\n` | `\n` |
| 16 | 3 | 0 | `}` | `}` |
| 17 | 3 | 1 | `\n` | `\n` |
| 18 | 5 | 0 | `root` | `root` |
| 19 | 5 | 4 | `(` | `(` |
| 20 | 5 | 5 | `)` | `)` |
| 21 | 5 | 7 | `{` | `{` |
| 22 | 5 | 8 | `\n` | `\n` |
| 23 | 6 | 4 | `seed` | `seed` |
| 24 | 6 | 9 | `id` | `value` |
| 25 | 6 | 15 | `=` | `=` |
| 26 | 6 | 17 | `intlit` | `0` |
| 27 | 6 | 18 | `;` | `;` |
| 28 | 6 | 19 | `\n` | `\n` |
| 29 | 7 | 1 | `seed` | `seed` |
| 30 | 7 | 6 | `id` | `i` |
| 31 | 7 | 7 | `;` | `;` |
| 32 | 7 | 8 | `\n` | `\n` |
| 33 | 8 | 4 | `cultivate` | `cultivate` |
| 34 | 8 | 15 | `(` | `(` |
| 35 | 8 | 16 | `id` | `i` |
| 36 | 8 | 18 | `=` | `=` |
| 37 | 8 | 20 | `intlit` | `1` |
| 38 | 8 | 21 | `;` | `;` |
| 39 | 8 | 23 | `id` | `i` |
| 40 | 8 | 25 | `<=` | `<=` |
| 41 | 8 | 28 | `intlit` | `4` |
| 42 | 8 | 29 | `;` | `;` |
| 43 | 8 | 31 | `id` | `i` |
| 44 | 8 | 32 | `++` | `++` |
| 45 | 8 | 34 | `)` | `)` |
| 46 | 8 | 36 | `{` | `{` |
| 47 | 8 | 37 | `\n` | `\n` |
| 48 | 9 | 8 | `id` | `value` |
| 49 | 9 | 14 | `=` | `=` |
| 50 | 9 | 16 | `id` | `timesThree` |
| 51 | 9 | 26 | `(` | `(` |
| 52 | 9 | 27 | `id` | `i` |
| 53 | 9 | 28 | `)` | `)` |
| 54 | 9 | 29 | `;` | `;` |
| 55 | 9 | 30 | `\n` | `\n` |
| 56 | 10 | 8 | `spring` | `spring` |
| 57 | 10 | 15 | `(` | `(` |
| 58 | 10 | 16 | `id` | `value` |
| 59 | 10 | 22 | `%` | `%` |
| 60 | 10 | 24 | `intlit` | `2` |
| 61 | 10 | 26 | `==` | `==` |
| 62 | 10 | 29 | `intlit` | `0` |
| 63 | 10 | 30 | `)` | `)` |
| 64 | 10 | 32 | `{` | `{` |
| 65 | 10 | 33 | `\n` | `\n` |
| 66 | 11 | 12 | `plant` | `plant` |
| 67 | 11 | 17 | `(` | `(` |
| 68 | 11 | 18 | `stringlit` | `"Even product:"` |
| 69 | 11 | 33 | `,` | `,` |
| 70 | 11 | 34 | `id` | `value` |
| 71 | 11 | 39 | `)` | `)` |
| 72 | 11 | 40 | `;` | `;` |
| 73 | 11 | 41 | `\n` | `\n` |
| 74 | 12 | 8 | `}` | `}` |
| 75 | 12 | 10 | `wither` | `wither` |
| 76 | 12 | 17 | `{` | `{` |
| 77 | 12 | 18 | `\n` | `\n` |
| 78 | 13 | 12 | `plant` | `plant` |
| 79 | 13 | 17 | `(` | `(` |
| 80 | 13 | 18 | `stringlit` | `"Odd  product:"` |
| 81 | 13 | 33 | `,` | `,` |
| 82 | 13 | 34 | `id` | `value` |
| 83 | 13 | 39 | `)` | `)` |
| 84 | 13 | 40 | `;` | `;` |
| 85 | 13 | 41 | `\n` | `\n` |
| 86 | 14 | 8 | `}` | `}` |
| 87 | 14 | 9 | `\n` | `\n` |
| 88 | 15 | 4 | `}` | `}` |
| 89 | 15 | 5 | `\n` | `\n` |
| 90 | 17 | 4 | `reclaim` | `reclaim` |
| 91 | 17 | 11 | `;` | `;` |
| 92 | 17 | 12 | `\n` | `\n` |
| 93 | 18 | 0 | `}` | `}` |
| 94 | 18 | 1 | `\n` | `\n` |
| 95 | 19 | 1 | `EOF` | `` |

## Short Defense Explanation
Sa lexer, unang ginagawa ng system is kunin yung buong source code. Pero hindi niya agad iniintindi yung buong program. Character by character siya gumagalaw gamit `self.current_char` and `self.advance()`. Kapag may nabuo siyang reserved word, identifier, literal, operator, or symbol, nilalagay niya yun sa `tokens`. Kapag mali naman yung kasunod na delimiter or invalid yung character, nilalagay niya sa `errors`. Pag tapos na yung source code, nagdadagdag siya ng `EOF` token para alam ng parser na tapos na ang input.