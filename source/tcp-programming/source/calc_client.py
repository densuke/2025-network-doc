import socket

HOST = '127.0.0.1'  # サーバーのアドレス
PORT = 10000        # サーバーのポート番号

with socket.create_connection((HOST, PORT)) as sock:
    print(f"[client] Connected to {HOST}:{PORT}")
    while True:
        expr = input("計算式を入力してください（例: 2+3, quitで終了）: ")
        sock.sendall(expr.encode())
        if expr == "quit":
            print("[client] 終了します")
            break
        data = sock.recv(1024)
        print(f"[client] 結果: {data.decode()}")
