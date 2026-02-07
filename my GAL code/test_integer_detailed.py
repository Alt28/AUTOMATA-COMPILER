from Backend.lexer import Lexer

# Test with various integer lengths
test_cases = [
    ("9 digits", "123456789"),
    ("10 digits", "1234567890"),
    ("17 digits", "12345678901234567"),
    ("18 digits", "123456789012345678"),
    ("19 digits", "1234567890123456789"),
]

for label, num_str in test_cases:
    test_code = f"root() {{\n    seed x = {num_str};\n}}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {label} - '{num_str}' (length {len(num_str)})")
    print('='*60)
    
    lexer = Lexer(test_code)
    tokens, errors = lexer.make_tokens()
    
    print("TOKENS (integer only):")
    for token in tokens:
        if token.type == 'intlit':
            print(f"  Value: '{token.value}' (length {len(token.value)})")
    
    print("\nERRORS:")
    if errors:
        for error in errors:
            if "Integer exceeds" in error.details:
                print(f"  {error.details}")
    else:
        print("  No errors")
    
    # Calculate expected behavior
    full_length = len(num_str)
    num_9_chunks = full_length // 9
    remaining = full_length % 9
    print(f"\nExpected: {num_9_chunks} error(s), ", end="")
    if remaining > 0:
        print(f"token with {remaining} digit(s)")
    else:
        print("no token (0 remaining)")
