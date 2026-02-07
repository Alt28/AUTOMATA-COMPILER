from Backend.lexer import Lexer

# Test with various identifier lengths
test_cases = [
    ("16 chars", "abcdefghijklmnop"),
    ("17 chars", "abcdefghijklmnopq"),
    ("31 chars", "abcdefghijklmnopqrstuvwxyz12345"),
    ("32 chars", "abcdefghijklmnopqrstuvwxyz123456"),
    ("33 chars", "abcdefghijklmnopqrstuvwxyz1234567"),
]

for label, ident in test_cases:
    test_code = f"root() {{\n    tree {ident} = 5.0;\n}}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {label} - '{ident}' (length {len(ident)})")
    print('='*60)
    
    lexer = Lexer(test_code)
    tokens, errors = lexer.make_tokens()
    
    print("TOKENS (identifier only):")
    for token in tokens:
        if token.type == 'id':
            print(f"  Value: '{token.value}' (length {len(token.value)})")
    
    print("\nERRORS:")
    if errors:
        for error in errors:
            if "Identifier exceeds" in error.details:
                print(f"  {error.details}")
    else:
        print("  No errors")
    
    # Calculate expected behavior
    full_length = len(ident)
    num_16_chunks = full_length // 16
    remaining = full_length % 16
    print(f"\nExpected: {num_16_chunks} error(s), ", end="")
    if remaining > 0:
        print(f"token with {remaining} char(s)")
    else:
        print("no token (0 remaining)")
