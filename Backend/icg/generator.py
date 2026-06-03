# AUTO: Imports names from another module.
from __future__ import annotations
# AUTO: Imports names from another module.
from dataclasses import dataclass
# AUTO: Imports names from another module.
from typing import Any, Dict, List, Optional, Tuple, Union


# AUTO: Attaches this decorator to the next function/class.
@dataclass
# AUTO: Defines class `_Tok`.
class _Tok:
    # AUTO: Executes this statement.
    type: str
    # AUTO: Executes this statement.
    value: str
    # AUTO: Executes this statement.
    line: int
    # AUTO: Sets `col: int`.
    col: int = 0


# AUTO: Defines function `_as_tok`.
def _as_tok(raw: Any) -> _Tok:
    # AUTO: Checks this condition.
    if isinstance(raw, dict):
        # AUTO: Returns this result to the caller.
        return _Tok(
            # AUTO: Sets `type`.
            type=str(raw.get("type", "")),
            # AUTO: Sets `value`.
            value=str(raw.get("value", "")),
            # AUTO: Sets `line`.
            line=int(raw.get("line", 0) or 0),
            # AUTO: Sets `col`.
            col=int(raw.get("col", 0) or 0),
        # AUTO: Closes the current grouped code/data.
        )
    # AUTO: Returns this result to the caller.
    return _Tok(
        # AUTO: Sets `type`.
        type=str(getattr(raw, "type", "")),
        # AUTO: Sets `value`.
        value=str(getattr(raw, "value", "")),
        # AUTO: Sets `line`.
        line=int(getattr(raw, "line", 0) or 0),
        # AUTO: Sets `col`.
        col=int(getattr(raw, "col", 0) or 0),
    # AUTO: Closes the current grouped code/data.
    )


# AUTO: Attaches this decorator to the next function/class.
@dataclass
# AUTO: Defines class `TACInstruction`.
class TACInstruction:
    # AUTO: Executes this statement.
    op: str
    # AUTO: Sets `arg1: Optional[str]`.
    arg1: Optional[str] = None
    # AUTO: Sets `arg2: Optional[str]`.
    arg2: Optional[str] = None
    # AUTO: Sets `result: Optional[str]`.
    result: Optional[str] = None

    # AUTO: Defines function `__str__`.
    def __str__(self) -> str:
        # AUTO: Checks this condition.
        if self.op == "LABEL":
            # AUTO: Returns this result to the caller.
            return f"{self.result}:"
        # AUTO: Checks this condition.
        if self.op == "GOTO":
            # AUTO: Returns this result to the caller.
            return f"goto {self.result}"
        # AUTO: Checks this condition.
        if self.op == "IF":
            # AUTO: Returns this result to the caller.
            return f"if {self.arg1} goto {self.result}"
        # AUTO: Checks this condition.
        if self.op == "IFFALSE":
            # AUTO: Returns this result to the caller.
            return f"ifFalse {self.arg1} goto {self.result}"
        # AUTO: Checks this condition.
        if self.op == "PARAM":
            # AUTO: Returns this result to the caller.
            return f"param {self.arg1}"
        # AUTO: Checks this condition.
        if self.op == "CALL":
            # AUTO: Returns this result to the caller.
            return f"{self.result} = call {self.arg1}, {self.arg2}"
        # AUTO: Checks this condition.
        if self.op == "RETURN":
            # AUTO: Returns this result to the caller.
            return f"return {self.arg1 or ''}"
        # AUTO: Checks this condition.
        if self.op == "PRINT":
            # AUTO: Returns this result to the caller.
            return f"print {self.arg1}"
        # AUTO: Checks this condition.
        if self.op == "READ":
            # AUTO: Returns this result to the caller.
            return f"read {self.result}"
        # AUTO: Checks this condition.
        if self.op == "FUNC":
            # AUTO: Returns this result to the caller.
            return f"func {self.arg1}:"
        # AUTO: Checks this condition.
        if self.op == "ENDFUNC":
            # AUTO: Returns this result to the caller.
            return f"endfunc"
        # AUTO: Checks this condition.
        if self.op == "DECLARE":
            # AUTO: Returns this result to the caller.
            return f"declare {self.result} : {self.arg1}"
        # AUTO: Checks this condition.
        if self.op == "ARRAY_DECLARE":
            # AUTO: Returns this result to the caller.
            return f"declare {self.result}[{self.arg2}] : {self.arg1}"
        # AUTO: Checks this condition.
        if self.op == "ARRAY_STORE":
            # AUTO: Returns this result to the caller.
            return f"{self.result}[{self.arg2}] = {self.arg1}"
        # AUTO: Checks this condition.
        if self.op == "ARRAY_LOAD":
            # AUTO: Returns this result to the caller.
            return f"{self.result} = {self.arg1}[{self.arg2}]"
        # AUTO: Checks this condition.
        if self.op == "STRUCT_STORE":
            # AUTO: Returns this result to the caller.
            return f"{self.arg1}.{self.arg2} = {self.result}"
        # AUTO: Checks this condition.
        if self.op == "STRUCT_LOAD":
            # AUTO: Returns this result to the caller.
            return f"{self.result} = {self.arg1}.{self.arg2}"
        # AUTO: Checks this condition.
        if self.op == "CONST":
            # AUTO: Returns this result to the caller.
            return f"const {self.result} : {self.arg1} = {self.arg2}"
        # AUTO: Checks this condition.
        if self.op == "INC":
            # AUTO: Returns this result to the caller.
            return f"{self.arg1} = {self.arg1} + 1"
        # AUTO: Checks this condition.
        if self.op == "DEC":
            # AUTO: Returns this result to the caller.
            return f"{self.arg1} = {self.arg1} - 1"
        # AUTO: Checks this condition.
        if self.arg2 is not None:
            # AUTO: Returns this result to the caller.
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        # AUTO: Checks this condition.
        if self.op == "=":
            # AUTO: Returns this result to the caller.
            return f"{self.result} = {self.arg1}"
        # AUTO: Checks this condition.
        if self.op == "UNARY_MINUS":
            # AUTO: Returns this result to the caller.
            return f"{self.result} = -{self.arg1}"
        # AUTO: Checks this condition.
        if self.op == "NOT":
            # AUTO: Returns this result to the caller.
            return f"{self.result} = !{self.arg1}"
        # AUTO: Returns this result to the caller.
        return f"{self.op} {self.arg1 or ''} {self.arg2 or ''} {self.result or ''}".strip()

    # AUTO: Defines function `to_dict`.
    def to_dict(self) -> dict:
        # AUTO: Returns this result to the caller.
        return {
            # AUTO: Executes this statement.
            "op": self.op,
            # AUTO: Executes this statement.
            "arg1": self.arg1,
            # AUTO: Executes this statement.
            "arg2": self.arg2,
            # AUTO: Executes this statement.
            "result": self.result,
            # AUTO: Calls `str`.
            "text": str(self),
        # AUTO: Closes the current grouped code/data.
        }


# AUTO: Sets `GAL_TYPE_MAP`.
GAL_TYPE_MAP = {
    # AUTO: Executes this statement.
    "seed": "int",
    # AUTO: Executes this statement.
    "tree": "float",
    # AUTO: Executes this statement.
    "leaf": "char",
    # AUTO: Executes this statement.
    "branch": "bool",
    # AUTO: Executes this statement.
    "vine": "string",
    # AUTO: Executes this statement.
    "empty": "void",
# AUTO: Closes the current grouped code/data.
}

# AUTO: Sets `DATA_TYPE_TOKENS`.
DATA_TYPE_TOKENS = set(GAL_TYPE_MAP.keys())

# AUTO: Adds into `ASSIGN_OPS = {"=", "`.
ASSIGN_OPS = {"=", "+=", "-=", "*=", "/=", "%="}


# AUTO: Defines class `ICGenerator`.
class ICGenerator:

    # AUTO: Defines function `__init__`.
    def __init__(self, tokens: List[Any]):
        # AUTO: Sets `self.tokens: List[_Tok]`.
        self.tokens: List[_Tok] = self._prepare(tokens)
        # AUTO: Sets `self.pos: int`.
        self.pos: int = 0
        # AUTO: Sets `self.code: List[TACInstruction]`.
        self.code: List[TACInstruction] = []
        # AUTO: Sets `self.errors: List[str]`.
        self.errors: List[str] = []
        # AUTO: Sets `self._temp_counter: int`.
        self._temp_counter: int = 0
        # AUTO: Sets `self._label_counter: int`.
        self._label_counter: int = 0


    # AUTO: Defines function `_prepare`.
    def _prepare(self, raw_tokens: List[Any]) -> List[_Tok]:
        # AUTO: Sets `toks: List[_Tok]`.
        toks: List[_Tok] = []
        # AUTO: Starts a loop over these values.
        for t in raw_tokens:
            # AUTO: Sets `tv`.
            tv = _as_tok(t)
            # AUTO: Checks this condition.
            if tv.type in ("\n", "comment", "mcommentlit"):
                # AUTO: Skips to the next loop iteration.
                continue
            # AUTO: Appends a value to a list.
            toks.append(tv)
        # AUTO: Checks this condition.
        if not toks or toks[-1].type != "EOF":
            # AUTO: Sets `last_line`.
            last_line = toks[-1].line if toks else 1
            # AUTO: Appends a value to a list.
            toks.append(_Tok("EOF", "EOF", last_line))
        # AUTO: Returns this result to the caller.
        return toks

    # AUTO: Defines function `_peek`.
    def _peek(self) -> _Tok:
        # AUTO: Checks this condition.
        if self.pos < len(self.tokens):
            # AUTO: Returns this result to the caller.
            return self.tokens[self.pos]
        # AUTO: Returns this result to the caller.
        return _Tok("EOF", "EOF", 0)

    # AUTO: Defines function `_advance`.
    def _advance(self) -> _Tok:
        # AUTO: Sets `tok`.
        tok = self._peek()
        # AUTO: Checks this condition.
        if self.pos < len(self.tokens):
            # AUTO: Adds into `self.pos`.
            self.pos += 1
        # AUTO: Returns this result to the caller.
        return tok

    # AUTO: Defines function `_expect`.
    def _expect(self, token_type: str) -> _Tok:
        # AUTO: Sets `tok`.
        tok = self._peek()
        # AUTO: Checks this condition.
        if tok.type != token_type:
            # AUTO: Appends a value to a list.
            self.errors.append(
                # AUTO: Executes this statement.
                f"ICG Line {tok.line}: expected '{token_type}', got '{tok.type}'"
            # AUTO: Closes the current grouped code/data.
            )
            # AUTO: Returns this result to the caller.
            return tok
        # AUTO: Returns this result to the caller.
        return self._advance()

    # AUTO: Defines function `_match`.
    def _match(self, token_type: str) -> bool:
        # AUTO: Checks this condition.
        if self._peek().type == token_type:
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Returns this result to the caller.
            return True
        # AUTO: Returns this result to the caller.
        return False

    # AUTO: Defines function `_new_temp`.
    def _new_temp(self) -> str:
        # AUTO: Sets `name`.
        name = f"t{self._temp_counter}"
        # AUTO: Adds into `self._temp_counter`.
        self._temp_counter += 1
        # AUTO: Returns this result to the caller.
        return name

    # AUTO: Defines function `_new_label`.
    def _new_label(self) -> str:
        # AUTO: Sets `name`.
        name = f"L{self._label_counter}"
        # AUTO: Adds into `self._label_counter`.
        self._label_counter += 1
        # AUTO: Returns this result to the caller.
        return name

    # AUTO: Defines function `_emit`.
    def _emit(self, op: str, arg1: Optional[str] = None,
              # AUTO: Sets `arg2: Optional[str]`.
              arg2: Optional[str] = None, result: Optional[str] = None):
        # AUTO: Appends a value to a list.
        self.code.append(TACInstruction(op, arg1, arg2, result))

    # AUTO: Defines function `_is_data_type`.
    def _is_data_type(self, tok: _Tok) -> bool:
        # AUTO: Returns this result to the caller.
        return tok.type in DATA_TYPE_TOKENS


    # AUTO: Defines function `generate`.
    def generate(self) -> Tuple[List[TACInstruction], List[str]]:
        # AUTO: Starts protected code that can catch errors.
        try:
            # AUTO: Calls `self._program`.
            self._program()
        # AUTO: Handles the matching error case.
        except Exception as exc:
            # AUTO: Appends a value to a list.
            self.errors.append(f"ICG internal error: {exc}")
        # AUTO: Returns this result to the caller.
        return self.code, self.errors

    # AUTO: Defines function `_program`.
    def _program(self):
        # AUTO: Calls `self._global_declaration`.
        self._global_declaration()
        # AUTO: Calls `self._function_definition`.
        self._function_definition()

        # AUTO: Calls `self._expect`.
        self._expect("root")
        # AUTO: Calls `self._expect`.
        self._expect("(")
        # AUTO: Calls `self._expect`.
        self._expect(")")
        # AUTO: Calls `self._expect`.
        self._expect("{")
        # AUTO: Calls `self._emit`.
        self._emit("FUNC", "root")

        # AUTO: Calls `self._declaration`.
        self._declaration()
        # AUTO: Calls `self._statement`.
        self._statement()

        # AUTO: Calls `self._expect`.
        self._expect("reclaim")
        # AUTO: Calls `self._expect`.
        self._expect(";")
        # AUTO: Calls `self._emit`.
        self._emit("RETURN")

        # AUTO: Calls `self._expect`.
        self._expect("}")
        # AUTO: Calls `self._emit`.
        self._emit("ENDFUNC")


    # AUTO: Defines function `_global_declaration`.
    def _global_declaration(self):
        # AUTO: Repeats while this condition is true.
        while True:
            # AUTO: Sets `tok`.
            tok = self._peek()
            # AUTO: Checks this condition.
            if tok.type == "bundle":
                # AUTO: Calls `self._advance`.
                self._advance()
                # AUTO: Sets `name_tok`.
                name_tok = self._expect("id")
                # AUTO: Sets `nxt`.
                nxt = self._peek()
                # AUTO: Checks this condition.
                if nxt.type == "{":
                    # AUTO: Calls `self._advance`.
                    self._advance()
                    # AUTO: Calls `self._bundle_members`.
                    self._bundle_members()
                    # AUTO: Calls `self._expect`.
                    self._expect("}")
                    # AUTO: Calls `self._expect`.
                    self._expect(";")
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Calls `self._bundle_mem_dec`.
                    self._bundle_mem_dec()
                    # AUTO: Calls `self._expect`.
                    self._expect(";")
                # AUTO: Calls `self._global_declaration`.
                self._global_declaration()
                # AUTO: Returns this result to the caller.
                return

            # AUTO: Checks the next alternate condition.
            elif self._is_data_type(tok):
                # AUTO: Sets `dtype`.
                dtype = self._advance()
                # AUTO: Sets `id_tok`.
                id_tok = self._expect("id")
                # AUTO: Sets `arr_dims`.
                arr_dims = self._array_dec()
                # AUTO: Checks this condition.
                if arr_dims:
                    # AUTO: Starts a loop over these values.
                    for dim in arr_dims:
                        # AUTO: Calls `self._emit`.
                        self._emit("ARRAY_DECLARE", GAL_TYPE_MAP.get(dtype.type, dtype.type),
                                   # AUTO: Executes this statement.
                                   dim, id_tok.value)
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Calls `self._emit`.
                    self._emit("DECLARE", GAL_TYPE_MAP.get(dtype.type, dtype.type),
                               # AUTO: Executes this statement.
                               None, id_tok.value)
                # AUTO: Calls `self._var_value`.
                self._var_value(id_tok.value)
                # AUTO: Calls `self._expect`.
                self._expect(";")
                # AUTO: Calls `self._global_declaration`.
                self._global_declaration()
                # AUTO: Returns this result to the caller.
                return

            # AUTO: Checks the next alternate condition.
            elif tok.type == "fertile":
                # AUTO: Calls `self._const_dec`.
                self._const_dec()
                # AUTO: Calls `self._expect`.
                self._expect(";")
                # AUTO: Calls `self._global_declaration`.
                self._global_declaration()
                # AUTO: Returns this result to the caller.
                return

            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Returns this result to the caller.
                return


    # AUTO: Defines function `_declaration`.
    def _declaration(self):
        # AUTO: Repeats while this condition is true.
        while True:
            # AUTO: Sets `tok`.
            tok = self._peek()
            # AUTO: Checks this condition.
            if self._is_data_type(tok) or tok.type == "bundle":
                # AUTO: Calls `self._var_dec`.
                self._var_dec()
                # AUTO: Calls `self._expect`.
                self._expect(";")
            # AUTO: Checks the next alternate condition.
            elif tok.type == "fertile":
                # AUTO: Calls `self._const_dec`.
                self._const_dec()
                # AUTO: Calls `self._expect`.
                self._expect(";")
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Stops the nearest loop.
                break

    # AUTO: Defines function `_var_dec`.
    def _var_dec(self):
        # AUTO: Sets `tok`.
        tok = self._peek()
        # AUTO: Checks this condition.
        if tok.type == "bundle":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Sets `id_tok`.
            id_tok = self._expect("id")
            # AUTO: Calls `self._bundle_mem_dec`.
            self._bundle_mem_dec()
            # AUTO: Returns this result to the caller.
            return

        # AUTO: Sets `dtype`.
        dtype = self._advance()
        # AUTO: Sets `id_tok`.
        id_tok = self._expect("id")
        # AUTO: Sets `arr_dims`.
        arr_dims = self._array_dec()
        # AUTO: Checks this condition.
        if arr_dims:
            # AUTO: Starts a loop over these values.
            for dim in arr_dims:
                # AUTO: Calls `self._emit`.
                self._emit("ARRAY_DECLARE", GAL_TYPE_MAP.get(dtype.type, dtype.type),
                           # AUTO: Executes this statement.
                           dim, id_tok.value)
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Calls `self._emit`.
            self._emit("DECLARE", GAL_TYPE_MAP.get(dtype.type, dtype.type), None, id_tok.value)
        # AUTO: Calls `self._var_value`.
        self._var_value(id_tok.value)

    # AUTO: Defines function `_const_dec`.
    def _const_dec(self):
        # AUTO: Calls `self._expect`.
        self._expect("fertile")
        # AUTO: Sets `dtype`.
        dtype = self._advance()
        # AUTO: Sets `id_tok`.
        id_tok = self._expect("id")
        # AUTO: Sets `self._expect("`.
        self._expect("=")
        # AUTO: Sets `val`.
        val = self._init_val()
        # AUTO: Calls `self._emit`.
        self._emit("CONST", GAL_TYPE_MAP.get(dtype.type, dtype.type), val, id_tok.value)
        # AUTO: Calls `self._const_next`.
        self._const_next(dtype)

    # AUTO: Defines function `_const_next`.
    def _const_next(self, dtype_tok: _Tok):
        # AUTO: Repeats while this condition is true.
        while self._match(","):
            # AUTO: Sets `id_tok`.
            id_tok = self._expect("id")
            # AUTO: Sets `self._expect("`.
            self._expect("=")
            # AUTO: Sets `val`.
            val = self._init_val()
            # AUTO: Calls `self._emit`.
            self._emit("CONST", GAL_TYPE_MAP.get(dtype_tok.type, dtype_tok.type), val, id_tok.value)

    # AUTO: Defines function `_var_value`.
    def _var_value(self, var_name: str):
        # AUTO: Checks this condition.
        if self._peek().type == "=":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Sets `val`.
            val = self._init_val()
            # AUTO: Sets `self._emit("`.
            self._emit("=", val, None, var_name)
            # AUTO: Calls `self._var_value_next`.
            self._var_value_next()
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Calls `self._var_value_next`.
            self._var_value_next()

    # AUTO: Defines function `_var_value_next`.
    def _var_value_next(self):
        # AUTO: Checks this condition.
        if self._match(","):
            # AUTO: Sets `id_tok`.
            id_tok = self._expect("id")
            # AUTO: Sets `arr_dims`.
            arr_dims = self._array_dec()
            # AUTO: Checks this condition.
            if arr_dims:
                # AUTO: Starts a loop over these values.
                for dim in arr_dims:
                    # AUTO: Calls `self._emit`.
                    self._emit("ARRAY_DECLARE", "int", dim, id_tok.value)
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Calls `self._emit`.
                self._emit("DECLARE", "int", None, id_tok.value)
            # AUTO: Calls `self._var_value`.
            self._var_value(id_tok.value)

    # AUTO: Defines function `_init_val`.
    def _init_val(self) -> str:
        # AUTO: Checks this condition.
        if self._peek().type == "{":
            # AUTO: Returns this result to the caller.
            return self._array_init()
        # AUTO: Returns this result to the caller.
        return self._expression()

    # AUTO: Defines function `_array_init`.
    def _array_init(self) -> str:
        # AUTO: Calls `self._expect`.
        self._expect("{")
        # AUTO: Sets `tmp`.
        tmp = self._new_temp()
        # AUTO: Sets `idx`.
        idx = 0
        # AUTO: Checks this condition.
        if self._peek().type != "}":
            # AUTO: Sets `val`.
            val = self._init_val_item()
            # AUTO: Calls `self._emit`.
            self._emit("ARRAY_STORE", val, str(idx), tmp)
            # AUTO: Adds into `idx`.
            idx += 1
            # AUTO: Repeats while this condition is true.
            while self._match(","):
                # AUTO: Sets `val`.
                val = self._init_val_item()
                # AUTO: Calls `self._emit`.
                self._emit("ARRAY_STORE", val, str(idx), tmp)
                # AUTO: Adds into `idx`.
                idx += 1
        # AUTO: Calls `self._expect`.
        self._expect("}")
        # AUTO: Returns this result to the caller.
        return tmp

    # AUTO: Defines function `_init_val_item`.
    def _init_val_item(self) -> str:
        # AUTO: Checks this condition.
        if self._peek().type == "{":
            # AUTO: Returns this result to the caller.
            return self._array_init()
        # AUTO: Returns this result to the caller.
        return self._expression()


    # AUTO: Defines function `_array_dec`.
    def _array_dec(self) -> List[str]:
        # AUTO: Sets `dims: List[str]`.
        dims: List[str] = []
        # AUTO: Repeats while this condition is true.
        while self._peek().type == "[":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Checks this condition.
            if self._peek().type == "intlit":
                # AUTO: Appends a value to a list.
                dims.append(self._advance().value)
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Appends a value to a list.
                dims.append("0")
            # AUTO: Calls `self._expect`.
            self._expect("]")
        # AUTO: Returns this result to the caller.
        return dims

    # AUTO: Defines function `_bundle_members`.
    def _bundle_members(self):
        # AUTO: Repeats while this condition is true.
        while self._is_data_type(self._peek()):
            # AUTO: Sets `dtype`.
            dtype = self._advance()
            # AUTO: Sets `id_tok`.
            id_tok = self._expect("id")
            # AUTO: Calls `self._expect`.
            self._expect(";")

    # AUTO: Defines function `_bundle_mem_dec`.
    def _bundle_mem_dec(self):
        # AUTO: Sets `id_tok`.
        id_tok = self._expect("id")
        # AUTO: Sets `arr_dims`.
        arr_dims = self._array_dec()
        # AUTO: Checks this condition.
        if arr_dims:
            # AUTO: Starts a loop over these values.
            for dim in arr_dims:
                # AUTO: Calls `self._emit`.
                self._emit("ARRAY_DECLARE", "bundle", dim, id_tok.value)
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Calls `self._emit`.
            self._emit("DECLARE", "bundle", None, id_tok.value)


    # AUTO: Defines function `_function_definition`.
    def _function_definition(self):
        # AUTO: Repeats while this condition is true.
        while self._peek().type == "pollinate":
            # AUTO: Calls `self._advance`.
            self._advance()

            # AUTO: Checks this condition.
            if self._peek().type == "empty":
                # AUTO: Sets `ret_type`.
                ret_type = self._advance().type
            # AUTO: Checks the next alternate condition.
            elif self._is_data_type(self._peek()):
                # AUTO: Sets `ret_type`.
                ret_type = self._advance().type
            # AUTO: Checks the next alternate condition.
            elif self._peek().type == "id":
                # AUTO: Sets `ret_type`.
                ret_type = self._advance().value
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Sets `ret_type`.
                ret_type = "void"

            # AUTO: Sets `func_name`.
            func_name = self._expect("id")
            # AUTO: Calls `self._expect`.
            self._expect("(")

            # AUTO: Sets `params`.
            params = self._parameters()

            # AUTO: Calls `self._expect`.
            self._expect(")")
            # AUTO: Calls `self._expect`.
            self._expect("{")

            # AUTO: Calls `self._emit`.
            self._emit("FUNC", func_name.value)
            # AUTO: Starts a loop over these values.
            for ptype, pname, *rest in params:
                # AUTO: Sets `is_array`.
                is_array = rest[0] if rest else False
                # AUTO: Checks this condition.
                if is_array:
                    # AUTO: Calls `self._emit`.
                    self._emit("ARRAY_DECLARE", GAL_TYPE_MAP.get(ptype, ptype), "param", pname)
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Calls `self._emit`.
                    self._emit("DECLARE", GAL_TYPE_MAP.get(ptype, ptype), None, pname)

            # AUTO: Calls `self._declaration`.
            self._declaration()
            # AUTO: Calls `self._statement`.
            self._statement()

            # AUTO: Calls `self._expect`.
            self._expect("reclaim")
            # AUTO: Checks this condition.
            if self._peek().type == ";":
                # AUTO: Calls `self._emit`.
                self._emit("RETURN")
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Sets `val`.
                val = self._expression()
                # AUTO: Calls `self._emit`.
                self._emit("RETURN", val)
            # AUTO: Calls `self._expect`.
            self._expect(";")

            # AUTO: Calls `self._expect`.
            self._expect("}")
            # AUTO: Calls `self._emit`.
            self._emit("ENDFUNC")

    # AUTO: Defines function `_parameters`.
    def _parameters(self):
        # AUTO: Sets `params`.
        params = []
        # AUTO: Checks this condition.
        if self._is_data_type(self._peek()) or self._peek().type == "id":
            # AUTO: Sets `p`.
            p = self._param()
            # AUTO: Appends a value to a list.
            params.append(p)
            # AUTO: Repeats while this condition is true.
            while self._match(","):
                # AUTO: Sets `p`.
                p = self._param()
                # AUTO: Appends a value to a list.
                params.append(p)
        # AUTO: Returns this result to the caller.
        return params

    # AUTO: Defines function `_param`.
    def _param(self) -> Tuple[str, str]:
        # AUTO: Sets `dtype`.
        dtype = self._advance()
        # AUTO: Sets `id_tok`.
        id_tok = self._expect("id")
        # AUTO: Executes this statement.
        type_name = dtype.value if dtype.type == "id" else dtype.type
        # AUTO: Sets `is_array`.
        is_array = False
        # AUTO: Checks this condition.
        if self._peek().type == "[":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Calls `self._expect`.
            self._expect("]")
            # AUTO: Sets `is_array`.
            is_array = True
        # AUTO: Returns this result to the caller.
        return (type_name, id_tok.value, is_array)


    # AUTO: Defines function `_statement`.
    def _statement(self, allow_reclaim: bool = False):
        # AUTO: Sets `stopping_tokens`.
        stopping_tokens = {"}", "EOF", "variety", "soil", "prune"}
        # AUTO: Repeats while this condition is true.
        while self._peek().type not in stopping_tokens:
            # AUTO: Sets `tok`.
            tok = self._peek()
            # AUTO: Checks this condition.
            if tok.type == "reclaim":
                # AUTO: Checks this condition.
                if not allow_reclaim:
                    # AUTO: Returns this result to the caller.
                    return
                # AUTO: Calls `self._return_stmt`.
                self._return_stmt()
                # AUTO: Skips to the next loop iteration.
                continue
            # AUTO: Checks this condition.
            if self._is_data_type(tok) or tok.type == "bundle" or tok.type == "fertile":
                # AUTO: Checks this condition.
                if tok.type == "fertile":
                    # AUTO: Calls `self._const_dec`.
                    self._const_dec()
                    # AUTO: Calls `self._expect`.
                    self._expect(";")
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Calls `self._var_dec`.
                    self._var_dec()
                    # AUTO: Calls `self._expect`.
                    self._expect(";")
                # AUTO: Skips to the next loop iteration.
                continue
            # AUTO: Calls `self._simple_stmt`.
            self._simple_stmt()

    # AUTO: Defines function `_return_stmt`.
    def _return_stmt(self):
        # AUTO: Calls `self._expect`.
        self._expect("reclaim")
        # AUTO: Checks this condition.
        if self._peek().type == ";":
            # AUTO: Calls `self._emit`.
            self._emit("RETURN")
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Calls `self._emit`.
            self._emit("RETURN", self._expression())
        # AUTO: Calls `self._expect`.
        self._expect(";")

    # AUTO: Defines function `_simple_stmt`.
    def _simple_stmt(self):
        # AUTO: Sets `tok`.
        tok = self._peek()

        # AUTO: Checks this condition.
        if tok.type == "id":
            # AUTO: Calls `self._id_stmt`.
            self._id_stmt()
        # AUTO: Checks the next alternate condition.
        elif tok.type in ("water", "plant"):
            # AUTO: Calls `self._io_stmt`.
            self._io_stmt()
        # AUTO: Checks the next alternate condition.
        elif tok.type == "spring":
            # AUTO: Calls `self._conditional_stmt`.
            self._conditional_stmt()
        # AUTO: Checks the next alternate condition.
        elif tok.type in ("grow", "cultivate", "tend"):
            # AUTO: Calls `self._loop_stmt`.
            self._loop_stmt()
        # AUTO: Checks the next alternate condition.
        elif tok.type == "harvest":
            # AUTO: Calls `self._switch_stmt`.
            self._switch_stmt()
        # AUTO: Checks the next alternate condition.
        elif tok.type in ("prune", "skip"):
            # AUTO: Calls `self._control_stmt`.
            self._control_stmt()
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Appends a value to a list.
            self.errors.append(f"ICG Line {tok.line}: unexpected token '{tok.type}'")
            # AUTO: Calls `self._advance`.
            self._advance()


    # AUTO: Defines function `_id_stmt`.
    def _id_stmt(self):
        # AUTO: Sets `id_tok`.
        id_tok = self._advance()
        # AUTO: Sets `tok`.
        tok = self._peek()

        # AUTO: Checks this condition.
        if tok.type == "(":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Sets `args`.
            args = self._arguments()
            # AUTO: Calls `self._expect`.
            self._expect(")")
            # AUTO: Calls `self._expect`.
            self._expect(";")
            # AUTO: Starts a loop over these values.
            for a in args:
                # AUTO: Calls `self._emit`.
                self._emit("PARAM", a)
            # AUTO: Sets `tmp`.
            tmp = self._new_temp()
            # AUTO: Calls `self._emit`.
            self._emit("CALL", id_tok.value, str(len(args)), tmp)
            # AUTO: Returns this result to the caller.
            return

        # AUTO: Checks this condition.
        if tok.type in ("++", "--"):
            # AUTO: Sets `op_tok`.
            op_tok = self._advance()
            # AUTO: Calls `self._expect`.
            self._expect(";")
            # AUTO: Calls `self._emit`.
            self._emit("INC" if op_tok.type == "++" else "DEC", id_tok.value)
            # AUTO: Returns this result to the caller.
            return

        # AUTO: Sets `lhs`.
        lhs = id_tok.value
        # AUTO: Sets `lhs`.
        lhs = self._resolve_lhs(lhs)

        # AUTO: Checks this condition.
        if self._peek().type in ASSIGN_OPS:
            # AUTO: Sets `op_tok`.
            op_tok = self._advance()
            # AUTO: Sets `rhs`.
            rhs = self._expression()
            # AUTO: Calls `self._expect`.
            self._expect(";")

            # AUTO: Checks this condition.
            if op_tok.type == "=":
                # AUTO: Sets `self._emit("`.
                self._emit("=", rhs, None, lhs)
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Sets `base_op`.
                base_op = op_tok.type[0]
                # AUTO: Sets `tmp`.
                tmp = self._new_temp()
                # AUTO: Calls `self._emit`.
                self._emit(base_op, lhs, rhs, tmp)
                # AUTO: Sets `self._emit("`.
                self._emit("=", tmp, None, lhs)
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Appends a value to a list.
            self.errors.append(f"ICG Line {tok.line}: unexpected token after id '{id_tok.value}'")
            # AUTO: Repeats while this condition is true.
            while self._peek().type not in (";", "}", "EOF"):
                # AUTO: Calls `self._advance`.
                self._advance()
            # AUTO: Calls `self._match`.
            self._match(";")

    # AUTO: Defines function `_resolve_lhs`.
    def _resolve_lhs(self, base: str) -> str:
        # AUTO: Sets `tok`.
        tok = self._peek()
        # AUTO: Checks this condition.
        if tok.type == "[":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Sets `idx`.
            idx = self._expression()
            # AUTO: Calls `self._expect`.
            self._expect("]")
            # AUTO: Repeats while this condition is true.
            while self._peek().type == "[":
                # AUTO: Calls `self._advance`.
                self._advance()
                # AUTO: Sets `idx2`.
                idx2 = self._expression()
                # AUTO: Calls `self._expect`.
                self._expect("]")
                # AUTO: Sets `tmp`.
                tmp = self._new_temp()
                # AUTO: Calls `self._emit`.
                self._emit("*", idx, idx2, tmp)
                # AUTO: Sets `idx`.
                idx = tmp
            # AUTO: Returns this result to the caller.
            return f"{base}[{idx}]"
        # AUTO: Checks the next alternate condition.
        elif tok.type == ".":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Sets `member`.
            member = self._expect("id")
            # AUTO: Sets `chain`.
            chain = f"{base}.{member.value}"
            # AUTO: Repeats while this condition is true.
            while self._peek().type == ".":
                # AUTO: Calls `self._advance`.
                self._advance()
                # AUTO: Sets `m2`.
                m2 = self._expect("id")
                # AUTO: Sets `chain`.
                chain = f"{chain}.{m2.value}"
            # AUTO: Returns this result to the caller.
            return chain
        # AUTO: Returns this result to the caller.
        return base


    # AUTO: Defines function `_io_stmt`.
    def _io_stmt(self):
        # AUTO: Sets `io_tok`.
        io_tok = self._advance()
        # AUTO: Calls `self._expect`.
        self._expect("(")
        # AUTO: Sets `args`.
        args = self._arguments()
        # AUTO: Calls `self._expect`.
        self._expect(")")
        # AUTO: Calls `self._expect`.
        self._expect(";")

        # AUTO: Checks this condition.
        if io_tok.type == "plant":
            # AUTO: Starts a loop over these values.
            for a in args:
                # AUTO: Calls `self._emit`.
                self._emit("PRINT", a)
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Starts a loop over these values.
            for a in args:
                # AUTO: Calls `self._emit`.
                self._emit("READ", None, None, a)


    # AUTO: Defines function `_conditional_stmt`.
    def _conditional_stmt(self):
        # AUTO: Calls `self._expect`.
        self._expect("spring")
        # AUTO: Calls `self._expect`.
        self._expect("(")
        # AUTO: Sets `cond`.
        cond = self._expression()
        # AUTO: Calls `self._expect`.
        self._expect(")")

        # AUTO: Sets `false_label`.
        false_label = self._new_label()
        # AUTO: Sets `end_label`.
        end_label = self._new_label()

        # AUTO: Calls `self._emit`.
        self._emit("IFFALSE", cond, None, false_label)

        # AUTO: Calls `self._expect`.
        self._expect("{")
        # AUTO: Sets `self._statement(allow_reclaim`.
        self._statement(allow_reclaim=True)
        # AUTO: Calls `self._expect`.
        self._expect("}")

        # AUTO: Calls `self._emit`.
        self._emit("GOTO", None, None, end_label)
        # AUTO: Calls `self._emit`.
        self._emit("LABEL", None, None, false_label)

        # AUTO: Calls `self._elseif_chain`.
        self._elseif_chain(end_label)

        # AUTO: Checks this condition.
        if self._peek().type == "wither":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Calls `self._expect`.
            self._expect("{")
            # AUTO: Sets `self._statement(allow_reclaim`.
            self._statement(allow_reclaim=True)
            # AUTO: Calls `self._expect`.
            self._expect("}")

        # AUTO: Calls `self._emit`.
        self._emit("LABEL", None, None, end_label)

    # AUTO: Defines function `_elseif_chain`.
    def _elseif_chain(self, end_label: str):
        # AUTO: Repeats while this condition is true.
        while self._peek().type == "bud":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Calls `self._expect`.
            self._expect("(")
            # AUTO: Sets `cond`.
            cond = self._expression()
            # AUTO: Calls `self._expect`.
            self._expect(")")

            # AUTO: Sets `next_label`.
            next_label = self._new_label()
            # AUTO: Calls `self._emit`.
            self._emit("IFFALSE", cond, None, next_label)

            # AUTO: Calls `self._expect`.
            self._expect("{")
            # AUTO: Sets `self._statement(allow_reclaim`.
            self._statement(allow_reclaim=True)
            # AUTO: Calls `self._expect`.
            self._expect("}")

            # AUTO: Calls `self._emit`.
            self._emit("GOTO", None, None, end_label)
            # AUTO: Calls `self._emit`.
            self._emit("LABEL", None, None, next_label)


    # AUTO: Defines function `_loop_stmt`.
    def _loop_stmt(self):
        # AUTO: Sets `tok`.
        tok = self._peek()
        # AUTO: Checks this condition.
        if tok.type == "grow":
            # AUTO: Calls `self._while_loop`.
            self._while_loop()
        # AUTO: Checks the next alternate condition.
        elif tok.type == "cultivate":
            # AUTO: Calls `self._for_loop`.
            self._for_loop()
        # AUTO: Checks the next alternate condition.
        elif tok.type == "tend":
            # AUTO: Calls `self._do_while_loop`.
            self._do_while_loop()

    # AUTO: Defines function `_while_loop`.
    def _while_loop(self):
        # AUTO: Calls `self._expect`.
        self._expect("grow")
        # AUTO: Calls `self._expect`.
        self._expect("(")

        # AUTO: Sets `start_label`.
        start_label = self._new_label()
        # AUTO: Sets `end_label`.
        end_label = self._new_label()

        # AUTO: Calls `self._emit`.
        self._emit("LABEL", None, None, start_label)
        # AUTO: Sets `cond`.
        cond = self._expression()
        # AUTO: Calls `self._expect`.
        self._expect(")")

        # AUTO: Calls `self._emit`.
        self._emit("IFFALSE", cond, None, end_label)

        # AUTO: Calls `self._expect`.
        self._expect("{")
        # AUTO: Sets `self._statement(allow_reclaim`.
        self._statement(allow_reclaim=True)
        # AUTO: Calls `self._expect`.
        self._expect("}")

        # AUTO: Calls `self._emit`.
        self._emit("GOTO", None, None, start_label)
        # AUTO: Calls `self._emit`.
        self._emit("LABEL", None, None, end_label)

    # AUTO: Defines function `_for_loop`.
    def _for_loop(self):
        # AUTO: Calls `self._expect`.
        self._expect("cultivate")
        # AUTO: Calls `self._expect`.
        self._expect("(")

        # AUTO: Calls `self._for_init`.
        self._for_init()
        # AUTO: Calls `self._expect`.
        self._expect(";")

        # AUTO: Sets `start_label`.
        start_label = self._new_label()
        # AUTO: Sets `end_label`.
        end_label = self._new_label()
        # AUTO: Sets `update_label`.
        update_label = self._new_label()

        # AUTO: Calls `self._emit`.
        self._emit("LABEL", None, None, start_label)

        # AUTO: Sets `cond`.
        cond = self._expression()
        # AUTO: Calls `self._emit`.
        self._emit("IFFALSE", cond, None, end_label)

        # AUTO: Calls `self._expect`.
        self._expect(";")

        # AUTO: Sets `update_instrs: List[TACInstruction]`.
        update_instrs: List[TACInstruction] = []
        # AUTO: Sets `saved_code`.
        saved_code = self.code
        # AUTO: Sets `self.code`.
        self.code = update_instrs
        # AUTO: Calls `self._for_update`.
        self._for_update()
        # AUTO: Sets `self.code`.
        self.code = saved_code

        # AUTO: Calls `self._expect`.
        self._expect(")")
        # AUTO: Calls `self._expect`.
        self._expect("{")
        # AUTO: Sets `self._statement(allow_reclaim`.
        self._statement(allow_reclaim=True)
        # AUTO: Calls `self._expect`.
        self._expect("}")

        # AUTO: Calls `self._emit`.
        self._emit("LABEL", None, None, update_label)
        # AUTO: Calls `self.code.extend`.
        self.code.extend(update_instrs)
        # AUTO: Calls `self._emit`.
        self._emit("GOTO", None, None, start_label)
        # AUTO: Calls `self._emit`.
        self._emit("LABEL", None, None, end_label)

    # AUTO: Defines function `_for_init`.
    def _for_init(self):
        # AUTO: Sets `tok`.
        tok = self._peek()
        # AUTO: Checks this condition.
        if self._is_data_type(tok):
            # AUTO: Calls `self._var_dec`.
            self._var_dec()
        # AUTO: Checks the next alternate condition.
        elif tok.type == "id":
            # AUTO: Sets `id_tok`.
            id_tok = self._advance()
            # AUTO: Sets `lhs`.
            lhs = self._resolve_lhs(id_tok.value)
            # AUTO: Checks this condition.
            if self._peek().type in ASSIGN_OPS:
                # AUTO: Sets `op_tok`.
                op_tok = self._advance()
                # AUTO: Sets `rhs`.
                rhs = self._expression()
                # AUTO: Checks this condition.
                if op_tok.type == "=":
                    # AUTO: Sets `self._emit("`.
                    self._emit("=", rhs, None, lhs)
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Sets `base_op`.
                    base_op = op_tok.type[0]
                    # AUTO: Sets `tmp`.
                    tmp = self._new_temp()
                    # AUTO: Calls `self._emit`.
                    self._emit(base_op, lhs, rhs, tmp)
                    # AUTO: Sets `self._emit("`.
                    self._emit("=", tmp, None, lhs)

    # AUTO: Defines function `_for_update`.
    def _for_update(self):
        # AUTO: Checks this condition.
        if self._peek().type == "id":
            # AUTO: Sets `id_tok`.
            id_tok = self._advance()
            # AUTO: Sets `tok`.
            tok = self._peek()
            # AUTO: Checks this condition.
            if tok.type in ("++", "--"):
                # AUTO: Sets `op`.
                op = self._advance()
                # AUTO: Calls `self._emit`.
                self._emit("INC" if op.type == "++" else "DEC", id_tok.value)
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Sets `lhs`.
                lhs = self._resolve_lhs(id_tok.value)
                # AUTO: Checks this condition.
                if self._peek().type in ASSIGN_OPS:
                    # AUTO: Sets `op_tok`.
                    op_tok = self._advance()
                    # AUTO: Sets `rhs`.
                    rhs = self._expression()
                    # AUTO: Checks this condition.
                    if op_tok.type == "=":
                        # AUTO: Sets `self._emit("`.
                        self._emit("=", rhs, None, lhs)
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Sets `base_op`.
                        base_op = op_tok.type[0]
                        # AUTO: Sets `tmp`.
                        tmp = self._new_temp()
                        # AUTO: Calls `self._emit`.
                        self._emit(base_op, lhs, rhs, tmp)
                        # AUTO: Sets `self._emit("`.
                        self._emit("=", tmp, None, lhs)

    # AUTO: Defines function `_do_while_loop`.
    def _do_while_loop(self):
        # AUTO: Calls `self._expect`.
        self._expect("tend")
        # AUTO: Calls `self._expect`.
        self._expect("{")

        # AUTO: Sets `start_label`.
        start_label = self._new_label()
        # AUTO: Calls `self._emit`.
        self._emit("LABEL", None, None, start_label)

        # AUTO: Sets `self._statement(allow_reclaim`.
        self._statement(allow_reclaim=True)
        # AUTO: Calls `self._expect`.
        self._expect("}")

        # AUTO: Calls `self._expect`.
        self._expect("grow")
        # AUTO: Calls `self._expect`.
        self._expect("(")
        # AUTO: Sets `cond`.
        cond = self._expression()
        # AUTO: Calls `self._expect`.
        self._expect(")")
        # AUTO: Calls `self._expect`.
        self._expect(";")

        # AUTO: Calls `self._emit`.
        self._emit("IF", cond, None, start_label)


    # AUTO: Defines function `_switch_stmt`.
    def _switch_stmt(self):
        # AUTO: Calls `self._expect`.
        self._expect("harvest")
        # AUTO: Calls `self._expect`.
        self._expect("(")
        # AUTO: Sets `expr`.
        expr = self._expression()
        # AUTO: Calls `self._expect`.
        self._expect(")")
        # AUTO: Calls `self._expect`.
        self._expect("{")

        # AUTO: Sets `end_label`.
        end_label = self._new_label()
        # AUTO: Calls `self._case_list`.
        self._case_list(expr, end_label)
        # AUTO: Calls `self._default_opt`.
        self._default_opt(end_label)

        # AUTO: Calls `self._expect`.
        self._expect("}")
        # AUTO: Calls `self._emit`.
        self._emit("LABEL", None, None, end_label)

    # AUTO: Defines function `_case_list`.
    def _case_list(self, switch_expr: str, end_label: str):
        # AUTO: Repeats while this condition is true.
        while self._peek().type == "variety":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Sets `case_val`.
            case_val = self._expression()
            # AUTO: Calls `self._expect`.
            self._expect(":")

            # AUTO: Sets `next_label`.
            next_label = self._new_label()
            # AUTO: Sets `body_label`.
            body_label = self._new_label()
            # AUTO: Sets `cmp_tmp`.
            cmp_tmp = self._new_temp()

            # AUTO: Calls `self._emit`.
            self._emit("==", switch_expr, case_val, cmp_tmp)
            # AUTO: Calls `self._emit`.
            self._emit("IFFALSE", cmp_tmp, None, next_label)
            # AUTO: Calls `self._emit`.
            self._emit("LABEL", None, None, body_label)

            # AUTO: Calls `self._declaration`.
            self._declaration()
            # AUTO: Calls `self._case_statements`.
            self._case_statements()

            # AUTO: Checks this condition.
            if self._peek().type == "prune":
                # AUTO: Calls `self._advance`.
                self._advance()
                # AUTO: Calls `self._expect`.
                self._expect(";")

            # AUTO: Calls `self._emit`.
            self._emit("GOTO", None, None, end_label)
            # AUTO: Calls `self._emit`.
            self._emit("LABEL", None, None, next_label)

    # AUTO: Defines function `_case_statements`.
    def _case_statements(self):
        # AUTO: Repeats while this condition is true.
        while self._peek().type not in ("variety", "soil", "}", "prune", "EOF"):
            # AUTO: Sets `tok`.
            tok = self._peek()
            # AUTO: Checks this condition.
            if tok.type == "id":
                # AUTO: Calls `self._id_stmt`.
                self._id_stmt()
            # AUTO: Checks the next alternate condition.
            elif tok.type == "water":
                # AUTO: Calls `self._io_stmt`.
                self._io_stmt()
            # AUTO: Checks the next alternate condition.
            elif tok.type == "plant":
                # AUTO: Calls `self._io_stmt`.
                self._io_stmt()
            # AUTO: Checks the next alternate condition.
            elif tok.type == "skip":
                # AUTO: Calls `self._advance`.
                self._advance()
                # AUTO: Calls `self._expect`.
                self._expect(";")
            # AUTO: Checks the next alternate condition.
            elif tok.type == "reclaim":
                # AUTO: Calls `self._return_stmt`.
                self._return_stmt()
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Stops the nearest loop.
                break

    # AUTO: Defines function `_default_opt`.
    def _default_opt(self, end_label: str):
        # AUTO: Checks this condition.
        if self._peek().type == "soil":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Calls `self._expect`.
            self._expect(":")
            # AUTO: Calls `self._declaration`.
            self._declaration()
            # AUTO: Calls `self._case_statements`.
            self._case_statements()


    # AUTO: Defines function `_control_stmt`.
    def _control_stmt(self):
        # AUTO: Sets `tok`.
        tok = self._advance()
        # AUTO: Calls `self._expect`.
        self._expect(";")
        # AUTO: Checks this condition.
        if tok.type == "prune":
            # AUTO: Calls `self._emit`.
            self._emit("GOTO", None, None, "BREAK")
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Calls `self._emit`.
            self._emit("GOTO", None, None, "CONTINUE")


    # AUTO: Defines function `_expression`.
    def _expression(self) -> str:
        # AUTO: Sets `left`.
        left = self._logic_or()
        # AUTO: Checks this condition.
        if self._peek().type not in ASSIGN_OPS:
            # AUTO: Returns this result to the caller.
            return left

        # AUTO: Sets `op_tok`.
        op_tok = self._advance()
        # AUTO: Sets `right`.
        right = self._expression()
        # AUTO: Checks this condition.
        if op_tok.type == "=":
            # AUTO: Sets `self._emit("`.
            self._emit("=", right, None, left)
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Sets `tmp`.
            tmp = self._new_temp()
            # AUTO: Calls `self._emit`.
            self._emit(op_tok.type[0], left, right, tmp)
            # AUTO: Sets `self._emit("`.
            self._emit("=", tmp, None, left)
        # AUTO: Returns this result to the caller.
        return left

    # AUTO: Defines function `_logic_or`.
    def _logic_or(self) -> str:
        # AUTO: Sets `left`.
        left = self._logic_and()
        # AUTO: Repeats while this condition is true.
        while self._peek().type == "||":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Sets `right`.
            right = self._logic_and()
            # AUTO: Sets `tmp`.
            tmp = self._new_temp()
            # AUTO: Calls `self._emit`.
            self._emit("||", left, right, tmp)
            # AUTO: Sets `left`.
            left = tmp
        # AUTO: Returns this result to the caller.
        return left

    # AUTO: Defines function `_logic_and`.
    def _logic_and(self) -> str:
        # AUTO: Sets `left`.
        left = self._relational()
        # AUTO: Repeats while this condition is true.
        while self._peek().type == "&&":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Sets `right`.
            right = self._relational()
            # AUTO: Sets `tmp`.
            tmp = self._new_temp()
            # AUTO: Calls `self._emit`.
            self._emit("&&", left, right, tmp)
            # AUTO: Sets `left`.
            left = tmp
        # AUTO: Returns this result to the caller.
        return left

    # AUTO: Defines function `_relational`.
    def _relational(self) -> str:
        # AUTO: Sets `left`.
        left = self._arithmetic()
        # AUTO: Checks this condition.
        if self._peek().type in (">", "<", ">=", "<=", "==", "!="):
            # AUTO: Sets `op`.
            op = self._advance().type
            # AUTO: Sets `right`.
            right = self._arithmetic()
            # AUTO: Sets `tmp`.
            tmp = self._new_temp()
            # AUTO: Calls `self._emit`.
            self._emit(op, left, right, tmp)
            # AUTO: Returns this result to the caller.
            return tmp
        # AUTO: Returns this result to the caller.
        return left

    # AUTO: Defines function `_arithmetic`.
    def _arithmetic(self) -> str:
        # AUTO: Sets `left`.
        left = self._term()
        # AUTO: Repeats while this condition is true.
        while self._peek().type in ("+", "-"):
            # AUTO: Sets `op`.
            op = self._advance().type
            # AUTO: Sets `right`.
            right = self._term()
            # AUTO: Sets `tmp`.
            tmp = self._new_temp()
            # AUTO: Calls `self._emit`.
            self._emit(op, left, right, tmp)
            # AUTO: Sets `left`.
            left = tmp
        # AUTO: Returns this result to the caller.
        return left

    # AUTO: Defines function `_term`.
    def _term(self) -> str:
        # AUTO: Sets `left`.
        left = self._power()
        # AUTO: Repeats while this condition is true.
        while self._peek().type in ("*", "/", "%"):
            # AUTO: Sets `op`.
            op = self._advance().type
            # AUTO: Sets `right`.
            right = self._power()
            # AUTO: Sets `tmp`.
            tmp = self._new_temp()
            # AUTO: Calls `self._emit`.
            self._emit(op, left, right, tmp)
            # AUTO: Sets `left`.
            left = tmp
        # AUTO: Returns this result to the caller.
        return left

    # AUTO: Defines function `_power`.
    def _power(self) -> str:
        # AUTO: Sets `left`.
        left = self._factor()
        # AUTO: Checks this condition.
        if self._peek().type == "**":
            # AUTO: Sets `op`.
            op = self._advance().type
            # AUTO: Sets `right`.
            right = self._power()
            # AUTO: Sets `tmp`.
            tmp = self._new_temp()
            # AUTO: Calls `self._emit`.
            self._emit(op, left, right, tmp)
            # AUTO: Returns this result to the caller.
            return tmp
        # AUTO: Returns this result to the caller.
        return left

    # AUTO: Defines function `_factor`.
    def _factor(self) -> str:
        # AUTO: Sets `tok`.
        tok = self._peek()

        # AUTO: Checks this condition.
        if tok.type == "(":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Sets `val`.
            val = self._expression()
            # AUTO: Calls `self._expect`.
            self._expect(")")
            # AUTO: Returns this result to the caller.
            return val

        # AUTO: Checks this condition.
        if tok.type in ("~", "!"):
            # AUTO: Sets `op`.
            op = self._advance()
            # AUTO: Sets `inner`.
            inner = self._factor()
            # AUTO: Sets `tmp`.
            tmp = self._new_temp()
            # AUTO: Checks this condition.
            if op.type == "~":
                # AUTO: Calls `self._emit`.
                self._emit("UNARY_MINUS", inner, None, tmp)
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Calls `self._emit`.
                self._emit("NOT", inner, None, tmp)
            # AUTO: Returns this result to the caller.
            return tmp

        # AUTO: Checks this condition.
        if tok.type == "id":
            # AUTO: Sets `id_tok`.
            id_tok = self._advance()
            # AUTO: Sets `nxt`.
            nxt = self._peek()

            # AUTO: Checks this condition.
            if nxt.type == "(":
                # AUTO: Calls `self._advance`.
                self._advance()
                # AUTO: Sets `args`.
                args = self._arguments()
                # AUTO: Calls `self._expect`.
                self._expect(")")
                # AUTO: Starts a loop over these values.
                for a in args:
                    # AUTO: Calls `self._emit`.
                    self._emit("PARAM", a)
                # AUTO: Sets `tmp`.
                tmp = self._new_temp()
                # AUTO: Calls `self._emit`.
                self._emit("CALL", id_tok.value, str(len(args)), tmp)
                # AUTO: Returns this result to the caller.
                return tmp

            # AUTO: Checks this condition.
            if nxt.type == "[":
                # AUTO: Calls `self._advance`.
                self._advance()
                # AUTO: Sets `idx`.
                idx = self._expression()
                # AUTO: Calls `self._expect`.
                self._expect("]")
                # AUTO: Repeats while this condition is true.
                while self._peek().type == "[":
                    # AUTO: Calls `self._advance`.
                    self._advance()
                    # AUTO: Sets `idx2`.
                    idx2 = self._expression()
                    # AUTO: Calls `self._expect`.
                    self._expect("]")
                    # AUTO: Sets `tmp`.
                    tmp = self._new_temp()
                    # AUTO: Calls `self._emit`.
                    self._emit("*", idx, idx2, tmp)
                    # AUTO: Sets `idx`.
                    idx = tmp
                # AUTO: Sets `location`.
                location = f"{id_tok.value}[{idx}]"
                # AUTO: Checks this condition.
                if self._peek().type in ASSIGN_OPS:
                    # AUTO: Returns this result to the caller.
                    return location
                # AUTO: Sets `tmp`.
                tmp = self._new_temp()
                # AUTO: Calls `self._emit`.
                self._emit("ARRAY_LOAD", id_tok.value, idx, tmp)
                # AUTO: Returns this result to the caller.
                return tmp

            # AUTO: Checks this condition.
            if nxt.type == ".":
                # AUTO: Calls `self._advance`.
                self._advance()
                # AUTO: Sets `member`.
                member = self._expect("id")
                # AUTO: Sets `chain`.
                chain = member.value
                # AUTO: Repeats while this condition is true.
                while self._peek().type == ".":
                    # AUTO: Calls `self._advance`.
                    self._advance()
                    # AUTO: Sets `m2`.
                    m2 = self._expect("id")
                    # AUTO: Sets `chain`.
                    chain = f"{chain}.{m2.value}"
                # AUTO: Sets `location`.
                location = f"{id_tok.value}.{chain}"
                # AUTO: Checks this condition.
                if self._peek().type in ASSIGN_OPS:
                    # AUTO: Returns this result to the caller.
                    return location
                # AUTO: Sets `tmp`.
                tmp = self._new_temp()
                # AUTO: Calls `self._emit`.
                self._emit("STRUCT_LOAD", id_tok.value, chain, tmp)
                # AUTO: Returns this result to the caller.
                return tmp

            # AUTO: Returns this result to the caller.
            return id_tok.value

        # AUTO: Checks this condition.
        if tok.type == "intlit":
            # AUTO: Returns this result to the caller.
            return self._advance().value
        # AUTO: Checks this condition.
        if tok.type == "dblit":
            # AUTO: Returns this result to the caller.
            return self._advance().value
        # AUTO: Checks this condition.
        if tok.type == "chrlit":
            # AUTO: Returns this result to the caller.
            return self._advance().value
        # AUTO: Checks this condition.
        if tok.type == "stringlit":
            # AUTO: Returns this result to the caller.
            return self._advance().value
        # AUTO: Checks this condition.
        if tok.type == "sunshine":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Returns this result to the caller.
            return "true"
        # AUTO: Checks this condition.
        if tok.type == "frost":
            # AUTO: Calls `self._advance`.
            self._advance()
            # AUTO: Returns this result to the caller.
            return "false"

        # AUTO: Appends a value to a list.
        self.errors.append(f"ICG Line {tok.line}: unexpected token in expression: '{tok.type}'")
        # AUTO: Calls `self._advance`.
        self._advance()
        # AUTO: Returns this result to the caller.
        return "???"


    # AUTO: Defines function `_arguments`.
    def _arguments(self) -> List[str]:
        # AUTO: Sets `args: List[str]`.
        args: List[str] = []
        # AUTO: Checks this condition.
        if self._peek().type in (")", "EOF"):
            # AUTO: Returns this result to the caller.
            return args
        # AUTO: Appends a value to a list.
        args.append(self._expression())
        # AUTO: Repeats while this condition is true.
        while self._match(","):
            # AUTO: Appends a value to a list.
            args.append(self._expression())
        # AUTO: Returns this result to the caller.
        return args


# AUTO: Defines function `generate_icg`.
def generate_icg(tokens: List[Any]) -> Dict[str, Any]:
    # AUTO: Sets `gen`.
    gen = ICGenerator(tokens)
    # AUTO: Sets `code, errors`.
    code, errors = gen.generate()

    # AUTO: Sets `tac_dicts`.
    tac_dicts = [instr.to_dict() for instr in code]
    # AUTO: Sets `tac_text`.
    tac_text = "\n".join(str(instr) for instr in code)

    # AUTO: Returns this result to the caller.
    return {
        # AUTO: Executes this statement.
        "success": len(errors) == 0,
        # AUTO: Executes this statement.
        "tac": tac_dicts,
        # AUTO: Executes this statement.
        "tac_text": tac_text,
        # AUTO: Executes this statement.
        "errors": errors,
    # AUTO: Closes the current grouped code/data.
    }
