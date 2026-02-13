from Backend.lexer import lex
from Backend.Gal_Parser import LL1Parser
from Backend.cfg import cfg, compute_first, compute_follow, compute_predict
import sys
import io

code = '''root() {
 seed x = (5 +) ;
  reclaim;
}'''

tokens, lex_errors = lex(code)

# Suppress grammar output
old_stdout = sys.stdout
sys.stdout = io.StringIO()

first_sets = compute_first(cfg)
follow_sets = compute_follow(cfg, first_sets)
predict_sets = compute_predict(cfg, first_sets, follow_sets)
parser = LL1Parser(cfg, predict_sets, first_sets, skip_token_types={'\n', 'nl'})
parse_tree, parse_errors = parser.parse(tokens)

sys.stdout = old_stdout

print('=== RESULT ===')
print(f'Lexical errors: {len(lex_errors)}')
print(f'Syntax errors: {len(parse_errors)}')
if lex_errors:
    print('\nLexical Error:')
    print(f'  {lex_errors[0]}')
if parse_errors:
    print('\nSyntax Error:')
    print(f'  {parse_errors[0]}')
