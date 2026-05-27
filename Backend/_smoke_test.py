import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import lex
from parser import LL1Parser
from cfg import cfg, first_sets, predict_sets
from semantic import validate_ast
from interpreter import Interpreter


class _Collector:
    def __init__(self): self.outputs = []
    def emit(self, event, data=None, **kw):
        if event == 'output' and data:
            self.outputs.append(data.get('output', ''))


PROGRAMS = [
    ('hello',   'root() { plant("hello"); reclaim; }',
     ['hello']),
    ('arith',   'root() { seed a = ~5 + 3; plant("b={}", a); reclaim; }',
     ['b=-2']),
    ('unary',   'root() { tree x = 2.5; tree y = ~x; seed n = ~(2 + 3); plant("{} {}", y, n); reclaim; }',
     ['-2.5 -5']),
    ('strings', 'root() { vine hi = "Hi"; leaf mark = \'!\'; vine msg = hi ` mark; branch same = msg == "Hi!"; plant("{} {}", msg, same); reclaim; }',
     ['Hi! True']),
    ('float',   'root() { tree pi = 3.14; tree r = 2.0; tree area = pi * r * r; plant("area={}", area); reclaim; }',
     ['area=12.56']),
    ('forloop', 'root() { seed s = 0; cultivate(seed i = 1; i <= 3; i++) { s += i; } plant("sum={}", s); reclaim; }',
     ['sum=6']),
    ('assignexpr', 'root() { seed a = 0; seed b = 0; seed c = (a = b = 5) + 2; plant("a={} b={} c={}", a, b, c); reclaim; }',
     ['a=5 b=5 c=7']),
    ('switch',  'root() { seed x = 2; harvest(x) { variety 1: { plant("one"); prune; } variety 2: { plant("two"); prune; } soil: { plant("other"); } } reclaim; }',
     ['two']),
    ('declfirst', 'root() { seed num = 5; plant("begin"); num += 2; plant("num={}", num); reclaim; }',
     ['begin', 'num=7']),
    ('bundlevar', 'bundle Student { seed age; }; root() { bundle Student student; student.age = 20; plant("age={}", student.age); reclaim; }',
     ['age=20']),
    ('nestedreturn', 'root() { branch stop = frost; spring (stop) { reclaim; } plant("continued"); reclaim; }',
     ['continued']),
    ('arr_postfix', 'root() { seed arr[3]; arr[0] = 1; arr[0]++; plant("v={}", arr[0]); reclaim; }',
     ['v=2']),
    ('arr_prefix',  'root() { seed arr[3]; arr[0] = 5; ++arr[0]; plant("v={}", arr[0]); reclaim; }',
     ['v=6']),
    ('arr_postdec', 'root() { seed arr[3]; arr[0] = 7; arr[0]--; plant("v={}", arr[0]); reclaim; }',
     ['v=6']),
    ('struct_postinc', 'bundle P { seed a; }; root() { bundle P p; p.a = 1; p.a++; plant("v={}", p.a); reclaim; }',
     ['v=2']),
    ('struct_preinc',  'bundle P { seed a; }; root() { bundle P p; p.a = 5; ++p.a; plant("v={}", p.a); reclaim; }',
     ['v=6']),
    ('struct_postdec', 'bundle P { seed a; }; root() { bundle P p; p.a = 10; p.a--; plant("v={}", p.a); reclaim; }',
     ['v=9']),
    ('arr_in_loop', 'root() { seed arr[3]; arr[0]=0; arr[1]=0; arr[2]=0; cultivate(seed i = 0; i < 3; i++) { arr[i]++; } plant("a={} b={} c={}", arr[0], arr[1], arr[2]); reclaim; }',
     ['a=1 b=1 c=1']),
    ('exp_assign_seed', 'root() { seed x = 2; x **= 3; plant("{}", x); reclaim; }',
     ['8']),
    ('exp_assign_chain', 'root() { seed x = 2; x **= 3; x **= 2; plant("{}", x); reclaim; }',
     ['64']),
    ('exp_assign_member', 'bundle P { seed v; }; root() { bundle P p; p.v = 5; p.v **= 2; plant("{}", p.v); reclaim; }',
     ['25']),
]

REJECTED_PROGRAMS = [
    ('late_decl', 'root() { plant("begin"); seed num = 5; reclaim; }',
     'Local declarations must appear first in the block.'),
    ('late_nested', 'root() { branch ok = sunshine; spring (ok) { plant("begin"); seed num = 5; } reclaim; }',
     'Local declarations must appear first in the block.'),
    ('late_case', 'root() { seed n = 1; harvest (n) { variety 1: plant("begin"); seed late = 5; prune; } reclaim; }',
     'Local declarations must appear first in the block.'),
    ('bundle_no_var', 'bundle Student { seed age; }; root() { bundle Student; reclaim; }',
     'Expected: id'),
    ('bundle_leading_comma', 'bundle Student { seed age; }; root() { bundle Student, student; reclaim; }',
     'Expected: id'),
    ('bundle_multiple', 'bundle Student { seed age; }; root() { bundle Student first, second; reclaim; }',
     "Expected: ';'"),
    ('missing_root_reclaim', 'root() { }',
     "expected 'reclaim;' before '}'"),
    ('missing_final_reclaim', 'root() { branch stop = sunshine; spring (stop) { reclaim; } }',
     "expected 'reclaim;' before '}'"),
    ('missing_function_reclaim', 'pollinate empty greet() { plant("hi"); } root() { reclaim; }',
     "expected 'reclaim;' before '}'"),
    ('array_decimal_size', 'root() { seed arr[2.5]; reclaim; }',
     "Expected: ']', intlit"),
    ('empty_initializer', 'root() { seed x = ; reclaim; }',
     "Missing value after '=' operator."),
    ('string_case_literal', 'root() { seed x = 1; harvest (x) { variety "a": { prune; } } reclaim; }',
     "Expected: chrlit, 'frost', intlit, 'sunshine'"),
]


def run():
    parser = LL1Parser(cfg=cfg, predict_sets=predict_sets, first_sets=first_sets,
                       start_symbol='<program>', end_marker='EOF', skip_token_types={'\n'})
    ok = 0
    for name, src, expected in PROGRAMS:
        tokens, lex_errs = lex(src)
        if lex_errs:
            print(f'{name:10s} LEX FAIL  {lex_errs[:1]}'); continue
        pr = parser.parse_and_build(tokens)
        if not pr['success']:
            print(f'{name:10s} PARSE FAIL  {pr["errors"][:1]}'); continue
        sr = validate_ast(pr['ast'], pr['symbol_table'])
        if not sr.get('success', True):
            print(f'{name:10s} SEM FAIL  {sr.get("errors", [])[:1]}'); continue
        c = _Collector()
        try:
            Interpreter(socketio=c).interpret(sr['ast'])
            status = 'OK' if c.outputs == expected else f'WRONG (expected {expected})'
            print(f'{name:10s} {status:30s} got {c.outputs}')
            if c.outputs == expected: ok += 1
        except Exception as e:
            print(f'{name:10s} RUN FAIL  {e}')

    reject_ok = 0
    for name, src, expected_error in REJECTED_PROGRAMS:
        tokens, lex_errs = lex(src)
        if lex_errs:
            print(f'{name:10s} LEX FAIL  {lex_errs[:1]}'); continue
        pr = parser.parse_and_build(tokens)
        message = pr.get('errors', [''])[0] if not pr['success'] else ''
        status = 'OK' if expected_error in message else f'WRONG (expected rejection containing {expected_error!r})'
        print(f'{name:10s} {status:30s} got {message!r}')
        if expected_error in message:
            reject_ok += 1
    print()
    print(f'PASS: {ok}/{len(PROGRAMS)} valid, {reject_ok}/{len(REJECTED_PROGRAMS)} rejected')
    return ok == len(PROGRAMS) and reject_ok == len(REJECTED_PROGRAMS)


if __name__ == '__main__':
    sys.exit(0 if run() else 1)
