import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

# Suppress FIRST/FOLLOW/PREDICT output
import io
from contextlib import redirect_stdout

f = io.StringIO()
with redirect_stdout(f):
    from lexer import lex
    from Gal_Parser import LL1Parser
    from cfg import cfg, compute_first, compute_follow, compute_predict

print("Testing prefix notation error detection...")
print("=" * 60)

code = """branch r = (> a b);"""

print(f"Code:\n{code}\n")
print("Tokenizing and parsing...")

# Tokenize
tokens, lex_errors = lex(code)
print(f"Lexer errors: {lex_errors}")
print(f"Tokens: {[(t.type, t.value) for t in tokens]}\n")

# Build parsing structures
first_sets = compute_first(cfg)
follow_sets = compute_follow(cfg, first_sets)
predict_sets = compute_predict(cfg, first_sets, follow_sets)

# Parse
parser = LL1Parser(cfg, predict_sets, first_sets, skip_token_types={'\n', 'nl'})
success, syntax_errors = parser.parse(tokens)

if syntax_errors:
    print("Parser errors:")
    for error in syntax_errors:
        print(f"  {error}")
else:
    print("No parser errors")
