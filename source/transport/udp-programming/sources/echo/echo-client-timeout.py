#!/usr/bin/env python3
import socket

def main():
    # UDPソケットを作る
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # 今回は、自分自身(localhost)のポート10000を接続先とします(10000/udp)
        server_address = ('localhost', 10000)
        
        message = b'Hello, World!' # 送信したいデータ列(バイト列に変換しておく)
        print(f'送信内容: {message}')
        sock.sendto(message, server_address)

        # Receive response
        print('応答待ち')
        # タイムアウトを1秒に設定
        sock.settimeout(1.0)
        try:
            data, server = sock.recvfrom(4096)
            print(f'受信しました: {data}')
        except socket.timeout:
            print('応答がありませんでした。タイムアウトしました。')

    print('終了します')

if __name__ == '__main__':
    main()
