# 計算機サーバーを作ってみる

次は、サーバー側の作成手順です。クライアントから計算式（例: 2+3）を受け取り、計算結果を返すTCPサーバーを作成します。

## サーバーの仕様

- クライアントから1行の計算式（例: 2+3）を受信
- 受信した式を評価し、結果を返す
- "quit"が送られてきたら接続を終了

## サーバーのPythonコード

ファイル名は`calc_server.py`とします。

```{literalinclude} source/calc_server.py
:language: python
:linenos:
```

### ポイント

- `socket`モジュールを使い、TCPソケットを作成します
- `bind`でアドレスとポートを指定し、`listen`で待ち受けます
- クライアントからの接続ごとに1つの計算を処理します

---

## サーバーの起動方法

uvを使って以下のように実行します。

```bash
uv run python3 source/calc_server.py
```
