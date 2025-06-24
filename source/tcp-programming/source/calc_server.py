import socket

HOST = '127.0.0.1'  # ローカルホスト
PORT = 10000        # 任意の空いているポート番号

with socket.create_server((HOST, PORT)) as server:
    print(f"[server] Listening on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        with conn:
            print(f"[server] Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                expr = data.decode().strip()
                if expr == "quit":
                    print("[server] Connection closed by client")
                    break
                try:
                    # 安全のため、evalの利用は最小限に
                    result = str(eval(expr, {"__builtins__": {}}))
                except Exception as e:
                    result = f"Error: {e}"
                conn.sendall(result.encode())
