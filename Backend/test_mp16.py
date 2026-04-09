"""Test MP16: Array print + sort with recursion using array parameter passing."""
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

pollinate empty bubblePass(seed arr[], seed n, seed i) {
    spring(i >= n - 1) {
        reclaim ;
    }
    spring(arr[i] > arr[i + 1]) {
        seed temp = arr[i] ;
        arr[i] = arr[i + 1] ;
        arr[i + 1] = temp ;
    }
    bubblePass(arr, n, i + 1) ;
    reclaim ;
}

pollinate empty bubbleSort(seed arr[], seed n) {
    spring(n <= 1) {
        reclaim ;
    }
    bubblePass(arr, n, 0) ;
    bubbleSort(arr, n - 1) ;
    reclaim ;
}

root() {
    seed nums[5] ;
    nums[0] = 64 ;
    nums[1] = 34 ;
    nums[2] = 25 ;
    nums[3] = 12 ;
    nums[4] = 22 ;

    plant("Before sorting:") ;
    printArr(nums, 5, 0) ;
    plant("") ;

    bubbleSort(nums, 5) ;

    plant("After sorting:") ;
    printArr(nums, 5, 0) ;
    plant("") ;
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
