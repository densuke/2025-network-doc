#!/usr/bin/env python
"""メールアドレスからMXレコードとIPアドレスを取得するモジュール"""

import dns.resolver
from typing import List, Dict, Any


def extract_domain_from_email(email: str) -> str:
    """メールアドレスからドメイン部分を抽出する

    Args:
        email: メールアドレス文字列

    Returns:
        ドメイン部分の文字列

    Raises:
        ValueError: メールアドレスの形式が不正な場合
    """
    if not email:
        raise ValueError("メールアドレスが空です")

    parts = email.split("@")
    if len(parts) != 2:
        raise ValueError("メールアドレスの形式が不正です(@が無いか複数あります)")

    domain = parts[1]
    if not domain:
        raise ValueError("ドメイン部分が空です")

    return domain


def resolve_mx_records(domain: str) -> List[Dict[str, Any]]:
    """ドメインのMXレコードを優先度順に取得する

    Args:
        domain: ドメイン名

    Returns:
        MXレコードのリスト(優先度順)
        各要素は {"priority": int, "hostname": str} の辞書

    Raises:
        Exception: MXレコードが取得できない場合
    """
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
    except Exception as e:
        raise Exception(f"MXレコードの取得に失敗しました: {e}")

    result = []
    for mx in mx_records:
        result.append({
            "priority": mx.preference,
            "hostname": str(mx.exchange).rstrip(".")
        })

    # 優先度順にソート
    result.sort(key=lambda x: x["priority"])
    return result


def resolve_ip_addresses(hostname: str) -> List[str]:
    """ホスト名からIPv4アドレスを取得する

    Args:
        hostname: ホスト名

    Returns:
        IPv4アドレスのリスト
    """
    try:
        answers = dns.resolver.resolve(hostname, "A")
        return [str(answer) for answer in answers]
    except Exception:
        return []


def get_mail_server_info(email: str) -> Dict[str, Any]:
    """メールアドレスから送信先サーバー情報を取得する

    Args:
        email: メールアドレス

    Returns:
        以下の形式の辞書:
        {
            "email": str,
            "domain": str,
            "mx_records": [
                {
                    "priority": int,
                    "hostname": str,
                    "ip_addresses": List[str]
                }
            ]
        }
    """
    domain = extract_domain_from_email(email)
    mx_records = resolve_mx_records(domain)

    # 各MXレコードのIPアドレスを取得
    for mx in mx_records:
        mx["ip_addresses"] = resolve_ip_addresses(mx["hostname"])

    return {
        "email": email,
        "domain": domain,
        "mx_records": mx_records
    }
