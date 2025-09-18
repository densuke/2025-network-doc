# 引数で渡された文字列を、Base64で符号化してください
# augumentparserを使って引数の文字列を受け取ります。
import argparse
import base64


def main():
    parser = argparse.ArgumentParser(description="Base64 encode a string")
    parser.add_argument("string", type=str, help="String to be encoded")
    args = parser.parse_args()

    # 文字列をバイトに変換
    byte_string = args.string.encode("utf-8")

    # Base64で符号化
    b64_encoded = base64.b64encode(byte_string)

    # バイトを文字列に変換して出力
    print(b64_encoded.decode("utf-8"))


if __name__ == "__main__":
    main()
