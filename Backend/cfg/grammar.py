import sys
from collections import defaultdict

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

EPSILON = "λ"


def compute_first(cfg):
    first = defaultdict(set)
    epsilon = EPSILON

    for lhs, productions in cfg.items():
        for prod in productions:
            if not prod:
                continue
            if prod[0] == epsilon:
                first[lhs].add(epsilon)
            elif prod[0] not in cfg:
                first[lhs].add(prod[0])

    changed = True
    while changed:
        changed = False
        for lhs, productions in cfg.items():
            for prod in productions:
                before = len(first[lhs])

                for symbol in prod:
                    if symbol in cfg:
                        first[lhs] |= (first[symbol] - {epsilon})
                        if epsilon not in first[symbol]:
                            break
                    else:
                        if symbol != epsilon:
                            first[lhs].add(symbol)
                        break
                else:
                    first[lhs].add(epsilon)

                if len(first[lhs]) > before:
                    changed = True

    return first


def compute_follow(cfg, first):
    follow = defaultdict(set)
    epsilon = EPSILON

    start_symbol = next(iter(cfg))
    follow[start_symbol].add("EOF")

    changed = True
    while changed:
        changed = False
        for lhs, productions in cfg.items():
            for prod in productions:
                for i, symbol in enumerate(prod):
                    if symbol in cfg:
                        before = len(follow[symbol])

                        j = i + 1
                        while j < len(prod):
                            next_symbol = prod[j]
                            if next_symbol in cfg:
                                follow[symbol] |= (first[next_symbol] - {epsilon})
                                if epsilon not in first[next_symbol]:
                                    break
                            else:
                                if next_symbol != epsilon:
                                    follow[symbol].add(next_symbol)
                                break
                            j += 1
                        else:
                            follow[symbol] |= follow[lhs]

                        if len(follow[symbol]) > before:
                            changed = True

    return follow


def compute_predict(cfg, first, follow):
    predict = {}
    epsilon = EPSILON

    for lhs, productions in cfg.items():
        for prod in productions:
            key = (lhs, tuple(prod))
            predict[key] = set()

            if not prod or (len(prod) == 1 and prod[0] == epsilon):
                predict[key] = follow[lhs].copy()
                continue

            first_set = set()
            for symbol in prod:
                if symbol in cfg:
                    first_set |= (first[symbol] - {epsilon})
                    if epsilon not in first[symbol]:
                        break
                else:
                    if symbol != epsilon:
                        first_set.add(symbol)
                    break
            else:
                first_set.add(epsilon)

            if epsilon in first_set:
                predict[key] = (first_set - {epsilon}) | follow[lhs]
            else:
                predict[key] = first_set

    return predict


cfg = {
    "<program>": [
        [
            "<global_declaration>",
            "<function_definition>",
            "root",
            "(",
            ")",
            "{",
            "<local_declaration>",
            "<body_statement>",
            "reclaim",
            ";",
            "}",
        ]
    ],

    "<global_declaration>": [
        ["bundle", "id", "<bundle_or_var>", "<global_declaration>"],
        ["<data_type>", "id", "<array_dec>", "<var_value>", ";", "<global_declaration>"],
        ["fertile", "<data_type>", "id", "=", "<init_val>", "<const_next>", ";", "<global_declaration>"],
        [EPSILON],
    ],

    "<bundle_or_var>": [
        ["{", "<bundle_members>", "}", ";"],
        ["<bundle_mem_dec>", ";"],
    ],

    "<local_declaration>": [
        ["<var_dec>", ";", "<local_declaration>"],
        ["<const_dec>", ";", "<local_declaration>"],
        [EPSILON],
    ],

    "<data_type>": [
        ["seed"],
        ["tree"],
        ["leaf"],
        ["branch"],
        ["vine"],
    ],

    "<const_dec>": [
        ["fertile", "<data_type>", "id", "=", "<init_val>", "<const_next>"],
    ],

    "<const_next>": [
        [",", "id", "=", "<init_val>", "<const_next>"],
        [EPSILON],
    ],

    "<var_dec>": [
        ["<data_type>", "id", "<array_dec>", "<var_value>"],
        ["bundle", "id", "<bundle_mem_dec>"],
    ],

    "<bundle_mem_dec>": [
        ["id", "<array_dec>"],
    ],

    "<var_value>": [
        ["=", "<init_val>", "<var_value_next>"],
        ["<var_value_next>"],
    ],

    "<var_value_next>": [
        [",", "id", "<array_dec>", "<var_value>"],
        [EPSILON],
    ],

    "<init_val>": [
        ["<array_init_opt>"],
        ["water", "(", "<water_arg>", ")"],
        ["<expression>"],
    ],

    "<array_dec>": [
        ["[", "<array_dim_opt>", "]", "<array_dec>"],
        [EPSILON],
    ],

    "<array_dim_opt>": [
        ["intlit"],
        [EPSILON],
    ],

    "<array_init_opt>": [
        ["{", "<init_vals>", "}"],
    ],

    "<init_vals>": [
        ["<init_val_item>", "<init_vals_next>"],
        [EPSILON],
    ],

    "<init_vals_next>": [
        [",", "<init_val_item>", "<init_vals_next>"],
        [EPSILON],
    ],

    "<init_val_item>": [
        ["{", "<init_vals>", "}"],
        ["<expression>"],
    ],

    "<bundle_members>": [
        ["<data_type>", "id", ";", "<bundle_members>"],
        ["id", "id", ";", "<bundle_members>"],
        [EPSILON],
    ],

    "<function_definition>": [
        [
            "pollinate",
            "<return_type>",
            "id",
            "(",
            "<parameters>",
            ")",
            "{",
            "<local_declaration>",
            "<body_statement>",
            "reclaim",
            "<reclaim_value>",
            "}",
            "<function_definition>",
        ],
        [EPSILON],
    ],

    "<return_type>": [
        ["<data_type>"],
        ["empty"],
        ["id"],
    ],

    "<parameters>": [
        [EPSILON],
        ["<param>", "<param_next>"],
    ],

    "<param>": [
        ["<data_type>", "id", "<param_array>"],
        ["id", "id"],
    ],

    "<param_array>": [
        [EPSILON],
        ["[", "]"],
    ],

    "<param_next>": [
        [EPSILON],
        [",", "<param>", "<param_next>"],
    ],

    "<reclaim_value>": [
        ["<expression>", ";"],
        [";"],
    ],

    "<body_statement>": [
        ["<non_reclaim_stmt>", "<body_statement>"],
        [EPSILON],
    ],

    "<non_reclaim_stmt>": [
        ["id", "<id_stmt>"],
        ["<inc_dec_op>", "id", "<id_next>", ";"],
        ["<io_stmt>"],
        ["<conditional_stmt>"],
        ["<loop_stmt>"],
        ["<switch_stmt>"],
        ["<control_stmt>"],
    ],

    "<statement>": [
        ["<simple_stmt>", "<statement>"],
        [EPSILON],
    ],

    "<simple_stmt>": [
        ["<non_reclaim_stmt>"],
        ["reclaim", "<reclaim_value>"],
    ],

    "<id_stmt>": [
        ["<id_next>", "<id_stmt_tail>"],
        ["(", "<arguments>", ")", ";"],
    ],

    "<id_stmt_tail>": [
        ["<assign_op>", "<assign_rhs>", ";"],
        ["<inc_dec_op>", ";"],
    ],

    "<assign_rhs>": [
        ["water", "(", "<water_arg>", ")"],
        ["<expression>"],
    ],

    "<assign_op>": [
        ["="],
        ["+="],
        ["-="],
        ["*="],
        ["/="],
        ["%="],
        ["**="],
    ],

    "<id_next>": [
        ["<array_access>", "<post_array_access>"],
        ["<struct_access>"],
        [EPSILON],
    ],

    "<array_access>": [
        ["[", "<expression>", "]", "<array_access_more>"],
    ],

    "<array_access_more>": [
        ["[", "<expression>", "]", "<array_access_more>"],
        [EPSILON],
    ],

    "<struct_access>": [
        [".", "id", "<struct_access_more>"],
    ],

    "<struct_access_more>": [
        [".", "id", "<struct_access_more>"],
        [EPSILON],
    ],

    "<post_array_access>": [
        [".", "id", "<post_array_access>"],
        [EPSILON],
    ],

    "<io_stmt>": [
        ["plant", "(", "<arguments>", ")", ";"],
        ["water", "(", "<water_arg>", ")", ";"],
    ],

    "<water_arg>": [
        ["<data_type>"],
        ["id", "<water_id_tail>"],
        [EPSILON],
    ],

    "<water_id_tail>": [
        ["[", "<expression>", "]", "<water_id_tail>"],
        [EPSILON],
    ],

    "<arguments>": [
        ["<expression>", "<arg_next>"],
        [EPSILON],
    ],

    "<arg_next>": [
        [",", "<expression>", "<arg_next>"],
        [EPSILON],
    ],

    "<conditional_stmt>": [
        [
            "spring",
            "(",
            "<expression>",
            ")",
            "{",
            "<local_declaration>",
            "<statement>",
            "}",
            "<elseif_chain>",
            "<else_opt>",
        ]
    ],

    "<elseif_chain>": [
        [
            "bud",
            "(",
            "<expression>",
            ")",
            "{",
            "<local_declaration>",
            "<statement>",
            "}",
            "<elseif_chain>",
        ],
        [EPSILON],
    ],

    "<else_opt>": [
        ["wither", "{", "<local_declaration>", "<statement>", "}"],
        [EPSILON],
    ],

    "<loop_stmt>": [
        ["grow", "(", "<expression>", ")", "{", "<local_declaration>", "<statement>", "}"],
        
        [
            "cultivate",
            "(",
            "<for_init>",
            ";",
            "<expression>",
            ";",
            "<for_update>",
            ")",
            "{",
            "<local_declaration>",
            "<statement>",
            "}",
        ],
        
        ["tend", "{", "<local_declaration>", "<statement>", "}", "grow", "(", "<expression>", ")", ";"],
    ],

    "<for_init>": [
        ["<data_type>", "id", "<array_dec>", "<var_value>"],
        ["id", "<id_next>", "<assign_op>", "<expression>"],
        [EPSILON],
    ],

    "<for_update>": [
        ["id", "<id_next>", "<for_update_tail>"],
        [EPSILON],
    ],

    "<for_update_tail>": [
        ["<inc_dec_op>"],
        ["<assign_op>", "<expression>"],
    ],

    "<inc_dec_op>": [
        ["++"],
        ["--"],
    ],

    "<switch_stmt>": [
        ["harvest", "(", "<expression>", ")", "{", "<case_list>", "<default_opt>", "}"],
    ],

    "<case_list>": [
        [
            "variety",
            "<case_literal>",
            ":",
            "<local_declaration>",
            "<case_statements>",
            "<case_list>",
        ],
        [EPSILON],
    ],

    "<case_literal>": [
        ["intlit"],
        ["chrlit"],
        ["sunshine"],
        ["frost"],
    ],

    "<case_statements>": [
        ["<case_statement>", "<case_statements>"],
        [EPSILON],
    ],
    
    "<case_statement>": [
        ["id", "<id_stmt>"],
        ["<inc_dec_op>", "id", "<id_next>", ";"],
        ["<io_stmt>"],
        ["<conditional_stmt>"],
        ["<loop_stmt>"],
        ["<switch_stmt>"],
        ["{", "<local_declaration>", "<statement>", "}"],
        ["prune", ";"],
        ["skip", ";"],
        ["reclaim", "<reclaim_value>"],
    ],

    "<default_opt>": [
        ["soil", ":", "<local_declaration>", "<case_statements>"],
        [EPSILON],
    ],

    "<control_stmt>": [
        ["prune", ";"],
        ["skip", ";"],
    ],


    "<expression>": [
        ["<assignment_expression>"],
    ],

    "<assignment_expression>": [
        ["<logic_or>", "<assignment_expression_next>"],
    ],

    "<assignment_expression_next>": [
        ["<assign_op>", "<assignment_expression>"],
        [EPSILON],
    ],

    "<logic_or>": [
        ["<logic_and>", "<logic_or_next>"],
    ],

    "<logic_or_next>": [
        ["||", "<logic_and>", "<logic_or_next>"],
        [EPSILON],
    ],

    "<logic_and>": [
        ["<relational>", "<logic_and_next>"],
    ],

    "<logic_and_next>": [
        ["&&", "<relational>", "<logic_and_next>"],
        [EPSILON],
    ],

    "<relational>": [
        ["<arithmetic>", "<relational_next>"],
    ],

    "<relational_next>": [
        ["<relational_op>", "<arithmetic>"],
        [EPSILON],
    ],

    "<relational_op>": [
        [">"],
        ["<"],
        [">="],
        ["<="],
        ["=="],
        ["!="],
    ],

    "<arithmetic>": [
        ["<term>", "<arithmetic_next>"],
    ],

    "<arithmetic_next>": [
        ["+", "<term>", "<arithmetic_next>"],
        ["-", "<term>", "<arithmetic_next>"],
        ["`", "<term>", "<arithmetic_next>"],
        [EPSILON],
    ],


    "<term>": [
        ["<power>", "<term_next>"],
    ],

    "<term_next>": [
        ["*", "<power>", "<term_next>"],
        ["/", "<power>", "<term_next>"],
        ["%", "<power>", "<term_next>"],
        [EPSILON],
    ],

    "<power>": [
        ["<factor>", "<power_next>"],
    ],

    "<power_next>": [
        ["**", "<power>"],
        [EPSILON],
    ],

    "<factor>": [
        ["(", "<paren_expr>"],
        ["<unary_op>", "<factor>"],
        ["id", "<factor_id_next>"],
        ["<literal>"],
    ],

    "<literal>": [
        ["intlit"],
        ["dblit"],
        ["chrlit"],
        ["stringlit"],
        ["sunshine"],
        ["frost"],
    ],

    "<paren_expr>": [
        ["<data_type>", ")", "<factor>"],
        ["<expression>", ")"],
    ],
    
    "<unary_op>": [
        ["~"],
        ["!"],
    ],

    "<factor_id_next>": [
        ["<array_access>", "<post_array_access>"],
        ["<struct_access>"],
        ["(", "<arguments>", ")"],
        [EPSILON],
    ],
}


first_sets = compute_first(cfg)
follow_sets = compute_follow(cfg, first_sets)
predict_sets = compute_predict(cfg, first_sets, follow_sets)


if __name__ == '__main__':
    print("=" * 80)
    print("FIRST SETS")
    print("=" * 80)
    print("Shows which terminals can appear first in each non-terminal")
    print()
    for nt in first_sets:
        print(f"First({nt}) = {{ {', '.join(sorted(first_sets[nt]))} }}")

    print("\n" + "=" * 80)
    print("FOLLOW SETS")
    print("=" * 80)
    print("Shows which terminals can appear after each non-terminal")
    print()
    for nt in follow_sets:
        print(f"Follow({nt}) = {{ {', '.join(sorted(follow_sets[nt]))} }}")

    print("\n" + "=" * 80)
    print("PREDICT SETS")
    print("=" * 80)
    print("Shows which terminal triggers each production rule")
    print()
    for (lhs, prod), pset in predict_sets.items():
        prod_str = " ".join(prod)
        print(f"Predict({lhs} -> {prod_str}) = {{ {', '.join(sorted(pset))} }}")

    print("\n" + "=" * 80)
