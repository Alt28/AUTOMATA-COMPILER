from Backend.lexer import lex
from Backend.Gal_Parser import LL1Parser
from Backend.cfg import cfg, compute_first, compute_follow, compute_predict
import sys
import io

# Test case: space in compound assignment operator
code = """root() {
 a + = 2;

  reclaim;
}"""

print("Testing code:")
print(code)
print("\n" + "="*80 + "\n")

# Suppress grammar output
old_stdout = sys.stdout
sys.stdout = io.StringIO()

# Tokenize
tokens, lex_errors = lex(code)

first_sets = compute_first(cfg)
follow_sets = compute_follow(cfg, first_sets)
predict_sets = compute_predict(cfg, first_sets, follow_sets)

parser = LL1Parser(cfg, predict_sets, first_sets, skip_token_types={'\n', 'nl'})
success, syntax_errors = parser.parse(tokens)

# Restore output
sys.stdout = old_stdout

print(f"Lexical Analysis: {len(lex_errors)} errors")
for err in lex_errors:
    print(f"  {err}")

print(f"\nSyntax Analysis: {'SUCCESS' if success else 'FAILED'}")
if syntax_errors:
    print(f"Syntax errors: {len(syntax_errors)}")
    for err in syntax_errors:
        print(f"  {err}")
else:
    print("  No syntax errors")
