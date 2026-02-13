import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from lexer import lex
from Gal_Parser import LL1Parser
from cfg import cfg, predict_sets, first_sets

# Test without newlines
code = 'root(){ vine string = "333"; reclaim; }'

print("Testing code (no newlines):")
print(code)
print("\n" + "="*60)

tokens, errors = lex(code)

if errors:
    print(f"Lexer errors: {errors}\n")
else:
    print("Tokens:")
    for t in tokens:
        if t.type != '\n' and t.type != '':  # Skip newlines
            print(f"  {t.type:15} = '{t.value}'")
    print()

parser = LL1Parser(cfg, predict_sets, first_sets)
success, parse_errors = parser.parse(tokens)

print("="*60)
if success:
    print("✓ Parser: VALID - No syntax errors")
    print("\nThe variable name 'string' is ALLOWED because:")
    print("  - 'string' is NOT a reserved keyword in GAL")
    print("  - The string data type in GAL is 'vine', not 'string'")
    print("  - 'string' is treated as a regular identifier (variable name)")
else:
    print("✗ Parser: INVALID - Syntax errors found:")
    for error in parse_errors:
        print(f"  {error}")
