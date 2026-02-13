import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from lexer import lex
from Gal_Parser import LL1Parser
from cfg import cfg, predict_sets, first_sets

def test_code(code, description):
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"{'='*60}")
    print(f"Code: {code}")
    print("-" * 60)
    
    tokens, errors = lex(code)
    
    if errors:
        print(f"Lexer errors: {errors}\n")
        return
    
    print(f"Tokens: {[(t.type, t.value) for t in tokens if t.type not in ['\\n', '']]}\n")
    
    parser = LL1Parser(cfg, predict_sets, first_sets)
    success, parse_errors = parser.parse(tokens)
    
    if success:
        print("✓ PASS - Syntax valid")
    else:
        print("✗ FAIL - Syntax error:")
        for error in parse_errors:
            print(f"  {error}")

print("="*60)
print("TESTING: Multi-character in single quotes for leaf (char)")
print("="*60)

# Should FAIL - multi-character string for char type
test_code("root(){ leaf string = 'hhh'; reclaim; }", 
          "Should FAIL: leaf = 'hhh' (multi-character)")

# Should PASS - single character for char type
test_code("root(){ leaf ch = 'h'; reclaim; }", 
          "Should PASS: leaf = 'h' (single character)")

# Should FAIL - empty character literal
test_code("root(){ leaf ch = ''; reclaim; }", 
          "Should FAIL: leaf = '' (empty)")
