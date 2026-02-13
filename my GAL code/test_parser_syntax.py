from Backend.lexer import lex
from Backend.Gal_Parser import LL1Parser
from Backend.cfg import cfg, compute_first, compute_follow, compute_predict
import sys

# Suppress the verbose grammar output
original_stdout = sys.stdout
sys.stdout = open('nul', 'w') if sys.platform == 'win32' else open('/dev/null', 'w')

code = '''root() {
 seed x = 5 + * 2;
  reclaim;
}'''

# Compute grammar sets silently
first_sets = compute_first(cfg)
follow_sets = compute_follow(cfg, first_sets)
predict_sets = compute_predict(cfg, first_sets, follow_sets)

# Restore output
sys.stdout = original_stdout

print('=== Step 1: LEXICAL ANALYSIS ===')
tokens, lex_errors = lex(code)
if lex_errors:
    print('❌ Lexical Errors:')
    for err in lex_errors:
        print(f'  {err}')
else:
    print(f'✓ No lexical errors! Tokenized {len(tokens)} tokens')

print('\n=== Step 2: SYNTAX ANALYSIS ===')
try:
    # Create parser - configure it to skip newline tokens (type '\n')
    parser = LL1Parser(cfg, predict_sets, first_sets, skip_token_types={'\n', 'nl'})
    
    # Parse tokens
    parse_tree, parse_errors = parser.parse(tokens)
    
    if parse_errors:
        print('✓ SYNTAX ERROR detected (as expected):')
        for err in parse_errors:
            print(f'  ❌ {err}')
    else:
        print('✗ No syntax errors detected (unexpected!)')
        
except Exception as e:
    print(f'Parser exception: {e}')
