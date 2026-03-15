# ============================================================================
# GAL LANGUAGE – INTERMEDIATE CODE GENERATOR (ICG)
# ============================================================================
# Generates three-address code (TAC) from a GAL token stream.
#
# The output is a list of TAC instructions (quad-like) that can be further
# optimised or translated to target code.
#
# TAC instruction format:
#   (op, arg1, arg2, result)
#
# Examples:
#   ('+',  'a', 'b', 't0')     →  t0 = a + b
#   ('=',  '5', None, 'x')     →  x = 5
#   ('LABEL', None, None, 'L0') → L0:
#   ('IF',  't0', None, 'L1')   → if t0 goto L1
#   ('GOTO', None, None, 'L2')  → goto L2
#   ('PARAM', 'x', None, None)  → param x
#   ('CALL', 'func', '2', 't1') → t1 = call func, 2
#   ('RETURN', 'x', None, None) → return x
#   ('PRINT', 'x', None, None)  → print x
#   ('READ', None, None, 'x')   → read x
# ============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Token view helper (same normalisation used by the parser)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _Tok:
    type: str
    value: str
    line: int
    col: int = 0


def _as_tok(raw: Any) -> _Tok:
    """Normalise dict / object tokens into a uniform view."""
    if isinstance(raw, dict):
        return _Tok(
            type=str(raw.get("type", "")),
            value=str(raw.get("value", "")),
            line=int(raw.get("line", 0) or 0),
            col=int(raw.get("col", 0) or 0),
        )
    return _Tok(
        type=str(getattr(raw, "type", "")),
        value=str(getattr(raw, "value", "")),
        line=int(getattr(raw, "line", 0) or 0),
        col=int(getattr(raw, "col", 0) or 0),
    )


# ---------------------------------------------------------------------------
# Three-Address Code (TAC) instruction
# ---------------------------------------------------------------------------

@dataclass
class TACInstruction:
    """One three-address code quad."""
    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    result: Optional[str] = None

    def __str__(self) -> str:
        if self.op == "LABEL":
            return f"{self.result}:"
        if self.op == "GOTO":
            return f"goto {self.result}"
        if self.op == "IF":
            return f"if {self.arg1} goto {self.result}"
        if self.op == "IFFALSE":
            return f"ifFalse {self.arg1} goto {self.result}"
        if self.op == "PARAM":
            return f"param {self.arg1}"
        if self.op == "CALL":
            return f"{self.result} = call {self.arg1}, {self.arg2}"
        if self.op == "RETURN":
            return f"return {self.arg1 or ''}"
        if self.op == "PRINT":
            return f"print {self.arg1}"
        if self.op == "READ":
            return f"read {self.result}"
        if self.op == "FUNC":
            return f"func {self.arg1}:"
        if self.op == "ENDFUNC":
            return f"endfunc"
        if self.op == "DECLARE":
            return f"declare {self.result} : {self.arg1}"
        if self.op == "ARRAY_DECLARE":
            return f"declare {self.result}[{self.arg2}] : {self.arg1}"
        if self.op == "ARRAY_STORE":
            return f"{self.result}[{self.arg2}] = {self.arg1}"
        if self.op == "ARRAY_LOAD":
            return f"{self.result} = {self.arg1}[{self.arg2}]"
        if self.op == "STRUCT_STORE":
            return f"{self.arg1}.{self.arg2} = {self.result}"
        if self.op == "STRUCT_LOAD":
            return f"{self.result} = {self.arg1}.{self.arg2}"
        if self.op == "CONST":
            return f"const {self.result} : {self.arg1} = {self.arg2}"
        if self.op == "INC":
            return f"{self.arg1} = {self.arg1} + 1"
        if self.op == "DEC":
            return f"{self.arg1} = {self.arg1} - 1"
        # Binary / unary arithmetic & assignment
        if self.arg2 is not None:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        if self.op == "=":
            return f"{self.result} = {self.arg1}"
        if self.op == "UNARY_MINUS":
            return f"{self.result} = -{self.arg1}"
        if self.op == "NOT":
            return f"{self.result} = !{self.arg1}"
        return f"{self.op} {self.arg1 or ''} {self.arg2 or ''} {self.result or ''}".strip()

    def to_dict(self) -> dict:
        return {
            "op": self.op,
            "arg1": self.arg1,
            "arg2": self.arg2,
            "result": self.result,
            "text": str(self),
        }


# ---------------------------------------------------------------------------
# GAL type map
# ---------------------------------------------------------------------------
GAL_TYPE_MAP = {
    "seed": "int",
    "tree": "float",
    "leaf": "char",
    "branch": "bool",
    "vine": "string",
    "empty": "void",
}

DATA_TYPE_TOKENS = set(GAL_TYPE_MAP.keys())

ASSIGN_OPS = {"=", "+=", "-=", "*=", "/=", "%="}


# ---------------------------------------------------------------------------
# Intermediate Code Generator
# ---------------------------------------------------------------------------

class ICGenerator:
    """Generates three-address code from a GAL token stream."""

    def __init__(self, tokens: List[Any]):
        self.tokens: List[_Tok] = self._prepare(tokens)
        self.pos: int = 0               # current position in token stream
        self.code: List[TACInstruction] = []  # generated TAC
        self.errors: List[str] = []
        self._temp_counter: int = 0
        self._label_counter: int = 0

    # -- helpers ------------------------------------------------------------

    def _prepare(self, raw_tokens: List[Any]) -> List[_Tok]:
        """Normalise and filter (skip newlines)."""
        toks: List[_Tok] = []
        for t in raw_tokens:
            tv = _as_tok(t)
            if tv.type == "\n":
                continue
            toks.append(tv)
        # Ensure EOF
        if not toks or toks[-1].type != "EOF":
            last_line = toks[-1].line if toks else 1
            toks.append(_Tok("EOF", "EOF", last_line))
        return toks

    def _peek(self) -> _Tok:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return _Tok("EOF", "EOF", 0)

    def _advance(self) -> _Tok:
        tok = self._peek()
        if self.pos < len(self.tokens):
            self.pos += 1
        return tok

    def _expect(self, token_type: str) -> _Tok:
        tok = self._peek()
        if tok.type != token_type:
            self.errors.append(
                f"ICG Line {tok.line}: expected '{token_type}', got '{tok.type}'"
            )
            # try to continue anyway
            return tok
        return self._advance()

    def _match(self, token_type: str) -> bool:
        """If current token matches, consume and return True."""
        if self._peek().type == token_type:
            self._advance()
            return True
        return False

    def _new_temp(self) -> str:
        name = f"t{self._temp_counter}"
        self._temp_counter += 1
        return name

    def _new_label(self) -> str:
        name = f"L{self._label_counter}"
        self._label_counter += 1
        return name

    def _emit(self, op: str, arg1: Optional[str] = None,
              arg2: Optional[str] = None, result: Optional[str] = None):
        self.code.append(TACInstruction(op, arg1, arg2, result))

    def _is_data_type(self, tok: _Tok) -> bool:
        return tok.type in DATA_TYPE_TOKENS

    # ======================================================================
    # TOP-LEVEL: <program>
    # ======================================================================

    def generate(self) -> Tuple[List[TACInstruction], List[str]]:
        """Entry point — generate TAC for the whole program."""
        try:
            self._program()
        except Exception as exc:
            self.errors.append(f"ICG internal error: {exc}")
        return self.code, self.errors

    def _program(self):
        """<program> -> <global_declaration> <function_definition> root ( ) { <declaration> <statement> reclaim ; }"""
        self._global_declaration()
        self._function_definition()

        # root ( ) { ... }
        self._expect("root")
        self._expect("(")
        self._expect(")")
        self._expect("{")
        self._emit("FUNC", "root")

        self._declaration()
        self._statement()

        # reclaim ;
        if self._peek().type == "reclaim":
            self._advance()
            if self._peek().type != ";":
                val = self._expression()
                self._emit("RETURN", val)
            else:
                self._emit("RETURN")
            self._expect(";")

        self._expect("}")
        self._emit("ENDFUNC")

    # ======================================================================
    # GLOBAL DECLARATIONS
    # ======================================================================

    def _global_declaration(self):
        """<global_declaration> → bundle id ... | <data_type> id ... | fertile ... | λ"""
        while True:
            tok = self._peek()
            if tok.type == "bundle":
                self._advance()  # bundle
                name_tok = self._expect("id")
                nxt = self._peek()
                if nxt.type == "{":
                    # bundle definition: bundle Id { members }
                    self._advance()  # {
                    self._bundle_members()
                    self._expect("}")
                else:
                    # bundle variable: bundle Id varName ... ;
                    self._bundle_mem_dec()
                    self._expect(";")
                self._global_declaration()
                return

            elif self._is_data_type(tok):
                dtype = self._advance()  # data type
                id_tok = self._expect("id")
                arr_dims = self._array_dec()
                if arr_dims:
                    for dim in arr_dims:
                        self._emit("ARRAY_DECLARE", GAL_TYPE_MAP.get(dtype.type, dtype.type),
                                   dim, id_tok.value)
                else:
                    self._emit("DECLARE", GAL_TYPE_MAP.get(dtype.type, dtype.type),
                               None, id_tok.value)
                self._var_value(id_tok.value)
                self._expect(";")
                self._global_declaration()
                return

            elif tok.type == "fertile":
                self._const_dec()
                self._expect(";")
                self._global_declaration()
                return

            else:
                # λ — no more global declarations
                return

    # ======================================================================
    # LOCAL DECLARATIONS
    # ======================================================================

    def _declaration(self):
        """<declaration> → <var_dec> ; <declaration> | <const_dec> ; <declaration> | λ"""
        while True:
            tok = self._peek()
            if self._is_data_type(tok) or tok.type == "bundle":
                self._var_dec()
                self._expect(";")
            elif tok.type == "fertile":
                self._const_dec()
                self._expect(";")
            else:
                break

    def _var_dec(self):
        """<var_dec> → <data_type> id <array_dec> <var_value> | bundle id <bundle_mem_dec>"""
        tok = self._peek()
        if tok.type == "bundle":
            self._advance()
            id_tok = self._expect("id")
            self._bundle_mem_dec()
            return

        dtype = self._advance()  # data type keyword
        id_tok = self._expect("id")
        arr_dims = self._array_dec()
        if arr_dims:
            for dim in arr_dims:
                self._emit("ARRAY_DECLARE", GAL_TYPE_MAP.get(dtype.type, dtype.type),
                           dim, id_tok.value)
        else:
            self._emit("DECLARE", GAL_TYPE_MAP.get(dtype.type, dtype.type), None, id_tok.value)
        self._var_value(id_tok.value)

    def _const_dec(self):
        """fertile <data_type> id = <init_val> <const_next>"""
        self._expect("fertile")
        dtype = self._advance()  # data type
        id_tok = self._expect("id")
        self._expect("=")
        val = self._init_val()
        self._emit("CONST", GAL_TYPE_MAP.get(dtype.type, dtype.type), val, id_tok.value)
        self._const_next(dtype)

    def _const_next(self, dtype_tok: _Tok):
        """<const_next> → , id = <init_val> <const_next> | λ"""
        while self._match(","):
            id_tok = self._expect("id")
            self._expect("=")
            val = self._init_val()
            self._emit("CONST", GAL_TYPE_MAP.get(dtype_tok.type, dtype_tok.type), val, id_tok.value)

    def _var_value(self, var_name: str):
        """<var_value> → = <init_val> <var_value_next> | <var_value_next>"""
        if self._peek().type == "=":
            self._advance()  # =
            val = self._init_val()
            self._emit("=", val, None, var_name)
            self._var_value_next()
        else:
            self._var_value_next()

    def _var_value_next(self):
        """<var_value_next> → , id <array_dec> <var_value> | λ"""
        if self._match(","):
            id_tok = self._expect("id")
            arr_dims = self._array_dec()
            if arr_dims:
                for dim in arr_dims:
                    self._emit("ARRAY_DECLARE", "int", dim, id_tok.value)
            else:
                self._emit("DECLARE", "int", None, id_tok.value)
            self._var_value(id_tok.value)

    def _init_val(self) -> str:
        """<init_val> → <array_init_opt> | <expression>"""
        if self._peek().type == "{":
            return self._array_init()
        return self._expression()

    def _array_init(self) -> str:
        """{ <init_vals> }  — emit element-by-element stores, return temp."""
        self._expect("{")
        tmp = self._new_temp()
        idx = 0
        if self._peek().type != "}":
            val = self._init_val_item()
            self._emit("ARRAY_STORE", val, str(idx), tmp)
            idx += 1
            while self._match(","):
                val = self._init_val_item()
                self._emit("ARRAY_STORE", val, str(idx), tmp)
                idx += 1
        self._expect("}")
        return tmp

    def _init_val_item(self) -> str:
        if self._peek().type == "{":
            return self._array_init()
        return self._expression()

    # ======================================================================
    # ARRAY & STRUCT HELPERS
    # ======================================================================

    def _array_dec(self) -> List[str]:
        """<array_dec> → [ <array_dim_opt> ] <array_dec> | λ  — returns list of dimension sizes."""
        dims: List[str] = []
        while self._peek().type == "[":
            self._advance()  # [
            if self._peek().type == "intlit":
                dims.append(self._advance().value)
            else:
                dims.append("0")  # dynamic / unspecified
            self._expect("]")
        return dims

    def _bundle_members(self):
        """<bundle_members> → <data_type> id ; <bundle_members> | λ"""
        while self._is_data_type(self._peek()):
            dtype = self._advance()
            id_tok = self._expect("id")
            self._expect(";")

    def _bundle_mem_dec(self):
        """<bundle_mem_dec> → id <var_value_next> | , id <var_value_next> | λ"""
        tok = self._peek()
        if tok.type == "id":
            id_tok = self._advance()
            self._emit("DECLARE", "bundle", None, id_tok.value)
            self._var_value_next_simple()
        elif tok.type == ",":
            self._advance()
            id_tok = self._expect("id")
            self._emit("DECLARE", "bundle", None, id_tok.value)
            self._var_value_next_simple()

    def _var_value_next_simple(self):
        while self._match(","):
            id_tok = self._expect("id")
            self._emit("DECLARE", "bundle", None, id_tok.value)

    # ======================================================================
    # FUNCTION DEFINITIONS
    # ======================================================================

    def _function_definition(self):
        """<function_definition> → pollinate <return_type> id ( <parameters> ) { ... } <function_definition> | λ"""
        while self._peek().type == "pollinate":
            self._advance()  # pollinate

            # return type
            if self._peek().type == "empty":
                ret_type = self._advance().type
            elif self._is_data_type(self._peek()):
                ret_type = self._advance().type
            elif self._peek().type == "id":
                # User-defined bundle type as return type
                ret_type = self._advance().value
            else:
                ret_type = "void"

            func_name = self._expect("id")
            self._expect("(")

            # parameters
            params = self._parameters()

            self._expect(")")
            self._expect("{")

            self._emit("FUNC", func_name.value)
            for ptype, pname in params:
                self._emit("DECLARE", GAL_TYPE_MAP.get(ptype, ptype), None, pname)

            self._declaration()
            self._statement()

            # optional reclaim
            if self._peek().type == "reclaim":
                self._advance()
                if self._peek().type == ";":
                    self._emit("RETURN")
                else:
                    val = self._expression()
                    self._emit("RETURN", val)
                self._expect(";")

            self._expect("}")
            self._emit("ENDFUNC")

    def _parameters(self) -> List[Tuple[str, str]]:
        """<parameters> → <param> <param_next> | λ"""
        params: List[Tuple[str, str]] = []
        if self._is_data_type(self._peek()) or self._peek().type == "id":
            p = self._param()
            params.append(p)
            while self._match(","):
                p = self._param()
                params.append(p)
        return params

    def _param(self) -> Tuple[str, str]:
        dtype = self._advance()
        id_tok = self._expect("id")
        # For bundle types, dtype.type is "id" — use dtype.value to get the actual type name
        type_name = dtype.value if dtype.type == "id" else dtype.type
        return (type_name, id_tok.value)

    # ======================================================================
    # STATEMENTS
    # ======================================================================

    def _statement(self):
        """<statement> → <simple_stmt> <statement> | λ
        Also handles inline declarations gracefully for robustness."""
        while self._peek().type not in ("}", "EOF", "reclaim", "variety", "soil", "prune"):
            tok = self._peek()
            # Handle inline variable declarations (data types appearing mid-block)
            if self._is_data_type(tok) or tok.type == "bundle" or tok.type == "fertile":
                if tok.type == "fertile":
                    self._const_dec()
                    self._expect(";")
                else:
                    self._var_dec()
                    self._expect(";")
                continue
            self._simple_stmt()

    def _simple_stmt(self):
        """Dispatch on the first token."""
        tok = self._peek()

        if tok.type == "id":
            self._id_stmt()
        elif tok.type in ("water", "plant"):
            self._io_stmt()
        elif tok.type == "spring":
            self._conditional_stmt()
        elif tok.type in ("grow", "cultivate", "tend"):
            self._loop_stmt()
        elif tok.type == "harvest":
            self._switch_stmt()
        elif tok.type in ("prune", "skip"):
            self._control_stmt()
        else:
            # Skip unknown token to avoid infinite loop
            self.errors.append(f"ICG Line {tok.line}: unexpected token '{tok.type}'")
            self._advance()

    # -- id statement -------------------------------------------------------

    def _id_stmt(self):
        """id <id_next> <assign_op> <expression> ;  |  id <inc_dec_op> ;  |  id ( <arguments> ) ;"""
        id_tok = self._advance()  # id
        tok = self._peek()

        # Function call
        if tok.type == "(":
            self._advance()  # (
            args = self._arguments()
            self._expect(")")
            self._expect(";")
            for a in args:
                self._emit("PARAM", a)
            tmp = self._new_temp()
            self._emit("CALL", id_tok.value, str(len(args)), tmp)
            return

        # Increment / decrement
        if tok.type in ("++", "--"):
            op_tok = self._advance()
            self._expect(";")
            self._emit("INC" if op_tok.type == "++" else "DEC", id_tok.value)
            return

        # Assignment (possibly with array / struct access on LHS)
        lhs = id_tok.value
        lhs = self._resolve_lhs(lhs)

        # Assign op
        if self._peek().type in ASSIGN_OPS:
            op_tok = self._advance()
            rhs = self._expression()
            self._expect(";")

            if op_tok.type == "=":
                self._emit("=", rhs, None, lhs)
            else:
                # compound assignment: x += e  →  x = x + e
                base_op = op_tok.type[0]  # +, -, *, /, %
                tmp = self._new_temp()
                self._emit(base_op, lhs, rhs, tmp)
                self._emit("=", tmp, None, lhs)
        else:
            # If it doesn't look like anything valid, skip to ;
            self.errors.append(f"ICG Line {tok.line}: unexpected token after id '{id_tok.value}'")
            while self._peek().type not in (";", "}", "EOF"):
                self._advance()
            self._match(";")

    def _resolve_lhs(self, base: str) -> str:
        """Handle array access [expr] or struct access .id after an identifier for LHS."""
        tok = self._peek()
        if tok.type == "[":
            # array access
            self._advance()
            idx = self._expression()
            self._expect("]")
            # possibly multi-dimensional
            while self._peek().type == "[":
                self._advance()
                idx2 = self._expression()
                self._expect("]")
                tmp = self._new_temp()
                self._emit("*", idx, idx2, tmp)
                idx = tmp
            return f"{base}[{idx}]"
        elif tok.type == ".":
            self._advance()
            member = self._expect("id")
            # Possibly nested
            chain = f"{base}.{member.value}"
            while self._peek().type == ".":
                self._advance()
                m2 = self._expect("id")
                chain = f"{chain}.{m2.value}"
            return chain
        return base

    # -- I/O ---------------------------------------------------------------

    def _io_stmt(self):
        """water ( args ) ;  |  plant ( args ) ;"""
        io_tok = self._advance()  # water / plant
        self._expect("(")
        args = self._arguments()
        self._expect(")")
        self._expect(";")

        if io_tok.type == "plant":
            for a in args:
                self._emit("PRINT", a)
        else:  # water
            for a in args:
                self._emit("READ", None, None, a)

    # -- conditional --------------------------------------------------------

    def _conditional_stmt(self):
        """spring ( <expr> ) { <stmt> } <elseif_chain> <else_opt>"""
        self._expect("spring")
        self._expect("(")
        cond = self._expression()
        self._expect(")")

        false_label = self._new_label()
        end_label = self._new_label()

        self._emit("IFFALSE", cond, None, false_label)

        self._expect("{")
        self._statement()
        self._expect("}")

        self._emit("GOTO", None, None, end_label)
        self._emit("LABEL", None, None, false_label)

        # elseif chain
        self._elseif_chain(end_label)

        # else opt
        if self._peek().type == "wither":
            self._advance()
            self._expect("{")
            self._statement()
            self._expect("}")

        self._emit("LABEL", None, None, end_label)

    def _elseif_chain(self, end_label: str):
        """bud ( <expr> ) { <stmt> } <elseif_chain>"""
        while self._peek().type == "bud":
            self._advance()  # bud
            self._expect("(")
            cond = self._expression()
            self._expect(")")

            next_label = self._new_label()
            self._emit("IFFALSE", cond, None, next_label)

            self._expect("{")
            self._statement()
            self._expect("}")

            self._emit("GOTO", None, None, end_label)
            self._emit("LABEL", None, None, next_label)

    # -- loops --------------------------------------------------------------

    def _loop_stmt(self):
        tok = self._peek()
        if tok.type == "grow":
            self._while_loop()
        elif tok.type == "cultivate":
            self._for_loop()
        elif tok.type == "tend":
            self._do_while_loop()

    def _while_loop(self):
        """grow ( <expr> ) { <stmt> }"""
        self._expect("grow")
        self._expect("(")

        start_label = self._new_label()
        end_label = self._new_label()

        self._emit("LABEL", None, None, start_label)
        cond = self._expression()
        self._expect(")")

        self._emit("IFFALSE", cond, None, end_label)

        self._expect("{")
        self._statement()
        self._expect("}")

        self._emit("GOTO", None, None, start_label)
        self._emit("LABEL", None, None, end_label)

    def _for_loop(self):
        """cultivate ( <for_init> ; <expr> ; <for_update> ) { <stmt> }"""
        self._expect("cultivate")
        self._expect("(")

        # init
        self._for_init()
        self._expect(";")

        start_label = self._new_label()
        end_label = self._new_label()
        update_label = self._new_label()

        self._emit("LABEL", None, None, start_label)

        # condition
        cond = self._expression()
        self._emit("IFFALSE", cond, None, end_label)

        self._expect(";")

        # save update position — we need to emit update *after* body
        update_instrs: List[TACInstruction] = []
        saved_code = self.code
        self.code = update_instrs
        self._for_update()
        self.code = saved_code

        self._expect(")")
        self._expect("{")
        self._statement()
        self._expect("}")

        # emit update
        self._emit("LABEL", None, None, update_label)
        self.code.extend(update_instrs)
        self._emit("GOTO", None, None, start_label)
        self._emit("LABEL", None, None, end_label)

    def _for_init(self):
        """<for_init> → <data_type> id <array_dec> <var_value> | id <id_next> <assign_op> <expression> | λ"""
        tok = self._peek()
        if self._is_data_type(tok):
            self._var_dec()
        elif tok.type == "id":
            id_tok = self._advance()
            lhs = self._resolve_lhs(id_tok.value)
            if self._peek().type in ASSIGN_OPS:
                op_tok = self._advance()
                rhs = self._expression()
                if op_tok.type == "=":
                    self._emit("=", rhs, None, lhs)
                else:
                    base_op = op_tok.type[0]
                    tmp = self._new_temp()
                    self._emit(base_op, lhs, rhs, tmp)
                    self._emit("=", tmp, None, lhs)
        # else: λ

    def _for_update(self):
        """<for_update> → id <for_update_type> | λ"""
        if self._peek().type == "id":
            id_tok = self._advance()
            tok = self._peek()
            if tok.type in ("++", "--"):
                op = self._advance()
                self._emit("INC" if op.type == "++" else "DEC", id_tok.value)
            else:
                lhs = self._resolve_lhs(id_tok.value)
                if self._peek().type in ASSIGN_OPS:
                    op_tok = self._advance()
                    rhs = self._expression()
                    if op_tok.type == "=":
                        self._emit("=", rhs, None, lhs)
                    else:
                        base_op = op_tok.type[0]
                        tmp = self._new_temp()
                        self._emit(base_op, lhs, rhs, tmp)
                        self._emit("=", tmp, None, lhs)

    def _do_while_loop(self):
        """tend { <stmt> } grow ( <expr> ) ;"""
        self._expect("tend")
        self._expect("{")

        start_label = self._new_label()
        self._emit("LABEL", None, None, start_label)

        self._statement()
        self._expect("}")

        self._expect("grow")
        self._expect("(")
        cond = self._expression()
        self._expect(")")
        self._expect(";")

        self._emit("IF", cond, None, start_label)

    # -- switch -------------------------------------------------------------

    def _switch_stmt(self):
        """harvest ( <expr> ) { <case_list> <default_opt> }"""
        self._expect("harvest")
        self._expect("(")
        expr = self._expression()
        self._expect(")")
        self._expect("{")

        end_label = self._new_label()
        self._case_list(expr, end_label)
        self._default_opt(end_label)

        self._expect("}")
        self._emit("LABEL", None, None, end_label)

    def _case_list(self, switch_expr: str, end_label: str):
        """variety <expr> : <case_statements> prune ; <case_list> | λ"""
        while self._peek().type == "variety":
            self._advance()  # variety
            case_val = self._expression()
            self._expect(":")

            next_label = self._new_label()
            body_label = self._new_label()
            cmp_tmp = self._new_temp()

            self._emit("==", switch_expr, case_val, cmp_tmp)
            self._emit("IFFALSE", cmp_tmp, None, next_label)
            self._emit("LABEL", None, None, body_label)

            # case body statements
            self._case_statements()

            # prune ;
            if self._peek().type == "prune":
                self._advance()
                self._expect(";")

            self._emit("GOTO", None, None, end_label)
            self._emit("LABEL", None, None, next_label)

    def _case_statements(self):
        """<case_statements> → <case_statement> <case_statements> | λ"""
        while self._peek().type not in ("variety", "soil", "}", "prune", "EOF"):
            tok = self._peek()
            if tok.type == "id":
                self._id_stmt()
            elif tok.type == "water":
                self._io_stmt()
            elif tok.type == "plant":
                self._io_stmt()
            elif tok.type == "skip":
                self._advance()
                self._expect(";")
                # skip = continue, emit as nop in switch context
            else:
                break

    def _default_opt(self, end_label: str):
        """soil : <case_statements> | λ"""
        if self._peek().type == "soil":
            self._advance()
            self._expect(":")
            self._case_statements()

    # -- control (break, continue) ------------------------------------------

    def _control_stmt(self):
        tok = self._advance()  # prune or skip
        self._expect(";")
        if tok.type == "prune":
            self._emit("GOTO", None, None, "BREAK")   # placeholder; real label resolved later
        else:
            self._emit("GOTO", None, None, "CONTINUE")

    # ======================================================================
    # EXPRESSIONS  (precedence climbing, matching the CFG)
    # ======================================================================

    def _expression(self) -> str:
        """<expression> → <logic_or>"""
        return self._logic_or()

    def _logic_or(self) -> str:
        """<logic_or> → <logic_and> <logic_or_next>"""
        left = self._logic_and()
        while self._peek().type == "||":
            self._advance()
            right = self._logic_and()
            tmp = self._new_temp()
            self._emit("||", left, right, tmp)
            left = tmp
        return left

    def _logic_and(self) -> str:
        """<logic_and> → <relational> <logic_and_next>"""
        left = self._relational()
        while self._peek().type == "&&":
            self._advance()
            right = self._relational()
            tmp = self._new_temp()
            self._emit("&&", left, right, tmp)
            left = tmp
        return left

    def _relational(self) -> str:
        """<relational> → <arithmetic> <relational_next>"""
        left = self._arithmetic()
        if self._peek().type in (">", "<", ">=", "<=", "==", "!="):
            op = self._advance().type
            right = self._arithmetic()
            tmp = self._new_temp()
            self._emit(op, left, right, tmp)
            return tmp
        return left

    def _arithmetic(self) -> str:
        """<arithmetic> → <term> <arithmetic_next>"""
        left = self._term()
        while self._peek().type in ("+", "-"):
            op = self._advance().type
            right = self._term()
            tmp = self._new_temp()
            self._emit(op, left, right, tmp)
            left = tmp
        return left

    def _term(self) -> str:
        """<term> → <factor> <term_next>"""
        left = self._factor()
        while self._peek().type in ("*", "/", "%"):
            op = self._advance().type
            right = self._factor()
            tmp = self._new_temp()
            self._emit(op, left, right, tmp)
            left = tmp
        return left

    def _factor(self) -> str:
        """<factor> → ( <expr> ) | <unary_op> <factor> | id ... | literal"""
        tok = self._peek()

        # ( expression )
        if tok.type == "(":
            self._advance()
            val = self._expression()
            self._expect(")")
            return val

        # Unary: ~ or !
        if tok.type in ("~", "!"):
            op = self._advance()
            inner = self._factor()
            tmp = self._new_temp()
            if op.type == "~":
                self._emit("UNARY_MINUS", inner, None, tmp)
            else:
                self._emit("NOT", inner, None, tmp)
            return tmp

        # Identifier (variable, array, struct, or function call)
        if tok.type == "id":
            id_tok = self._advance()
            nxt = self._peek()

            # Function call in expression
            if nxt.type == "(":
                self._advance()
                args = self._arguments()
                self._expect(")")
                for a in args:
                    self._emit("PARAM", a)
                tmp = self._new_temp()
                self._emit("CALL", id_tok.value, str(len(args)), tmp)
                return tmp

            # Array access
            if nxt.type == "[":
                self._advance()
                idx = self._expression()
                self._expect("]")
                # multi-dim
                while self._peek().type == "[":
                    self._advance()
                    idx2 = self._expression()
                    self._expect("]")
                    tmp = self._new_temp()
                    self._emit("*", idx, idx2, tmp)
                    idx = tmp
                tmp = self._new_temp()
                self._emit("ARRAY_LOAD", id_tok.value, idx, tmp)
                return tmp

            # Struct access
            if nxt.type == ".":
                self._advance()
                member = self._expect("id")
                chain = member.value
                while self._peek().type == ".":
                    self._advance()
                    m2 = self._expect("id")
                    chain = f"{chain}.{m2.value}"
                tmp = self._new_temp()
                self._emit("STRUCT_LOAD", id_tok.value, chain, tmp)
                return tmp

            # Simple variable
            return id_tok.value

        # Literals
        if tok.type == "intlit":
            return self._advance().value
        if tok.type == "dblit":
            return self._advance().value
        if tok.type == "chrlit":
            return self._advance().value
        if tok.type == "stringlit":
            return self._advance().value
        if tok.type == "sunshine":
            self._advance()
            return "true"
        if tok.type == "frost":
            self._advance()
            return "false"

        # Fallback
        self.errors.append(f"ICG Line {tok.line}: unexpected token in expression: '{tok.type}'")
        self._advance()
        return "???"

    # -- arguments ----------------------------------------------------------

    def _arguments(self) -> List[str]:
        """<arguments> → <expression> <arg_next> | λ"""
        args: List[str] = []
        if self._peek().type in (")", "EOF"):
            return args
        args.append(self._expression())
        while self._match(","):
            args.append(self._expression())
        return args


# ===========================================================================
# Public API
# ===========================================================================

def generate_icg(tokens: List[Any]) -> Dict[str, Any]:
    """
    Main entry point for intermediate code generation.
    Returns a dict with:
      - 'success': bool
      - 'tac': list of TAC instruction dicts
      - 'tac_text': human-readable TAC string
      - 'errors': list of error strings
    """
    gen = ICGenerator(tokens)
    code, errors = gen.generate()

    tac_dicts = [instr.to_dict() for instr in code]
    tac_text = "\n".join(str(instr) for instr in code)

    return {
        "success": len(errors) == 0,
        "tac": tac_dicts,
        "tac_text": tac_text,
        "errors": errors,
    }
