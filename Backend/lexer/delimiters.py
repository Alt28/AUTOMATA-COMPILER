ZERO = '0'
DIGIT = '123456789'
ZERODIGIT = ZERO + DIGIT

LOW_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
UPPER_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPHA = LOW_ALPHA + UPPER_ALPHA
ALPHANUM = ALPHA + ZERODIGIT + '_'

WHITESPACE = ' \t\n'
EOF = None

statement_end_delim = set(ALPHA + WHITESPACE + '}') | {EOF}
open_paren_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '"' + "'" + '~' + '!' + '(' + ')')
close_paren_delim = set(WHITESPACE) | {';', '{', ')', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ']'}
open_bracket_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '~' + '!' + '(' + '"' + "'")
close_bracket_delim = set(WHITESPACE) | {';', ',', ')', ']', '[', '.', '=', '+', '-', '*', '/', '%', '>', '<', '!', '&', '|'}
block_start_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '}/{"\'~!(')
block_end_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '};,)]')
case_colon_delim = set(ALPHA + WHITESPACE + '}/')
after_comma_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '"' + "'" + '~' + '!' + '(' + '{')
space_delim = {' ', '\t', '\n'}
period_delim = {'.'}
underscore_delim = {'_'}
open_brack_delim = {'['}
close_brack_delim = {']'}
comma_delim = {','}
delim1 = {'}'}
delim2 = {':'}
delim3 = {'{'}
delim4 = {':', '('}
delim5 = {'('}
delim6 = {';', ',', '=', '>', '<', '!', '}', ')', '('}
delim7 = {'('}
delim8 = {';'}
delim9 = set(ALPHA + '(' + ',' + ';' + ')')
delim10 = {';', ')'}
delim11 = set([LOW_ALPHA, ZERODIGIT, ']', '~'])
delim12 = set(ALPHA + ZERODIGIT + ']' + '~')
delim13 = {';', ')', '['}
delim14 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')
delim15 = {'\n', ';', '}', ','}
delim16 = set(ALPHANUM + ')' + '"' + '!' + '(' + '[' + '\'')
delim17 = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}
delim18 = {';', '{', ')', '&', '|', '+', '-', '*', '/', '%'}
delim19 = {';', ',', '}', ')', '=', '>', '<', '!'}
delim20 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')
delim21 = set(DIGIT)
delim22 = {',', ';', '(', ')', '{', '[', ']'}
delim23 = {';', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}
delim24 = set(ZERODIGIT + ALPHA + '~(' + ' \t\n')
delim25 = set(ALPHANUM + ';) \t\n')
delim26 = set(ZERODIGIT + ALPHA + '~(' + '"\'' + ' \t\n')
idf_delim = {' ', ',', ';', '(', ')', '{', '}', '[', ']', ':', '+', '-', '*', '/', '%',
             '>', '<', '=', '\t', '\n', '.', '"', "'"}
whlnum_delim = {';', ' ', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<',
                '!', '&', '|', '\t', '\n'}
decim_delim = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ' ',
               '\t', '\n', ')', ']'}
comment_delim = set(ALPHANUM + ';+-*/%}{()' + '\n')
