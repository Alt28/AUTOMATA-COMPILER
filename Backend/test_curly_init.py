"""Test array initialization with curly brace syntax: seed nums[3] = {10, 20, 30}"""
from lexer import Lexer
from Gal_Parser import LL1Parser
from GALsemantic import build_ast
from GALinterpreter import Interpreter
from cfg import cfg, first_sets, predict_sets

code = '''
pollinate empty printArr(seed arr[], seed n, seed i) {
    spring(i >= n) {
        reclaim ;
    }
    plant("{}  ", arr[i]) ;
    printArr(arr, n, i + 1) ;
    reclaim ;
}

root() {
    seed nums[3] = {10, 20, 30} ;
    printArr(nums, 3, 0) ;
    reclaim ;
}
'''

lexer = Lexer(code)
tokens, lex_errors = lexer.make_tokens()
print("Lex:", len(tokens), "tokens, errors:", lex_errors)

parser = LL1Parser(cfg=cfg, predict_sets=predict_sets, first_sets=first_sets)
errors = parser.parse(tokens)
print("Parse:", errors)

filtered = [t for t in tokens if t.type != '\n']
ast = build_ast(filtered)
print("Semantic OK")

interp = Interpreter()
interp.plant = lambda value: print(value, end="")
interp.interpret(ast)
print()
print("Done")
