"""Test GAL arithmetic, string, boolean, and other operations."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

from lexer import lex
from Gal_Parser import LL1Parser
from GALsemantic import analyze_semantics
from GALinterpreter import Interpreter
from cfg import cfg, first_sets, predict_sets

code = r"""
root() {
    vine name;
    seed age;

    plant("Enter your name: ");
    name = water();

    plant("Enter your age: ");
    age = water(seed);

    plant("Hello ");
    plant(name);

    plant("You are ");
    plant(age);

    spring (age >= 18) {
        plant("Status: Adult\n");
    } wither {
        plant("Status: Minor");
    }

    reclaim;
}
"""

# Lex
tokens, lex_errors = lex(code)
if lex_errors:
    print("LEX ERRORS:", lex_errors)
    sys.exit(1)
print("Lexer: OK")

# Parse
parser = LL1Parser(cfg=cfg, predict_sets=predict_sets, first_sets=first_sets,
                   start_symbol="<program>", end_marker="EOF", skip_token_types={'\n'})
success, parse_errors = parser.parse(tokens)
if not success:
    print("PARSE ERRORS:", parse_errors)
    sys.exit(1)
print("Parser: OK")

# Semantic
semantic_result = analyze_semantics(tokens)
if not semantic_result['success']:
    print("SEMANTIC ERRORS:", semantic_result['errors'])
    sys.exit(1)
print("Semantic: OK")
ast = semantic_result['ast']

# Interpret
class FakeIO:
    """Dummy socketio that just collects output."""
    def __init__(self): self.messages = []
    def emit(self, event, data, **kw):
        if event == 'output':
            self.messages.append(data.get('output', ''))

fake = FakeIO()
interp = Interpreter(socketio=fake)
interp.interpret(ast)
print("--- Interpreter Output ---")
# Also check interp.output
for line in interp.output:
    print(line)
for msg in fake.messages:
    print(msg)
