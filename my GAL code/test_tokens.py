from Backend.lexer import lex

code = '''root() {
 seed x = 5 + * 2;
  reclaim;
}'''

tokens, lex_errors = lex(code)

print('=== TOKENS ===')
for i, t in enumerate(tokens):
    print(f'{i:2}: {t.type:15} = "{t.value}" (line {t.line}, col {t.col})')
