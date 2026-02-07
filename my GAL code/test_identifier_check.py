from Backend.lexer import Lexer

# Test with a 32 character identifier
test_code = """root() {
    tree abcdefghijklmnopqrstuvwxyz123456 = 5.0;
}"""

print("Testing identifier with 32 characters...")
print("Input code:")
print(test_code)
print("\n" + "="*60 + "\n")

lexer = Lexer(test_code)
tokens, errors = lexer.make_tokens()

print("TOKENS (identifiers only):")
for token in tokens:
    if token.type == 'id':
        print(f"  {token.type:15} | {token.value:20} | Length: {len(token.value)}")

print("\nERRORS:")
if errors:
    for error in errors:
        print(f"  Line {error.pos.ln}, Col {error.pos.col}: {error.details}")
else:
    print("  No errors found")

print("\n" + "="*60)
print("\nIdentifier breakdown:")
print("  Full identifier: 'abcdefghijklmnopqrstuvwxyz123456' (32 chars)")
print("  First 16 chars:  'abcdefghijklmnop' (error)")
print("  Second 16 chars: 'qrstuvwxyz123456' (error)")
print("  Remaining:       '' (0 chars - no token)")
print("  BUT if there are remaining chars ≤15, they become a valid identifier token")
