# SMTPとそのフロー

SMTP(Simple Mail Transfer Protocol)は、インターネット上で電子メールを送信するための主要なプロトコルです。このドキュメントでは、SMTPの基本的なフローとその動作について説明します。

## SMTPは『状態』を持つ

SMTPはステートフル(stateful)、すなわち『状態を持つ』構造をしたプロトコルです。
これは、SMTPによる接続〜切断までの『セッション』において、クライアントとサーバーの間で「今こういう状態にある」ということを意識する必要があることを示しています。

大雑把には、以下の状態遷移があります。
1. 接続確立 (Connection Established)
2. 挨拶 (Greeting)
3. メール送信準備 (Mail Transaction Preparation)
4. メール送信 (Mail Transaction)
5. 切断 (Connection Termination)
また、場所に関係なくやり直しを行うためのリセット操作も用意されています。

## SMTPと亜種

SMTPは歴史的にかなり長い(比較的初期から存在する)ため、歴史的経緯によりアップデートが多少されていますが、根本としてのSMTPはほぼ変化がありません。
今後解説することになると思いますが、以下について補足をしておきます。

### ESMTP
ESMTP(Extended SMTP)は、SMTPの拡張版であり、追加のコマンドや機能を提供します。ESMTPは、SMTPの基本的なフローを維持しつつ、より高度なメール送信機能をサポートします。
本来のSMTPに若干高度な機能をサポートしたものです。
現在のSMTPが全てESMTPとして機能しているかというと、実はそうでもなかったりします。

### SMTPS
SMTPSは、SMTP over SSL/TLSの略で、SMTP通信を暗号化するための方式です。主に2つのやり方があります。

- STARTTLS による明示的アップグレード: 平文で始まるSMTP(主に 25/TCP や 587/TCP)のセッションを、STARTTLSコマンドでTLSに切り替える方式
- いわゆる SMTPS(implicit TLS): 最初からTLSで開始する方式で、465/TCP(“submissions”)が用いられます(RFC 8314)

どちらもSMTPの基本フローは同じですが、暗号化の開始タイミングが異なります。

### サブミッションとSMTP AUTH
サブミッション(Submission)は、メールクライアント(MUA)がメールサーバー(MSA)にメールを送信するための経路/サービスを指します(通常 587/TCP)。
SMTP AUTH は、その際にクライアントを認証するための仕組み（認証メカニズム）です。

もともとSMTPは認証を前提としていませんでしたが、不正利用を防ぐ目的から、MUAからSMTPにつなぐ際に『正当なサービス利用者』を確認する目的で用意されたのがSMTP Authとなります。
こちらも(E)SMTPの基本的なフローを維持しつつ、認証機能が追加されています。

```{note}
日本語では MUA→MSA の経路を『サブミッション』と呼ぶことが多く、ポートは 587/TCP が一般的です（STARTTLS で暗号化）。
```

## SMTPの基本フロー

SMTPは先にも述べたように、状態を持ちます。
SMTP(25/tcp)で接続した直後はまだ開始状態にあるため、そこからのメールを送信するまでの流れを順を追って見ていきましょう。

```{mermaid}
sequenceDiagram
    autonumber
    participant Client as クライアント(MUA/MTA)
    participant Server as サーバー(MTA)
    
    Note over Client,Server: 接続確立
    Client->>Server: TCP接続確立(25/tcp)
    Server-->>Client: 220 Service Ready
    
    Note over Client,Server: 挨拶
    Client->>Server: HELO/EHLO client.example.com
    Server-->>Client: 250 OK
    
    Note over Client,Server: メール送信準備
    Client->>Server: MAIL FROM:<sender@example.com>
    Server-->>Client: 250 OK
    Client->>Server: RCPT TO:<recipient@example.com>
    Server-->>Client: 250 OK
    
    Note over Client,Server: メール送信
    Client->>Server: DATA
    Server-->>Client: 354 Start mail input
    Client->>Server: メール本文...CRLF.CRLF
    Server-->>Client: 250 OK queued
    
    Note over Client,Server: 切断
    Client->>Server: QUIT
    Server-->>Client: 221 Bye
```

### 挨拶について

SMTPでは、接続したときにクライアントからサーバーに対して挨拶を行います。
この挨拶はHELOもしくはEHLOコマンドが使われます。

```text
HELO domain.name
(もしくは)
EHLO domain.name
```

EHLOはESMTPを使うための挨拶となっており、このタイミングでサーバー側は命令の解釈を本来のSMTPか、ESMTPかを判断しています。

EHLO/HELO の引数には、原則として自ホストのFQDNを渡すことが推奨されます（RFC 5321）。MTA間の通信では特に重要で、`localhost` のような値はスパム判定の材料になることがあります。MUAがサブミッションに接続する場合はFQDNを持たない環境もありますが、可能なら正しいホスト名を設定しましょう。

### メール送信準備について

メール送信の準備では、誰(送信者)が誰(送信先)に送るのかを指定します。
そのために2つの命令を使って送る仕組みになっています。

- `MAIL FROM:`: 送信者アドレスを指定します。
- `RCPT TO:`: 受信者アドレスを指定します。

```{note}
そろそろ気づいたかと思いますが、原則としてSMTPの最初の命令は大文字の4文字で固定化されています。
これはSMTPの歴史的経緯として見ておくと良いでしょう。
当時(1970、1980年代)では技術的な制約が強く、命令調を固定化して読み取りを高速化するなどの対策が取られている時期でもありました。
```

面白いのは、`MAIL FROM:` は一度のトランザクションにつき1回だけですが、`RCPT TO:` は複数回指定できることです。
つまり、一つの送信で複数の受信者に送ることが可能です。

### 大切なおまけ: 送信先メールアドレスとヘッダ指定

私達がメールを送信する時、メールアドレスを複数つけられることは学んでいると思います。
この際、`To:`や`Cc:`、`Bcc:`といったヘッダを使って送信先を指定します。
これらはメールヘッダの話ですが、SMTPにおける`MAIL FROM:`や`RCPT TO:`は『エンベロープ』と呼ばれる本文の外で使われる制御情報になります。ですが、使用する値は同一のものとなるわけです。

つまり、SMTPの`RCPT TO:`で指定したアドレスは、メールヘッダの`To:`や`Cc:`に対応することになります。

たとえば、以下のようなメールを送信する場合を考えます。

```
From: sender@example.com
To: recipient@example.com
Cc: cc@example.com
Bcc: bcc@example.com
```

これに対応するSMTPコマンドは、以下のようになります（アドレスは角括弧で囲むのが正式な書式です）。

```
MAIL FROM:<sender@example.com>
RCPT TO:<recipient@example.com>
RCPT TO:<cc@example.com>
RCPT TO:<bcc@example.com>
```

つまり、To/Cc/Bccすべての受信者アドレスは、SMTPの`RCPT TO:`コマンドで指定されることになります。
そして、To/Cc/Bccの扱いはMUAやMTAの実装で依存することとなります。

- To/Cc: これらはメールヘッダに含まれます
- Bcc: このアドレスは送信の最中に剥がされ、メールヘッダからは消えてしまいます。

ということでBccは、『送信者(記入したから知っているはず)』『Bcc受信者(自分の名前がないのになぜか届いている)』および処理のために関与したMTAのみが知ることとなります。
この性質からBccは『密かに送りたい』場合に使用されます。自身に送ってバックアップにしたり、上司にこっそり送って『送信したことの証左』にしておくなど、用途はいくつか考えられると思います。

### メール送信について

メールの送り先情報が確定すれば、あとは実際にメール本文を送るだけです。
メール本文を送るためには、まず`DATA`コマンドを送信します。
すると、サーバー側は「メール本文を送って良いよ」という応答を返します。
その後、クライアント側はメール本文を送信し、最後にピリオド1つを改行で送信することで、メール本文の終了を示します。

```{note}
より正確には「改行.改行」が終了です。
更に正確には <CRLF>.<CRLF> となります。

- SMTPでは改行はCRLFと決められています
- 意図的にピリオドが行頭に来る場合は、送信時にピリオドを2つにして送信します(ピリオドエスケープ)
```

```text
DATA
From: sender@example.com
To: recipient@example.com
Subject: Test Email

This is a test email.
.
```
サーバー側はメール本文を受信し終えると、`250 OK queued`のような応答を返します。
メールは仕組み上、即座に送信するのではなく、送信待ちキューに登録され、少々の間が挟まった後に送信される仕組みとなっています。

### 送信後の切断について

SMTPのセッションは再利用される可能性もありますが、基本的には一通りのメール送信が終われば切断されます。
切断するためには、`QUIT`コマンドを送信します。
サーバー側は`221 Bye`のような応答を返し、TCP接続が切断されます。

同じメールサーバーで別のメールを送るのであれば、接続を再利用したほうがいい場合もあります。
そのためにはリセット(`RSET`コマンド)を送信して、状態を初期化することができます。
