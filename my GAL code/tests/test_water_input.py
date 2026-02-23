import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Backend.lexer import Lexer

code = r"""root() {
    vine name;
    seed age;
    seed nextAge;

    plant("Name: ");
    name = water(vine);

    plant("Age: ");
    age = water(seed);

    nextAge = age + 1;

    plant("Hello ");
    plant(name);

    plant("Next year you are ");
    plant(nextAge);

    reclaim;
}"""

lexer = Lexer(code)
tokens, errors = lexer.make_tokens()
print('=== TOKENS ===')
for t in tokens:
    print(f'  Line {t.line}: type={t.type!r:15s} value={t.value!r}')
print()
if errors:
    print('=== LEXER ERRORS ===')
    for e in errors:
        print(f'  {e}')
    sys.exit(1)

print('=== PARSING ===')
from Backend.cfg import cfg, compute_first, compute_follow, compute_predict
from Backend.Gal_Parser import LL1Parser

first = compute_first(cfg)
follow = compute_follow(cfg, first)
predict = compute_predict(cfg, first, follow)

parser = LL1Parser(cfg, predict, first)
result = parser.parse(tokens)
print(result)
