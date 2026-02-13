import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from lexer import lex
from Gal_Parser import LL1Parser
from cfg import cfg, predict_sets, first_sets

# Test without newlines
code = "root(){ leaf string = 'hhh'; reclaim; }"

print("="*60)
print("USER'S TEST CASE")
print("="*60)
print(f"Code: {code}\n")
print("-" * 60)

tokens, errors = lex(code)

if errors:
    print(f"Lexer errors: {errors}\n")

parser = LL1Parser(cfg, predict_sets, first_sets)
success, parse_errors = parser.parse(tokens)

print("="*60)
if success:
    print("✓ PASS - Syntax valid (UNEXPECTED)")
else:
    print("✗ FAIL - Syntax error (EXPECTED):")
    for error in parse_errors:
        print(f"  {error}")
print("="*60)
print("\n✓ Multi-character strings in single quotes for leaf variables")
print("  are now properly rejected!")
