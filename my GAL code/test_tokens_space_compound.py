from Backend.lexer import lex

code = """root() {
 a + = 2;

  reclaim;
}"""

tokens, lex_errors = lex(code)

print("Tokens:")
for i, tok in enumerate(tokens):
    print(f"  {i}: type={tok.type:15s} value={str(tok.value):15s} line={tok.line} col={tok.col}")
