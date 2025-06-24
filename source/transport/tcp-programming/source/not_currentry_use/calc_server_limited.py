import socket
import ast
from calc_cost_util import calc_cost

HOST = '127.0.0.1'
PORT = 10000
COST_LIMIT = 1200  # セッション内のコスト上限

def safe_eval(expr):
    """安全な式評価（数値演算のみ）"""
    node = ast.parse(expr, mode='eval')
    for n in ast.walk(node):
        if not isinstance(n, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd, ast.Mod, ast.FloorDiv, ast.BitXor, ast.BitOr, ast.BitAnd, ast.LShift, ast.RShift)):
            raise ValueError("不正な式です")
    return eval(compile(node, '<string>', 'eval'), {'__builtins__': {}})

with socket.create_server((HOST, PORT)) as server:
    print(f"[server] Listening on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        with conn:
            print(f"[server] Connected by {addr}")
            session_cost = 0
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                expr = data.decode().strip()
                if expr == "quit":
                    print("[server] Connection closed by client")
                    break
                try:
                    node = ast.parse(expr, mode='eval')
                    cost = calc_cost(node)
                    if session_cost + cost > COST_LIMIT:
                        result = f"Error: セッションコスト上限({COST_LIMIT})を超えました | 累積コスト: {session_cost}"
                    else:
                        session_cost += cost
                        value = str(safe_eval(expr))
                        result = f"結果: {value} | この式のコスト: {cost} | 累積コスト: {session_cost}"
                except Exception as e:
                    result = f"Error: {e} | 累積コスト: {session_cost}"
                conn.sendall(result.encode())
