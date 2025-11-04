import ast

# ノードごとのコストを定義(例: 乗算やべき乗は高コスト)
NODE_COST = {
    ast.Add: 1,
    ast.Sub: 1,
    ast.Mult: 10,
    ast.Div: 10,
    ast.Pow: 1000,
    ast.USub: 1,
    ast.UAdd: 1,
    ast.Mod: 10,
    ast.FloorDiv: 10,
    ast.BitXor: 5,
    ast.BitOr: 5,
    ast.BitAnd: 5,
    ast.LShift: 20,
    ast.RShift: 20,
    ast.Constant: 1,  # ast.Numは3.14で廃止
}

def calc_cost(node):
    """ASTノードから計算コストを再帰的に算出"""
    cost = NODE_COST.get(type(node), 0)
    for child in ast.iter_child_nodes(node):
        cost += calc_cost(child)
    return cost
