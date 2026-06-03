"""LL(1) syntax checker for GAL.

The parser receives lexer tokens, consults the CFG/PREDICT table, and only
calls builder.py to create the AST after the token stream is syntactically valid.
"""

# AUTO: Imports names from another module.
from __future__ import annotations

# AUTO: Imports names from another module.
from dataclasses import dataclass
# AUTO: Imports names from another module.
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

# AUTO: Imports names from another module.
from .builder import (
    # AUTO: Executes this statement.
    build_ast as _build_ast,
    # AUTO: Executes this statement.
    symbol_table as _builder_st,
# AUTO: Closes the current grouped code/data.
)
# AUTO: Imports names from another module.
from semantic.errors import SemanticError as _SemanticError


# AUTO: Attaches this decorator to the next function/class.
@dataclass(frozen=True)
# AUTO: Defines class `_TokView`.
class _TokView:
    # GUIDE: Lightweight token shape used internally so parser input can be Token
    # objects or dictionaries from API tests.
    # AUTO: Executes this statement.
    type: str
    # AUTO: Executes this statement.
    value: str
    # AUTO: Executes this statement.
    line: int
    # AUTO: Sets `col: int`.
    col: int = 0


# AUTO: Defines function `_as_tok`.
def _as_tok(token: Any) -> _TokView:
    # LINE: Accept dictionary tokens from API/tests.
    if isinstance(token, Mapping):
        # AUTO: Returns this result to the caller.
        return _TokView(
            # AUTO: Sets `type`.
            type=str(token.get("type", "")),
            # AUTO: Sets `value`.
            value=str(token.get("value", "")),
            # AUTO: Sets `line`.
            line=int(token.get("line", 0) or 0),
            # AUTO: Sets `col`.
            col=int(token.get("col", 0) or 0),
        # AUTO: Closes the current grouped code/data.
        )
    # LINE: Accept Token objects from the lexer.
    return _TokView(
        # AUTO: Sets `type`.
        type=str(getattr(token, "type", "")),
        # AUTO: Sets `value`.
        value=str(getattr(token, "value", "")),
        # AUTO: Sets `line`.
        line=int(getattr(token, "line", 0) or 0),
        # AUTO: Sets `col`.
        col=int(getattr(token, "col", 0) or 0),
    # AUTO: Closes the current grouped code/data.
    )


# AUTO: Defines class `LL1Parser`.
class LL1Parser:
    # AUTO: Defines function `__init__`.
    def __init__(
        # AUTO: Executes this statement.
        self,
        # AUTO: Executes this statement.
        cfg: Dict[str, List[List[str]]],
        # AUTO: Executes this statement.
        predict_sets: Dict[Tuple[str, Tuple[str, ...]], Set[str]],
        # AUTO: Executes this statement.
        first_sets: Dict[str, Set[str]],
        # AUTO: Executes this statement.
        *,
        # AUTO: Sets `start_symbol: str`.
        start_symbol: str = "<program>",
        # AUTO: Sets `end_marker: str`.
        end_marker: str = "EOF",
        # AUTO: Sets `epsilon_symbols: Iterable[str]`.
        epsilon_symbols: Iterable[str] = ("λ", "ε"),
        # AUTO: Sets `skip_token_types: Optional[Set[str]]`.
        skip_token_types: Optional[Set[str]] = None,
        # AUTO: Sets `token_type_alias: Optional[Dict[str, str]]`.
        token_type_alias: Optional[Dict[str, str]] = None,
    # AUTO: Closes the current grouped code/data.
    ):
        # AUTO: Sets `self.cfg`.
        self.cfg = cfg
        # AUTO: Sets `self.predict_sets`.
        self.predict_sets = predict_sets
        # AUTO: Sets `self.first_sets`.
        self.first_sets = first_sets

        # AUTO: Sets `self.epsilon_symbols: Set[str]`.
        self.epsilon_symbols: Set[str] = set(epsilon_symbols)
        # AUTO: Sets `self.start_symbol`.
        self.start_symbol = start_symbol
        # AUTO: Sets `self.end_marker`.
        self.end_marker = end_marker

        # Comments ('comment' = //..., 'mcommentlit' = /*...*/) are emitted by
        # the lexer for the lexeme table but are not grammar tokens, so the
        # parser skips them just like newlines.
        # AUTO: Sets `self.skip_token_types: Set[str]`.
        self.skip_token_types: Set[str] = set(skip_token_types or {"\n", "comment", "mcommentlit"})
        # AUTO: Sets `self.token_type_alias`.
        self.token_type_alias = token_type_alias or {
            # AUTO: Executes this statement.
            'idf': 'id',
            # AUTO: Executes this statement.
            'dbllit': 'dblit',
        # AUTO: Closes the current grouped code/data.
        }
        
        # AUTO: Sets `self.parsing_table: Dict[str, Dict[str, List[str]]]`.
        self.parsing_table: Dict[str, Dict[str, List[str]]] = self.construct_parsing_table()

    # AUTO: Defines function `construct_parsing_table`.
    def construct_parsing_table(self) -> Dict[str, Dict[str, List[str]]]:
        # GUIDE: Convert PREDICT sets into table[non_terminal][lookahead] = production.
        # LINE: table maps each non-terminal and lookahead token to one CFG rule.
        table: Dict[str, Dict[str, List[str]]] = {}

        # LINE: Visit every non-terminal in the grammar.
        for non_terminal, productions in self.cfg.items():
            # LINE: row stores all lookahead choices for this non-terminal.
            row: Dict[str, List[str]] = {}
            # LINE: Visit every production under the current non-terminal.
            for production in productions:
                # LINE: This key matches how predict_sets stores each production.
                key = (non_terminal, tuple(production))
                # LINE: terms are the lookahead terminals that choose this production.
                terms = self.predict_sets.get(key, set())
                # LINE: Fill the parse table for each lookahead terminal.
                for terminal in terms:
                    # AUTO: Checks this condition.
                    if terminal in row and row[terminal] != production:
                        # LINE: A conflict means the grammar is not LL(1) here.
                        raise ValueError(
                            # AUTO: Executes this statement.
                            f"LL(1) conflict at {non_terminal} with lookahead {terminal}: "
                            # AUTO: Executes this statement.
                            f"{row[terminal]} vs {production}"
                        # AUTO: Closes the current grouped code/data.
                        )
                    # AUTO: Sets `row[terminal]`.
                    row[terminal] = production
            # LINE: Save this non-terminal row in the final parsing table.
            table[non_terminal] = row
        # LINE: Return the completed LL(1) parse table.
        return table


    # AUTO: Defines function `_normalize_token_type`.
    def _normalize_token_type(self, token_type: str) -> str:
        # LINE: Convert lexer aliases like idf/dbllit into grammar names.
        return self.token_type_alias.get(token_type, token_type)

    # AUTO: Defines function `_ensure_eof`.
    def _ensure_eof(self, toks: List[_TokView]) -> List[_TokView]:
        # LINE: Empty input still needs EOF so parser can stop cleanly.
        if not toks:
            # AUTO: Returns this result to the caller.
            return [_TokView(self.end_marker, self.end_marker, 1, 0)]
        # LINE: Add EOF if lexer/caller did not already include it.
        if toks[-1].type != self.end_marker:
            # AUTO: Sets `last_line`.
            last_line = toks[-1].line or 1
            # AUTO: Sets `last_col`.
            last_col = toks[-1].col or 0
            # AUTO: Sets `toks`.
            toks = toks + [_TokView(self.end_marker, self.end_marker, last_line, last_col)]
        # LINE: Return token stream guaranteed to end with EOF.
        return toks

    # AUTO: Sets `_TERMINAL_DISPLAY: Dict[str, str]`.
    _TERMINAL_DISPLAY: Dict[str, str] = {
        # AUTO: Executes this statement.
        'id': 'id', 'intlit': 'intlit', 'dblit': 'dblit',
        # AUTO: Executes this statement.
        'stringlit': 'stringlit', 'chrlit': 'chrlit',
        # AUTO: Executes this statement.
        'sunshine': "'sunshine'", 'frost': "'frost'",
        # AUTO: Executes this statement.
        'seed': "'seed'", 'tree': "'tree'",
        # AUTO: Executes this statement.
        'leaf': "'leaf'", 'branch': "'branch'",
        # AUTO: Executes this statement.
        'vine': "'vine'",
        # AUTO: Executes this statement.
        'bundle': "'bundle'", 'fertile': "'fertile'",
        # AUTO: Executes this statement.
        'pollinate': "'pollinate'", 'root': "'root'",
        # AUTO: Executes this statement.
        'reclaim': "'reclaim'", 'spring': "'spring'",
        # AUTO: Executes this statement.
        'bud': "'bud'", 'wither': "'wither'",
        # AUTO: Executes this statement.
        'grow': "'grow'", 'cultivate': "'cultivate'",
        # AUTO: Executes this statement.
        'tend': "'tend'", 'harvest': "'harvest'",
        # AUTO: Executes this statement.
        'variety': "'variety'", 'soil': "'soil'",
        # AUTO: Executes this statement.
        'prune': "'prune'", 'skip': "'skip'",
        # AUTO: Executes this statement.
        'water': "'water'", 'plant': "'plant'",
        # AUTO: Executes this statement.
        'empty': "'empty'",
        # AUTO: Executes this statement.
        'EOF': 'end of file',
    # AUTO: Closes the current grouped code/data.
    }

    # AUTO: Defines function `_format_expected`.
    def _format_expected(self, expected: Set[str], non_terminal: Optional[str] = None) -> str:
        # AUTO: Sets `symbols`.
        symbols = {'(', ')', '{', '}', ';', ',', '=', '+', '-', '*', '/', '%',
                   # AUTO: Executes this statement.
                   '++', '--', '==', '!=', '<', '>', '<=', '>=', '&&', '||',
                   # AUTO: Adds into `'!', '~', '`.
                   '!', '~', '+=', '-=', '*=', '/=', '%=', '.', '[', ']', ':', '`'}
        # AUTO: Calls `any`.
        has_reclaim = any(tk.type == 'reclaim' for tk in getattr(self, '_current_tokens', []))

        # AUTO: Sets `parts: List[str]`.
        parts: List[str] = []
        # AUTO: Starts a loop over these values.
        for t in sorted(expected):
            # AUTO: Checks this condition.
            if t == 'reclaim' and has_reclaim:
                # AUTO: Skips to the next loop iteration.
                continue
            # AUTO: Checks this condition.
            if t in self._TERMINAL_DISPLAY:
                # AUTO: Appends a value to a list.
                parts.append(self._TERMINAL_DISPLAY[t])
            # AUTO: Checks the next alternate condition.
            elif t in symbols:
                # AUTO: Appends a value to a list.
                parts.append(f"'{t}'")
            # AUTO: Checks the next alternate condition.
            elif t.startswith('<') and t.endswith('>'):
                # AUTO: Skips to the next loop iteration.
                continue
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Appends a value to a list.
                parts.append(f"'{t}'")
        # AUTO: Checks this condition.
        if not parts:
            # AUTO: Returns this result to the caller.
            return 'nothing'
        # AUTO: Returns this result to the caller.
        return f"Expected: {', '.join(parts)}"

    # AUTO: Defines function `_generate_helpful_error`.
    def _generate_helpful_error(
        # AUTO: Executes this statement.
        self,
        # AUTO: Executes this statement.
        non_terminal: str,
        # AUTO: Executes this statement.
        token_type: str,
        # AUTO: Executes this statement.
        token_value: str,
        # AUTO: Executes this statement.
        line: int,
        # AUTO: Executes this statement.
        col: int,
        # AUTO: Executes this statement.
        expected: Set[str],
        # AUTO: Executes this statement.
        index: int,
        # AUTO: Executes this statement.
        toks: List[_TokView]
    # AUTO: Closes the current grouped code/data.
    ) -> str:
        
        # AUTO: Sets `param_type_tokens`.
        param_type_tokens = {'seed', 'tree', 'leaf', 'vine', 'branch'}
        
        # AUTO: Checks this condition.
        if token_type == self.end_marker or token_value == '':
            # AUTO: Checks this condition.
            if '}' in expected:
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} Unexpected end of file. Missing closing '}}'. {self._format_expected(expected, non_terminal)}"
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Unexpected end of file. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type == '=' and index > 0:
            # AUTO: Sets `prev_index`.
            prev_index = index - 1
            # AUTO: Repeats while this condition is true.
            while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                # AUTO: Subtracts from `prev_index`.
                prev_index -= 1
            
            # AUTO: Checks this condition.
            if prev_index >= 0 and toks[prev_index].type == '==':
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} Invalid operator '==='. Use '==' for equality comparison. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type == '&' and index > 0:
            # AUTO: Sets `prev_index`.
            prev_index = index - 1
            # AUTO: Repeats while this condition is true.
            while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                # AUTO: Subtracts from `prev_index`.
                prev_index -= 1
            
            # AUTO: Checks this condition.
            if prev_index >= 0 and toks[prev_index].type == '&&':
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} Invalid operator '&&&'. Use '&&' for logical AND. {self._format_expected(expected, non_terminal)}"
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Invalid operator '&'. Use '&&' for logical AND. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type == '|' and index > 0:
            # AUTO: Sets `prev_index`.
            prev_index = index - 1
            # AUTO: Repeats while this condition is true.
            while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                # AUTO: Subtracts from `prev_index`.
                prev_index -= 1
            
            # AUTO: Checks this condition.
            if prev_index >= 0 and toks[prev_index].type == '||':
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} Invalid operator '|||'. Use '||' for logical OR. {self._format_expected(expected, non_terminal)}"
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Invalid operator '|'. Use '||' for logical OR. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type == 'chrlit' and token_value and not token_value.endswith("'"):
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type == 'stringlit' and token_value and not token_value.endswith('"'):
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if non_terminal == '<reclaim_value>' and token_type == '}':
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Missing ';' after 'reclaim'. Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type == ')' and ')' not in expected:
            # AUTO: Checks this condition.
            if index > 0:
                # AUTO: Sets `prev_index`.
                prev_index = index - 1
                # AUTO: Repeats while this condition is true.
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    # AUTO: Subtracts from `prev_index`.
                    prev_index -= 1
                
                # AUTO: Checks this condition.
                if prev_index >= 0:
                    # AUTO: Sets `prev_tok`.
                    prev_tok = toks[prev_index]
                    # AUTO: Executes this statement.
                    binary_operators = {'+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||'}
                    # AUTO: Checks this condition.
                    if prev_tok.type in binary_operators:
                        # AUTO: Returns this result to the caller.
                        return f"SYNTAX error line {line} col {col} Unexpected token ')' after binary operator '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"
                    
                    # AUTO: Checks this condition.
                    if prev_tok.type == ',' and param_type_tokens & expected:
                        # AUTO: Returns this result to the caller.
                        return f"SYNTAX error line {line} col {col} Unexpected token ')'. Expected parameter type (seed, tree, leaf, vine, branch) after ','"
                    
                    # AUTO: Checks this condition.
                    if prev_tok.type == '(':
                        # AUTO: Sets `kw_index`.
                        kw_index = prev_index - 1
                        # AUTO: Repeats while this condition is true.
                        while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:
                            # AUTO: Subtracts from `kw_index`.
                            kw_index -= 1
                        # AUTO: Checks this condition.
                        if kw_index >= 0:
                            # AUTO: Sets `keyword_descriptions`.
                            keyword_descriptions = {
                                # AUTO: Executes this statement.
                                'grow': 'while-loop', 'spring': 'if-statement', 'cultivate': 'for-loop',
                                # AUTO: Executes this statement.
                                'tend': 'do-while-loop', 'harvest': 'switch-statement', 'bud': 'else-if',
                                # AUTO: Executes this statement.
                                'plant': 'output function', 'water': 'input function',
                                # AUTO: Executes this statement.
                                'seed': 'integer type', 'tree': 'float type', 'leaf': 'character type',
                                # AUTO: Executes this statement.
                                'vine': 'string type', 'branch': 'boolean type',
                                # AUTO: Executes this statement.
                                'reclaim': 'return statement', 'prune': 'break statement',
                                # AUTO: Executes this statement.
                                'skip': 'continue statement', 'pollinate': 'function declaration',
                                # AUTO: Executes this statement.
                                'root': 'main function', 'wither': 'else-statement',
                                # AUTO: Executes this statement.
                                'fertile': 'constant declaration', 'bundle': 'struct definition',
                                # AUTO: Executes this statement.
                                'variety': 'case label', 'soil': 'default case',
                                # AUTO: Executes this statement.
                                'empty': 'void type',
                            # AUTO: Closes the current grouped code/data.
                            }
                            # AUTO: Sets `kw_tok`.
                            kw_tok = toks[kw_index]
                            # AUTO: Checks this condition.
                            if kw_tok.type in keyword_descriptions:
                                # AUTO: Sets `desc`.
                                desc = keyword_descriptions[kw_tok.type]
                                # AUTO: Returns this result to the caller.
                                return f"SYNTAX error line {kw_tok.line} col {kw_tok.col} '{kw_tok.value}' is a reserved keyword ({desc}) and cannot be used as a function name."
            
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Unexpected token ')' - no matching '(' found in expression. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Adds into `assignment_operators = {'`.
        assignment_operators = {'+=', '-=', '*=', '/=', '%='}
        # AUTO: Checks this condition.
        if token_type in assignment_operators:
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Assignment operator '{token_value}' must follow a modifiable assignment target. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type == '=':
            # AUTO: Checks this condition.
            if index > 0:
                # AUTO: Sets `prev_index`.
                prev_index = index - 1
                # AUTO: Repeats while this condition is true.
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    # AUTO: Subtracts from `prev_index`.
                    prev_index -= 1
                
                # AUTO: Checks this condition.
                if prev_index >= 0:
                    # AUTO: Sets `prev_tok`.
                    prev_tok = toks[prev_index]
                    # AUTO: Sets `compound_op_bases`.
                    compound_op_bases = {'+', '-', '*', '/', '%'}
                    # AUTO: Checks this condition.
                    if prev_tok.type in compound_op_bases:
                        # AUTO: Sets `prev_prev_index`.
                        prev_prev_index = prev_index - 1
                        # AUTO: Repeats while this condition is true.
                        while prev_prev_index >= 0 and toks[prev_prev_index].type in self.skip_token_types:
                            # AUTO: Subtracts from `prev_prev_index`.
                            prev_prev_index -= 1
                        
                        # AUTO: Checks this condition.
                        if prev_prev_index >= 0 and toks[prev_prev_index].type == 'id':
                            # AUTO: Sets `id_tok`.
                            id_tok = toks[prev_prev_index]
                            # AUTO: Sets `compound_op`.
                            compound_op = f"{prev_tok.value}="
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {line} col {col} Unexpected token '=' after operator '{prev_tok.value}'. Did you mean '{id_tok.value} {compound_op}' (compound assignment with no space)? {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type == '{' and non_terminal in {'<program>', '<global_declaration>'}:
            # AUTO: Checks this condition.
            if index == 0 or (index <= 2 and all(toks[i].type in self.skip_token_types for i in range(index))):
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} 'root' function declaration is missing opening '('. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if index + 1 < len(toks):
            # AUTO: Sets `next_tok`.
            next_tok = toks[index + 1]
            # AUTO: Checks this condition.
            if next_tok.type == 'chrlit' and next_tok.value and not next_tok.value.endswith("'"):
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {next_tok.line} col {next_tok.col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"
            
            # AUTO: Checks this condition.
            if next_tok.type == 'stringlit' and next_tok.value and not next_tok.value.endswith('"'):
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {next_tok.line} col {next_tok.col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type == ';' and non_terminal == '<global_declaration>':
            # AUTO: Checks this condition.
            if index > 0:
                # AUTO: Sets `prev_index`.
                prev_index = index - 1
                # AUTO: Repeats while this condition is true.
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    # AUTO: Subtracts from `prev_index`.
                    prev_index -= 1
                
                # AUTO: Checks this condition.
                if prev_index >= 0 and toks[prev_index].type == '}':
                    # AUTO: Sets `bundle_index`.
                    bundle_index = prev_index - 1
                    # AUTO: Repeats while this condition is true.
                    while bundle_index >= 0 and toks[bundle_index].type in self.skip_token_types:
                        # AUTO: Subtracts from `bundle_index`.
                        bundle_index -= 1
                    
                    # AUTO: Sets `found_bundle`.
                    found_bundle = False
                    # AUTO: Starts a loop over these values.
                    for i in range(bundle_index, max(0, bundle_index - 20) - 1, -1):
                        # AUTO: Checks this condition.
                        if toks[i].type == 'bundle':
                            # AUTO: Sets `found_bundle`.
                            found_bundle = True
                            # AUTO: Stops the nearest loop.
                            break
                    
                    # AUTO: Checks this condition.
                    if found_bundle:
                        # AUTO: Sets `expected_str`.
                        expected_str = self._format_expected(expected, non_terminal)
                        # AUTO: Returns this result to the caller.
                        return f"SYNTAX error line {line} col {col} Unexpected token ';' after bundle definition closing '}}'. ';' is not in {expected_str}. Remove the trailing ';'"
        
        # AUTO: Sets `common_keyword_mistakes`.
        common_keyword_mistakes = {
            # AUTO: Executes this statement.
            'function': 'pollinate',
            # AUTO: Executes this statement.
            'int': 'seed',
            # AUTO: Executes this statement.
            'float': 'tree',
            # AUTO: Executes this statement.
            'double': 'tree',
            # AUTO: Executes this statement.
            'char': 'leaf',
            # AUTO: Executes this statement.
            'bool': 'branch',
            # AUTO: Executes this statement.
            'boolean': 'branch',
            # AUTO: Executes this statement.
            'if': 'spring',
            # AUTO: Executes this statement.
            'else': 'wither',
            # AUTO: Executes this statement.
            'elif': 'bud',
            # AUTO: Executes this statement.
            'while': 'grow',
            # AUTO: Executes this statement.
            'for': 'cultivate',
            # AUTO: Executes this statement.
            'switch': 'harvest',
            # AUTO: Executes this statement.
            'case': 'variety',
            # AUTO: Executes this statement.
            'default': 'soil',
            # AUTO: Executes this statement.
            'break': 'prune',
            # AUTO: Executes this statement.
            'continue': 'skip',
            # AUTO: Executes this statement.
            'return': 'reclaim',
            # AUTO: Executes this statement.
            'void': 'empty',
            # AUTO: Executes this statement.
            'const': 'fertile',
            # AUTO: Executes this statement.
            'struct': 'bundle',
            # AUTO: Executes this statement.
            'string': 'vine',
            # AUTO: Executes this statement.
            'printf': 'plant',
            # AUTO: Executes this statement.
            'scanf': 'water',
            # AUTO: Executes this statement.
            'print': 'plant',
            # AUTO: Executes this statement.
            'input': 'water'
        # AUTO: Closes the current grouped code/data.
        }
        
        # AUTO: Checks this condition.
        if token_type == 'id' and token_value in common_keyword_mistakes:
            # AUTO: Sets `correct_keyword`.
            correct_keyword = common_keyword_mistakes[token_value]
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} '{token_value}' is not a GAL keyword. Use '{correct_keyword}' instead."
        
        # AUTO: Checks this condition.
        if token_type == '{' and (non_terminal == '<bundle_or_var>' or non_terminal == '<bundle_mem_dec>'):
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Bundle definitions must be at global scope (outside all functions). Move this bundle definition before 'root()'. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Sets `statement_starters`.
        statement_starters = {
            # AUTO: Executes this statement.
            'reclaim', 'spring', 'wither', 'bud', 'grow', 'cultivate', 'tend',
            # AUTO: Executes this statement.
            'harvest', 'prune', 'skip', 'water', 'plant', 'seed', 'leaf',
            # AUTO: Executes this statement.
            'branch', 'tree', 'vine', 'bundle', 'fertile', 'pollinate', 'root', 'id'
        # AUTO: Closes the current grouped code/data.
        }
        
        # AUTO: Checks this condition.
        if ':' in expected and token_type in statement_starters:
            # AUTO: Sets `context_keyword`.
            context_keyword = None
            # AUTO: Checks this condition.
            if index > 0:
                # AUTO: Sets `scan`.
                scan = index - 1
                # AUTO: Repeats while this condition is true.
                while scan >= 0:
                    # AUTO: Checks this condition.
                    if toks[scan].type in self.skip_token_types:
                        # AUTO: Subtracts from `scan`.
                        scan -= 1
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Checks this condition.
                    if toks[scan].type == 'variety':
                        # AUTO: Sets `context_keyword`.
                        context_keyword = 'variety'
                        # AUTO: Stops the nearest loop.
                        break
                    # AUTO: Checks this condition.
                    if toks[scan].type == 'soil':
                        # AUTO: Sets `context_keyword`.
                        context_keyword = 'soil'
                        # AUTO: Stops the nearest loop.
                        break
                    # AUTO: Checks this condition.
                    if toks[scan].type in {'id', 'intlit', 'dblit', 'stringlit', 'chrlit',
                                           # AUTO: Executes this statement.
                                           'sunshine', 'frost', '+', '-', '*', '/', '%',
                                           # AUTO: Executes this statement.
                                           '==', '!=', '<', '>', '<=', '>=', '&&', '||',
                                           # AUTO: Executes this statement.
                                           '(', ')', '`', '~'}:
                        # AUTO: Subtracts from `scan`.
                        scan -= 1
                        # AUTO: Skips to the next loop iteration.
                        continue
                    # AUTO: Stops the nearest loop.
                    break
            # AUTO: Checks this condition.
            if context_keyword:
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}' after '{context_keyword}'. {self._format_expected({':'})}"
        
        # AUTO: Checks this condition.
        if ';' in expected:
            # AUTO: Checks this condition.
            if token_type in statement_starters or token_type == 'id':
                # AUTO: Checks this condition.
                if index > 0:
                    # AUTO: Sets `prev_index`.
                    prev_index = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_index`.
                        prev_index -= 1
                    
                    # AUTO: Checks this condition.
                    if prev_index >= 0:
                        # AUTO: Sets `prev_tok`.
                        prev_tok = toks[prev_index]
                        
                        # AUTO: Checks this condition.
                        if prev_tok.type == '=':
                            # AUTO: Sets `prev_line`.
                            prev_line = prev_tok.line
                            # AUTO: Sets `prev_col`.
                            prev_col = prev_tok.col
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing value after '=' operator. {self._format_expected(expected, non_terminal)}"
                        
                        # AUTO: Checks this condition.
                        if prev_tok.type == 'chrlit' and prev_tok.value and not prev_tok.value.endswith("'"):
                            # AUTO: Sets `prev_line`.
                            prev_line = prev_tok.line
                            # AUTO: Sets `prev_col`.
                            prev_col = prev_tok.col
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"
                        
                        # AUTO: Checks this condition.
                        if prev_tok.type == 'stringlit' and prev_tok.value and not prev_tok.value.endswith('"'):
                            # AUTO: Sets `prev_line`.
                            prev_line = prev_tok.line
                            # AUTO: Sets `prev_col`.
                            prev_col = prev_tok.col
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"
                        
                        # AUTO: Sets `prev_line`.
                        prev_line = prev_tok.line
                        # AUTO: Sets `prev_col`.
                        prev_col = prev_tok.col + len(str(prev_tok.value))
                        # AUTO: Sets `expected_str`.
                        expected_str = self._format_expected(expected, non_terminal)
                        # AUTO: Checks this condition.
                        if prev_line != line:
                            # AUTO: Returns this result to the caller.
                            return (f"SYNTAX error line {prev_line} col {prev_col} Unexpected token '{token_value}' after '{prev_tok.value}'. {expected_str}")
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {expected_str}"
            # AUTO: Checks the next alternate condition.
            elif token_type == '}':
                # AUTO: Checks this condition.
                if index > 0:
                    # AUTO: Sets `prev_index`.
                    prev_index = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_index`.
                        prev_index -= 1
                    
                    # AUTO: Checks this condition.
                    if prev_index >= 0:
                        # AUTO: Sets `prev_tok`.
                        prev_tok = toks[prev_index]
                        
                        # AUTO: Checks this condition.
                        if prev_tok.type == 'reclaim':
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {prev_tok.line} col {prev_tok.col + len('reclaim')} Missing ';' after 'reclaim'. {self._format_expected(expected, non_terminal)}"
                        
                        # AUTO: Checks this condition.
                        if prev_tok.type == 'chrlit' and prev_tok.value and not prev_tok.value.endswith("'"):
                            # AUTO: Sets `prev_line`.
                            prev_line = prev_tok.line
                            # AUTO: Sets `prev_col`.
                            prev_col = prev_tok.col
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"
                        
                        # AUTO: Checks this condition.
                        if prev_tok.type == 'stringlit' and prev_tok.value and not prev_tok.value.endswith('"'):
                            # AUTO: Sets `prev_line`.
                            prev_line = prev_tok.line
                            # AUTO: Sets `prev_col`.
                            prev_col = prev_tok.col
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"
                        
                        # AUTO: Sets `prev_line`.
                        prev_line = prev_tok.line
                        # AUTO: Sets `prev_col`.
                        prev_col = prev_tok.col + len(str(prev_tok.value))
                        # AUTO: Sets `expected_str`.
                        expected_str = self._format_expected(expected, non_terminal)
                        # AUTO: Checks this condition.
                        if prev_line != line:
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {prev_line} col {prev_col} Unexpected token '}}' after '{prev_tok.value}'. {expected_str}"
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {line} col {col} Unexpected token '}}'. {expected_str}"
        
        # AUTO: Checks this condition.
        if 'reclaim' in expected and token_type == '}':
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} expected 'reclaim;' before '}}'. All functions, including root(), must end with 'reclaim;'. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if 'prune' in expected and token_type in {'variety', 'soil', '}'}:
            # AUTO: Checks this condition.
            if token_type == 'variety':
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} expected 'prune;' before next 'variety'. Each case in 'harvest' must end with 'prune;'. {self._format_expected(expected, non_terminal)}"
            # AUTO: Checks the next alternate condition.
            elif token_type == 'soil':
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} expected 'prune;' before 'soil'. Each case must end with 'prune;'. {self._format_expected(expected, non_terminal)}"
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} expected 'prune;' before closing '}}'. Each case must end with 'prune;'. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type in {'-', '+'} and non_terminal in {'<expression>', '<factor>', '<term>', '<arithmetic>', '<logic_or>', '<logic_and>', '<relational>', '<init_val>'}:
            # AUTO: Checks this condition.
            if index > 0:
                # AUTO: Sets `prev_index`.
                prev_index = index - 1
                # AUTO: Repeats while this condition is true.
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    # AUTO: Subtracts from `prev_index`.
                    prev_index -= 1
                
                # AUTO: Checks this condition.
                if prev_index >= 0:
                    # AUTO: Sets `prev_tok`.
                    prev_tok = toks[prev_index]
                    # AUTO: Checks this condition.
                    if prev_tok.type in {'=', '+=', '-=', '*=', '/=', '%=', '(', ','}:
                        # AUTO: Checks this condition.
                        if token_value == '-':
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {line} col {col} Unary '-' not supported. Use '~' for negative numbers (e.g., '~5') or '(0 - value)' for negation. {self._format_expected(expected, non_terminal)}"
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {line} col {col} Unary '+' operator not supported. Use parentheses for expressions like '(0 + value)'. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type in {'*', '/', '%', '+', '-', '`', '&&', '||', '==', '!=', '<', '>', '<=', '>='}:
            # AUTO: Checks this condition.
            if index > 0:
                # AUTO: Sets `prev_index`.
                prev_index = index - 1
                # AUTO: Repeats while this condition is true.
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    # AUTO: Subtracts from `prev_index`.
                    prev_index -= 1
                
                # AUTO: Checks this condition.
                if prev_index >= 0 and toks[prev_index].type == '(':
                    # AUTO: Returns this result to the caller.
                    return f"SYNTAX error line {line} col {col} Unexpected binary operator '{token_value}'. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if '(' in expected and token_type != '(':
            # AUTO: Checks this condition.
            if index > 0 and token_type not in {'-', '+'}:
                # AUTO: Sets `prev_index`.
                prev_index = index - 1
                # AUTO: Repeats while this condition is true.
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    # AUTO: Subtracts from `prev_index`.
                    prev_index -= 1
                
                # AUTO: Checks this condition.
                if prev_index >= 0:
                    # AUTO: Sets `prev_tok`.
                    prev_tok = toks[prev_index]
                    # AUTO: Checks this condition.
                    if prev_tok.type in {'+', '-', '*', '/', '%', '`', '=', '+=', '-=', '*=', '/=', '%=', '&&', '||', '==', '!=', '<', '>', '<=', '>='}:
                        # AUTO: Checks this condition.
                        if token_type in {'*', '/', '%', '+', '-', '`', '&&', '||', '==', '!=', '<', '>', '<=', '>='}:
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}' operator - binary operators cannot start an expression. {self._format_expected(expected, non_terminal)}"
                        # AUTO: Returns this result to the caller.
                        return f"SYNTAX error line {line} col {col} Missing value after '{prev_tok.value}' operator. {self._format_expected(expected, non_terminal)}"
            
            # AUTO: Checks this condition.
            if token_type in {'=', '+=', '-=', '*=', '/=', '%='}:
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"
            
            # AUTO: Checks this condition.
            if index > 0:
                # AUTO: Sets `prev_index`.
                prev_index = index - 1
                # AUTO: Repeats while this condition is true.
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    # AUTO: Subtracts from `prev_index`.
                    prev_index -= 1
                
                # AUTO: Checks this condition.
                if prev_index >= 0:
                    # AUTO: Sets `prev_tok`.
                    prev_tok = toks[prev_index]
                    
                    # AUTO: Sets `common_keyword_mistakes`.
                    common_keyword_mistakes = {
                        # AUTO: Executes this statement.
                        'function': 'pollinate',
                        # AUTO: Executes this statement.
                        'int': 'seed',
                        # AUTO: Executes this statement.
                        'float': 'tree',
                        # AUTO: Executes this statement.
                        'double': 'tree',
                        # AUTO: Executes this statement.
                        'char': 'leaf',
                        # AUTO: Executes this statement.
                        'bool': 'branch',
                        # AUTO: Executes this statement.
                        'boolean': 'branch',
                        # AUTO: Executes this statement.
                        'if': 'spring',
                        # AUTO: Executes this statement.
                        'else': 'wither',
                        # AUTO: Executes this statement.
                        'elif': 'bud',
                        # AUTO: Executes this statement.
                        'while': 'grow',
                        # AUTO: Executes this statement.
                        'for': 'cultivate',
                        # AUTO: Executes this statement.
                        'switch': 'harvest',
                        # AUTO: Executes this statement.
                        'case': 'variety',
                        # AUTO: Executes this statement.
                        'default': 'soil',
                        # AUTO: Executes this statement.
                        'break': 'prune',
                        # AUTO: Executes this statement.
                        'continue': 'skip',
                        # AUTO: Executes this statement.
                        'return': 'reclaim',
                        # AUTO: Executes this statement.
                        'void': 'empty',
                        # AUTO: Executes this statement.
                        'const': 'fertile',
                        # AUTO: Executes this statement.
                        'struct': 'bundle',
                        # AUTO: Executes this statement.
                        'string': 'vine',
                        # AUTO: Executes this statement.
                        'printf': 'plant',
                        # AUTO: Executes this statement.
                        'scanf': 'water',
                        # AUTO: Executes this statement.
                        'print': 'plant',
                        # AUTO: Executes this statement.
                        'input': 'water'
                    # AUTO: Closes the current grouped code/data.
                    }
                    
                    # AUTO: Checks this condition.
                    if prev_tok.type == 'id' and prev_tok.value in common_keyword_mistakes:
                        # AUTO: Sets `correct_keyword`.
                        correct_keyword = common_keyword_mistakes[prev_tok.value]
                        # AUTO: Returns this result to the caller.
                        return f"SYNTAX error line {prev_tok.line} col {prev_tok.col} '{prev_tok.value}' is not a GAL keyword. Use '{correct_keyword}' instead."
                    
                    # AUTO: Sets `keywords_needing_parens`.
                    keywords_needing_parens = {'spring', 'grow', 'cultivate', 'harvest', 'water', 'plant', 'tend', 'bud'}
                    # AUTO: Checks this condition.
                    if prev_tok.type in keywords_needing_parens:
                        # AUTO: Returns this result to the caller.
                        return f"SYNTAX error line {line} col {col} Missing '(' after '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"
                    
                    # AUTO: Checks this condition.
                    if prev_tok.type == 'id':
                        # NOTE: GAL does support '**' (exponentiation) and '**=' (exponent-assign).

                        # AUTO: Sets `compound_op_bases`.
                        compound_op_bases = {'+', '-', '*', '/', '%'}
                        # AUTO: Checks this condition.
                        if token_type in compound_op_bases:
                            # AUTO: Sets `next_index`.
                            next_index = index + 1
                            # AUTO: Repeats while this condition is true.
                            while next_index < len(toks) and toks[next_index].type in self.skip_token_types:
                                # AUTO: Adds into `next_index`.
                                next_index += 1
                            
                            # AUTO: Checks this condition.
                            if next_index < len(toks) and toks[next_index].type == '=':
                                # AUTO: Sets `compound_op`.
                                compound_op = f"{token_value}="
                                # AUTO: Returns this result to the caller.
                                return f"SYNTAX error line {line} col {col} Unexpected operator '{token_value}' followed by '='. Expected: '{compound_op}' (compound assignment must be written without spaces). {self._format_expected(expected, non_terminal)}"
                        
                        # AUTO: Executes this statement.
                        binary_operators = {'+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||'}
                        # AUTO: Sets `has_operators_expected`.
                        has_operators_expected = bool(binary_operators & expected)
                        
                        # AUTO: Checks this condition.
                        if has_operators_expected:
                            # AUTO: Checks this condition.
                            if token_type in {'++', '--'}:
                                # AUTO: Sets `next_index`.
                                next_index = index + 1
                                # AUTO: Repeats while this condition is true.
                                while next_index < len(toks) and toks[next_index].type in self.skip_token_types:
                                    # AUTO: Adds into `next_index`.
                                    next_index += 1
                                
                                # AUTO: Checks this condition.
                                if next_index < len(toks):
                                    # AUTO: Sets `next_tok`.
                                    next_tok = toks[next_index]
                                    # AUTO: Checks this condition.
                                    if (token_type == '++' and next_tok.type == '+') or (token_type == '--' and next_tok.type == '-'):
                                        # AUTO: Calls `+`.
                                        operator_seq = token_type + ('+' if token_type == '++' else '-')
                                        # AUTO: Returns this result to the caller.
                                        return f"SYNTAX error line {line} col {col} Unexpected token '{operator_seq}' operator sequence. {self._format_expected(expected, non_terminal)}"
                                
                                # AUTO: Returns this result to the caller.
                                return f"SYNTAX error line {line} col {col} Unexpected {token_type} operator. {self._format_expected(expected, non_terminal)}"
                            # AUTO: Checks this condition.
                            if token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'id'}:
                                # AUTO: Returns this result to the caller.
                                return f"SYNTAX error line {line} col {col} Unexpected token '{token_type}' after identifier '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Returns this result to the caller.
                                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}' after identifier '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {prev_tok.line} col {prev_tok.col} invalid statement: identifier '{prev_tok.value}' must be followed by assignment operator, unary operator (++/--), or function call syntax '()'. {self._format_expected(expected, non_terminal)}"
            
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Sets `declaration_keywords`.
        declaration_keywords = {'seed', 'tree', 'leaf', 'vine', 'branch', 'bundle', 'fertile'}
        # AUTO: Checks this condition.
        if token_type in declaration_keywords and non_terminal in {'<body_statement>', '<statement>', '<case_statements>'}:
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Unexpected local declaration '{token_value}' after an executable statement. Local declarations must appear first in the block. {self._format_expected(expected, non_terminal)}"

        # AUTO: Checks this condition.
        if '}' in expected and token_type in statement_starters:
            # AUTO: Checks this condition.
            if token_type == 'bud':
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} 'bud' can only appear after a 'spring' statement. {self._format_expected(expected, non_terminal)}"
            # AUTO: Checks the next alternate condition.
            elif token_type == 'wither':
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} 'wither' can only appear after a 'spring' or 'bud' statement. {self._format_expected(expected, non_terminal)}"
            # AUTO: Checks the next alternate condition.
            elif token_type == 'reclaim':
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} Missing closing brace before '{token_value}'. {self._format_expected(expected, non_terminal)}"
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Missing closing brace before '{token_value}'. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type in {'++', '--'} and ')' in expected:
            # AUTO: Executes this statement.
            op_name = "increment" if token_value == "++" else "decrement"
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Postfix {op_name} operator '{token_value}' not allowed in expression context. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if param_type_tokens & expected and ')' in expected and token_type == 'id':
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. Expected parameter type (seed, tree, leaf, vine, branch) or ')'"
        
        # AUTO: Checks this condition.
        if ')' in expected and token_type not in {')'}:
            # AUTO: Checks this condition.
            if ',' in expected and token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'id', 'sunshine', 'frost', '~', '!'}:
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. Expected ',' between arguments or ')' to close function call"
            # AUTO: Checks this condition.
            if token_type in {'~', '!'}:
                # AUTO: Returns this result to the caller.
                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'id'}:
            # AUTO: Checks this condition.
            if index > 0:
                # AUTO: Sets `prev_index`.
                prev_index = index - 1
                # AUTO: Repeats while this condition is true.
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    # AUTO: Subtracts from `prev_index`.
                    prev_index -= 1
                
                # AUTO: Checks this condition.
                if prev_index >= 0:
                    # AUTO: Sets `prev_tok`.
                    prev_tok = toks[prev_index]
                    # AUTO: Checks this condition.
                    if prev_tok.type in {'id', 'intlit', 'dblit', 'stringlit', 'chrlit'}:
                        # AUTO: Sets `expression_contexts`.
                        expression_contexts = {'<expression>', '<factor>', '<term>', '<arithmetic>', '<logic_or>', 
                                             # AUTO: Executes this statement.
                                             '<logic_and>', '<relational>', '<init_val>', '<param_list>', '<arg_list>',
                                             # AUTO: Executes this statement.
                                             '<term_tail>', '<arithmetic_tail>', '<relational_tail>', '<logic_and_tail>', '<logic_or_tail>'}
                        
                        # AUTO: Checks this condition.
                        if non_terminal in expression_contexts:
                            # AUTO: Sets `prev_type_friendly`.
                            prev_type_friendly = {
                                # AUTO: Executes this statement.
                                'id': 'identifier',
                                # AUTO: Executes this statement.
                                'intlit': 'integer literal',
                                # AUTO: Executes this statement.
                                'dblit': 'double literal',
                                # AUTO: Executes this statement.
                                'stringlit': 'string literal',
                                # AUTO: Executes this statement.
                                'chrlit': 'character literal'
                            # AUTO: Closes the current grouped code/data.
                            }.get(prev_tok.type, prev_tok.type)
                            
                            # AUTO: Sets `curr_type_friendly`.
                            curr_type_friendly = {
                                # AUTO: Executes this statement.
                                'id': 'identifier',
                                # AUTO: Executes this statement.
                                'intlit': 'integer literal',
                                # AUTO: Executes this statement.
                                'dblit': 'double literal',
                                # AUTO: Executes this statement.
                                'stringlit': 'string literal',
                                # AUTO: Executes this statement.
                                'chrlit': 'character literal'
                            # AUTO: Closes the current grouped code/data.
                            }.get(token_type, token_type)
                            
                            # AUTO: Returns this result to the caller.
                            return f"SYNTAX error line {line} col {col} Unexpected {curr_type_friendly} '{token_value}' after {prev_type_friendly} '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"
        
        # AUTO: Checks this condition.
        if non_terminal == '<array_dim_opt>' and token_type == 'id':
            # AUTO: Returns this result to the caller.
            return f"SYNTAX error line {line} col {col} Array size must be a constant integer literal, not a variable '{token_value}'. Expected: ']', dblit, intlit"

        # AUTO: Returns this result to the caller.
        return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"

    # AUTO: Defines function `parse`.
    def parse(self, tokens: Sequence[Any]) -> Tuple[bool, List[str]]:
        # GUIDE: Main LL(1) stack algorithm; compare grammar symbols on the stack
        # with the current lookahead token, then expand or consume.
        # Convert incoming Token objects into the parser's simple _TokView form.
        # LINE: Convert lexer Token objects into the parser's lightweight token view.
        toks = [_as_tok(t) for t in tokens]

        # Normalize token names so lexer aliases still match grammar terminals.
        # LINE: Rename token types if lexer name and grammar name differ.
        toks = [_TokView(self._normalize_token_type(t.type), t.value, t.line, t.col) for t in toks]

        # Make sure the parser always has an EOF marker to know when to stop.
        # LINE: Ensure EOF exists so the parsing loop has a stopping token.
        toks = self._ensure_eof(toks)

        # LINE: Keep current tokens for helper error messages.
        self._current_tokens = toks

        # Stack starts with EOF at the bottom and <program> on top. The parser
        # repeatedly expands the top grammar symbol until the stack is empty.
        # LINE: Start with EOF at bottom and <program> as the first rule to expand.
        stack: List[str] = [self.end_marker, self.start_symbol]
        # LINE: index points to the current lookahead token in toks.
        index = 0
        
        # LINE: Track declaration type to make simple literal mismatch messages clearer.
        current_var_type: Optional[str] = None
        # LINE: Becomes seed/tree/etc after '=' while parsing declarations.
        expecting_value_for_type: Optional[str] = None

        # LINE: Tracks whether reclaim already appeared inside each block.
        reclaim_seen_stack: List[bool] = []

        # AUTO: Defines function `current_token`.
        def current_token() -> _TokView:
            # Lookahead token: the parser decides what to do using only this
            # current token type, which is the LL(1) idea.
            # AUTO: Uses a variable from an outer function scope.
            nonlocal index
            # LINE: If index passed the stream, pretend the lookahead is EOF.
            if index >= len(toks):
                # AUTO: Sets `last_line`.
                last_line = toks[-1].line if toks else 1
                # AUTO: Sets `last_col`.
                last_col = toks[-1].col if toks else 0
                # AUTO: Returns this result to the caller.
                return _TokView(self.end_marker, self.end_marker, last_line, last_col)
            # LINE: Return the token currently being compared with the stack top.
            return toks[index]

        # LINE: Keep parsing until every grammar symbol in the stack is handled.
        while stack:
            # top is the grammar symbol we need to match/expand.
            # tok is the current input token from the lexer.
            # LINE: Read the top grammar symbol and the current lookahead token.
            top = stack[-1]
            # AUTO: Sets `tok`.
            tok = current_token()
            # AUTO: Sets `token_type`.
            token_type = tok.type
            # AUTO: Sets `token_value`.
            token_value = tok.value
            # AUTO: Sets `line`.
            line = tok.line or 1

            # LINE: Ignore comments/newlines when the grammar is not asking for them.
            if token_type in self.skip_token_types and top != token_type:
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Skips to the next loop iteration.
                continue

            # LINE: Non-terminal case, such as <program> or <statement>.
            if top in self.parsing_table:
                # Non-terminal case: use parsing_table[top][lookahead] to pick
                # the correct production from the CFG.
                # LINE: Get the parse-table row for this non-terminal.
                row = self.parsing_table[top]
                # LINE: If lookahead exists in this row, we know which production to use.
                if token_type in row:
                    # LINE: Select the CFG production predicted by this lookahead token.
                    production = row[token_type]
                    
                    # AUTO: Checks this condition.
                    if top == '<statement>' and token_type != '}' and reclaim_seen_stack and reclaim_seen_stack[-1]:
                        # AUTO: Returns this result to the caller.
                        return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after 'reclaim'. Expected: '}}'."]

                    # AUTO: Checks this condition.
                    if top == '<statement>' and token_type == '}':
                        # AUTO: Calls `=`.
                        is_epsilon = (len(production) == 0 or (len(production) == 1 and production[0] in self.epsilon_symbols))
                        # AUTO: Checks this condition.
                        if is_epsilon:
                            # AUTO: Sets `lookback`.
                            lookback = index - 1
                            # AUTO: Repeats while this condition is true.
                            while lookback >= 0 and toks[lookback].type in self.skip_token_types:
                                # AUTO: Subtracts from `lookback`.
                                lookback -= 1
                            
                            # AUTO: Checks this condition.
                            if lookback >= 0 and toks[lookback].type == '{':
                                # AUTO: Sets `before_brace`.
                                before_brace = lookback - 1
                                # AUTO: Repeats while this condition is true.
                                while before_brace >= 0 and toks[before_brace].type in self.skip_token_types:
                                    # AUTO: Subtracts from `before_brace`.
                                    before_brace -= 1
                                
                                # AUTO: Checks this condition.
                                if before_brace >= 0 and toks[before_brace].type == ')':
                                    # AUTO: Sets `paren_depth`.
                                    paren_depth = 1
                                    # AUTO: Sets `paren_pos`.
                                    paren_pos = before_brace - 1
                                    # AUTO: Repeats while this condition is true.
                                    while paren_pos >= 0 and paren_depth > 0:
                                        # AUTO: Checks this condition.
                                        if toks[paren_pos].type == ')':
                                            # AUTO: Adds into `paren_depth`.
                                            paren_depth += 1
                                        # AUTO: Checks the next alternate condition.
                                        elif toks[paren_pos].type == '(':
                                            # AUTO: Subtracts from `paren_depth`.
                                            paren_depth -= 1
                                        # AUTO: Subtracts from `paren_pos`.
                                        paren_pos -= 1
                                    
                                    # AUTO: Checks this condition.
                                    if paren_pos >= 0:
                                        # AUTO: Sets `kw_pos`.
                                        kw_pos = paren_pos
                                        # AUTO: Repeats while this condition is true.
                                        while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:
                                            # AUTO: Subtracts from `kw_pos`.
                                            kw_pos -= 1
                                        
                                        # AUTO: Checks this condition.
                                        if kw_pos >= 0:
                                            # AUTO: Sets `kw`.
                                            kw = toks[kw_pos]
                                            # AUTO: Sets `conditional_keywords`.
                                            conditional_keywords = {'spring', 'bud', 'wither', 'grow', 'cultivate', 'tend', 'harvest'}
                                            # AUTO: Checks this condition.
                                            if kw.type in conditional_keywords:
                                                # AUTO: Returns this result to the caller.
                                                return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
                                
                                # AUTO: Checks the next alternate condition.
                                elif before_brace >= 0 and toks[before_brace].type in {'wither', 'tend'}:
                                    # AUTO: Sets `kw`.
                                    kw = toks[before_brace]
                                    # AUTO: Returns this result to the caller.
                                    return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
                    
                    # LINE: Remove the non-terminal before replacing it with its production.
                    stack.pop()

                    # AUTO: Checks this condition.
                    if not (
                        # AUTO: Executes this statement.
                        len(production) == 0
                        # AUTO: Calls `or`.
                        or (len(production) == 1 and production[0] in self.epsilon_symbols)
                    # AUTO: Closes the current grouped code/data.
                    ):
                        # Push production in reverse so the leftmost grammar
                        # symbol is processed next.
                        # LINE: Push RHS in reverse so the first RHS symbol becomes stack top.
                        stack.extend(reversed(production))
                    # AUTO: Skips to the next loop iteration.
                    continue

                # LINE: If lookahead is not in row, parser knows this is a syntax error.
                expected = set(row.keys())
                
                # AUTO: Checks this condition.
                if token_type in {'variety', 'soil'} and token_type not in expected:
                    # AUTO: Repeats while this condition is true.
                    while index < len(toks) and toks[index].type != ';':
                        # AUTO: Checks this condition.
                        if toks[index].type == 'prune':
                            # AUTO: Adds into `index`.
                            index += 1
                            # AUTO: Stops the nearest loop.
                            break
                        # AUTO: Adds into `index`.
                        index += 1
                    # AUTO: Checks this condition.
                    if index < len(toks) and toks[index].type == ';':
                        # AUTO: Adds into `index`.
                        index += 1
                    # AUTO: Skips to the next loop iteration.
                    continue

                # LINE: Create a friendly expected-token message and stop parsing.
                error_msg = self._generate_helpful_error(top, token_type, token_value, line, tok.col, expected, index, toks)
                # AUTO: Returns this result to the caller.
                return False, [error_msg]

            # LINE: Terminal case, such as seed, id, ;, (, or =.
            if top == token_type:
                # Terminal case: grammar expected the same token type the lexer
                # produced, so consume it by popping stack and moving index.
                # LINE: Remember declared type when consuming a data-type token.
                if token_type in {'seed', 'tree', 'leaf', 'branch', 'vine'}:
                    # AUTO: Sets `current_var_type`.
                    current_var_type = token_type
                    # AUTO: Sets `expecting_value_for_type`.
                    expecting_value_for_type = None
                
                # AUTO: Checks the next alternate condition.
                elif token_type == '=' and current_var_type is not None:
                    # AUTO: Sets `expecting_value_for_type`.
                    expecting_value_for_type = current_var_type
                
                # AUTO: Checks the next alternate condition.
                elif expecting_value_for_type is not None and token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'sunshine', 'frost', 'id'}:
                    # AUTO: Sets `type_value_map`.
                    type_value_map = {
                        # AUTO: Executes this statement.
                        'seed': {'intlit', 'dblit'},
                        # AUTO: Executes this statement.
                        'tree': {'dblit', 'intlit'},
                        # AUTO: Executes this statement.
                        'leaf': {'chrlit'},
                        # AUTO: Executes this statement.
                        'branch': {'sunshine', 'frost'},
                        # AUTO: Executes this statement.
                        'vine': {'stringlit'}
                    # AUTO: Closes the current grouped code/data.
                    }
                    
                    # AUTO: Checks this condition.
                    if token_type == 'id':
                        # AUTO: Sets `expecting_value_for_type`.
                        expecting_value_for_type = None
                        # AUTO: Removes and returns an item.
                        stack.pop()
                        # AUTO: Adds into `index`.
                        index += 1
                        # AUTO: Skips to the next loop iteration.
                        continue
                    
                    # AUTO: Sets `expected_value_types`.
                    expected_value_types = type_value_map.get(expecting_value_for_type, set())
                    
                    # AUTO: Checks this condition.
                    if token_type not in expected_value_types:
                        # AUTO: Sets `type_names`.
                        type_names = {
                            # AUTO: Executes this statement.
                            'seed': 'integer (seed)',
                            # AUTO: Executes this statement.
                            'tree': 'double (tree)',
                            # AUTO: Executes this statement.
                            'leaf': 'character (leaf)',
                            # AUTO: Executes this statement.
                            'branch': 'boolean (branch)',
                            # AUTO: Executes this statement.
                            'vine': 'string (vine)'
                        # AUTO: Closes the current grouped code/data.
                        }
                        # AUTO: Sets `value_type_names`.
                        value_type_names = {
                            # AUTO: Executes this statement.
                            'intlit': 'integer',
                            # AUTO: Executes this statement.
                            'dblit': 'double',
                            # AUTO: Executes this statement.
                            'stringlit': 'string',
                            # AUTO: Executes this statement.
                            'chrlit': 'character',
                            # AUTO: Executes this statement.
                            'sunshine': 'boolean',
                            # AUTO: Executes this statement.
                            'frost': 'boolean',
                            # AUTO: Executes this statement.
                            'id': 'identifier'
                        # AUTO: Closes the current grouped code/data.
                        }
                        
                        # AUTO: Sets `declared_type`.
                        declared_type = type_names.get(expecting_value_for_type, expecting_value_for_type)
                        # AUTO: Sets `actual_type`.
                        actual_type = value_type_names.get(token_type, token_type)
                        
                        # AUTO: Sets `error_msg`.
                        error_msg = f"SEMANTIC error line {line} col {tok.col} Type mismatch: cannot assign {actual_type} value '{token_value}' to {declared_type} variable"
                        # AUTO: Returns this result to the caller.
                        return False, [error_msg]
                    
                    # AUTO: Checks this condition.
                    if token_type == 'chrlit' and expecting_value_for_type == 'leaf':
                        # AUTO: Executes this statement.
                        char_content = token_value[1:-1] if len(token_value) >= 2 else token_value
                        # AUTO: Checks this condition.
                        if len(char_content) == 0:
                            # AUTO: Sets `error_msg`.
                            error_msg = f"SYNTAX error line {line} col {tok.col} Character literal cannot be empty. Expected a single character for leaf variable"
                            # AUTO: Returns this result to the caller.
                            return False, [error_msg]
                        # AUTO: Checks the next alternate condition.
                        elif char_content.startswith('\\') and len(char_content) == 2:
                            # AUTO: Does nothing for this required block.
                            pass
                        # AUTO: Checks the next alternate condition.
                        elif len(char_content) > 1:
                            # AUTO: Sets `error_msg`.
                            error_msg = f"SYNTAX error line {line} col {tok.col} Character literal '{token_value}' contains {len(char_content)} characters. leaf variables can only hold a single character"
                            # AUTO: Returns this result to the caller.
                            return False, [error_msg]
                    
                    
                    # AUTO: Sets `expecting_value_for_type`.
                    expecting_value_for_type = None
                
                # AUTO: Checks the next alternate condition.
                elif token_type == ';':
                    # AUTO: Sets `current_var_type`.
                    current_var_type = None
                    # AUTO: Sets `expecting_value_for_type`.
                    expecting_value_for_type = None
                
                # AUTO: Checks this condition.
                if top == 'intlit' or top == 'dblit':
                    # AUTO: Sets `lookback`.
                    lookback = index - 1
                    # AUTO: Repeats while this condition is true.
                    while lookback >= 0 and toks[lookback].type in self.skip_token_types:
                        # AUTO: Subtracts from `lookback`.
                        lookback -= 1
                    
                    # AUTO: Checks this condition.
                    if lookback >= 0 and toks[lookback].type == '(':
                        # AUTO: Sets `kw_pos`.
                        kw_pos = lookback - 1
                        # AUTO: Repeats while this condition is true.
                        while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:
                            # AUTO: Subtracts from `kw_pos`.
                            kw_pos -= 1
                        
                        # AUTO: Checks this condition.
                        if kw_pos >= 0:
                            # AUTO: Sets `kw`.
                            kw = toks[kw_pos]
                            # AUTO: Sets `condition_keywords`.
                            condition_keywords = {'spring', 'grow', 'cultivate', 'tend', 'bud'}
                            # AUTO: Checks this condition.
                            if kw.type in condition_keywords:
                                # AUTO: Sets `next_idx`.
                                next_idx = index + 1
                                # AUTO: Repeats while this condition is true.
                                while next_idx < len(toks) and toks[next_idx].type in self.skip_token_types:
                                    # AUTO: Adds into `next_idx`.
                                    next_idx += 1
                                
                                # AUTO: Checks this condition.
                                if next_idx < len(toks) and toks[next_idx].type == ')':
                                    # AUTO: Returns this result to the caller.
                                    return False, [f"SYNTAX error line {line} col {tok.col} '{kw.value}' requires a boolean condition, not a numeric literal"]
                
                # AUTO: Checks this condition.
                if token_type in {'&&', '||'}:
                    # AUTO: Sets `prev_idx`.
                    prev_idx = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_idx >= 0 and toks[prev_idx].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_idx`.
                        prev_idx -= 1
                    # AUTO: Checks this condition.
                    if prev_idx >= 0:
                        # AUTO: Sets `prev_tok`.
                        prev_tok = toks[prev_idx]
                        # AUTO: Sets `non_branch_literals`.
                        non_branch_literals = {'intlit', 'dblit', 'stringlit', 'chrlit'}
                        # AUTO: Checks this condition.
                        if prev_tok.type in non_branch_literals:
                            # AUTO: Sets `cmp_idx`.
                            cmp_idx = prev_idx - 1
                            # AUTO: Repeats while this condition is true.
                            while cmp_idx >= 0 and toks[cmp_idx].type in self.skip_token_types:
                                # AUTO: Subtracts from `cmp_idx`.
                                cmp_idx -= 1
                            # AUTO: Executes this statement.
                            comparison_ops = {'<', '>', '<=', '>=', '==', '!='}
                            # AUTO: Checks this condition.
                            if cmp_idx >= 0 and toks[cmp_idx].type in comparison_ops:
                                # AUTO: Does nothing for this required block.
                                pass
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Sets `type_names`.
                                type_names = {
                                    # AUTO: Executes this statement.
                                    'intlit': 'integer literal',
                                    # AUTO: Executes this statement.
                                    'dblit': 'double literal',
                                    # AUTO: Executes this statement.
                                    'stringlit': 'string literal',
                                    # AUTO: Executes this statement.
                                    'chrlit': 'character literal',
                                # AUTO: Closes the current grouped code/data.
                                }
                                # AUTO: Executes this statement.
                                op_name = 'AND' if token_type == '&&' else 'OR'
                                # AUTO: Returns this result to the caller.
                                return False, [f"SYNTAX error line {line} col {tok.col} Logical operator '{token_type}' ({op_name}) requires branch operands, not {type_names[prev_tok.type]} '{prev_tok.value}'"]
                
                # AUTO: Checks this condition.
                if token_type in {'intlit', 'dblit', 'stringlit', 'chrlit'}:
                    # AUTO: Sets `prev_idx`.
                    prev_idx = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_idx >= 0 and toks[prev_idx].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_idx`.
                        prev_idx -= 1
                    # AUTO: Checks this condition.
                    if prev_idx >= 0 and toks[prev_idx].type in {'&&', '||'}:
                        # AUTO: Sets `next_check`.
                        next_check = index + 1
                        # AUTO: Repeats while this condition is true.
                        while next_check < len(toks) and toks[next_check].type in self.skip_token_types:
                            # AUTO: Adds into `next_check`.
                            next_check += 1
                        # AUTO: Executes this statement.
                        comparison_ops = {'<', '>', '<=', '>=', '==', '!='}
                        # AUTO: Checks this condition.
                        if next_check < len(toks) and toks[next_check].type in comparison_ops:
                            # AUTO: Does nothing for this required block.
                            pass
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Sets `type_names`.
                            type_names = {
                                # AUTO: Executes this statement.
                                'intlit': 'integer literal',
                                # AUTO: Executes this statement.
                                'dblit': 'double literal',
                                # AUTO: Executes this statement.
                                'stringlit': 'string literal',
                                # AUTO: Executes this statement.
                                'chrlit': 'character literal',
                            # AUTO: Closes the current grouped code/data.
                            }
                            # AUTO: Executes this statement.
                            op_name = 'AND' if toks[prev_idx].type == '&&' else 'OR'
                            # AUTO: Returns this result to the caller.
                            return False, [f"SYNTAX error line {line} col {tok.col} Logical operator '{toks[prev_idx].type}' ({op_name}) requires branch operands, not {type_names[token_type]} '{token_value}'"]

                # AUTO: Checks this condition.
                if token_type == '{':
                    # AUTO: Appends a value to a list.
                    reclaim_seen_stack.append(False)
                # AUTO: Checks the next alternate condition.
                elif token_type == '}':
                    # AUTO: Checks this condition.
                    if reclaim_seen_stack:
                        # AUTO: Removes and returns an item.
                        reclaim_seen_stack.pop()
                # AUTO: Checks the next alternate condition.
                elif token_type == 'reclaim':
                    # AUTO: Checks this condition.
                    if reclaim_seen_stack:
                        # AUTO: Sets `reclaim_seen_stack[-1]`.
                        reclaim_seen_stack[-1] = True

                # LINE: Matched terminal is done, so remove it from the stack.
                stack.pop()
                # LINE: Move to the next lexer token.
                index += 1
                # AUTO: Skips to the next loop iteration.
                continue

            # LINE: EOF can pass over skipped comments/newlines.
            if top == self.end_marker and token_type in self.skip_token_types:
                # AUTO: Adds into `index`.
                index += 1
                # AUTO: Skips to the next loop iteration.
                continue

            # LINE: If stack terminal and token do not match, build syntax error.
            expected = {top}
            # AUTO: Executes this statement.
            shown_value = "end of file" if token_type == self.end_marker else token_value
            
            # AUTO: Checks this condition.
            if token_type == self.end_marker:
                # AUTO: Sets `error_msg`.
                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected end of file. Expected: '{top}'. Missing closing '}}' or incomplete statement."
                # AUTO: Returns this result to the caller.
                return False, [error_msg]
            
            # AUTO: Checks this condition.
            if top == 'grow' and token_type == '(':
                # AUTO: Sets `scan_idx`.
                scan_idx = index - 1
                # AUTO: Repeats while this condition is true.
                while scan_idx >= 0 and toks[scan_idx].type in self.skip_token_types:
                    # AUTO: Subtracts from `scan_idx`.
                    scan_idx -= 1
                # AUTO: Checks this condition.
                if scan_idx >= 0 and toks[scan_idx].type == '}':
                    # AUTO: Sets `brace_depth`.
                    brace_depth = 1
                    # AUTO: Subtracts from `scan_idx`.
                    scan_idx -= 1
                    # AUTO: Repeats while this condition is true.
                    while scan_idx >= 0 and brace_depth > 0:
                        # AUTO: Checks this condition.
                        if toks[scan_idx].type == '}':
                            # AUTO: Adds into `brace_depth`.
                            brace_depth += 1
                        # AUTO: Checks the next alternate condition.
                        elif toks[scan_idx].type == '{':
                            # AUTO: Subtracts from `brace_depth`.
                            brace_depth -= 1
                        # AUTO: Subtracts from `scan_idx`.
                        scan_idx -= 1
                    # AUTO: Sets `kw_idx`.
                    kw_idx = scan_idx
                    # AUTO: Repeats while this condition is true.
                    while kw_idx >= 0 and toks[kw_idx].type in self.skip_token_types:
                        # AUTO: Subtracts from `kw_idx`.
                        kw_idx -= 1
                    # AUTO: Checks this condition.
                    if kw_idx >= 0 and toks[kw_idx].type == 'tend':
                        # AUTO: Sets `error_msg`.
                        error_msg = f"SYNTAX error line {line} col {tok.col} Missing 'grow' keyword before '('. {self._format_expected(expected, top)}. Correct format: tend {{ ... }} grow (condition);"
                        # AUTO: Returns this result to the caller.
                        return False, [error_msg]
            
            # AUTO: Checks this condition.
            if top == 'reclaim' and token_type == '}':
                # AUTO: Sets `is_root`.
                is_root = False
                # AUTO: Starts a loop over these values.
                for i in range(index - 1, -1, -1):
                    # AUTO: Checks this condition.
                    if toks[i].type == 'root':
                        # AUTO: Sets `is_root`.
                        is_root = True
                        # AUTO: Stops the nearest loop.
                        break
                    # AUTO: Checks the next alternate condition.
                    elif toks[i].type == 'pollinate':
                        # AUTO: Sets `is_root`.
                        is_root = False
                        # AUTO: Stops the nearest loop.
                        break
                
                # AUTO: Checks this condition.
                if is_root:
                    # AUTO: Sets `error_msg`.
                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'reclaim;' before '}}'. The root() function (main program) must end with 'reclaim;'. {self._format_expected(expected)}"
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Sets `error_msg`.
                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'reclaim;' before '}}'. All functions must end with 'reclaim;'. {self._format_expected(expected)}"
                # AUTO: Returns this result to the caller.
                return False, [error_msg]
            # AUTO: Checks the next alternate condition.
            elif top == 'prune' and token_type in {'variety', 'soil', '}'}:
                # AUTO: Checks this condition.
                if token_type == 'variety':
                    # AUTO: Sets `error_msg`.
                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'prune;' before next 'variety'. Each case in 'harvest' must end with 'prune;'. {self._format_expected(expected)}"
                # AUTO: Checks the next alternate condition.
                elif token_type == 'soil':
                    # AUTO: Sets `error_msg`.
                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'prune;' before 'soil'. Each case must end with 'prune;'. {self._format_expected(expected)}"
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Sets `error_msg`.
                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'prune;' before closing '}}'. Each case must end with 'prune;'. {self._format_expected(expected)}"
                # AUTO: Returns this result to the caller.
                return False, [error_msg]
            # AUTO: Checks the next alternate condition.
            elif top == '(' and token_type != '(':
                # AUTO: Checks this condition.
                if token_type in {'=', '+=', '-=', '*=', '/=', '%='}:
                    # AUTO: Sets `error_msg`.
                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected, top)}"
                # AUTO: Checks the next alternate condition.
                elif index > 0:
                    # AUTO: Sets `prev_index`.
                    prev_index = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_index`.
                        prev_index -= 1
                    
                    # AUTO: Checks this condition.
                    if prev_index >= 0:
                        # AUTO: Sets `prev_tok`.
                        prev_tok = toks[prev_index]
                        
                        # AUTO: Checks this condition.
                        if prev_tok.type == '}':
                            # AUTO: Sets `brace_depth`.
                            brace_depth = 1
                            # AUTO: Sets `scan_idx`.
                            scan_idx = prev_index - 1
                            # AUTO: Repeats while this condition is true.
                            while scan_idx >= 0 and brace_depth > 0:
                                # AUTO: Checks this condition.
                                if toks[scan_idx].type == '}':
                                    # AUTO: Adds into `brace_depth`.
                                    brace_depth += 1
                                # AUTO: Checks the next alternate condition.
                                elif toks[scan_idx].type == '{':
                                    # AUTO: Subtracts from `brace_depth`.
                                    brace_depth -= 1
                                # AUTO: Subtracts from `scan_idx`.
                                scan_idx -= 1
                            
                            # AUTO: Checks this condition.
                            if scan_idx >= 0:
                                # AUTO: Sets `kw_idx`.
                                kw_idx = scan_idx
                                # AUTO: Repeats while this condition is true.
                                while kw_idx >= 0 and toks[kw_idx].type in self.skip_token_types:
                                    # AUTO: Subtracts from `kw_idx`.
                                    kw_idx -= 1
                                
                                # AUTO: Checks this condition.
                                if kw_idx >= 0 and toks[kw_idx].type == 'tend':
                                    # AUTO: Sets `error_msg`.
                                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. 'tend' requires 'grow' after closing brace '}}'. Correct format: tend {{ ... }} grow (condition); {self._format_expected(expected)}"
                                # AUTO: Runs when previous condition did not pass.
                                else:
                                    # AUTO: Sets `error_msg`.
                                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Sets `error_msg`.
                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Sets `keywords_needing_parens`.
                            keywords_needing_parens = {'spring', 'grow', 'cultivate', 'harvest', 'water', 'plant', 'tend', 'bud'}
                            # AUTO: Checks this condition.
                            if prev_tok.type in keywords_needing_parens:
                                # AUTO: Sets `error_msg`.
                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{prev_tok.value}'. {self._format_expected(expected)}"
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Sets `error_msg`.
                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Sets `error_msg`.
                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Sets `error_msg`.
                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                # AUTO: Returns this result to the caller.
                return False, [error_msg]
            # AUTO: Checks the next alternate condition.
            elif top == '{' and token_type != '{':
                # AUTO: Sets `error_msg`.
                error_msg = None
                # AUTO: Checks this condition.
                if token_type == ')' and index > 0:
                    # AUTO: Sets `prev_index`.
                    prev_index = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_index`.
                        prev_index -= 1
                    
                    # AUTO: Checks this condition.
                    if prev_index >= 0 and toks[prev_index].type == ')':
                        # AUTO: Sets `paren_index`.
                        paren_index = prev_index - 1
                        # AUTO: Sets `paren_count`.
                        paren_count = 1
                        # AUTO: Repeats while this condition is true.
                        while paren_index >= 0 and paren_count > 0:
                            # AUTO: Checks this condition.
                            if toks[paren_index].type == ')':
                                # AUTO: Adds into `paren_count`.
                                paren_count += 1
                            # AUTO: Checks the next alternate condition.
                            elif toks[paren_index].type == '(':
                                # AUTO: Subtracts from `paren_count`.
                                paren_count -= 1
                            # AUTO: Subtracts from `paren_index`.
                            paren_index -= 1
                        
                        # AUTO: Checks this condition.
                        if paren_index >= 0:
                            # AUTO: Sets `kw_index`.
                            kw_index = paren_index
                            # AUTO: Repeats while this condition is true.
                            while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:
                                # AUTO: Subtracts from `kw_index`.
                                kw_index -= 1
                            
                            # AUTO: Checks this condition.
                            if kw_index >= 0:
                                # AUTO: Sets `kw_tok`.
                                kw_tok = toks[kw_index]
                                # AUTO: Checks this condition.
                                if kw_tok.type in {'root', 'pollinate'}:
                                    # AUTO: Sets `error_msg`.
                                    error_msg = f"SYNTAX error line {line} col {tok.col} Extra closing ')' after '{kw_tok.value}()'. Correct syntax: {kw_tok.value}(){{ ... }}. {self._format_expected(expected)}"
                
                # AUTO: Checks this condition.
                if error_msg is None and index > 0:
                    # AUTO: Sets `prev_index`.
                    prev_index = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_index`.
                        prev_index -= 1
                    
                    # AUTO: Checks this condition.
                    if prev_index >= 0:
                        # AUTO: Sets `prev_tok`.
                        prev_tok = toks[prev_index]
                        # AUTO: Sets `keywords_needing_braces`.
                        keywords_needing_braces = {'spring', 'wither', 'grow', 'cultivate', 'tend', 'harvest', 'bud', ')', 'pollinate', 'root'}
                        # AUTO: Checks this condition.
                        if prev_tok.type in keywords_needing_braces:
                            # AUTO: Checks this condition.
                            if prev_tok.type == ')':
                                # AUTO: Sets `paren_index`.
                                paren_index = prev_index - 1
                                # AUTO: Sets `paren_count`.
                                paren_count = 1
                                # AUTO: Repeats while this condition is true.
                                while paren_index >= 0 and paren_count > 0:
                                    # AUTO: Checks this condition.
                                    if toks[paren_index].type == ')':
                                        # AUTO: Adds into `paren_count`.
                                        paren_count += 1
                                    # AUTO: Checks the next alternate condition.
                                    elif toks[paren_index].type == '(':
                                        # AUTO: Subtracts from `paren_count`.
                                        paren_count -= 1
                                    # AUTO: Subtracts from `paren_index`.
                                    paren_index -= 1
                                
                                # AUTO: Checks this condition.
                                if paren_index >= 0:
                                    # AUTO: Sets `kw_index`.
                                    kw_index = paren_index
                                    # AUTO: Repeats while this condition is true.
                                    while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:
                                        # AUTO: Subtracts from `kw_index`.
                                        kw_index -= 1
                                    
                                    # AUTO: Checks this condition.
                                    if kw_index >= 0:
                                        # AUTO: Sets `kw_tok`.
                                        kw_tok = toks[kw_index]
                                        # AUTO: Checks this condition.
                                        if kw_tok.type in {'spring', 'grow', 'cultivate', 'tend', 'harvest', 'bud', 'pollinate', 'root'}:
                                            # AUTO: Sets `error_msg`.
                                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{kw_tok.value}' statement. {self._format_expected(expected)}"
                                        # AUTO: Runs when previous condition did not pass.
                                        else:
                                            # AUTO: Sets `error_msg`.
                                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                                    # AUTO: Runs when previous condition did not pass.
                                    else:
                                        # AUTO: Sets `error_msg`.
                                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                                # AUTO: Runs when previous condition did not pass.
                                else:
                                    # AUTO: Sets `error_msg`.
                                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Sets `error_msg`.
                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{prev_tok.value}'. {self._format_expected(expected)}"
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Sets `error_msg`.
                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Sets `error_msg`.
                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                # AUTO: Checks the next alternate condition.
                elif error_msg is None:
                    # AUTO: Sets `error_msg`.
                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                # AUTO: Returns this result to the caller.
                return False, [error_msg]
            # AUTO: Checks the next alternate condition.
            elif top == '}' and token_type != '}':
                # AUTO: Returns this result to the caller.
                return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. Missing closing brace. {self._format_expected(expected)}"]
            # AUTO: Checks the next alternate condition.
            elif top == ')' and token_type != ')':
                # AUTO: Returns this result to the caller.
                return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"]
            # AUTO: Checks the next alternate condition.
            elif top == ':' and token_type != ':':
                # AUTO: Sets `context_keyword`.
                context_keyword = None
                # AUTO: Checks this condition.
                if index > 0:
                    # AUTO: Sets `prev_index`.
                    prev_index = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_index`.
                        prev_index -= 1
                    # AUTO: Checks this condition.
                    if prev_index >= 0:
                        # AUTO: Sets `prev_tok`.
                        prev_tok = toks[prev_index]
                        # AUTO: Checks this condition.
                        if prev_tok.type == 'soil':
                            # AUTO: Sets `context_keyword`.
                            context_keyword = 'soil'
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Sets `scan`.
                            scan = prev_index
                            # AUTO: Repeats while this condition is true.
                            while scan >= 0:
                                # AUTO: Checks this condition.
                                if toks[scan].type in self.skip_token_types:
                                    # AUTO: Subtracts from `scan`.
                                    scan -= 1
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                # AUTO: Checks this condition.
                                if toks[scan].type == 'variety':
                                    # AUTO: Sets `context_keyword`.
                                    context_keyword = 'variety'
                                    # AUTO: Stops the nearest loop.
                                    break
                                # AUTO: Checks this condition.
                                if toks[scan].type in {'id', 'intlit', 'dblit', 'stringlit', 'chrlit',
                                                       # AUTO: Executes this statement.
                                                       'sunshine', 'frost', '+', '-', '*', '/', '%',
                                                       # AUTO: Executes this statement.
                                                       '==', '!=', '<', '>', '<=', '>=', '&&', '||',
                                                       # AUTO: Executes this statement.
                                                       '(', ')', '`', '~'}:
                                    # AUTO: Subtracts from `scan`.
                                    scan -= 1
                                    # AUTO: Skips to the next loop iteration.
                                    continue
                                # AUTO: Stops the nearest loop.
                                break
                # AUTO: Checks this condition.
                if context_keyword:
                    # AUTO: Returns this result to the caller.
                    return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{context_keyword}'. {self._format_expected({':'})}"]
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Returns this result to the caller.
                    return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected({':'})}"]
            # AUTO: Checks the next alternate condition.
            elif top == ';' and token_type != ';':
                # AUTO: Sets `common_keyword_mistakes`.
                common_keyword_mistakes = {
                    # AUTO: Executes this statement.
                    'function': 'pollinate', 'int': 'seed', 'float': 'tree', 'double': 'tree',
                    # AUTO: Executes this statement.
                    'char': 'leaf', 'bool': 'branch', 'boolean': 'branch', 'if': 'spring',
                    # AUTO: Executes this statement.
                    'else': 'wither', 'elif': 'bud', 'while': 'grow', 'for': 'cultivate',
                    # AUTO: Executes this statement.
                    'switch': 'harvest', 'case': 'variety', 'default': 'soil', 'break': 'prune',
                    # AUTO: Executes this statement.
                    'continue': 'skip', 'return': 'reclaim', 'void': 'empty', 'const': 'fertile',
                    # AUTO: Executes this statement.
                    'struct': 'bundle', 'string': 'vine', 'printf': 'plant', 'scanf': 'water',
                    # AUTO: Executes this statement.
                    'print': 'plant', 'input': 'water'
                # AUTO: Closes the current grouped code/data.
                }
                
                # AUTO: Sets `error_msg`.
                error_msg = None
                # AUTO: Checks this condition.
                if token_type == '{' and index > 0:
                    # AUTO: Sets `paren_idx`.
                    paren_idx = index - 1
                    # AUTO: Repeats while this condition is true.
                    while paren_idx >= 0 and toks[paren_idx].type in self.skip_token_types:
                        # AUTO: Subtracts from `paren_idx`.
                        paren_idx -= 1
                    
                    # AUTO: Checks this condition.
                    if paren_idx >= 0 and toks[paren_idx].type == ')':
                        # AUTO: Sets `paren_depth`.
                        paren_depth = 1
                        # AUTO: Subtracts from `paren_idx`.
                        paren_idx -= 1
                        # AUTO: Repeats while this condition is true.
                        while paren_idx >= 0 and paren_depth > 0:
                            # AUTO: Checks this condition.
                            if toks[paren_idx].type == ')':
                                # AUTO: Adds into `paren_depth`.
                                paren_depth += 1
                            # AUTO: Checks the next alternate condition.
                            elif toks[paren_idx].type == '(':
                                # AUTO: Subtracts from `paren_depth`.
                                paren_depth -= 1
                            # AUTO: Subtracts from `paren_idx`.
                            paren_idx -= 1
                        
                        # AUTO: Checks this condition.
                        if paren_idx >= 0:
                            # AUTO: Sets `id_idx`.
                            id_idx = paren_idx
                            # AUTO: Repeats while this condition is true.
                            while id_idx >= 0 and toks[id_idx].type in self.skip_token_types:
                                # AUTO: Subtracts from `id_idx`.
                                id_idx -= 1
                            
                            # AUTO: Checks this condition.
                            if id_idx >= 0 and toks[id_idx].type == 'id' and toks[id_idx].value in common_keyword_mistakes:
                                # AUTO: Sets `keyword_tok`.
                                keyword_tok = toks[id_idx]
                                # AUTO: Sets `correct_keyword`.
                                correct_keyword = common_keyword_mistakes[keyword_tok.value]
                                # AUTO: Sets `error_msg`.
                                error_msg = f"SYNTAX error line {keyword_tok.line} col {keyword_tok.col} '{keyword_tok.value}' is not a GAL keyword. Use '{correct_keyword}' instead."
                
                # AUTO: Checks this condition.
                if error_msg is None and token_type == 'id' and token_value in common_keyword_mistakes:
                    # AUTO: Sets `correct_keyword`.
                    correct_keyword = common_keyword_mistakes[token_value]
                    # AUTO: Sets `error_msg`.
                    error_msg = f"SYNTAX error line {line} col {tok.col} '{token_value}' is not a GAL keyword. Use '{correct_keyword}' instead."
                
                # AUTO: Checks this condition.
                if error_msg is None and token_type in {'++', '--'} and index > 0:
                    # AUTO: Sets `prev_index`.
                    prev_index = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_index`.
                        prev_index -= 1
                    
                    # AUTO: Checks this condition.
                    if prev_index >= 0:
                        # AUTO: Sets `prev_tok`.
                        prev_tok = toks[prev_index]
                        # AUTO: Checks this condition.
                        if prev_tok.type in {'++', '--'}:
                            # AUTO: Sets `error_msg`.
                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{prev_tok.value}'. Increment/decrement operators cannot be chained. {self._format_expected(expected)}"
                
                # AUTO: Executes this statement.
                binary_operators = {'+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||'}
                # AUTO: Checks this condition.
                if error_msg is None and token_type in binary_operators and index > 0:
                    # AUTO: Sets `prev_index`.
                    prev_index = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_index`.
                        prev_index -= 1
                    
                    # AUTO: Checks this condition.
                    if prev_index >= 0:
                        # AUTO: Sets `prev_tok`.
                        prev_tok = toks[prev_index]
                        # AUTO: Checks this condition.
                        if prev_tok.type in {'++', '--'}:
                            # AUTO: Sets `error_msg`.
                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected binary operator '{token_value}' after unary operator '{prev_tok.value}'. Increment/decrement must be standalone statements. {self._format_expected(expected)}"
                
                # AUTO: Checks this condition.
                if error_msg is None:
                    # AUTO: Checks this condition.
                    if index > 0:
                        # AUTO: Sets `prev_index`.
                        prev_index = index - 1
                        # AUTO: Repeats while this condition is true.
                        while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                            # AUTO: Subtracts from `prev_index`.
                            prev_index -= 1
                        
                        # AUTO: Checks this condition.
                        if prev_index >= 0:
                            # AUTO: Sets `prev_tok`.
                            prev_tok = toks[prev_index]
                            # AUTO: Sets `error_msg`.
                            error_msg = f"SYNTAX error line {prev_tok.line} col {prev_tok.col + len(str(prev_tok.value))} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                            # AUTO: Sets `line`.
                            line = prev_tok.line
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Sets `error_msg`.
                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Sets `error_msg`.
                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                
                # AUTO: Returns this result to the caller.
                return False, [error_msg]
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Checks this condition.
                if top == 'id' and token_type == '(' and index > 0:
                    # AUTO: Sets `prev_index`.
                    prev_index = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_index`.
                        prev_index -= 1
                    # AUTO: Checks this condition.
                    if prev_index >= 0 and toks[prev_index].type == 'id':
                        # AUTO: Sets `kw_index`.
                        kw_index = prev_index - 1
                        # AUTO: Repeats while this condition is true.
                        while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:
                            # AUTO: Subtracts from `kw_index`.
                            kw_index -= 1
                        # AUTO: Checks this condition.
                        if kw_index >= 0 and toks[kw_index].type == 'pollinate':
                            # AUTO: Sets `func_name`.
                            func_name = toks[prev_index].value
                            # AUTO: Returns this result to the caller.
                            return False, [f"SYNTAX error line {toks[kw_index].line} col {toks[kw_index].col} Missing return type after 'pollinate'. '{func_name}' was parsed as the return type, not the function name. Expected: 'branch', 'empty', 'leaf', 'seed', 'tree', 'vine'"]

                # AUTO: Checks this condition.
                if top == 'id' and token_type == ')' and index > 0:
                    # AUTO: Sets `prev_index`.
                    prev_index = index - 1
                    # AUTO: Repeats while this condition is true.
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        # AUTO: Subtracts from `prev_index`.
                        prev_index -= 1
                    # AUTO: Checks this condition.
                    if prev_index >= 0 and toks[prev_index].type == 'id':
                        # AUTO: Sets `comma_index`.
                        comma_index = prev_index - 1
                        # AUTO: Repeats while this condition is true.
                        while comma_index >= 0 and toks[comma_index].type in self.skip_token_types:
                            # AUTO: Subtracts from `comma_index`.
                            comma_index -= 1
                        # AUTO: Checks this condition.
                        if comma_index >= 0 and toks[comma_index].type == ',':
                            # AUTO: Sets `param_name`.
                            param_name = toks[prev_index].value
                            # AUTO: Sets `param_expected`.
                            param_expected = {'seed', 'tree', 'leaf', 'vine', 'branch'}
                            # AUTO: Returns this result to the caller.
                            return False, [f"SYNTAX error line {toks[prev_index].line} col {toks[prev_index].col} Missing type for parameter '{param_name}'. Each parameter requires a type. {self._format_expected(param_expected)}"]

                # AUTO: Sets `error_msg`.
                error_msg = self._generate_helpful_error(
                    # AUTO: Executes this statement.
                    top, token_type, token_value, line, tok.col, expected, index, toks
                # AUTO: Closes the current grouped code/data.
                )
                # AUTO: Returns this result to the caller.
                return False, [error_msg]

        # AUTO: Repeats while this condition is true.
        while index < len(toks) and toks[index].type in self.skip_token_types:
            # AUTO: Adds into `index`.
            index += 1
        # AUTO: Checks this condition.
        if index < len(toks) and toks[index].type != self.end_marker:
            # AUTO: Sets `tok`.
            tok = toks[index]
            # AUTO: Returns this result to the caller.
            return False, [
                # AUTO: Executes this statement.
                f"SYNTAX error line {tok.line} col {tok.col} Unexpected token '{tok.value}' after program end. All code must be inside functions or global declarations. {self._format_expected({self.end_marker})}"
            # AUTO: Closes the current grouped code/data.
            ]
        
        # AUTO: Returns this result to the caller.
        return True, []

    # AUTO: Defines function `parse_and_build`.
    def parse_and_build(self, tokens: Sequence[Any]):
        # GUIDE: Public parser API used by server.py; syntax first, AST next.
        # LINE: Run LL(1) syntax validation before building AST.
        syntax_ok, syntax_errors = self.parse(tokens)
        # LINE: If syntax failed, return errors and do not call builder.py.
        if not syntax_ok:
            # AUTO: Sets `first_err`.
            first_err = syntax_errors[0] if syntax_errors else ""
            # LINE: Some parser checks intentionally return semantic-style messages.
            stage = "semantic" if first_err.startswith("SEMANTIC error") else "syntax"
            # AUTO: Returns this result to the caller.
            return {
                # AUTO: Executes this statement.
                "success": False,
                # AUTO: Executes this statement.
                "errors": syntax_errors,
                # AUTO: Executes this statement.
                "ast": None,
                # AUTO: Executes this statement.
                "symbol_table": {},
                # AUTO: Executes this statement.
                "error_stage": stage,
            # AUTO: Closes the current grouped code/data.
            }

        # AUTO: Starts protected code that can catch errors.
        try:
            # LINE: Remove comments/newlines because builder only needs meaningful tokens.
            filtered = [t for t in tokens if getattr(t, 'type', '') not in ('\n', 'comment', 'mcommentlit')]
            # LINE: Convert the token stream into AST nodes.
            ast = _build_ast(filtered)

            # LINE: Build frontend-friendly symbol table data from builder state.
            st = {
                # AUTO: Executes this statement.
                "variables": [
                    # AUTO: Executes this statement.
                    {
                        # AUTO: Executes this statement.
                        "name": name,
                        # AUTO: Executes this statement.
                        "type": info["type"],
                        # AUTO: Executes this statement.
                        "scope": "global",
                        # AUTO: Calls `info.get`.
                        "is_list": info.get("is_list", False),
                        # AUTO: Calls `info.get`.
                        "is_constant": info.get("is_fertile", False),
                    # AUTO: Closes the current grouped code/data.
                    }
                    # AUTO: Starts a loop over these values.
                    for name, info in _builder_st.variables.items()
                # AUTO: Closes the current grouped code/data.
                ],
                # AUTO: Executes this statement.
                "functions": {
                    # AUTO: Executes this statement.
                    name: {
                        # AUTO: Executes this statement.
                        "return_type": info["return_type"],
                        # AUTO: Executes this statement.
                        "params": [
                            # AUTO: Executes this statement.
                            {
                                # AUTO: Executes this statement.
                                "type": p.children[0].value if p.children else "unknown",
                                # AUTO: Executes this statement.
                                "name": p.children[1].value if len(p.children) > 1 else "unknown",
                            # AUTO: Closes the current grouped code/data.
                            }
                            # AUTO: Starts a loop over these values.
                            for p in info["params"]
                        # AUTO: Closes the current grouped code/data.
                        ] if info["params"] else [],
                    # AUTO: Closes the current grouped code/data.
                    }
                    # AUTO: Starts a loop over these values.
                    for name, info in _builder_st.functions.items()
                # AUTO: Closes the current grouped code/data.
                },
            # AUTO: Closes the current grouped code/data.
            }

            # LINE: Return AST and symbol table to semantic/interpreter stages.
            return {
                # AUTO: Executes this statement.
                "success": True,
                # AUTO: Executes this statement.
                "errors": [],
                # AUTO: Executes this statement.
                "ast": ast,
                # AUTO: Executes this statement.
                "symbol_table": st,
            # AUTO: Closes the current grouped code/data.
            }

        # AUTO: Handles the matching error case.
        except _SemanticError as e:
            # LINE: Builder semantic errors are returned as semantic stage failures.
            return {
                # AUTO: Executes this statement.
                "success": False,
                # AUTO: Executes this statement.
                "errors": [str(e)],
                # AUTO: Executes this statement.
                "ast": None,
                # AUTO: Executes this statement.
                "symbol_table": {},
                # AUTO: Executes this statement.
                "error_stage": "semantic",
            # AUTO: Closes the current grouped code/data.
            }
