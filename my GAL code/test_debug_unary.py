import sys
sys.path.insert(0, './Backend')
from Gal_Parser import LL1Parser
from lexer import Lexer
from cfg import cfg, first_sets, predict_sets

code = "root() { seed x = -5; reclaim; }"
l = Lexer(code)
tokens, lex_errors = l.make_tokens()

# Print tokens
print("Tokens:")
for i, tok in enumerate(tokens):
    print(f"  {i}: {tok.type} = '{tok.value}' at Ln {tok.line}, Col {tok.col}")

# Add debugging to parser
original_generate = LL1Parser._generate_helpful_error

def debug_generate(self, non_terminal, token, expected, toks, index):
    result = original_generate(self, non_terminal, token, expected, toks, index)
    print(f"\nError at index {index}:")
    print(f"  Non-terminal: {non_terminal}")
    print(f"  Token: {token.type} = '{token.value}'")
    print(f"  Expected: {expected}")
    print(f"  Result: {result}")
    return result

LL1Parser._generate_helpful_error = debug_generate

p = LL1Parser(
    cfg=cfg, 
    predict_sets=predict_sets, 
    first_sets=first_sets, 
    start_symbol='<program>', 
    end_marker='EOF', 
    skip_token_types={'\n'}
)

success, parse_errors = p.parse(tokens)
print(f"\nFinal Error: {parse_errors[0] if parse_errors else 'None'}")
