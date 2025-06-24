import asyncio
import ast

HOST = '127.0.0.1'  # ローカルホスト
PORT = 10000        # 任意の空いているポート番号

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """各クライアント接続を処理するコルーチン"""
    addr = writer.get_extra_info('peername')
    print(f"[async server] Connected by {addr}")
    try:
        while True:
            # クライアントから1行読み込む
            data = await reader.readline()
            if not data:
                print(f"[async server] Connection closed (EOF) from {addr}")
                break

            expr = data.decode().strip()
            if expr == 'quit':
                print(f"[async server] Connection closed by client {addr}")
                break

            try:
                # 安全な評価（同期版と同じロジック）
                tree = ast.parse(expr, mode='eval')
                safe_nodes = (
                    ast.Expression, ast.Constant, ast.BinOp, ast.UnaryOp,
                    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.UAdd, ast.USub
                )
                for node in ast.walk(tree):
                    if not isinstance(node, safe_nodes):
                        raise ValueError(f"Unsupported operation: {type(node).__name__}")
                code = compile(tree, filename='<string>', mode='eval')
                result = str(eval(code, {"__builtins__": {}}))
            except Exception as e:
                result = f"Error: {e}"

            # 結果をクライアントに書き込む
            writer.write((result + '\n').encode())
            # バッファをフラッシュして送信を完了させる
            await writer.drain()
    except ConnectionResetError:
        print(f"[async server] Connection reset by {addr}")
    finally:
        # 接続を閉じる
        writer.close()
        await writer.wait_closed()
        print(f"[async server] Disconnected {addr}")

async def main():
    """サーバーを起動して待機するメインコルーチン"""
    server = await asyncio.start_server(handle_client, HOST, PORT)

    addr = server.sockets[0].getsockname()
    print(f"[async server] Serving on {addr}")

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[async server] Shutting down")
