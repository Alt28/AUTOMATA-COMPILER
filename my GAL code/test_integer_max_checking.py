from Backend.lexer import Lexer

# Test integer maximum checking with error recovery
test_code = """root() {
    seed x = 123456789;
    seed y = 12345678901234567890;
    seed z = 123;
}"""

print("Testing integer maximum checking with error recovery...")
print("Input code:")
print(test_code)
print("\n" + "="*60 + "\n")

lexer = Lexer(test_code)
tokens, errors = lexer.make_tokens()

print("TOKENS:")
for token in tokens:
    print(f"  {token.type:15} | {token.value:20} | Line {token.line}, Col {token.col}")

print("\nERRORS:")
if errors:
    for error in errors:
        print(f"  Line {error.pos.ln}, Col {error.pos.col}: {error.details}")
else:
    print("  No errors found")

print("\n" + "="*60)
print("\nExpected behavior:")
print("  - 123456789 (9 digits): Should generate error and tokenize only '9' (the remaining 1 digit)")
print("  - 12345678901234567890 (20 digits): Should generate 2 errors (first 9, second 9) and tokenize '78' (remaining 2 digits)")
print("  - 123 (3 digits): Should tokenize normally with no error")
