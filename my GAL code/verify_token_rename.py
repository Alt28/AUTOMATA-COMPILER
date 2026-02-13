import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from lexer import lex

# Test that token type is now 'stringlit'
code = 'root(){ vine msg = "Hello"; reclaim; }'

print("="*60)
print("VERIFYING TOKEN TYPE CHANGE: strlit -> stringlit")
print("="*60)
print(f"\nCode: {code}\n")

tokens, errors = lex(code)

print("Token types found:")
for t in tokens:
    if 'string' in t.type.lower() or t.value == '"Hello"':
        print(f"  ✓ {t.type:15} = '{t.value}'")

# Find the string token
string_token = None
for t in tokens:
    if t.value == '"Hello"':
        string_token = t
        break

print("\n" + "="*60)
if string_token and string_token.type == 'stringlit':
    print("✓ SUCCESS: Token type is now 'stringlit'")
    print(f"  Old: 'strlit'")
    print(f"  New: 'stringlit' ✓")
else:
    print("✗ FAILED: Token type is not 'stringlit'")
print("="*60)
