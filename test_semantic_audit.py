"""
Semantic Error Audit Test Suite for the GAL Compiler
=====================================================
Tests each category from the textbook checklist:
  1. Variable and Function Declarations
  2. Type Compatibility
  3. Function-Related Errors
  4. Scope and Visibility
  5. Control Flow Errors
  6. Array and Pointer Errors
  7. Struct/Bundle Errors
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Backend"))

from lexer import lex
from Gal_Parser import LL1Parser
from cfg import cfg, first_sets, predict_sets

parser = LL1Parser(cfg, predict_sets, first_sets)

def compile_gal(code):
    """Returns (success: bool, errors: list[str], stage: str)"""
    tokens, lex_errors = lex(code)
    if lex_errors:
        return False, lex_errors, "lexical"
    result = parser.parse_and_build(tokens)
    if not result["success"]:
        return False, [str(e) for e in result["errors"]], result.get("error_stage", "syntax")
    return True, [], "ok"

def expect_error(label, code, keyword=None):
    """Expect compilation to FAIL. Optionally check error contains keyword."""
    ok, errors, stage = compile_gal(code)
    if ok:
        print(f"  FAIL  {label} — expected error but compiled OK")
        return False
    if keyword and not any(keyword.lower() in e.lower() for e in errors):
        print(f"  FAIL  {label} — error found but missing keyword '{keyword}': {errors}")
        return False
    print(f"  PASS  {label}")
    return True

def expect_ok(label, code):
    """Expect compilation to SUCCEED."""
    ok, errors, stage = compile_gal(code)
    if not ok:
        print(f"  FAIL  {label} — expected OK but got {stage} error: {errors}")
        return False
    print(f"  PASS  {label}")
    return True

passed = 0
failed = 0
total = 0

def run(fn, *args):
    global passed, failed, total
    total += 1
    if fn(*args):
        passed += 1
    else:
        failed += 1


# ═══════════════════════════════════════════════════════════════════════
# 1. VARIABLE AND FUNCTION DECLARATIONS
# ═══════════════════════════════════════════════════════════════════════
print("\n=== 1. Variable and Function Declarations ===")

# 1a. Duplicate variable declaration (same scope)
run(expect_error, "1a. Duplicate variable (same scope)", """
root() {
    seed x;
    seed x;
    reclaim;
}
""", "already declared")

# 1b. Duplicate function declaration
run(expect_error, "1b. Duplicate function declaration", """
pollinate empty foo() { reclaim; }
pollinate empty foo() { reclaim; }
root() { reclaim; }
""", "already declared")

# 1c. Use of undeclared variable
run(expect_error, "1c. Undeclared variable", """
root() {
    x = 5;
    reclaim;
}
""", "before declaration")

# 1d. Use of undeclared function
run(expect_error, "1d. Undeclared function", """
root() {
    bar();
    reclaim;
}
""", "not")

# 1e. Valid declaration (positive test)
run(expect_ok, "1e. Valid declarations", """
seed g;
pollinate empty foo() { reclaim; }
root() {
    seed x;
    x = 5;
    foo();
    reclaim;
}
""")


# ═══════════════════════════════════════════════════════════════════════
# 2. TYPE COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════════
print("\n=== 2. Type Compatibility ===")

# 2a. Assign string to integer variable
run(expect_error, "2a. Assign vine to seed", """
root() {
    seed x;
    x = "hello";
    reclaim;
}
""", "type")

# 2b. seed ↔ tree implicit conversion (should succeed)
run(expect_ok, "2b. seed ↔ tree implicit conversion", """
root() {
    seed x;
    tree y;
    x = 5;
    y = x;
    reclaim;
}
""")

# 2c. Comparing incompatible types (seed == vine)
run(expect_error, "2c. Compare seed == vine", """
root() {
    seed x;
    x = 5;
    spring (x == "hello") {
        plant("bad");
    }
    reclaim;
}
""", "compare")

# 2d. Arithmetic on non-numeric (vine + vine using +)
run(expect_error, "2d. Arithmetic + on vine", """
root() {
    vine a;
    vine b;
    a = "hi";
    b = "lo";
    seed c;
    c = a + b;
    reclaim;
}
""")

# 2e. Valid type usage (positive)
run(expect_ok, "2e. Valid types", """
root() {
    seed a;
    tree b;
    a = 3;
    b = 4.5;
    seed c;
    c = a + 2;
    reclaim;
}
""")


# ═══════════════════════════════════════════════════════════════════════
# 3. FUNCTION-RELATED ERRORS
# ═══════════════════════════════════════════════════════════════════════
print("\n=== 3. Function-Related Errors ===")

# 3a. Too many arguments
run(expect_error, "3a. Too many arguments", """
pollinate empty foo(seed x) { reclaim; }
root() {
    foo(1, 2);
    reclaim;
}
""", "argument")

# 3b. Too few arguments
run(expect_error, "3b. Too few arguments", """
pollinate empty foo(seed x, seed y) { reclaim; }
root() {
    foo(1);
    reclaim;
}
""", "argument")

# 3c. Argument type mismatch (passing vine where seed expected)
run(expect_error, "3c. Argument type mismatch", """
pollinate empty foo(seed x) { reclaim; }
root() {
    foo("hello");
    reclaim;
}
""", "type")

# 3d. Return type mismatch (function returns vine but declared seed)
run(expect_error, "3d. Return type mismatch", """
pollinate seed foo() {
    reclaim "hello";
}
root() {
    seed x;
    x = foo();
    reclaim;
}
""", "type")

# 3e. Missing return statement on all paths
run(expect_error, "3e. Missing return on all paths", """
pollinate seed foo(seed x) {
    spring (x > 0) {
        reclaim x;
    }
}
root() {
    seed x;
    x = foo(5);
    reclaim;
}
""", "return")

# 3f. Valid function (positive)
run(expect_ok, "3f. Valid function with return", """
pollinate seed add(seed a, seed b) {
    reclaim a + b;
}
root() {
    seed x;
    x = add(3, 4);
    reclaim;
}
""")

# 3g. Bundle return type (new feature)
run(expect_ok, "3g. Bundle return type", """
bundle Pair {
    seed a;
    seed b;
};
pollinate Pair makePair(seed x, seed y) {
    bundle Pair p;
    p.a = x;
    p.b = y;
    reclaim p;
}
root() {
    bundle Pair k;
    k = makePair(3, 4);
    plant(k.a);
    reclaim;
}
""")

# 3h. Bundle parameter type (new feature)
run(expect_ok, "3h. Bundle parameter type", """
bundle Point {
    seed x;
    seed y;
};
pollinate seed sumPoint(Point p) {
    reclaim p.x + p.y;
}
root() {
    bundle Point pt;
    pt.x = 10;
    pt.y = 20;
    seed s;
    s = sumPoint(pt);
    plant(s);
    reclaim;
}
""")

# 3i. empty function must not return value
run(expect_error, "3i. empty func returns value", """
pollinate empty foo() {
    reclaim 5;
}
root() {
    foo();
    reclaim;
}
""", "empty")


# ═══════════════════════════════════════════════════════════════════════
# 4. SCOPE AND VISIBILITY
# ═══════════════════════════════════════════════════════════════════════
print("\n=== 4. Scope and Visibility ===")

# 4a. Variable out of scope (function local not visible externally)
run(expect_error, "4a. Out-of-scope access", """
pollinate empty foo() {
    seed local_var;
    local_var = 10;
    reclaim;
}
root() {
    local_var = 5;
    reclaim;
}
""", "before declaration")

# 4b. Global variable accessible everywhere
run(expect_ok, "4b. Global variable access", """
seed g;
pollinate empty setG() {
    g = 42;
    reclaim;
}
root() {
    setG();
    plant(g);
    reclaim;
}
""")

# 4c. Block scope (if block)
run(expect_ok, "4c. Valid block scope usage", """
root() {
    seed x;
    x = 10;
    spring (x > 5) {
        seed y;
        y = x + 1;
        plant(y);
    }
    reclaim;
}
""")


# ═══════════════════════════════════════════════════════════════════════
# 5. CONTROL FLOW ERRORS
# ═══════════════════════════════════════════════════════════════════════
print("\n=== 5. Control Flow Errors ===")

# 5a. break outside loop
run(expect_error, "5a. prune outside loop", """
root() {
    prune;
    reclaim;
}
""", "prune")

# 5b. continue outside loop
run(expect_error, "5b. skip outside loop", """
root() {
    skip;
    reclaim;
}
""", "skip")

# 5c. Valid break/continue inside loop
run(expect_ok, "5c. Valid prune/skip in loop", """
root() {
    seed i;
    i = 0;
    grow (i < 10) {
        spring (i == 5) {
            prune;
        }
        i++;
    }
    reclaim;
}
""")


# ═══════════════════════════════════════════════════════════════════════
# 6. ARRAY AND POINTER ERRORS
# ═══════════════════════════════════════════════════════════════════════
print("\n=== 6. Array and Pointer Errors ===")

# 6a. Array size must be integer (float literal)
run(expect_error, "6a. Float array size", """
root() {
    seed arr[3.5];
    reclaim;
}
""", "seed")

# 6b. Valid array declaration
run(expect_ok, "6b. Valid array", """
root() {
    seed arr[5];
    arr[0] = 10;
    plant(arr[0]);
    reclaim;
}
""")


# ═══════════════════════════════════════════════════════════════════════
# 7. STRUCT/BUNDLE ERRORS
# ═══════════════════════════════════════════════════════════════════════
print("\n=== 7. Struct/Bundle Errors ===")

# 7a. Access non-existent member
run(expect_error, "7a. Non-existent bundle member", """
bundle Foo {
    seed x;
};
root() {
    bundle Foo f;
    f.z = 5;
    reclaim;
}
""", "member")

# 7b. Use undefined bundle type
run(expect_error, "7b. Undefined bundle type", """
root() {
    bundle Unknown u;
    reclaim;
}
""", "not defined")

# 7c. Duplicate member in bundle
run(expect_error, "7c. Duplicate bundle member", """
bundle Bad {
    seed x;
    seed x;
};
root() { reclaim; }
""", "duplicate")

# 7d. Valid bundle usage
run(expect_ok, "7d. Valid bundle", """
bundle Person {
    seed age;
    vine name;
};
root() {
    bundle Person p;
    p.age = 25;
    p.name = "Alice";
    plant(p.age);
    plant(p.name);
    reclaim;
}
""")

# 7e. Nested bundle
run(expect_ok, "7e. Nested bundle", """
bundle Address {
    seed zip;
};
bundle Person {
    seed age;
    Address addr;
};
root() {
    bundle Person p;
    p.age = 25;
    p.addr.zip = 12345;
    plant(p.addr.zip);
    reclaim;
}
""")


# ═══════════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"RESULTS: {passed}/{total} passed, {failed} failed")
print(f"{'='*60}")
