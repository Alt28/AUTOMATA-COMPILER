"""Smoke test runner for restructure. Run after each phase: python _smoke_test.py"""
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
    print()
    print(f'PASS: {ok}/{len(PROGRAMS)}')
    return ok == len(PROGRAMS)


if __name__ == '__main__':
    sys.exit(0 if run() else 1)
