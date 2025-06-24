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

### 接続について

接続に必要となるソケットは、UDP版と同じく`socket.socket()`で作成します。
TCPのため、以下の設定でソケットを作成しています。

- `socket.AF_INET` - IPv4アドレスファミリーを使用
- `socket.SOCK_STREAM` - ストリームソケットを使用

```{note}
ストリームソケットを利用することで、TCPという扱いになっています。
```

今回のコードでは、`with`文を使ってソケットを自動的に閉じるようにしています。

```{literalinclude} source/calc_client.py
:language: python
:lines: 6
:linenos:
:lineno-start: 6
```

### コネクションの確立

TCPでは、UDPと異なり明確に『接続』が求められます。
そのため、接続に対して送りつける(`sendto()`)ではなく、`connect()`を使います。

```{literalinclude} source/calc_client.py
:language: python
:lines: 7
:linenos:
:lineno-start: 7
```

`socket.connect()`はいわゆる『ブロッキング』という動作です。
これは、相手との接続が確立されるまで、プログラムが待機することを意味します。
TCPでの接続は、いわゆる{ref}`3ウェイハンドシェイク <3wayhandshake>`と呼ばれる手順を経て行われます。

もちろん、そもそも相手のポートでの受信ができていない状態(すなわち「サーバーが起動していない」状態)もありえます。
この場合は『接続以前の問題』としてエラーによる終了となります。

よって、以降は接続が確立した状態を前提として進めることになります。

### 計算式の送信(サーバーへの送信)

接続後、ユーザーからの入力を受け付けてサーバーへ送信します。

```{literalinclude} source/calc_client.py
:language: python
:linenos:
:lines: 9-16
```

### ソケットはファイルに見える

TCPのソケットは、ストリームと呼ばれている構造となっています。
これは、情報がそれぞれの方向に流れている状況です。

- 一方の書き込みが他方の読み込みに繋がっている
- 反対側も同様である

```{mermaid}
graph TD
    subgraph クライアント
        direction LR
        C_WRITE(write)
        C_READ(read)
    end
    subgraph サーバー
        direction LR
        S_WRITE(write)
        S_READ(read)
    end

    C_WRITE --> S_READ
    S_WRITE --> C_READ
```

この図のように、TCPソケットは2つの独立したストリーム（流れ）が対になっていると考えることができます。

- クライアントからサーバーへのストリーム（クライアントの`write`がサーバーの`read`に繋がる）
- サーバーからクライアントへのストリーム（サーバーの`write`がクライアントの`read`に繋がる）

この仕様は、ソケットがファイルのように見えるということで「プログラマーにとってはソケットも普通のファイルのように操作できる。

ですが、Pythonではこの部分をさらに簡単に扱うための処置が含まれているため、普通に使おうとすると、`send()`や`recv()`を使ってもう少し簡単に書けてしまいます。

ここではファイルと同様であるということで、Pythonの流儀からは少し外れますがファイルに変換して読み書きをする方法で書いています。

```{literalinclude} source/calc_client.py
:language: python
:linenos:
:lines: 9-18
:lineno-start: 9
:emphasize-lines: 3-5,9
```

- 11行目でソケットから本来のファイルに相当するオブジェクトを取得しています(Python的には通常は不要ですが)。
- 12行目で、`write()`により送信を行います。
- ですが、`write()`はバッファリングされるため、すぐに送信されるわけではありません。よって13行目の`flush()`でバッファをフラッシュして、すぐに送信されるようにしています。
- 17行目で逆に1行分の読み込みを行っています(`readline()`)。

このように、ソケットをファイルのように扱うことで、Pythonの標準的なファイル操作と同じ感覚でTCP通信を行うことができます。

とりあえずクライアントのコードはここまでにして、続いてサーバー側の実装を考えてみましょう。
