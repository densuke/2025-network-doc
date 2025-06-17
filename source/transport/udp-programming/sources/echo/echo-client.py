#!/usr/bin/env python3
import socket

def main():
    # UDPソケットを作る
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 今回は、自分自身(localhost)のポート10000を接続先とします(10000/udp)
    server_address = ('localhost', 10000)
    
    try:
        message = b'Hello, World!' # 送信したいデータ列(バイト列に変換しておく)
        print(f'送信内容: {message}')
        sent = sock.sendto(message, server_address)

        # Receive response
        print('応答待ち')
        data, server = sock.recvfrom(4096)
        print(f'受信しました: {data}')

    finally:
        print('終了します')
        sock.close()

if __name__ == '__main__':
    main()
