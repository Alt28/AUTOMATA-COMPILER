import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from lexer import lex
from Gal_Parser import LL1Parser
from cfg import cfg, predict_sets, first_sets

code = '''root(){
	vine string = "333";
	
	reclaim;
}'''

print("Testing code:")
print(code)
print("\n" + "="*60)

tokens, errors = lex(code)

if errors:
    print(f"Lexer errors: {errors}\n")
else:
    print("Tokens:")
    for t in tokens:
        print(f"  {t.type:15} = '{t.value}'")
    print()

parser = LL1Parser(cfg, predict_sets, first_sets)
success, parse_errors = parser.parse(tokens)

print("="*60)
if success:
    print("✓ Parser: VALID - No syntax errors")
else:
    print("✗ Parser: INVALID - Syntax errors found:")
    for error in parse_errors:
        print(f"  {error}")
