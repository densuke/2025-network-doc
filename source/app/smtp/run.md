# 実習: 実際に走らせてみよう

流石にインターネット向けのサーバーとして起動することはできませんが、ローカルネットワークで試すことができるメールサーバーを試してみましょう。
Linux上には様々なサービスが用意されています。もちろんメールサーバーだって実装が用意されています。

ここでは、Postfixというメールサーバーを使ってみましょう。
そして、ローカルネットワーク上で動くメールサーバーを構築し、SMTPを使ってメッセージを送ってみたいと思います。
この演習は、後ほどPOP3の実習でも使います。

## Postfixのインストール

Postfixは、多くのLinuxディストリビューションで利用されているメールサーバー実装の一つです。Debian系のディストリビューションでは、以下のコマンドでインストールできます。

```bash
$ sudo apt-get update
$ sudo apt-get install -y postfix
```

```{figure} images/postfix-1.png
:width: 65%

Postfixのインストール画面(1)
```

説明文が出ますが、{kbd}`TAB`キーで『了解』にカーソルを移動させてEnterで次へ進めてください。

```{figure} images/postfix-2.png
:width: 65%

Postfixのインストール画面(2)
```

選択肢はカーソルキーの上下で選べます。メールサーバーの構成についてはここでは(外部に出ても困るので)『ローカル』を選んでEnterで次へ進めてください。

```{figure} images/postfix-3.png
:width: 65%

Postfixのインストール画面(3)
```

システム名(サーバー名)を聞かれるので、ここではそのまま(linuxstudy)でEnterを押して次へ進めてください。
これでPostfixのインストールは完了です。

## サーバーの起動

Postfixサーバーの起動は、以下のコマンドで行えます。

```bash
$ sudo systemctl start postfix
$ systemctl status postfix
```

正しく動いているのであれば、active(exited)と表示されます。
確認したら {kbd}`q`キーで抜けておいてください。

```{figure} images/postfix-running.png
:width: 65%

Postfixサーバーの起動確認
```

## メールを送信してみる

サーバーの起動が確認できたら、実際にSMTPを使ってメールを送信してみましょう。

### telnetコマンドのインストール
まず、telnetコマンドがインストールされていない場合は、以下のコマンドでインストールしてください。

```bash
$ sudo apt-get install -y telnet
```

### 事前にファイルの準備

メールのやり取りに使うデータを先に作っておきましょう。
vscode(リモート接続)を利用して、以下の内容で `mail.txt` というファイルを作製してください。

```{literalinclude} app/mail-send/mail.txt
:language: text
:caption: mail.txt
```

Linuxでのコマンド操作だとリダイレクトで直接流し込むのですが、逆に送信速度が速すぎるからかエラーになってしまうようです。そこで簡易的なスクリプトを用意して、少しずつ送るようにしてみましょう。
`slowsend`という名前でファイルを作ってください。

```{literalinclude} app/mail-send/slowsend
:language: bash
:caption: slowsend
```

````{note}
スクリプトが気になる方へ概要説明

- `while read LINE; do ... done` は、標準入力から1行ずつ読み込んで処理を繰り返す構文です。
- `echo "$LINE"` は、読み込んだ行をそのまま出力します。
- `echo "$LINE" > /dev/stderr` は、読み込んだ行を標準エラー出力に出力します。別にしなくてもいいのですが、これをしないと『何を出力しているのかが見えにくい』というのがあるためです。
- `sleep 1` で1秒間待ちます

つまり「1行読んで出力したら、1秒待つ、ファイルの最終行までこれを繰り返す」という挙動になっています。

````

### 送信してみよう

では実際に送信させてみます。

```{code-block}
:language: bash
:caption: SMTPでのメール送信(バッチ処理)
:emphasize-lines: 1,6,8,10,12,14-19,21

$ bash slowsend < mail.txt | telnet localhost 25
Trying ::1...
Connected to localhost.
Escape character is '^]'.
220 linuxstudy.brill-gila.ts.net ESMTP Postfix (Debian/GNU)
HELO localhost      ← 挨拶
250 linuxstudy.brill-gila.ts.net
MAIL FROM:<linux@localhost> ← 送信者の指定
250 2.1.0 Ok
RCPT TO:<linux@localhost> ← 受信者の指定
250 2.1.5 Ok
DATA                 ← メール本文の開始
354 End data with <CR><LF>.<CR><LF>
From: linux@localhost
To: linux@localhost
Subject: Hello, Postfix

Hello, Hello.
.                   ← 送信終了
250 2.0.0 Ok: queued as 1A748200B6
QUIT                ← 切断
221 2.0.0 Bye
Connection closed by foreign host.
```

無事送信されると、メールがキューに登録されています(上気の例だと `1A748200B6` )。
そしてローカル受信と判定された結果、メールがローカルのメールボックスに格納されます。

```bash
$ ls /var/mail
linux
$ cat /var/mail/linux
```

中身が確認できればOKです。


