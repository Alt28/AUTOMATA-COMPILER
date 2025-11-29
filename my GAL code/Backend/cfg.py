from collections import defaultdict

# Use λ (lambda) as epsilon symbol - represents empty/null production
EPSILON = "λ"


def compute_first(cfg):
    """
    Compute FIRST sets for all non-terminals in the grammar.
    
    FIRST(X) = set of terminals that can appear at the beginning 
               of any string derived from X
    
    Example: If X -> aB, then 'a' is in FIRST(X)
    """
    first = defaultdict(set)  # Dictionary to store FIRST sets for each non-terminal
    epsilon = EPSILON

    # Initial pass: Add terminals and epsilon that appear first in productions
    for lhs, productions in cfg.items():  # lhs = left-hand side (non-terminal)
        for prod in productions:  # prod = production (right-hand side)
            if not prod:
                continue
            if prod[0] == epsilon:  # Production derives epsilon directly
                first[lhs].add(epsilon)
            elif prod[0] not in cfg:  # First symbol is a terminal (not a non-terminal)
                first[lhs].add(prod[0])

    # Iterative pass: Keep updating FIRST sets until no changes occur
    changed = True
    while changed:
        changed = False
        for lhs, productions in cfg.items():
            for prod in productions:
                before = len(first[lhs])  # Track size to detect changes

                # Process each symbol in the production
                for symbol in prod:
                    if symbol in cfg:  # Symbol is a non-terminal
                        # Add FIRST(symbol) to FIRST(lhs), excluding epsilon
                        first[lhs] |= (first[symbol] - {epsilon})
                        # If symbol cannot derive epsilon, stop here
                        if epsilon not in first[symbol]:
                            break
                    else:  # Symbol is a terminal
                        if symbol != epsilon:
                            first[lhs].add(symbol)
                        break
                else:
                    # All symbols can derive epsilon, so this production can too
                    first[lhs].add(epsilon)

                # Check if FIRST set grew
                if len(first[lhs]) > before:
                    changed = True

    return first


def compute_follow(cfg, first):
    """
    Compute FOLLOW sets for all non-terminals in the grammar.
    
    FOLLOW(X) = set of terminals that can appear immediately after X
                in any derivation
    
    Example: If S -> AB, then FOLLOW(A) includes FIRST(B)
    """
    follow = defaultdict(set)  # Dictionary to store FOLLOW sets
    epsilon = EPSILON

    # Start symbol gets end-of-input marker ($)
    start_symbol = next(iter(cfg))  # First non-terminal in grammar
    follow[start_symbol].add("$")

    # Iterative pass: Keep updating until no changes
    changed = True
    while changed:
        changed = False
        for lhs, productions in cfg.items():
            for prod in productions:
                # Check each symbol in the production
                for i, symbol in enumerate(prod):
                    if symbol in cfg:  # Only compute FOLLOW for non-terminals
                        before = len(follow[symbol])

                        # Look at what comes after this symbol
                        if i + 1 < len(prod):  # There's a next symbol
                            next_symbol = prod[i + 1]
                            if next_symbol in cfg:  # Next symbol is non-terminal
                                # Add FIRST(next_symbol) to FOLLOW(symbol), excluding epsilon
                                follow[symbol] |= (first[next_symbol] - {epsilon})
                                # If next symbol can be epsilon, also add FOLLOW(lhs)
                                if epsilon in first[next_symbol]:
                                    follow[symbol] |= follow[lhs]
                            else:  # Next symbol is terminal
                                if next_symbol != epsilon:
                                    follow[symbol].add(next_symbol)
                        else:
                            # Symbol is at the end of production
                            # Add FOLLOW(lhs) to FOLLOW(symbol)
                            follow[symbol] |= follow[lhs]

                        # Check if FOLLOW set grew
                        if len(follow[symbol]) > before:
                            changed = True

    return follow


def compute_predict(cfg, first, follow):
    """
    Compute PREDICT sets for all productions in the grammar.
    
    PREDICT(A -> α) = set of terminals that indicate when to use this production
    
    Used to build parsing table for predictive (LL) parser:
    - If next input token is in PREDICT(A -> α), use that production
    
    Rules:
    1. Add FIRST(α) to PREDICT
    2. If α can derive epsilon, also add FOLLOW(A)
    """
    predict = {}  # Dictionary to store PREDICT sets
    epsilon = EPSILON

    for lhs, productions in cfg.items():
        for prod in productions:
            # Key is (non-terminal, production tuple)
            key = (lhs, tuple(prod))
            predict[key] = set()

            # Compute FIRST set of this production
            first_set = set()
            for symbol in prod:
                if symbol in cfg:  # Symbol is non-terminal
                    # Add FIRST(symbol) excluding epsilon
                    first_set |= (first[symbol] - {epsilon})
                    # If symbol cannot derive epsilon, stop
                    if epsilon not in first[symbol]:
                        break
                else:  # Symbol is terminal
                    if symbol != epsilon:
                        first_set.add(symbol)
                    break
            else:
                # All symbols can derive epsilon
                first_set.add(epsilon)

            # PREDICT set starts with FIRST set
            predict[key] = first_set
            # If production can derive epsilon, add FOLLOW(lhs)
            if epsilon in first_set:
                predict[key] |= follow[lhs]

    return predict


# ===============================================================================
# GAL (Grow A Language) Context-Free Grammar Definition
# ===============================================================================
# This dictionary defines the complete grammar for the GAL programming language.
# Format: { "<non-terminal>": [ [production1], [production2], ... ] }
# 
# Non-terminals: Enclosed in < >, represent grammar rules (e.g., <program>)
# Terminals: Actual tokens from the lexer (e.g., "seed", "id", "{")
# λ (EPSILON): Represents empty production (optional/nullable rules)
# ===============================================================================

cfg = {
    # ===== PROGRAM STRUCTURE =====
    # Entry point: Every GAL program must have a root() function
    "<program>": [
        [
            "<global_declaration>",   # Global variables, constants, bundles (structs)
            "<function_definition>",  # User-defined functions
            "root",                   # Main function name (like main() in C)
            "(",
            ")",
            "{",
            "<declaration>",          # Local declarations in root
            "<statement>",            # Statements/code in root
            "reclaim",                # Return statement (required in root)
            ";",
            "}",
        ]
    ],

    # ===== GLOBAL DECLARATIONS =====
    # Variables, constants, and structs declared outside functions
    "<global_declaration>": [
        ["<bundle_declaration>", "<global_declaration>"],  # Struct definition
        ["<var_dec>", ";", "<global_declaration>"],        # Variable declaration
        ["<const_dec>", ";", "<global_declaration>"],      # Constant declaration
        [EPSILON],  # Can be empty (no global declarations)
    ],

    # ===== LOCAL DECLARATIONS =====
    # Variables and constants declared inside functions
    "<declaration>": [
        ["<var_dec>", ";", "<declaration>"],   # Variable declaration
        ["<const_dec>", ";", "<declaration>"], # Constant declaration
        [EPSILON],  # Can be empty (no local declarations)
    ],

    # ===== DATA TYPES =====
    # The four primitive types in GAL
    "<data_type>": [
        ["seed"],    # Integer type
        ["tree"],    # Float/Double type
        ["leaf"],    # Character type
        ["branch"],  # String type
    ],

    # ===== CONSTANT DECLARATIONS =====
    # Example: fertile seed MAX = 100;
    #          fertile leaf NEWLINE = '\n', TAB = '\t';
    "<const_dec>": [
        ["fertile", "<data_type>", "id", "=", "<init_val>", "<const_next>"],
    ],

    "<const_next>": [
        [",", "id", "=", "<init_val>", "<const_next>"],  # Multiple constants in one line
        [EPSILON],  # Single constant
    ],

    # ===== VARIABLE DECLARATIONS =====
    # Examples: seed x = 5;
    #           tree arr[10];
    #           bundle Person p;
    "<var_dec>": [
        ["<data_type>", "id", "<array_dec>", "<var_value>"],  # Regular variable or array
        ["bundle", "id", "<bundle_mem_dec>"],                 # Struct variable
    ],

    "<bundle_mem_dec>": [
        ["id", "<var_value_next>"],         # bundle Person p = {...};
        [",", "id", "<var_value_next>"],    # Multiple struct variables
        [EPSILON],                           # Just declaration without initialization
    ],

    "<var_value>": [
        ["=", "<init_val>", "<var_value_next>"],  # With initialization
        [EPSILON],                                 # Without initialization
    ],

    "<var_value_next>": [
        [",", "id", "<array_dec>", "<var_value_next>"],  # Multiple variables: seed x, y, z;
        [EPSILON],
    ],

    # ===== INITIALIZATION VALUES =====
    "<init_val>": [
        ["<expression>"],      # Single value: seed x = 5 + 3;
        ["<array_init_opt>"],  # Array initialization: seed arr[] = {1, 2, 3};
    ],

    # ===== ARRAY DECLARATIONS =====
    # Examples: seed arr[10];    (fixed size)
    #           tree vals[];     (dynamic size)
    "<array_dec>": [
        ["[", "<array_dim_opt>", "]"],  # With or without size
        ["[", "]"],                      # Empty brackets (dynamic)
    ],

    "<array_dim_opt>": [
        ["intlit"],  # Size specified: [10]
        [EPSILON],   # Size not specified: []
    ],

    # ===== ARRAY INITIALIZATION =====
    # Examples: {1, 2, 3}
    #           {{1, 2}, {3, 4}}  (nested arrays)
    "<array_init_opt>": [
        ["{", "<init_vals>", "}"],  # Array initializer
        [EPSILON],                   # No initialization
    ],

    "<init_vals>": [
        ["<arguments>"],                      # Simple list: {1, 2, 3}
        ["<arguments>", ",", "<nested_init>"], # Nested: {1, {2, 3}}
    ],

    "<nested_init>": [
        ["{", "<arguments>", "}"],                         # Single nested: {1, 2}
        ["{", "<arguments>", "}", ",", "<nested_init>"],   # Multiple nested
    ],

    # ===== STRUCT (BUNDLE) DECLARATIONS =====
    # Example: bundle Person {
    #              seed age;
    #              branch name;
    #          }
    "<bundle_declaration>": [
        ["bundle", "id", "{", "<bundle_members>", "}"],
    ],

    "<bundle_members>": [
        ["<data_type>", "id", ";", "<bundle_members>"],  # Member fields
        [EPSILON],                                        # Empty struct or end of members
    ],

    # ===== FUNCTION DEFINITIONS =====
    # Example: pollinate seed add(seed a, seed b) {
    #              reclaim a + b;
    #          }
    "<function_definition>": [
        [
            "pollinate",           # Keyword for function definition
            "<return_type>",       # Return type (seed, tree, leaf, branch, or empty)
            "id",                  # Function name
            "(",
            "<parameters>",        # Parameter list
            ")",
            "{",
            "<declaration>",       # Local variable declarations
            "<statement>",         # Function body statements
            "<reclaim_opt>",       # Return statement (optional for void/empty)
            "}",
            "<function_definition>",  # Multiple functions (recursive definition)
        ],
        [EPSILON],  # No more functions
    ],

    # ===== RETURN TYPE =====
    "<return_type>": [
        ["<data_type>"],  # Returns seed, tree, leaf, or branch
        ["empty"],        # Void function (no return value)
    ],

    # ===== FUNCTION PARAMETERS =====
    # Examples: (seed x, tree y)
    #           ()  (no parameters)
    "<parameters>": [
        [EPSILON],                      # No parameters
        ["<param>", "<param_next>"],    # One or more parameters
    ],

    "<param>": [
        ["<data_type>", "id"],  # Parameter: type + name
    ],

    "<param_next>": [
        [EPSILON],                           # Last parameter
        [",", "<param>", "<param_next>"],    # More parameters
    ],

    # ===== RETURN STATEMENT =====
    # Examples: reclaim x + y;
    #           reclaim;  (for empty functions)
    "<reclaim_opt>": [
        ["reclaim", "<expression>", ";"],  # Return with value
        ["reclaim", ";"],                  # Return without value
        [EPSILON],                         # No return (optional in some cases)
    ],

    # ===== STATEMENTS =====
    # A sequence of statements (one or more, or none)
    "<statement>": [
        ["<simple_stmt>", "<statement>"],  # One statement followed by more
        [EPSILON],                         # No more statements
    ],

    # ===== TYPES OF STATEMENTS =====
    "<simple_stmt>": [
        ["<assignment_stmt>"],    # x = 5;
        ["<unary_stmt>"],         # x++; or x--;
        ["<io_stmt>"],            # water() or plant()
        ["<function_call>"],      # myFunc();
        ["<conditional_stmt>"],   # spring (if), wither (else), bud (else-if)
        ["<loop_stmt>"],          # grow (while), cultivate (for), tend (do-while)
        ["<switch_stmt>"],        # harvest (switch)
        ["<control_stmt>"],       # prune (break), skip (continue)
    ],

    # ===== ASSIGNMENT STATEMENTS =====
    # Examples: x = 10;
    #           arr[0] = 5;
    #           person.age = 25;
    #           total += 5;
    "<assignment_stmt>": [
        ["<value>", "<assign_op>", "<expression>", ";"],
    ],

    # Assignment operators
    "<assign_op>": [
        ["="],   # Simple assignment
        ["+="],  # Add and assign
        ["-="],  # Subtract and assign
        ["*="],  # Multiply and assign
        ["/="],  # Divide and assign
        ["%="],  # Modulo and assign
    ],

    # Left-hand side of assignment (variable, array element, or struct member)
    "<value>": [
        ["id", "<id_next>"],  # Variable name with optional array/struct access
    ],

    "<id_next>": [
        ["<array_access>"],   # Array indexing: arr[0]
        ["<struct_access>"],  # Struct member: person.name
        [EPSILON],            # Just a simple variable: x
    ],

    # ===== ARRAY ACCESS =====
    # Examples: arr[0]
    #           matrix[i][j]  (multi-dimensional)
    "<array_access>": [
        ["[", "<expression>", "]", "<array_access_more>"],
    ],

    "<array_access_more>": [
        ["[", "<expression>", "]", "<array_access_more>"],  # Additional dimensions
        [EPSILON],                                           # End of array indexing
    ],

    # ===== STRUCT/BUNDLE ACCESS =====
    # Examples: person.name
    #           person.address.city  (nested structs)
    "<struct_access>": [
        [".", "id", "<struct_access_more>"],
    ],

    "<struct_access_more>": [
        [".", "id", "<struct_access_more>"],  # Nested member access
        [EPSILON],                             # End of member access
    ],

    # ===== INPUT/OUTPUT STATEMENTS =====
    # water() - output/print function
    # plant() - input/read function
    # Examples: water("Hello");
    #           plant(x, y, z);
    "<io_stmt>": [
        ["water", "(", "<arguments>", ")", ";"],  # Output
        ["plant", "(", "<arguments>", ")", ";"],  # Input
    ],

    # Argument list for function calls and I/O
    "<arguments>": [
        ["<expression>", "<arg_next>"],  # One or more arguments
        [EPSILON],                        # No arguments
    ],

    "<arg_next>": [
        [",", "<expression>", "<arg_next>"],  # More arguments
        [EPSILON],                             # Last argument
    ],

    # ===== CONDITIONAL STATEMENTS =====
    # spring = if
    # bud = else if
    # wither = else
    # 
    # Example: spring (x > 0) {
    #              water("positive");
    #          }
    #          bud (x < 0) {
    #              water("negative");
    #          }
    #          wither {
    #              water("zero");
    #          }
    "<conditional_stmt>": [
        [
            "spring",              # if keyword
            "(",
            "<expression>",        # condition
            ")",
            "{",
            "<statement>",         # if body
            "}",
            "<elseif_chain>",      # else-if chain (optional)
            "<else_opt>",          # else clause (optional)
        ]
    ],

    "<elseif_chain>": [
        [
            "bud",                 # else-if keyword
            "(",
            "<expression>",        # condition
            ")",
            "{",
            "<statement>",         # else-if body
            "}",
            "<elseif_chain>",      # More else-ifs
        ],
        [EPSILON],  # No else-if
    ],

    "<else_opt>": [
        ["wither", "{", "<statement>", "}"],  # else clause
        [EPSILON],                             # No else
    ],

    # ===== LOOP STATEMENTS =====
    # grow = while loop
    # cultivate = for loop
    # tend = do-while loop
    "<loop_stmt>": [
        # While loop: grow (x < 10) { ... }
        ["grow", "(", "<expression>", ")", "{", "<statement>", "}"],
        
        # For loop: cultivate (seed i = 0; i < 10; i++) { ... }
        [
            "cultivate",
            "(",
            "<for_init>",          # Initialization
            ";",
            "<expression>",        # Condition
            ";",
            "<for_update>",        # Update
            ")",
            "{",
            "<statement>",
            "}",
        ],
        
        # Do-while: tend ( ... x < 10);
        ["tend", "(", "<statement>", "<expression>", ")", ";"],
    ],

    "<for_init>": [
        ["<assignment_stmt>"],  # seed i = 0
        [EPSILON],              # Empty initialization
    ],

    "<for_update>": [
        ["<assignment_stmt>"],  # i = i + 1
        ["<unary_stmt>"],       # i++
        [EPSILON],              # Empty update
    ],

    # ===== UNARY STATEMENTS =====
    # Examples: x++;  y--;
    "<unary_stmt>": [
        ["id", "<unary_op>", ";"],
    ],

    "<unary_op>": [
        ["++"],  # Increment
        ["--"],  # Decrement
    ],

    # ===== SWITCH STATEMENT =====
    # harvest = switch
    # variety = case
    # soil = default
    # prune = break (required after each case)
    #
    # Example: harvest (choice) {
    #              variety (1): water("One"); prune;
    #              variety (2): water("Two"); prune;
    #              soil: water("Default");
    #          }
    "<switch_stmt>": [
        ["harvest", "(", "<expression>", ")", "{", "<case_list>", "<default_opt>", "}"],
    ],

    "<case_list>": [
        [
            "variety",             # case keyword
            "(",
            "<expression>",        # case value
            ")",
            ":",
            "<statement>",         # case body
            "prune",               # break (required)
            ";",
            "<case_list>",         # More cases
        ],
        [EPSILON],  # No more cases
    ],

    "<default_opt>": [
        ["soil", ":", "<statement>"],  # default case
        [EPSILON],                      # No default
    ],

    # ===== CONTROL FLOW STATEMENTS =====
    "<control_stmt>": [
        ["prune", ";"],  # break
        ["skip", ";"],   # continue
    ],

    # ===== FUNCTION CALL =====
    # Example: myFunc(x, y, z);
    "<function_call>": [
        ["id", "(", "<arguments>", ")", ";"],
    ],

    # ===== EXPRESSIONS =====
    # Expressions follow operator precedence (lowest to highest):
    # 1. Logical OR (||)
    # 2. Logical AND (&&)
    # 3. Relational (>, <, >=, <=, ==, !=)
    # 4. Arithmetic (+, -)
    # 5. Term (*, /, %)
    # 6. Factor (literals, variables, function calls, parentheses)
    
    # Level 1: Logical OR (lowest precedence)
    # Example: a || b || c
    "<expression>": [
        ["<logic_or>", "<logic_or_next>"],
    ],

    "<logic_or>": [
        ["<logic_and>", "<logic_and_next>"],
    ],

    "<logic_or_next>": [
        ["||", "<logic_and>", "<logic_or_next>"],  # More OR operations
        [EPSILON],                                  # End
    ],

    # Level 2: Logical AND
    # Example: a && b && c
    "<logic_and>": [
        ["<relational>", "<logic_and_next>"],
    ],

    "<logic_and_next>": [
        ["&&", "<relational>", "<logic_and_next>"],  # More AND operations
        [EPSILON],                                    # End
    ],

    # Level 3: Relational operators
    # Example: a > b, x == y
    "<relational>": [
        ["<arithmetic>", "<relational_op>", "<arithmetic>"],  # Comparison
        ["<arithmetic>"],                                      # Just arithmetic
    ],

    "<relational_op>": [
        [">"],   # Greater than
        ["<"],   # Less than
        [">="],  # Greater than or equal
        ["<="],  # Less than or equal
        ["=="],  # Equal
        ["!="],  # Not equal
    ],

    # Level 4: Arithmetic (addition/subtraction)
    # Example: a + b - c
    "<arithmetic>": [
        ["<term>", "<arithmetic_next>"],
    ],

    "<arithmetic_next>": [
        ["+", "<term>", "<arithmetic_next>"],  # Addition
        ["-", "<term>", "<arithmetic_next>"],  # Subtraction
        [EPSILON],                              # End
    ],

    # Level 5: Term (multiplication/division/modulo)
    # Example: a * b / c % d
    "<term>": [
        ["<factor>", "<term_next>"],
    ],

    "<term_next>": [
        ["*", "<factor>", "<term_next>"],  # Multiplication
        ["/", "<factor>", "<term_next>"],  # Division
        ["%", "<factor>", "<term_next>"],  # Modulo
        [EPSILON],                          # End
    ],

    # Level 6: Factor (highest precedence - literals, variables, etc.)
    "<factor>": [
        ["(", "<expression>", ")"],      # Parenthesized expression
        ["id", "<factor_id_next>"],      # Variable, array, struct, or function
        ["intlit"],                      # Integer literal (e.g., 42)
        ["dblit"],                       # Double/float literal (e.g., 3.14)
        ["chlit"],                       # Character literal (e.g., 'a')
        ["strlit"],                      # String literal (e.g., "hello")
        ["sunshine"],                    # Boolean true
        ["frost"],                       # Boolean false
    ],

    # For identifiers in expressions - could be variable, array, struct, or function
    "<factor_id_next>": [
        ["<array_access>"],   # Array element: arr[0]
        ["<struct_access>"],  # Struct member: person.name
        [EPSILON],            # Simple variable: x
    ],
}


# ===============================================================================
# COMPUTE FIRST, FOLLOW, AND PREDICT SETS
# ===============================================================================
# These sets are used for building a predictive (LL) parser


# Compute the FIRST, FOLLOW, and PREDICT sets
first_sets = compute_first(cfg)
follow_sets = compute_follow(cfg, first_sets)
predict_sets = compute_predict(cfg, first_sets, follow_sets)


# ===============================================================================
# OUTPUT: Display the computed sets
# ===============================================================================

print("=" * 80)
print("FIRST SETS")
print("=" * 80)
print("Shows which terminals can appear first in each non-terminal")
print()
for nt in first_sets:
    print(f"First({nt}) = {{ {', '.join(sorted(first_sets[nt]))} }}")

print("\n" + "=" * 80)
print("FOLLOW SETS")
print("=" * 80)
print("Shows which terminals can appear after each non-terminal")
print()
for nt in follow_sets:
    print(f"Follow({nt}) = {{ {', '.join(sorted(follow_sets[nt]))} }}")

print("\n" + "=" * 80)
print("PREDICT SETS")
print("=" * 80)
print("Shows which terminal triggers each production rule")
print()
for (lhs, prod), pset in predict_sets.items():
    prod_str = " ".join(prod)
    print(f"Predict({lhs} -> {prod_str}) = {{ {', '.join(sorted(pset))} }}")

print("\n" + "=" * 80)
