"""
Parser error‑message tests.
Each test prints the error output so you can verify
the 'Expected:' list is human-readable and derived from the predict set.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

from cfg import cfg, first_sets, predict_sets
from Gal_Parser import LL1Parser
from lexer import lex

parser = LL1Parser(
    cfg=cfg,
    predict_sets=predict_sets,
    first_sets=first_sets,
    start_symbol="<program>",
    end_marker="EOF",
    skip_token_types={'\n'},
)

# ── helpers ──────────────────────────────────────────────────────────
def run(label: str, code: str, expect_pass: bool = False):
    tokens, lex_errs = lex(code)
    ok, errs = parser.parse(tokens)
    status = "PASS" if ok else "FAIL"
    icon = "✓" if ok == expect_pass else "✗"
    print(f"[{icon}] {label}  ({status})")
    for e in lex_errs:
        print(f"     LEX : {e}")
    for e in errs:
        print(f"     PARSE: {e}")
    print()

# ── VALID programs (should PASS) ────────────────────────────────────
run("1. Minimal valid program",
    "root() {\n    reclaim;\n}",
    expect_pass=True)

run("2. Global variable + output",
    "seed x;\nroot() {\n    x = 5;\n    plant(x);\n    reclaim;\n}",
    expect_pass=True)

run("3. All data types",
    ("seed a;\ntree b;\nleaf c;\nbranch d;\nvine e;\n"
     "root() {\n    a = 1;\n    b = 3.14;\n    c = 'Z';\n"
     "    d = sunshine;\n    e = \"hi\";\n    reclaim;\n}"),
    expect_pass=True)

run("4. Conditional (spring / wither)",
    ("seed x;\nroot() {\n    x = 10;\n"
     "    spring (x > 5) {\n        plant(x);\n    } wither {\n        plant(0);\n    }\n"
     "    reclaim;\n}"),
    expect_pass=True)

run("5. Loop (grow)",
    ("seed i;\nroot() {\n"
     "    grow (i = 0; i < 5; i++) {\n        plant(i);\n    }\n"
     "    reclaim;\n}"),
    expect_pass=True)

# ── ERROR programs (should FAIL with clear Expected) ────────────────

run("6. Missing semicolon after assignment",
    "seed x;\nroot() {\n    x = 5\n    reclaim;\n}")

run("7. Wrong keyword: 'if' instead of 'spring'",
    "root() {\n    if (sunshine) {\n        plant(1);\n    }\n    reclaim;\n}")

run("8. Missing 'reclaim' at end of root",
    "root() {\n    seed x = 5;\n}")

run("9. Type mismatch: double to seed",
    "root() {\n    seed x = 3.14;\n    reclaim;\n}")

run("10. Unexpected token in expression (==)",
    "seed x;\nroot() {\n    x = ==;\n    reclaim;\n}")

run("11. Invalid operator '==='",
    "seed x;\nroot() {\n    x === 5;\n    reclaim;\n}")

run("12. Missing closing parenthesis",
    "seed x;\nroot() {\n    spring (x == 5 {\n        plant(x);\n    }\n    reclaim;\n}")

run("13. Empty block in spring",
    "seed x;\nroot() {\n    spring (x == 5) {\n    }\n    reclaim;\n}")

run("14. Extra code after program end",
    "root() {\n    reclaim;\n}\nseed extra;")

run("15. Single '&' instead of '&&'",
    "branch a;\nroot() {\n    a = sunshine & frost;\n    reclaim;\n}")

run("16. Unary minus (not supported)",
    "seed x;\nroot() {\n    x = -5;\n    reclaim;\n}")

run("17. Missing opening brace after spring",
    "seed x;\nroot() {\n    spring (x == 1)\n        plant(x);\n    reclaim;\n}")

run("18. Using C keyword 'int' instead of 'seed'",
    "root() {\n    int x = 5;\n    reclaim;\n}")

run("19. Missing value after '='",
    "seed x;\nroot() {\n    x = ;\n    reclaim;\n}")

run("20. Identifier after identifier (missing operator)",
    "seed x;\nseed y;\nroot() {\n    x = x y;\n    reclaim;\n}")
