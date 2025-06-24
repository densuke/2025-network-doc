# 計算機クライアントを作ってみる

次は、クライアント側の作成手順です。サーバーに計算式を送り、結果を受け取るTCPクライアントを作成します。

## クライアントの仕様

- ユーザーから計算式（例: 2+3）を入力
- サーバーに送信し、結果を受信して表示
- "quit"と入力すると終了

## クライアントのPythonコード

ファイル名は`calc_client.py`とします。

```{literalinclude} source/calc_client.py
:language: python
:linenos:
```

---

## クライアントの起動方法

uvを使って以下のように実行します。

```bash
uv run python3 source/calc_client.py
```
