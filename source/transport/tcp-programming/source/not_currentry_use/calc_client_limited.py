import socket
import ast
from calc_cost_util import calc_cost

HOST = '127.0.0.1'  # サーバーのアドレス
PORT = 10000        # サーバーのポート番号

with socket.create_connection((HOST, PORT)) as sock:
    print(f"[client] Connected to {HOST}:{PORT}")
    session_cost = 0
    while True:
        expr = input("計算式を入力してください（例: 2+3, quitで終了）: ")
        try:
            node = ast.parse(expr, mode='eval')
            cost = calc_cost(node)
        except Exception:
            cost = 0
        print(f"[client] この式の計算コスト: {cost} (累積: {session_cost + cost})")
        sock.sendall(expr.encode())
        if expr == "quit":
            print("[client] 終了します")
            break
        data = sock.recv(1024)
        print(f"[client] サーバー応答: {data.decode()}")
        session_cost += cost
