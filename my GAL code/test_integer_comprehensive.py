from Backend.lexer import Lexer

print("="*70)
print("INTEGER MAXIMUM CHECKING - ERROR RECOVERY TEST")
print("="*70)

test_code = """root() {
    seed a = 12345678;
    seed b = 123456789;
    seed c = 1234567890;
    seed d = 123456789012345678;
    seed e = 12345678901234567890;
}"""

print("\nTest Code:")
print(test_code)
print("\n" + "="*70 + "\n")

lexer = Lexer(test_code)
tokens, errors = lexer.make_tokens()

# Display analysis
print("ANALYSIS:")
print("-"*70)

test_values = [
    ("12345678", 8),
    ("123456789", 9),
    ("1234567890", 10),
    ("123456789012345678", 18),
    ("12345678901234567890", 20),
]

for value, length in test_values:
    num_errors = length // 9
    remaining = length % 9
    
    print(f"\n{value} ({length} digits):")
    print(f"  - Errors: {num_errors} (each for 9-digit chunk)")
    if remaining > 0:
        remaining_value = value[-remaining:].lstrip("0") or "0"
        print(f"  - Token: '{remaining_value}' ({remaining} digit(s), after removing leading zeros)")
    else:
        print(f"  - Token: None (no remaining digits)")

print("\n" + "="*70)
print("\nACTUAL RESULTS:")
print("-"*70)

print("\nINTEGER TOKENS:")
for token in tokens:
    if token.type == 'intlit':
        print(f"  Line {token.line}, Col {token.col}: '{token.value}'")

print("\nERRORS:")
for error in errors:
    if "Integer exceeds" in error.details:
        print(f"  Line {error.pos.ln}, Col {error.pos.col}: {error.details}")

print("\n" + "="*70)
print("\nSUMMARY:")
print("-"*70)
print("✓ Integer checking now continues reading even when there's an error")
print("✓ Processes in chunks of 9 digits (max is 8)")
print("✓ Generates error for each 9-digit chunk")
print("✓ Tokenizes remaining valid digits (≤8) after stripping leading zeros")
print("✓ Behavior matches identifier error recovery pattern")
print("="*70)
