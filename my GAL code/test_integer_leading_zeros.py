from Backend.lexer import Lexer

# Test with leading zeros
test_cases = [
    ("17 digits with leading zeros", "00012345678901234"),
    ("10 digits all zeros except last", "0000000009"),
]

for label, num_str in test_cases:
    test_code = f"root() {{\n    seed x = {num_str};\n}}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {label}")
    print(f"Input: '{num_str}' (length {len(num_str)})")
    print('='*60)
    
    lexer = Lexer(test_code)
    tokens, errors = lexer.make_tokens()
    
    print("TOKENS (integer only):")
    for token in tokens:
        if token.type == 'intlit':
            print(f"  Value: '{token.value}'")
    
    print("\nERRORS:")
    if errors:
        for error in errors:
            if "Integer exceeds" in error.details:
                print(f"  {error.details}")
    else:
        print("  No errors")
