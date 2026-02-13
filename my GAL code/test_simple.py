from Backend.lexer import lex
from Backend.Gal_Parser import LL1Parser
from Backend.cfg import cfg, compute_first, compute_follow, compute_predict
import sys
import io

code = '''root() {
 seed x = (5 ++)) ;
  reclaim;
}'''

# Suppress grammar output entirely
old_stdout = sys.stdout
sys.stdout = io.StringIO()

tokens, lex_errors = lex(code)
first_sets = compute_first(cfg)
follow_sets = compute_follow(cfg, first_sets)
predict_sets = compute_predict(cfg, first_sets, follow_sets)
parser = LL1Parser(cfg, predict_sets, first_sets, skip_token_types={'\n', 'nl'})
parse_tree, parse_errors = parser.parse(tokens)

# Restore output
sys.stdout = old_stdout

print('=== RESULT ===')
print(f'Lexical errors: {len(lex_errors)}')
print(f'Syntax errors: {len(parse_errors)}')
print()
if parse_errors:
    print('Syntax Error:')
    print(f'  {parse_errors[0]}')
