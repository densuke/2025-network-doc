#!/usr/bin/env python3
import socket

def main():
    # UDPソケットを作る
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 今回は、localhostのポート10000で待ち受けます(10000/udp)
    server_address = ('localhost', 10000)
    sock.bind(server_address)

    print(f'サーバーは {server_address} で待ち受けています')

    while True:
        # データを受信する
        data, address = sock.recvfrom(4096)
        print(f'受信しました: {data} from {address}')

        # 受け取ったデータをそのまま送り返す(エコー)
        sent = sock.sendto(data, address)
        print(f'送信しました: {data}')

if __name__ == '__main__':
    main()
