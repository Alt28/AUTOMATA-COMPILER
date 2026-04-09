"""Quick test for array parameter passing feature."""
from lexer import Lexer
from Gal_Parser import LL1Parser
from GALsemantic import build_ast
from GALinterpreter import Interpreter
from cfg import cfg, first_sets, predict_sets

code = '''
pollinate empty printEl(seed arr[], seed i) {
    plant("{} ", arr[i]) ;
    reclaim ;
}

root() {
    seed nums[3] ;
    nums[0] = 10 ;
    nums[1] = 20 ;
    nums[2] = 30 ;
    printEl(nums, 0) ;
    printEl(nums, 1) ;
    printEl(nums, 2) ;
    reclaim ;
}
'''

# Lexer
lexer = Lexer(code)
tokens, lex_errors = lexer.make_tokens()
print("Lex OK:", len(tokens), "tokens, errors:", lex_errors)

# Parser
parser = LL1Parser(cfg=cfg, predict_sets=predict_sets, first_sets=first_sets)
errors = parser.parse(tokens)
print("Parse errors:", errors)

# Semantic + AST
filtered = [t for t in tokens if t.type != '\n']
ast = build_ast(filtered)
print("Semantic + AST OK")

# Interpreter — patch plant() since no Socket.IO in test
interp = Interpreter()
interp.plant = lambda value: print(value, end="")
interp.interpret(ast)
print("\nDone")
