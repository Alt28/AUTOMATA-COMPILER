from Backend.lexer import lex

code = """root() {
 branch r = (a === b);
  reclaim;
}"""

print("Testing triple equals tokenization...")
print(f"Code:\n{code}\n")

tokens, errors = lex(code)

print("Lexer errors:")
for err in errors:
    print(f"  {err}")

print(f"\nTokens:")
for i, tok in enumerate(tokens):
    print(f"  {i}: {tok.type:15} {repr(tok.value):20} line {tok.line} col {tok.col}")
