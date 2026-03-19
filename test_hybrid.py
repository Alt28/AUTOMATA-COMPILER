"""Test the 3-layer hybrid fallback system."""
import sys, re
sys.path.insert(0, "Backend")
import gal_fallback as fb

passed = 0
failed = 0

def check(label, msg, expect_pattern):
    global passed, failed
    result = fb._rule_engine_match(msg) if "RULE" in label else fb.fallback_reply(msg)
    if result is None:
        ok = False
    else:
        ok = re.search(expect_pattern, result, re.I) is not None
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"  {status}: {label}")
        if result:
            print(f"    GOT: {result[:120]}")
        else:
            print(f"    GOT: None")
        return
    print(f"  {status}: {label}")

print("=" * 60)
print("RULE ENGINE TESTS (Layer 1)")
print("=" * 60)

# Lexer errors
check("RULE: identifier too long",
      "Identifier exceeds maximum length of 15 characters",
      r"Lexical Analysis")
check("RULE: integer too long",
      "Integer exceeds maximum of 8 digits",
      r"8 digits")
check("RULE: missing string close",
      "Missing closing '\"' for string literal",
      r"closing double quote")
check("RULE: illegal char",
      "Illegal Character '@'",
      r"not valid in GAL")
check("RULE: identifier starts with number",
      "Identifiers cannot start with a number",
      r"start with a letter")
check("RULE: invalid escape",
      "Invalid escape sequence",
      r"Valid escapes")
check("RULE: unclosed comment",
      "Missing closing '*/' for multi-line comment",
      r"never closed")

# Parser errors
check("RULE: === operator",
      "'===' is not valid in GAL. Use '==' for comparison.",
      r"Syntax Analysis")
check("RULE: single & operator",
      "'&' is not valid in GAL. Use '&&' for logical AND.",
      r"logical AND")
check("RULE: C keyword mistake",
      "'if' is not a GAL keyword. Use 'spring' instead.",
      r"not a GAL keyword")
check("RULE: missing semicolon",
      "Unexpected token 'seed'. Expected ';'.",
      r"semicolon")
check("RULE: missing closing brace",
      "Missing closing brace",
      r"closing brace")
check("RULE: empty block",
      "Empty block. Expected at least one statement inside braces.",
      r"at least one statement")
check("RULE: unreachable code",
      "Unreachable code after 'reclaim'",
      r"never execute")
check("RULE: chained increment",
      "Increment/decrement operators cannot be chained.",
      r"chained")
check("RULE: missing return type",
      "Missing return type after 'pollinate'. 'add' was parsed as the return type.",
      r"return type")
check("RULE: missing param type",
      "Missing type for parameter 'x'.",
      r"type")
check("RULE: code after program",
      "Unexpected token 'seed' after program end.",
      r"inside functions")
check("RULE: type mismatch decl",
      "Type mismatch in declaration of 'x': variable declared as 'seed' but assigned 'stringlit' value(s).",
      r"match")

# Semantic errors
check("RULE: variable already declared",
      "Semantic Error: Variable 'x' already declared.",
      r"already been declared")
check("RULE: variable used before decl",
      "Semantic Error: Variable 'x' used before declaration.",
      r"before being declared")
check("RULE: type mismatch assign",
      "Semantic Error: Type Mismatch! Cannot assign vine to variable 'x' of type seed.",
      r"Semantic Analysis")
check("RULE: modulo requires seed",
      "Semantic Error: Modulo operator '%' requires 'seed' (integer) operands.",
      r"integer")
check("RULE: ! only on branch",
      "'!' operator can only be used with 'branch' (boolean) values.",
      r"branch")
check("RULE: function not defined",
      "Semantic Error: Function 'myFunc' is not defined.",
      r"never defined")
check("RULE: function arg count",
      "Semantic Error: Function 'add' expects 2 argument(s), got 3.",
      r"expects 2")
check("RULE: empty func return",
      "empty function must not return any value.",
      r"reclaim.*without a value")
check("RULE: must end with reclaim",
      "Semantic Error: Function 'test' must end with 'reclaim'.",
      r"missing.*reclaim")
check("RULE: prune outside loop",
      "'prune' used outside a loop or switch.",
      r"only.*inside")
check("RULE: skip outside loop",
      "'skip' used outside a loop.",
      r"only.*inside")
check("RULE: fertile reassign",
      "Variable 'MAX' is declared as fertile and cannot be re-assigned a value.",
      r"fertile.*cannot")
check("RULE: fertile must init",
      "Fertile variables must be initialized.",
      r"must be assigned")
check("RULE: condition must be branch",
      "spring condition must be branch, got seed.",
      r"boolean")
check("RULE: harvest wrong type",
      "'harvest' expression must be 'seed'/'leaf'/'branch', not 'vine'.",
      r"seed.*leaf.*branch")
check("RULE: duplicate variety",
      "Duplicate 'variety' value",
      r"unique")
check("RULE: bundle not defined",
      "Bundle type 'Point' is not defined.",
      r"must be defined")
check("RULE: ts wrong type",
      "'ts()' can only be used on lists or vines.",
      r"arrays.*vine")
check("RULE: plant placeholder",
      "Found 3 argument(s). Expected 2 argument(s).",
      r"placeholder")

# Runtime errors
check("RULE: division by zero",
      "Runtime Error: Division by zero is undefined",
      r"Runtime.*Interpreter")
check("RULE: infinite loop",
      "Runtime Error: Infinite loop detected!",
      r"10.000")
check("RULE: index out of bounds",
      "Runtime Error: Index '5' out of bounds for list 'arr'",
      r"0.*length")
check("RULE: number exceeds 16",
      "Evaluated number exceeds maximum number of 16 digits",
      r"16")
check("RULE: condition not boolean",
      "Condition must be a boolean. Got '42'",
      r"sunshine.*frost")
check("RULE: not a list",
      "Variable 'x' is not a list",
      r"only arrays")

print()
print("=" * 60)
print("RETRIEVER TESTS (Layer 2)")
print("=" * 60)

# Original topics
check("KB: data types", "what are the data types in GAL?", r"(?s)seed.*tree.*leaf.*vine.*branch")
check("KB: variables", "how do I declare a variable?", r"seed|tree|vine|leaf|branch")
check("KB: arrays", "how to use arrays?", r"arr\[")
check("KB: for loop", "what is cultivate?", r"cultivate")
check("KB: while loop", "explain the grow loop", r"grow")
check("KB: do-while", "how does tend work?", r"tend.*grow")
check("KB: if/else", "how to use spring bud wither?", r"spring|bud|wither")
check("KB: switch", "explain harvest variety soil", r"harvest|variety|soil")
check("KB: functions", "how to create a function?", r"pollinate")
check("KB: input", "how to read user input?", r"water")
check("KB: output", "how to print output?", r"plant")
check("KB: bundles", "how to create a struct?", r"bundle")
check("KB: operators", "what operators does GAL have?", r"\+.*\-.*\*")
check("KB: keywords", "show me the keyword reference", r"GAL.*C Equivalent|Keyword Reference")
check("KB: example", "show me a sample program", r"root\(\)")
check("KB: C to GAL", "how to convert C code to GAL?", r"seed|tree|leaf")
check("KB: comments", "how to write comments?", r"//|/\*")
check("KB: identifiers", "what are the identifier rules?", r"15 characters")
check("KB: type casting", "how to cast types?", r"\(seed\)|\(tree\)")
check("KB: array builtins", "how to append to an array?", r"append")
check("KB: escape sequences", "what escape sequences exist?", r"\\\\n|Newline")
check("KB: string concat", "how to concatenate strings?", r"backtick|concat")

# New topics (25-54)
check("KB: program structure", "how to organize a GAL program?", r"root|global|pollinate")
check("KB: scope", "what are the scope rules?", r"local|global|scope")
check("KB: constants", "how to make a constant?", r"fertile")
check("KB: booleans", "what is sunshine and frost?", r"sunshine.*true|frost.*false")
check("KB: return types", "what function return types exist?", r"empty|seed|tree")
check("KB: recursion", "how to write a recursive function?", r"factorial|recursive|calls itself")
check("KB: nested if", "nested if statements", r"nested|spring.*spring")
check("KB: prune skip", "how to break out of a loop?", r"prune|break")
check("KB: nested loops", "loop inside a loop", r"nested|inner.*outer")
check("KB: 2D arrays", "how to use a 2D array?", r"matrix|\[.*\]\[.*\]")
check("KB: array of bundles", "array of structs", r"bundle.*arr|class\[")
check("KB: nested bundles", "nested bundle struct fields", r"nested|addr\.city")
check("KB: TS function", "how to get array length?", r"TS\(|length")
check("KB: taper function", "split string to characters", r"taper")
check("KB: precedence", "what is the operator precedence?", r"priority|highest|lowest")
check("KB: increment", "difference between i++ and ++i", r"prefix|postfix")
check("KB: tilde", "how to make a negative number?", r"tilde|~")
check("KB: compound assign", "what does += do?", r"\+=|compound")
check("KB: format strings", "how to use format strings in plant?", r"\{\}|placeholder")
check("KB: limits", "what are GAL's limits?", r"15 characters|10.000|8 digits")
check("KB: compiler stages", "how does the GAL compiler work?", r"Lexer|Parser|Semantic|Interpreter")
check("KB: missing semicolon", "where do I put semicolons?", r"semicolon|;")
check("KB: type mismatch", "type mismatch error help", r"compatible|incompatible|seed.*tree")
check("KB: undeclared var", "variable not declared error", r"declare|before use")
check("KB: wrong keywords", "I used C keywords instead of GAL", r"spring|cultivate|keyword")
check("KB: fertile errors", "constant error fertile", r"fertile|cannot|reassign")
check("KB: factorial example", "factorial program example", r"factorial")
check("KB: array ops example", "array sum example", r"sum|arr")
check("KB: bubble sort", "sort an array", r"sort|bubble|swap")
check("KB: bundle example", "complete bundle usage example", r"bundle|Student")

# Greeting tests
check("KB: greeting", "Hello!", r"Hey there|GAL AI")
check("KB: thanks", "thank you", r"welcome")
check("KB: bye", "bye", r"Goodbye")

print()
print("=" * 60)
total = passed + failed
print(f"TOTAL: {passed}/{total} passed ({100*passed//total}%)")
if failed:
    print(f"  {failed} test(s) failed")
else:
    print("  ALL TESTS PASSED!")
