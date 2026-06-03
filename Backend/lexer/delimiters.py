"""Character groups used by the scanner to validate token boundaries.

A delimiter set is not a token by itself. It means "after reading this token,
the next character must be one of these characters, otherwise report a lexical
delimiter error."
"""

# LINE: ZERO is separated because some numeric rules treat 0 specially.
ZERO = '0'
# LINE: DIGIT contains non-zero digits.
DIGIT = '123456789'
# LINE: ZERODIGIT means any numeric digit 0-9.
ZERODIGIT = ZERO + DIGIT

# LINE: Lowercase letters accepted by identifiers/reserved words.
LOW_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
# LINE: Uppercase letters accepted by identifiers/reserved words.
UPPER_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# LINE: ALPHA combines all letters.
ALPHA = LOW_ALPHA + UPPER_ALPHA
# LINE: ALPHANUM is what identifiers can continue with.
ALPHANUM = ALPHA + ZERODIGIT + '_'

# LINE: Common whitespace characters.
WHITESPACE = ' \t\n'
# LINE: EOF marker used inside delimiter sets.
EOF = None

# GUIDE: Named delimiter sets describe common token-boundary situations.
# LINE: Characters allowed after a statement-ending context.
statement_end_delim = set(ALPHA + WHITESPACE + '}') | {EOF}
# LINE: Characters allowed after an opening parenthesis.
open_paren_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '"' + "'" + '~' + '!' + '(' + ')')
# LINE: Characters allowed after a closing parenthesis.
close_paren_delim = set(WHITESPACE) | {';', '{', ')', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ']'}
# AUTO: Sets `open_bracket_delim`.
open_bracket_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '~' + '!' + '(' + '"' + "'")
# AUTO: Sets `close_bracket_delim`.
close_bracket_delim = set(WHITESPACE) | {';', ',', ')', ']', '[', '.', '=', '+', '-', '*', '/', '%', '>', '<', '!', '&', '|'}
# AUTO: Sets `block_start_delim`.
block_start_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '}/{"\'~!(')
# AUTO: Sets `block_end_delim`.
block_end_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '};,)]')
# AUTO: Sets `case_colon_delim`.
case_colon_delim = set(ALPHA + WHITESPACE + '}/')
# AUTO: Sets `after_comma_delim`.
after_comma_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '"' + "'" + '~' + '!' + '(' + '{')
# AUTO: Sets `space_delim`.
space_delim = {' ', '\t', '\n'}
# AUTO: Sets `period_delim`.
period_delim = {'.'}
# AUTO: Sets `underscore_delim`.
underscore_delim = {'_'}
# AUTO: Sets `open_brack_delim`.
open_brack_delim = {'['}
# AUTO: Sets `close_brack_delim`.
close_brack_delim = {']'}
# AUTO: Sets `comma_delim`.
comma_delim = {','}

# GUIDE: Numbered delimiter sets are legacy FSM groups used by scanner.py branches.
# LINE: Each delimN is a valid-next-character set, not a token.
delim1 = {'}'}
# AUTO: Sets `delim2`.
delim2 = {':'}
# AUTO: Sets `delim3`.
delim3 = {'{'}
# AUTO: Sets `delim4`.
delim4 = {':', '('}
# AUTO: Sets `delim5`.
delim5 = {'('}
# AUTO: Sets `delim6`.
delim6 = {';', ',', '=', '>', '<', '!', '}', ')', '('}
# AUTO: Sets `delim7`.
delim7 = {'('}
# AUTO: Sets `delim8`.
delim8 = {';'}
# AUTO: Sets `delim9`.
delim9 = set(ALPHA + '(' + ',' + ';' + ')')
# AUTO: Sets `delim10`.
delim10 = {';', ')'}
# AUTO: Sets `delim11`.
delim11 = set(LOW_ALPHA + ZERODIGIT + ']~')
# AUTO: Sets `delim12`.
delim12 = set(ALPHA + ZERODIGIT + ']' + '~')
# AUTO: Sets `delim13`.
delim13 = {';', ')', '['}
# AUTO: Sets `delim14`.
delim14 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')
# AUTO: Sets `delim15`.
delim15 = {'\n', ';', '}', ','}
# AUTO: Sets `delim16`.
delim16 = set(ALPHANUM + ')' + '"' + '!' + '(' + '[' + '\'')
# AUTO: Sets `delim17`.
delim17 = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}
# AUTO: Sets `delim18`.
delim18 = {';', '{', ')', '&', '|', '+', '-', '*', '/', '%'}
# AUTO: Sets `delim19`.
delim19 = {';', ',', '}', ')', '=', '>', '<', '!'}
# AUTO: Sets `delim20`.
delim20 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')
# AUTO: Sets `delim21`.
delim21 = set(ALPHA + ZERODIGIT + WHITESPACE + '~!("\'')
# AUTO: Sets `delim22`.
delim22 = {',', ';', '(', ')', '{', '[', ']'}
# AUTO: Sets `delim23`.
delim23 = {';', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', '`'}
# LINE: delim24 is used after binary/assignment operators like +, +=, ==.
delim24 = set(ZERODIGIT + ALPHA + '~!("\'' + WHITESPACE)
# LINE: delim25 is used after ++/-- so postfix/prefix boundaries are accepted.
delim25 = set(ALPHANUM + ';) \t\n')
# AUTO: Sets `delim26`.
delim26 = set(ZERODIGIT + ALPHA + '~(' + '"\'' + ' \t\n')
# LINE: idf_delim tells lexer what can legally appear after an identifier.
idf_delim = {' ', ',', ';', '(', ')', '{', '}', '[', ']', ':', '+', '-', '*', '/', '%',
             # AUTO: Sets `'>', '<', '`.
             '>', '<', '=', '\t', '\n', '.', '"', "'", '&', '|', '`'}
# LINE: whlnum_delim tells lexer what can legally appear after an integer.
whlnum_delim = {';', ' ', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<',
                # AUTO: Executes this statement.
                '!', '&', '|', '\t', '\n'}
# LINE: decim_delim tells lexer what can legally appear after a double literal.
decim_delim = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ' ',
               # AUTO: Executes this statement.
               '\t', '\n', ')', ']'}
# LINE: comment_delim is used around comment scanning boundaries.
comment_delim = set(ALPHANUM + ';+-*/%}{()' + '\n')
