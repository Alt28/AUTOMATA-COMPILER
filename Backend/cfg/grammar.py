"""System CFG and LL(1) helper-set generation for GrowALanguage.

The parser imports cfg, first_sets, and predict_sets from this file. The grammar
is written as productions, then FIRST/FOLLOW/PREDICT sets are computed from it.
"""

# AUTO: Imports a module used by this file.
import sys
# AUTO: Imports names from another module.
from collections import defaultdict

# AUTO: Checks this condition.
if sys.platform == 'win32':
    # AUTO: Starts protected code that can catch errors.
    try:
        # AUTO: Sets `sys.stdout.reconfigure(encoding`.
        sys.stdout.reconfigure(encoding='utf-8')
    # AUTO: Executes this statement.
    except:
        # AUTO: Does nothing for this required block.
        pass

# AUTO: Sets `EPSILON`.
EPSILON = "λ"


# AUTO: Defines function `compute_first`.
def compute_first(cfg):
    # GUIDE: FIRST(A) answers what token can begin strings derived from A.
    # AUTO: Sets `first`.
    first = defaultdict(set)
    # AUTO: Sets `epsilon`.
    epsilon = EPSILON

    # AUTO: Starts a loop over these values.
    for lhs, productions in cfg.items():
        # AUTO: Starts a loop over these values.
        for prod in productions:
            # AUTO: Checks this condition.
            if not prod:
                # AUTO: Skips to the next loop iteration.
                continue
            # AUTO: Checks this condition.
            if prod[0] == epsilon:
                # AUTO: Calls `first[lhs].add`.
                first[lhs].add(epsilon)
            # AUTO: Checks the next alternate condition.
            elif prod[0] not in cfg:
                # AUTO: Calls `first[lhs].add`.
                first[lhs].add(prod[0])

    # AUTO: Sets `changed`.
    changed = True
    # AUTO: Repeats while this condition is true.
    while changed:
        # AUTO: Sets `changed`.
        changed = False
        # AUTO: Starts a loop over these values.
        for lhs, productions in cfg.items():
            # AUTO: Starts a loop over these values.
            for prod in productions:
                # AUTO: Sets `before`.
                before = len(first[lhs])

                # AUTO: Starts a loop over these values.
                for symbol in prod:
                    # AUTO: Checks this condition.
                    if symbol in cfg:
                        # AUTO: Sets `first[lhs] |`.
                        first[lhs] |= (first[symbol] - {epsilon})
                        # AUTO: Checks this condition.
                        if epsilon not in first[symbol]:
                            # AUTO: Stops the nearest loop.
                            break
                    # AUTO: Runs when previous condition did not pass.
                    else:
                        # AUTO: Checks this condition.
                        if symbol != epsilon:
                            # AUTO: Calls `first[lhs].add`.
                            first[lhs].add(symbol)
                        # AUTO: Stops the nearest loop.
                        break
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Calls `first[lhs].add`.
                    first[lhs].add(epsilon)

                # AUTO: Checks this condition.
                if len(first[lhs]) > before:
                    # AUTO: Sets `changed`.
                    changed = True

    # AUTO: Returns this result to the caller.
    return first


# AUTO: Defines function `compute_follow`.
def compute_follow(cfg, first):
    # GUIDE: FOLLOW(A) answers what token can appear immediately after A.
    # AUTO: Sets `follow`.
    follow = defaultdict(set)
    # AUTO: Sets `epsilon`.
    epsilon = EPSILON

    # AUTO: Sets `start_symbol`.
    start_symbol = next(iter(cfg))
    # AUTO: Calls `follow[start_symbol].add`.
    follow[start_symbol].add("EOF")

    # AUTO: Sets `changed`.
    changed = True
    # AUTO: Repeats while this condition is true.
    while changed:
        # AUTO: Sets `changed`.
        changed = False
        # AUTO: Starts a loop over these values.
        for lhs, productions in cfg.items():
            # AUTO: Starts a loop over these values.
            for prod in productions:
                # AUTO: Starts a loop over these values.
                for i, symbol in enumerate(prod):
                    # AUTO: Checks this condition.
                    if symbol in cfg:
                        # AUTO: Sets `before`.
                        before = len(follow[symbol])

                        # AUTO: Sets `j`.
                        j = i + 1
                        # AUTO: Repeats while this condition is true.
                        while j < len(prod):
                            # AUTO: Sets `next_symbol`.
                            next_symbol = prod[j]
                            # AUTO: Checks this condition.
                            if next_symbol in cfg:
                                # AUTO: Sets `follow[symbol] |`.
                                follow[symbol] |= (first[next_symbol] - {epsilon})
                                # AUTO: Checks this condition.
                                if epsilon not in first[next_symbol]:
                                    # AUTO: Stops the nearest loop.
                                    break
                            # AUTO: Runs when previous condition did not pass.
                            else:
                                # AUTO: Checks this condition.
                                if next_symbol != epsilon:
                                    # AUTO: Calls `follow[symbol].add`.
                                    follow[symbol].add(next_symbol)
                                # AUTO: Stops the nearest loop.
                                break
                            # AUTO: Adds into `j`.
                            j += 1
                        # AUTO: Runs when previous condition did not pass.
                        else:
                            # AUTO: Sets `follow[symbol] |`.
                            follow[symbol] |= follow[lhs]

                        # AUTO: Checks this condition.
                        if len(follow[symbol]) > before:
                            # AUTO: Sets `changed`.
                            changed = True

    # AUTO: Returns this result to the caller.
    return follow


# AUTO: Defines function `compute_predict`.
def compute_predict(cfg, first, follow):
    # GUIDE: PREDICT chooses a production using one lookahead token.
    # AUTO: Sets `predict`.
    predict = {}
    # AUTO: Sets `epsilon`.
    epsilon = EPSILON

    # AUTO: Starts a loop over these values.
    for lhs, productions in cfg.items():
        # AUTO: Starts a loop over these values.
        for prod in productions:
            # AUTO: Sets `key`.
            key = (lhs, tuple(prod))
            # AUTO: Sets `predict[key]`.
            predict[key] = set()

            # AUTO: Checks this condition.
            if not prod or (len(prod) == 1 and prod[0] == epsilon):
                # AUTO: Sets `predict[key]`.
                predict[key] = follow[lhs].copy()
                # AUTO: Skips to the next loop iteration.
                continue

            # AUTO: Sets `first_set`.
            first_set = set()
            # AUTO: Starts a loop over these values.
            for symbol in prod:
                # AUTO: Checks this condition.
                if symbol in cfg:
                    # AUTO: Sets `first_set |`.
                    first_set |= (first[symbol] - {epsilon})
                    # AUTO: Checks this condition.
                    if epsilon not in first[symbol]:
                        # AUTO: Stops the nearest loop.
                        break
                # AUTO: Runs when previous condition did not pass.
                else:
                    # AUTO: Checks this condition.
                    if symbol != epsilon:
                        # AUTO: Calls `first_set.add`.
                        first_set.add(symbol)
                    # AUTO: Stops the nearest loop.
                    break
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Calls `first_set.add`.
                first_set.add(epsilon)

            # AUTO: Checks this condition.
            if epsilon in first_set:
                # AUTO: Sets `predict[key]`.
                predict[key] = (first_set - {epsilon}) | follow[lhs]
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Sets `predict[key]`.
                predict[key] = first_set

    # AUTO: Returns this result to the caller.
    return predict


# GUIDE: Actual grammar used by parser.py; terminals match lexer token.type values.
# AUTO: Sets `cfg`.
cfg = {
    # AUTO: Executes this statement.
    "<program>": [
        # AUTO: Executes this statement.
        [
            # AUTO: Executes this statement.
            "<global_declaration>",
            # AUTO: Executes this statement.
            "<function_definition>",
            # AUTO: Executes this statement.
            "root",
            # AUTO: Executes this statement.
            "(",
            # AUTO: Executes this statement.
            ")",
            # AUTO: Executes this statement.
            "{",
            # AUTO: Executes this statement.
            "<local_declaration>",
            # AUTO: Executes this statement.
            "<body_statement>",
            # AUTO: Executes this statement.
            "reclaim",
            # AUTO: Executes this statement.
            ";",
            # AUTO: Executes this statement.
            "}",
        # AUTO: Closes the current grouped code/data.
        ]
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<global_declaration>": [
        # AUTO: Executes this statement.
        ["bundle", "id", "<bundle_or_var>", "<global_declaration>"],
        # AUTO: Executes this statement.
        ["<data_type>", "id", "<array_dec>", "<var_value>", ";", "<global_declaration>"],
        # AUTO: Sets `["fertile", "<data_type>", "id", "`.
        ["fertile", "<data_type>", "id", "=", "<init_val>", "<const_next>", ";", "<global_declaration>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<bundle_or_var>": [
        # AUTO: Executes this statement.
        ["{", "<bundle_members>", "}", ";"],
        # AUTO: Executes this statement.
        ["<bundle_mem_dec>", ";"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<local_declaration>": [
        # AUTO: Executes this statement.
        ["<var_dec>", ";", "<local_declaration>"],
        # AUTO: Executes this statement.
        ["<const_dec>", ";", "<local_declaration>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<data_type>": [
        # AUTO: Executes this statement.
        ["seed"],
        # AUTO: Executes this statement.
        ["tree"],
        # AUTO: Executes this statement.
        ["leaf"],
        # AUTO: Executes this statement.
        ["branch"],
        # AUTO: Executes this statement.
        ["vine"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<const_dec>": [
        # AUTO: Sets `["fertile", "<data_type>", "id", "`.
        ["fertile", "<data_type>", "id", "=", "<init_val>", "<const_next>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<const_next>": [
        # AUTO: Sets `[",", "id", "`.
        [",", "id", "=", "<init_val>", "<const_next>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<var_dec>": [
        # AUTO: Executes this statement.
        ["<data_type>", "id", "<array_dec>", "<var_value>"],
        # AUTO: Executes this statement.
        ["bundle", "id", "<bundle_mem_dec>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<bundle_mem_dec>": [
        # AUTO: Executes this statement.
        ["id", "<array_dec>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<var_value>": [
        # AUTO: Sets `["`.
        ["=", "<init_val>", "<var_value_next>"],
        # AUTO: Executes this statement.
        ["<var_value_next>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<var_value_next>": [
        # AUTO: Executes this statement.
        [",", "id", "<array_dec>", "<var_value>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<init_val>": [
        # AUTO: Executes this statement.
        ["<array_init_opt>"],
        # AUTO: Executes this statement.
        ["water", "(", "<water_arg>", ")"],
        # AUTO: Executes this statement.
        ["<expression>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<array_dec>": [
        # AUTO: Executes this statement.
        ["[", "<array_dim_opt>", "]", "<array_dec>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<array_dim_opt>": [
        # AUTO: Executes this statement.
        ["intlit"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<array_init_opt>": [
        # AUTO: Executes this statement.
        ["{", "<init_vals>", "}"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<init_vals>": [
        # AUTO: Executes this statement.
        ["<init_val_item>", "<init_vals_next>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<init_vals_next>": [
        # AUTO: Executes this statement.
        [",", "<init_val_item>", "<init_vals_next>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<init_val_item>": [
        # AUTO: Executes this statement.
        ["{", "<init_vals>", "}"],
        # AUTO: Executes this statement.
        ["<expression>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<bundle_members>": [
        # AUTO: Executes this statement.
        ["<data_type>", "id", ";", "<bundle_members>"],
        # AUTO: Executes this statement.
        ["id", "id", ";", "<bundle_members>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<function_definition>": [
        # AUTO: Executes this statement.
        [
            # AUTO: Executes this statement.
            "pollinate",
            # AUTO: Executes this statement.
            "<return_type>",
            # AUTO: Executes this statement.
            "id",
            # AUTO: Executes this statement.
            "(",
            # AUTO: Executes this statement.
            "<parameters>",
            # AUTO: Executes this statement.
            ")",
            # AUTO: Executes this statement.
            "{",
            # AUTO: Executes this statement.
            "<local_declaration>",
            # AUTO: Executes this statement.
            "<body_statement>",
            # AUTO: Executes this statement.
            "reclaim",
            # AUTO: Executes this statement.
            "<reclaim_value>",
            # AUTO: Executes this statement.
            "}",
            # AUTO: Executes this statement.
            "<function_definition>",
        # AUTO: Closes the current grouped code/data.
        ],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<return_type>": [
        # AUTO: Executes this statement.
        ["<data_type>"],
        # AUTO: Executes this statement.
        ["empty"],
        # AUTO: Executes this statement.
        ["id"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<parameters>": [
        # AUTO: Executes this statement.
        [EPSILON],
        # AUTO: Executes this statement.
        ["<param>", "<param_next>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<param>": [
        # AUTO: Executes this statement.
        ["<data_type>", "id", "<param_array>"],
        # AUTO: Executes this statement.
        ["id", "id"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<param_array>": [
        # AUTO: Executes this statement.
        [EPSILON],
        # AUTO: Executes this statement.
        ["[", "]"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<param_next>": [
        # AUTO: Executes this statement.
        [EPSILON],
        # AUTO: Executes this statement.
        [",", "<param>", "<param_next>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<reclaim_value>": [
        # AUTO: Executes this statement.
        ["<expression>", ";"],
        # AUTO: Executes this statement.
        [";"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<body_statement>": [
        # AUTO: Executes this statement.
        ["<non_reclaim_stmt>", "<body_statement>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<non_reclaim_stmt>": [
        # AUTO: Executes this statement.
        ["id", "<id_stmt>"],
        # AUTO: Executes this statement.
        ["<inc_dec_op>", "id", "<id_next>", ";"],
        # AUTO: Executes this statement.
        ["<io_stmt>"],
        # AUTO: Executes this statement.
        ["<conditional_stmt>"],
        # AUTO: Executes this statement.
        ["<loop_stmt>"],
        # AUTO: Executes this statement.
        ["<switch_stmt>"],
        # AUTO: Executes this statement.
        ["<control_stmt>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<statement>": [
        # AUTO: Executes this statement.
        ["<simple_stmt>", "<statement>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<simple_stmt>": [
        # AUTO: Executes this statement.
        ["<non_reclaim_stmt>"],
        # AUTO: Executes this statement.
        ["reclaim", "<reclaim_value>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<id_stmt>": [
        # AUTO: Executes this statement.
        ["<id_next>", "<id_stmt_tail>"],
        # AUTO: Executes this statement.
        ["(", "<arguments>", ")", ";"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<id_stmt_tail>": [
        # AUTO: Executes this statement.
        ["<assign_op>", "<assign_rhs>", ";"],
        # AUTO: Executes this statement.
        ["<inc_dec_op>", ";"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<assign_rhs>": [
        # AUTO: Executes this statement.
        ["water", "(", "<water_arg>", ")"],
        # AUTO: Executes this statement.
        ["<expression>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<assign_op>": [
        # AUTO: Sets `["`.
        ["="],
        # AUTO: Adds into `["`.
        ["+="],
        # AUTO: Subtracts from `["`.
        ["-="],
        # AUTO: Multiplies into `["`.
        ["*="],
        # AUTO: Divides into `["`.
        ["/="],
        # AUTO: Sets `["%`.
        ["%="],
        # AUTO: Multiplies into `["*`.
        ["**="],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<id_next>": [
        # AUTO: Executes this statement.
        ["<array_access>", "<post_array_access>"],
        # AUTO: Executes this statement.
        ["<struct_access>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<array_access>": [
        # AUTO: Executes this statement.
        ["[", "<expression>", "]", "<array_access_more>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<array_access_more>": [
        # AUTO: Executes this statement.
        ["[", "<expression>", "]", "<array_access_more>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<struct_access>": [
        # AUTO: Executes this statement.
        [".", "id", "<struct_access_more>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<struct_access_more>": [
        # AUTO: Executes this statement.
        [".", "id", "<struct_access_more>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<post_array_access>": [
        # AUTO: Executes this statement.
        [".", "id", "<post_array_access>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<io_stmt>": [
        # AUTO: Executes this statement.
        ["plant", "(", "<arguments>", ")", ";"],
        # AUTO: Executes this statement.
        ["water", "(", "<water_arg>", ")", ";"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<water_arg>": [
        # AUTO: Executes this statement.
        ["<data_type>"],
        # AUTO: Executes this statement.
        ["id", "<water_id_tail>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<water_id_tail>": [
        # AUTO: Executes this statement.
        ["[", "<expression>", "]", "<water_id_tail>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<arguments>": [
        # AUTO: Executes this statement.
        ["<expression>", "<arg_next>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<arg_next>": [
        # AUTO: Executes this statement.
        [",", "<expression>", "<arg_next>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<conditional_stmt>": [
        # AUTO: Executes this statement.
        [
            # AUTO: Executes this statement.
            "spring",
            # AUTO: Executes this statement.
            "(",
            # AUTO: Executes this statement.
            "<expression>",
            # AUTO: Executes this statement.
            ")",
            # AUTO: Executes this statement.
            "{",
            # AUTO: Executes this statement.
            "<local_declaration>",
            # AUTO: Executes this statement.
            "<statement>",
            # AUTO: Executes this statement.
            "}",
            # AUTO: Executes this statement.
            "<elseif_chain>",
            # AUTO: Executes this statement.
            "<else_opt>",
        # AUTO: Closes the current grouped code/data.
        ]
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<elseif_chain>": [
        # AUTO: Executes this statement.
        [
            # AUTO: Executes this statement.
            "bud",
            # AUTO: Executes this statement.
            "(",
            # AUTO: Executes this statement.
            "<expression>",
            # AUTO: Executes this statement.
            ")",
            # AUTO: Executes this statement.
            "{",
            # AUTO: Executes this statement.
            "<local_declaration>",
            # AUTO: Executes this statement.
            "<statement>",
            # AUTO: Executes this statement.
            "}",
            # AUTO: Executes this statement.
            "<elseif_chain>",
        # AUTO: Closes the current grouped code/data.
        ],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<else_opt>": [
        # AUTO: Executes this statement.
        ["wither", "{", "<local_declaration>", "<statement>", "}"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<loop_stmt>": [
        # AUTO: Executes this statement.
        ["grow", "(", "<expression>", ")", "{", "<local_declaration>", "<statement>", "}"],
        
        # AUTO: Executes this statement.
        [
            # AUTO: Executes this statement.
            "cultivate",
            # AUTO: Executes this statement.
            "(",
            # AUTO: Executes this statement.
            "<for_init>",
            # AUTO: Executes this statement.
            ";",
            # AUTO: Executes this statement.
            "<expression>",
            # AUTO: Executes this statement.
            ";",
            # AUTO: Executes this statement.
            "<for_update>",
            # AUTO: Executes this statement.
            ")",
            # AUTO: Executes this statement.
            "{",
            # AUTO: Executes this statement.
            "<local_declaration>",
            # AUTO: Executes this statement.
            "<statement>",
            # AUTO: Executes this statement.
            "}",
        # AUTO: Closes the current grouped code/data.
        ],
        
        # AUTO: Executes this statement.
        ["tend", "{", "<local_declaration>", "<statement>", "}", "grow", "(", "<expression>", ")", ";"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<for_init>": [
        # AUTO: Executes this statement.
        ["<data_type>", "id", "<array_dec>", "<var_value>"],
        # AUTO: Executes this statement.
        ["id", "<id_next>", "<assign_op>", "<expression>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<for_update>": [
        # AUTO: Executes this statement.
        ["id", "<id_next>", "<for_update_tail>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<for_update_tail>": [
        # AUTO: Executes this statement.
        ["<inc_dec_op>"],
        # AUTO: Executes this statement.
        ["<assign_op>", "<expression>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<inc_dec_op>": [
        # AUTO: Executes this statement.
        ["++"],
        # AUTO: Executes this statement.
        ["--"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<switch_stmt>": [
        # AUTO: Executes this statement.
        ["harvest", "(", "<expression>", ")", "{", "<case_list>", "<default_opt>", "}"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<case_list>": [
        # AUTO: Executes this statement.
        [
            # AUTO: Executes this statement.
            "variety",
            # AUTO: Executes this statement.
            "<case_literal>",
            # AUTO: Executes this statement.
            ":",
            # AUTO: Executes this statement.
            "<local_declaration>",
            # AUTO: Executes this statement.
            "<case_statements>",
            # AUTO: Executes this statement.
            "<case_list>",
        # AUTO: Closes the current grouped code/data.
        ],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<case_literal>": [
        # AUTO: Executes this statement.
        ["intlit"],
        # AUTO: Executes this statement.
        ["chrlit"],
        # AUTO: Executes this statement.
        ["sunshine"],
        # AUTO: Executes this statement.
        ["frost"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<case_statements>": [
        # AUTO: Executes this statement.
        ["<case_statement>", "<case_statements>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],
    
    # AUTO: Executes this statement.
    "<case_statement>": [
        # AUTO: Executes this statement.
        ["id", "<id_stmt>"],
        # AUTO: Executes this statement.
        ["<inc_dec_op>", "id", "<id_next>", ";"],
        # AUTO: Executes this statement.
        ["<io_stmt>"],
        # AUTO: Executes this statement.
        ["<conditional_stmt>"],
        # AUTO: Executes this statement.
        ["<loop_stmt>"],
        # AUTO: Executes this statement.
        ["<switch_stmt>"],
        # AUTO: Executes this statement.
        ["{", "<local_declaration>", "<statement>", "}"],
        # AUTO: Executes this statement.
        ["prune", ";"],
        # AUTO: Executes this statement.
        ["skip", ";"],
        # AUTO: Executes this statement.
        ["reclaim", "<reclaim_value>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<default_opt>": [
        # AUTO: Executes this statement.
        ["soil", ":", "<local_declaration>", "<case_statements>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<control_stmt>": [
        # AUTO: Executes this statement.
        ["prune", ";"],
        # AUTO: Executes this statement.
        ["skip", ";"],
    # AUTO: Closes the current grouped code/data.
    ],


    # AUTO: Executes this statement.
    "<expression>": [
        # AUTO: Executes this statement.
        ["<assignment_expression>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<assignment_expression>": [
        # AUTO: Executes this statement.
        ["<logic_or>", "<assignment_expression_next>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<assignment_expression_next>": [
        # AUTO: Executes this statement.
        ["<assign_op>", "<assignment_expression>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<logic_or>": [
        # AUTO: Executes this statement.
        ["<logic_and>", "<logic_or_next>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<logic_or_next>": [
        # AUTO: Executes this statement.
        ["||", "<logic_and>", "<logic_or_next>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<logic_and>": [
        # AUTO: Executes this statement.
        ["<relational>", "<logic_and_next>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<logic_and_next>": [
        # AUTO: Executes this statement.
        ["&&", "<relational>", "<logic_and_next>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<relational>": [
        # AUTO: Executes this statement.
        ["<arithmetic>", "<relational_next>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<relational_next>": [
        # AUTO: Executes this statement.
        ["<relational_op>", "<arithmetic>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<relational_op>": [
        # AUTO: Executes this statement.
        [">"],
        # AUTO: Executes this statement.
        ["<"],
        # AUTO: Executes this statement.
        [">="],
        # AUTO: Executes this statement.
        ["<="],
        # AUTO: Executes this statement.
        ["=="],
        # AUTO: Executes this statement.
        ["!="],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<arithmetic>": [
        # AUTO: Executes this statement.
        ["<term>", "<arithmetic_next>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<arithmetic_next>": [
        # AUTO: Executes this statement.
        ["+", "<term>", "<arithmetic_next>"],
        # AUTO: Executes this statement.
        ["-", "<term>", "<arithmetic_next>"],
        # AUTO: Executes this statement.
        ["`", "<term>", "<arithmetic_next>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],


    # AUTO: Executes this statement.
    "<term>": [
        # AUTO: Executes this statement.
        ["<power>", "<term_next>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<term_next>": [
        # AUTO: Executes this statement.
        ["*", "<power>", "<term_next>"],
        # AUTO: Executes this statement.
        ["/", "<power>", "<term_next>"],
        # AUTO: Executes this statement.
        ["%", "<power>", "<term_next>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<power>": [
        # AUTO: Executes this statement.
        ["<factor>", "<power_next>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<power_next>": [
        # AUTO: Executes this statement.
        ["**", "<power>"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<factor>": [
        # AUTO: Executes this statement.
        ["(", "<paren_expr>"],
        # AUTO: Executes this statement.
        ["<unary_op>", "<factor>"],
        # AUTO: Executes this statement.
        ["id", "<factor_id_next>"],
        # AUTO: Executes this statement.
        ["<literal>"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<literal>": [
        # AUTO: Executes this statement.
        ["intlit"],
        # AUTO: Executes this statement.
        ["dblit"],
        # AUTO: Executes this statement.
        ["chrlit"],
        # AUTO: Executes this statement.
        ["stringlit"],
        # AUTO: Executes this statement.
        ["sunshine"],
        # AUTO: Executes this statement.
        ["frost"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<paren_expr>": [
        # AUTO: Executes this statement.
        ["<data_type>", ")", "<factor>"],
        # AUTO: Executes this statement.
        ["<expression>", ")"],
    # AUTO: Closes the current grouped code/data.
    ],
    
    # AUTO: Executes this statement.
    "<unary_op>": [
        # AUTO: Executes this statement.
        ["~"],
        # AUTO: Executes this statement.
        ["!"],
    # AUTO: Closes the current grouped code/data.
    ],

    # AUTO: Executes this statement.
    "<factor_id_next>": [
        # AUTO: Executes this statement.
        ["<array_access>", "<post_array_access>"],
        # AUTO: Executes this statement.
        ["<struct_access>"],
        # AUTO: Executes this statement.
        ["(", "<arguments>", ")"],
        # AUTO: Executes this statement.
        [EPSILON],
    # AUTO: Closes the current grouped code/data.
    ],
# AUTO: Closes the current grouped code/data.
}


# GUIDE: Build the LL(1) helper sets once at import time.
# AUTO: Sets `first_sets`.
first_sets = compute_first(cfg)
# AUTO: Sets `follow_sets`.
follow_sets = compute_follow(cfg, first_sets)
# AUTO: Sets `predict_sets`.
predict_sets = compute_predict(cfg, first_sets, follow_sets)


# AUTO: Checks this condition.
if __name__ == '__main__':
    # AUTO: Sets `print("`.
    print("=" * 80)
    # AUTO: Calls `print`.
    print("FIRST SETS")
    # AUTO: Sets `print("`.
    print("=" * 80)
    # AUTO: Calls `print`.
    print("Shows which terminals can appear first in each non-terminal")
    # AUTO: Calls `print`.
    print()
    # AUTO: Starts a loop over these values.
    for nt in first_sets:
        # AUTO: Sets `print(f"First({nt})`.
        print(f"First({nt}) = {{ {', '.join(sorted(first_sets[nt]))} }}")

    # AUTO: Sets `print("\n" + "`.
    print("\n" + "=" * 80)
    # AUTO: Calls `print`.
    print("FOLLOW SETS")
    # AUTO: Sets `print("`.
    print("=" * 80)
    # AUTO: Calls `print`.
    print("Shows which terminals can appear after each non-terminal")
    # AUTO: Calls `print`.
    print()
    # AUTO: Starts a loop over these values.
    for nt in follow_sets:
        # AUTO: Sets `print(f"Follow({nt})`.
        print(f"Follow({nt}) = {{ {', '.join(sorted(follow_sets[nt]))} }}")

    # AUTO: Sets `print("\n" + "`.
    print("\n" + "=" * 80)
    # AUTO: Calls `print`.
    print("PREDICT SETS")
    # AUTO: Sets `print("`.
    print("=" * 80)
    # AUTO: Calls `print`.
    print("Shows which terminal triggers each production rule")
    # AUTO: Calls `print`.
    print()
    # AUTO: Starts a loop over these values.
    for (lhs, prod), pset in predict_sets.items():
        # AUTO: Sets `prod_str`.
        prod_str = " ".join(prod)
        # AUTO: Sets `print(f"Predict({lhs} -> {prod_str})`.
        print(f"Predict({lhs} -> {prod_str}) = {{ {', '.join(sorted(pset))} }}")

    # AUTO: Sets `print("\n" + "`.
    print("\n" + "=" * 80)
