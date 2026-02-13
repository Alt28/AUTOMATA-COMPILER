from Backend.lexer import lex
import sys
import io

# Test case: identifier followed by literal without operator
code = """root() {
  seed x =  fff 2 + 3; 
  reclaim;
}"""

print("Testing code:")
print(code)
print("\n" + "="*80 + "\n")

# Tokenize
tokens, lex_errors = lex(code)

print(f"Lexical Analysis: {len(lex_errors)} errors")
for err in lex_errors:
    print(f"  {err}")

print(f"\nTokens: {len(tokens)}")
for i, tok in enumerate(tokens):
    print(f"  {i}: type={tok.type:15s} value={str(tok.value):15s} line={tok.line} col={tok.col}")
