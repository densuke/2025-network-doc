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

## コードの解説

このサーバープログラムは、TCPサーバーの基本的な要素で構成されています。一つずつ見ていきましょう。

### ソケットの作成 (`socket.socket`)

```{literalinclude} source/calc_server.py
:language: python
:linenos:
:lines: 32-33
:lineno-start: 32
:emphasize-lines: 2
```

`socket.socket(socket.AF_INET, socket.SOCK_STREAM)` で、IPv4 (`AF_INET`) を使うTCP (`SOCK_STREAM`) ソケットを作成します。これが、ネットワーク通信の出入り口になります。

`setsockopt()`は、サーバーを終了してすぐに再起動した際に、同じポートをすぐ使えるようにするためのおまじないです。

### アドレスとポートの割り当て (`bind`)

```{literalinclude} source/calc_server.py
:language: python
:linenos:
:lines: 37-38
:lineno-start: 37
:emphasize-lines: 2
```

`sock.bind((HOST, PORT))` で、作成したソケットに特定のIPアドレス (`HOST`) とポート番号 (`PORT`) を結びつけます。これにより、クライアントはこのアドレスとポートを目がけて接続に来ることができます。

### 接続待機 (`listen`)

```{literalinclude} source/calc_server.py
:language: python
:linenos:
:lines: 39-40
:lineno-start: 39
:emphasize-lines: 2
```

`sock.listen()` で、ソケットを「待機モード」にします。これにより、クライアントからの接続要求を受け付けられるようになります。

### 接続の受け入れ (`accept`)

```{literalinclude} source/calc_server.py
:language: python
:lines: 43-45
:lineno-start: 43
:emphasize-lines: 3
```

`sock.accept()` は、クライアントからの接続要求を待ち、実際に接続が確立されると、新しいソケットオブジェクト (`conn`) とクライアントのアドレス (`addr`) を返します。

`accept()` は**ブロッキング呼び出し**であり、クライアントが接続してくるまでプログラムの実行はここで停止します。以降のクライアントとの通信は、この新しいソケット `conn` を通じて行われます。

### ファイルオブジェクトによる送受信 (`makefile`)

```{literalinclude} source/calc_server.py
:language: python
:lines: 9-12
:lineno-start: 9
:linenos:
:emphasize-lines: 4
```

`handle_client`関数内で`conn.makefile()`を使うと、ソケットをファイルのように扱うことができます。
以降のソケットに対する読み書きは、ファイルオブジェクトと同様の`read()`メソッドや`write()`メソッドなどで行えるようになります。

- `conn.makefile('rw', encoding='utf-8', newline='\n') as f:`
  - 接続済みのソケット`conn`から、ファイルオブジェクト`f`を作成します。
  - `'rw'`は読み書き両用モードを意味します。
  - `encoding='utf-8'`を指定することで、送受信時に自動でUTF-8へのエンコード・デコードが行われ、`encode()`や`decode()`を呼び出す手間が省けます。
  - `newline='\n'`は、異なるOS間でも改行コードを`\n`として扱うための設定です。

これにより、データの送受信は後述のように、使い慣れたファイル操作のメソッドで行えます。

### データの読み取り・書き込みについて

ここまでくると、ソケットはファイルの形でのも読み書きが普通に行えるようになります。

```{literalinclude} source/calc_server.py
:language: python
:lines: 14-15
:lineno-start: 14
:linenos:
:emphasize-lines: 2
```

```{literalinclude} source/calc_server.py
:language: python
:lines: 26-29
:lineno-start: 26
:linenos:
:emphasize-lines: 2
```

- **受信: `f.readline()`**
  - クライアントから送られてくるデータを1行ずつ読み込みます。
- **送信: `f.write(result + '\n')`**
  - 計算結果の文字列の末尾に改行を付けて書き込みます。クライアント側が`readline()`で待っているため、改行を送ることが重要です。


また、クライアントでの動作と同じく、バッファリングされているデータを書き出すために`flush()`も使っていることに注意してください。

### 接続の終了

- 12行目、46行目にて`with`構文を使っています。これによりブロックを抜けるときに自動的に`f.close()`と`conn.close()`が呼ばれ、クライアントとの接続が安全に閉じられます。
- サーバー全体を終了するとき（例えばCtrl+Cを押したとき）は、`finally`ブロックで`sock.close()`が呼ばれ、待機用のソケットも確実に閉じられます。

閉じ忘れていても、プロセスの終了後に適当なタイミングでクローズが行われますが、明示的にクローズすること以下のメリットが得られます。

- リソースの解放: ソケットを閉じることで、システムリソースが解放されます。
- クライアントに終了を通知: クライアント側は、サーバーが接続を閉じたことを認識できます(いきなり着られることはうれしくないとは思いますが)。

以上で、基本的なサーバーの実装になっています。
