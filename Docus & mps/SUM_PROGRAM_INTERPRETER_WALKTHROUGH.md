# Exact Interpreter Walkthrough Pattern

This document explains the exact step-by-step interpreter simulation pattern for the simple sum program.

Project path: `C:\Users\clarence\Downloads\AUTOMATA-COMPILER-main (1)\AUTOMATA-COMPILER-main\my GAL code`

Generated: 2026-06-03 01:13

## Program Example

```gal
root() {
    seed a;
    seed b;
    seed sum;

    plant("Enter 1st number: ");
    water(a);

    plant("Enter 2nd number: ");
    water(b);

    sum = a + b;

    plant("Sum: ", sum);
    reclaim;
}
```

Sample input used in this walkthrough: `a = 5`, `b = 7`.

## Short Rule

For a complete program, the interpreter always starts at `interpret(ProgramNode)`. Then it goes to `eval_program()`. `eval_program()` first stores top-level functions, then creates a manual call to `root()`.

## Exact Walking Pattern With Lines

| Step | File / Line | Code Route | What Happens |
|---|---|---|---|
| 1 | `interpreter.py:121` | `def interpret(self, node):` | Start here. The first node is the whole AST, a `ProgramNode`. |
| 2 | `interpreter.py:122-123` | `if isinstance(node, ProgramNode): return self.eval_program(node)` | Because the node is `ProgramNode`, the interpreter goes to `eval_program()`. |
| 3 | `interpreter.py:210` | `def eval_program(self, node):` | You are now inside the evaluator for the whole program. |
| 4 | `interpreter.py:211-212` | `for child in node.children: self.interpret(child)` | The program has one top-level child: `FunctionDeclarationNode root`. The interpreter sends that child back to `interpret()`. |
| 5 | `interpreter.py:121` | `interpret(child)` | Now the current node is the root function declaration. |
| 6 | `interpreter.py:140-141` | `elif isinstance(node, FunctionDeclarationNode): return self.eval_function_declaration(node)` | Because root is a function declaration, it goes to `eval_function_declaration()`. |
| 7 | `interpreter.py:716` | `def eval_function_declaration(self, node):` | Root is now being registered/saved, not executed yet. |
| 8 | `interpreter.py:717-719` | `return_type = ...; parameters_node = ...; func_name = ...` | Reads root information. `func_name = 'root'`, parameters are empty, return type is root/empty type. |
| 9 | `interpreter.py:721-729` | `params = []` and parameter loop | Because `root()` has no parameters, `params` stays empty. |
| 10 | `interpreter.py:731` | `self.declare_function(func_name, return_type, params, node)` | Calls helper method to save the root function. |
| 11 | `interpreter.py:95-98` | `self.functions[name] = {...}` | Root is saved in `self.functions['root']`. The saved node contains the root body. |
| 12 | `interpreter.py:733` | `return None` | `eval_function_declaration()` ends and returns to the caller. |
| 13 | `interpreter.py:212` | `self.interpret(child)` finishes | The root declaration child is done. Control returns to `eval_program()`. |
| 14 | `interpreter.py:214` | `main_call = FunctionCallNode('root', [], node.line)` | Creates a fake/manual AST node that means `root()` should be called. |
| 15 | `interpreter.py:215` | `return self.interpret(main_call)` | Sends the root call back to `interpret()`. |
| 16 | `interpreter.py:121` | `interpret(main_call)` | Now the current node is `FunctionCallNode root`. |
| 17 | `interpreter.py:150-151` | `elif isinstance(node, FunctionCallNode): return self.eval_function_call(node)` | Because this is a function call, go to `eval_function_call()`. |
| 18 | `interpreter.py:856` | `def eval_function_call(self, node):` | Root will now actually run. |
| 19 | `interpreter.py:857-858` | `function_name = node.value; args = [...]` | For root, `function_name = 'root'` and `args = []`. |
| 20 | `interpreter.py:860-865` | `lookup_function`, `expected_params`, `function_node` | Finds the saved root function in `self.functions` and gets its body node. |
| 21 | `interpreter.py:873` | `self.enter_scope()` | Creates a new runtime scope for variables inside root. |
| 22 | `interpreter.py:883-884` | `self.eval_block(function_node.children[2])` | Starts executing the root body block. |
| 23 | `interpreter.py:735-737` | `for statement in block_node.children: self.interpret(statement)` | Runs each root statement one by one. |

## Root Body Statement Pattern

| Step | GAL Statement | Interpreter Route | Runtime Effect |
|---|---|---|---|
| 24 | `seed a;` | `interpret(VariableDeclarationNode)` -> `eval_variable_declaration()` line `218` | Declares `a` with default seed value `0`. |
| 25 | `seed b;` | `interpret(VariableDeclarationNode)` -> `eval_variable_declaration()` | Declares `b = 0`. |
| 26 | `seed sum;` | `interpret(VariableDeclarationNode)` -> `eval_variable_declaration()` | Declares `sum = 0`. |
| 27 | `plant("Enter 1st number: ");` | `interpret(PrintNode)` -> `eval_print()` line `752` | Outputs `Enter 1st number:`. |
| 28 | `water(a);` | `interpret(AssignmentNode)` -> `eval_assignment()` line `346` -> `eval_input()` line `1348` | Asks input for `a`; if user enters `5`, stores `a = 5`. |
| 29 | `plant("Enter 2nd number: ");` | `interpret(PrintNode)` -> `eval_print()` | Outputs `Enter 2nd number:`. |
| 30 | `water(b);` | `interpret(AssignmentNode)` -> `eval_assignment()` -> `eval_input()` | Asks input for `b`; if user enters `7`, stores `b = 7`. |
| 31 | `sum = a + b;` | `interpret(AssignmentNode)` -> `eval_assignment()` -> `interpret(BinaryOpNode)` -> `eval_binary_op()` line `510` | Looks up `a = 5`, `b = 7`, computes `5 + 7 = 12`, stores `sum = 12`. |
| 32 | `plant("Sum: ", sum);` | `interpret(PrintNode)` -> `eval_print()` | Prints `Sum:  12`. There are two spaces because the string already has a space and print joins arguments with a space. |
| 33 | `reclaim;` | `interpret(ReturnNode)` -> `eval_return()` line `851` | Raises `ReturnValue(None)` to stop root. |
| 34 | Return catch | `eval_function_call()` lines `886-887` | Catches `ReturnValue` and returns from root. |
| 35 | Scope cleanup | `eval_function_call()` lines `891-892` | Runs `self.exit_scope()`. Root scope is removed. Program ends. |

## Variable Table During Runtime

| Moment | a | b | sum |
|---|---|---|---|
| After declarations | 0 | 0 | 0 |
| After `water(a)` input `5` | 5 | 0 | 0 |
| After `water(b)` input `7` | 5 | 7 | 0 |
| After `sum = a + b` | 5 | 7 | 12 |
| After final print | 5 | 7 | 12 |

## Final Output

```text
Enter 1st number:
Enter 2nd number:
Sum:  12
```

## One-Line Pattern To Memorize

```text
interpret(ProgramNode)
-> eval_program()
-> interpret(FunctionDeclarationNode root)
-> eval_function_declaration()
-> declare_function() saves root
-> back to eval_program()
-> create FunctionCallNode('root')
-> interpret(FunctionCallNode root)
-> eval_function_call()
-> eval_block(root body)
-> each statement goes back to interpret()
-> matching eval_* function runs
-> reclaim ends root
```

## Defense Script

```text
Sa interpreter, nagsisimula siya sa interpret gamit ang ProgramNode. Dahil ProgramNode siya, papasok siya sa eval_program. Sa eval_program, una niyang niloloop ang node.children. Sa sample na ito, ang child lang ay root function declaration. Pinapasa niya iyon ulit sa interpret, tapos dahil FunctionDeclarationNode siya, pupunta sa eval_function_declaration. Doon kinukuha ang function name, return type, and parameters, then sine-save ang root sa self.functions gamit declare_function.

Pag tapos nang ma-save ang root, babalik siya sa eval_program. Tapos gagawa siya ng FunctionCallNode('root'), meaning tatawagin na niya ang root. Ipapasa ulit iyon sa interpret, then dahil FunctionCallNode na siya, pupunta sa eval_function_call. Sa eval_function_call, hahanapin niya ang saved root, gagawa ng scope, then tatawagin ang eval_block para patakbuhin isa-isa ang statements sa loob ng root.

Sa eval_block, bawat statement bumabalik sa interpret. Kaya seed a goes to eval_variable_declaration, plant goes to eval_print, water goes to eval_assignment then eval_input, sum = a + b goes to eval_assignment then eval_binary_op, and reclaim goes to eval_return para matapos ang root.
```