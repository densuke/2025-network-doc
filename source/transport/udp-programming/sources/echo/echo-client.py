#!/usr/bin/env python3
import socket

def main():
    # UDPソケットを作る
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # 今回は、自分自身(localhost)のポート10000を接続先とします(10000/udp)
        server_address = ('localhost', 10000)
        
        message = b'Hello, World!' # 送信したいデータ列(バイト列に変換しておく)
        print(f'送信内容: {message}')
        sent = sock.sendto(message, server_address)

        # Receive response
        print('応答待ち')
        data, server = sock.recvfrom(4096)
        print(f'受信しました: {data}')

    print('終了します')

if __name__ == '__main__':
    main()
