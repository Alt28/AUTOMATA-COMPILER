from Backend.lexer import lex
from Backend.Gal_Parser import LL1Parser
from Backend.cfg import cfg, compute_first, compute_follow, compute_predict
import sys

code = '''root() {
 seed x = (5 ++)) ;
  reclaim;
}'''

print('=== TOKENS ===')
tokens, lex_errors = lex(code)
for i, t in enumerate(tokens):
    if t.line == 2:  # Show only line 2 tokens
        print(f'{i:2}: {t.type:15} = "{t.value}" (line {t.line}, col {t.col})')

print('\n=== LEXICAL ANALYSIS ===')
if lex_errors:
    print('❌ Lexical Errors:')
    for err in lex_errors:
        print(f'  {err}')
else:
    print('✓ No lexical errors')

print('\n=== SYNTAX ANALYSIS ===')
# Suppress verbose grammar output
original_stdout = sys.stdout
sys.stdout = open('nul', 'w') if sys.platform == 'win32' else open('/dev/null', 'w')

first_sets = compute_first(cfg)
follow_sets = compute_follow(cfg, first_sets)
predict_sets = compute_predict(cfg, first_sets, follow_sets)

sys.stdout = original_stdout

parser = LL1Parser(cfg, predict_sets, first_sets, skip_token_types={'\n', 'nl'})
parse_tree, parse_errors = parser.parse(tokens)

if parse_errors:
    print('❌ Syntax Error (parser caught it):')
    for err in parse_errors:
        print(f'  {err}')
