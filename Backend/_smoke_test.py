# AUTO: Imports a module used by this file.
import sys, os
# AUTO: Calls `sys.path.insert`.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# AUTO: Imports names from another module.
from lexer import lex
# AUTO: Imports names from another module.
from parser import LL1Parser
# AUTO: Imports names from another module.
from cfg import cfg, first_sets, predict_sets
# AUTO: Imports names from another module.
from semantic import validate_ast
# AUTO: Imports names from another module.
from interpreter import Interpreter


# AUTO: Defines class `_Collector`.
class _Collector:
    # AUTO: Defines function `__init__`.
    def __init__(self): self.outputs = []
    # AUTO: Defines function `emit`.
    def emit(self, event, data=None, **kw):
        # AUTO: Checks this condition.
        if event == 'output' and data:
            # AUTO: Appends a value to a list.
            self.outputs.append(data.get('output', ''))


# AUTO: Sets `PROGRAMS`.
PROGRAMS = [
    # AUTO: Executes this statement.
    ('hello',   'root() { plant("hello"); reclaim; }',
     # AUTO: Calls `function`.
     ['hello']),
    # AUTO: Sets `('arith',   'root() { seed a`.
    ('arith',   'root() { seed a = ~5 + 3; plant("b={}", a); reclaim; }',
     # AUTO: Sets `['b`.
     ['b=-2']),
    # AUTO: Sets `('unary',   'root() { tree x`.
    ('unary',   'root() { tree x = 2.5; tree y = ~x; seed n = ~(2 + 3); plant("{} {}", y, n); reclaim; }',
     # AUTO: Calls `function`.
     ['-2.5 -5']),
    # AUTO: Executes this statement.
    ('strings', 'root() { vine hi = "Hi"; leaf mark = \'!\'; vine msg = hi ` mark; branch same = msg == "Hi!"; plant("{} {}", msg, same); reclaim; }',
     # AUTO: Calls `function`.
     ['Hi! True']),
    # AUTO: Sets `('float',   'root() { tree pi`.
    ('float',   'root() { tree pi = 3.14; tree r = 2.0; tree area = pi * r * r; plant("area={}", area); reclaim; }',
     # AUTO: Sets `['area`.
     ['area=12.56']),
    # AUTO: Adds into `('forloop', 'root() { seed s = 0; cultivate(seed i = 1; i <= 3; i++) { s`.
    ('forloop', 'root() { seed s = 0; cultivate(seed i = 1; i <= 3; i++) { s += i; } plant("sum={}", s); reclaim; }',
     # AUTO: Sets `['sum`.
     ['sum=6']),
    # AUTO: Sets `('assignexpr', 'root() { seed a`.
    ('assignexpr', 'root() { seed a = 0; seed b = 0; seed c = (a = b = 5) + 2; plant("a={} b={} c={}", a, b, c); reclaim; }',
     # AUTO: Sets `['a`.
     ['a=5 b=5 c=7']),
    # AUTO: Sets `('switch',  'root() { seed x`.
    ('switch',  'root() { seed x = 2; harvest(x) { variety 1: { plant("one"); prune; } variety 2: { plant("two"); prune; } soil: { plant("other"); } } reclaim; }',
     # AUTO: Calls `function`.
     ['two']),
    # AUTO: Adds into `('declfirst', 'root() { seed num = 5; plant("begin"); num`.
    ('declfirst', 'root() { seed num = 5; plant("begin"); num += 2; plant("num={}", num); reclaim; }',
     # AUTO: Sets `['begin', 'num`.
     ['begin', 'num=7']),
    # AUTO: Sets `('bundlevar', 'bundle Student { seed age; }; root() { bundle Student student; student.age`.
    ('bundlevar', 'bundle Student { seed age; }; root() { bundle Student student; student.age = 20; plant("age={}", student.age); reclaim; }',
     # AUTO: Sets `['age`.
     ['age=20']),
    # AUTO: Sets `('nestedreturn', 'root() { branch stop`.
    ('nestedreturn', 'root() { branch stop = frost; spring (stop) { reclaim; } plant("continued"); reclaim; }',
     # AUTO: Calls `function`.
     ['continued']),
    # AUTO: Sets `('arr_postfix', 'root() { seed arr[3]; arr[0]`.
    ('arr_postfix', 'root() { seed arr[3]; arr[0] = 1; arr[0]++; plant("v={}", arr[0]); reclaim; }',
     # AUTO: Sets `['v`.
     ['v=2']),
    # AUTO: Sets `('arr_prefix',  'root() { seed arr[3]; arr[0]`.
    ('arr_prefix',  'root() { seed arr[3]; arr[0] = 5; ++arr[0]; plant("v={}", arr[0]); reclaim; }',
     # AUTO: Sets `['v`.
     ['v=6']),
    # AUTO: Sets `('arr_postdec', 'root() { seed arr[3]; arr[0]`.
    ('arr_postdec', 'root() { seed arr[3]; arr[0] = 7; arr[0]--; plant("v={}", arr[0]); reclaim; }',
     # AUTO: Sets `['v`.
     ['v=6']),
    # AUTO: Sets `('struct_postinc', 'bundle P { seed a; }; root() { bundle P p; p.a`.
    ('struct_postinc', 'bundle P { seed a; }; root() { bundle P p; p.a = 1; p.a++; plant("v={}", p.a); reclaim; }',
     # AUTO: Sets `['v`.
     ['v=2']),
    # AUTO: Sets `('struct_preinc',  'bundle P { seed a; }; root() { bundle P p; p.a`.
    ('struct_preinc',  'bundle P { seed a; }; root() { bundle P p; p.a = 5; ++p.a; plant("v={}", p.a); reclaim; }',
     # AUTO: Sets `['v`.
     ['v=6']),
    # AUTO: Sets `('struct_postdec', 'bundle P { seed a; }; root() { bundle P p; p.a`.
    ('struct_postdec', 'bundle P { seed a; }; root() { bundle P p; p.a = 10; p.a--; plant("v={}", p.a); reclaim; }',
     # AUTO: Sets `['v`.
     ['v=9']),
    # AUTO: Sets `('arr_in_loop', 'root() { seed arr[3]; arr[0]`.
    ('arr_in_loop', 'root() { seed arr[3]; arr[0]=0; arr[1]=0; arr[2]=0; cultivate(seed i = 0; i < 3; i++) { arr[i]++; } plant("a={} b={} c={}", arr[0], arr[1], arr[2]); reclaim; }',
     # AUTO: Sets `['a`.
     ['a=1 b=1 c=1']),
    # AUTO: Multiplies into `('exp_assign_seed', 'root() { seed x = 2; x *`.
    ('exp_assign_seed', 'root() { seed x = 2; x **= 3; plant("{}", x); reclaim; }',
     # AUTO: Calls `function`.
     ['8']),
    # AUTO: Multiplies into `('exp_assign_chain', 'root() { seed x = 2; x *`.
    ('exp_assign_chain', 'root() { seed x = 2; x **= 3; x **= 2; plant("{}", x); reclaim; }',
     # AUTO: Calls `function`.
     ['64']),
    # AUTO: Multiplies into `('exp_assign_member', 'bundle P { seed v; }; root() { bundle P p; p.v = 5; p.v *`.
    ('exp_assign_member', 'bundle P { seed v; }; root() { bundle P p; p.v = 5; p.v **= 2; plant("{}", p.v); reclaim; }',
     # AUTO: Calls `function`.
     ['25']),
# AUTO: Closes the current grouped code/data.
]

# AUTO: Sets `REJECTED_PROGRAMS`.
REJECTED_PROGRAMS = [
    # AUTO: Sets `('late_decl', 'root() { plant("begin"); seed num`.
    ('late_decl', 'root() { plant("begin"); seed num = 5; reclaim; }',
     # AUTO: Calls `function`.
     'Local declarations must appear first in the block.'),
    # AUTO: Sets `('late_nested', 'root() { branch ok`.
    ('late_nested', 'root() { branch ok = sunshine; spring (ok) { plant("begin"); seed num = 5; } reclaim; }',
     # AUTO: Calls `function`.
     'Local declarations must appear first in the block.'),
    # AUTO: Sets `('late_case', 'root() { seed n`.
    ('late_case', 'root() { seed n = 1; harvest (n) { variety 1: plant("begin"); seed late = 5; prune; } reclaim; }',
     # AUTO: Calls `function`.
     'Local declarations must appear first in the block.'),
    # AUTO: Executes this statement.
    ('bundle_no_var', 'bundle Student { seed age; }; root() { bundle Student; reclaim; }',
     # AUTO: Calls `function`.
     'Expected: id'),
    # AUTO: Executes this statement.
    ('bundle_leading_comma', 'bundle Student { seed age; }; root() { bundle Student, student; reclaim; }',
     # AUTO: Calls `function`.
     'Expected: id'),
    # AUTO: Executes this statement.
    ('bundle_multiple', 'bundle Student { seed age; }; root() { bundle Student first, second; reclaim; }',
     # AUTO: Calls `function`.
     "Expected: ';'"),
    # AUTO: Executes this statement.
    ('missing_root_reclaim', 'root() { }',
     # AUTO: Calls `function`.
     "expected 'reclaim;' before '}'"),
    # AUTO: Sets `('missing_final_reclaim', 'root() { branch stop`.
    ('missing_final_reclaim', 'root() { branch stop = sunshine; spring (stop) { reclaim; } }',
     # AUTO: Calls `function`.
     "expected 'reclaim;' before '}'"),
    # AUTO: Executes this statement.
    ('missing_function_reclaim', 'pollinate empty greet() { plant("hi"); } root() { reclaim; }',
     # AUTO: Calls `function`.
     "expected 'reclaim;' before '}'"),
    # AUTO: Executes this statement.
    ('array_decimal_size', 'root() { seed arr[2.5]; reclaim; }',
     # AUTO: Calls `function`.
     "Expected: ']', intlit"),
    # AUTO: Sets `('empty_initializer', 'root() { seed x`.
    ('empty_initializer', 'root() { seed x = ; reclaim; }',
     # AUTO: Sets `"Missing value after '`.
     "Missing value after '=' operator."),
    # AUTO: Sets `('string_case_literal', 'root() { seed x`.
    ('string_case_literal', 'root() { seed x = 1; harvest (x) { variety "a": { prune; } } reclaim; }',
     # AUTO: Calls `function`.
     "Expected: chrlit, 'frost', intlit, 'sunshine'"),
# AUTO: Closes the current grouped code/data.
]


# AUTO: Defines function `run`.
def run():
    # AUTO: Sets `parser`.
    parser = LL1Parser(cfg=cfg, predict_sets=predict_sets, first_sets=first_sets,
                       # AUTO: Sets `start_symbol`.
                       start_symbol='<program>', end_marker='EOF',
                       # AUTO: Sets `skip_token_types`.
                       skip_token_types={'\n', 'comment', 'mcommentlit'})
    # AUTO: Sets `ok`.
    ok = 0
    # AUTO: Starts a loop over these values.
    for name, src, expected in PROGRAMS:
        # AUTO: Sets `tokens, lex_errs`.
        tokens, lex_errs = lex(src)
        # AUTO: Checks this condition.
        if lex_errs:
            # AUTO: Executes this statement.
            print(f'{name:10s} LEX FAIL  {lex_errs[:1]}'); continue
        # AUTO: Sets `pr`.
        pr = parser.parse_and_build(tokens)
        # AUTO: Checks this condition.
        if not pr['success']:
            # AUTO: Executes this statement.
            print(f'{name:10s} PARSE FAIL  {pr["errors"][:1]}'); continue
        # AUTO: Sets `sr`.
        sr = validate_ast(pr['ast'], pr['symbol_table'])
        # AUTO: Checks this condition.
        if not sr.get('success', True):
            # AUTO: Executes this statement.
            print(f'{name:10s} SEM FAIL  {sr.get("errors", [])[:1]}'); continue
        # AUTO: Sets `c`.
        c = _Collector()
        # AUTO: Starts protected code that can catch errors.
        try:
            # AUTO: Sets `Interpreter(socketio`.
            Interpreter(socketio=c).interpret(sr['ast'])
            # AUTO: Executes this statement.
            status = 'OK' if c.outputs == expected else f'WRONG (expected {expected})'
            # AUTO: Calls `print`.
            print(f'{name:10s} {status:30s} got {c.outputs}')
            # AUTO: Checks this condition.
            if c.outputs == expected: ok += 1
        # AUTO: Handles the matching error case.
        except Exception as e:
            # AUTO: Calls `print`.
            print(f'{name:10s} RUN FAIL  {e}')

    # AUTO: Sets `reject_ok`.
    reject_ok = 0
    # AUTO: Starts a loop over these values.
    for name, src, expected_error in REJECTED_PROGRAMS:
        # AUTO: Sets `tokens, lex_errs`.
        tokens, lex_errs = lex(src)
        # AUTO: Checks this condition.
        if lex_errs:
            # AUTO: Executes this statement.
            print(f'{name:10s} LEX FAIL  {lex_errs[:1]}'); continue
        # AUTO: Sets `pr`.
        pr = parser.parse_and_build(tokens)
        # AUTO: Sets `message`.
        message = pr.get('errors', [''])[0] if not pr['success'] else ''
        # AUTO: Sets `status`.
        status = 'OK' if expected_error in message else f'WRONG (expected rejection containing {expected_error!r})'
        # AUTO: Calls `print`.
        print(f'{name:10s} {status:30s} got {message!r}')
        # AUTO: Checks this condition.
        if expected_error in message:
            # AUTO: Adds into `reject_ok`.
            reject_ok += 1
    # AUTO: Calls `print`.
    print()
    # AUTO: Calls `print`.
    print(f'PASS: {ok}/{len(PROGRAMS)} valid, {reject_ok}/{len(REJECTED_PROGRAMS)} rejected')
    # AUTO: Returns this result to the caller.
    return ok == len(PROGRAMS) and reject_ok == len(REJECTED_PROGRAMS)


# AUTO: Checks this condition.
if __name__ == '__main__':
    # AUTO: Calls `sys.exit`.
    sys.exit(0 if run() else 1)
