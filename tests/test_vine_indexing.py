"""Quick test for vine (string) indexing and soil/bloom support."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

from lexer import lex
from GALsemantic import analyze_semantics
from GALinterpreter import Interpreter

# Test 1: Read vine[i] - both direct plant and via variable
code1 = """
root() {{
    vine word = "hello";
    vine ch = word[0];
    plant(ch);
    vine ch2 = word[4];
    plant(ch2);
    reclaim;
}}
"""

# Test 2: vine indexing in a loop (palindrome-like)
code2 = """
root() {{
    vine word = "racecar";
    seed len = 7;
    seed i = 0;
    branch isPalindrome = sunshine;
    grow(i < len / 2) {{
        spring(word[i] != word[len - 1 - i]) {{
            isPalindrome = frost;
        }}
        i++;
    }}
    spring(isPalindrome == sunshine) {{
        plant("Palindrome!");
    }}
    wither {{
        plant("Not a palindrome");
    }}
    reclaim;
}}
"""

# Test 3: wilt (lowercase) and bloom (uppercase)
code3 = """
root() {{
    vine word = "Hello World";
    vine lower = word.wilt;
    vine upper = word.bloom;
    plant(lower);
    plant(upper);
    reclaim;
}}
"""

def run_test(label, code):
    print(f"\n=== {label} ===")
    try:
        tokens, lex_errors = lex(code)
        if lex_errors:
            print(f"Lex errors: {lex_errors}")
            return False
        result = analyze_semantics(tokens)
        if not result["success"]:
            print(f"Semantic Error: {result['errors']}")
            return False
        ast = result["ast"]
        output = []
        
        # Mock socketio
        class MockSocketIO:
            def emit(self, event, data):
                output.append(data['output'])
        
        interp = Interpreter(socketio=MockSocketIO())
        interp.interpret(ast)
        print("Output:", output)
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR: {e}")
        return False

ok1 = run_test("Test 1: Basic vine indexing", code1)
ok2 = run_test("Test 2: Palindrome check with vine indexing", code2)
ok3 = run_test("Test 3: soil/bloom (lowercase/uppercase)", code3)

print(f"\nResults: {'PASS' if ok1 else 'FAIL'} / {'PASS' if ok2 else 'FAIL'} / {'PASS' if ok3 else 'FAIL'}")
