
ZERO = '0'
DIGIT = '123456789'
ZERODIGIT = ZERO + DIGIT

LOW_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
UPPER_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPHA = LOW_ALPHA + UPPER_ALPHA
ALPHANUM = ALPHA + ZERODIGIT + '_'

space_delim = {' ', '\t', '\n'}                                                    
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
delim24 = set(ZERODIGIT + ALPHA + '~!(' + "\"'" + ' \t\n')
delim25 = set(ALPHANUM + ';}) \t\n')
delim26 = {'(', '['} | set(ALPHA) | {' ', '\t', '\n'}
idf_delim = {' ', ',', ';', '(', ')', '{', '}', '[', ']', ':', '+', '-', '*', '/', '%',
             '>', '<', '=', '\t', '\n', '.', '"', "'"}
whlnum_delim = {';', ' ', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<',
                '!', '&', '|', '\t', '\n'}
decim_delim = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ' ',
               '\t', '\n', ')', ']'}
comment_delim = set(ALPHANUM + ';+-*/%}{()' + '\n')
