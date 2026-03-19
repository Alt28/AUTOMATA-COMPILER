import sys
sys.path.insert(0, 'Backend')
from lexer import Lexer
from Gal_Parser import LL1Parser
from cfg import cfg, first_sets, predict_sets

with open('test_fib.gal', 'r') as f:
    code = f.read()

lexer = Lexer(code)
tokens, lex_errors = lexer.make_tokens()
if lex_errors:
    print('LEXER ERRORS:')
    for e in lex_errors:
        print(f'  {e}')
else:
    print(f'Lexer OK: {len(tokens)} tokens')
    parser = LL1Parser(
        cfg=cfg,
        predict_sets=predict_sets,
        first_sets=first_sets,
        start_symbol="<program>",
        end_marker="EOF",
        skip_token_types={'\n'}
    )
    parse_success, parse_errors = parser.parse(tokens)
    if parse_errors:
        print('PARSE ERRORS:')
        for e in parse_errors:
            print(f'  {e}')
    else:
        print(f'Parser OK: success={parse_success}')
        result = parser.parse_and_build(tokens)
        if not result['success']:
            print('AST/SEMANTIC ERRORS:')
            for e in result['errors']:
                print(f'  {e}')
        else:
            print('AST build OK')
            print(f'Symbol table functions: {list(result["symbol_table"].get("functions", {}).keys())}')
