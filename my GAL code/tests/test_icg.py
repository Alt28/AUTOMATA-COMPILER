import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

from lexer import lex
from icg import generate_icg

# Test 1: Constants, arrays, booleans, strings, logical operators
code1 = """
fertile seed MAX = 100;
seed arr[5];

root() {
    branch flag = sunshine;
    vine msg = "hello";
    seed i;

    spring (flag == sunshine) {
        plant(msg);
    }

    water(i);
    plant(i);

    reclaim 0;
}
"""

# Test 2: Comprehensive with all loop types
code2 = """
pollinate seed add(seed a, seed b) {
    reclaim a + b;
}

root() {
    seed i = 0;
    seed sum = 0;

    grow (i < 10) {
        sum += i;
        i++;
    }

    cultivate (seed j = 0; j < 5; j++) {
        plant(j);
    }

    seed k = 0;
    tend {
        k++;
    } grow (k < 3);

    seed result = add(sum, k);

    harvest (result) {
        variety 1:
            plant(1);
            prune;
        variety 2:
            plant(2);
            prune;
        soil:
            plant(0);
    }

    reclaim 0;
}
"""

for label, code in [("Test 1", code1), ("Test 2", code2)]:
    print(f"{'='*60}")
    print(f" {label}")
    print(f"{'='*60}")
    tokens, errors = lex(code)
    if errors:
        print("LEX ERRORS:", errors)
    else:
        result = generate_icg(tokens)
        print("SUCCESS:", result["success"])
        print()
        print(result["tac_text"])
        if result["errors"]:
            print()
            print("ERRORS:", result["errors"])
    print()
