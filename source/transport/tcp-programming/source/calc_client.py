import socket

HOST = '127.0.0.1'  # サーバーのアドレス
PORT = 10000        # サーバーのポート番号

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    print(f"[client] Connected to {HOST}:{PORT}")
    while True:
        expr = input("計算式を入力してください（例: 2+3, quitで終了）: ")
        sock_file = sock.makefile('rwb')
        sock_file.write((expr + '\n').encode())
        sock_file.flush()
        if expr == "quit":
            print("[client] 終了します")
            break
        data = sock_file.readline()
        print(f"[client] 結果: {data.decode()}")
