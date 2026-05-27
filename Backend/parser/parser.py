from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from .builder import (
    build_ast as _build_ast,
    symbol_table as _builder_st,
)
from semantic.errors import SemanticError as _SemanticError


@dataclass(frozen=True)
class _TokView:
    type: str
    value: str
    line: int
    col: int = 0


def _as_tok(token: Any) -> _TokView:
    if isinstance(token, Mapping):
        return _TokView(
            type=str(token.get("type", "")),
            value=str(token.get("value", "")),
            line=int(token.get("line", 0) or 0),
            col=int(token.get("col", 0) or 0),
        )
    return _TokView(
        type=str(getattr(token, "type", "")),
        value=str(getattr(token, "value", "")),
        line=int(getattr(token, "line", 0) or 0),
        col=int(getattr(token, "col", 0) or 0),
    )


class LL1Parser:
    def __init__(
        self,
        cfg: Dict[str, List[List[str]]],
        predict_sets: Dict[Tuple[str, Tuple[str, ...]], Set[str]],
        first_sets: Dict[str, Set[str]],
        *,
        start_symbol: str = "<program>",
        end_marker: str = "EOF",
        epsilon_symbols: Iterable[str] = ("λ", "ε"),
        skip_token_types: Optional[Set[str]] = None,
        token_type_alias: Optional[Dict[str, str]] = None,
    ):
        self.cfg = cfg
        self.predict_sets = predict_sets
        self.first_sets = first_sets

        self.epsilon_symbols: Set[str] = set(epsilon_symbols)
        self.start_symbol = start_symbol
        self.end_marker = end_marker

        self.skip_token_types: Set[str] = set(skip_token_types or {"\n"})
        self.token_type_alias = token_type_alias or {
            'idf': 'id',
            'dbllit': 'dblit',
        }
        
        self.parsing_table: Dict[str, Dict[str, List[str]]] = self.construct_parsing_table()

    def construct_parsing_table(self) -> Dict[str, Dict[str, List[str]]]:
        table: Dict[str, Dict[str, List[str]]] = {}

        for non_terminal, productions in self.cfg.items():
            row: Dict[str, List[str]] = {}
            for production in productions:
                key = (non_terminal, tuple(production))
                terms = self.predict_sets.get(key, set())
                for terminal in terms:
                    if terminal in row and row[terminal] != production:
                        raise ValueError(
                            f"LL(1) conflict at {non_terminal} with lookahead {terminal}: "
                            f"{row[terminal]} vs {production}"
                        )
                    row[terminal] = production
            table[non_terminal] = row
        return table


    def _normalize_token_type(self, token_type: str) -> str:
        return self.token_type_alias.get(token_type, token_type)

    def _ensure_eof(self, toks: List[_TokView]) -> List[_TokView]:
        if not toks:
            return [_TokView(self.end_marker, self.end_marker, 1, 0)]
        if toks[-1].type != self.end_marker:
            last_line = toks[-1].line or 1
            last_col = toks[-1].col or 0
            toks = toks + [_TokView(self.end_marker, self.end_marker, last_line, last_col)]
        return toks

    _TERMINAL_DISPLAY: Dict[str, str] = {
        'id': 'id', 'intlit': 'intlit', 'dblit': 'dblit',
        'stringlit': 'stringlit', 'chrlit': 'chrlit',
        'sunshine': "'sunshine'", 'frost': "'frost'",
        'seed': "'seed'", 'tree': "'tree'",
        'leaf': "'leaf'", 'branch': "'branch'",
        'vine': "'vine'",
        'bundle': "'bundle'", 'fertile': "'fertile'",
        'pollinate': "'pollinate'", 'root': "'root'",
        'reclaim': "'reclaim'", 'spring': "'spring'",
        'bud': "'bud'", 'wither': "'wither'",
        'grow': "'grow'", 'cultivate': "'cultivate'",
        'tend': "'tend'", 'harvest': "'harvest'",
        'variety': "'variety'", 'soil': "'soil'",
        'prune': "'prune'", 'skip': "'skip'",
        'water': "'water'", 'plant': "'plant'",
        'empty': "'empty'",
        'EOF': 'end of file',
    }

    def _format_expected(self, expected: Set[str], non_terminal: Optional[str] = None) -> str:
        symbols = {'(', ')', '{', '}', ';', ',', '=', '+', '-', '*', '/', '%',
                   '++', '--', '==', '!=', '<', '>', '<=', '>=', '&&', '||',
                   '!', '~', '+=', '-=', '*=', '/=', '%=', '.', '[', ']', ':', '`'}
        has_reclaim = any(tk.type == 'reclaim' for tk in getattr(self, '_current_tokens', []))

        parts: List[str] = []
        for t in sorted(expected):
            if t == 'reclaim' and has_reclaim:
                continue
            if t in self._TERMINAL_DISPLAY:
                parts.append(self._TERMINAL_DISPLAY[t])
            elif t in symbols:
                parts.append(f"'{t}'")
            elif t.startswith('<') and t.endswith('>'):
                continue
            else:
                parts.append(f"'{t}'")
        if not parts:
            return 'nothing'
        return f"Expected: {', '.join(parts)}"

    def _generate_helpful_error(
        self,
        non_terminal: str,
        token_type: str,
        token_value: str,
        line: int,
        col: int,
        expected: Set[str],
        index: int,
        toks: List[_TokView]
    ) -> str:
        
        param_type_tokens = {'seed', 'tree', 'leaf', 'vine', 'branch'}
        
        if token_type == self.end_marker or token_value == '':
            if '}' in expected:
                return f"SYNTAX error line {line} col {col} Unexpected end of file. Missing closing '}}'. {self._format_expected(expected, non_terminal)}"
            return f"SYNTAX error line {line} col {col} Unexpected end of file. {self._format_expected(expected, non_terminal)}"
        
        if token_type == '=' and index > 0:
            prev_index = index - 1
            while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                prev_index -= 1
            
            if prev_index >= 0 and toks[prev_index].type == '==':
                return f"SYNTAX error line {line} col {col} Invalid operator '==='. Use '==' for equality comparison. {self._format_expected(expected, non_terminal)}"
        
        if token_type == '&' and index > 0:
            prev_index = index - 1
            while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                prev_index -= 1
            
            if prev_index >= 0 and toks[prev_index].type == '&&':
                return f"SYNTAX error line {line} col {col} Invalid operator '&&&'. Use '&&' for logical AND. {self._format_expected(expected, non_terminal)}"
            return f"SYNTAX error line {line} col {col} Invalid operator '&'. Use '&&' for logical AND. {self._format_expected(expected, non_terminal)}"
        
        if token_type == '|' and index > 0:
            prev_index = index - 1
            while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                prev_index -= 1
            
            if prev_index >= 0 and toks[prev_index].type == '||':
                return f"SYNTAX error line {line} col {col} Invalid operator '|||'. Use '||' for logical OR. {self._format_expected(expected, non_terminal)}"
            return f"SYNTAX error line {line} col {col} Invalid operator '|'. Use '||' for logical OR. {self._format_expected(expected, non_terminal)}"
        
        if token_type == 'chrlit' and token_value and not token_value.endswith("'"):
            return f"SYNTAX error line {line} col {col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"
        
        if token_type == 'stringlit' and token_value and not token_value.endswith('"'):
            return f"SYNTAX error line {line} col {col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"
        
        if non_terminal == '<reclaim_value>' and token_type == '}':
            return f"SYNTAX error line {line} col {col} Missing ';' after 'reclaim'. Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"
        
        if token_type == ')' and ')' not in expected:
            if index > 0:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0:
                    prev_tok = toks[prev_index]
                    binary_operators = {'+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||'}
                    if prev_tok.type in binary_operators:
                        return f"SYNTAX error line {line} col {col} Unexpected token ')' after binary operator '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"
                    
                    if prev_tok.type == ',' and param_type_tokens & expected:
                        return f"SYNTAX error line {line} col {col}: Unexpected token ')'. Expected parameter type (seed, tree, leaf, vine, branch) after ','"
                    
                    if prev_tok.type == '(':
                        kw_index = prev_index - 1
                        while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:
                            kw_index -= 1
                        if kw_index >= 0:
                            keyword_descriptions = {
                                'grow': 'while-loop', 'spring': 'if-statement', 'cultivate': 'for-loop',
                                'tend': 'do-while-loop', 'harvest': 'switch-statement', 'bud': 'else-if',
                                'plant': 'output function', 'water': 'input function',
                                'seed': 'integer type', 'tree': 'float type', 'leaf': 'character type',
                                'vine': 'string type', 'branch': 'boolean type',
                                'reclaim': 'return statement', 'prune': 'break statement',
                                'skip': 'continue statement', 'pollinate': 'function declaration',
                                'root': 'main function', 'wither': 'else-statement',
                                'fertile': 'constant declaration', 'bundle': 'struct definition',
                                'variety': 'case label', 'soil': 'default case',
                                'empty': 'void type',
                            }
                            kw_tok = toks[kw_index]
                            if kw_tok.type in keyword_descriptions:
                                desc = keyword_descriptions[kw_tok.type]
                                return f"SYNTAX error line {kw_tok.line} col {kw_tok.col} '{kw_tok.value}' is a reserved keyword ({desc}) and cannot be used as a function name."
            
            return f"SYNTAX error line {line} col {col} Unexpected token ')' - no matching '(' found in expression. {self._format_expected(expected, non_terminal)}"
        
        assignment_operators = {'+=', '-=', '*=', '/=', '%='}
        if token_type in assignment_operators:
            return f"SYNTAX error line {line} col {col} Assignment operator '{token_value}' must follow a modifiable assignment target. {self._format_expected(expected, non_terminal)}"
        
        if token_type == '=':
            if index > 0:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0:
                    prev_tok = toks[prev_index]
                    compound_op_bases = {'+', '-', '*', '/', '%'}
                    if prev_tok.type in compound_op_bases:
                        prev_prev_index = prev_index - 1
                        while prev_prev_index >= 0 and toks[prev_prev_index].type in self.skip_token_types:
                            prev_prev_index -= 1
                        
                        if prev_prev_index >= 0 and toks[prev_prev_index].type == 'id':
                            id_tok = toks[prev_prev_index]
                            compound_op = f"{prev_tok.value}="
                            return f"SYNTAX error line {line} col {col} Unexpected token '=' after operator '{prev_tok.value}'. Did you mean '{id_tok.value} {compound_op}' (compound assignment with no space)? {self._format_expected(expected, non_terminal)}"
        
        if token_type == '{' and non_terminal in {'<program>', '<global_declaration>'}:
            if index == 0 or (index <= 2 and all(toks[i].type in self.skip_token_types for i in range(index))):
                return f"SYNTAX error line {line} col {col} 'root' function declaration is missing opening '('. {self._format_expected(expected, non_terminal)}"
        
        if index + 1 < len(toks):
            next_tok = toks[index + 1]
            if next_tok.type == 'chrlit' and next_tok.value and not next_tok.value.endswith("'"):
                return f"SYNTAX error line {next_tok.line} col {next_tok.col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"
            
            if next_tok.type == 'stringlit' and next_tok.value and not next_tok.value.endswith('"'):
                return f"SYNTAX error line {next_tok.line} col {next_tok.col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"
        
        if token_type == ';' and non_terminal == '<global_declaration>':
            if index > 0:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0 and toks[prev_index].type == '}':
                    bundle_index = prev_index - 1
                    while bundle_index >= 0 and toks[bundle_index].type in self.skip_token_types:
                        bundle_index -= 1
                    
                    found_bundle = False
                    for i in range(bundle_index, max(0, bundle_index - 20) - 1, -1):
                        if toks[i].type == 'bundle':
                            found_bundle = True
                            break
                    
                    if found_bundle:
                        expected_str = self._format_expected(expected, non_terminal)
                        return f"SYNTAX error line {line} col {col} Unexpected token ';' after bundle definition closing '}}'. ';' is not in {expected_str}. Remove the trailing ';'"
        
        common_keyword_mistakes = {
            'function': 'pollinate',
            'int': 'seed',
            'float': 'tree',
            'double': 'tree',
            'char': 'leaf',
            'bool': 'branch',
            'boolean': 'branch',
            'if': 'spring',
            'else': 'wither',
            'elif': 'bud',
            'while': 'grow',
            'for': 'cultivate',
            'switch': 'harvest',
            'case': 'variety',
            'default': 'soil',
            'break': 'prune',
            'continue': 'skip',
            'return': 'reclaim',
            'void': 'empty',
            'const': 'fertile',
            'struct': 'bundle',
            'string': 'vine',
            'printf': 'plant',
            'scanf': 'water',
            'print': 'plant',
            'input': 'water'
        }
        
        if token_type == 'id' and token_value in common_keyword_mistakes:
            correct_keyword = common_keyword_mistakes[token_value]
            return f"SYNTAX error line {line} col {col} '{token_value}' is not a GAL keyword. Use '{correct_keyword}' instead."
        
        if token_type == '{' and (non_terminal == '<bundle_or_var>' or non_terminal == '<bundle_mem_dec>'):
            return f"SYNTAX error line {line} col {col} Bundle definitions must be at global scope (outside all functions). Move this bundle definition before 'root()'. {self._format_expected(expected, non_terminal)}"
        
        statement_starters = {
            'reclaim', 'spring', 'wither', 'bud', 'grow', 'cultivate', 'tend',
            'harvest', 'prune', 'skip', 'water', 'plant', 'seed', 'leaf',
            'branch', 'tree', 'vine', 'bundle', 'fertile', 'pollinate', 'root', 'id'
        }
        
        if ':' in expected and token_type in statement_starters:
            context_keyword = None
            if index > 0:
                scan = index - 1
                while scan >= 0:
                    if toks[scan].type in self.skip_token_types:
                        scan -= 1
                        continue
                    if toks[scan].type == 'variety':
                        context_keyword = 'variety'
                        break
                    if toks[scan].type == 'soil':
                        context_keyword = 'soil'
                        break
                    if toks[scan].type in {'id', 'intlit', 'dblit', 'stringlit', 'chrlit',
                                           'sunshine', 'frost', '+', '-', '*', '/', '%',
                                           '==', '!=', '<', '>', '<=', '>=', '&&', '||',
                                           '(', ')', '`', '~'}:
                        scan -= 1
                        continue
                    break
            if context_keyword:
                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}' after '{context_keyword}'. {self._format_expected({':'})}"
        
        if ';' in expected:
            if token_type in statement_starters or token_type == 'id':
                if index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        
                        if prev_tok.type == '=':
                            prev_line = prev_tok.line
                            prev_col = prev_tok.col
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing value after '=' operator. {self._format_expected(expected, non_terminal)}"
                        
                        if prev_tok.type == 'chrlit' and prev_tok.value and not prev_tok.value.endswith("'"):
                            prev_line = prev_tok.line
                            prev_col = prev_tok.col
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"
                        
                        if prev_tok.type == 'stringlit' and prev_tok.value and not prev_tok.value.endswith('"'):
                            prev_line = prev_tok.line
                            prev_col = prev_tok.col
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"
                        
                        prev_line = prev_tok.line
                        prev_col = prev_tok.col + len(str(prev_tok.value))
                        expected_str = self._format_expected(expected, non_terminal)
                        if prev_line != line:
                            return (f"SYNTAX error line {prev_line} col {prev_col} Unexpected token '{token_value}' after '{prev_tok.value}'. {expected_str}")
                        else:
                            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {expected_str}"
            elif token_type == '}':
                if index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        
                        if prev_tok.type == 'reclaim':
                            return f"SYNTAX error line {prev_tok.line} col {prev_tok.col + len('reclaim')} Missing ';' after 'reclaim'. {self._format_expected(expected, non_terminal)}"
                        
                        if prev_tok.type == 'chrlit' and prev_tok.value and not prev_tok.value.endswith("'"):
                            prev_line = prev_tok.line
                            prev_col = prev_tok.col
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"
                        
                        if prev_tok.type == 'stringlit' and prev_tok.value and not prev_tok.value.endswith('"'):
                            prev_line = prev_tok.line
                            prev_col = prev_tok.col
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"
                        
                        prev_line = prev_tok.line
                        prev_col = prev_tok.col + len(str(prev_tok.value))
                        expected_str = self._format_expected(expected, non_terminal)
                        if prev_line != line:
                            return f"SYNTAX error line {prev_line} col {prev_col} Unexpected token '}}' after '{prev_tok.value}'. {expected_str}"
                        else:
                            return f"SYNTAX error line {line} col {col} Unexpected token '}}'. {expected_str}"
        
        if 'reclaim' in expected and token_type == '}':
            return f"SYNTAX error line {line} col {col} expected 'reclaim;' before '}}'. All functions, including root(), must end with 'reclaim;'. {self._format_expected(expected, non_terminal)}"
        
        if 'prune' in expected and token_type in {'variety', 'soil', '}'}:
            if token_type == 'variety':
                return f"SYNTAX error line {line} col {col} expected 'prune;' before next 'variety'. Each case in 'harvest' must end with 'prune;'. {self._format_expected(expected, non_terminal)}"
            elif token_type == 'soil':
                return f"SYNTAX error line {line} col {col} expected 'prune;' before 'soil'. Each case must end with 'prune;'. {self._format_expected(expected, non_terminal)}"
            else:
                return f"SYNTAX error line {line} col {col} expected 'prune;' before closing '}}'. Each case must end with 'prune;'. {self._format_expected(expected, non_terminal)}"
        
        if token_type in {'-', '+'} and non_terminal in {'<expression>', '<factor>', '<term>', '<arithmetic>', '<logic_or>', '<logic_and>', '<relational>', '<init_val>'}:
            if index > 0:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0:
                    prev_tok = toks[prev_index]
                    if prev_tok.type in {'=', '+=', '-=', '*=', '/=', '%=', '(', ','}:
                        if token_value == '-':
                            return f"SYNTAX error line {line} col {col} Unary '-' not supported. Use '~' for negative numbers (e.g., '~5') or '(0 - value)' for negation. {self._format_expected(expected, non_terminal)}"
                        else:
                            return f"SYNTAX error line {line} col {col} Unary '+' operator not supported. Use parentheses for expressions like '(0 + value)'. {self._format_expected(expected, non_terminal)}"
        
        if token_type in {'*', '/', '%', '+', '-', '`', '&&', '||', '==', '!=', '<', '>', '<=', '>='}:
            if index > 0:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0 and toks[prev_index].type == '(':
                    return f"SYNTAX error line {line} col {col} Unexpected binary operator '{token_value}'. {self._format_expected(expected, non_terminal)}"
        
        if '(' in expected and token_type != '(':
            if index > 0 and token_type not in {'-', '+'}:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0:
                    prev_tok = toks[prev_index]
                    if prev_tok.type in {'+', '-', '*', '/', '%', '`', '=', '+=', '-=', '*=', '/=', '%=', '&&', '||', '==', '!=', '<', '>', '<=', '>='}:
                        if token_type in {'*', '/', '%', '+', '-', '`', '&&', '||', '==', '!=', '<', '>', '<=', '>='}:
                            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}' operator - binary operators cannot start an expression. {self._format_expected(expected, non_terminal)}"
                        return f"SYNTAX error line {line} col {col} Missing value after '{prev_tok.value}' operator. {self._format_expected(expected, non_terminal)}"
            
            if token_type in {'=', '+=', '-=', '*=', '/=', '%='}:
                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"
            
            if index > 0:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0:
                    prev_tok = toks[prev_index]
                    
                    common_keyword_mistakes = {
                        'function': 'pollinate',
                        'int': 'seed',
                        'float': 'tree',
                        'double': 'tree',
                        'char': 'leaf',
                        'bool': 'branch',
                        'boolean': 'branch',
                        'if': 'spring',
                        'else': 'wither',
                        'elif': 'bud',
                        'while': 'grow',
                        'for': 'cultivate',
                        'switch': 'harvest',
                        'case': 'variety',
                        'default': 'soil',
                        'break': 'prune',
                        'continue': 'skip',
                        'return': 'reclaim',
                        'void': 'empty',
                        'const': 'fertile',
                        'struct': 'bundle',
                        'string': 'vine',
                        'printf': 'plant',
                        'scanf': 'water',
                        'print': 'plant',
                        'input': 'water'
                    }
                    
                    if prev_tok.type == 'id' and prev_tok.value in common_keyword_mistakes:
                        correct_keyword = common_keyword_mistakes[prev_tok.value]
                        return f"SYNTAX error line {prev_tok.line} col {prev_tok.col} '{prev_tok.value}' is not a GAL keyword. Use '{correct_keyword}' instead."
                    
                    keywords_needing_parens = {'spring', 'grow', 'cultivate', 'harvest', 'water', 'plant', 'tend', 'bud'}
                    if prev_tok.type in keywords_needing_parens:
                        return f"SYNTAX error line {line} col {col} Missing '(' after '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"
                    
                    if prev_tok.type == 'id':
                        # NOTE: GAL does support '**' (exponentiation) and '**=' (exponent-assign).

                        compound_op_bases = {'+', '-', '*', '/', '%'}
                        if token_type in compound_op_bases:
                            next_index = index + 1
                            while next_index < len(toks) and toks[next_index].type in self.skip_token_types:
                                next_index += 1
                            
                            if next_index < len(toks) and toks[next_index].type == '=':
                                compound_op = f"{token_value}="
                                return f"SYNTAX error line {line} col {col} Unexpected operator '{token_value}' followed by '='. Expected: '{compound_op}' (compound assignment must be written without spaces). {self._format_expected(expected, non_terminal)}"
                        
                        binary_operators = {'+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||'}
                        has_operators_expected = bool(binary_operators & expected)
                        
                        if has_operators_expected:
                            if token_type in {'++', '--'}:
                                next_index = index + 1
                                while next_index < len(toks) and toks[next_index].type in self.skip_token_types:
                                    next_index += 1
                                
                                if next_index < len(toks):
                                    next_tok = toks[next_index]
                                    if (token_type == '++' and next_tok.type == '+') or (token_type == '--' and next_tok.type == '-'):
                                        operator_seq = token_type + ('+' if token_type == '++' else '-')
                                        return f"SYNTAX error line {line} col {col} Unexpected token '{operator_seq}' operator sequence. {self._format_expected(expected, non_terminal)}"
                                
                                return f"SYNTAX error line {line} col {col} Unexpected {token_type} operator. {self._format_expected(expected, non_terminal)}"
                            if token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'id'}:
                                return f"SYNTAX error line {line} col {col} Unexpected token '{token_type}' after identifier '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"
                            else:
                                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}' after identifier '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"
                        else:
                            return f"SYNTAX error line {prev_tok.line} col {prev_tok.col} invalid statement: identifier '{prev_tok.value}' must be followed by assignment operator, unary operator (++/--), or function call syntax '()'. {self._format_expected(expected, non_terminal)}"
            
            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"
        
        declaration_keywords = {'seed', 'tree', 'leaf', 'vine', 'branch', 'bundle', 'fertile'}
        if token_type in declaration_keywords and non_terminal in {'<body_statement>', '<statement>', '<case_statements>'}:
            return f"SYNTAX error line {line} col {col} Unexpected local declaration '{token_value}' after an executable statement. Local declarations must appear first in the block. {self._format_expected(expected, non_terminal)}"

        if '}' in expected and token_type in statement_starters:
            if token_type == 'bud':
                return f"SYNTAX error line {line} col {col} 'bud' can only appear after a 'spring' statement. {self._format_expected(expected, non_terminal)}"
            elif token_type == 'wither':
                return f"SYNTAX error line {line} col {col} 'wither' can only appear after a 'spring' or 'bud' statement. {self._format_expected(expected, non_terminal)}"
            elif token_type == 'reclaim':
                return f"SYNTAX error line {line} col {col} Missing closing brace before '{token_value}'. {self._format_expected(expected, non_terminal)}"
            return f"SYNTAX error line {line} col {col} Missing closing brace before '{token_value}'. {self._format_expected(expected, non_terminal)}"
        
        if token_type in {'++', '--'} and ')' in expected:
            op_name = "increment" if token_value == "++" else "decrement"
            return f"SYNTAX error line {line} col {col} Postfix {op_name} operator '{token_value}' not allowed in expression context. {self._format_expected(expected, non_terminal)}"
        
        if param_type_tokens & expected and ')' in expected and token_type == 'id':
            return f"SYNTAX error line {line} col {col}: Unexpected token '{token_value}'. Expected parameter type (seed, tree, leaf, vine, branch) or ')'"
        
        if ')' in expected and token_type not in {')'}:
            if ',' in expected and token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'id', 'sunshine', 'frost', '~', '!'}:
                return f"SYNTAX error line {line} col {col}: Unexpected token '{token_value}'. Expected ',' between arguments or ')' to close function call"
            if token_type in {'~', '!'}:
                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"
            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"
        
        if token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'id'}:
            if index > 0:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0:
                    prev_tok = toks[prev_index]
                    if prev_tok.type in {'id', 'intlit', 'dblit', 'stringlit', 'chrlit'}:
                        expression_contexts = {'<expression>', '<factor>', '<term>', '<arithmetic>', '<logic_or>', 
                                             '<logic_and>', '<relational>', '<init_val>', '<param_list>', '<arg_list>',
                                             '<term_tail>', '<arithmetic_tail>', '<relational_tail>', '<logic_and_tail>', '<logic_or_tail>'}
                        
                        if non_terminal in expression_contexts:
                            prev_type_friendly = {
                                'id': 'identifier',
                                'intlit': 'integer literal',
                                'dblit': 'double literal',
                                'stringlit': 'string literal',
                                'chrlit': 'character literal'
                            }.get(prev_tok.type, prev_tok.type)
                            
                            curr_type_friendly = {
                                'id': 'identifier',
                                'intlit': 'integer literal',
                                'dblit': 'double literal',
                                'stringlit': 'string literal',
                                'chrlit': 'character literal'
                            }.get(token_type, token_type)
                            
                            return f"SYNTAX error line {line} col {col} Unexpected {curr_type_friendly} '{token_value}' after {prev_type_friendly} '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"
        
        if non_terminal == '<array_dim_opt>' and token_type == 'id':
            return f"SYNTAX error line {line} col {col} Array size must be a constant integer literal, not a variable '{token_value}'. Expected: ']', dblit, intlit"

        return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"

    def parse(self, tokens: Sequence[Any]) -> Tuple[bool, List[str]]:
        toks = [_as_tok(t) for t in tokens]
        toks = [_TokView(self._normalize_token_type(t.type), t.value, t.line, t.col) for t in toks]
        toks = self._ensure_eof(toks)

        self._current_tokens = toks

        stack: List[str] = [self.end_marker, self.start_symbol]
        index = 0
        
        current_var_type: Optional[str] = None
        expecting_value_for_type: Optional[str] = None

        reclaim_seen_stack: List[bool] = []

        def current_token() -> _TokView:
            nonlocal index
            if index >= len(toks):
                last_line = toks[-1].line if toks else 1
                last_col = toks[-1].col if toks else 0
                return _TokView(self.end_marker, self.end_marker, last_line, last_col)
            return toks[index]

        while stack:
            top = stack[-1]
            tok = current_token()
            token_type = tok.type
            token_value = tok.value
            line = tok.line or 1

            if token_type in self.skip_token_types and top != token_type:
                index += 1
                continue

            if top in self.parsing_table:
                row = self.parsing_table[top]
                if token_type in row:
                    production = row[token_type]
                    
                    if top == '<statement>' and token_type != '}' and reclaim_seen_stack and reclaim_seen_stack[-1]:
                        return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after 'reclaim'. Expected: '}}'."]

                    if top == '<statement>' and token_type == '}':
                        is_epsilon = (len(production) == 0 or (len(production) == 1 and production[0] in self.epsilon_symbols))
                        if is_epsilon:
                            lookback = index - 1
                            while lookback >= 0 and toks[lookback].type in self.skip_token_types:
                                lookback -= 1
                            
                            if lookback >= 0 and toks[lookback].type == '{':
                                before_brace = lookback - 1
                                while before_brace >= 0 and toks[before_brace].type in self.skip_token_types:
                                    before_brace -= 1
                                
                                if before_brace >= 0 and toks[before_brace].type == ')':
                                    paren_depth = 1
                                    paren_pos = before_brace - 1
                                    while paren_pos >= 0 and paren_depth > 0:
                                        if toks[paren_pos].type == ')':
                                            paren_depth += 1
                                        elif toks[paren_pos].type == '(':
                                            paren_depth -= 1
                                        paren_pos -= 1
                                    
                                    if paren_pos >= 0:
                                        kw_pos = paren_pos
                                        while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:
                                            kw_pos -= 1
                                        
                                        if kw_pos >= 0:
                                            kw = toks[kw_pos]
                                            conditional_keywords = {'spring', 'bud', 'wither', 'grow', 'cultivate', 'tend', 'harvest'}
                                            if kw.type in conditional_keywords:
                                                return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
                                
                                elif before_brace >= 0 and toks[before_brace].type in {'wither', 'tend'}:
                                    kw = toks[before_brace]
                                    return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
                    
                    stack.pop()

                    if not (
                        len(production) == 0
                        or (len(production) == 1 and production[0] in self.epsilon_symbols)
                    ):
                        stack.extend(reversed(production))
                    continue

                expected = set(row.keys())
                
                if token_type in {'variety', 'soil'} and token_type not in expected:
                    while index < len(toks) and toks[index].type != ';':
                        if toks[index].type == 'prune':
                            index += 1
                            break
                        index += 1
                    if index < len(toks) and toks[index].type == ';':
                        index += 1
                    continue

                error_msg = self._generate_helpful_error(top, token_type, token_value, line, tok.col, expected, index, toks)
                return False, [error_msg]

            if top == token_type:
                if token_type in {'seed', 'tree', 'leaf', 'branch', 'vine'}:
                    current_var_type = token_type
                    expecting_value_for_type = None
                
                elif token_type == '=' and current_var_type is not None:
                    expecting_value_for_type = current_var_type
                
                elif expecting_value_for_type is not None and token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'sunshine', 'frost', 'id'}:
                    type_value_map = {
                        'seed': {'intlit', 'dblit'},
                        'tree': {'dblit', 'intlit'},
                        'leaf': {'chrlit'},
                        'branch': {'sunshine', 'frost'},
                        'vine': {'stringlit'}
                    }
                    
                    if token_type == 'id':
                        expecting_value_for_type = None
                        stack.pop()
                        index += 1
                        continue
                    
                    expected_value_types = type_value_map.get(expecting_value_for_type, set())
                    
                    if token_type not in expected_value_types:
                        type_names = {
                            'seed': 'integer (seed)',
                            'tree': 'double (tree)',
                            'leaf': 'character (leaf)',
                            'branch': 'boolean (branch)',
                            'vine': 'string (vine)'
                        }
                        value_type_names = {
                            'intlit': 'integer',
                            'dblit': 'double',
                            'stringlit': 'string',
                            'chrlit': 'character',
                            'sunshine': 'boolean',
                            'frost': 'boolean',
                            'id': 'identifier'
                        }
                        
                        declared_type = type_names.get(expecting_value_for_type, expecting_value_for_type)
                        actual_type = value_type_names.get(token_type, token_type)
                        
                        error_msg = f"SEMANTIC error line {line} col {tok.col} Type mismatch: cannot assign {actual_type} value '{token_value}' to {declared_type} variable"
                        return False, [error_msg]
                    
                    if token_type == 'chrlit' and expecting_value_for_type == 'leaf':
                        char_content = token_value[1:-1] if len(token_value) >= 2 else token_value
                        if len(char_content) == 0:
                            error_msg = f"SYNTAX error line {line} col {tok.col} Character literal cannot be empty. Expected a single character for leaf variable"
                            return False, [error_msg]
                        elif char_content.startswith('\\') and len(char_content) == 2:
                            pass
                        elif len(char_content) > 1:
                            error_msg = f"SYNTAX error line {line} col {tok.col} Character literal '{token_value}' contains {len(char_content)} characters. leaf variables can only hold a single character"
                            return False, [error_msg]
                    
                    
                    expecting_value_for_type = None
                
                elif token_type == ';':
                    current_var_type = None
                    expecting_value_for_type = None
                
                if top == 'intlit' or top == 'dblit':
                    lookback = index - 1
                    while lookback >= 0 and toks[lookback].type in self.skip_token_types:
                        lookback -= 1
                    
                    if lookback >= 0 and toks[lookback].type == '(':
                        kw_pos = lookback - 1
                        while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:
                            kw_pos -= 1
                        
                        if kw_pos >= 0:
                            kw = toks[kw_pos]
                            condition_keywords = {'spring', 'grow', 'cultivate', 'tend', 'bud'}
                            if kw.type in condition_keywords:
                                next_idx = index + 1
                                while next_idx < len(toks) and toks[next_idx].type in self.skip_token_types:
                                    next_idx += 1
                                
                                if next_idx < len(toks) and toks[next_idx].type == ')':
                                    return False, [f"SYNTAX error line {line} col {tok.col} '{kw.value}' requires a boolean condition, not a numeric literal"]
                
                if token_type in {'&&', '||'}:
                    prev_idx = index - 1
                    while prev_idx >= 0 and toks[prev_idx].type in self.skip_token_types:
                        prev_idx -= 1
                    if prev_idx >= 0:
                        prev_tok = toks[prev_idx]
                        non_branch_literals = {'intlit', 'dblit', 'stringlit', 'chrlit'}
                        if prev_tok.type in non_branch_literals:
                            cmp_idx = prev_idx - 1
                            while cmp_idx >= 0 and toks[cmp_idx].type in self.skip_token_types:
                                cmp_idx -= 1
                            comparison_ops = {'<', '>', '<=', '>=', '==', '!='}
                            if cmp_idx >= 0 and toks[cmp_idx].type in comparison_ops:
                                pass
                            else:
                                type_names = {
                                    'intlit': 'integer literal',
                                    'dblit': 'double literal',
                                    'stringlit': 'string literal',
                                    'chrlit': 'character literal',
                                }
                                op_name = 'AND' if token_type == '&&' else 'OR'
                                return False, [f"SYNTAX error line {line} col {tok.col} Logical operator '{token_type}' ({op_name}) requires branch operands, not {type_names[prev_tok.type]} '{prev_tok.value}'"]
                
                if token_type in {'intlit', 'dblit', 'stringlit', 'chrlit'}:
                    prev_idx = index - 1
                    while prev_idx >= 0 and toks[prev_idx].type in self.skip_token_types:
                        prev_idx -= 1
                    if prev_idx >= 0 and toks[prev_idx].type in {'&&', '||'}:
                        next_check = index + 1
                        while next_check < len(toks) and toks[next_check].type in self.skip_token_types:
                            next_check += 1
                        comparison_ops = {'<', '>', '<=', '>=', '==', '!='}
                        if next_check < len(toks) and toks[next_check].type in comparison_ops:
                            pass
                        else:
                            type_names = {
                                'intlit': 'integer literal',
                                'dblit': 'double literal',
                                'stringlit': 'string literal',
                                'chrlit': 'character literal',
                            }
                            op_name = 'AND' if toks[prev_idx].type == '&&' else 'OR'
                            return False, [f"SYNTAX error line {line} col {tok.col} Logical operator '{toks[prev_idx].type}' ({op_name}) requires branch operands, not {type_names[token_type]} '{token_value}'"]

                if token_type == '{':
                    reclaim_seen_stack.append(False)
                elif token_type == '}':
                    if reclaim_seen_stack:
                        reclaim_seen_stack.pop()
                elif token_type == 'reclaim':
                    if reclaim_seen_stack:
                        reclaim_seen_stack[-1] = True

                stack.pop()
                index += 1
                continue

            if top == self.end_marker and token_type in self.skip_token_types:
                index += 1
                continue

            expected = {top}
            shown_value = "end of file" if token_type == self.end_marker else token_value
            
            if token_type == self.end_marker:
                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected end of file. Expected: '{top}'. Missing closing '}}' or incomplete statement."
                return False, [error_msg]
            
            if top == 'grow' and token_type == '(':
                scan_idx = index - 1
                while scan_idx >= 0 and toks[scan_idx].type in self.skip_token_types:
                    scan_idx -= 1
                if scan_idx >= 0 and toks[scan_idx].type == '}':
                    brace_depth = 1
                    scan_idx -= 1
                    while scan_idx >= 0 and brace_depth > 0:
                        if toks[scan_idx].type == '}':
                            brace_depth += 1
                        elif toks[scan_idx].type == '{':
                            brace_depth -= 1
                        scan_idx -= 1
                    kw_idx = scan_idx
                    while kw_idx >= 0 and toks[kw_idx].type in self.skip_token_types:
                        kw_idx -= 1
                    if kw_idx >= 0 and toks[kw_idx].type == 'tend':
                        error_msg = f"SYNTAX error line {line} col {tok.col} Missing 'grow' keyword before '('. {self._format_expected(expected, top)}. Correct format: tend {{ ... }} grow (condition);"
                        return False, [error_msg]
            
            if top == 'reclaim' and token_type == '}':
                is_root = False
                for i in range(index - 1, -1, -1):
                    if toks[i].type == 'root':
                        is_root = True
                        break
                    elif toks[i].type == 'pollinate':
                        is_root = False
                        break
                
                if is_root:
                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'reclaim;' before '}}'. The root() function (main program) must end with 'reclaim;'. {self._format_expected(expected)}"
                else:
                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'reclaim;' before '}}'. All functions must end with 'reclaim;'. {self._format_expected(expected)}"
                return False, [error_msg]
            elif top == 'prune' and token_type in {'variety', 'soil', '}'}:
                if token_type == 'variety':
                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'prune;' before next 'variety'. Each case in 'harvest' must end with 'prune;'. {self._format_expected(expected)}"
                elif token_type == 'soil':
                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'prune;' before 'soil'. Each case must end with 'prune;'. {self._format_expected(expected)}"
                else:
                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'prune;' before closing '}}'. Each case must end with 'prune;'. {self._format_expected(expected)}"
                return False, [error_msg]
            elif top == '(' and token_type != '(':
                if token_type in {'=', '+=', '-=', '*=', '/=', '%='}:
                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected, top)}"
                elif index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        
                        if prev_tok.type == '}':
                            brace_depth = 1
                            scan_idx = prev_index - 1
                            while scan_idx >= 0 and brace_depth > 0:
                                if toks[scan_idx].type == '}':
                                    brace_depth += 1
                                elif toks[scan_idx].type == '{':
                                    brace_depth -= 1
                                scan_idx -= 1
                            
                            if scan_idx >= 0:
                                kw_idx = scan_idx
                                while kw_idx >= 0 and toks[kw_idx].type in self.skip_token_types:
                                    kw_idx -= 1
                                
                                if kw_idx >= 0 and toks[kw_idx].type == 'tend':
                                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. 'tend' requires 'grow' after closing brace '}}'. Correct format: tend {{ ... }} grow (condition); {self._format_expected(expected)}"
                                else:
                                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                            else:
                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                        else:
                            keywords_needing_parens = {'spring', 'grow', 'cultivate', 'harvest', 'water', 'plant', 'tend', 'bud'}
                            if prev_tok.type in keywords_needing_parens:
                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{prev_tok.value}'. {self._format_expected(expected)}"
                            else:
                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                    else:
                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                else:
                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                return False, [error_msg]
            elif top == '{' and token_type != '{':
                error_msg = None
                if token_type == ')' and index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0 and toks[prev_index].type == ')':
                        paren_index = prev_index - 1
                        paren_count = 1
                        while paren_index >= 0 and paren_count > 0:
                            if toks[paren_index].type == ')':
                                paren_count += 1
                            elif toks[paren_index].type == '(':
                                paren_count -= 1
                            paren_index -= 1
                        
                        if paren_index >= 0:
                            kw_index = paren_index
                            while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:
                                kw_index -= 1
                            
                            if kw_index >= 0:
                                kw_tok = toks[kw_index]
                                if kw_tok.type in {'root', 'pollinate'}:
                                    error_msg = f"SYNTAX error line {line} col {tok.col} Extra closing ')' after '{kw_tok.value}()'. Correct syntax: {kw_tok.value}(){{ ... }}. {self._format_expected(expected)}"
                
                if error_msg is None and index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        keywords_needing_braces = {'spring', 'wither', 'grow', 'cultivate', 'tend', 'harvest', 'bud', ')', 'pollinate', 'root'}
                        if prev_tok.type in keywords_needing_braces:
                            if prev_tok.type == ')':
                                paren_index = prev_index - 1
                                paren_count = 1
                                while paren_index >= 0 and paren_count > 0:
                                    if toks[paren_index].type == ')':
                                        paren_count += 1
                                    elif toks[paren_index].type == '(':
                                        paren_count -= 1
                                    paren_index -= 1
                                
                                if paren_index >= 0:
                                    kw_index = paren_index
                                    while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:
                                        kw_index -= 1
                                    
                                    if kw_index >= 0:
                                        kw_tok = toks[kw_index]
                                        if kw_tok.type in {'spring', 'grow', 'cultivate', 'tend', 'harvest', 'bud', 'pollinate', 'root'}:
                                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{kw_tok.value}' statement. {self._format_expected(expected)}"
                                        else:
                                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                                    else:
                                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                                else:
                                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                            else:
                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{prev_tok.value}'. {self._format_expected(expected)}"
                        else:
                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                    else:
                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                elif error_msg is None:
                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"
                return False, [error_msg]
            elif top == '}' and token_type != '}':
                return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. Missing closing brace. {self._format_expected(expected)}"]
            elif top == ')' and token_type != ')':
                return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"]
            elif top == ':' and token_type != ':':
                context_keyword = None
                if index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        if prev_tok.type == 'soil':
                            context_keyword = 'soil'
                        else:
                            scan = prev_index
                            while scan >= 0:
                                if toks[scan].type in self.skip_token_types:
                                    scan -= 1
                                    continue
                                if toks[scan].type == 'variety':
                                    context_keyword = 'variety'
                                    break
                                if toks[scan].type in {'id', 'intlit', 'dblit', 'stringlit', 'chrlit',
                                                       'sunshine', 'frost', '+', '-', '*', '/', '%',
                                                       '==', '!=', '<', '>', '<=', '>=', '&&', '||',
                                                       '(', ')', '`', '~'}:
                                    scan -= 1
                                    continue
                                break
                if context_keyword:
                    return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{context_keyword}'. {self._format_expected({':'})}"]
                else:
                    return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected({':'})}"]
            elif top == ';' and token_type != ';':
                common_keyword_mistakes = {
                    'function': 'pollinate', 'int': 'seed', 'float': 'tree', 'double': 'tree',
                    'char': 'leaf', 'bool': 'branch', 'boolean': 'branch', 'if': 'spring',
                    'else': 'wither', 'elif': 'bud', 'while': 'grow', 'for': 'cultivate',
                    'switch': 'harvest', 'case': 'variety', 'default': 'soil', 'break': 'prune',
                    'continue': 'skip', 'return': 'reclaim', 'void': 'empty', 'const': 'fertile',
                    'struct': 'bundle', 'string': 'vine', 'printf': 'plant', 'scanf': 'water',
                    'print': 'plant', 'input': 'water'
                }
                
                error_msg = None
                if token_type == '{' and index > 0:
                    paren_idx = index - 1
                    while paren_idx >= 0 and toks[paren_idx].type in self.skip_token_types:
                        paren_idx -= 1
                    
                    if paren_idx >= 0 and toks[paren_idx].type == ')':
                        paren_depth = 1
                        paren_idx -= 1
                        while paren_idx >= 0 and paren_depth > 0:
                            if toks[paren_idx].type == ')':
                                paren_depth += 1
                            elif toks[paren_idx].type == '(':
                                paren_depth -= 1
                            paren_idx -= 1
                        
                        if paren_idx >= 0:
                            id_idx = paren_idx
                            while id_idx >= 0 and toks[id_idx].type in self.skip_token_types:
                                id_idx -= 1
                            
                            if id_idx >= 0 and toks[id_idx].type == 'id' and toks[id_idx].value in common_keyword_mistakes:
                                keyword_tok = toks[id_idx]
                                correct_keyword = common_keyword_mistakes[keyword_tok.value]
                                error_msg = f"SYNTAX error line {keyword_tok.line} col {keyword_tok.col} '{keyword_tok.value}' is not a GAL keyword. Use '{correct_keyword}' instead."
                
                if error_msg is None and token_type == 'id' and token_value in common_keyword_mistakes:
                    correct_keyword = common_keyword_mistakes[token_value]
                    error_msg = f"SYNTAX error line {line} col {tok.col} '{token_value}' is not a GAL keyword. Use '{correct_keyword}' instead."
                
                if error_msg is None and token_type in {'++', '--'} and index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        if prev_tok.type in {'++', '--'}:
                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{prev_tok.value}'. Increment/decrement operators cannot be chained. {self._format_expected(expected)}"
                
                binary_operators = {'+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||'}
                if error_msg is None and token_type in binary_operators and index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        if prev_tok.type in {'++', '--'}:
                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected binary operator '{token_value}' after unary operator '{prev_tok.value}'. Increment/decrement must be standalone statements. {self._format_expected(expected)}"
                
                if error_msg is None:
                    if index > 0:
                        prev_index = index - 1
                        while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                            prev_index -= 1
                        
                        if prev_index >= 0:
                            prev_tok = toks[prev_index]
                            error_msg = f"SYNTAX error line {prev_tok.line} col {prev_tok.col + len(str(prev_tok.value))} Unexpected token '{token_value}'. Expected ';'. {self._format_expected(expected)}"
                            line = prev_tok.line
                        else:
                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. Expected ';'. {self._format_expected(expected)}"
                    else:
                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. Expected ';'. {self._format_expected(expected)}"
                
                return False, [error_msg]
            else:
                if top == 'id' and token_type == '(' and index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    if prev_index >= 0 and toks[prev_index].type == 'id':
                        kw_index = prev_index - 1
                        while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:
                            kw_index -= 1
                        if kw_index >= 0 and toks[kw_index].type == 'pollinate':
                            func_name = toks[prev_index].value
                            return False, [f"SYNTAX error line {toks[kw_index].line} col {toks[kw_index].col} Missing return type after 'pollinate'. '{func_name}' was parsed as the return type, not the function name. Expected: 'branch', 'empty', 'leaf', 'seed', 'tree', 'vine'"]

                if top == 'id' and token_type == ')' and index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    if prev_index >= 0 and toks[prev_index].type == 'id':
                        comma_index = prev_index - 1
                        while comma_index >= 0 and toks[comma_index].type in self.skip_token_types:
                            comma_index -= 1
                        if comma_index >= 0 and toks[comma_index].type == ',':
                            param_name = toks[prev_index].value
                            param_expected = {'seed', 'tree', 'leaf', 'vine', 'branch'}
                            return False, [f"SYNTAX error line {toks[prev_index].line} col {toks[prev_index].col} Missing type for parameter '{param_name}'. Each parameter requires a type. {self._format_expected(param_expected)}"]

                error_msg = self._generate_helpful_error(
                    top, token_type, token_value, line, tok.col, expected, index, toks
                )
                return False, [error_msg]

        while index < len(toks) and toks[index].type in self.skip_token_types:
            index += 1
        if index < len(toks) and toks[index].type != self.end_marker:
            tok = toks[index]
            return False, [
                f"SYNTAX error line {tok.line} col {tok.col} Unexpected token '{tok.value}' after program end. All code must be inside functions or global declarations. {self._format_expected({self.end_marker})}"
            ]
        
        return True, []

    def parse_and_build(self, tokens: Sequence[Any]):
        syntax_ok, syntax_errors = self.parse(tokens)
        if not syntax_ok:
            return {
                "success": False,
                "errors": syntax_errors,
                "ast": None,
                "symbol_table": {},
            }

        try:
            filtered = [t for t in tokens if getattr(t, 'type', '') != '\n']
            ast = _build_ast(filtered)

            st = {
                "variables": [
                    {
                        "name": name,
                        "type": info["type"],
                        "scope": "global",
                        "is_list": info.get("is_list", False),
                        "is_constant": info.get("is_fertile", False),
                    }
                    for name, info in _builder_st.variables.items()
                ],
                "functions": {
                    name: {
                        "return_type": info["return_type"],
                        "params": [
                            {
                                "type": p.children[0].value if p.children else "unknown",
                                "name": p.children[1].value if len(p.children) > 1 else "unknown",
                            }
                            for p in info["params"]
                        ] if info["params"] else [],
                    }
                    for name, info in _builder_st.functions.items()
                },
            }

            return {
                "success": True,
                "errors": [],
                "ast": ast,
                "symbol_table": st,
            }

        except _SemanticError as e:
            return {
                "success": False,
                "errors": [str(e)],
                "ast": None,
                "symbol_table": {},
                "error_stage": "semantic",
            }


