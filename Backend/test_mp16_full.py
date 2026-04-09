"""Test MP16: Array Elements Print & Sort with Recursion (lex+parse+semantic only)."""
from lexer import Lexer
from Gal_Parser import LL1Parser
from GALsemantic import build_ast
from cfg import cfg, first_sets, predict_sets

code = '''
pollinate empty printArr(seed arr[], seed n, seed i) {
    spring(i >= n) {
        reclaim ;
    }
    plant("{} ", arr[i]) ;
    printArr(arr, n, i + 1) ;
    reclaim ;
}

pollinate empty bblPass(seed arr[], seed n, seed i) {
    spring(i >= n - 1) {
        reclaim ;
    }
    spring(arr[i] > arr[i + 1]) {
        seed temp = arr[i] ;
        arr[i] = arr[i + 1] ;
        arr[i + 1] = temp ;
    }
    bblPass(arr, n, i + 1) ;
    reclaim ;
}

pollinate empty sortAsc(seed arr[], seed n) {
    spring(n <= 1) {
        reclaim ;
    }
    bblPass(arr, n, 0) ;
    sortAsc(arr, n - 1) ;
    reclaim ;
}

pollinate empty bblPassDsc(seed arr[], seed n, seed i) {
    spring(i >= n - 1) {
        reclaim ;
    }
    spring(arr[i] < arr[i + 1]) {
        seed dTemp = arr[i] ;
        arr[i] = arr[i + 1] ;
        arr[i + 1] = dTemp ;
    }
    bblPassDsc(arr, n, i + 1) ;
    reclaim ;
}

pollinate empty sortDsc(seed arr[], seed n) {
    spring(n <= 1) {
        reclaim ;
    }
    bblPassDsc(arr, n, 0) ;
    sortDsc(arr, n - 1) ;
    reclaim ;
}

root() {
    plant("Input the number of elements to be stored in the array :") ;
    seed n = water(seed) ;
    seed arr[20] ;

    plant("Input {} elements in the array :", n) ;
    cultivate(seed i = 0 ; i < n ; i++) {
        plant("element - {} : ", i) ;
        arr[i] = water(seed) ;
    }

    plant("The elements in the array are : ") ;
    printArr(arr, n, 0) ;

    plant("Sort Out:") ;
    plant("1. Ascending") ;
    plant("2. Descending") ;
    plant("Enter choice (1 or 2): ") ;
    seed choice = water(seed) ;

    spring(choice == 1) {
        sortAsc(arr, n) ;
        plant("Ascending order : ") ;
        printArr(arr, n, 0) ;
    }
    bud(choice == 2) {
        sortDsc(arr, n) ;
        plant("Descending order : ") ;
        printArr(arr, n, 0) ;
    }
    wither {
        plant("Invalid choice!") ;
    }

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
print("Parse:", errors)

# Semantic + AST
filtered = [t for t in tokens if t.type != '\n']
ast = build_ast(filtered)
print("Semantic + AST OK")
print("All stages passed!")
