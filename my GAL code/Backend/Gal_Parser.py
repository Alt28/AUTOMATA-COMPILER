"""

LL(1) table-driven parser for GrowALanguage (GAL).

Aligned to GAL-FINALDOCX.pdf conventions:
- The start symbol is <program>.
- The empty/epsilon production is represented as λ in the document.

You provide:
- cfg: {NonTerminal: [production, ...]}, where production is a list[str]
- predict_sets: {(NonTerminal, tuple(production)): set(terminals)}
- first_sets: {NonTerminal: set(terminals including possibly λ)}

Token requirements:
- Each token must expose: .type, .value, .line
  (dict tokens with keys 'type'/'value'/'line' are also accepted)

Notes:
- If your lexer emits newline tokens (e.g., 'nl'), you can skip them by default.
  If your grammar explicitly expects newlines, pass skip_token_types=set().
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple


@dataclass(frozen=True)
class _TokView:
    """Lightweight view to normalize token access."""
    type: str
    value: str
    line: int
    col: int = 0


def _as_tok(token: Any) -> _TokView:
    """Normalize token objects/dicts to a common view."""
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

        # GAL uses λ to denote the empty production in its CFG/FIRST/FOLLOW/PREDICT sets.
        self.epsilon_symbols: Set[str] = set(epsilon_symbols)
        self.start_symbol = start_symbol
        self.end_marker = end_marker

        # If lexer emits newlines as tokens, treat them as skippable by default.
        self.skip_token_types: Set[str] = set(skip_token_types or {"nl"})
        self.token_type_alias = token_type_alias or {
            # Helpful defaults based on inconsistencies seen in the document's token labels
            # (e.g., 'idf' vs 'id', 'dbllit' vs 'dblit').
            'idf': 'id',
            'dbllit': 'dblit',
        }

        self.parsing_table: Dict[str, Dict[str, List[str]]] = self.construct_parsing_table()

    def construct_parsing_table(self) -> Dict[str, Dict[str, List[str]]]:
        """Build LL(1) parsing table using provided PREDICT sets."""
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
        """Map lexer token types into the terminal names used by the CFG."""
        return self.token_type_alias.get(token_type, token_type)

    def _ensure_eof(self, toks: List[_TokView]) -> List[_TokView]:
        if not toks:
            return [_TokView(self.end_marker, self.end_marker, 1, 0)]
        if toks[-1].type != self.end_marker:
            last_line = toks[-1].line or 1
            last_col = toks[-1].col or 0
            toks = toks + [_TokView(self.end_marker, self.end_marker, last_line, last_col)]
        return toks

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
        """Generate contextual error messages for common syntax mistakes."""
        
        # PRIORITY CHECK: Detect malformed literals in current token
        if token_type == 'chrlit' and token_value and not token_value.endswith("'"):
            return f"SYNTAX error line {line} col {col} Missing closing single quote in character literal"
        
        if token_type == 'strlit' and token_value and not token_value.endswith('"'):
            return f"SYNTAX error line {line} col {col} Missing closing double quote in string literal"
        
        # Check next token if it exists (look-ahead for malformed literals)
        if index + 1 < len(toks):
            next_tok = toks[index + 1]
            if next_tok.type == 'chrlit' and next_tok.value and not next_tok.value.endswith("'"):
                return f"SYNTAX error line {next_tok.line} col {next_tok.col} Missing closing single quote in character literal"
            
            if next_tok.type == 'strlit' and next_tok.value and not next_tok.value.endswith('"'):
                return f"SYNTAX error line {next_tok.line} col {next_tok.col} Missing closing double quote in string literal"
        
        # Check for semicolon after bundle closing brace (common mistake)
        if token_type == ';' and non_terminal == '<global_declaration>':
            # Look back to see if previous token was '}' from a bundle definition
            if index > 0:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0 and toks[prev_index].type == '}':
                    # Look further back to see if this was a bundle definition
                    bundle_index = prev_index - 1
                    while bundle_index >= 0 and toks[bundle_index].type in self.skip_token_types:
                        bundle_index -= 1
                    
                    # Check if we can find 'bundle' keyword before this
                    found_bundle = False
                    for i in range(bundle_index, max(0, bundle_index - 20), -1):
                        if toks[i].type == 'bundle':
                            found_bundle = True
                            break
                    
                    if found_bundle:
                        return f"SYNTAX error line {line} col {col} Unexpected ';' after bundle definition. Bundle definitions don't need a semicolon after the closing '}}'. Remove this ';'"
        
        # Check for common invalid keywords from other languages (check early)
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
            return f"SYNTAX error line {line} col {col} '{token_value}' expected '{correct_keyword}'"
        
        # Check for bundle definition inside a function (common mistake)
        if token_type == '{' and (non_terminal == '<bundle_or_var>' or non_terminal == '<bundle_mem_dec>'):
            # This means we saw "bundle id {" but inside a function body
            # In global scope, this would be a bundle definition, but it's not allowed inside functions
            return f"SYNTAX error line {line} col {col} Bundle definitions must be at global scope (outside all functions). Move this bundle definition before 'root()'"
        
        # Check if semicolon is expected and we're seeing a keyword/statement starter
        statement_starters = {
            'reclaim', 'spring', 'wither', 'bud', 'grow', 'cultivate', 'tend',
            'harvest', 'prune', 'skip', 'water', 'plant', 'seed', 'leaf',
            'branch', 'tree', 'vine', 'bundle', 'fertile', 'pollinate', 'root', 'id'
        }
        
        if ';' in expected:
            if token_type in statement_starters or token_type == 'id':
                # Look back at previous token to show what was incomplete
                # Skip past newlines to find the actual meaningful previous token
                if index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        
                        # Check if previous token is a malformed character literal (missing closing quote)
                        if prev_tok.type == 'chrlit' and prev_tok.value and not prev_tok.value.endswith("'"):
                            prev_line = prev_tok.line
                            prev_col = prev_tok.col
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing single quote in character literal"
                        
                        # Check if previous token is a malformed string literal (missing closing quote)
                        if prev_tok.type == 'strlit' and prev_tok.value and not prev_tok.value.endswith('"'):
                            prev_line = prev_tok.line
                            prev_col = prev_tok.col
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing double quote in string literal"
                        
                        prev_line = prev_tok.line
                        prev_col = prev_tok.col + len(str(prev_tok.value))
                        if prev_line != line:  # Previous token on different line
                            return (f"SYNTAX error line {prev_line} col {prev_col} expected ';' after '{prev_tok.value}'")
                        else:
                            return f"SYNTAX error line {line} col {col} expected ';' before '{token_value}'"
            elif token_type == '}':
                # Missing semicolon before closing brace
                if index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        
                        # Check if previous token is a malformed character literal (missing closing quote)
                        if prev_tok.type == 'chrlit' and prev_tok.value and not prev_tok.value.endswith("'"):
                            prev_line = prev_tok.line
                            prev_col = prev_tok.col
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing single quote in character literal"
                        
                        # Check if previous token is a malformed string literal (missing closing quote)
                        if prev_tok.type == 'strlit' and prev_tok.value and not prev_tok.value.endswith('"'):
                            prev_line = prev_tok.line
                            prev_col = prev_tok.col
                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing double quote in string literal"
                        
                        prev_line = prev_tok.line
                        prev_col = prev_tok.col + len(str(prev_tok.value))
                        if prev_line != line:
                            return f"SYNTAX error line {prev_line} col {prev_col} expected ';' after '{prev_tok.value}'"
                        else:
                            return f"SYNTAX error line {line} col {col} expected ';' before '}}'"
        
        # Check for missing reclaim statement
        if 'reclaim' in expected and token_type == '}':
            return f"SYNTAX error line {line} col {col} expected 'reclaim' statement before closing '}}'. Functions must end with 'reclaim;'"
        
        # Check for missing prune (break) in variety (case) statements
        if 'prune' in expected and token_type in {'variety', 'soil', '}'}:
            if token_type == 'variety':
                return f"SYNTAX error line {line} col {col} expected 'prune;' before next 'variety'. Each case in 'harvest' (switch) must end with 'prune;'"
            elif token_type == 'soil':
                return f"SYNTAX error line {line} col {col} expected 'prune;' before 'soil' (default case). Each case must end with 'prune;'"
            else:  # token_type == '}'
                return f"SYNTAX error line {line} col {col} expected 'prune;' before closing '}}'. Each case must end with 'prune;'"
        
        # Check for unary minus/plus usage (not supported in grammar) - must check BEFORE missing value error
        if token_type in {'-', '+'} and non_terminal in {'<expression>', '<factor>', '<term>', '<arithmetic>', '<logic_or>', '<logic_and>', '<relational>', '<init_val>'}:
            # Look back to see what preceded this operator
            if index > 0:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0:
                    prev_tok = toks[prev_index]
                    # If preceded by assignment or operators, likely trying to use unary operator
                    if prev_tok.type in {'=', '+=', '-=', '*=', '/=', '%=', '(', ','}:
                        if token_value == '-':
                            return f"SYNTAX error line {line} col {col} Unary '-' not supported. Use '~' for negative numbers (e.g., '~5') or '(0 - value)' for negation"
                        else:
                            return f"SYNTAX error line {line} col {col} Unary '+' operator not supported. Use parentheses for expressions like '(0 + value)'"
        
        # Check for missing opening parenthesis
        if '(' in expected and token_type != '(':
            # Check if previous token was an arithmetic/logical operator - missing operand case
            # BUT skip if current token is +/- (handled above as unary operator case)
            if index > 0 and token_type not in {'-', '+'}:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0:
                    prev_tok = toks[prev_index]
                    # If an operator precedes the current token, user likely forgot an operand
                    if prev_tok.type in {'+', '-', '*', '/', '%', '=', '+=', '-=', '*=', '/=', '%=', '&&', '||', '==', '!=', '<', '>', '<=', '>='}:
                        return f"SYNTAX error line {line} col {col} Missing value after '{prev_tok.value}' operator"
            
            # Don't report misleading "missing parenthesis" for assignment operators
            # This likely indicates an invalid chained assignment
            if token_type in {'=', '+=', '-=', '*=', '/=', '%='}:
                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. Expected: {expected}"
            
            # Look back to find the keyword/statement that needs parentheses
            if index > 0:
                prev_index = index - 1
                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                    prev_index -= 1
                
                if prev_index >= 0:
                    prev_tok = toks[prev_index]
                    
                    # Check if previous token was an invalid keyword from other languages
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
                        return f"SYNTAX error line {prev_tok.line} col {prev_tok.col} '{prev_tok.value}' expected '{correct_keyword}'"
                    
                    # Keywords that require parentheses
                    keywords_needing_parens = {'spring', 'grow', 'cultivate', 'harvest', 'water', 'plant', 'tend', 'bud'}
                    if prev_tok.type in keywords_needing_parens:
                        return f"SYNTAX error line {line} col {col} expected '(' after '{prev_tok.value}'"
                    
                    # If previous token was an identifier, provide helpful message
                    if prev_tok.type == 'id':
                        return f"SYNTAX error line {prev_tok.line} col {prev_tok.col} invalid statement: identifier '{prev_tok.value}' must be followed by assignment operator, unary operator (++/--), or function call syntax '()'"
            
            # Fallback message
            return f"SYNTAX error line {line} col {col} expected '('"
        
        # Check for missing closing braces
        if '}' in expected and token_type in statement_starters:
            # Special case: bud/wither appearing without a preceding spring
            if token_type == 'bud':
                return f"SYNTAX error line {line} col {col} 'bud' can only appear after a 'spring' statement"
            elif token_type == 'wither':
                return f"SYNTAX error line {line} col {col} 'wither' can only appear after a 'spring' or 'bud' statement"
            elif token_type == 'reclaim':
                return f"SYNTAX error line {line} col {col} expected '}}' before '{token_value}'. Missing closing brace"
            return f"SYNTAX error line {line} col {col} expected '}}' before '{token_value}'. Missing closing brace"
        
        # Check for missing closing parenthesis
        if ')' in expected and token_type not in {')'}:
            return f"SYNTAX error line {line} col {col} expected ')' before '{token_value}'. Missing closing parenthesis"
        
        # Default message with helpful context
        return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. Expected: {expected}"

    def parse(self, tokens: Sequence[Any]) -> Tuple[bool, List[str]]:
        """Parse tokens according to the supplied CFG/PREDICT sets.

        Returns:
            (success, errors)
        """
        toks = [_as_tok(t) for t in tokens]
        toks = [_TokView(self._normalize_token_type(t.type), t.value, t.line, t.col) for t in toks]
        toks = self._ensure_eof(toks)

        stack: List[str] = [self.end_marker, self.start_symbol]
        index = 0
        errors: List[str] = []

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

            # Skip configured whitespace-like tokens unless grammar explicitly expects them.
            if token_type in self.skip_token_types and top != token_type:
                index += 1
                continue

            # Expand non-terminal
            if top in self.parsing_table:
                row = self.parsing_table[top]
                if token_type in row:
                    production = row[token_type]
                    
                    # Check for empty blocks in conditionals/loops
                    # When <statement> expands to epsilon and next token is '}', check if inside conditional/loop
                    if top == '<statement>' and token_type == '}':
                        is_epsilon = (len(production) == 0 or (len(production) == 1 and production[0] in self.epsilon_symbols))
                        if is_epsilon:
                            # Look back to find the opening brace
                            lookback = index - 1
                            while lookback >= 0 and toks[lookback].type in self.skip_token_types:
                                lookback -= 1
                            
                            # If we immediately see '{' after skipping whitespace, it's an empty block
                            if lookback >= 0 and toks[lookback].type == '{':
                                # Find what's before the brace
                                before_brace = lookback - 1
                                while before_brace >= 0 and toks[before_brace].type in self.skip_token_types:
                                    before_brace -= 1
                                
                                # Check if there's a ')' before the brace (conditional/loop pattern)
                                if before_brace >= 0 and toks[before_brace].type == ')':
                                    # Find the matching '(' and the keyword before it
                                    paren_depth = 1
                                    paren_pos = before_brace - 1
                                    while paren_pos >= 0 and paren_depth > 0:
                                        if toks[paren_pos].type == ')':
                                            paren_depth += 1
                                        elif toks[paren_pos].type == '(':
                                            paren_depth -= 1
                                        paren_pos -= 1
                                    
                                    # Find keyword before the '('
                                    if paren_pos >= 0:
                                        kw_pos = paren_pos
                                        while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:
                                            kw_pos -= 1
                                        
                                        if kw_pos >= 0:
                                            kw = toks[kw_pos]
                                            # These keywords require at least one statement in their blocks
                                            conditional_keywords = {'spring', 'bud', 'wither', 'grow', 'cultivate', 'tend', 'harvest'}
                                            if kw.type in conditional_keywords:
                                                errors.append(f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required")
                                                return False, errors
                    
                    stack.pop()

                    # Push RHS (unless epsilon)
                    if not (
                        len(production) == 0
                        or (len(production) == 1 and production[0] in self.epsilon_symbols)
                    ):
                        stack.extend(reversed(production))
                    continue

                expected = set(row.keys())
                
                # Enhanced error messages for common mistakes
                error_msg = self._generate_helpful_error(top, token_type, token_value, line, tok.col, expected, index, toks)
                errors.append(error_msg)
                return False, errors

            # Match terminal
            if top == token_type:
                # Check for numeric literal in control flow condition
                if top == 'intlit' or top == 'dblit':
                    # Look back to see if we're inside a control flow condition
                    # Check if there's a '(' before this and a control flow keyword before that
                    lookback = index - 1
                    while lookback >= 0 and toks[lookback].type in self.skip_token_types:
                        lookback -= 1
                    
                    if lookback >= 0 and toks[lookback].type == '(':
                        # Found '(', now check for control flow keyword before it
                        kw_pos = lookback - 1
                        while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:
                            kw_pos -= 1
                        
                        if kw_pos >= 0:
                            kw = toks[kw_pos]
                            condition_keywords = {'spring', 'grow', 'cultivate', 'tend', 'bud'}
                            if kw.type in condition_keywords:
                                # Check if next token after the literal is ')' (meaning no comparison operator)
                                next_idx = index + 1
                                while next_idx < len(toks) and toks[next_idx].type in self.skip_token_types:
                                    next_idx += 1
                                
                                if next_idx < len(toks) and toks[next_idx].type == ')':
                                    errors.append(f"SYNTAX error line {line} col {tok.col} '{kw.value}' requires a boolean condition, not a numeric literal")
                                    return False, errors
                
                stack.pop()
                index += 1
                continue

            # If the stack expects EOF but we still have skippable tokens, skip them.
            if top == self.end_marker and token_type in self.skip_token_types:
                index += 1
                continue

            expected = {top}
            shown_value = "EOF" if token_type == self.end_marker else token_value
            
            # Enhanced error messages for specific missing tokens
            if top == 'reclaim' and token_type == '}':
                # Check if we're in root() function vs regular function
                # Look back to find if this is root() or a regular function
                is_root = False
                for i in range(index - 1, -1, -1):
                    if toks[i].type == 'root':
                        is_root = True
                        break
                    elif toks[i].type == 'pollinate':
                        is_root = False
                        break
                
                if is_root:
                    errors.append(f"SYNTAX error line {line} col {tok.col} expected 'reclaim;' before '}}'. The root() function (main program) must end with 'reclaim;'")
                else:
                    errors.append(f"SYNTAX error line {line} col {tok.col} expected 'reclaim;' before '}}'. All functions must end with 'reclaim;'")
                return False, errors
            elif top == 'prune' and token_type in {'variety', 'soil', '}'}:
                # Missing prune (break) in variety (case) statement
                if token_type == 'variety':
                    errors.append(f"SYNTAX error line {line} col {tok.col} expected 'prune;' before next 'variety'. Each case in 'harvest' (switch) must end with 'prune;'")
                elif token_type == 'soil':
                    errors.append(f"SYNTAX error line {line} col {tok.col} expected 'prune;' before 'soil' (default case). Each case must end with 'prune;'")
                else:
                    errors.append(f"SYNTAX error line {line} col {tok.col} expected 'prune;' before closing '}}'. Each case must end with 'prune;'")
                return False, errors
            elif top == '(' and token_type != '(':
                # Don't give misleading "missing opening parenthesis" error for assignment operators
                # This happens when there's a chained assignment which is not supported
                if token_type in {'=', '+=', '-=', '*=', '/=', '%='}:
                    errors.append(f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. Expected: {expected}")
                    return False, errors
                elif index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        
                        # Special case: tend requires condition after closing brace
                        if prev_tok.type == '}':
                            # Look back to find 'tend' keyword
                            brace_depth = 1
                            scan_idx = prev_index - 1
                            while scan_idx >= 0 and brace_depth > 0:
                                if toks[scan_idx].type == '}':
                                    brace_depth += 1
                                elif toks[scan_idx].type == '{':
                                    brace_depth -= 1
                                scan_idx -= 1
                            
                            # Now check if 'tend' is before the opening brace
                            if scan_idx >= 0:
                                kw_idx = scan_idx
                                while kw_idx >= 0 and toks[kw_idx].type in self.skip_token_types:
                                    kw_idx -= 1
                                
                                if kw_idx >= 0 and toks[kw_idx].type == 'tend':
                                    errors.append(f"SYNTAX error line {line} col {tok.col} expected '(' after closing brace. 'tend' requires a condition after closing brace '}}'. Format: tend {{ ... }} (condition);")
                                else:
                                    errors.append(f"SYNTAX error line {line} col {tok.col} expected '('")
                            else:
                                errors.append(f"SYNTAX error line {line} col {tok.col} expected '('")
                        else:
                            keywords_needing_parens = {'spring', 'grow', 'cultivate', 'harvest', 'water', 'plant', 'tend', 'bud'}
                            if prev_tok.type in keywords_needing_parens:
                                errors.append(f"SYNTAX error line {line} col {tok.col} expected '(' after '{prev_tok.value}'")
                            else:
                                errors.append(f"SYNTAX error line {line} col {tok.col} expected '('")
                    else:
                        errors.append(f"SYNTAX error line {line} col {tok.col} expected '('")
                else:
                    errors.append(f"SYNTAX error line {line} col {tok.col} expected '('")
                return False, errors
            elif top == '{' and token_type != '{':
                # Missing opening brace - look back to find the keyword
                if index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        # Keywords/tokens that require braces
                        keywords_needing_braces = {'spring', 'wither', 'grow', 'cultivate', 'tend', 'harvest', 'bud', ')', 'pollinate', 'root'}
                        if prev_tok.type in keywords_needing_braces:
                            if prev_tok.type == ')':
                                # Look further back to find the keyword before the closing paren
                                paren_index = prev_index - 1
                                paren_count = 1
                                while paren_index >= 0 and paren_count > 0:
                                    if toks[paren_index].type == ')':
                                        paren_count += 1
                                    elif toks[paren_index].type == '(':
                                        paren_count -= 1
                                    paren_index -= 1
                                
                                # Now find the keyword before the opening paren
                                if paren_index >= 0:
                                    kw_index = paren_index
                                    while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:
                                        kw_index -= 1
                                    
                                    if kw_index >= 0:
                                        kw_tok = toks[kw_index]
                                        if kw_tok.type in {'spring', 'grow', 'cultivate', 'tend', 'harvest', 'bud', 'pollinate', 'root'}:
                                            errors.append(f"SYNTAX error line {line} col {tok.col} expected '{{' after '{kw_tok.value}' statement")
                                        else:
                                            errors.append(f"SYNTAX error line {line} col {tok.col} expected '{{'")
                                    else:
                                        errors.append(f"SYNTAX error line {line} col {tok.col} expected '{{'")
                                else:
                                    errors.append(f"SYNTAX error line {line} col {tok.col} expected '{{'")
                            else:
                                errors.append(f"SYNTAX error line {line} col {tok.col} expected '{{' after '{prev_tok.value}'")
                        else:
                            errors.append(f"SYNTAX error line {line} col {tok.col} expected '{{'")
                    else:
                        errors.append(f"SYNTAX error line {line} col {tok.col} expected '{{'")
                else:
                    errors.append(f"SYNTAX error line {line} col {tok.col} expected '{{'")
                return False, errors
            elif top == '}' and token_type != '}':
                # Missing closing brace
                errors.append(f"SYNTAX error line {line} col {tok.col} expected '}}'. Missing closing brace")
                return False, errors
            elif top == ')' and token_type != ')':
                # Missing closing parenthesis
                errors.append(f"SYNTAX error line {line} col {tok.col} expected ')'. Missing closing parenthesis")
                return False, errors
            elif top == ';' and token_type != ';':
                # Missing semicolon - but check if this might be an invalid keyword used as a function
                # Pattern: "if (condition) {" where parser saw "if()" as a function call  
                common_keyword_mistakes = {
                    'function': 'pollinate', 'int': 'seed', 'float': 'tree', 'double': 'tree',
                    'char': 'leaf', 'bool': 'branch', 'boolean': 'branch', 'if': 'spring',
                    'else': 'wither', 'elif': 'bud', 'while': 'grow', 'for': 'cultivate',
                    'switch': 'harvest', 'case': 'variety', 'default': 'soil', 'break': 'prune',
                    'continue': 'skip', 'return': 'reclaim', 'void': 'empty', 'const': 'fertile',
                    'struct': 'bundle', 'string': 'vine', 'printf': 'plant', 'scanf': 'water',
                    'print': 'plant', 'input': 'water'
                }
                
                # Check if current token is '{' after what looks like a function call with invalid keyword
                if token_type == '{' and index > 0:
                    # Look back for a closing parenthesis
                    paren_idx = index - 1
                    while paren_idx >= 0 and toks[paren_idx].type in self.skip_token_types:
                        paren_idx -= 1
                    
                    if paren_idx >= 0 and toks[paren_idx].type == ')':
                        # Find the matching opening parenthesis
                        paren_depth = 1
                        paren_idx -= 1
                        while paren_idx >= 0 and paren_depth > 0:
                            if toks[paren_idx].type == ')':
                                paren_depth += 1
                            elif toks[paren_idx].type == '(':
                                paren_depth -= 1
                            paren_idx -= 1
                        
                        # Check token before the opening parenthesis
                        if paren_idx >= 0:
                            id_idx = paren_idx
                            while id_idx >= 0 and toks[id_idx].type in self.skip_token_types:
                                id_idx -= 1
                            
                            if id_idx >= 0 and toks[id_idx].type == 'id' and toks[id_idx].value in common_keyword_mistakes:
                                keyword_tok = toks[id_idx]
                                correct_keyword = common_keyword_mistakes[keyword_tok.value]
                                errors.append(f"SYNTAX error line {keyword_tok.line} col {keyword_tok.col} '{keyword_tok.value}' expected '{correct_keyword}'")
                                return False, errors
                
                # Check if CURRENT token (the one we're looking at) is an invalid keyword
                if token_type == 'id' and token_value in common_keyword_mistakes:
                    correct_keyword = common_keyword_mistakes[token_value]
                    errors.append(f"SYNTAX error line {line} col {tok.col} '{token_value}' expected '{correct_keyword}'")
                    return False, errors
                
                # Otherwise, it's a missing semicolon - report on the line where it should be added
                if index > 0:
                    prev_index = index - 1
                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:
                        prev_index -= 1
                    
                    if prev_index >= 0:
                        prev_tok = toks[prev_index]
                        # Report error on the line of the previous token (where semicolon should be)
                        errors.append(f"SYNTAX error line {prev_tok.line} col {prev_tok.col + len(str(prev_tok.value))} expected ';'")
                    else:
                        errors.append(f"SYNTAX error line {line} col {tok.col} expected ';'")
                else:
                    errors.append(f"SYNTAX error line {line} col {tok.col} expected ';'")
                return False, errors
            else:
                # Use the helper method for better error messages
                error_msg = self._generate_helpful_error(
                    top, token_type, token_value, line, tok.col, expected, index, toks
                )
                errors.append(error_msg)
                return False, errors

        # Consume trailing skippables then require EOF
        while index < len(toks) and toks[index].type in self.skip_token_types:
            index += 1
        if index < len(toks) and toks[index].type != self.end_marker:
            tok = toks[index]
            return False, [
                f"SYNTAX error line {tok.line} col {tok.col} Unexpected token '{tok.value}' after program end. All code must be inside functions or global declarations"
            ]
        return True, []











