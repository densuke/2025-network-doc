import socket
import ast # 現在は不要でした(削除可能)

HOST = '127.0.0.1'  # ローカルホスト
PORT = 10000        # 任意の空いているポート番号

def handle_client(conn, addr):
    print(f"[server] Connected by {addr}")
    # ソケットをファイルのように扱うため、makefile()でファイルオブジェクトを作成
    # 'rw'は読み書き両用、encoding='utf-8'で送受信する文字列のエンコーディングを指定
    # newline='\n'は、行末をLFに統一
    with conn.makefile('rw', encoding='utf-8', newline='\n') as f:
        while True:
            # 5. f.readline()で一行受信 (read)
            expr = f.readline().strip()
            if not expr:
                print("[server] Connection closed (EOF)")
                break
            if expr == "quit":
                print("[server] Connection closed by client")
                break
            try:
                result = str(eval(expr, {"__builtins__": {}}))
            except Exception as e:
                result = f"Error: {e}"
            # 6. f.write()で一行送信 (write)
            f.write(result + '\n')
            # バッファをフラッシュして、データを即座に送信
            f.flush()

def run_server():
    # 1. ソケットの作成
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # サーバーを閉じた後、すぐに同じポートで再起動できるように設定
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        # 2. bind()で、作成したソケットにIPアドレスとポート番号を割り当てる
        sock.bind((HOST, PORT))
        # 3. listen()で、クライアントからの接続を待ち受ける状態に移行
        sock.listen()
        print(f"[server] Listening on {HOST}:{PORT}")
        while True:
            # 4. accept()で、クライアントからの接続要求を受け入れ、
            #    新しいソケット(conn)とクライアントのアドレス(addr)を取得
            conn, addr = sock.accept()
            with conn:
                handle_client(conn, addr)
    finally:
        print("[server] Shutting down")
        sock.close()

if __name__ == '__main__':
    run_server()
