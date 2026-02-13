import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from lexer import lex, get_token_description

code = 'root(){ vine string = "333"; reclaim; }'

print("="*60)
print("TESTING TOKEN TYPE DISPLAY")
print("="*60)
print(f"\nCode: {code}\n")

tokens, errors = lex(code)

print("LEXEMES TABLE:")
print(f"{'LEXEME':<15} {'TOKEN':<15} {'TYPE':<20}")
print("-" * 60)

for token in tokens:
    if token.type != '\n' and token.value != '':
        lexeme = token.value if token.value else token.type
        tok_type = token.type
        description = get_token_description(token.type)
        print(f"{lexeme:<15} {tok_type:<15} {description:<20}")

print("\n" + "="*60)
print("✓ The TYPE for 'stringlit' should now show: string")
print("="*60)
