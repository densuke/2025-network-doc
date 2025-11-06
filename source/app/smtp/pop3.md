# POP3プロトコル

初期のメールは、直接利用者のところへ届く仕組みになっていましたが、インターネットの普及とともに、メールサーバーを介してメールを管理する仕組みが一般的になりました。
そのため、届いたメールを利用者が自分用のメールサーバーから受信しないといけなくなりました。

そこで考案されたプロトコルのうち、残存するもののひとつとして、POP3(Post Office Protocol version 3)があります。このプロトコルもシンプルなため、基本的な動作を理解しやすいものとなっています。POP3は110/tcpで動作します。

## POP3もステートフルです

POP3はSMTPと同様にステートフル(stateful)、すなわち『状態を持つ』構造をしたプロトコルです。
もともとメールはユーザー別に管理されているため、認証を行ったうえでメールボックスにアクセスするという仕組みになっています。

POP3における大雑把な状態遷移は以下の通りです。
1. 接続確立 (Connection Established)
2. 認証 (Authentication)
3. メール操作 (Mail Transaction)
4. 切断 (Connection Termination)

また、場所に関係なくやり直しを行うためのリセット操作も用意されています。
メールの削除はその場で行わず、切断時にまとめて行うため、削除の取り消しも可能です。

POP3の主な命令は、以下のとおりです。`QUIT`は文字通りの終了のため割愛します。

### 認証関連

|コマンド|説明|
|---|---|
|USER ユーザー名|ユーザー名の指定|
|PASS パスワード|パスワードの指定|

### メール操作関連

|コマンド|説明|
|---|---|
|STAT|メールボックスの状態取得(メール数、サイズ)|
|LIST|メール一覧の取得(メール番号、サイズ)|
|RETR 番号|メールの取得|
|DELE 番号|メールの削除|
|NOOP|何もしない(接続維持)|
|RSET|削除指定のリセット(削除取り消し)|

### その他の操作

|コマンド|説明|
|---|---|
|TOP 番号 行数|指定したメールのヘッダと本文の一部を取得|
|UIDL|メールの一意識別子一覧の取得| 

セッション(接続)終了時に、削除指定されたメールがまとめて削除されます。

## POP3を試すには

SMTP同様に試すためには、POP3のサーバーが必要です。
POP3実装として、dovecotが有名です。使ってみましょう。

### dovecotのインストール

```bash
$ sudo apt install -y dovecot-pop3d
$ sudo systemctl start dovecot
$ sudo systemctl status dovecot # 確認したら qキーで抜けてください
```

### メールの受信

```bash
$ telnet localhost 110
Trying ::1...
Connected to localhost.
Escape character is '^]'.
+OK Dovecot (Debian) ready.
USER linux
+OK
PASS penguin
+OK Logged in.
LIST
+OK 2 messages:
1 490
2 476
.
RETR 1
+OK 490 octets
Return-Path: <linux@localhost>
...(中略)...

Hello, Hello, Hello, Hello.
.
DELE 1
+OK Marked to be deleted.
QUIT
+OK Logging out, messages deleted.
Connection closed by foreign host.
```

上記の例では、`linux`ユーザーのメールボックスに2通のメールが届いていることがわかります。
1通目のメールを取得し、内容を確認した後、削除指定を行い、セッションを終了しています。

MUAは、このような操作を裏で自動的に行い(もしくは手動で取得指示をして行い)、ユーザーにメールを見せていることになります。

