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

    # 自分でBase64エンコードしてみる
    my_b64_encoded = base64_self(byte_string)
    print(my_b64_encoded)


def base64_self(s: bytes) -> str:
    """自分でBase64エンコードしてみる

    Args:
        s (str): エンコードしたい文字列
    Returns:
        str: Base64エンコードされた文字列
    """

    # バイト列をビット列に変換
    bits = "".join(format(byte, "08b") for byte in s)

    # 6ビットずつに分割
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    #               ^^^^^^^^^^^^^^^^^^^^^^^^^^--------------------------^^^^^^^^^^--
    #               英大文字(26文字)            英小文字(26文字)            数字(10)   +/ ということで64種類の文字
    encoded = ""
    for i in range(0, len(bits), 6):
        chunk = bits[i : i + 6]
        if len(chunk) < 6:
            chunk += "0" * (6 - len(chunk))  # パディング
        index = int(chunk, 2)
        encoded += base64_chars[index]

    # パディング文字を追加
    padding = (3 - len(s) % 3) % 3
    encoded += "=" * padding

    return encoded


if __name__ == "__main__":
    main()
