#!/usr/bin/env python
"""メールアドレスからMXレコードとIPアドレスを表示するスクリプト"""

import argparse
import sys
from mail_mx_resolver import get_mail_server_info


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="メールアドレスからMXレコードとIPアドレスを取得します",
        epilog="例: python resolve_mail.py user@example.com"
    )
    parser.add_argument(
        "email",
        help="解析するメールアドレス"
    )

    args = parser.parse_args()
    email = args.email

    try:
        result = get_mail_server_info(email)

        print(f"メールアドレス: {result['email']}")
        print(f"ドメイン: {result['domain']}")
        print("\nMXレコード(優先度順):")
        print("-" * 80)

        for i, mx in enumerate(result['mx_records'], 1):
            print(f"\n{i}. 優先度: {mx['priority']}")
            print(f"   ホスト名: {mx['hostname']}")
            print("   IPアドレス:")
            if mx['ip_addresses']:
                for ip in mx['ip_addresses']:
                    print(f"     - {ip}")
            else:
                print("     (IPアドレスが取得できませんでした)")

    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
