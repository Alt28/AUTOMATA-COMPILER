from Backend.lexer import lex

code = '''root() {
 seed x = 5 + * 2;
  reclaim;
}'''

tokens, errors = lex(code)
print('=== LEXICAL ANALYSIS ===')
if errors:
    print('Lexical Errors:')
    for err in errors:
        print(f'  {err}')
else:
    print('✓ No lexical errors!')
    print(f'✓ Successfully tokenized {len(tokens)} tokens')
    print(f'\nTokens around the operators:')
    for i, t in enumerate(tokens):
        if t.value in ['5', '+', '*', '2']:
            print(f'  Token {i}: {t.type} = "{t.value}" (line {t.line}, col {t.col})')
