# ============================================================================
# DELIMITER SETS - Character sets used by the lexer's FSM
# ============================================================================
# Each delim* set names the characters that may legally appear AFTER a
# specific token type. The lexer consults these to enforce GAL's strict
# delimiter rules and reject ambiguous trailing characters.
# ============================================================================

# --- CHARACTER CLASSES ---
ZERO = '0'                                          # Zero digit (special case for leading zeros)
DIGIT = '123456789'                                 # Non-zero digits
ZERODIGIT = ZERO + DIGIT                            # All digits (0-9)

LOW_ALPHA = 'abcdefghijklmnopqrstuvwxyz'            # Lowercase letters
UPPER_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'          # Uppercase letters
ALPHA = LOW_ALPHA + UPPER_ALPHA                     # All letters
ALPHANUM = ALPHA + ZERODIGIT + '_'                  # Identifier characters

# --- DELIMITER SETS ---
# Delimiters are characters that can legally appear AFTER certain tokens.
# Different token types have different valid delimiters to ensure proper syntax.
space_delim = {' ', '\t', '\n'}                                                                 # after 'seed', 'tree', 'leaf'
delim2 = {';', ':'}                                                                             # after 'soil' (default case)
delim3 = {'{'}                                                                                  # after 'tend', 'wither'
delim4 = {':', '('}                                                                             # after 'bud', 'cultivate', 'harvest'
delim5 = {'('}                                                                                  # after keywords requiring (
delim6 = {';', ',', '=', '>', '<', '!', '}', ')', '('}                                          # after 'spring', 'plant', 'water'
delim7 = {'('}                                                                                  # after 'root'
delim8 = {';'}                                                                                  # after statements needing ;
delim9 = set(ALPHA + '(' + ',' + ';' + ')')                                                     # function-related contexts
delim10 = {';', ')'}                                                                            # closing statements
delim11 = {'\n'}                                                                                # newline-only
delim12 = set(ALPHA + ZERODIGIT + ']' + '~')                                                    # array/negation contexts
delim13 = {';', ')', '['}                                                                       # mixed statement endings
delim14 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')                                              # before literals/blocks
delim15 = {'\n', ';', '}', ','}                                                                 # multi-context endings
delim16 = set(ALPHANUM + ')' + '"' + '!' + '(' + '[' + '\'')                                    # expression contexts
delim17 = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}                # operator contexts
delim18 = {';', '{', ')', '&', '|', '+', '-', '*', '/', '%'}                                    # logical/arithmetic contexts
delim19 = {';', ',', '}', ')', '=', '>', '<', '!'}                                              # comparison contexts
delim20 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')                                              # before string/char literals
delim21 = set(DIGIT)                                                                            # digit delimiters
delim22 = {',', ';', '(', ')', '{', '[', ']'}                                                   # punctuation contexts
delim23 = {';', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'} # after literals
delim24 = set(ZERODIGIT + ALPHA + '~' + '(')                                                    # unary/function contexts
idf_delim = {' ', ',', ';', '(', ')', '{', '}', '[', ']', ':', '+', '-', '*', '/', '%',
             '>', '<', '=', '\t', '\n', '.', '"', "'"}                                          # after identifiers
whlnum_delim = {';', ' ', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<',
                '!', '&', '|', '\t', '\n'}                                                      # after integers
decim_delim = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ' ',
               '\t', '\n', ')', ']'}                                                            # after floats/doubles
comment_delim = set(ALPHANUM + ';+-*/%}{()' + '\n')                                             # within comments
