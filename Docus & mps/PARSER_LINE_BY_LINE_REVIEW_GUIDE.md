# Parser Line-by-Line Review Guide

Generated: 2026-06-07 17:08:55
Source file: `Backend\parser\parser.py`
Total lines: 2335

## 1. Purpose
`parser.py` checks the lexer token stream against the CFG/PREDICT table. It only calls `builder.py` after syntax succeeds.

## 2. Important Parser Lines
| Concept | Line | Explanation |
|---|---:|---|
| Token view class | 30 | Internal simple token shape: type, value, line, col. |
| Token converter | 44 | Converts lexer Token/dict into _TokView. |
| Parser class | 74 | Main LL(1) parser class. |
| Parser setup | 76 | Stores CFG, PREDICT, FIRST, EOF, skip tokens, and builds the table. |
| Parse table builder | 131 | Turns PREDICT sets into parsing_table[non_terminal][lookahead]. |
| Normalize token type | 167 | Maps lexer token aliases to grammar terminal names. |
| Ensure EOF | 172 | Adds EOF when missing. |
| Expected-token formatter | 228 | Makes expected-token text readable. |
| Helpful error builder | 270 | Creates custom syntax messages. |
| Main parse algorithm | 1141 | Runs the stack-based LL(1) checker. |
| Convert tokens | 1146 | First step inside parse(): simplify incoming tokens. |
| Initialize stack | 1162 | Stack begins with EOF and <program>. |
| Main stack loop | 1192 | Repeatedly compares stack top with current lookahead token. |
| Non-terminal branch | 1214 | Uses parse table when stack top is a CFG non-terminal. |
| Production selection | 1222 | Chooses the RHS predicted by current lookahead. |
| Push production | 1311 | Pushes RHS reversed so the leftmost symbol is processed next. |
| Terminal match | 1343 | Consumes input when expected terminal matches lookahead. |
| Public parse/build API | 2224 | Syntax first, then AST build. |
| Call parse | 2227 | Stops before builder if syntax is invalid. |
| Filter comments/newlines | 2252 | Builder receives only meaningful tokens. |
| Call builder.py | 2254 | Creates AST after syntax success. |

## 3. Functions and Classes
| Kind | Name | Lines | Purpose |
|---|---|---:|---|
| ClassDef | `_TokView` | 30-40 | Internal token view with type, value, line, col. |
| FunctionDef | `_as_tok` | 44-70 | Converts input tokens to _TokView. |
| ClassDef | `LL1Parser` | 74-2335 | Main LL(1) syntax checker. |
| method | `LL1Parser.__init__` | 76-128 | Saves grammar data and builds parse table. |
| method | `LL1Parser.construct_parsing_table` | 131-163 | Builds table from PREDICT sets. |
| method | `LL1Parser._normalize_token_type` | 167-169 | Fixes token-name aliases. |
| method | `LL1Parser._ensure_eof` | 172-186 | Guarantees EOF token at the end. |
| method | `LL1Parser._format_expected` | 228-267 | Formats expected-token lists. |
| method | `LL1Parser._generate_helpful_error` | 270-1138 | Creates detailed syntax errors. |
| method | `LL1Parser.parse` | 1141-2221 | Main stack-based parser algorithm. |
| method | `LL1Parser.parse_and_build` | 2224-2335 | Runs syntax then builder. |

## 4. CFG References
| Symbol | grammar.py Line | Use |
|---|---:|---|
| `<program>` | 231 | Whole program shape. |
| `<function_definition>` | 237 | pollinate functions before root. |
| `<local_declaration>` | 247 | Declarations at start of block. |
| `<body_statement>` | 249 | Executable statements. |
| `<non_reclaim_stmt>` | 529 | Normal statements except reclaim. |
| `<expression>` | 366 | Expression entry. |
| `<factor>` | 1089 | Literals, ids, calls, parentheses. |
| `<io_stmt>` | 542 | plant/water statements. |
| `<conditional_stmt>` | 544 | spring/bud/wither. |
| `<loop_stmt>` | 546 | grow/cultivate/tend/harvest. |
| `<for_init>` | 796 | cultivate init. |
| `<for_update>` | 804 | cultivate update. |
| `<factor_id_next>` | 1109 | What can come after id. |

## 5. Key Code Blocks
### Token Conversion
Lines 44-70
```python
44: def _as_tok(token: Any) -> _TokView:
45:     # LINE: Accept dictionary tokens from API/tests.
46:     if isinstance(token, Mapping):
47:         # AUTO: Returns this result to the caller.
48:         return _TokView(
49:             # AUTO: Sets `type`.
50:             type=str(token.get("type", "")),
51:             # AUTO: Sets `value`.
52:             value=str(token.get("value", "")),
53:             # AUTO: Sets `line`.
54:             line=int(token.get("line", 0) or 0),
55:             # AUTO: Sets `col`.
56:             col=int(token.get("col", 0) or 0),
57:         # AUTO: Closes the current grouped code/data.
58:         )
59:     # LINE: Accept Token objects from the lexer.
60:     return _TokView(
61:         # AUTO: Sets `type`.
62:         type=str(getattr(token, "type", "")),
63:         # AUTO: Sets `value`.
64:         value=str(getattr(token, "value", "")),
65:         # AUTO: Sets `line`.
66:         line=int(getattr(token, "line", 0) or 0),
67:         # AUTO: Sets `col`.
68:         col=int(getattr(token, "col", 0) or 0),
69:     # AUTO: Closes the current grouped code/data.
70:     )
```
Accepts lexer tokens and API-style dicts.

### Parser Setup
Lines 76-128
```python
76:     def __init__(
77:         # AUTO: Executes this statement.
78:         self,
79:         # AUTO: Executes this statement.
80:         cfg: Dict[str, List[List[str]]],
81:         # AUTO: Executes this statement.
82:         predict_sets: Dict[Tuple[str, Tuple[str, ...]], Set[str]],
83:         # AUTO: Executes this statement.
84:         first_sets: Dict[str, Set[str]],
85:         # AUTO: Executes this statement.
86:         *,
87:         # AUTO: Sets `start_symbol: str`.
88:         start_symbol: str = "<program>",
89:         # AUTO: Sets `end_marker: str`.
90:         end_marker: str = "EOF",
91:         # AUTO: Sets `epsilon_symbols: Iterable[str]`.
92:         epsilon_symbols: Iterable[str] = ("λ", "ε"),
93:         # AUTO: Sets `skip_token_types: Optional[Set[str]]`.
94:         skip_token_types: Optional[Set[str]] = None,
95:         # AUTO: Sets `token_type_alias: Optional[Dict[str, str]]`.
96:         token_type_alias: Optional[Dict[str, str]] = None,
97:     # AUTO: Closes the current grouped code/data.
98:     ):
99:         # AUTO: Sets `self.cfg`.
100:         self.cfg = cfg
101:         # AUTO: Sets `self.predict_sets`.
102:         self.predict_sets = predict_sets
103:         # AUTO: Sets `self.first_sets`.
104:         self.first_sets = first_sets
105: 
106:         # AUTO: Sets `self.epsilon_symbols: Set[str]`.
107:         self.epsilon_symbols: Set[str] = set(epsilon_symbols)
108:         # AUTO: Sets `self.start_symbol`.
109:         self.start_symbol = start_symbol
110:         # AUTO: Sets `self.end_marker`.
111:         self.end_marker = end_marker
112: 
113:         # Comments ('comment' = //..., 'mcommentlit' = /*...*/) are emitted by
114:         # the lexer for the lexeme table but are not grammar tokens, so the
115:         # parser skips them just like newlines.
116:         # AUTO: Sets `self.skip_token_types: Set[str]`.
117:         self.skip_token_types: Set[str] = set(skip_token_types or {"\n", "comment", "mcommentlit"})
118:         # AUTO: Sets `self.token_type_alias`.
119:         self.token_type_alias = token_type_alias or {
120:             # AUTO: Executes this statement.
121:             'idf': 'id',
122:             # AUTO: Executes this statement.
123:             'dbllit': 'dblit',
124:         # AUTO: Closes the current grouped code/data.
125:         }
126:         
127:         # AUTO: Sets `self.parsing_table: Dict[str, Dict[str, List[str]]]`.
128:         self.parsing_table: Dict[str, Dict[str, List[str]]] = self.construct_parsing_table()
```
Stores grammar state and parse table.

### Parse Table Construction
Lines 131-163
```python
131:     def construct_parsing_table(self) -> Dict[str, Dict[str, List[str]]]:
132:         # GUIDE: Convert PREDICT sets into table[non_terminal][lookahead] = production.
133:         # LINE: table maps each non-terminal and lookahead token to one CFG rule.
134:         table: Dict[str, Dict[str, List[str]]] = {}
135: 
136:         # LINE: Visit every non-terminal in the grammar.
137:         for non_terminal, productions in self.cfg.items():
138:             # LINE: row stores all lookahead choices for this non-terminal.
139:             row: Dict[str, List[str]] = {}
140:             # LINE: Visit every production under the current non-terminal.
141:             for production in productions:
142:                 # LINE: This key matches how predict_sets stores each production.
143:                 key = (non_terminal, tuple(production))
144:                 # LINE: terms are the lookahead terminals that choose this production.
145:                 terms = self.predict_sets.get(key, set())
146:                 # LINE: Fill the parse table for each lookahead terminal.
147:                 for terminal in terms:
148:                     # AUTO: Checks this condition.
149:                     if terminal in row and row[terminal] != production:
150:                         # LINE: A conflict means the grammar is not LL(1) here.
151:                         raise ValueError(
152:                             # AUTO: Executes this statement.
153:                             f"LL(1) conflict at {non_terminal} with lookahead {terminal}: "
154:                             # AUTO: Executes this statement.
155:                             f"{row[terminal]} vs {production}"
156:                         # AUTO: Closes the current grouped code/data.
157:                         )
158:                     # AUTO: Sets `row[terminal]`.
159:                     row[terminal] = production
160:             # LINE: Save this non-terminal row in the final parsing table.
161:             table[non_terminal] = row
162:         # LINE: Return the completed LL(1) parse table.
163:         return table
```
Builds table from PREDICT sets.

### Parse Start
Lines 1141-1164
```python
1141:     def parse(self, tokens: Sequence[Any]) -> Tuple[bool, List[str]]:
1142:         # GUIDE: Main LL(1) stack algorithm; compare grammar symbols on the stack
1143:         # with the current lookahead token, then expand or consume.
1144:         # Convert incoming Token objects into the parser's simple _TokView form.
1145:         # LINE: Convert lexer Token objects into the parser's lightweight token view.
1146:         toks = [_as_tok(t) for t in tokens]
1147: 
1148:         # Normalize token names so lexer aliases still match grammar terminals.
1149:         # LINE: Rename token types if lexer name and grammar name differ.
1150:         toks = [_TokView(self._normalize_token_type(t.type), t.value, t.line, t.col) for t in toks]
1151: 
1152:         # Make sure the parser always has an EOF marker to know when to stop.
1153:         # LINE: Ensure EOF exists so the parsing loop has a stopping token.
1154:         toks = self._ensure_eof(toks)
1155: 
1156:         # LINE: Keep current tokens for helper error messages.
1157:         self._current_tokens = toks
1158: 
1159:         # Stack starts with EOF at the bottom and <program> on top. The parser
1160:         # repeatedly expands the top grammar symbol until the stack is empty.
1161:         # LINE: Start with EOF at bottom and <program> as the first rule to expand.
1162:         stack: List[str] = [self.end_marker, self.start_symbol]
1163:         # LINE: index points to the current lookahead token in toks.
1164:         index = 0
```
Prepares tokens and parser stack.

### Stack Loop
Lines 1192-1224
```python
1192:         while stack:
1193:             # top is the grammar symbol we need to match/expand.
1194:             # tok is the current input token from the lexer.
1195:             # LINE: Read the top grammar symbol and the current lookahead token.
1196:             top = stack[-1]
1197:             # AUTO: Sets `tok`.
1198:             tok = current_token()
1199:             # AUTO: Sets `token_type`.
1200:             token_type = tok.type
1201:             # AUTO: Sets `token_value`.
1202:             token_value = tok.value
1203:             # AUTO: Sets `line`.
1204:             line = tok.line or 1
1205: 
1206:             # LINE: Ignore comments/newlines when the grammar is not asking for them.
1207:             if token_type in self.skip_token_types and top != token_type:
1208:                 # AUTO: Adds into `index`.
1209:                 index += 1
1210:                 # AUTO: Skips to the next loop iteration.
1211:                 continue
1212: 
1213:             # LINE: Non-terminal case, such as <program> or <statement>.
1214:             if top in self.parsing_table:
1215:                 # Non-terminal case: use parsing_table[top][lookahead] to pick
1216:                 # the correct production from the CFG.
1217:                 # LINE: Get the parse-table row for this non-terminal.
1218:                 row = self.parsing_table[top]
1219:                 # LINE: If lookahead exists in this row, we know which production to use.
1220:                 if token_type in row:
1221:                     # LINE: Select the CFG production predicted by this lookahead token.
1222:                     production = row[token_type]
1223:                     
1224:                     # AUTO: Checks this condition.
```
Reads stack top and lookahead.

### Production Expansion
Lines 1298-1312
```python
1298:                     stack.pop()
1299: 
1300:                     # AUTO: Checks this condition.
1301:                     if not (
1302:                         # AUTO: Executes this statement.
1303:                         len(production) == 0
1304:                         # AUTO: Calls `or`.
1305:                         or (len(production) == 1 and production[0] in self.epsilon_symbols)
1306:                     # AUTO: Closes the current grouped code/data.
1307:                     ):
1308:                         # Push production in reverse so the leftmost grammar
1309:                         # symbol is processed next.
1310:                         # LINE: Push RHS in reverse so the first RHS symbol becomes stack top.
1311:                         stack.extend(reversed(production))
1312:                     # AUTO: Skips to the next loop iteration.
```
Replaces non-terminal with RHS.

### Terminal Match
Lines 1343-1365
```python
1343:             if top == token_type:
1344:                 # Terminal case: grammar expected the same token type the lexer
1345:                 # produced, so consume it by popping stack and moving index.
1346:                 # LINE: Remember declared type when consuming a data-type token.
1347:                 if token_type in {'seed', 'tree', 'leaf', 'branch', 'vine'}:
1348:                     # AUTO: Sets `current_var_type`.
1349:                     current_var_type = token_type
1350:                     # AUTO: Sets `expecting_value_for_type`.
1351:                     expecting_value_for_type = None
1352:                 
1353:                 # AUTO: Checks the next alternate condition.
1354:                 elif token_type == '=' and current_var_type is not None:
1355:                     # AUTO: Sets `expecting_value_for_type`.
1356:                     expecting_value_for_type = current_var_type
1357:                 
1358:                 # AUTO: Checks the next alternate condition.
1359:                 elif expecting_value_for_type is not None and token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'sunshine', 'frost', 'id'}:
1360:                     # AUTO: Sets `type_value_map`.
1361:                     type_value_map = {
1362:                         # AUTO: Executes this statement.
1363:                         'seed': {'intlit', 'dblit'},
1364:                         # AUTO: Executes this statement.
1365:                         'tree': {'dblit', 'intlit'},
```
Consumes matching terminal token.

### Parse And Build
Lines 2224-2256
```python
2224:     def parse_and_build(self, tokens: Sequence[Any]):
2225:         # GUIDE: Public parser API used by server.py; syntax first, AST next.
2226:         # LINE: Run LL(1) syntax validation before building AST.
2227:         syntax_ok, syntax_errors = self.parse(tokens)
2228:         # LINE: If syntax failed, return errors and do not call builder.py.
2229:         if not syntax_ok:
2230:             # AUTO: Sets `first_err`.
2231:             first_err = syntax_errors[0] if syntax_errors else ""
2232:             # LINE: Some parser checks intentionally return semantic-style messages.
2233:             stage = "semantic" if first_err.startswith("SEMANTIC error") else "syntax"
2234:             # AUTO: Returns this result to the caller.
2235:             return {
2236:                 # AUTO: Executes this statement.
2237:                 "success": False,
2238:                 # AUTO: Executes this statement.
2239:                 "errors": syntax_errors,
2240:                 # AUTO: Executes this statement.
2241:                 "ast": None,
2242:                 # AUTO: Executes this statement.
2243:                 "symbol_table": {},
2244:                 # AUTO: Executes this statement.
2245:                 "error_stage": stage,
2246:             # AUTO: Closes the current grouped code/data.
2247:             }
2248: 
2249:         # AUTO: Starts protected code that can catch errors.
2250:         try:
2251:             # LINE: Remove comments/newlines because builder only needs meaningful tokens.
2252:             filtered = [t for t in tokens if getattr(t, 'type', '') not in ('\n', 'comment', 'mcommentlit')]
2253:             # LINE: Convert the token stream into AST nodes.
2254:             ast = _build_ast(filtered)
2255: 
2256:             # LINE: Build frontend-friendly symbol table data from builder state.
```
Syntax first, AST second.

## 6. Sample Program
```gal
pollinate seed timesThree(seed n) {
    reclaim n * 3;
}
    
root() {
    seed value = 0;
    seed i;
    cultivate  (i = 1; i <= 4; i++) {
        value = timesThree(i);
        spring (value % 2 == 0) {
            plant("Even product:",value);
        } wither {
            plant("Odd  product:",value);
        }
    }

    reclaim;
}
```

Parser result: `parse() -> True, errors=[]`
Builder result: `parse_and_build() -> success=True, errors=[]`

## 7. Token Table
| # | Line | Col | Type | Value |
|---:|---:|---:|---|---|
| 1 | 1 | 0 | `pollinate` | `pollinate` |
| 2 | 1 | 10 | `seed` | `seed` |
| 3 | 1 | 15 | `id` | `timesThree` |
| 4 | 1 | 25 | `(` | `(` |
| 5 | 1 | 26 | `seed` | `seed` |
| 6 | 1 | 31 | `id` | `n` |
| 7 | 1 | 32 | `)` | `)` |
| 8 | 1 | 34 | `{` | `{` |
| 9 | 1 | 35 | `<br>` | `\n` |
| 10 | 2 | 4 | `reclaim` | `reclaim` |
| 11 | 2 | 12 | `id` | `n` |
| 12 | 2 | 14 | `*` | `*` |
| 13 | 2 | 16 | `intlit` | `3` |
| 14 | 2 | 17 | `;` | `;` |
| 15 | 2 | 18 | `<br>` | `\n` |
| 16 | 3 | 0 | `}` | `}` |
| 17 | 3 | 1 | `<br>` | `\n` |
| 18 | 5 | 0 | `root` | `root` |
| 19 | 5 | 4 | `(` | `(` |
| 20 | 5 | 5 | `)` | `)` |
| 21 | 5 | 7 | `{` | `{` |
| 22 | 5 | 8 | `<br>` | `\n` |
| 23 | 6 | 4 | `seed` | `seed` |
| 24 | 6 | 9 | `id` | `value` |
| 25 | 6 | 15 | `=` | `=` |
| 26 | 6 | 17 | `intlit` | `0` |
| 27 | 6 | 18 | `;` | `;` |
| 28 | 6 | 19 | `<br>` | `\n` |
| 29 | 7 | 4 | `seed` | `seed` |
| 30 | 7 | 9 | `id` | `i` |
| 31 | 7 | 10 | `;` | `;` |
| 32 | 7 | 11 | `<br>` | `\n` |
| 33 | 8 | 4 | `cultivate` | `cultivate` |
| 34 | 8 | 15 | `(` | `(` |
| 35 | 8 | 16 | `id` | `i` |
| 36 | 8 | 18 | `=` | `=` |
| 37 | 8 | 20 | `intlit` | `1` |
| 38 | 8 | 21 | `;` | `;` |
| 39 | 8 | 23 | `id` | `i` |
| 40 | 8 | 25 | `<=` | `<=` |
| 41 | 8 | 28 | `intlit` | `4` |
| 42 | 8 | 29 | `;` | `;` |
| 43 | 8 | 31 | `id` | `i` |
| 44 | 8 | 32 | `++` | `++` |
| 45 | 8 | 34 | `)` | `)` |
| 46 | 8 | 36 | `{` | `{` |
| 47 | 8 | 37 | `<br>` | `\n` |
| 48 | 9 | 8 | `id` | `value` |
| 49 | 9 | 14 | `=` | `=` |
| 50 | 9 | 16 | `id` | `timesThree` |
| 51 | 9 | 26 | `(` | `(` |
| 52 | 9 | 27 | `id` | `i` |
| 53 | 9 | 28 | `)` | `)` |
| 54 | 9 | 29 | `;` | `;` |
| 55 | 9 | 30 | `<br>` | `\n` |
| 56 | 10 | 8 | `spring` | `spring` |
| 57 | 10 | 15 | `(` | `(` |
| 58 | 10 | 16 | `id` | `value` |
| 59 | 10 | 22 | `%` | `%` |
| 60 | 10 | 24 | `intlit` | `2` |
| 61 | 10 | 26 | `==` | `==` |
| 62 | 10 | 29 | `intlit` | `0` |
| 63 | 10 | 30 | `)` | `)` |
| 64 | 10 | 32 | `{` | `{` |
| 65 | 10 | 33 | `<br>` | `\n` |
| 66 | 11 | 12 | `plant` | `plant` |
| 67 | 11 | 17 | `(` | `(` |
| 68 | 11 | 18 | `stringlit` | `"Even product:"` |
| 69 | 11 | 33 | `,` | `,` |
| 70 | 11 | 34 | `id` | `value` |
| 71 | 11 | 39 | `)` | `)` |
| 72 | 11 | 40 | `;` | `;` |
| 73 | 11 | 41 | `<br>` | `\n` |
| 74 | 12 | 8 | `}` | `}` |
| 75 | 12 | 10 | `wither` | `wither` |
| 76 | 12 | 17 | `{` | `{` |
| 77 | 12 | 18 | `<br>` | `\n` |
| 78 | 13 | 12 | `plant` | `plant` |
| 79 | 13 | 17 | `(` | `(` |
| 80 | 13 | 18 | `stringlit` | `"Odd  product:"` |
| 81 | 13 | 33 | `,` | `,` |
| 82 | 13 | 34 | `id` | `value` |
| 83 | 13 | 39 | `)` | `)` |
| 84 | 13 | 40 | `;` | `;` |
| 85 | 13 | 41 | `<br>` | `\n` |
| 86 | 14 | 8 | `}` | `}` |
| 87 | 14 | 9 | `<br>` | `\n` |
| 88 | 15 | 4 | `}` | `}` |
| 89 | 15 | 5 | `<br>` | `\n` |
| 90 | 17 | 4 | `reclaim` | `reclaim` |
| 91 | 17 | 11 | `;` | `;` |
| 92 | 17 | 12 | `<br>` | `\n` |
| 93 | 18 | 0 | `}` | `}` |
| 94 | 18 | 0 | `EOF` | `` |

## 8. Parser Simulation
| Step | Location | Explanation |
|---:|---|---|
| 1 | Line 2224: parse_and_build(tokens) | Parser public entry. It receives lexer tokens. |
| 2 | Line 2227: self.parse(tokens) | Runs LL(1) syntax check first. |
| 3 | Line 1141: parse(self, tokens) | The syntax algorithm starts. |
| 4 | Line 1146: _as_tok conversion | Every lexer Token becomes _TokView(type,value,line,col). |
| 5 | Line 1154: ensure EOF | EOF is appended if needed. |
| 6 | Line 1162: stack = [EOF, <program>] | <program> is the first grammar rule to expand. |
| 7 | Line 1192: while stack | Parser repeats until stack is empty or error occurs. |
| 8 | Lookahead pollinate | <program> predicts function_definition before root. |
| 9 | Line 1214: non-terminal branch | For <program>, <function_definition>, etc., use parse table. |
| 10 | Line 1222: production selected | Lookahead chooses one grammar production. |
| 11 | Line 1311: push RHS reversed | Leftmost RHS symbol is checked next. |
| 12 | Line 1343: terminal match | pollinate/seed/id/( etc. are consumed when matched. |
| 13 | Function parsed | pollinate seed timesThree(seed n) { reclaim n * 3; } is valid. |
| 14 | root parsed | root() opens, then local declarations are checked first. |
| 15 | cultivate parsed | Checks init i=1, condition i<=4, update i++, and loop block. |
| 16 | assignment parsed | value = timesThree(i); uses id assignment and function call expression. |
| 17 | spring/wither parsed | Checks condition value % 2 == 0 and both plant blocks. |
| 18 | reclaim parsed | root must end with reclaim ; then }. |
| 19 | Line 2254: _build_ast(filtered) | After syntax success, builder.py builds AST. |

## 9. Stack and Lookahead Meaning
The stack top is what the grammar expects. The lookahead is the current token from the lexer. If stack top is a non-terminal, the parser uses the parse table. If stack top is a terminal, it must match the lookahead token type.

## 10. Full Line-by-Line Explanation
| Line | Code | Explanation |
|---:|---|---|
| 1 | `"""LL(1) syntax checker for GAL.` | Parser module documentation string. |
| 2 | `` | Blank spacing line. |
| 3 | `The parser receives lexer tokens, consults the CFG/PREDICT table, and only` | Parser support logic used during syntax checking. |
| 4 | `calls builder.py to create the AST after the token stream is syntactically valid.` | Parser support logic used during syntax checking. |
| 5 | `"""` | Parser module documentation string. |
| 6 | `` | Blank spacing line. |
| 7 | `# AUTO: Imports names from another module.` | Comment/guideline in the current parser file. |
| 8 | `from __future__ import annotations` | Import needed parser dependency. |
| 9 | `` | Blank spacing line. |
| 10 | `# AUTO: Imports names from another module.` | Comment/guideline in the current parser file. |
| 11 | `from dataclasses import dataclass` | Import needed parser dependency. |
| 12 | `# AUTO: Imports names from another module.` | Comment/guideline in the current parser file. |
| 13 | `from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple` | Import needed parser dependency. |
| 14 | `` | Blank spacing line. |
| 15 | `# AUTO: Imports names from another module.` | Comment/guideline in the current parser file. |
| 16 | `from .builder import (` | Import needed parser dependency. |
| 17 | `    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 18 | `    build_ast as _build_ast,` | Parser support logic used during syntax checking. |
| 19 | `    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 20 | `    symbol_table as _builder_st,` | Parser support logic used during syntax checking. |
| 21 | `# AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 22 | `)` | Closes Python grouping/list/dict/call. |
| 23 | `# AUTO: Imports names from another module.` | Comment/guideline in the current parser file. |
| 24 | `from semantic.errors import SemanticError as _SemanticError` | Import needed parser dependency. |
| 25 | `` | Blank spacing line. |
| 26 | `` | Blank spacing line. |
| 27 | `# AUTO: Attaches this decorator to the next function/class.` | Comment/guideline in the current parser file. |
| 28 | `@dataclass(frozen=True)` | Decorator that auto-builds small class methods. |
| 29 | `# AUTO: Defines class `_TokView`.` | Comment/guideline in the current parser file. |
| 30 | `class _TokView:` | Defines simple token record used by parser. |
| 31 | `    # GUIDE: Lightweight token shape used internally so parser input can be Token` | Comment/guideline in the current parser file. |
| 32 | `    # objects or dictionaries from API tests.` | Comment/guideline in the current parser file. |
| 33 | `    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 34 | `    type: str` | Parser support logic used during syntax checking. |
| 35 | `    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 36 | `    value: str` | Parser support logic used during syntax checking. |
| 37 | `    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 38 | `    line: int` | Parser support logic used during syntax checking. |
| 39 | `    # AUTO: Sets `col: int`.` | Comment/guideline in the current parser file. |
| 40 | `    col: int = 0` | Stores/updates parser state or response data. |
| 41 | `` | Blank spacing line. |
| 42 | `` | Blank spacing line. |
| 43 | `# AUTO: Defines function `_as_tok`.` | Comment/guideline in the current parser file. |
| 44 | `def _as_tok(token: Any) -> _TokView:` | Function starts: convert any token shape into _TokView. |
| 45 | `    # LINE: Accept dictionary tokens from API/tests.` | Comment/guideline in the current parser file. |
| 46 | `    if isinstance(token, Mapping):` | Checks parser condition. |
| 47 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 48 | `        return _TokView(` | Returns value/result to caller. |
| 49 | `            # AUTO: Sets `type`.` | Comment/guideline in the current parser file. |
| 50 | `            type=str(token.get("type", "")),` | Stores/updates parser state or response data. |
| 51 | `            # AUTO: Sets `value`.` | Comment/guideline in the current parser file. |
| 52 | `            value=str(token.get("value", "")),` | Stores/updates parser state or response data. |
| 53 | `            # AUTO: Sets `line`.` | Comment/guideline in the current parser file. |
| 54 | `            line=int(token.get("line", 0) or 0),` | Stores/updates parser state or response data. |
| 55 | `            # AUTO: Sets `col`.` | Comment/guideline in the current parser file. |
| 56 | `            col=int(token.get("col", 0) or 0),` | Stores/updates parser state or response data. |
| 57 | `        # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 58 | `        )` | Closes Python grouping/list/dict/call. |
| 59 | `    # LINE: Accept Token objects from the lexer.` | Comment/guideline in the current parser file. |
| 60 | `    return _TokView(` | Returns value/result to caller. |
| 61 | `        # AUTO: Sets `type`.` | Comment/guideline in the current parser file. |
| 62 | `        type=str(getattr(token, "type", "")),` | Stores/updates parser state or response data. |
| 63 | `        # AUTO: Sets `value`.` | Comment/guideline in the current parser file. |
| 64 | `        value=str(getattr(token, "value", "")),` | Stores/updates parser state or response data. |
| 65 | `        # AUTO: Sets `line`.` | Comment/guideline in the current parser file. |
| 66 | `        line=int(getattr(token, "line", 0) or 0),` | Stores/updates parser state or response data. |
| 67 | `        # AUTO: Sets `col`.` | Comment/guideline in the current parser file. |
| 68 | `        col=int(getattr(token, "col", 0) or 0),` | Stores/updates parser state or response data. |
| 69 | `    # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 70 | `    )` | Closes Python grouping/list/dict/call. |
| 71 | `` | Blank spacing line. |
| 72 | `` | Blank spacing line. |
| 73 | `# AUTO: Defines class `LL1Parser`.` | Comment/guideline in the current parser file. |
| 74 | `class LL1Parser:` | Defines the LL(1) parser. |
| 75 | `    # AUTO: Defines function `__init__`.` | Comment/guideline in the current parser file. |
| 76 | `    def __init__(` | Method starts: initialize grammar/parser state. |
| 77 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 78 | `        self,` | Parser support logic used during syntax checking. |
| 79 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 80 | `        cfg: Dict[str, List[List[str]]],` | Parser support logic used during syntax checking. |
| 81 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 82 | `        predict_sets: Dict[Tuple[str, Tuple[str, ...]], Set[str]],` | Parser support logic used during syntax checking. |
| 83 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 84 | `        first_sets: Dict[str, Set[str]],` | Parser support logic used during syntax checking. |
| 85 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 86 | `        *,` | Parser support logic used during syntax checking. |
| 87 | `        # AUTO: Sets `start_symbol: str`.` | Comment/guideline in the current parser file. |
| 88 | `        start_symbol: str = "<program>",` | Stores/updates parser state or response data. |
| 89 | `        # AUTO: Sets `end_marker: str`.` | Comment/guideline in the current parser file. |
| 90 | `        end_marker: str = "EOF",` | Stores/updates parser state or response data. |
| 91 | `        # AUTO: Sets `epsilon_symbols: Iterable[str]`.` | Comment/guideline in the current parser file. |
| 92 | `        epsilon_symbols: Iterable[str] = ("λ", "ε"),` | Stores/updates parser state or response data. |
| 93 | `        # AUTO: Sets `skip_token_types: Optional[Set[str]]`.` | Comment/guideline in the current parser file. |
| 94 | `        skip_token_types: Optional[Set[str]] = None,` | Stores/updates parser state or response data. |
| 95 | `        # AUTO: Sets `token_type_alias: Optional[Dict[str, str]]`.` | Comment/guideline in the current parser file. |
| 96 | `        token_type_alias: Optional[Dict[str, str]] = None,` | Stores/updates parser state or response data. |
| 97 | `    # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 98 | `    ):` | Parser support logic used during syntax checking. |
| 99 | `        # AUTO: Sets `self.cfg`.` | Comment/guideline in the current parser file. |
| 100 | `        self.cfg = cfg` | Stores/updates parser state or response data. |
| 101 | `        # AUTO: Sets `self.predict_sets`.` | Comment/guideline in the current parser file. |
| 102 | `        self.predict_sets = predict_sets` | Stores/updates parser state or response data. |
| 103 | `        # AUTO: Sets `self.first_sets`.` | Comment/guideline in the current parser file. |
| 104 | `        self.first_sets = first_sets` | Stores/updates parser state or response data. |
| 105 | `` | Blank spacing line. |
| 106 | `        # AUTO: Sets `self.epsilon_symbols: Set[str]`.` | Comment/guideline in the current parser file. |
| 107 | `        self.epsilon_symbols: Set[str] = set(epsilon_symbols)` | Stores/updates parser state or response data. |
| 108 | `        # AUTO: Sets `self.start_symbol`.` | Comment/guideline in the current parser file. |
| 109 | `        self.start_symbol = start_symbol` | Stores/updates parser state or response data. |
| 110 | `        # AUTO: Sets `self.end_marker`.` | Comment/guideline in the current parser file. |
| 111 | `        self.end_marker = end_marker` | Stores/updates parser state or response data. |
| 112 | `` | Blank spacing line. |
| 113 | `        # Comments ('comment' = //..., 'mcommentlit' = /*...*/) are emitted by` | Comment/guideline in the current parser file. |
| 114 | `        # the lexer for the lexeme table but are not grammar tokens, so the` | Comment/guideline in the current parser file. |
| 115 | `        # parser skips them just like newlines.` | Comment/guideline in the current parser file. |
| 116 | `        # AUTO: Sets `self.skip_token_types: Set[str]`.` | Comment/guideline in the current parser file. |
| 117 | `        self.skip_token_types: Set[str] = set(skip_token_types or {"\n", "comment", "mcommentlit"})` | Stores/updates parser state or response data. |
| 118 | `        # AUTO: Sets `self.token_type_alias`.` | Comment/guideline in the current parser file. |
| 119 | `        self.token_type_alias = token_type_alias or {` | Stores/updates parser state or response data. |
| 120 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 121 | `            'idf': 'id',` | Parser support logic used during syntax checking. |
| 122 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 123 | `            'dbllit': 'dblit',` | Parser support logic used during syntax checking. |
| 124 | `        # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 125 | `        }` | Closes Python grouping/list/dict/call. |
| 126 | `        ` | Blank spacing line. |
| 127 | `        # AUTO: Sets `self.parsing_table: Dict[str, Dict[str, List[str]]]`.` | Comment/guideline in the current parser file. |
| 128 | `        self.parsing_table: Dict[str, Dict[str, List[str]]] = self.construct_parsing_table()` | Stores/updates parser state or response data. |
| 129 | `` | Blank spacing line. |
| 130 | `    # AUTO: Defines function `construct_parsing_table`.` | Comment/guideline in the current parser file. |
| 131 | `    def construct_parsing_table(self) -> Dict[str, Dict[str, List[str]]]:` | Method starts: build LL(1) table. |
| 132 | `        # GUIDE: Convert PREDICT sets into table[non_terminal][lookahead] = production.` | Comment/guideline in the current parser file. |
| 133 | `        # LINE: table maps each non-terminal and lookahead token to one CFG rule.` | Comment/guideline in the current parser file. |
| 134 | `        table: Dict[str, Dict[str, List[str]]] = {}` | Stores/updates parser state or response data. |
| 135 | `` | Blank spacing line. |
| 136 | `        # LINE: Visit every non-terminal in the grammar.` | Comment/guideline in the current parser file. |
| 137 | `        for non_terminal, productions in self.cfg.items():` | Loops over items. |
| 138 | `            # LINE: row stores all lookahead choices for this non-terminal.` | Comment/guideline in the current parser file. |
| 139 | `            row: Dict[str, List[str]] = {}` | Stores/updates parser state or response data. |
| 140 | `            # LINE: Visit every production under the current non-terminal.` | Comment/guideline in the current parser file. |
| 141 | `            for production in productions:` | Loops over items. |
| 142 | `                # LINE: This key matches how predict_sets stores each production.` | Comment/guideline in the current parser file. |
| 143 | `                key = (non_terminal, tuple(production))` | Stores/updates parser state or response data. |
| 144 | `                # LINE: terms are the lookahead terminals that choose this production.` | Comment/guideline in the current parser file. |
| 145 | `                terms = self.predict_sets.get(key, set())` | Stores/updates parser state or response data. |
| 146 | `                # LINE: Fill the parse table for each lookahead terminal.` | Comment/guideline in the current parser file. |
| 147 | `                for terminal in terms:` | Loops over items. |
| 148 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 149 | `                    if terminal in row and row[terminal] != production:` | Checks parser condition. |
| 150 | `                        # LINE: A conflict means the grammar is not LL(1) here.` | Comment/guideline in the current parser file. |
| 151 | `                        raise ValueError(` | Parser support logic used during syntax checking. |
| 152 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 153 | `                            f"LL(1) conflict at {non_terminal} with lookahead {terminal}: "` | Parser support logic used during syntax checking. |
| 154 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 155 | `                            f"{row[terminal]} vs {production}"` | Parser support logic used during syntax checking. |
| 156 | `                        # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 157 | `                        )` | Closes Python grouping/list/dict/call. |
| 158 | `                    # AUTO: Sets `row[terminal]`.` | Comment/guideline in the current parser file. |
| 159 | `                    row[terminal] = production` | Stores/updates parser state or response data. |
| 160 | `            # LINE: Save this non-terminal row in the final parsing table.` | Comment/guideline in the current parser file. |
| 161 | `            table[non_terminal] = row` | Stores/updates parser state or response data. |
| 162 | `        # LINE: Return the completed LL(1) parse table.` | Comment/guideline in the current parser file. |
| 163 | `        return table` | Returns value/result to caller. |
| 164 | `` | Blank spacing line. |
| 165 | `` | Blank spacing line. |
| 166 | `    # AUTO: Defines function `_normalize_token_type`.` | Comment/guideline in the current parser file. |
| 167 | `    def _normalize_token_type(self, token_type: str) -> str:` | Method starts: normalize lexer token names. |
| 168 | `        # LINE: Convert lexer aliases like idf/dbllit into grammar names.` | Comment/guideline in the current parser file. |
| 169 | `        return self.token_type_alias.get(token_type, token_type)` | Returns value/result to caller. |
| 170 | `` | Blank spacing line. |
| 171 | `    # AUTO: Defines function `_ensure_eof`.` | Comment/guideline in the current parser file. |
| 172 | `    def _ensure_eof(self, toks: List[_TokView]) -> List[_TokView]:` | Method starts: ensure EOF token exists. |
| 173 | `        # LINE: Empty input still needs EOF so parser can stop cleanly.` | Comment/guideline in the current parser file. |
| 174 | `        if not toks:` | Checks parser condition. |
| 175 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 176 | `            return [_TokView(self.end_marker, self.end_marker, 1, 0)]` | Returns value/result to caller. |
| 177 | `        # LINE: Add EOF if lexer/caller did not already include it.` | Comment/guideline in the current parser file. |
| 178 | `        if toks[-1].type != self.end_marker:` | Checks parser condition. |
| 179 | `            # AUTO: Sets `last_line`.` | Comment/guideline in the current parser file. |
| 180 | `            last_line = toks[-1].line or 1` | Stores/updates parser state or response data. |
| 181 | `            # AUTO: Sets `last_col`.` | Comment/guideline in the current parser file. |
| 182 | `            last_col = toks[-1].col or 0` | Stores/updates parser state or response data. |
| 183 | `            # AUTO: Sets `toks`.` | Comment/guideline in the current parser file. |
| 184 | `            toks = toks + [_TokView(self.end_marker, self.end_marker, last_line, last_col)]` | Stores/updates parser state or response data. |
| 185 | `        # LINE: Return token stream guaranteed to end with EOF.` | Comment/guideline in the current parser file. |
| 186 | `        return toks` | Returns value/result to caller. |
| 187 | `` | Blank spacing line. |
| 188 | `    # AUTO: Sets `_TERMINAL_DISPLAY: Dict[str, str]`.` | Comment/guideline in the current parser file. |
| 189 | `    _TERMINAL_DISPLAY: Dict[str, str] = {` | Stores/updates parser state or response data. |
| 190 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 191 | `        'id': 'id', 'intlit': 'intlit', 'dblit': 'dblit',` | Parser support logic used during syntax checking. |
| 192 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 193 | `        'stringlit': 'stringlit', 'chrlit': 'chrlit',` | Parser support logic used during syntax checking. |
| 194 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 195 | `        'sunshine': "'sunshine'", 'frost': "'frost'",` | Parser support logic used during syntax checking. |
| 196 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 197 | `        'seed': "'seed'", 'tree': "'tree'",` | Parser support logic used during syntax checking. |
| 198 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 199 | `        'leaf': "'leaf'", 'branch': "'branch'",` | Parser support logic used during syntax checking. |
| 200 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 201 | `        'vine': "'vine'",` | Parser support logic used during syntax checking. |
| 202 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 203 | `        'bundle': "'bundle'", 'fertile': "'fertile'",` | Parser support logic used during syntax checking. |
| 204 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 205 | `        'pollinate': "'pollinate'", 'root': "'root'",` | Parser support logic used during syntax checking. |
| 206 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 207 | `        'reclaim': "'reclaim'", 'spring': "'spring'",` | Parser support logic used during syntax checking. |
| 208 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 209 | `        'bud': "'bud'", 'wither': "'wither'",` | Parser support logic used during syntax checking. |
| 210 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 211 | `        'grow': "'grow'", 'cultivate': "'cultivate'",` | Parser support logic used during syntax checking. |
| 212 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 213 | `        'tend': "'tend'", 'harvest': "'harvest'",` | Parser support logic used during syntax checking. |
| 214 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 215 | `        'variety': "'variety'", 'soil': "'soil'",` | Parser support logic used during syntax checking. |
| 216 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 217 | `        'prune': "'prune'", 'skip': "'skip'",` | Parser support logic used during syntax checking. |
| 218 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 219 | `        'water': "'water'", 'plant': "'plant'",` | Parser support logic used during syntax checking. |
| 220 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 221 | `        'empty': "'empty'",` | Parser support logic used during syntax checking. |
| 222 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 223 | `        'EOF': 'end of file',` | Parser support logic used during syntax checking. |
| 224 | `    # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 225 | `    }` | Closes Python grouping/list/dict/call. |
| 226 | `` | Blank spacing line. |
| 227 | `    # AUTO: Defines function `_format_expected`.` | Comment/guideline in the current parser file. |
| 228 | `    def _format_expected(self, expected: Set[str], non_terminal: Optional[str] = None) -> str:` | Method starts: format expected-token message. |
| 229 | `        # AUTO: Sets `symbols`.` | Comment/guideline in the current parser file. |
| 230 | `        symbols = {'(', ')', '{', '}', ';', ',', '=', '+', '-', '*', '/', '%',` | Stores/updates parser state or response data. |
| 231 | `                   # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 232 | `                   '++', '--', '==', '!=', '<', '>', '<=', '>=', '&&', '\|\|',` | Stores/updates parser state or response data. |
| 233 | `                   # AUTO: Adds into `'!', '~', '`.` | Comment/guideline in the current parser file. |
| 234 | `                   '!', '~', '+=', '-=', '*=', '/=', '%=', '.', '[', ']', ':', '`'}` | Stores/updates parser state or response data. |
| 235 | `        # AUTO: Calls `any`.` | Comment/guideline in the current parser file. |
| 236 | `        has_reclaim = any(tk.type == 'reclaim' for tk in getattr(self, '_current_tokens', []))` | Stores/updates parser state or response data. |
| 237 | `` | Blank spacing line. |
| 238 | `        # AUTO: Sets `parts: List[str]`.` | Comment/guideline in the current parser file. |
| 239 | `        parts: List[str] = []` | Stores/updates parser state or response data. |
| 240 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current parser file. |
| 241 | `        for t in sorted(expected):` | Loops over items. |
| 242 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 243 | `            if t == 'reclaim' and has_reclaim:` | Checks parser condition. |
| 244 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 245 | `                continue` | Moves to next loop iteration. |
| 246 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 247 | `            if t in self._TERMINAL_DISPLAY:` | Checks parser condition. |
| 248 | `                # AUTO: Appends a value to a list.` | Comment/guideline in the current parser file. |
| 249 | `                parts.append(self._TERMINAL_DISPLAY[t])` | Parser support logic used during syntax checking. |
| 250 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 251 | `            elif t in symbols:` | Alternative condition. |
| 252 | `                # AUTO: Appends a value to a list.` | Comment/guideline in the current parser file. |
| 253 | `                parts.append(f"'{t}'")` | Parser support logic used during syntax checking. |
| 254 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 255 | `            elif t.startswith('<') and t.endswith('>'):` | Alternative condition. |
| 256 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 257 | `                continue` | Moves to next loop iteration. |
| 258 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 259 | `            else:` | Fallback branch. |
| 260 | `                # AUTO: Appends a value to a list.` | Comment/guideline in the current parser file. |
| 261 | `                parts.append(f"'{t}'")` | Parser support logic used during syntax checking. |
| 262 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 263 | `        if not parts:` | Checks parser condition. |
| 264 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 265 | `            return 'nothing'` | Returns value/result to caller. |
| 266 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 267 | `        return f"Expected: {', '.join(parts)}"` | Returns value/result to caller. |
| 268 | `` | Blank spacing line. |
| 269 | `    # AUTO: Defines function `_generate_helpful_error`.` | Comment/guideline in the current parser file. |
| 270 | `    def _generate_helpful_error(` | Method starts: build detailed syntax error. |
| 271 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 272 | `        self,` | Parser support logic used during syntax checking. |
| 273 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 274 | `        non_terminal: str,` | Parser support logic used during syntax checking. |
| 275 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 276 | `        token_type: str,` | Parser support logic used during syntax checking. |
| 277 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 278 | `        token_value: str,` | Parser support logic used during syntax checking. |
| 279 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 280 | `        line: int,` | Parser support logic used during syntax checking. |
| 281 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 282 | `        col: int,` | Parser support logic used during syntax checking. |
| 283 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 284 | `        expected: Set[str],` | Parser support logic used during syntax checking. |
| 285 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 286 | `        index: int,` | Parser support logic used during syntax checking. |
| 287 | `        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 288 | `        toks: List[_TokView]` | Parser support logic used during syntax checking. |
| 289 | `    # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 290 | `    ) -> str:` | Parser support logic used during syntax checking. |
| 291 | `        ` | Blank spacing line. |
| 292 | `        # AUTO: Sets `param_type_tokens`.` | Comment/guideline in the current parser file. |
| 293 | `        param_type_tokens = {'seed', 'tree', 'leaf', 'vine', 'branch'}` | Stores/updates parser state or response data. |
| 294 | `        ` | Blank spacing line. |
| 295 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 296 | `        if token_type == self.end_marker or token_value == '':` | Checks parser condition. |
| 297 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 298 | `            if '}' in expected:` | Checks parser condition. |
| 299 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 300 | `                return f"SYNTAX error line {line} col {col} Unexpected end of file. Missing closing '}}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 301 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 302 | `            return f"SYNTAX error line {line} col {col} Unexpected end of file. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 303 | `        ` | Blank spacing line. |
| 304 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 305 | `        if token_type == '=' and index > 0:` | Checks parser condition. |
| 306 | `            # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 307 | `            prev_index = index - 1` | Stores/updates parser state or response data. |
| 308 | `            # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 309 | `            while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 310 | `                # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 311 | `                prev_index -= 1` | Stores/updates parser state or response data. |
| 312 | `            ` | Blank spacing line. |
| 313 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 314 | `            if prev_index >= 0 and toks[prev_index].type == '==':` | Checks parser condition. |
| 315 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 316 | `                return f"SYNTAX error line {line} col {col} Invalid operator '==='. Use '==' for equality comparison. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 317 | `        ` | Blank spacing line. |
| 318 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 319 | `        if token_type == '&' and index > 0:` | Checks parser condition. |
| 320 | `            # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 321 | `            prev_index = index - 1` | Stores/updates parser state or response data. |
| 322 | `            # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 323 | `            while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 324 | `                # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 325 | `                prev_index -= 1` | Stores/updates parser state or response data. |
| 326 | `            ` | Blank spacing line. |
| 327 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 328 | `            if prev_index >= 0 and toks[prev_index].type == '&&':` | Checks parser condition. |
| 329 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 330 | `                return f"SYNTAX error line {line} col {col} Invalid operator '&&&'. Use '&&' for logical AND. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 331 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 332 | `            return f"SYNTAX error line {line} col {col} Invalid operator '&'. Use '&&' for logical AND. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 333 | `        ` | Blank spacing line. |
| 334 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 335 | `        if token_type == '\|' and index > 0:` | Checks parser condition. |
| 336 | `            # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 337 | `            prev_index = index - 1` | Stores/updates parser state or response data. |
| 338 | `            # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 339 | `            while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 340 | `                # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 341 | `                prev_index -= 1` | Stores/updates parser state or response data. |
| 342 | `            ` | Blank spacing line. |
| 343 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 344 | `            if prev_index >= 0 and toks[prev_index].type == '\|\|':` | Checks parser condition. |
| 345 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 346 | `                return f"SYNTAX error line {line} col {col} Invalid operator '\|\|\|'. Use '\|\|' for logical OR. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 347 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 348 | `            return f"SYNTAX error line {line} col {col} Invalid operator '\|'. Use '\|\|' for logical OR. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 349 | `        ` | Blank spacing line. |
| 350 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 351 | `        if token_type == 'chrlit' and token_value and not token_value.endswith("'"):` | Checks parser condition. |
| 352 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 353 | `            return f"SYNTAX error line {line} col {col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 354 | `        ` | Blank spacing line. |
| 355 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 356 | `        if token_type == 'stringlit' and token_value and not token_value.endswith('"'):` | Checks parser condition. |
| 357 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 358 | `            return f"SYNTAX error line {line} col {col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 359 | `        ` | Blank spacing line. |
| 360 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 361 | `        if non_terminal == '<reclaim_value>' and token_type == '}':` | Checks parser condition. |
| 362 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 363 | `            return f"SYNTAX error line {line} col {col} Missing ';' after 'reclaim'. Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 364 | `        ` | Blank spacing line. |
| 365 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 366 | `        if token_type == ')' and ')' not in expected:` | Checks parser condition. |
| 367 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 368 | `            if index > 0:` | Checks parser condition. |
| 369 | `                # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 370 | `                prev_index = index - 1` | Stores/updates parser state or response data. |
| 371 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 372 | `                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 373 | `                    # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 374 | `                    prev_index -= 1` | Stores/updates parser state or response data. |
| 375 | `                ` | Blank spacing line. |
| 376 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 377 | `                if prev_index >= 0:` | Checks parser condition. |
| 378 | `                    # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 379 | `                    prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 380 | `                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 381 | `                    binary_operators = {'+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '\|\|'}` | Stores/updates parser state or response data. |
| 382 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 383 | `                    if prev_tok.type in binary_operators:` | Checks parser condition. |
| 384 | `                        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 385 | `                        return f"SYNTAX error line {line} col {col} Unexpected token ')' after binary operator '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 386 | `                    ` | Blank spacing line. |
| 387 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 388 | `                    if prev_tok.type == ',' and param_type_tokens & expected:` | Checks parser condition. |
| 389 | `                        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 390 | `                        return f"SYNTAX error line {line} col {col} Unexpected token ')'. Expected parameter type (seed, tree, leaf, vine, branch) after ','"` | Returns value/result to caller. |
| 391 | `                    ` | Blank spacing line. |
| 392 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 393 | `                    if prev_tok.type == '(':` | Checks parser condition. |
| 394 | `                        # AUTO: Sets `kw_index`.` | Comment/guideline in the current parser file. |
| 395 | `                        kw_index = prev_index - 1` | Stores/updates parser state or response data. |
| 396 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 397 | `                        while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 398 | `                            # AUTO: Subtracts from `kw_index`.` | Comment/guideline in the current parser file. |
| 399 | `                            kw_index -= 1` | Stores/updates parser state or response data. |
| 400 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 401 | `                        if kw_index >= 0:` | Checks parser condition. |
| 402 | `                            # AUTO: Sets `keyword_descriptions`.` | Comment/guideline in the current parser file. |
| 403 | `                            keyword_descriptions = {` | Stores/updates parser state or response data. |
| 404 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 405 | `                                'grow': 'while-loop', 'spring': 'if-statement', 'cultivate': 'for-loop',` | Parser support logic used during syntax checking. |
| 406 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 407 | `                                'tend': 'do-while-loop', 'harvest': 'switch-statement', 'bud': 'else-if',` | Parser support logic used during syntax checking. |
| 408 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 409 | `                                'plant': 'output function', 'water': 'input function',` | Parser support logic used during syntax checking. |
| 410 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 411 | `                                'seed': 'integer type', 'tree': 'float type', 'leaf': 'character type',` | Parser support logic used during syntax checking. |
| 412 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 413 | `                                'vine': 'string type', 'branch': 'boolean type',` | Parser support logic used during syntax checking. |
| 414 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 415 | `                                'reclaim': 'return statement', 'prune': 'break statement',` | Parser support logic used during syntax checking. |
| 416 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 417 | `                                'skip': 'continue statement', 'pollinate': 'function declaration',` | Parser support logic used during syntax checking. |
| 418 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 419 | `                                'root': 'main function', 'wither': 'else-statement',` | Parser support logic used during syntax checking. |
| 420 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 421 | `                                'fertile': 'constant declaration', 'bundle': 'struct definition',` | Parser support logic used during syntax checking. |
| 422 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 423 | `                                'variety': 'case label', 'soil': 'default case',` | Parser support logic used during syntax checking. |
| 424 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 425 | `                                'empty': 'void type',` | Parser support logic used during syntax checking. |
| 426 | `                            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 427 | `                            }` | Closes Python grouping/list/dict/call. |
| 428 | `                            # AUTO: Sets `kw_tok`.` | Comment/guideline in the current parser file. |
| 429 | `                            kw_tok = toks[kw_index]` | Stores/updates parser state or response data. |
| 430 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 431 | `                            if kw_tok.type in keyword_descriptions:` | Checks parser condition. |
| 432 | `                                # AUTO: Sets `desc`.` | Comment/guideline in the current parser file. |
| 433 | `                                desc = keyword_descriptions[kw_tok.type]` | Stores/updates parser state or response data. |
| 434 | `                                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 435 | `                                return f"SYNTAX error line {kw_tok.line} col {kw_tok.col} '{kw_tok.value}' is a reserved keyword ({desc}) and cannot be used as a function name."` | Returns value/result to caller. |
| 436 | `            ` | Blank spacing line. |
| 437 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 438 | `            return f"SYNTAX error line {line} col {col} Unexpected token ')' - no matching '(' found in expression. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 439 | `        ` | Blank spacing line. |
| 440 | `        # AUTO: Adds into `assignment_operators = {'`.` | Comment/guideline in the current parser file. |
| 441 | `        assignment_operators = {'+=', '-=', '*=', '/=', '%='}` | Stores/updates parser state or response data. |
| 442 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 443 | `        if token_type in assignment_operators:` | Checks parser condition. |
| 444 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 445 | `            return f"SYNTAX error line {line} col {col} Assignment operator '{token_value}' must follow a modifiable assignment target. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 446 | `        ` | Blank spacing line. |
| 447 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 448 | `        if token_type == '=':` | Checks parser condition. |
| 449 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 450 | `            if index > 0:` | Checks parser condition. |
| 451 | `                # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 452 | `                prev_index = index - 1` | Stores/updates parser state or response data. |
| 453 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 454 | `                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 455 | `                    # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 456 | `                    prev_index -= 1` | Stores/updates parser state or response data. |
| 457 | `                ` | Blank spacing line. |
| 458 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 459 | `                if prev_index >= 0:` | Checks parser condition. |
| 460 | `                    # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 461 | `                    prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 462 | `                    # AUTO: Sets `compound_op_bases`.` | Comment/guideline in the current parser file. |
| 463 | `                    compound_op_bases = {'+', '-', '*', '/', '%'}` | Stores/updates parser state or response data. |
| 464 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 465 | `                    if prev_tok.type in compound_op_bases:` | Checks parser condition. |
| 466 | `                        # AUTO: Sets `prev_prev_index`.` | Comment/guideline in the current parser file. |
| 467 | `                        prev_prev_index = prev_index - 1` | Stores/updates parser state or response data. |
| 468 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 469 | `                        while prev_prev_index >= 0 and toks[prev_prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 470 | `                            # AUTO: Subtracts from `prev_prev_index`.` | Comment/guideline in the current parser file. |
| 471 | `                            prev_prev_index -= 1` | Stores/updates parser state or response data. |
| 472 | `                        ` | Blank spacing line. |
| 473 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 474 | `                        if prev_prev_index >= 0 and toks[prev_prev_index].type == 'id':` | Checks parser condition. |
| 475 | `                            # AUTO: Sets `id_tok`.` | Comment/guideline in the current parser file. |
| 476 | `                            id_tok = toks[prev_prev_index]` | Stores/updates parser state or response data. |
| 477 | `                            # AUTO: Sets `compound_op`.` | Comment/guideline in the current parser file. |
| 478 | `                            compound_op = f"{prev_tok.value}="` | Stores/updates parser state or response data. |
| 479 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 480 | `                            return f"SYNTAX error line {line} col {col} Unexpected token '=' after operator '{prev_tok.value}'. Did you mean '{id_tok.value} {compound_op}' (compound assignment with no space)? {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 481 | `        ` | Blank spacing line. |
| 482 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 483 | `        if token_type == '{' and non_terminal in {'<program>', '<global_declaration>'}:` | Checks parser condition. |
| 484 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 485 | `            if index == 0 or (index <= 2 and all(toks[i].type in self.skip_token_types for i in range(index))):` | Checks parser condition. |
| 486 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 487 | `                return f"SYNTAX error line {line} col {col} 'root' function declaration is missing opening '('. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 488 | `        ` | Blank spacing line. |
| 489 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 490 | `        if index + 1 < len(toks):` | Checks parser condition. |
| 491 | `            # AUTO: Sets `next_tok`.` | Comment/guideline in the current parser file. |
| 492 | `            next_tok = toks[index + 1]` | Stores/updates parser state or response data. |
| 493 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 494 | `            if next_tok.type == 'chrlit' and next_tok.value and not next_tok.value.endswith("'"):` | Checks parser condition. |
| 495 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 496 | `                return f"SYNTAX error line {next_tok.line} col {next_tok.col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 497 | `            ` | Blank spacing line. |
| 498 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 499 | `            if next_tok.type == 'stringlit' and next_tok.value and not next_tok.value.endswith('"'):` | Checks parser condition. |
| 500 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 501 | `                return f"SYNTAX error line {next_tok.line} col {next_tok.col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 502 | `        ` | Blank spacing line. |
| 503 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 504 | `        if token_type == ';' and non_terminal == '<global_declaration>':` | Checks parser condition. |
| 505 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 506 | `            if index > 0:` | Checks parser condition. |
| 507 | `                # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 508 | `                prev_index = index - 1` | Stores/updates parser state or response data. |
| 509 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 510 | `                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 511 | `                    # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 512 | `                    prev_index -= 1` | Stores/updates parser state or response data. |
| 513 | `                ` | Blank spacing line. |
| 514 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 515 | `                if prev_index >= 0 and toks[prev_index].type == '}':` | Checks parser condition. |
| 516 | `                    # AUTO: Sets `bundle_index`.` | Comment/guideline in the current parser file. |
| 517 | `                    bundle_index = prev_index - 1` | Stores/updates parser state or response data. |
| 518 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 519 | `                    while bundle_index >= 0 and toks[bundle_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 520 | `                        # AUTO: Subtracts from `bundle_index`.` | Comment/guideline in the current parser file. |
| 521 | `                        bundle_index -= 1` | Stores/updates parser state or response data. |
| 522 | `                    ` | Blank spacing line. |
| 523 | `                    # AUTO: Sets `found_bundle`.` | Comment/guideline in the current parser file. |
| 524 | `                    found_bundle = False` | Stores/updates parser state or response data. |
| 525 | `                    # AUTO: Starts a loop over these values.` | Comment/guideline in the current parser file. |
| 526 | `                    for i in range(bundle_index, max(0, bundle_index - 20) - 1, -1):` | Loops over items. |
| 527 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 528 | `                        if toks[i].type == 'bundle':` | Checks parser condition. |
| 529 | `                            # AUTO: Sets `found_bundle`.` | Comment/guideline in the current parser file. |
| 530 | `                            found_bundle = True` | Stores/updates parser state or response data. |
| 531 | `                            # AUTO: Stops the nearest loop.` | Comment/guideline in the current parser file. |
| 532 | `                            break` | Stops nearest loop. |
| 533 | `                    ` | Blank spacing line. |
| 534 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 535 | `                    if found_bundle:` | Checks parser condition. |
| 536 | `                        # AUTO: Sets `expected_str`.` | Comment/guideline in the current parser file. |
| 537 | `                        expected_str = self._format_expected(expected, non_terminal)` | Stores/updates parser state or response data. |
| 538 | `                        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 539 | `                        return f"SYNTAX error line {line} col {col} Unexpected token ';' after bundle definition closing '}}'. ';' is not in {expected_str}. Remove the trailing ';'"` | Returns value/result to caller. |
| 540 | `        ` | Blank spacing line. |
| 541 | `        # AUTO: Sets `common_keyword_mistakes`.` | Comment/guideline in the current parser file. |
| 542 | `        common_keyword_mistakes = {` | Stores/updates parser state or response data. |
| 543 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 544 | `            'function': 'pollinate',` | Parser support logic used during syntax checking. |
| 545 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 546 | `            'int': 'seed',` | Parser support logic used during syntax checking. |
| 547 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 548 | `            'float': 'tree',` | Parser support logic used during syntax checking. |
| 549 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 550 | `            'double': 'tree',` | Parser support logic used during syntax checking. |
| 551 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 552 | `            'char': 'leaf',` | Parser support logic used during syntax checking. |
| 553 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 554 | `            'bool': 'branch',` | Parser support logic used during syntax checking. |
| 555 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 556 | `            'boolean': 'branch',` | Parser support logic used during syntax checking. |
| 557 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 558 | `            'if': 'spring',` | Parser support logic used during syntax checking. |
| 559 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 560 | `            'else': 'wither',` | Parser support logic used during syntax checking. |
| 561 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 562 | `            'elif': 'bud',` | Parser support logic used during syntax checking. |
| 563 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 564 | `            'while': 'grow',` | Parser support logic used during syntax checking. |
| 565 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 566 | `            'for': 'cultivate',` | Parser support logic used during syntax checking. |
| 567 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 568 | `            'switch': 'harvest',` | Parser support logic used during syntax checking. |
| 569 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 570 | `            'case': 'variety',` | Parser support logic used during syntax checking. |
| 571 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 572 | `            'default': 'soil',` | Parser support logic used during syntax checking. |
| 573 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 574 | `            'break': 'prune',` | Parser support logic used during syntax checking. |
| 575 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 576 | `            'continue': 'skip',` | Parser support logic used during syntax checking. |
| 577 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 578 | `            'return': 'reclaim',` | Parser support logic used during syntax checking. |
| 579 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 580 | `            'void': 'empty',` | Parser support logic used during syntax checking. |
| 581 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 582 | `            'const': 'fertile',` | Parser support logic used during syntax checking. |
| 583 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 584 | `            'struct': 'bundle',` | Parser support logic used during syntax checking. |
| 585 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 586 | `            'string': 'vine',` | Parser support logic used during syntax checking. |
| 587 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 588 | `            'printf': 'plant',` | Parser support logic used during syntax checking. |
| 589 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 590 | `            'scanf': 'water',` | Parser support logic used during syntax checking. |
| 591 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 592 | `            'print': 'plant',` | Parser support logic used during syntax checking. |
| 593 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 594 | `            'input': 'water'` | Parser support logic used during syntax checking. |
| 595 | `        # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 596 | `        }` | Closes Python grouping/list/dict/call. |
| 597 | `        ` | Blank spacing line. |
| 598 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 599 | `        if token_type == 'id' and token_value in common_keyword_mistakes:` | Checks parser condition. |
| 600 | `            # AUTO: Sets `correct_keyword`.` | Comment/guideline in the current parser file. |
| 601 | `            correct_keyword = common_keyword_mistakes[token_value]` | Stores/updates parser state or response data. |
| 602 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 603 | `            return f"SYNTAX error line {line} col {col} '{token_value}' is not a GAL keyword. Use '{correct_keyword}' instead."` | Returns value/result to caller. |
| 604 | `        ` | Blank spacing line. |
| 605 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 606 | `        if token_type == '{' and (non_terminal == '<bundle_or_var>' or non_terminal == '<bundle_mem_dec>'):` | Checks parser condition. |
| 607 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 608 | `            return f"SYNTAX error line {line} col {col} Bundle definitions must be at global scope (outside all functions). Move this bundle definition before 'root()'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 609 | `        ` | Blank spacing line. |
| 610 | `        # AUTO: Sets `statement_starters`.` | Comment/guideline in the current parser file. |
| 611 | `        statement_starters = {` | Stores/updates parser state or response data. |
| 612 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 613 | `            'reclaim', 'spring', 'wither', 'bud', 'grow', 'cultivate', 'tend',` | Parser support logic used during syntax checking. |
| 614 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 615 | `            'harvest', 'prune', 'skip', 'water', 'plant', 'seed', 'leaf',` | Parser support logic used during syntax checking. |
| 616 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 617 | `            'branch', 'tree', 'vine', 'bundle', 'fertile', 'pollinate', 'root', 'id'` | Parser support logic used during syntax checking. |
| 618 | `        # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 619 | `        }` | Closes Python grouping/list/dict/call. |
| 620 | `        ` | Blank spacing line. |
| 621 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 622 | `        if ':' in expected and token_type in statement_starters:` | Checks parser condition. |
| 623 | `            # AUTO: Sets `context_keyword`.` | Comment/guideline in the current parser file. |
| 624 | `            context_keyword = None` | Stores/updates parser state or response data. |
| 625 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 626 | `            if index > 0:` | Checks parser condition. |
| 627 | `                # AUTO: Sets `scan`.` | Comment/guideline in the current parser file. |
| 628 | `                scan = index - 1` | Stores/updates parser state or response data. |
| 629 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 630 | `                while scan >= 0:` | Repeats while condition is true. |
| 631 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 632 | `                    if toks[scan].type in self.skip_token_types:` | Checks parser condition. |
| 633 | `                        # AUTO: Subtracts from `scan`.` | Comment/guideline in the current parser file. |
| 634 | `                        scan -= 1` | Stores/updates parser state or response data. |
| 635 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 636 | `                        continue` | Moves to next loop iteration. |
| 637 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 638 | `                    if toks[scan].type == 'variety':` | Checks parser condition. |
| 639 | `                        # AUTO: Sets `context_keyword`.` | Comment/guideline in the current parser file. |
| 640 | `                        context_keyword = 'variety'` | Stores/updates parser state or response data. |
| 641 | `                        # AUTO: Stops the nearest loop.` | Comment/guideline in the current parser file. |
| 642 | `                        break` | Stops nearest loop. |
| 643 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 644 | `                    if toks[scan].type == 'soil':` | Checks parser condition. |
| 645 | `                        # AUTO: Sets `context_keyword`.` | Comment/guideline in the current parser file. |
| 646 | `                        context_keyword = 'soil'` | Stores/updates parser state or response data. |
| 647 | `                        # AUTO: Stops the nearest loop.` | Comment/guideline in the current parser file. |
| 648 | `                        break` | Stops nearest loop. |
| 649 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 650 | `                    if toks[scan].type in {'id', 'intlit', 'dblit', 'stringlit', 'chrlit',` | Checks parser condition. |
| 651 | `                                           # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 652 | `                                           'sunshine', 'frost', '+', '-', '*', '/', '%',` | Parser support logic used during syntax checking. |
| 653 | `                                           # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 654 | `                                           '==', '!=', '<', '>', '<=', '>=', '&&', '\|\|',` | Stores/updates parser state or response data. |
| 655 | `                                           # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 656 | `                                           '(', ')', '`', '~'}:` | Parser support logic used during syntax checking. |
| 657 | `                        # AUTO: Subtracts from `scan`.` | Comment/guideline in the current parser file. |
| 658 | `                        scan -= 1` | Stores/updates parser state or response data. |
| 659 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 660 | `                        continue` | Moves to next loop iteration. |
| 661 | `                    # AUTO: Stops the nearest loop.` | Comment/guideline in the current parser file. |
| 662 | `                    break` | Stops nearest loop. |
| 663 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 664 | `            if context_keyword:` | Checks parser condition. |
| 665 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 666 | `                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}' after '{context_keyword}'. {self._format_expected({':'})}"` | Returns value/result to caller. |
| 667 | `        ` | Blank spacing line. |
| 668 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 669 | `        if ';' in expected:` | Checks parser condition. |
| 670 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 671 | `            if token_type in statement_starters or token_type == 'id':` | Checks parser condition. |
| 672 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 673 | `                if index > 0:` | Checks parser condition. |
| 674 | `                    # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 675 | `                    prev_index = index - 1` | Stores/updates parser state or response data. |
| 676 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 677 | `                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 678 | `                        # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 679 | `                        prev_index -= 1` | Stores/updates parser state or response data. |
| 680 | `                    ` | Blank spacing line. |
| 681 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 682 | `                    if prev_index >= 0:` | Checks parser condition. |
| 683 | `                        # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 684 | `                        prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 685 | `                        ` | Blank spacing line. |
| 686 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 687 | `                        if prev_tok.type == '=':` | Checks parser condition. |
| 688 | `                            # AUTO: Sets `prev_line`.` | Comment/guideline in the current parser file. |
| 689 | `                            prev_line = prev_tok.line` | Stores/updates parser state or response data. |
| 690 | `                            # AUTO: Sets `prev_col`.` | Comment/guideline in the current parser file. |
| 691 | `                            prev_col = prev_tok.col` | Stores/updates parser state or response data. |
| 692 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 693 | `                            return f"SYNTAX error line {prev_line} col {prev_col} Missing value after '=' operator. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 694 | `                        ` | Blank spacing line. |
| 695 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 696 | `                        if prev_tok.type == 'chrlit' and prev_tok.value and not prev_tok.value.endswith("'"):` | Checks parser condition. |
| 697 | `                            # AUTO: Sets `prev_line`.` | Comment/guideline in the current parser file. |
| 698 | `                            prev_line = prev_tok.line` | Stores/updates parser state or response data. |
| 699 | `                            # AUTO: Sets `prev_col`.` | Comment/guideline in the current parser file. |
| 700 | `                            prev_col = prev_tok.col` | Stores/updates parser state or response data. |
| 701 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 702 | `                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 703 | `                        ` | Blank spacing line. |
| 704 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 705 | `                        if prev_tok.type == 'stringlit' and prev_tok.value and not prev_tok.value.endswith('"'):` | Checks parser condition. |
| 706 | `                            # AUTO: Sets `prev_line`.` | Comment/guideline in the current parser file. |
| 707 | `                            prev_line = prev_tok.line` | Stores/updates parser state or response data. |
| 708 | `                            # AUTO: Sets `prev_col`.` | Comment/guideline in the current parser file. |
| 709 | `                            prev_col = prev_tok.col` | Stores/updates parser state or response data. |
| 710 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 711 | `                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 712 | `                        ` | Blank spacing line. |
| 713 | `                        # AUTO: Sets `prev_line`.` | Comment/guideline in the current parser file. |
| 714 | `                        prev_line = prev_tok.line` | Stores/updates parser state or response data. |
| 715 | `                        # AUTO: Sets `prev_col`.` | Comment/guideline in the current parser file. |
| 716 | `                        prev_col = prev_tok.col + len(str(prev_tok.value))` | Stores/updates parser state or response data. |
| 717 | `                        # AUTO: Sets `expected_str`.` | Comment/guideline in the current parser file. |
| 718 | `                        expected_str = self._format_expected(expected, non_terminal)` | Stores/updates parser state or response data. |
| 719 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 720 | `                        if prev_line != line:` | Checks parser condition. |
| 721 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 722 | `                            return (f"SYNTAX error line {prev_line} col {prev_col} Unexpected token '{token_value}' after '{prev_tok.value}'. {expected_str}")` | Returns value/result to caller. |
| 723 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 724 | `                        else:` | Fallback branch. |
| 725 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 726 | `                            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {expected_str}"` | Returns value/result to caller. |
| 727 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 728 | `            elif token_type == '}':` | Alternative condition. |
| 729 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 730 | `                if index > 0:` | Checks parser condition. |
| 731 | `                    # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 732 | `                    prev_index = index - 1` | Stores/updates parser state or response data. |
| 733 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 734 | `                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 735 | `                        # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 736 | `                        prev_index -= 1` | Stores/updates parser state or response data. |
| 737 | `                    ` | Blank spacing line. |
| 738 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 739 | `                    if prev_index >= 0:` | Checks parser condition. |
| 740 | `                        # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 741 | `                        prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 742 | `                        ` | Blank spacing line. |
| 743 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 744 | `                        if prev_tok.type == 'reclaim':` | Checks parser condition. |
| 745 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 746 | `                            return f"SYNTAX error line {prev_tok.line} col {prev_tok.col + len('reclaim')} Missing ';' after 'reclaim'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 747 | `                        ` | Blank spacing line. |
| 748 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 749 | `                        if prev_tok.type == 'chrlit' and prev_tok.value and not prev_tok.value.endswith("'"):` | Checks parser condition. |
| 750 | `                            # AUTO: Sets `prev_line`.` | Comment/guideline in the current parser file. |
| 751 | `                            prev_line = prev_tok.line` | Stores/updates parser state or response data. |
| 752 | `                            # AUTO: Sets `prev_col`.` | Comment/guideline in the current parser file. |
| 753 | `                            prev_col = prev_tok.col` | Stores/updates parser state or response data. |
| 754 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 755 | `                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing single quote in character literal. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 756 | `                        ` | Blank spacing line. |
| 757 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 758 | `                        if prev_tok.type == 'stringlit' and prev_tok.value and not prev_tok.value.endswith('"'):` | Checks parser condition. |
| 759 | `                            # AUTO: Sets `prev_line`.` | Comment/guideline in the current parser file. |
| 760 | `                            prev_line = prev_tok.line` | Stores/updates parser state or response data. |
| 761 | `                            # AUTO: Sets `prev_col`.` | Comment/guideline in the current parser file. |
| 762 | `                            prev_col = prev_tok.col` | Stores/updates parser state or response data. |
| 763 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 764 | `                            return f"SYNTAX error line {prev_line} col {prev_col} Missing closing double quote in string literal. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 765 | `                        ` | Blank spacing line. |
| 766 | `                        # AUTO: Sets `prev_line`.` | Comment/guideline in the current parser file. |
| 767 | `                        prev_line = prev_tok.line` | Stores/updates parser state or response data. |
| 768 | `                        # AUTO: Sets `prev_col`.` | Comment/guideline in the current parser file. |
| 769 | `                        prev_col = prev_tok.col + len(str(prev_tok.value))` | Stores/updates parser state or response data. |
| 770 | `                        # AUTO: Sets `expected_str`.` | Comment/guideline in the current parser file. |
| 771 | `                        expected_str = self._format_expected(expected, non_terminal)` | Stores/updates parser state or response data. |
| 772 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 773 | `                        if prev_line != line:` | Checks parser condition. |
| 774 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 775 | `                            return f"SYNTAX error line {prev_line} col {prev_col} Unexpected token '}}' after '{prev_tok.value}'. {expected_str}"` | Returns value/result to caller. |
| 776 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 777 | `                        else:` | Fallback branch. |
| 778 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 779 | `                            return f"SYNTAX error line {line} col {col} Unexpected token '}}'. {expected_str}"` | Returns value/result to caller. |
| 780 | `        ` | Blank spacing line. |
| 781 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 782 | `        if 'reclaim' in expected and token_type == '}':` | Checks parser condition. |
| 783 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 784 | `            return f"SYNTAX error line {line} col {col} expected 'reclaim;' before '}}'. All functions, including root(), must end with 'reclaim;'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 785 | `        ` | Blank spacing line. |
| 786 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 787 | `        if 'prune' in expected and token_type in {'variety', 'soil', '}'}:` | Checks parser condition. |
| 788 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 789 | `            if token_type == 'variety':` | Checks parser condition. |
| 790 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 791 | `                return f"SYNTAX error line {line} col {col} expected 'prune;' before next 'variety'. Each case in 'harvest' must end with 'prune;'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 792 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 793 | `            elif token_type == 'soil':` | Alternative condition. |
| 794 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 795 | `                return f"SYNTAX error line {line} col {col} expected 'prune;' before 'soil'. Each case must end with 'prune;'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 796 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 797 | `            else:` | Fallback branch. |
| 798 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 799 | `                return f"SYNTAX error line {line} col {col} expected 'prune;' before closing '}}'. Each case must end with 'prune;'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 800 | `        ` | Blank spacing line. |
| 801 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 802 | `        if token_type in {'-', '+'} and non_terminal in {'<expression>', '<factor>', '<term>', '<arithmetic>', '<logic_or>', '<logic_and>', '<relational>', '<init_val>'}:` | Checks parser condition. |
| 803 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 804 | `            if index > 0:` | Checks parser condition. |
| 805 | `                # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 806 | `                prev_index = index - 1` | Stores/updates parser state or response data. |
| 807 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 808 | `                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 809 | `                    # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 810 | `                    prev_index -= 1` | Stores/updates parser state or response data. |
| 811 | `                ` | Blank spacing line. |
| 812 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 813 | `                if prev_index >= 0:` | Checks parser condition. |
| 814 | `                    # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 815 | `                    prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 816 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 817 | `                    if prev_tok.type in {'=', '+=', '-=', '*=', '/=', '%=', '(', ','}:` | Checks parser condition. |
| 818 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 819 | `                        if token_value == '-':` | Checks parser condition. |
| 820 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 821 | `                            return f"SYNTAX error line {line} col {col} Unary '-' not supported. Use '~' for negative numbers (e.g., '~5') or '(0 - value)' for negation. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 822 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 823 | `                        else:` | Fallback branch. |
| 824 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 825 | `                            return f"SYNTAX error line {line} col {col} Unary '+' operator not supported. Use parentheses for expressions like '(0 + value)'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 826 | `        ` | Blank spacing line. |
| 827 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 828 | `        if token_type in {'*', '/', '%', '+', '-', '`', '&&', '\|\|', '==', '!=', '<', '>', '<=', '>='}:` | Checks parser condition. |
| 829 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 830 | `            if index > 0:` | Checks parser condition. |
| 831 | `                # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 832 | `                prev_index = index - 1` | Stores/updates parser state or response data. |
| 833 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 834 | `                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 835 | `                    # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 836 | `                    prev_index -= 1` | Stores/updates parser state or response data. |
| 837 | `                ` | Blank spacing line. |
| 838 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 839 | `                if prev_index >= 0 and toks[prev_index].type == '(':` | Checks parser condition. |
| 840 | `                    # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 841 | `                    return f"SYNTAX error line {line} col {col} Unexpected binary operator '{token_value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 842 | `        ` | Blank spacing line. |
| 843 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 844 | `        if '(' in expected and token_type != '(':` | Checks parser condition. |
| 845 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 846 | `            if index > 0 and token_type not in {'-', '+'}:` | Checks parser condition. |
| 847 | `                # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 848 | `                prev_index = index - 1` | Stores/updates parser state or response data. |
| 849 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 850 | `                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 851 | `                    # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 852 | `                    prev_index -= 1` | Stores/updates parser state or response data. |
| 853 | `                ` | Blank spacing line. |
| 854 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 855 | `                if prev_index >= 0:` | Checks parser condition. |
| 856 | `                    # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 857 | `                    prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 858 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 859 | `                    if prev_tok.type in {'+', '-', '*', '/', '%', '`', '=', '+=', '-=', '*=', '/=', '%=', '&&', '\|\|', '==', '!=', '<', '>', '<=', '>='}:` | Checks parser condition. |
| 860 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 861 | `                        if token_type in {'*', '/', '%', '+', '-', '`', '&&', '\|\|', '==', '!=', '<', '>', '<=', '>='}:` | Checks parser condition. |
| 862 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 863 | `                            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}' operator - binary operators cannot start an expression. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 864 | `                        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 865 | `                        return f"SYNTAX error line {line} col {col} Missing value after '{prev_tok.value}' operator. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 866 | `            ` | Blank spacing line. |
| 867 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 868 | `            if token_type in {'=', '+=', '-=', '*=', '/=', '%='}:` | Checks parser condition. |
| 869 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 870 | `                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 871 | `            ` | Blank spacing line. |
| 872 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 873 | `            if index > 0:` | Checks parser condition. |
| 874 | `                # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 875 | `                prev_index = index - 1` | Stores/updates parser state or response data. |
| 876 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 877 | `                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 878 | `                    # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 879 | `                    prev_index -= 1` | Stores/updates parser state or response data. |
| 880 | `                ` | Blank spacing line. |
| 881 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 882 | `                if prev_index >= 0:` | Checks parser condition. |
| 883 | `                    # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 884 | `                    prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 885 | `                    ` | Blank spacing line. |
| 886 | `                    # AUTO: Sets `common_keyword_mistakes`.` | Comment/guideline in the current parser file. |
| 887 | `                    common_keyword_mistakes = {` | Stores/updates parser state or response data. |
| 888 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 889 | `                        'function': 'pollinate',` | Parser support logic used during syntax checking. |
| 890 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 891 | `                        'int': 'seed',` | Parser support logic used during syntax checking. |
| 892 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 893 | `                        'float': 'tree',` | Parser support logic used during syntax checking. |
| 894 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 895 | `                        'double': 'tree',` | Parser support logic used during syntax checking. |
| 896 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 897 | `                        'char': 'leaf',` | Parser support logic used during syntax checking. |
| 898 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 899 | `                        'bool': 'branch',` | Parser support logic used during syntax checking. |
| 900 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 901 | `                        'boolean': 'branch',` | Parser support logic used during syntax checking. |
| 902 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 903 | `                        'if': 'spring',` | Parser support logic used during syntax checking. |
| 904 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 905 | `                        'else': 'wither',` | Parser support logic used during syntax checking. |
| 906 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 907 | `                        'elif': 'bud',` | Parser support logic used during syntax checking. |
| 908 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 909 | `                        'while': 'grow',` | Parser support logic used during syntax checking. |
| 910 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 911 | `                        'for': 'cultivate',` | Parser support logic used during syntax checking. |
| 912 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 913 | `                        'switch': 'harvest',` | Parser support logic used during syntax checking. |
| 914 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 915 | `                        'case': 'variety',` | Parser support logic used during syntax checking. |
| 916 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 917 | `                        'default': 'soil',` | Parser support logic used during syntax checking. |
| 918 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 919 | `                        'break': 'prune',` | Parser support logic used during syntax checking. |
| 920 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 921 | `                        'continue': 'skip',` | Parser support logic used during syntax checking. |
| 922 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 923 | `                        'return': 'reclaim',` | Parser support logic used during syntax checking. |
| 924 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 925 | `                        'void': 'empty',` | Parser support logic used during syntax checking. |
| 926 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 927 | `                        'const': 'fertile',` | Parser support logic used during syntax checking. |
| 928 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 929 | `                        'struct': 'bundle',` | Parser support logic used during syntax checking. |
| 930 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 931 | `                        'string': 'vine',` | Parser support logic used during syntax checking. |
| 932 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 933 | `                        'printf': 'plant',` | Parser support logic used during syntax checking. |
| 934 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 935 | `                        'scanf': 'water',` | Parser support logic used during syntax checking. |
| 936 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 937 | `                        'print': 'plant',` | Parser support logic used during syntax checking. |
| 938 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 939 | `                        'input': 'water'` | Parser support logic used during syntax checking. |
| 940 | `                    # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 941 | `                    }` | Closes Python grouping/list/dict/call. |
| 942 | `                    ` | Blank spacing line. |
| 943 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 944 | `                    if prev_tok.type == 'id' and prev_tok.value in common_keyword_mistakes:` | Checks parser condition. |
| 945 | `                        # AUTO: Sets `correct_keyword`.` | Comment/guideline in the current parser file. |
| 946 | `                        correct_keyword = common_keyword_mistakes[prev_tok.value]` | Stores/updates parser state or response data. |
| 947 | `                        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 948 | `                        return f"SYNTAX error line {prev_tok.line} col {prev_tok.col} '{prev_tok.value}' is not a GAL keyword. Use '{correct_keyword}' instead."` | Returns value/result to caller. |
| 949 | `                    ` | Blank spacing line. |
| 950 | `                    # AUTO: Sets `keywords_needing_parens`.` | Comment/guideline in the current parser file. |
| 951 | `                    keywords_needing_parens = {'spring', 'grow', 'cultivate', 'harvest', 'water', 'plant', 'tend', 'bud'}` | Stores/updates parser state or response data. |
| 952 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 953 | `                    if prev_tok.type in keywords_needing_parens:` | Checks parser condition. |
| 954 | `                        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 955 | `                        return f"SYNTAX error line {line} col {col} Missing '(' after '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 956 | `                    ` | Blank spacing line. |
| 957 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 958 | `                    if prev_tok.type == 'id':` | Checks parser condition. |
| 959 | `                        # NOTE: GAL does support '**' (exponentiation) and '**=' (exponent-assign).` | Comment/guideline in the current parser file. |
| 960 | `` | Blank spacing line. |
| 961 | `                        # AUTO: Sets `compound_op_bases`.` | Comment/guideline in the current parser file. |
| 962 | `                        compound_op_bases = {'+', '-', '*', '/', '%'}` | Stores/updates parser state or response data. |
| 963 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 964 | `                        if token_type in compound_op_bases:` | Checks parser condition. |
| 965 | `                            # AUTO: Sets `next_index`.` | Comment/guideline in the current parser file. |
| 966 | `                            next_index = index + 1` | Stores/updates parser state or response data. |
| 967 | `                            # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 968 | `                            while next_index < len(toks) and toks[next_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 969 | `                                # AUTO: Adds into `next_index`.` | Comment/guideline in the current parser file. |
| 970 | `                                next_index += 1` | Stores/updates parser state or response data. |
| 971 | `                            ` | Blank spacing line. |
| 972 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 973 | `                            if next_index < len(toks) and toks[next_index].type == '=':` | Checks parser condition. |
| 974 | `                                # AUTO: Sets `compound_op`.` | Comment/guideline in the current parser file. |
| 975 | `                                compound_op = f"{token_value}="` | Stores/updates parser state or response data. |
| 976 | `                                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 977 | `                                return f"SYNTAX error line {line} col {col} Unexpected operator '{token_value}' followed by '='. Expected: '{compound_op}' (compound assignment must be written without spaces). {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 978 | `                        ` | Blank spacing line. |
| 979 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 980 | `                        binary_operators = {'+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '\|\|'}` | Stores/updates parser state or response data. |
| 981 | `                        # AUTO: Sets `has_operators_expected`.` | Comment/guideline in the current parser file. |
| 982 | `                        has_operators_expected = bool(binary_operators & expected)` | Stores/updates parser state or response data. |
| 983 | `                        ` | Blank spacing line. |
| 984 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 985 | `                        if has_operators_expected:` | Checks parser condition. |
| 986 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 987 | `                            if token_type in {'++', '--'}:` | Checks parser condition. |
| 988 | `                                # AUTO: Sets `next_index`.` | Comment/guideline in the current parser file. |
| 989 | `                                next_index = index + 1` | Stores/updates parser state or response data. |
| 990 | `                                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 991 | `                                while next_index < len(toks) and toks[next_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 992 | `                                    # AUTO: Adds into `next_index`.` | Comment/guideline in the current parser file. |
| 993 | `                                    next_index += 1` | Stores/updates parser state or response data. |
| 994 | `                                ` | Blank spacing line. |
| 995 | `                                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 996 | `                                if next_index < len(toks):` | Checks parser condition. |
| 997 | `                                    # AUTO: Sets `next_tok`.` | Comment/guideline in the current parser file. |
| 998 | `                                    next_tok = toks[next_index]` | Stores/updates parser state or response data. |
| 999 | `                                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1000 | `                                    if (token_type == '++' and next_tok.type == '+') or (token_type == '--' and next_tok.type == '-'):` | Checks parser condition. |
| 1001 | `                                        # AUTO: Calls `+`.` | Comment/guideline in the current parser file. |
| 1002 | `                                        operator_seq = token_type + ('+' if token_type == '++' else '-')` | Stores/updates parser state or response data. |
| 1003 | `                                        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1004 | `                                        return f"SYNTAX error line {line} col {col} Unexpected token '{operator_seq}' operator sequence. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1005 | `                                ` | Blank spacing line. |
| 1006 | `                                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1007 | `                                return f"SYNTAX error line {line} col {col} Unexpected {token_type} operator. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1008 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1009 | `                            if token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'id'}:` | Checks parser condition. |
| 1010 | `                                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1011 | `                                return f"SYNTAX error line {line} col {col} Unexpected token '{token_type}' after identifier '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1012 | `                            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1013 | `                            else:` | Fallback branch. |
| 1014 | `                                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1015 | `                                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}' after identifier '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1016 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1017 | `                        else:` | Fallback branch. |
| 1018 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1019 | `                            return f"SYNTAX error line {prev_tok.line} col {prev_tok.col} invalid statement: identifier '{prev_tok.value}' must be followed by assignment operator, unary operator (++/--), or function call syntax '()'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1020 | `            ` | Blank spacing line. |
| 1021 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1022 | `            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1023 | `        ` | Blank spacing line. |
| 1024 | `        # AUTO: Sets `declaration_keywords`.` | Comment/guideline in the current parser file. |
| 1025 | `        declaration_keywords = {'seed', 'tree', 'leaf', 'vine', 'branch', 'bundle', 'fertile'}` | Stores/updates parser state or response data. |
| 1026 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1027 | `        if token_type in declaration_keywords and non_terminal in {'<body_statement>', '<statement>', '<case_statements>'}:` | Checks parser condition. |
| 1028 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1029 | `            return f"SYNTAX error line {line} col {col} Unexpected local declaration '{token_value}' after an executable statement. Local declarations must appear first in the block. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1030 | `` | Blank spacing line. |
| 1031 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1032 | `        if '}' in expected and token_type in statement_starters:` | Checks parser condition. |
| 1033 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1034 | `            if token_type == 'bud':` | Checks parser condition. |
| 1035 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1036 | `                return f"SYNTAX error line {line} col {col} 'bud' can only appear after a 'spring' statement. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1037 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1038 | `            elif token_type == 'wither':` | Alternative condition. |
| 1039 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1040 | `                return f"SYNTAX error line {line} col {col} 'wither' can only appear after a 'spring' or 'bud' statement. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1041 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1042 | `            elif token_type == 'reclaim':` | Alternative condition. |
| 1043 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1044 | `                return f"SYNTAX error line {line} col {col} Missing closing brace before '{token_value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1045 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1046 | `            return f"SYNTAX error line {line} col {col} Missing closing brace before '{token_value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1047 | `        ` | Blank spacing line. |
| 1048 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1049 | `        if token_type in {'++', '--'} and ')' in expected:` | Checks parser condition. |
| 1050 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1051 | `            op_name = "increment" if token_value == "++" else "decrement"` | Stores/updates parser state or response data. |
| 1052 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1053 | `            return f"SYNTAX error line {line} col {col} Postfix {op_name} operator '{token_value}' not allowed in expression context. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1054 | `        ` | Blank spacing line. |
| 1055 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1056 | `        if param_type_tokens & expected and ')' in expected and token_type == 'id':` | Checks parser condition. |
| 1057 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1058 | `            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. Expected parameter type (seed, tree, leaf, vine, branch) or ')'"` | Returns value/result to caller. |
| 1059 | `        ` | Blank spacing line. |
| 1060 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1061 | `        if ')' in expected and token_type not in {')'}:` | Checks parser condition. |
| 1062 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1063 | `            if ',' in expected and token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'id', 'sunshine', 'frost', '~', '!'}:` | Checks parser condition. |
| 1064 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1065 | `                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. Expected ',' between arguments or ')' to close function call"` | Returns value/result to caller. |
| 1066 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1067 | `            if token_type in {'~', '!'}:` | Checks parser condition. |
| 1068 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1069 | `                return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1070 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1071 | `            return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1072 | `        ` | Blank spacing line. |
| 1073 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1074 | `        if token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'id'}:` | Checks parser condition. |
| 1075 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1076 | `            if index > 0:` | Checks parser condition. |
| 1077 | `                # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 1078 | `                prev_index = index - 1` | Stores/updates parser state or response data. |
| 1079 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1080 | `                while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 1081 | `                    # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 1082 | `                    prev_index -= 1` | Stores/updates parser state or response data. |
| 1083 | `                ` | Blank spacing line. |
| 1084 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1085 | `                if prev_index >= 0:` | Checks parser condition. |
| 1086 | `                    # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 1087 | `                    prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 1088 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1089 | `                    if prev_tok.type in {'id', 'intlit', 'dblit', 'stringlit', 'chrlit'}:` | Checks parser condition. |
| 1090 | `                        # AUTO: Sets `expression_contexts`.` | Comment/guideline in the current parser file. |
| 1091 | `                        expression_contexts = {'<expression>', '<factor>', '<term>', '<arithmetic>', '<logic_or>', ` | Stores/updates parser state or response data. |
| 1092 | `                                             # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1093 | `                                             '<logic_and>', '<relational>', '<init_val>', '<param_list>', '<arg_list>',` | Parser support logic used during syntax checking. |
| 1094 | `                                             # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1095 | `                                             '<term_tail>', '<arithmetic_tail>', '<relational_tail>', '<logic_and_tail>', '<logic_or_tail>'}` | Parser support logic used during syntax checking. |
| 1096 | `                        ` | Blank spacing line. |
| 1097 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1098 | `                        if non_terminal in expression_contexts:` | Checks parser condition. |
| 1099 | `                            # AUTO: Sets `prev_type_friendly`.` | Comment/guideline in the current parser file. |
| 1100 | `                            prev_type_friendly = {` | Stores/updates parser state or response data. |
| 1101 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1102 | `                                'id': 'identifier',` | Parser support logic used during syntax checking. |
| 1103 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1104 | `                                'intlit': 'integer literal',` | Parser support logic used during syntax checking. |
| 1105 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1106 | `                                'dblit': 'double literal',` | Parser support logic used during syntax checking. |
| 1107 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1108 | `                                'stringlit': 'string literal',` | Parser support logic used during syntax checking. |
| 1109 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1110 | `                                'chrlit': 'character literal'` | Parser support logic used during syntax checking. |
| 1111 | `                            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 1112 | `                            }.get(prev_tok.type, prev_tok.type)` | Parser support logic used during syntax checking. |
| 1113 | `                            ` | Blank spacing line. |
| 1114 | `                            # AUTO: Sets `curr_type_friendly`.` | Comment/guideline in the current parser file. |
| 1115 | `                            curr_type_friendly = {` | Stores/updates parser state or response data. |
| 1116 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1117 | `                                'id': 'identifier',` | Parser support logic used during syntax checking. |
| 1118 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1119 | `                                'intlit': 'integer literal',` | Parser support logic used during syntax checking. |
| 1120 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1121 | `                                'dblit': 'double literal',` | Parser support logic used during syntax checking. |
| 1122 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1123 | `                                'stringlit': 'string literal',` | Parser support logic used during syntax checking. |
| 1124 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1125 | `                                'chrlit': 'character literal'` | Parser support logic used during syntax checking. |
| 1126 | `                            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 1127 | `                            }.get(token_type, token_type)` | Parser support logic used during syntax checking. |
| 1128 | `                            ` | Blank spacing line. |
| 1129 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1130 | `                            return f"SYNTAX error line {line} col {col} Unexpected {curr_type_friendly} '{token_value}' after {prev_type_friendly} '{prev_tok.value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1131 | `        ` | Blank spacing line. |
| 1132 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1133 | `        if non_terminal == '<array_dim_opt>' and token_type == 'id':` | Checks parser condition. |
| 1134 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1135 | `            return f"SYNTAX error line {line} col {col} Array size must be a constant integer literal, not a variable '{token_value}'. Expected: ']', dblit, intlit"` | Returns value/result to caller. |
| 1136 | `` | Blank spacing line. |
| 1137 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1138 | `        return f"SYNTAX error line {line} col {col} Unexpected token '{token_value}'. {self._format_expected(expected, non_terminal)}"` | Returns value/result to caller. |
| 1139 | `` | Blank spacing line. |
| 1140 | `    # AUTO: Defines function `parse`.` | Comment/guideline in the current parser file. |
| 1141 | `    def parse(self, tokens: Sequence[Any]) -> Tuple[bool, List[str]]:` | Method starts: main stack parser. |
| 1142 | `        # GUIDE: Main LL(1) stack algorithm; compare grammar symbols on the stack` | Comment/guideline in the current parser file. |
| 1143 | `        # with the current lookahead token, then expand or consume.` | Comment/guideline in the current parser file. |
| 1144 | `        # Convert incoming Token objects into the parser's simple _TokView form.` | Comment/guideline in the current parser file. |
| 1145 | `        # LINE: Convert lexer Token objects into the parser's lightweight token view.` | Comment/guideline in the current parser file. |
| 1146 | `        toks = [_as_tok(t) for t in tokens]` | Converts incoming tokens into _TokView list. |
| 1147 | `` | Blank spacing line. |
| 1148 | `        # Normalize token names so lexer aliases still match grammar terminals.` | Comment/guideline in the current parser file. |
| 1149 | `        # LINE: Rename token types if lexer name and grammar name differ.` | Comment/guideline in the current parser file. |
| 1150 | `        toks = [_TokView(self._normalize_token_type(t.type), t.value, t.line, t.col) for t in toks]` | Aligns lexer token types with grammar terminals. |
| 1151 | `` | Blank spacing line. |
| 1152 | `        # Make sure the parser always has an EOF marker to know when to stop.` | Comment/guideline in the current parser file. |
| 1153 | `        # LINE: Ensure EOF exists so the parsing loop has a stopping token.` | Comment/guideline in the current parser file. |
| 1154 | `        toks = self._ensure_eof(toks)` | Guarantees EOF is present. |
| 1155 | `` | Blank spacing line. |
| 1156 | `        # LINE: Keep current tokens for helper error messages.` | Comment/guideline in the current parser file. |
| 1157 | `        self._current_tokens = toks` | Stores/updates parser state or response data. |
| 1158 | `` | Blank spacing line. |
| 1159 | `        # Stack starts with EOF at the bottom and <program> on top. The parser` | Comment/guideline in the current parser file. |
| 1160 | `        # repeatedly expands the top grammar symbol until the stack is empty.` | Comment/guideline in the current parser file. |
| 1161 | `        # LINE: Start with EOF at bottom and <program> as the first rule to expand.` | Comment/guideline in the current parser file. |
| 1162 | `        stack: List[str] = [self.end_marker, self.start_symbol]` | Creates parser stack with EOF and <program>. |
| 1163 | `        # LINE: index points to the current lookahead token in toks.` | Comment/guideline in the current parser file. |
| 1164 | `        index = 0` | Points to current lookahead token. |
| 1165 | `        ` | Blank spacing line. |
| 1166 | `        # LINE: Track declaration type to make simple literal mismatch messages clearer.` | Comment/guideline in the current parser file. |
| 1167 | `        current_var_type: Optional[str] = None` | Stores/updates parser state or response data. |
| 1168 | `        # LINE: Becomes seed/tree/etc after '=' while parsing declarations.` | Comment/guideline in the current parser file. |
| 1169 | `        expecting_value_for_type: Optional[str] = None` | Stores/updates parser state or response data. |
| 1170 | `` | Blank spacing line. |
| 1171 | `        # LINE: Tracks whether reclaim already appeared inside each block.` | Comment/guideline in the current parser file. |
| 1172 | `        reclaim_seen_stack: List[bool] = []` | Stores/updates parser state or response data. |
| 1173 | `` | Blank spacing line. |
| 1174 | `        # AUTO: Defines function `current_token`.` | Comment/guideline in the current parser file. |
| 1175 | `        def current_token() -> _TokView:` | Nested helper returns current token. |
| 1176 | `            # Lookahead token: the parser decides what to do using only this` | Comment/guideline in the current parser file. |
| 1177 | `            # current token type, which is the LL(1) idea.` | Comment/guideline in the current parser file. |
| 1178 | `            # AUTO: Uses a variable from an outer function scope.` | Comment/guideline in the current parser file. |
| 1179 | `            nonlocal index` | Parser support logic used during syntax checking. |
| 1180 | `            # LINE: If index passed the stream, pretend the lookahead is EOF.` | Comment/guideline in the current parser file. |
| 1181 | `            if index >= len(toks):` | Checks parser condition. |
| 1182 | `                # AUTO: Sets `last_line`.` | Comment/guideline in the current parser file. |
| 1183 | `                last_line = toks[-1].line if toks else 1` | Stores/updates parser state or response data. |
| 1184 | `                # AUTO: Sets `last_col`.` | Comment/guideline in the current parser file. |
| 1185 | `                last_col = toks[-1].col if toks else 0` | Stores/updates parser state or response data. |
| 1186 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1187 | `                return _TokView(self.end_marker, self.end_marker, last_line, last_col)` | Returns value/result to caller. |
| 1188 | `            # LINE: Return the token currently being compared with the stack top.` | Comment/guideline in the current parser file. |
| 1189 | `            return toks[index]` | Returns value/result to caller. |
| 1190 | `` | Blank spacing line. |
| 1191 | `        # LINE: Keep parsing until every grammar symbol in the stack is handled.` | Comment/guideline in the current parser file. |
| 1192 | `        while stack:` | Main loop for stack algorithm. |
| 1193 | `            # top is the grammar symbol we need to match/expand.` | Comment/guideline in the current parser file. |
| 1194 | `            # tok is the current input token from the lexer.` | Comment/guideline in the current parser file. |
| 1195 | `            # LINE: Read the top grammar symbol and the current lookahead token.` | Comment/guideline in the current parser file. |
| 1196 | `            top = stack[-1]` | Reads current grammar symbol from stack top. |
| 1197 | `            # AUTO: Sets `tok`.` | Comment/guideline in the current parser file. |
| 1198 | `            tok = current_token()` | Reads current input/lookahead token. |
| 1199 | `            # AUTO: Sets `token_type`.` | Comment/guideline in the current parser file. |
| 1200 | `            token_type = tok.type` | Stores token type for table lookup/match. |
| 1201 | `            # AUTO: Sets `token_value`.` | Comment/guideline in the current parser file. |
| 1202 | `            token_value = tok.value` | Stores lexeme for error messages. |
| 1203 | `            # AUTO: Sets `line`.` | Comment/guideline in the current parser file. |
| 1204 | `            line = tok.line or 1` | Stores/updates parser state or response data. |
| 1205 | `` | Blank spacing line. |
| 1206 | `            # LINE: Ignore comments/newlines when the grammar is not asking for them.` | Comment/guideline in the current parser file. |
| 1207 | `            if token_type in self.skip_token_types and top != token_type:` | Skips newline/comment tokens. |
| 1208 | `                # AUTO: Adds into `index`.` | Comment/guideline in the current parser file. |
| 1209 | `                index += 1` | Consumes current token. |
| 1210 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 1211 | `                continue` | Moves to next loop iteration. |
| 1212 | `` | Blank spacing line. |
| 1213 | `            # LINE: Non-terminal case, such as <program> or <statement>.` | Comment/guideline in the current parser file. |
| 1214 | `            if top in self.parsing_table:` | If top is non-terminal, expand it using parse table. |
| 1215 | `                # Non-terminal case: use parsing_table[top][lookahead] to pick` | Comment/guideline in the current parser file. |
| 1216 | `                # the correct production from the CFG.` | Comment/guideline in the current parser file. |
| 1217 | `                # LINE: Get the parse-table row for this non-terminal.` | Comment/guideline in the current parser file. |
| 1218 | `                row = self.parsing_table[top]` | Gets parse table row for this non-terminal. |
| 1219 | `                # LINE: If lookahead exists in this row, we know which production to use.` | Comment/guideline in the current parser file. |
| 1220 | `                if token_type in row:` | Checks if lookahead predicts a production. |
| 1221 | `                    # LINE: Select the CFG production predicted by this lookahead token.` | Comment/guideline in the current parser file. |
| 1222 | `                    production = row[token_type]` | Chooses the production RHS. |
| 1223 | `                    ` | Blank spacing line. |
| 1224 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1225 | `                    if top == '<statement>' and token_type != '}' and reclaim_seen_stack and reclaim_seen_stack[-1]:` | Checks parser condition. |
| 1226 | `                        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1227 | `                        return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after 'reclaim'. Expected: '}}'."]` | Returns syntax failure. |
| 1228 | `` | Blank spacing line. |
| 1229 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1230 | `                    if top == '<statement>' and token_type == '}':` | Checks parser condition. |
| 1231 | `                        # AUTO: Calls `=`.` | Comment/guideline in the current parser file. |
| 1232 | `                        is_epsilon = (len(production) == 0 or (len(production) == 1 and production[0] in self.epsilon_symbols))` | Stores/updates parser state or response data. |
| 1233 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1234 | `                        if is_epsilon:` | Checks parser condition. |
| 1235 | `                            # AUTO: Sets `lookback`.` | Comment/guideline in the current parser file. |
| 1236 | `                            lookback = index - 1` | Stores/updates parser state or response data. |
| 1237 | `                            # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1238 | `                            while lookback >= 0 and toks[lookback].type in self.skip_token_types:` | Repeats while condition is true. |
| 1239 | `                                # AUTO: Subtracts from `lookback`.` | Comment/guideline in the current parser file. |
| 1240 | `                                lookback -= 1` | Stores/updates parser state or response data. |
| 1241 | `                            ` | Blank spacing line. |
| 1242 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1243 | `                            if lookback >= 0 and toks[lookback].type == '{':` | Checks parser condition. |
| 1244 | `                                # AUTO: Sets `before_brace`.` | Comment/guideline in the current parser file. |
| 1245 | `                                before_brace = lookback - 1` | Stores/updates parser state or response data. |
| 1246 | `                                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1247 | `                                while before_brace >= 0 and toks[before_brace].type in self.skip_token_types:` | Repeats while condition is true. |
| 1248 | `                                    # AUTO: Subtracts from `before_brace`.` | Comment/guideline in the current parser file. |
| 1249 | `                                    before_brace -= 1` | Stores/updates parser state or response data. |
| 1250 | `                                ` | Blank spacing line. |
| 1251 | `                                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1252 | `                                if before_brace >= 0 and toks[before_brace].type == ')':` | Checks parser condition. |
| 1253 | `                                    # AUTO: Sets `paren_depth`.` | Comment/guideline in the current parser file. |
| 1254 | `                                    paren_depth = 1` | Stores/updates parser state or response data. |
| 1255 | `                                    # AUTO: Sets `paren_pos`.` | Comment/guideline in the current parser file. |
| 1256 | `                                    paren_pos = before_brace - 1` | Stores/updates parser state or response data. |
| 1257 | `                                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1258 | `                                    while paren_pos >= 0 and paren_depth > 0:` | Repeats while condition is true. |
| 1259 | `                                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1260 | `                                        if toks[paren_pos].type == ')':` | Checks parser condition. |
| 1261 | `                                            # AUTO: Adds into `paren_depth`.` | Comment/guideline in the current parser file. |
| 1262 | `                                            paren_depth += 1` | Stores/updates parser state or response data. |
| 1263 | `                                        # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1264 | `                                        elif toks[paren_pos].type == '(':` | Alternative condition. |
| 1265 | `                                            # AUTO: Subtracts from `paren_depth`.` | Comment/guideline in the current parser file. |
| 1266 | `                                            paren_depth -= 1` | Stores/updates parser state or response data. |
| 1267 | `                                        # AUTO: Subtracts from `paren_pos`.` | Comment/guideline in the current parser file. |
| 1268 | `                                        paren_pos -= 1` | Stores/updates parser state or response data. |
| 1269 | `                                    ` | Blank spacing line. |
| 1270 | `                                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1271 | `                                    if paren_pos >= 0:` | Checks parser condition. |
| 1272 | `                                        # AUTO: Sets `kw_pos`.` | Comment/guideline in the current parser file. |
| 1273 | `                                        kw_pos = paren_pos` | Stores/updates parser state or response data. |
| 1274 | `                                        # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1275 | `                                        while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:` | Repeats while condition is true. |
| 1276 | `                                            # AUTO: Subtracts from `kw_pos`.` | Comment/guideline in the current parser file. |
| 1277 | `                                            kw_pos -= 1` | Stores/updates parser state or response data. |
| 1278 | `                                        ` | Blank spacing line. |
| 1279 | `                                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1280 | `                                        if kw_pos >= 0:` | Checks parser condition. |
| 1281 | `                                            # AUTO: Sets `kw`.` | Comment/guideline in the current parser file. |
| 1282 | `                                            kw = toks[kw_pos]` | Stores/updates parser state or response data. |
| 1283 | `                                            # AUTO: Sets `conditional_keywords`.` | Comment/guideline in the current parser file. |
| 1284 | `                                            conditional_keywords = {'spring', 'bud', 'wither', 'grow', 'cultivate', 'tend', 'harvest'}` | Stores/updates parser state or response data. |
| 1285 | `                                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1286 | `                                            if kw.type in conditional_keywords:` | Checks parser condition. |
| 1287 | `                                                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1288 | `                                                return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]` | Returns syntax failure. |
| 1289 | `                                ` | Blank spacing line. |
| 1290 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1291 | `                                elif before_brace >= 0 and toks[before_brace].type in {'wither', 'tend'}:` | Alternative condition. |
| 1292 | `                                    # AUTO: Sets `kw`.` | Comment/guideline in the current parser file. |
| 1293 | `                                    kw = toks[before_brace]` | Stores/updates parser state or response data. |
| 1294 | `                                    # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1295 | `                                    return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]` | Returns syntax failure. |
| 1296 | `                    ` | Blank spacing line. |
| 1297 | `                    # LINE: Remove the non-terminal before replacing it with its production.` | Comment/guideline in the current parser file. |
| 1298 | `                    stack.pop()` | Removes matched/expanded symbol from stack. |
| 1299 | `` | Blank spacing line. |
| 1300 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1301 | `                    if not (` | Checks parser condition. |
| 1302 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1303 | `                        len(production) == 0` | Stores/updates parser state or response data. |
| 1304 | `                        # AUTO: Calls `or`.` | Comment/guideline in the current parser file. |
| 1305 | `                        or (len(production) == 1 and production[0] in self.epsilon_symbols)` | Stores/updates parser state or response data. |
| 1306 | `                    # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 1307 | `                    ):` | Parser support logic used during syntax checking. |
| 1308 | `                        # Push production in reverse so the leftmost grammar` | Comment/guideline in the current parser file. |
| 1309 | `                        # symbol is processed next.` | Comment/guideline in the current parser file. |
| 1310 | `                        # LINE: Push RHS in reverse so the first RHS symbol becomes stack top.` | Comment/guideline in the current parser file. |
| 1311 | `                        stack.extend(reversed(production))` | Pushes RHS reversed onto stack. |
| 1312 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 1313 | `                    continue` | Moves to next loop iteration. |
| 1314 | `` | Blank spacing line. |
| 1315 | `                # LINE: If lookahead is not in row, parser knows this is a syntax error.` | Comment/guideline in the current parser file. |
| 1316 | `                expected = set(row.keys())` | Collects valid expected lookaheads for error. |
| 1317 | `                ` | Blank spacing line. |
| 1318 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1319 | `                if token_type in {'variety', 'soil'} and token_type not in expected:` | Checks parser condition. |
| 1320 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1321 | `                    while index < len(toks) and toks[index].type != ';':` | Repeats while condition is true. |
| 1322 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1323 | `                        if toks[index].type == 'prune':` | Checks parser condition. |
| 1324 | `                            # AUTO: Adds into `index`.` | Comment/guideline in the current parser file. |
| 1325 | `                            index += 1` | Consumes current token. |
| 1326 | `                            # AUTO: Stops the nearest loop.` | Comment/guideline in the current parser file. |
| 1327 | `                            break` | Stops nearest loop. |
| 1328 | `                        # AUTO: Adds into `index`.` | Comment/guideline in the current parser file. |
| 1329 | `                        index += 1` | Consumes current token. |
| 1330 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1331 | `                    if index < len(toks) and toks[index].type == ';':` | Checks parser condition. |
| 1332 | `                        # AUTO: Adds into `index`.` | Comment/guideline in the current parser file. |
| 1333 | `                        index += 1` | Consumes current token. |
| 1334 | `                    # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 1335 | `                    continue` | Moves to next loop iteration. |
| 1336 | `` | Blank spacing line. |
| 1337 | `                # LINE: Create a friendly expected-token message and stop parsing.` | Comment/guideline in the current parser file. |
| 1338 | `                error_msg = self._generate_helpful_error(top, token_type, token_value, line, tok.col, expected, index, toks)` | Creates syntax error text. |
| 1339 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1340 | `                return False, [error_msg]` | Returns syntax failure. |
| 1341 | `` | Blank spacing line. |
| 1342 | `            # LINE: Terminal case, such as seed, id, ;, (, or =.` | Comment/guideline in the current parser file. |
| 1343 | `            if top == token_type:` | Terminal match branch. |
| 1344 | `                # Terminal case: grammar expected the same token type the lexer` | Comment/guideline in the current parser file. |
| 1345 | `                # produced, so consume it by popping stack and moving index.` | Comment/guideline in the current parser file. |
| 1346 | `                # LINE: Remember declared type when consuming a data-type token.` | Comment/guideline in the current parser file. |
| 1347 | `                if token_type in {'seed', 'tree', 'leaf', 'branch', 'vine'}:` | Checks parser condition. |
| 1348 | `                    # AUTO: Sets `current_var_type`.` | Comment/guideline in the current parser file. |
| 1349 | `                    current_var_type = token_type` | Stores/updates parser state or response data. |
| 1350 | `                    # AUTO: Sets `expecting_value_for_type`.` | Comment/guideline in the current parser file. |
| 1351 | `                    expecting_value_for_type = None` | Stores/updates parser state or response data. |
| 1352 | `                ` | Blank spacing line. |
| 1353 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1354 | `                elif token_type == '=' and current_var_type is not None:` | Alternative condition. |
| 1355 | `                    # AUTO: Sets `expecting_value_for_type`.` | Comment/guideline in the current parser file. |
| 1356 | `                    expecting_value_for_type = current_var_type` | Stores/updates parser state or response data. |
| 1357 | `                ` | Blank spacing line. |
| 1358 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1359 | `                elif expecting_value_for_type is not None and token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'sunshine', 'frost', 'id'}:` | Alternative condition. |
| 1360 | `                    # AUTO: Sets `type_value_map`.` | Comment/guideline in the current parser file. |
| 1361 | `                    type_value_map = {` | Stores/updates parser state or response data. |
| 1362 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1363 | `                        'seed': {'intlit', 'dblit'},` | Parser support logic used during syntax checking. |
| 1364 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1365 | `                        'tree': {'dblit', 'intlit'},` | Parser support logic used during syntax checking. |
| 1366 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1367 | `                        'leaf': {'chrlit'},` | Parser support logic used during syntax checking. |
| 1368 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1369 | `                        'branch': {'sunshine', 'frost'},` | Parser support logic used during syntax checking. |
| 1370 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1371 | `                        'vine': {'stringlit'}` | Parser support logic used during syntax checking. |
| 1372 | `                    # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 1373 | `                    }` | Closes Python grouping/list/dict/call. |
| 1374 | `                    ` | Blank spacing line. |
| 1375 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1376 | `                    if token_type == 'id':` | Checks parser condition. |
| 1377 | `                        # AUTO: Sets `expecting_value_for_type`.` | Comment/guideline in the current parser file. |
| 1378 | `                        expecting_value_for_type = None` | Stores/updates parser state or response data. |
| 1379 | `                        # AUTO: Removes and returns an item.` | Comment/guideline in the current parser file. |
| 1380 | `                        stack.pop()` | Removes matched/expanded symbol from stack. |
| 1381 | `                        # AUTO: Adds into `index`.` | Comment/guideline in the current parser file. |
| 1382 | `                        index += 1` | Consumes current token. |
| 1383 | `                        # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 1384 | `                        continue` | Moves to next loop iteration. |
| 1385 | `                    ` | Blank spacing line. |
| 1386 | `                    # AUTO: Sets `expected_value_types`.` | Comment/guideline in the current parser file. |
| 1387 | `                    expected_value_types = type_value_map.get(expecting_value_for_type, set())` | Stores/updates parser state or response data. |
| 1388 | `                    ` | Blank spacing line. |
| 1389 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1390 | `                    if token_type not in expected_value_types:` | Checks parser condition. |
| 1391 | `                        # AUTO: Sets `type_names`.` | Comment/guideline in the current parser file. |
| 1392 | `                        type_names = {` | Stores/updates parser state or response data. |
| 1393 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1394 | `                            'seed': 'integer (seed)',` | Parser support logic used during syntax checking. |
| 1395 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1396 | `                            'tree': 'double (tree)',` | Parser support logic used during syntax checking. |
| 1397 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1398 | `                            'leaf': 'character (leaf)',` | Parser support logic used during syntax checking. |
| 1399 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1400 | `                            'branch': 'boolean (branch)',` | Parser support logic used during syntax checking. |
| 1401 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1402 | `                            'vine': 'string (vine)'` | Parser support logic used during syntax checking. |
| 1403 | `                        # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 1404 | `                        }` | Closes Python grouping/list/dict/call. |
| 1405 | `                        # AUTO: Sets `value_type_names`.` | Comment/guideline in the current parser file. |
| 1406 | `                        value_type_names = {` | Stores/updates parser state or response data. |
| 1407 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1408 | `                            'intlit': 'integer',` | Parser support logic used during syntax checking. |
| 1409 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1410 | `                            'dblit': 'double',` | Parser support logic used during syntax checking. |
| 1411 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1412 | `                            'stringlit': 'string',` | Parser support logic used during syntax checking. |
| 1413 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1414 | `                            'chrlit': 'character',` | Parser support logic used during syntax checking. |
| 1415 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1416 | `                            'sunshine': 'boolean',` | Parser support logic used during syntax checking. |
| 1417 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1418 | `                            'frost': 'boolean',` | Parser support logic used during syntax checking. |
| 1419 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1420 | `                            'id': 'identifier'` | Parser support logic used during syntax checking. |
| 1421 | `                        # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 1422 | `                        }` | Closes Python grouping/list/dict/call. |
| 1423 | `                        ` | Blank spacing line. |
| 1424 | `                        # AUTO: Sets `declared_type`.` | Comment/guideline in the current parser file. |
| 1425 | `                        declared_type = type_names.get(expecting_value_for_type, expecting_value_for_type)` | Stores/updates parser state or response data. |
| 1426 | `                        # AUTO: Sets `actual_type`.` | Comment/guideline in the current parser file. |
| 1427 | `                        actual_type = value_type_names.get(token_type, token_type)` | Stores/updates parser state or response data. |
| 1428 | `                        ` | Blank spacing line. |
| 1429 | `                        # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1430 | `                        error_msg = f"SEMANTIC error line {line} col {tok.col} Type mismatch: cannot assign {actual_type} value '{token_value}' to {declared_type} variable"` | Stores/updates parser state or response data. |
| 1431 | `                        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1432 | `                        return False, [error_msg]` | Returns syntax failure. |
| 1433 | `                    ` | Blank spacing line. |
| 1434 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1435 | `                    if token_type == 'chrlit' and expecting_value_for_type == 'leaf':` | Checks parser condition. |
| 1436 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1437 | `                        char_content = token_value[1:-1] if len(token_value) >= 2 else token_value` | Stores/updates parser state or response data. |
| 1438 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1439 | `                        if len(char_content) == 0:` | Checks parser condition. |
| 1440 | `                            # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1441 | `                            error_msg = f"SYNTAX error line {line} col {tok.col} Character literal cannot be empty. Expected a single character for leaf variable"` | Stores/updates parser state or response data. |
| 1442 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1443 | `                            return False, [error_msg]` | Returns syntax failure. |
| 1444 | `                        # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1445 | `                        elif char_content.startswith('\\') and len(char_content) == 2:` | Alternative condition. |
| 1446 | `                            # AUTO: Does nothing for this required block.` | Comment/guideline in the current parser file. |
| 1447 | `                            pass` | Parser support logic used during syntax checking. |
| 1448 | `                        # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1449 | `                        elif len(char_content) > 1:` | Alternative condition. |
| 1450 | `                            # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1451 | `                            error_msg = f"SYNTAX error line {line} col {tok.col} Character literal '{token_value}' contains {len(char_content)} characters. leaf variables can only hold a single character"` | Stores/updates parser state or response data. |
| 1452 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1453 | `                            return False, [error_msg]` | Returns syntax failure. |
| 1454 | `                    ` | Blank spacing line. |
| 1455 | `                    ` | Blank spacing line. |
| 1456 | `                    # AUTO: Sets `expecting_value_for_type`.` | Comment/guideline in the current parser file. |
| 1457 | `                    expecting_value_for_type = None` | Stores/updates parser state or response data. |
| 1458 | `                ` | Blank spacing line. |
| 1459 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1460 | `                elif token_type == ';':` | Alternative condition. |
| 1461 | `                    # AUTO: Sets `current_var_type`.` | Comment/guideline in the current parser file. |
| 1462 | `                    current_var_type = None` | Stores/updates parser state or response data. |
| 1463 | `                    # AUTO: Sets `expecting_value_for_type`.` | Comment/guideline in the current parser file. |
| 1464 | `                    expecting_value_for_type = None` | Stores/updates parser state or response data. |
| 1465 | `                ` | Blank spacing line. |
| 1466 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1467 | `                if top == 'intlit' or top == 'dblit':` | Checks parser condition. |
| 1468 | `                    # AUTO: Sets `lookback`.` | Comment/guideline in the current parser file. |
| 1469 | `                    lookback = index - 1` | Stores/updates parser state or response data. |
| 1470 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1471 | `                    while lookback >= 0 and toks[lookback].type in self.skip_token_types:` | Repeats while condition is true. |
| 1472 | `                        # AUTO: Subtracts from `lookback`.` | Comment/guideline in the current parser file. |
| 1473 | `                        lookback -= 1` | Stores/updates parser state or response data. |
| 1474 | `                    ` | Blank spacing line. |
| 1475 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1476 | `                    if lookback >= 0 and toks[lookback].type == '(':` | Checks parser condition. |
| 1477 | `                        # AUTO: Sets `kw_pos`.` | Comment/guideline in the current parser file. |
| 1478 | `                        kw_pos = lookback - 1` | Stores/updates parser state or response data. |
| 1479 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1480 | `                        while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:` | Repeats while condition is true. |
| 1481 | `                            # AUTO: Subtracts from `kw_pos`.` | Comment/guideline in the current parser file. |
| 1482 | `                            kw_pos -= 1` | Stores/updates parser state or response data. |
| 1483 | `                        ` | Blank spacing line. |
| 1484 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1485 | `                        if kw_pos >= 0:` | Checks parser condition. |
| 1486 | `                            # AUTO: Sets `kw`.` | Comment/guideline in the current parser file. |
| 1487 | `                            kw = toks[kw_pos]` | Stores/updates parser state or response data. |
| 1488 | `                            # AUTO: Sets `condition_keywords`.` | Comment/guideline in the current parser file. |
| 1489 | `                            condition_keywords = {'spring', 'grow', 'cultivate', 'tend', 'bud'}` | Stores/updates parser state or response data. |
| 1490 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1491 | `                            if kw.type in condition_keywords:` | Checks parser condition. |
| 1492 | `                                # AUTO: Sets `next_idx`.` | Comment/guideline in the current parser file. |
| 1493 | `                                next_idx = index + 1` | Stores/updates parser state or response data. |
| 1494 | `                                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1495 | `                                while next_idx < len(toks) and toks[next_idx].type in self.skip_token_types:` | Repeats while condition is true. |
| 1496 | `                                    # AUTO: Adds into `next_idx`.` | Comment/guideline in the current parser file. |
| 1497 | `                                    next_idx += 1` | Stores/updates parser state or response data. |
| 1498 | `                                ` | Blank spacing line. |
| 1499 | `                                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1500 | `                                if next_idx < len(toks) and toks[next_idx].type == ')':` | Checks parser condition. |
| 1501 | `                                    # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1502 | `                                    return False, [f"SYNTAX error line {line} col {tok.col} '{kw.value}' requires a boolean condition, not a numeric literal"]` | Returns syntax failure. |
| 1503 | `                ` | Blank spacing line. |
| 1504 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1505 | `                if token_type in {'&&', '\|\|'}:` | Checks parser condition. |
| 1506 | `                    # AUTO: Sets `prev_idx`.` | Comment/guideline in the current parser file. |
| 1507 | `                    prev_idx = index - 1` | Stores/updates parser state or response data. |
| 1508 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1509 | `                    while prev_idx >= 0 and toks[prev_idx].type in self.skip_token_types:` | Repeats while condition is true. |
| 1510 | `                        # AUTO: Subtracts from `prev_idx`.` | Comment/guideline in the current parser file. |
| 1511 | `                        prev_idx -= 1` | Stores/updates parser state or response data. |
| 1512 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1513 | `                    if prev_idx >= 0:` | Checks parser condition. |
| 1514 | `                        # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 1515 | `                        prev_tok = toks[prev_idx]` | Stores/updates parser state or response data. |
| 1516 | `                        # AUTO: Sets `non_branch_literals`.` | Comment/guideline in the current parser file. |
| 1517 | `                        non_branch_literals = {'intlit', 'dblit', 'stringlit', 'chrlit'}` | Stores/updates parser state or response data. |
| 1518 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1519 | `                        if prev_tok.type in non_branch_literals:` | Checks parser condition. |
| 1520 | `                            # AUTO: Sets `cmp_idx`.` | Comment/guideline in the current parser file. |
| 1521 | `                            cmp_idx = prev_idx - 1` | Stores/updates parser state or response data. |
| 1522 | `                            # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1523 | `                            while cmp_idx >= 0 and toks[cmp_idx].type in self.skip_token_types:` | Repeats while condition is true. |
| 1524 | `                                # AUTO: Subtracts from `cmp_idx`.` | Comment/guideline in the current parser file. |
| 1525 | `                                cmp_idx -= 1` | Stores/updates parser state or response data. |
| 1526 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1527 | `                            comparison_ops = {'<', '>', '<=', '>=', '==', '!='}` | Stores/updates parser state or response data. |
| 1528 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1529 | `                            if cmp_idx >= 0 and toks[cmp_idx].type in comparison_ops:` | Checks parser condition. |
| 1530 | `                                # AUTO: Does nothing for this required block.` | Comment/guideline in the current parser file. |
| 1531 | `                                pass` | Parser support logic used during syntax checking. |
| 1532 | `                            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1533 | `                            else:` | Fallback branch. |
| 1534 | `                                # AUTO: Sets `type_names`.` | Comment/guideline in the current parser file. |
| 1535 | `                                type_names = {` | Stores/updates parser state or response data. |
| 1536 | `                                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1537 | `                                    'intlit': 'integer literal',` | Parser support logic used during syntax checking. |
| 1538 | `                                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1539 | `                                    'dblit': 'double literal',` | Parser support logic used during syntax checking. |
| 1540 | `                                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1541 | `                                    'stringlit': 'string literal',` | Parser support logic used during syntax checking. |
| 1542 | `                                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1543 | `                                    'chrlit': 'character literal',` | Parser support logic used during syntax checking. |
| 1544 | `                                # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 1545 | `                                }` | Closes Python grouping/list/dict/call. |
| 1546 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1547 | `                                op_name = 'AND' if token_type == '&&' else 'OR'` | Stores/updates parser state or response data. |
| 1548 | `                                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1549 | `                                return False, [f"SYNTAX error line {line} col {tok.col} Logical operator '{token_type}' ({op_name}) requires branch operands, not {type_names[prev_tok.type]} '{prev_tok.value}'"]` | Returns syntax failure. |
| 1550 | `                ` | Blank spacing line. |
| 1551 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1552 | `                if token_type in {'intlit', 'dblit', 'stringlit', 'chrlit'}:` | Checks parser condition. |
| 1553 | `                    # AUTO: Sets `prev_idx`.` | Comment/guideline in the current parser file. |
| 1554 | `                    prev_idx = index - 1` | Stores/updates parser state or response data. |
| 1555 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1556 | `                    while prev_idx >= 0 and toks[prev_idx].type in self.skip_token_types:` | Repeats while condition is true. |
| 1557 | `                        # AUTO: Subtracts from `prev_idx`.` | Comment/guideline in the current parser file. |
| 1558 | `                        prev_idx -= 1` | Stores/updates parser state or response data. |
| 1559 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1560 | `                    if prev_idx >= 0 and toks[prev_idx].type in {'&&', '\|\|'}:` | Checks parser condition. |
| 1561 | `                        # AUTO: Sets `next_check`.` | Comment/guideline in the current parser file. |
| 1562 | `                        next_check = index + 1` | Stores/updates parser state or response data. |
| 1563 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1564 | `                        while next_check < len(toks) and toks[next_check].type in self.skip_token_types:` | Repeats while condition is true. |
| 1565 | `                            # AUTO: Adds into `next_check`.` | Comment/guideline in the current parser file. |
| 1566 | `                            next_check += 1` | Stores/updates parser state or response data. |
| 1567 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1568 | `                        comparison_ops = {'<', '>', '<=', '>=', '==', '!='}` | Stores/updates parser state or response data. |
| 1569 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1570 | `                        if next_check < len(toks) and toks[next_check].type in comparison_ops:` | Checks parser condition. |
| 1571 | `                            # AUTO: Does nothing for this required block.` | Comment/guideline in the current parser file. |
| 1572 | `                            pass` | Parser support logic used during syntax checking. |
| 1573 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1574 | `                        else:` | Fallback branch. |
| 1575 | `                            # AUTO: Sets `type_names`.` | Comment/guideline in the current parser file. |
| 1576 | `                            type_names = {` | Stores/updates parser state or response data. |
| 1577 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1578 | `                                'intlit': 'integer literal',` | Parser support logic used during syntax checking. |
| 1579 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1580 | `                                'dblit': 'double literal',` | Parser support logic used during syntax checking. |
| 1581 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1582 | `                                'stringlit': 'string literal',` | Parser support logic used during syntax checking. |
| 1583 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1584 | `                                'chrlit': 'character literal',` | Parser support logic used during syntax checking. |
| 1585 | `                            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 1586 | `                            }` | Closes Python grouping/list/dict/call. |
| 1587 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1588 | `                            op_name = 'AND' if toks[prev_idx].type == '&&' else 'OR'` | Stores/updates parser state or response data. |
| 1589 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1590 | `                            return False, [f"SYNTAX error line {line} col {tok.col} Logical operator '{toks[prev_idx].type}' ({op_name}) requires branch operands, not {type_names[token_type]} '{token_value}'"]` | Returns syntax failure. |
| 1591 | `` | Blank spacing line. |
| 1592 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1593 | `                if token_type == '{':` | Checks parser condition. |
| 1594 | `                    # AUTO: Appends a value to a list.` | Comment/guideline in the current parser file. |
| 1595 | `                    reclaim_seen_stack.append(False)` | Parser support logic used during syntax checking. |
| 1596 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1597 | `                elif token_type == '}':` | Alternative condition. |
| 1598 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1599 | `                    if reclaim_seen_stack:` | Checks parser condition. |
| 1600 | `                        # AUTO: Removes and returns an item.` | Comment/guideline in the current parser file. |
| 1601 | `                        reclaim_seen_stack.pop()` | Parser support logic used during syntax checking. |
| 1602 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1603 | `                elif token_type == 'reclaim':` | Alternative condition. |
| 1604 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1605 | `                    if reclaim_seen_stack:` | Checks parser condition. |
| 1606 | `                        # AUTO: Sets `reclaim_seen_stack[-1]`.` | Comment/guideline in the current parser file. |
| 1607 | `                        reclaim_seen_stack[-1] = True` | Stores/updates parser state or response data. |
| 1608 | `` | Blank spacing line. |
| 1609 | `                # LINE: Matched terminal is done, so remove it from the stack.` | Comment/guideline in the current parser file. |
| 1610 | `                stack.pop()` | Removes matched/expanded symbol from stack. |
| 1611 | `                # LINE: Move to the next lexer token.` | Comment/guideline in the current parser file. |
| 1612 | `                index += 1` | Consumes current token. |
| 1613 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 1614 | `                continue` | Moves to next loop iteration. |
| 1615 | `` | Blank spacing line. |
| 1616 | `            # LINE: EOF can pass over skipped comments/newlines.` | Comment/guideline in the current parser file. |
| 1617 | `            if top == self.end_marker and token_type in self.skip_token_types:` | Checks parser condition. |
| 1618 | `                # AUTO: Adds into `index`.` | Comment/guideline in the current parser file. |
| 1619 | `                index += 1` | Consumes current token. |
| 1620 | `                # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 1621 | `                continue` | Moves to next loop iteration. |
| 1622 | `` | Blank spacing line. |
| 1623 | `            # LINE: If stack terminal and token do not match, build syntax error.` | Comment/guideline in the current parser file. |
| 1624 | `            expected = {top}` | Stores/updates parser state or response data. |
| 1625 | `            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1626 | `            shown_value = "end of file" if token_type == self.end_marker else token_value` | Stores/updates parser state or response data. |
| 1627 | `            ` | Blank spacing line. |
| 1628 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1629 | `            if token_type == self.end_marker:` | Checks parser condition. |
| 1630 | `                # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1631 | `                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected end of file. Expected: '{top}'. Missing closing '}}' or incomplete statement."` | Stores/updates parser state or response data. |
| 1632 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1633 | `                return False, [error_msg]` | Returns syntax failure. |
| 1634 | `            ` | Blank spacing line. |
| 1635 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1636 | `            if top == 'grow' and token_type == '(':` | Checks parser condition. |
| 1637 | `                # AUTO: Sets `scan_idx`.` | Comment/guideline in the current parser file. |
| 1638 | `                scan_idx = index - 1` | Stores/updates parser state or response data. |
| 1639 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1640 | `                while scan_idx >= 0 and toks[scan_idx].type in self.skip_token_types:` | Repeats while condition is true. |
| 1641 | `                    # AUTO: Subtracts from `scan_idx`.` | Comment/guideline in the current parser file. |
| 1642 | `                    scan_idx -= 1` | Stores/updates parser state or response data. |
| 1643 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1644 | `                if scan_idx >= 0 and toks[scan_idx].type == '}':` | Checks parser condition. |
| 1645 | `                    # AUTO: Sets `brace_depth`.` | Comment/guideline in the current parser file. |
| 1646 | `                    brace_depth = 1` | Stores/updates parser state or response data. |
| 1647 | `                    # AUTO: Subtracts from `scan_idx`.` | Comment/guideline in the current parser file. |
| 1648 | `                    scan_idx -= 1` | Stores/updates parser state or response data. |
| 1649 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1650 | `                    while scan_idx >= 0 and brace_depth > 0:` | Repeats while condition is true. |
| 1651 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1652 | `                        if toks[scan_idx].type == '}':` | Checks parser condition. |
| 1653 | `                            # AUTO: Adds into `brace_depth`.` | Comment/guideline in the current parser file. |
| 1654 | `                            brace_depth += 1` | Stores/updates parser state or response data. |
| 1655 | `                        # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1656 | `                        elif toks[scan_idx].type == '{':` | Alternative condition. |
| 1657 | `                            # AUTO: Subtracts from `brace_depth`.` | Comment/guideline in the current parser file. |
| 1658 | `                            brace_depth -= 1` | Stores/updates parser state or response data. |
| 1659 | `                        # AUTO: Subtracts from `scan_idx`.` | Comment/guideline in the current parser file. |
| 1660 | `                        scan_idx -= 1` | Stores/updates parser state or response data. |
| 1661 | `                    # AUTO: Sets `kw_idx`.` | Comment/guideline in the current parser file. |
| 1662 | `                    kw_idx = scan_idx` | Stores/updates parser state or response data. |
| 1663 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1664 | `                    while kw_idx >= 0 and toks[kw_idx].type in self.skip_token_types:` | Repeats while condition is true. |
| 1665 | `                        # AUTO: Subtracts from `kw_idx`.` | Comment/guideline in the current parser file. |
| 1666 | `                        kw_idx -= 1` | Stores/updates parser state or response data. |
| 1667 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1668 | `                    if kw_idx >= 0 and toks[kw_idx].type == 'tend':` | Checks parser condition. |
| 1669 | `                        # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1670 | `                        error_msg = f"SYNTAX error line {line} col {tok.col} Missing 'grow' keyword before '('. {self._format_expected(expected, top)}. Correct format: tend {{ ... }} grow (condition);"` | Stores/updates parser state or response data. |
| 1671 | `                        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1672 | `                        return False, [error_msg]` | Returns syntax failure. |
| 1673 | `            ` | Blank spacing line. |
| 1674 | `            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1675 | `            if top == 'reclaim' and token_type == '}':` | Checks parser condition. |
| 1676 | `                # AUTO: Sets `is_root`.` | Comment/guideline in the current parser file. |
| 1677 | `                is_root = False` | Stores/updates parser state or response data. |
| 1678 | `                # AUTO: Starts a loop over these values.` | Comment/guideline in the current parser file. |
| 1679 | `                for i in range(index - 1, -1, -1):` | Loops over items. |
| 1680 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1681 | `                    if toks[i].type == 'root':` | Checks parser condition. |
| 1682 | `                        # AUTO: Sets `is_root`.` | Comment/guideline in the current parser file. |
| 1683 | `                        is_root = True` | Stores/updates parser state or response data. |
| 1684 | `                        # AUTO: Stops the nearest loop.` | Comment/guideline in the current parser file. |
| 1685 | `                        break` | Stops nearest loop. |
| 1686 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1687 | `                    elif toks[i].type == 'pollinate':` | Alternative condition. |
| 1688 | `                        # AUTO: Sets `is_root`.` | Comment/guideline in the current parser file. |
| 1689 | `                        is_root = False` | Stores/updates parser state or response data. |
| 1690 | `                        # AUTO: Stops the nearest loop.` | Comment/guideline in the current parser file. |
| 1691 | `                        break` | Stops nearest loop. |
| 1692 | `                ` | Blank spacing line. |
| 1693 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1694 | `                if is_root:` | Checks parser condition. |
| 1695 | `                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1696 | `                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'reclaim;' before '}}'. The root() function (main program) must end with 'reclaim;'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1697 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1698 | `                else:` | Fallback branch. |
| 1699 | `                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1700 | `                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'reclaim;' before '}}'. All functions must end with 'reclaim;'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1701 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1702 | `                return False, [error_msg]` | Returns syntax failure. |
| 1703 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1704 | `            elif top == 'prune' and token_type in {'variety', 'soil', '}'}:` | Alternative condition. |
| 1705 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1706 | `                if token_type == 'variety':` | Checks parser condition. |
| 1707 | `                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1708 | `                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'prune;' before next 'variety'. Each case in 'harvest' must end with 'prune;'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1709 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1710 | `                elif token_type == 'soil':` | Alternative condition. |
| 1711 | `                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1712 | `                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'prune;' before 'soil'. Each case must end with 'prune;'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1713 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1714 | `                else:` | Fallback branch. |
| 1715 | `                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1716 | `                    error_msg = f"SYNTAX error line {line} col {tok.col} expected 'prune;' before closing '}}'. Each case must end with 'prune;'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1717 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1718 | `                return False, [error_msg]` | Returns syntax failure. |
| 1719 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1720 | `            elif top == '(' and token_type != '(':` | Alternative condition. |
| 1721 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1722 | `                if token_type in {'=', '+=', '-=', '*=', '/=', '%='}:` | Checks parser condition. |
| 1723 | `                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1724 | `                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected, top)}"` | Stores/updates parser state or response data. |
| 1725 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1726 | `                elif index > 0:` | Alternative condition. |
| 1727 | `                    # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 1728 | `                    prev_index = index - 1` | Stores/updates parser state or response data. |
| 1729 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1730 | `                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 1731 | `                        # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 1732 | `                        prev_index -= 1` | Stores/updates parser state or response data. |
| 1733 | `                    ` | Blank spacing line. |
| 1734 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1735 | `                    if prev_index >= 0:` | Checks parser condition. |
| 1736 | `                        # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 1737 | `                        prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 1738 | `                        ` | Blank spacing line. |
| 1739 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1740 | `                        if prev_tok.type == '}':` | Checks parser condition. |
| 1741 | `                            # AUTO: Sets `brace_depth`.` | Comment/guideline in the current parser file. |
| 1742 | `                            brace_depth = 1` | Stores/updates parser state or response data. |
| 1743 | `                            # AUTO: Sets `scan_idx`.` | Comment/guideline in the current parser file. |
| 1744 | `                            scan_idx = prev_index - 1` | Stores/updates parser state or response data. |
| 1745 | `                            # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1746 | `                            while scan_idx >= 0 and brace_depth > 0:` | Repeats while condition is true. |
| 1747 | `                                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1748 | `                                if toks[scan_idx].type == '}':` | Checks parser condition. |
| 1749 | `                                    # AUTO: Adds into `brace_depth`.` | Comment/guideline in the current parser file. |
| 1750 | `                                    brace_depth += 1` | Stores/updates parser state or response data. |
| 1751 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1752 | `                                elif toks[scan_idx].type == '{':` | Alternative condition. |
| 1753 | `                                    # AUTO: Subtracts from `brace_depth`.` | Comment/guideline in the current parser file. |
| 1754 | `                                    brace_depth -= 1` | Stores/updates parser state or response data. |
| 1755 | `                                # AUTO: Subtracts from `scan_idx`.` | Comment/guideline in the current parser file. |
| 1756 | `                                scan_idx -= 1` | Stores/updates parser state or response data. |
| 1757 | `                            ` | Blank spacing line. |
| 1758 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1759 | `                            if scan_idx >= 0:` | Checks parser condition. |
| 1760 | `                                # AUTO: Sets `kw_idx`.` | Comment/guideline in the current parser file. |
| 1761 | `                                kw_idx = scan_idx` | Stores/updates parser state or response data. |
| 1762 | `                                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1763 | `                                while kw_idx >= 0 and toks[kw_idx].type in self.skip_token_types:` | Repeats while condition is true. |
| 1764 | `                                    # AUTO: Subtracts from `kw_idx`.` | Comment/guideline in the current parser file. |
| 1765 | `                                    kw_idx -= 1` | Stores/updates parser state or response data. |
| 1766 | `                                ` | Blank spacing line. |
| 1767 | `                                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1768 | `                                if kw_idx >= 0 and toks[kw_idx].type == 'tend':` | Checks parser condition. |
| 1769 | `                                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1770 | `                                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. 'tend' requires 'grow' after closing brace '}}'. Correct format: tend {{ ... }} grow (condition); {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1771 | `                                # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1772 | `                                else:` | Fallback branch. |
| 1773 | `                                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1774 | `                                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1775 | `                            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1776 | `                            else:` | Fallback branch. |
| 1777 | `                                # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1778 | `                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1779 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1780 | `                        else:` | Fallback branch. |
| 1781 | `                            # AUTO: Sets `keywords_needing_parens`.` | Comment/guideline in the current parser file. |
| 1782 | `                            keywords_needing_parens = {'spring', 'grow', 'cultivate', 'harvest', 'water', 'plant', 'tend', 'bud'}` | Stores/updates parser state or response data. |
| 1783 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1784 | `                            if prev_tok.type in keywords_needing_parens:` | Checks parser condition. |
| 1785 | `                                # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1786 | `                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{prev_tok.value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1787 | `                            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1788 | `                            else:` | Fallback branch. |
| 1789 | `                                # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1790 | `                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1791 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1792 | `                    else:` | Fallback branch. |
| 1793 | `                        # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1794 | `                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1795 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1796 | `                else:` | Fallback branch. |
| 1797 | `                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1798 | `                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1799 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1800 | `                return False, [error_msg]` | Returns syntax failure. |
| 1801 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1802 | `            elif top == '{' and token_type != '{':` | Alternative condition. |
| 1803 | `                # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1804 | `                error_msg = None` | Stores/updates parser state or response data. |
| 1805 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1806 | `                if token_type == ')' and index > 0:` | Checks parser condition. |
| 1807 | `                    # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 1808 | `                    prev_index = index - 1` | Stores/updates parser state or response data. |
| 1809 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1810 | `                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 1811 | `                        # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 1812 | `                        prev_index -= 1` | Stores/updates parser state or response data. |
| 1813 | `                    ` | Blank spacing line. |
| 1814 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1815 | `                    if prev_index >= 0 and toks[prev_index].type == ')':` | Checks parser condition. |
| 1816 | `                        # AUTO: Sets `paren_index`.` | Comment/guideline in the current parser file. |
| 1817 | `                        paren_index = prev_index - 1` | Stores/updates parser state or response data. |
| 1818 | `                        # AUTO: Sets `paren_count`.` | Comment/guideline in the current parser file. |
| 1819 | `                        paren_count = 1` | Stores/updates parser state or response data. |
| 1820 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1821 | `                        while paren_index >= 0 and paren_count > 0:` | Repeats while condition is true. |
| 1822 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1823 | `                            if toks[paren_index].type == ')':` | Checks parser condition. |
| 1824 | `                                # AUTO: Adds into `paren_count`.` | Comment/guideline in the current parser file. |
| 1825 | `                                paren_count += 1` | Stores/updates parser state or response data. |
| 1826 | `                            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1827 | `                            elif toks[paren_index].type == '(':` | Alternative condition. |
| 1828 | `                                # AUTO: Subtracts from `paren_count`.` | Comment/guideline in the current parser file. |
| 1829 | `                                paren_count -= 1` | Stores/updates parser state or response data. |
| 1830 | `                            # AUTO: Subtracts from `paren_index`.` | Comment/guideline in the current parser file. |
| 1831 | `                            paren_index -= 1` | Stores/updates parser state or response data. |
| 1832 | `                        ` | Blank spacing line. |
| 1833 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1834 | `                        if paren_index >= 0:` | Checks parser condition. |
| 1835 | `                            # AUTO: Sets `kw_index`.` | Comment/guideline in the current parser file. |
| 1836 | `                            kw_index = paren_index` | Stores/updates parser state or response data. |
| 1837 | `                            # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1838 | `                            while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 1839 | `                                # AUTO: Subtracts from `kw_index`.` | Comment/guideline in the current parser file. |
| 1840 | `                                kw_index -= 1` | Stores/updates parser state or response data. |
| 1841 | `                            ` | Blank spacing line. |
| 1842 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1843 | `                            if kw_index >= 0:` | Checks parser condition. |
| 1844 | `                                # AUTO: Sets `kw_tok`.` | Comment/guideline in the current parser file. |
| 1845 | `                                kw_tok = toks[kw_index]` | Stores/updates parser state or response data. |
| 1846 | `                                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1847 | `                                if kw_tok.type in {'root', 'pollinate'}:` | Checks parser condition. |
| 1848 | `                                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1849 | `                                    error_msg = f"SYNTAX error line {line} col {tok.col} Extra closing ')' after '{kw_tok.value}()'. Correct syntax: {kw_tok.value}(){{ ... }}. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1850 | `                ` | Blank spacing line. |
| 1851 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1852 | `                if error_msg is None and index > 0:` | Checks parser condition. |
| 1853 | `                    # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 1854 | `                    prev_index = index - 1` | Stores/updates parser state or response data. |
| 1855 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1856 | `                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 1857 | `                        # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 1858 | `                        prev_index -= 1` | Stores/updates parser state or response data. |
| 1859 | `                    ` | Blank spacing line. |
| 1860 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1861 | `                    if prev_index >= 0:` | Checks parser condition. |
| 1862 | `                        # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 1863 | `                        prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 1864 | `                        # AUTO: Sets `keywords_needing_braces`.` | Comment/guideline in the current parser file. |
| 1865 | `                        keywords_needing_braces = {'spring', 'wither', 'grow', 'cultivate', 'tend', 'harvest', 'bud', ')', 'pollinate', 'root'}` | Stores/updates parser state or response data. |
| 1866 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1867 | `                        if prev_tok.type in keywords_needing_braces:` | Checks parser condition. |
| 1868 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1869 | `                            if prev_tok.type == ')':` | Checks parser condition. |
| 1870 | `                                # AUTO: Sets `paren_index`.` | Comment/guideline in the current parser file. |
| 1871 | `                                paren_index = prev_index - 1` | Stores/updates parser state or response data. |
| 1872 | `                                # AUTO: Sets `paren_count`.` | Comment/guideline in the current parser file. |
| 1873 | `                                paren_count = 1` | Stores/updates parser state or response data. |
| 1874 | `                                # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1875 | `                                while paren_index >= 0 and paren_count > 0:` | Repeats while condition is true. |
| 1876 | `                                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1877 | `                                    if toks[paren_index].type == ')':` | Checks parser condition. |
| 1878 | `                                        # AUTO: Adds into `paren_count`.` | Comment/guideline in the current parser file. |
| 1879 | `                                        paren_count += 1` | Stores/updates parser state or response data. |
| 1880 | `                                    # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1881 | `                                    elif toks[paren_index].type == '(':` | Alternative condition. |
| 1882 | `                                        # AUTO: Subtracts from `paren_count`.` | Comment/guideline in the current parser file. |
| 1883 | `                                        paren_count -= 1` | Stores/updates parser state or response data. |
| 1884 | `                                    # AUTO: Subtracts from `paren_index`.` | Comment/guideline in the current parser file. |
| 1885 | `                                    paren_index -= 1` | Stores/updates parser state or response data. |
| 1886 | `                                ` | Blank spacing line. |
| 1887 | `                                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1888 | `                                if paren_index >= 0:` | Checks parser condition. |
| 1889 | `                                    # AUTO: Sets `kw_index`.` | Comment/guideline in the current parser file. |
| 1890 | `                                    kw_index = paren_index` | Stores/updates parser state or response data. |
| 1891 | `                                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1892 | `                                    while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 1893 | `                                        # AUTO: Subtracts from `kw_index`.` | Comment/guideline in the current parser file. |
| 1894 | `                                        kw_index -= 1` | Stores/updates parser state or response data. |
| 1895 | `                                    ` | Blank spacing line. |
| 1896 | `                                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1897 | `                                    if kw_index >= 0:` | Checks parser condition. |
| 1898 | `                                        # AUTO: Sets `kw_tok`.` | Comment/guideline in the current parser file. |
| 1899 | `                                        kw_tok = toks[kw_index]` | Stores/updates parser state or response data. |
| 1900 | `                                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1901 | `                                        if kw_tok.type in {'spring', 'grow', 'cultivate', 'tend', 'harvest', 'bud', 'pollinate', 'root'}:` | Checks parser condition. |
| 1902 | `                                            # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1903 | `                                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{kw_tok.value}' statement. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1904 | `                                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1905 | `                                        else:` | Fallback branch. |
| 1906 | `                                            # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1907 | `                                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1908 | `                                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1909 | `                                    else:` | Fallback branch. |
| 1910 | `                                        # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1911 | `                                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1912 | `                                # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1913 | `                                else:` | Fallback branch. |
| 1914 | `                                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1915 | `                                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1916 | `                            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1917 | `                            else:` | Fallback branch. |
| 1918 | `                                # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1919 | `                                error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{prev_tok.value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1920 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1921 | `                        else:` | Fallback branch. |
| 1922 | `                            # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1923 | `                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1924 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1925 | `                    else:` | Fallback branch. |
| 1926 | `                        # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1927 | `                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1928 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1929 | `                elif error_msg is None:` | Alternative condition. |
| 1930 | `                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 1931 | `                    error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 1932 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1933 | `                return False, [error_msg]` | Returns syntax failure. |
| 1934 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1935 | `            elif top == '}' and token_type != '}':` | Alternative condition. |
| 1936 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1937 | `                return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. Missing closing brace. {self._format_expected(expected)}"]` | Returns syntax failure. |
| 1938 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1939 | `            elif top == ')' and token_type != ')':` | Alternative condition. |
| 1940 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1941 | `                return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"]` | Returns syntax failure. |
| 1942 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 1943 | `            elif top == ':' and token_type != ':':` | Alternative condition. |
| 1944 | `                # AUTO: Sets `context_keyword`.` | Comment/guideline in the current parser file. |
| 1945 | `                context_keyword = None` | Stores/updates parser state or response data. |
| 1946 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1947 | `                if index > 0:` | Checks parser condition. |
| 1948 | `                    # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 1949 | `                    prev_index = index - 1` | Stores/updates parser state or response data. |
| 1950 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1951 | `                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 1952 | `                        # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 1953 | `                        prev_index -= 1` | Stores/updates parser state or response data. |
| 1954 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1955 | `                    if prev_index >= 0:` | Checks parser condition. |
| 1956 | `                        # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 1957 | `                        prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 1958 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1959 | `                        if prev_tok.type == 'soil':` | Checks parser condition. |
| 1960 | `                            # AUTO: Sets `context_keyword`.` | Comment/guideline in the current parser file. |
| 1961 | `                            context_keyword = 'soil'` | Stores/updates parser state or response data. |
| 1962 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1963 | `                        else:` | Fallback branch. |
| 1964 | `                            # AUTO: Sets `scan`.` | Comment/guideline in the current parser file. |
| 1965 | `                            scan = prev_index` | Stores/updates parser state or response data. |
| 1966 | `                            # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 1967 | `                            while scan >= 0:` | Repeats while condition is true. |
| 1968 | `                                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1969 | `                                if toks[scan].type in self.skip_token_types:` | Checks parser condition. |
| 1970 | `                                    # AUTO: Subtracts from `scan`.` | Comment/guideline in the current parser file. |
| 1971 | `                                    scan -= 1` | Stores/updates parser state or response data. |
| 1972 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 1973 | `                                    continue` | Moves to next loop iteration. |
| 1974 | `                                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1975 | `                                if toks[scan].type == 'variety':` | Checks parser condition. |
| 1976 | `                                    # AUTO: Sets `context_keyword`.` | Comment/guideline in the current parser file. |
| 1977 | `                                    context_keyword = 'variety'` | Stores/updates parser state or response data. |
| 1978 | `                                    # AUTO: Stops the nearest loop.` | Comment/guideline in the current parser file. |
| 1979 | `                                    break` | Stops nearest loop. |
| 1980 | `                                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1981 | `                                if toks[scan].type in {'id', 'intlit', 'dblit', 'stringlit', 'chrlit',` | Checks parser condition. |
| 1982 | `                                                       # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1983 | `                                                       'sunshine', 'frost', '+', '-', '*', '/', '%',` | Parser support logic used during syntax checking. |
| 1984 | `                                                       # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1985 | `                                                       '==', '!=', '<', '>', '<=', '>=', '&&', '\|\|',` | Stores/updates parser state or response data. |
| 1986 | `                                                       # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 1987 | `                                                       '(', ')', '`', '~'}:` | Parser support logic used during syntax checking. |
| 1988 | `                                    # AUTO: Subtracts from `scan`.` | Comment/guideline in the current parser file. |
| 1989 | `                                    scan -= 1` | Stores/updates parser state or response data. |
| 1990 | `                                    # AUTO: Skips to the next loop iteration.` | Comment/guideline in the current parser file. |
| 1991 | `                                    continue` | Moves to next loop iteration. |
| 1992 | `                                # AUTO: Stops the nearest loop.` | Comment/guideline in the current parser file. |
| 1993 | `                                break` | Stops nearest loop. |
| 1994 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 1995 | `                if context_keyword:` | Checks parser condition. |
| 1996 | `                    # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 1997 | `                    return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{context_keyword}'. {self._format_expected({':'})}"]` | Returns syntax failure. |
| 1998 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 1999 | `                else:` | Fallback branch. |
| 2000 | `                    # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 2001 | `                    return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected({':'})}"]` | Returns syntax failure. |
| 2002 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 2003 | `            elif top == ';' and token_type != ';':` | Alternative condition. |
| 2004 | `                # AUTO: Sets `common_keyword_mistakes`.` | Comment/guideline in the current parser file. |
| 2005 | `                common_keyword_mistakes = {` | Stores/updates parser state or response data. |
| 2006 | `                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2007 | `                    'function': 'pollinate', 'int': 'seed', 'float': 'tree', 'double': 'tree',` | Parser support logic used during syntax checking. |
| 2008 | `                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2009 | `                    'char': 'leaf', 'bool': 'branch', 'boolean': 'branch', 'if': 'spring',` | Parser support logic used during syntax checking. |
| 2010 | `                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2011 | `                    'else': 'wither', 'elif': 'bud', 'while': 'grow', 'for': 'cultivate',` | Parser support logic used during syntax checking. |
| 2012 | `                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2013 | `                    'switch': 'harvest', 'case': 'variety', 'default': 'soil', 'break': 'prune',` | Parser support logic used during syntax checking. |
| 2014 | `                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2015 | `                    'continue': 'skip', 'return': 'reclaim', 'void': 'empty', 'const': 'fertile',` | Parser support logic used during syntax checking. |
| 2016 | `                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2017 | `                    'struct': 'bundle', 'string': 'vine', 'printf': 'plant', 'scanf': 'water',` | Parser support logic used during syntax checking. |
| 2018 | `                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2019 | `                    'print': 'plant', 'input': 'water'` | Parser support logic used during syntax checking. |
| 2020 | `                # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2021 | `                }` | Closes Python grouping/list/dict/call. |
| 2022 | `                ` | Blank spacing line. |
| 2023 | `                # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 2024 | `                error_msg = None` | Stores/updates parser state or response data. |
| 2025 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2026 | `                if token_type == '{' and index > 0:` | Checks parser condition. |
| 2027 | `                    # AUTO: Sets `paren_idx`.` | Comment/guideline in the current parser file. |
| 2028 | `                    paren_idx = index - 1` | Stores/updates parser state or response data. |
| 2029 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 2030 | `                    while paren_idx >= 0 and toks[paren_idx].type in self.skip_token_types:` | Repeats while condition is true. |
| 2031 | `                        # AUTO: Subtracts from `paren_idx`.` | Comment/guideline in the current parser file. |
| 2032 | `                        paren_idx -= 1` | Stores/updates parser state or response data. |
| 2033 | `                    ` | Blank spacing line. |
| 2034 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2035 | `                    if paren_idx >= 0 and toks[paren_idx].type == ')':` | Checks parser condition. |
| 2036 | `                        # AUTO: Sets `paren_depth`.` | Comment/guideline in the current parser file. |
| 2037 | `                        paren_depth = 1` | Stores/updates parser state or response data. |
| 2038 | `                        # AUTO: Subtracts from `paren_idx`.` | Comment/guideline in the current parser file. |
| 2039 | `                        paren_idx -= 1` | Stores/updates parser state or response data. |
| 2040 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 2041 | `                        while paren_idx >= 0 and paren_depth > 0:` | Repeats while condition is true. |
| 2042 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2043 | `                            if toks[paren_idx].type == ')':` | Checks parser condition. |
| 2044 | `                                # AUTO: Adds into `paren_depth`.` | Comment/guideline in the current parser file. |
| 2045 | `                                paren_depth += 1` | Stores/updates parser state or response data. |
| 2046 | `                            # AUTO: Checks the next alternate condition.` | Comment/guideline in the current parser file. |
| 2047 | `                            elif toks[paren_idx].type == '(':` | Alternative condition. |
| 2048 | `                                # AUTO: Subtracts from `paren_depth`.` | Comment/guideline in the current parser file. |
| 2049 | `                                paren_depth -= 1` | Stores/updates parser state or response data. |
| 2050 | `                            # AUTO: Subtracts from `paren_idx`.` | Comment/guideline in the current parser file. |
| 2051 | `                            paren_idx -= 1` | Stores/updates parser state or response data. |
| 2052 | `                        ` | Blank spacing line. |
| 2053 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2054 | `                        if paren_idx >= 0:` | Checks parser condition. |
| 2055 | `                            # AUTO: Sets `id_idx`.` | Comment/guideline in the current parser file. |
| 2056 | `                            id_idx = paren_idx` | Stores/updates parser state or response data. |
| 2057 | `                            # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 2058 | `                            while id_idx >= 0 and toks[id_idx].type in self.skip_token_types:` | Repeats while condition is true. |
| 2059 | `                                # AUTO: Subtracts from `id_idx`.` | Comment/guideline in the current parser file. |
| 2060 | `                                id_idx -= 1` | Stores/updates parser state or response data. |
| 2061 | `                            ` | Blank spacing line. |
| 2062 | `                            # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2063 | `                            if id_idx >= 0 and toks[id_idx].type == 'id' and toks[id_idx].value in common_keyword_mistakes:` | Checks parser condition. |
| 2064 | `                                # AUTO: Sets `keyword_tok`.` | Comment/guideline in the current parser file. |
| 2065 | `                                keyword_tok = toks[id_idx]` | Stores/updates parser state or response data. |
| 2066 | `                                # AUTO: Sets `correct_keyword`.` | Comment/guideline in the current parser file. |
| 2067 | `                                correct_keyword = common_keyword_mistakes[keyword_tok.value]` | Stores/updates parser state or response data. |
| 2068 | `                                # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 2069 | `                                error_msg = f"SYNTAX error line {keyword_tok.line} col {keyword_tok.col} '{keyword_tok.value}' is not a GAL keyword. Use '{correct_keyword}' instead."` | Stores/updates parser state or response data. |
| 2070 | `                ` | Blank spacing line. |
| 2071 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2072 | `                if error_msg is None and token_type == 'id' and token_value in common_keyword_mistakes:` | Checks parser condition. |
| 2073 | `                    # AUTO: Sets `correct_keyword`.` | Comment/guideline in the current parser file. |
| 2074 | `                    correct_keyword = common_keyword_mistakes[token_value]` | Stores/updates parser state or response data. |
| 2075 | `                    # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 2076 | `                    error_msg = f"SYNTAX error line {line} col {tok.col} '{token_value}' is not a GAL keyword. Use '{correct_keyword}' instead."` | Stores/updates parser state or response data. |
| 2077 | `                ` | Blank spacing line. |
| 2078 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2079 | `                if error_msg is None and token_type in {'++', '--'} and index > 0:` | Checks parser condition. |
| 2080 | `                    # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 2081 | `                    prev_index = index - 1` | Stores/updates parser state or response data. |
| 2082 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 2083 | `                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 2084 | `                        # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 2085 | `                        prev_index -= 1` | Stores/updates parser state or response data. |
| 2086 | `                    ` | Blank spacing line. |
| 2087 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2088 | `                    if prev_index >= 0:` | Checks parser condition. |
| 2089 | `                        # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 2090 | `                        prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 2091 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2092 | `                        if prev_tok.type in {'++', '--'}:` | Checks parser condition. |
| 2093 | `                            # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 2094 | `                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after '{prev_tok.value}'. Increment/decrement operators cannot be chained. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 2095 | `                ` | Blank spacing line. |
| 2096 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2097 | `                binary_operators = {'+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '\|\|'}` | Stores/updates parser state or response data. |
| 2098 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2099 | `                if error_msg is None and token_type in binary_operators and index > 0:` | Checks parser condition. |
| 2100 | `                    # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 2101 | `                    prev_index = index - 1` | Stores/updates parser state or response data. |
| 2102 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 2103 | `                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 2104 | `                        # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 2105 | `                        prev_index -= 1` | Stores/updates parser state or response data. |
| 2106 | `                    ` | Blank spacing line. |
| 2107 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2108 | `                    if prev_index >= 0:` | Checks parser condition. |
| 2109 | `                        # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 2110 | `                        prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 2111 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2112 | `                        if prev_tok.type in {'++', '--'}:` | Checks parser condition. |
| 2113 | `                            # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 2114 | `                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected binary operator '{token_value}' after unary operator '{prev_tok.value}'. Increment/decrement must be standalone statements. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 2115 | `                ` | Blank spacing line. |
| 2116 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2117 | `                if error_msg is None:` | Checks parser condition. |
| 2118 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2119 | `                    if index > 0:` | Checks parser condition. |
| 2120 | `                        # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 2121 | `                        prev_index = index - 1` | Stores/updates parser state or response data. |
| 2122 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 2123 | `                        while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 2124 | `                            # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 2125 | `                            prev_index -= 1` | Stores/updates parser state or response data. |
| 2126 | `                        ` | Blank spacing line. |
| 2127 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2128 | `                        if prev_index >= 0:` | Checks parser condition. |
| 2129 | `                            # AUTO: Sets `prev_tok`.` | Comment/guideline in the current parser file. |
| 2130 | `                            prev_tok = toks[prev_index]` | Stores/updates parser state or response data. |
| 2131 | `                            # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 2132 | `                            error_msg = f"SYNTAX error line {prev_tok.line} col {prev_tok.col + len(str(prev_tok.value))} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 2133 | `                            # AUTO: Sets `line`.` | Comment/guideline in the current parser file. |
| 2134 | `                            line = prev_tok.line` | Stores/updates parser state or response data. |
| 2135 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 2136 | `                        else:` | Fallback branch. |
| 2137 | `                            # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 2138 | `                            error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 2139 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 2140 | `                    else:` | Fallback branch. |
| 2141 | `                        # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 2142 | `                        error_msg = f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}'. {self._format_expected(expected)}"` | Stores/updates parser state or response data. |
| 2143 | `                ` | Blank spacing line. |
| 2144 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 2145 | `                return False, [error_msg]` | Returns syntax failure. |
| 2146 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current parser file. |
| 2147 | `            else:` | Fallback branch. |
| 2148 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2149 | `                if top == 'id' and token_type == '(' and index > 0:` | Checks parser condition. |
| 2150 | `                    # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 2151 | `                    prev_index = index - 1` | Stores/updates parser state or response data. |
| 2152 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 2153 | `                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 2154 | `                        # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 2155 | `                        prev_index -= 1` | Stores/updates parser state or response data. |
| 2156 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2157 | `                    if prev_index >= 0 and toks[prev_index].type == 'id':` | Checks parser condition. |
| 2158 | `                        # AUTO: Sets `kw_index`.` | Comment/guideline in the current parser file. |
| 2159 | `                        kw_index = prev_index - 1` | Stores/updates parser state or response data. |
| 2160 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 2161 | `                        while kw_index >= 0 and toks[kw_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 2162 | `                            # AUTO: Subtracts from `kw_index`.` | Comment/guideline in the current parser file. |
| 2163 | `                            kw_index -= 1` | Stores/updates parser state or response data. |
| 2164 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2165 | `                        if kw_index >= 0 and toks[kw_index].type == 'pollinate':` | Checks parser condition. |
| 2166 | `                            # AUTO: Sets `func_name`.` | Comment/guideline in the current parser file. |
| 2167 | `                            func_name = toks[prev_index].value` | Stores/updates parser state or response data. |
| 2168 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 2169 | `                            return False, [f"SYNTAX error line {toks[kw_index].line} col {toks[kw_index].col} Missing return type after 'pollinate'. '{func_name}' was parsed as the return type, not the function name. Expected: 'branch', 'empty', 'leaf', 'seed', 'tree', 'vine'"]` | Returns syntax failure. |
| 2170 | `` | Blank spacing line. |
| 2171 | `                # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2172 | `                if top == 'id' and token_type == ')' and index > 0:` | Checks parser condition. |
| 2173 | `                    # AUTO: Sets `prev_index`.` | Comment/guideline in the current parser file. |
| 2174 | `                    prev_index = index - 1` | Stores/updates parser state or response data. |
| 2175 | `                    # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 2176 | `                    while prev_index >= 0 and toks[prev_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 2177 | `                        # AUTO: Subtracts from `prev_index`.` | Comment/guideline in the current parser file. |
| 2178 | `                        prev_index -= 1` | Stores/updates parser state or response data. |
| 2179 | `                    # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2180 | `                    if prev_index >= 0 and toks[prev_index].type == 'id':` | Checks parser condition. |
| 2181 | `                        # AUTO: Sets `comma_index`.` | Comment/guideline in the current parser file. |
| 2182 | `                        comma_index = prev_index - 1` | Stores/updates parser state or response data. |
| 2183 | `                        # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 2184 | `                        while comma_index >= 0 and toks[comma_index].type in self.skip_token_types:` | Repeats while condition is true. |
| 2185 | `                            # AUTO: Subtracts from `comma_index`.` | Comment/guideline in the current parser file. |
| 2186 | `                            comma_index -= 1` | Stores/updates parser state or response data. |
| 2187 | `                        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2188 | `                        if comma_index >= 0 and toks[comma_index].type == ',':` | Checks parser condition. |
| 2189 | `                            # AUTO: Sets `param_name`.` | Comment/guideline in the current parser file. |
| 2190 | `                            param_name = toks[prev_index].value` | Stores/updates parser state or response data. |
| 2191 | `                            # AUTO: Sets `param_expected`.` | Comment/guideline in the current parser file. |
| 2192 | `                            param_expected = {'seed', 'tree', 'leaf', 'vine', 'branch'}` | Stores/updates parser state or response data. |
| 2193 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 2194 | `                            return False, [f"SYNTAX error line {toks[prev_index].line} col {toks[prev_index].col} Missing type for parameter '{param_name}'. Each parameter requires a type. {self._format_expected(param_expected)}"]` | Returns syntax failure. |
| 2195 | `` | Blank spacing line. |
| 2196 | `                # AUTO: Sets `error_msg`.` | Comment/guideline in the current parser file. |
| 2197 | `                error_msg = self._generate_helpful_error(` | Creates syntax error text. |
| 2198 | `                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2199 | `                    top, token_type, token_value, line, tok.col, expected, index, toks` | Parser support logic used during syntax checking. |
| 2200 | `                # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2201 | `                )` | Closes Python grouping/list/dict/call. |
| 2202 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 2203 | `                return False, [error_msg]` | Returns syntax failure. |
| 2204 | `` | Blank spacing line. |
| 2205 | `        # AUTO: Repeats while this condition is true.` | Comment/guideline in the current parser file. |
| 2206 | `        while index < len(toks) and toks[index].type in self.skip_token_types:` | Repeats while condition is true. |
| 2207 | `            # AUTO: Adds into `index`.` | Comment/guideline in the current parser file. |
| 2208 | `            index += 1` | Consumes current token. |
| 2209 | `        # AUTO: Checks this condition.` | Comment/guideline in the current parser file. |
| 2210 | `        if index < len(toks) and toks[index].type != self.end_marker:` | Checks parser condition. |
| 2211 | `            # AUTO: Sets `tok`.` | Comment/guideline in the current parser file. |
| 2212 | `            tok = toks[index]` | Stores/updates parser state or response data. |
| 2213 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 2214 | `            return False, [` | Returns syntax failure. |
| 2215 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2216 | `                f"SYNTAX error line {tok.line} col {tok.col} Unexpected token '{tok.value}' after program end. All code must be inside functions or global declarations. {self._format_expected({self.end_marker})}"` | Parser support logic used during syntax checking. |
| 2217 | `            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2218 | `            ]` | Closes Python grouping/list/dict/call. |
| 2219 | `        ` | Blank spacing line. |
| 2220 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 2221 | `        return True, []` | Returns syntax success. |
| 2222 | `` | Blank spacing line. |
| 2223 | `    # AUTO: Defines function `parse_and_build`.` | Comment/guideline in the current parser file. |
| 2224 | `    def parse_and_build(self, tokens: Sequence[Any]):` | Method starts: syntax check then AST build. |
| 2225 | `        # GUIDE: Public parser API used by server.py; syntax first, AST next.` | Comment/guideline in the current parser file. |
| 2226 | `        # LINE: Run LL(1) syntax validation before building AST.` | Comment/guideline in the current parser file. |
| 2227 | `        syntax_ok, syntax_errors = self.parse(tokens)` | Runs syntax validation. |
| 2228 | `        # LINE: If syntax failed, return errors and do not call builder.py.` | Comment/guideline in the current parser file. |
| 2229 | `        if not syntax_ok:` | Stops if syntax failed. |
| 2230 | `            # AUTO: Sets `first_err`.` | Comment/guideline in the current parser file. |
| 2231 | `            first_err = syntax_errors[0] if syntax_errors else ""` | Stores/updates parser state or response data. |
| 2232 | `            # LINE: Some parser checks intentionally return semantic-style messages.` | Comment/guideline in the current parser file. |
| 2233 | `            stage = "semantic" if first_err.startswith("SEMANTIC error") else "syntax"` | Stores/updates parser state or response data. |
| 2234 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current parser file. |
| 2235 | `            return {` | Returns value/result to caller. |
| 2236 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2237 | `                "success": False,` | Parser support logic used during syntax checking. |
| 2238 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2239 | `                "errors": syntax_errors,` | Parser support logic used during syntax checking. |
| 2240 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2241 | `                "ast": None,` | Parser support logic used during syntax checking. |
| 2242 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2243 | `                "symbol_table": {},` | Parser support logic used during syntax checking. |
| 2244 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2245 | `                "error_stage": stage,` | Parser support logic used during syntax checking. |
| 2246 | `            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2247 | `            }` | Closes Python grouping/list/dict/call. |
| 2248 | `` | Blank spacing line. |
| 2249 | `        # AUTO: Starts protected code that can catch errors.` | Comment/guideline in the current parser file. |
| 2250 | `        try:` | Starts protected block. |
| 2251 | `            # LINE: Remove comments/newlines because builder only needs meaningful tokens.` | Comment/guideline in the current parser file. |
| 2252 | `            filtered = [t for t in tokens if getattr(t, 'type', '') not in ('\n', 'comment', 'mcommentlit')]` | Removes comments/newlines for builder. |
| 2253 | `            # LINE: Convert the token stream into AST nodes.` | Comment/guideline in the current parser file. |
| 2254 | `            ast = _build_ast(filtered)` | Calls builder.py to build AST. |
| 2255 | `` | Blank spacing line. |
| 2256 | `            # LINE: Build frontend-friendly symbol table data from builder state.` | Comment/guideline in the current parser file. |
| 2257 | `            st = {` | Stores/updates parser state or response data. |
| 2258 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2259 | `                "variables": [` | Parser support logic used during syntax checking. |
| 2260 | `                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2261 | `                    {` | Parser support logic used during syntax checking. |
| 2262 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2263 | `                        "name": name,` | Parser support logic used during syntax checking. |
| 2264 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2265 | `                        "type": info["type"],` | Parser support logic used during syntax checking. |
| 2266 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2267 | `                        "scope": "global",` | Parser support logic used during syntax checking. |
| 2268 | `                        # AUTO: Calls `info.get`.` | Comment/guideline in the current parser file. |
| 2269 | `                        "is_list": info.get("is_list", False),` | Parser support logic used during syntax checking. |
| 2270 | `                        # AUTO: Calls `info.get`.` | Comment/guideline in the current parser file. |
| 2271 | `                        "is_constant": info.get("is_fertile", False),` | Parser support logic used during syntax checking. |
| 2272 | `                    # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2273 | `                    }` | Closes Python grouping/list/dict/call. |
| 2274 | `                    # AUTO: Starts a loop over these values.` | Comment/guideline in the current parser file. |
| 2275 | `                    for name, info in _builder_st.variables.items()` | Loops over items. |
| 2276 | `                # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2277 | `                ],` | Closes Python grouping/list/dict/call. |
| 2278 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2279 | `                "functions": {` | Parser support logic used during syntax checking. |
| 2280 | `                    # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2281 | `                    name: {` | Parser support logic used during syntax checking. |
| 2282 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2283 | `                        "return_type": info["return_type"],` | Parser support logic used during syntax checking. |
| 2284 | `                        # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2285 | `                        "params": [` | Parser support logic used during syntax checking. |
| 2286 | `                            # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2287 | `                            {` | Parser support logic used during syntax checking. |
| 2288 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2289 | `                                "type": p.children[0].value if p.children else "unknown",` | Parser support logic used during syntax checking. |
| 2290 | `                                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2291 | `                                "name": p.children[1].value if len(p.children) > 1 else "unknown",` | Parser support logic used during syntax checking. |
| 2292 | `                            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2293 | `                            }` | Closes Python grouping/list/dict/call. |
| 2294 | `                            # AUTO: Starts a loop over these values.` | Comment/guideline in the current parser file. |
| 2295 | `                            for p in info["params"]` | Loops over items. |
| 2296 | `                        # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2297 | `                        ] if info["params"] else [],` | Parser support logic used during syntax checking. |
| 2298 | `                    # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2299 | `                    }` | Closes Python grouping/list/dict/call. |
| 2300 | `                    # AUTO: Starts a loop over these values.` | Comment/guideline in the current parser file. |
| 2301 | `                    for name, info in _builder_st.functions.items()` | Loops over items. |
| 2302 | `                # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2303 | `                },` | Closes Python grouping/list/dict/call. |
| 2304 | `            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2305 | `            }` | Closes Python grouping/list/dict/call. |
| 2306 | `` | Blank spacing line. |
| 2307 | `            # LINE: Return AST and symbol table to semantic/interpreter stages.` | Comment/guideline in the current parser file. |
| 2308 | `            return {` | Returns value/result to caller. |
| 2309 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2310 | `                "success": True,` | Parser support logic used during syntax checking. |
| 2311 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2312 | `                "errors": [],` | Parser support logic used during syntax checking. |
| 2313 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2314 | `                "ast": ast,` | Parser support logic used during syntax checking. |
| 2315 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2316 | `                "symbol_table": st,` | Parser support logic used during syntax checking. |
| 2317 | `            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2318 | `            }` | Closes Python grouping/list/dict/call. |
| 2319 | `` | Blank spacing line. |
| 2320 | `        # AUTO: Handles the matching error case.` | Comment/guideline in the current parser file. |
| 2321 | `        except _SemanticError as e:` | Catches error. |
| 2322 | `            # LINE: Builder semantic errors are returned as semantic stage failures.` | Comment/guideline in the current parser file. |
| 2323 | `            return {` | Returns value/result to caller. |
| 2324 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2325 | `                "success": False,` | Parser support logic used during syntax checking. |
| 2326 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2327 | `                "errors": [str(e)],` | Parser support logic used during syntax checking. |
| 2328 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2329 | `                "ast": None,` | Parser support logic used during syntax checking. |
| 2330 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2331 | `                "symbol_table": {},` | Parser support logic used during syntax checking. |
| 2332 | `                # AUTO: Executes this statement.` | Comment/guideline in the current parser file. |
| 2333 | `                "error_stage": "semantic",` | Parser support logic used during syntax checking. |
| 2334 | `            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current parser file. |
| 2335 | `            }` | Closes Python grouping/list/dict/call. |