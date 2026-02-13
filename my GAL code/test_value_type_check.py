"""
Test value type checking in parser
Tests that the parser now validates value types match variable declarations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from lexer import lex
from Gal_Parser import LL1Parser
from cfg import cfg, predict_sets, first_sets

def test_parser(code, test_name):
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"{'='*60}")
    print(f"Code: {code}")
    print("-" * 60)
    
    tokens, errors = lex(code)
    
    if errors:
        print(f"Lexer errors: {errors}\n")
        return False, []
    
    print(f"Tokens: {[(t.type, t.value) for t in tokens]}\n")
    
    parser = LL1Parser(cfg, predict_sets, first_sets)
    success, errors = parser.parse(tokens)
    
    if success:
        print("✓ PASS - Syntax valid")
    else:
        print("✗ FAIL - Syntax error:")
        for error in errors:
            print(f"  {error}")
    
    return success, errors

# Test cases
print("\n" + "="*60)
print("PARSER VALUE TYPE CHECKING TESTS")
print("="*60)

# Test 1: Valid - vine with string
test_parser('root(){ vine hh = "6666"; reclaim; }', 
            "Valid: vine = string")

# Test 2: Invalid - vine with integer
test_parser('root(){ vine hh = 6666; reclaim; }', 
            "Invalid: vine = integer (should fail)")

# Test 3: Valid - seed with integer
test_parser('root(){ seed count = 42; reclaim; }', 
            "Valid: seed = integer")

# Test 4: Invalid - seed with string
test_parser('root(){ seed count = "42"; reclaim; }', 
            "Invalid: seed = string (should fail)")

# Test 5: Valid - tree with float
test_parser('root(){ tree pi = 3.14; reclaim; }', 
            "Valid: tree = float")

# Test 6: Valid - tree with integer (allowed)
test_parser('root(){ tree pi = 3; reclaim; }', 
            "Valid: tree = integer (allowed)")

# Test 7: Invalid - tree with string
test_parser('root(){ tree pi = "3.14"; reclaim; }', 
            "Invalid: tree = string (should fail)")

# Test 8: Valid - leaf with char
test_parser("root(){ leaf ch = 'a'; reclaim; }", 
            "Valid: leaf = char")

# Test 9: Invalid - leaf with string
test_parser('root(){ leaf ch = "a"; reclaim; }', 
            "Invalid: leaf = string (should fail)")

# Test 10: Valid - branch with boolean
test_parser('root(){ branch flag = sunshine; reclaim; }', 
            "Valid: branch = sunshine (true)")

# Test 11: Valid - branch with frost
test_parser('root(){ branch flag = frost; reclaim; }', 
            "Valid: branch = frost (false)")

# Test 12: Invalid - branch with integer
test_parser('root(){ branch flag = 1; reclaim; }', 
            "Invalid: branch = integer (should fail)")

# Test 13: Your original example
test_parser('root(){ vine hh = "6666"; reclaim; }', 
            "Your example: vine with string value")

print("\n" + "="*60)
print("TESTS COMPLETED")
print("="*60)
