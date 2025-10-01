# HTTPでの認証

HTTPは一期一会が基本ということは前述しましたが、利用者を識別する必要とする場合もあります。
そのため、HTTPには認証の仕組みが用意されています。

認証の方法としては、以下の2つが用意されています。

- Basic認証(ベーシック認証)
- Digest認証(ダイジェスト認証)

これらの認証方法は、HTTPの仕様として定義されているものです。

## Basic認証

Basic認証は、最もシンプルな認証方法です。シンプルが故にお手軽ですが、セキュリティ的には弱いため、注意が必要です。
Basic認証では、利用者がユーザ名とパスワードを入力し、それをBase64という方法でエンコードして送信します。

```{mermaid}
sequenceDiagram
    participant Client
    participant Server

    Client->>Server: "GET /protected-resource"
    Server->>Client: "401 Unauthorized"
    Client->>Server: "Authorization: Basic ..."
    Server->>Client: "200 OK"
```     

クライアントが保護されたリソースにアクセスしようとすると、サーバは`401 Unauthorized`レスポンスを返します。
そこで再度リクエストを出す際に、`Authorization`ヘッダにユーザ名とパスワードを送ります。

この時に送るヘッダとパスワードの構造は、以下の手順で作成します。

1. `username:password`の形式で文字列を作成します。
2. その文字列をBase64でエンコードします。

もしユーザ名が`alice`でパスワードが`secret`の場合、`alice:secret`をBase64でエンコードします。

```bash
# nkfは非標準ですが、Base64エンコードが可能なコマンドラインツールです。
$ echo -n "alice:secret" | nkf -MB
YWxpY2U6c2VjcmV0
```

よって、リクエストを送り直す際は、以下となります。

```
GET /protected-resource HTTP/1.1
Host: example.com
Authorization: Basic YWxpY2U6c2VjcmV0
   <--空行
```

このように、Basic認証は非常にシンプルな作りとなっています。
ただし、Base64は暗号化では無くあくまで『エンコード』です。よって、このやりとりが経路で覗かれた場合、簡単にユーザーとパスワードが漏れてしまう仕様となっています。
そのため、Basic認証を利用する場合は、必ずHTTPSなどの暗号化された通信路を利用するようにしてください。

## Digest認証

Digest認証は、Basic認証の弱点を補うために設計された認証方法です。
Digest認証では、パスワードそのものを送信するのではなく、パスワードとサーバから送られたランダムな値(ノンス)を組み合わせてハッシュ化した値を送信します。

```{mermaid}
sequenceDiagram
    participant Client
    participant Server

    Client->>Server: "GET /protected-resource"
    Server->>Client: "401 Unauthorized"
    Client->>Server: "Authorization: Digest ..."
    Server->>Client: "200 OK"
```

クライアントが保護されたリソースにアクセスしようとすると、サーバは`401 Unauthorized`レスポンスを返します。
サーバー側はDigest認証を利用する場合、レスポンスヘッダに`WWW-Authenticate`ヘッダを含めます。このヘッダには、認証方式やノンスなどの情報が含まれています。このレスポンス上の`WWW-Authenticate`では、以下のような値を受け取ります。


```{code-block}
:caption: WWW-Authenticateヘッダの例(Digest認証)

WWW-Authenticate: Digest 
    realm="example", 
    qop="auth", 
    algorithm=MD5,
    nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
    opaque="5ccc069c403ebaf9f0171e9517f40e41"
```

このヘッダの各フィールドの意味は以下の通りです。

- `realm`: 認証領域を示す文字列。クライアントはこの領域に対して認証情報を提供する必要があります。
- `qop`: Quality of Protectionの略で、認証の品質を示します。通常は`auth`が指定されます。
- `nonce`: サーバが生成したランダムな値で、リプレイ攻撃を防ぐために使用されます。
- `opaque`: サーバが生成したランダムな値で、クライアントがそのまま返す必要があります。
- `algorithm`: 使用されるハッシュアルゴリズムを示します。通常は`MD5`が指定されます。

クライアントはこの情報を元に、以下の手順で認証情報を生成します。

1. ユーザ名、パスワード、realmを使ってハッシュ値`HA1`を計算します。
   ```
   HA1 = MD5(username:realm:password)
   ```
2. リクエストメソッドとリクエストURIを使ってハッシュ値`HA2`を計算します。
   ```
   HA2 = MD5(method:digestURI)
   ```
3. `HA1`、`nonce`、`HA2`を使って最終的なレスポンスハッシュを計算します。
   ```
   response = MD5(HA1:nonce:HA2)
   ```
4. 最後に、`Authorization`ヘッダを作成し、必要な情報を含めてサーバに送信します。

少し複雑ですね。試しに計算してみましょう。ユーザ名が`alice`、パスワードが`secret`、realmが`example`、リクエストメソッドが`GET`、リクエストURIが`/protected-resource`、nonceが`dcd98b7102dd2f0e8b11d0f600bfb0c093`の場合を考えます。

1. `HA1`の計算
   ```
   HA1 = MD5("alice:example:secret")
       = a110383056f556b818bd7026fed7451b
    ``` 
2. `HA2`の計算
   ```
   HA2 = MD5("GET:/protected-resource")
       = 72fc00ec534be079d25c0b845fa04e1e
   ```
3. `response`の計算
   ```
   response = MD5("a110383056f556b818bd7026fed7451b:dcd98b7102dd2f0e8b11d0f600bfb0c093:72fc00ec534be079d25c0b845fa04e1e")
        = 9180cfd6e679f09f7c8debe8a15c297f
   ```

```{code-block}
:caption: Authorizationヘッダの例(Digest認証)

Authorization: Digest
    username="alice",
    realm="example",
    nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
    uri="/protected-resource",
    response="9180cfd6e679f09f7c8debe8a15c297f",
    qop=auth,
    nc=00000001,
    cnonce="0a4f113b"
```

といった具合に計算が行われます。

```{note}
ここではダイジェスト生成アルゴリズムとしてMD5を使用していますが、現在ではSHA-256など、より安全なハッシュ関数を使用することが推奨されています。
ダイジェストアルゴリズムの指定はサーバーレスポンスに含まれています(`algorithm`フィールド)。
```

この時、`cnonce`はクライアントが生成するランダムな値で、`nc`はリクエストのカウントを示します。これらの値は『再利用がされない』用にするためのもので、要求が発生するたびに変化しています。
これらの値を使うことで、仮に途中で傍受されたとしても、同じ認証コード(計算結果)を使うことができません[^replay]。

[^replay]: 傍受した内容を使って認証を代行して行うような行為は **リプレイ攻撃** と呼びます。Basic認証はリプレイ攻撃に弱いですね。

Digest認証はBasic認証に比べてセキュリティが向上していますが、計算が複雑であるため、実装や利用がやや難しいです。
また、Digest認証も完全に安全ではなく、適切なセキュリティ対策が必要です。可能であれば、HTTPSなどの暗号化された通信路を利用することをお勧めします。

## その他の認証方法

Basic認証やDigest認証はHTTPの仕様として定義されているものです。
しかし、実際のWebアプリケーションでは(とくにここ最近では)これらの認証はあまり使われていません。

では実際はどのようなものが使用されているのでしょうか。

- Cookie認証
- トークン認証(JWTなど)
- OAuth2.0
- SAML
- OpenID Connect
- [パスキー](passkey.md)

多様な方法が存在しますが、これらはHTTPの仕様ではなくアプリケーション側での実装となっています。
これらの認証方法は、より柔軟で安全な認証を提供するために設計されています。

## シングルサインイン(シングルサインオン)

シングルサインイン(混乱しやすいですがサイン **オン**とも呼ばれます、共に略語としてはSSO(Single Sign-On)と呼ばれます)は、一度の認証で複数のサービスにアクセスできる仕組みです。

たとえばGoogleアカウントやMicrosoftアカウントが例となります。
これらのアカウントでログインすると、関連サービス(メールやカレンダー、ドキュメントなど)に再度ログインすることなく利用できるようになっています。
また、その他のサービスでも、GoogleアカウントやMicrosoftアカウントを認証の代わりに使用することで、ユーザは新たにアカウントを作成することなくサービスを利用できるようになります。

もともとこの仕組みは、企業内での複数サービス利用において、一カ所での認証から発行されるチケットを使うという考え方で考案されたものから発展しています(Kerberos認証)。


## おまけ: Kerberos認証

パスワードを含め、認証に関しては非常にセンシティブな情報と捉えていろいろと研究が行われました。その結果として、以下の2点が重要であると考えられています。

- パスワードは平文で送信しない、どうしても必要なら暗号化された経路で行う
- そもそもパスワードを送信しない

HTTPのBasic認証はパスワードを事実上平文で送っているため、現代では使うべきものとはされていません(ただし、HTTPSによる暗号化で守られている場合は別です)。
Digest認証であれば、パスワード自体は送信しないためまだ安全ですが、計算が面倒ということもあり、あまり使われていません[^digest-pass]。

[^digest-pass]: Digest認証はその仕組み上、サーバー側にパスワードを平文で保存しておく必要があり、サーバー上のセキュリティという部分が生じてしまいます。

そこで後者の『そもそもパスワードを送信しない』という考え方に基づいて設計された認証方式がKerberos認証です。
Kerberos認証は、分散システムにおいていかに安全に認証を行うかということについて研究されたAthenaプロジェクトの成果の一つです。

そんなケルベロス認証のフローは、大雑把に以下のようになります。
チケットを対象のサービスに提出することで認証とするメカニズムとなっています。

```{mermaid}
sequenceDiagram
    participant C as クライアント
    participant K as KDC
    participant S as サービス

    C->>K: ログイン(AS)
    K->>C: TGT + セッション鍵
    C-->>C: 鍵を復号して保存
    C->>K: TGT添付でチケット要求
    K->>C: サービスチケット発行
    C->>S: サービス要求 (チケット + Auth)
    S-->>S: チケット復号・検証
    S->>C: サービス提供
```

以下は図の補足です。

- KDC: Key Distribution Centerの略で、認証を行い TGT やサービスチケットを発行するサーバ。
- TGT: Ticket Granting Ticket（再利用して各サービス用チケットを取得するためのチケット）。
- セッション鍵: クライアントとサービス間での一時鍵（通信保護や Authenticator の生成に使用）。
- Auth(Authenticator): セッション鍵で暗号化された時刻やID情報で、リプレイ防止に使われる。
