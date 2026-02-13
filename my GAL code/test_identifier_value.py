import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from lexer import lex
from Gal_Parser import LL1Parser
from cfg import cfg, predict_sets, first_sets

code = "root(){ seed num = fff; reclaim; }"

print("="*60)
print("USER'S TEST CASE")
print("="*60)
print(f"Code: {code}\n")
print("-" * 60)

tokens, errors = lex(code)

if errors:
    print(f"Lexer errors: {errors}\n")

print("Tokens:")
for t in tokens:
    if t.type not in ['\n', '']:
        print(f"  {t.type:15} = '{t.value}'")
print()

parser = LL1Parser(cfg, predict_sets, first_sets)
success, parse_errors = parser.parse(tokens)

print("="*60)
if success:
    print("✓ PASS - Syntax valid")
    print("\nISSUE: 'fff' is treated as an identifier (variable reference)")
    print("       not as an integer literal")
else:
    print("✗ FAIL - Syntax error:")
    for error in parse_errors:
        print(f"  {error}")
print("="*60)
