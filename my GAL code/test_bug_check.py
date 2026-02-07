import sys
sys.path.insert(0, './Backend')
from Gal_Parser import LL1Parser
from lexer import Lexer
from cfg import cfg, first_sets, predict_sets

# Test cases
test_cases = [
    ("Missing semicolon", "root() { seed x x = 1; reclaim; }"),
    ("Invalid keyword 'if'", "root() { seed x = 10; if (x > 5) { } reclaim; }"),
    ("Bundle inside function", "root() { bundle Person { seed id; }; reclaim; }"),
    ("Missing closing brace", "root() { seed x = 10; reclaim; "),
    ("Unary minus", "root() { seed x = -5; reclaim; }"),
    ("Empty function", "root() { }"),
    ("Missing prune in default case", """root() {
 seed choice;
 choice = 2;
 harvest (choice) {
  variety 1:
   plant("one");
   prune;
  soil:
   plant("default");
 }
 reclaim;
}"""),
    ("Valid code", "root() { seed x = 10; reclaim; }"),
]

print("=" * 80)
print("TESTING PARSER FOR BUGS")
print("=" * 80)

for name, code in test_cases:
    print(f"\n{name}:")
    print(f"Code: {code[:50]}...")
    
    l = Lexer(code)
    tokens, lex_errors = l.make_tokens()
    
    if lex_errors:
        print(f"❌ Lexer Errors: {lex_errors}")
        continue
    
    p = LL1Parser(
        cfg=cfg, 
        predict_sets=predict_sets, 
        first_sets=first_sets, 
        start_symbol='<program>', 
        end_marker='EOF', 
        skip_token_types={'\n'}
    )
    
    success, parse_errors = p.parse(tokens)
    
    if parse_errors:
        print(f"❌ Parse Error: {parse_errors[0]}")
    else:
        print(f"✅ Success: No errors")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
