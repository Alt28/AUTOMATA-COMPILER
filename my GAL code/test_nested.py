import sys
sys.path.insert(0, 'Backend')
from lexer import lex
from GALsemantic import analyze_semantics
from GALinterpreter import Interpreter

class FakeIO:
    def __init__(self):
        self.outputs = []
    def emit(self, event, data):
        if event == 'output':
            self.outputs.append(data)

def run_test(name, code):
    print(f"\n=== {name} ===")
    tokens, errors = lex(code)
    if errors:
        print('LEX ERRORS:', errors)
        return
    result = analyze_semantics(tokens)
    if isinstance(result, dict):
        if result.get('errors'):
            print('SEMANTIC ERRORS:', result['errors'])
            return
        ast = result.get('ast')
    else:
        ast = result
    if ast:
        fake = FakeIO()
        interp = Interpreter(socketio=fake)
        interp.interpret(ast)
        outputs = [o['output'] for o in fake.outputs]
        print('OUTPUTS:', outputs)

# Test 1: Nested bundles
run_test("Nested Bundles", '''
bundle Address {
    seed zip;
};
bundle Person {
    vine name;
    Address addr;
};
root() {
    bundle Person p;
    p.name = "Ana";
    p.addr.zip = 1000;
    plant(p.name);
    plant(p.addr.zip);
    reclaim;
}
''')

# Test 2: Regular bundle (no nesting)
run_test("Regular Bundle", '''
bundle Point {
    seed x;
    seed y;
};
root() {
    bundle Point p;
    p.x = 10;
    p.y = 20;
    plant(p.x);
    plant(p.y);
    reclaim;
}
''')

# Test 3: Bundle array
run_test("Bundle Array", '''
bundle Point {
    seed x;
    seed y;
};
root() {
    bundle Point p[2];
    p[0].x = 1;
    p[0].y = 2;
    p[1].x = 3;
    p[1].y = 4;
    plant(p[0].x);
    plant(p[1].y);
    reclaim;
}
''')

# Test 4: Regular array
run_test("Regular Array", '''
root() {
    seed a[3] = {10, 20, 30};
    plant(a[0]);
    plant(a[1]);
    plant(a[2]);
    reclaim;
}
''')

# Test 5: Bundle array with nested bundle
run_test("Bundle Array with Nested Bundle", '''
bundle Address {
    seed zip;
};
bundle Person {
    vine name;
    Address addr;
};
root() {
    bundle Person people[2];
    people[0].name = "Alice";
    people[0].addr.zip = 12345;
    people[1].name = "Bob";
    people[1].addr.zip = 67890;
    plant(people[0].name);
    plant(people[0].addr.zip);
    plant(people[1].name);
    plant(people[1].addr.zip);
    reclaim;
}
''')
