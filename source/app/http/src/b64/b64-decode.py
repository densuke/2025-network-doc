#!/usr/bin/env python
"""Base64デコードを行う
引数で渡されたBase64で符号化された文字列をデコードして元の文字列に戻す
"""

import argparse
import base64
import binascii
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Base64 decode a string")
    parser.add_argument("string", type=str, help="Base64 encoded string")
    args = parser.parse_args()
    b64_string = args.string
    # Base64でデコード
    try:
        decoded_bytes = base64.b64decode(b64_string, validate=True)
        # バイトを文字列に変換して出力
        print(decoded_bytes.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError) as e:
        print(f"Error decoding Base64 string: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
