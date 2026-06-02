from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class _Tok:
    type: str
    value: str
    line: int
    col: int = 0


def _as_tok(raw: Any) -> _Tok:
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


@dataclass
class TACInstruction:
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


class ICGenerator:

    def __init__(self, tokens: List[Any]):
        self.tokens: List[_Tok] = self._prepare(tokens)
        self.pos: int = 0
        self.code: List[TACInstruction] = []
        self.errors: List[str] = []
        self._temp_counter: int = 0
        self._label_counter: int = 0


    def _prepare(self, raw_tokens: List[Any]) -> List[_Tok]:
        toks: List[_Tok] = []
        for t in raw_tokens:
            tv = _as_tok(t)
            if tv.type in ("\n", "comment", "mcommentlit"):
                continue
            toks.append(tv)
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
            return tok
        return self._advance()

    def _match(self, token_type: str) -> bool:
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


    def generate(self) -> Tuple[List[TACInstruction], List[str]]:
        try:
            self._program()
        except Exception as exc:
            self.errors.append(f"ICG internal error: {exc}")
        return self.code, self.errors

    def _program(self):
        self._global_declaration()
        self._function_definition()

        self._expect("root")
        self._expect("(")
        self._expect(")")
        self._expect("{")
        self._emit("FUNC", "root")

        self._declaration()
        self._statement()

        self._expect("reclaim")
        self._expect(";")
        self._emit("RETURN")

        self._expect("}")
        self._emit("ENDFUNC")


    def _global_declaration(self):
        while True:
            tok = self._peek()
            if tok.type == "bundle":
                self._advance()
                name_tok = self._expect("id")
                nxt = self._peek()
                if nxt.type == "{":
                    self._advance()
                    self._bundle_members()
                    self._expect("}")
                    self._expect(";")
                else:
                    self._bundle_mem_dec()
                    self._expect(";")
                self._global_declaration()
                return

            elif self._is_data_type(tok):
                dtype = self._advance()
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
                return


    def _declaration(self):
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
        tok = self._peek()
        if tok.type == "bundle":
            self._advance()
            id_tok = self._expect("id")
            self._bundle_mem_dec()
            return

        dtype = self._advance()
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
        self._expect("fertile")
        dtype = self._advance()
        id_tok = self._expect("id")
        self._expect("=")
        val = self._init_val()
        self._emit("CONST", GAL_TYPE_MAP.get(dtype.type, dtype.type), val, id_tok.value)
        self._const_next(dtype)

    def _const_next(self, dtype_tok: _Tok):
        while self._match(","):
            id_tok = self._expect("id")
            self._expect("=")
            val = self._init_val()
            self._emit("CONST", GAL_TYPE_MAP.get(dtype_tok.type, dtype_tok.type), val, id_tok.value)

    def _var_value(self, var_name: str):
        if self._peek().type == "=":
            self._advance()
            val = self._init_val()
            self._emit("=", val, None, var_name)
            self._var_value_next()
        else:
            self._var_value_next()

    def _var_value_next(self):
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
        if self._peek().type == "{":
            return self._array_init()
        return self._expression()

    def _array_init(self) -> str:
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


    def _array_dec(self) -> List[str]:
        dims: List[str] = []
        while self._peek().type == "[":
            self._advance()
            if self._peek().type == "intlit":
                dims.append(self._advance().value)
            else:
                dims.append("0")
            self._expect("]")
        return dims

    def _bundle_members(self):
        while self._is_data_type(self._peek()):
            dtype = self._advance()
            id_tok = self._expect("id")
            self._expect(";")

    def _bundle_mem_dec(self):
        id_tok = self._expect("id")
        arr_dims = self._array_dec()
        if arr_dims:
            for dim in arr_dims:
                self._emit("ARRAY_DECLARE", "bundle", dim, id_tok.value)
        else:
            self._emit("DECLARE", "bundle", None, id_tok.value)


    def _function_definition(self):
        while self._peek().type == "pollinate":
            self._advance()

            if self._peek().type == "empty":
                ret_type = self._advance().type
            elif self._is_data_type(self._peek()):
                ret_type = self._advance().type
            elif self._peek().type == "id":
                ret_type = self._advance().value
            else:
                ret_type = "void"

            func_name = self._expect("id")
            self._expect("(")

            params = self._parameters()

            self._expect(")")
            self._expect("{")

            self._emit("FUNC", func_name.value)
            for ptype, pname, *rest in params:
                is_array = rest[0] if rest else False
                if is_array:
                    self._emit("ARRAY_DECLARE", GAL_TYPE_MAP.get(ptype, ptype), "param", pname)
                else:
                    self._emit("DECLARE", GAL_TYPE_MAP.get(ptype, ptype), None, pname)

            self._declaration()
            self._statement()

            self._expect("reclaim")
            if self._peek().type == ";":
                self._emit("RETURN")
            else:
                val = self._expression()
                self._emit("RETURN", val)
            self._expect(";")

            self._expect("}")
            self._emit("ENDFUNC")

    def _parameters(self):
        params = []
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
        type_name = dtype.value if dtype.type == "id" else dtype.type
        is_array = False
        if self._peek().type == "[":
            self._advance()
            self._expect("]")
            is_array = True
        return (type_name, id_tok.value, is_array)


    def _statement(self, allow_reclaim: bool = False):
        stopping_tokens = {"}", "EOF", "variety", "soil", "prune"}
        while self._peek().type not in stopping_tokens:
            tok = self._peek()
            if tok.type == "reclaim":
                if not allow_reclaim:
                    return
                self._return_stmt()
                continue
            if self._is_data_type(tok) or tok.type == "bundle" or tok.type == "fertile":
                if tok.type == "fertile":
                    self._const_dec()
                    self._expect(";")
                else:
                    self._var_dec()
                    self._expect(";")
                continue
            self._simple_stmt()

    def _return_stmt(self):
        self._expect("reclaim")
        if self._peek().type == ";":
            self._emit("RETURN")
        else:
            self._emit("RETURN", self._expression())
        self._expect(";")

    def _simple_stmt(self):
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
            self.errors.append(f"ICG Line {tok.line}: unexpected token '{tok.type}'")
            self._advance()


    def _id_stmt(self):
        id_tok = self._advance()
        tok = self._peek()

        if tok.type == "(":
            self._advance()
            args = self._arguments()
            self._expect(")")
            self._expect(";")
            for a in args:
                self._emit("PARAM", a)
            tmp = self._new_temp()
            self._emit("CALL", id_tok.value, str(len(args)), tmp)
            return

        if tok.type in ("++", "--"):
            op_tok = self._advance()
            self._expect(";")
            self._emit("INC" if op_tok.type == "++" else "DEC", id_tok.value)
            return

        lhs = id_tok.value
        lhs = self._resolve_lhs(lhs)

        if self._peek().type in ASSIGN_OPS:
            op_tok = self._advance()
            rhs = self._expression()
            self._expect(";")

            if op_tok.type == "=":
                self._emit("=", rhs, None, lhs)
            else:
                base_op = op_tok.type[0]
                tmp = self._new_temp()
                self._emit(base_op, lhs, rhs, tmp)
                self._emit("=", tmp, None, lhs)
        else:
            self.errors.append(f"ICG Line {tok.line}: unexpected token after id '{id_tok.value}'")
            while self._peek().type not in (";", "}", "EOF"):
                self._advance()
            self._match(";")

    def _resolve_lhs(self, base: str) -> str:
        tok = self._peek()
        if tok.type == "[":
            self._advance()
            idx = self._expression()
            self._expect("]")
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
            chain = f"{base}.{member.value}"
            while self._peek().type == ".":
                self._advance()
                m2 = self._expect("id")
                chain = f"{chain}.{m2.value}"
            return chain
        return base


    def _io_stmt(self):
        io_tok = self._advance()
        self._expect("(")
        args = self._arguments()
        self._expect(")")
        self._expect(";")

        if io_tok.type == "plant":
            for a in args:
                self._emit("PRINT", a)
        else:
            for a in args:
                self._emit("READ", None, None, a)


    def _conditional_stmt(self):
        self._expect("spring")
        self._expect("(")
        cond = self._expression()
        self._expect(")")

        false_label = self._new_label()
        end_label = self._new_label()

        self._emit("IFFALSE", cond, None, false_label)

        self._expect("{")
        self._statement(allow_reclaim=True)
        self._expect("}")

        self._emit("GOTO", None, None, end_label)
        self._emit("LABEL", None, None, false_label)

        self._elseif_chain(end_label)

        if self._peek().type == "wither":
            self._advance()
            self._expect("{")
            self._statement(allow_reclaim=True)
            self._expect("}")

        self._emit("LABEL", None, None, end_label)

    def _elseif_chain(self, end_label: str):
        while self._peek().type == "bud":
            self._advance()
            self._expect("(")
            cond = self._expression()
            self._expect(")")

            next_label = self._new_label()
            self._emit("IFFALSE", cond, None, next_label)

            self._expect("{")
            self._statement(allow_reclaim=True)
            self._expect("}")

            self._emit("GOTO", None, None, end_label)
            self._emit("LABEL", None, None, next_label)


    def _loop_stmt(self):
        tok = self._peek()
        if tok.type == "grow":
            self._while_loop()
        elif tok.type == "cultivate":
            self._for_loop()
        elif tok.type == "tend":
            self._do_while_loop()

    def _while_loop(self):
        self._expect("grow")
        self._expect("(")

        start_label = self._new_label()
        end_label = self._new_label()

        self._emit("LABEL", None, None, start_label)
        cond = self._expression()
        self._expect(")")

        self._emit("IFFALSE", cond, None, end_label)

        self._expect("{")
        self._statement(allow_reclaim=True)
        self._expect("}")

        self._emit("GOTO", None, None, start_label)
        self._emit("LABEL", None, None, end_label)

    def _for_loop(self):
        self._expect("cultivate")
        self._expect("(")

        self._for_init()
        self._expect(";")

        start_label = self._new_label()
        end_label = self._new_label()
        update_label = self._new_label()

        self._emit("LABEL", None, None, start_label)

        cond = self._expression()
        self._emit("IFFALSE", cond, None, end_label)

        self._expect(";")

        update_instrs: List[TACInstruction] = []
        saved_code = self.code
        self.code = update_instrs
        self._for_update()
        self.code = saved_code

        self._expect(")")
        self._expect("{")
        self._statement(allow_reclaim=True)
        self._expect("}")

        self._emit("LABEL", None, None, update_label)
        self.code.extend(update_instrs)
        self._emit("GOTO", None, None, start_label)
        self._emit("LABEL", None, None, end_label)

    def _for_init(self):
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

    def _for_update(self):
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
        self._expect("tend")
        self._expect("{")

        start_label = self._new_label()
        self._emit("LABEL", None, None, start_label)

        self._statement(allow_reclaim=True)
        self._expect("}")

        self._expect("grow")
        self._expect("(")
        cond = self._expression()
        self._expect(")")
        self._expect(";")

        self._emit("IF", cond, None, start_label)


    def _switch_stmt(self):
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
        while self._peek().type == "variety":
            self._advance()
            case_val = self._expression()
            self._expect(":")

            next_label = self._new_label()
            body_label = self._new_label()
            cmp_tmp = self._new_temp()

            self._emit("==", switch_expr, case_val, cmp_tmp)
            self._emit("IFFALSE", cmp_tmp, None, next_label)
            self._emit("LABEL", None, None, body_label)

            self._declaration()
            self._case_statements()

            if self._peek().type == "prune":
                self._advance()
                self._expect(";")

            self._emit("GOTO", None, None, end_label)
            self._emit("LABEL", None, None, next_label)

    def _case_statements(self):
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
            elif tok.type == "reclaim":
                self._return_stmt()
            else:
                break

    def _default_opt(self, end_label: str):
        if self._peek().type == "soil":
            self._advance()
            self._expect(":")
            self._declaration()
            self._case_statements()


    def _control_stmt(self):
        tok = self._advance()
        self._expect(";")
        if tok.type == "prune":
            self._emit("GOTO", None, None, "BREAK")
        else:
            self._emit("GOTO", None, None, "CONTINUE")


    def _expression(self) -> str:
        left = self._logic_or()
        if self._peek().type not in ASSIGN_OPS:
            return left

        op_tok = self._advance()
        right = self._expression()
        if op_tok.type == "=":
            self._emit("=", right, None, left)
        else:
            tmp = self._new_temp()
            self._emit(op_tok.type[0], left, right, tmp)
            self._emit("=", tmp, None, left)
        return left

    def _logic_or(self) -> str:
        left = self._logic_and()
        while self._peek().type == "||":
            self._advance()
            right = self._logic_and()
            tmp = self._new_temp()
            self._emit("||", left, right, tmp)
            left = tmp
        return left

    def _logic_and(self) -> str:
        left = self._relational()
        while self._peek().type == "&&":
            self._advance()
            right = self._relational()
            tmp = self._new_temp()
            self._emit("&&", left, right, tmp)
            left = tmp
        return left

    def _relational(self) -> str:
        left = self._arithmetic()
        if self._peek().type in (">", "<", ">=", "<=", "==", "!="):
            op = self._advance().type
            right = self._arithmetic()
            tmp = self._new_temp()
            self._emit(op, left, right, tmp)
            return tmp
        return left

    def _arithmetic(self) -> str:
        left = self._term()
        while self._peek().type in ("+", "-"):
            op = self._advance().type
            right = self._term()
            tmp = self._new_temp()
            self._emit(op, left, right, tmp)
            left = tmp
        return left

    def _term(self) -> str:
        left = self._power()
        while self._peek().type in ("*", "/", "%"):
            op = self._advance().type
            right = self._power()
            tmp = self._new_temp()
            self._emit(op, left, right, tmp)
            left = tmp
        return left

    def _power(self) -> str:
        left = self._factor()
        if self._peek().type == "**":
            op = self._advance().type
            right = self._power()
            tmp = self._new_temp()
            self._emit(op, left, right, tmp)
            return tmp
        return left

    def _factor(self) -> str:
        tok = self._peek()

        if tok.type == "(":
            self._advance()
            val = self._expression()
            self._expect(")")
            return val

        if tok.type in ("~", "!"):
            op = self._advance()
            inner = self._factor()
            tmp = self._new_temp()
            if op.type == "~":
                self._emit("UNARY_MINUS", inner, None, tmp)
            else:
                self._emit("NOT", inner, None, tmp)
            return tmp

        if tok.type == "id":
            id_tok = self._advance()
            nxt = self._peek()

            if nxt.type == "(":
                self._advance()
                args = self._arguments()
                self._expect(")")
                for a in args:
                    self._emit("PARAM", a)
                tmp = self._new_temp()
                self._emit("CALL", id_tok.value, str(len(args)), tmp)
                return tmp

            if nxt.type == "[":
                self._advance()
                idx = self._expression()
                self._expect("]")
                while self._peek().type == "[":
                    self._advance()
                    idx2 = self._expression()
                    self._expect("]")
                    tmp = self._new_temp()
                    self._emit("*", idx, idx2, tmp)
                    idx = tmp
                location = f"{id_tok.value}[{idx}]"
                if self._peek().type in ASSIGN_OPS:
                    return location
                tmp = self._new_temp()
                self._emit("ARRAY_LOAD", id_tok.value, idx, tmp)
                return tmp

            if nxt.type == ".":
                self._advance()
                member = self._expect("id")
                chain = member.value
                while self._peek().type == ".":
                    self._advance()
                    m2 = self._expect("id")
                    chain = f"{chain}.{m2.value}"
                location = f"{id_tok.value}.{chain}"
                if self._peek().type in ASSIGN_OPS:
                    return location
                tmp = self._new_temp()
                self._emit("STRUCT_LOAD", id_tok.value, chain, tmp)
                return tmp

            return id_tok.value

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

        self.errors.append(f"ICG Line {tok.line}: unexpected token in expression: '{tok.type}'")
        self._advance()
        return "???"


    def _arguments(self) -> List[str]:
        args: List[str] = []
        if self._peek().type in (")", "EOF"):
            return args
        args.append(self._expression())
        while self._match(","):
            args.append(self._expression())
        return args


def generate_icg(tokens: List[Any]) -> Dict[str, Any]:
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
