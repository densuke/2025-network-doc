# DNS

UDPを使ったプロトコルのひとつであるDNSを通して、UDPの理解を少しだけ深めてみましょう。
DNSは、日常のインターネット利用において非常に重要な役割を果たしています。DNSは、ドメイン名をIPアドレスに変換するためのシステムであり、インターネット上のリソースにアクセスする際に必要不可欠です。

## DNSの基本

DNSは、ドメイン名をIPアドレスに変換するための階層的なシステムです。以下のような構成要素があります。
- ルートDNSサーバ
- TLD（トップレベルドメイン）サーバ
- 権威DNSサーバ
- DNSリゾルバ（キャッシュサーバ）
- クライアント

```{mermaid}
flowchart TD
    Client[クライアント]
    Resolver[DNSリゾルバ]
    Root[ルートDNSサーバ]
    TLD[TLDサーバ]
    Authoritative[権威DNSサーバ]
    DNS_Server[DNSサーバ]

    Client -->|DNSリクエスト| Resolver
    Resolver -->|問い合わせ| DNS_Server
    DNS_Server -->|問い合わせ| Root
    Root -->|TLD情報| TLD
    TLD -->|権威サーバ情報| Authoritative
    Authoritative -->|最終的な応答| Resolver
    Resolver -->|応答| Client
```

少し仰々しい用語で書いているためわかりにくいですが、実は身近なところで動いています。

- クライアントは、ウェブブラウザやアプリケーションなど、DNSを利用する端末です。
- DNSリゾルバは、クライアントのリクエストを受け取り『どのようにそのリクエストに応えるか』を決定します。一般的な実装はシステムの提供するライブラリのようなもので、OSに組み込まれています。リゾルバでは、各種の手段が提供されており、その中からの選択を行っています。
  - 静的ホストテーブル(`/etc/hosts`など)
  - キャッシュされたDNS情報
  - DNSサーバーへの問い合わせ
  - WindowsなどではActive DirectoryのDNS情報も該当します
  - 古いUNIX系統ではNIS[^NIS]を利用していることもあります
- DNSサーバーは、一番近いDNSのサーバーであり、プロバイダにより提供されます。
    - アクセスポイントを設置している場合、アクセスポイントがその機能を引き継ぐ形になっていることが大半です。
    - Google提供のPublic DNS[^public_dns]や、CloudflareのDNS[^cloudflare_dns]などもあります。
    - DNSサーバーは『キャッシュ』の機能を持っており、以前の問い合わせが使える場合はその情報を返します
    - 含まれていない場合は、ルートDNSサーバーに問い合わせを行います

DNSサーバーの問い合わせは、必要に応じて繰り返し行われていきます。

このシーケンス図は、クライアントから始まるDNS問い合わせの流れを示しています。  
ルートDNSサーバーはTLDサーバーの情報を提供し、TLDサーバーは権威DNSサーバーの情報を返します。  
最終的に権威DNSサーバーから得られたIPアドレスがクライアントに返されます。

```{mermaid}
sequenceDiagram
    participant Client as クライアント
    participant Resolver as DNSリゾルバ
    participant DNS_Server as DNSサーバー
    participant Root as ルートDNSサーバー
    participant TLD as TLDサーバー
    participant Authoritative as 権威DNSサーバー

    Client->>Resolver: ドメイン名の問い合わせ
    Resolver->>DNS_Server: 問い合わせ
    DNS_Server->>Root: ルートDNSサーバーに問い合わせ
    Root-->>DNS_Server: TLDサーバー情報を返す
    DNS_Server->>TLD: TLDサーバーに問い合わせ
    TLD-->>DNS_Server: 権威DNSサーバー情報を返す
    DNS_Server->>Authoritative: 権威DNSサーバーに問い合わせ
    Authoritative-->>DNS_Server: 最終的なIPアドレスを返す
    DNS_Server-->>Resolver: 回答を返す
    Resolver-->>Client: 回答を返す
```

DNSリゾルバやDNSサーバーは『キャッシュ』が用意されており、以前の問い合わせ内容を覚えています。
各内容には「TTL(Time To Live)」と呼ばれる有効期限が設定されており、これが切れるまでの間は再度問い合わせを行う必要はありません。そのため、上記シーケンス図ではルートDNSサーバーへの問い合わせが含まれていますが、実際にはそんなに頻繁に使われることはありません。こういう上位のDNSサーバーの場合、非常に長いTTLが設定されていることが多い[^tld-ttl]です。

## ドメインツリー構造

上記の説明でTLDといった用語が登場しました。これを理解するために、DNSが背景として持つ『ドメインツリー』という空間および構造について説明します。

私たちは、インターネット上のサービス(リソース)へアクセスする際、一般的に『ホスト名』『サーバー名』と言ったものを使って接続先を認識しています。この名前を正確に書くと、ピリオド(.)で区切られた名前になることはご存じだと思います。

例えば、`www.example.com`という名前は、以下のように分解できます。

- `www`というホストは、`example.com`というドメイン(組織)の一部である。
- `example`は`com`というドメインの一部である。

このように、左にある部分は、右にある部分(組織)に属しているという関係を持っています。
これはツリー状に表現できます。

この時、最上位(表記上の一番右側のもの)をTLD(Top Level Domain)と呼びます。
あまり表記しませんが、TLD直下のものはSLD(Second Level Domain)と呼ばれたりもします。

```{mermaid}
graph TD
    B[TLD: com]
    C[example]
    D[www]

    B --> C
    C --> D
```


TLDは様々なものがあります。

- 国とは関係ない汎用TLD
  - `com` (商用)
  - `org` (組織)
  - `net` (ネットワーク)
  - `info` (情報)

- 国別TLD
  - `jp` (日本)
  - `us` (アメリカ)
  - `uk` (イギリス)
  - `de` (ドイツ)

最近では、一風変わったというべきものも増加していますね。

- `app` (アプリケーション)
- `dev` (開発)
- `shop` (ショップ)
- `blog` (ブログ)
- `tech` (テクノロジー)

たとえば日本の学校では、SLD部分に属性として`ac`を用いることで「学校(もしくは教育機関)である」と示されます。

この場合、TLDが大量に存在することになるため、それを集約するための存在として、**ルートドメイン**というものを用意します。これは単純に"."であり、TLDの右側に位置します。
ルートドメインの表記は『これ以上後はない』を意味するため、UNIXなどのOSで登場する『ルートディレクトリ』のような意味合いとなります。

- `www.example.com`の場合『もしかしたら`com`の後にまだ続くものがあるかもしれない』と判断されます。
- ですが、`www.example.com.`のように末尾にピリオドが付いている場合は『これ以上後はない』と判断されます。ルートドメインであることの判断は、検索を行う際の起点を正しく認識するために重要となります。

```{note}
ただし、実際に私たちがホスト名表記を行うときは、ルートドメインの表記をすることはまずありません。
これは、リゾルバが渡された文字列(ホスト名と思われるもの)に対して、以下のルールを適用しているためです。

1. とりあえず渡された文字列そのもので判断してみる(`foo` -> `foo.`)
2. 判断できなかった場合、自分のコンピュータ内であらかじめ決めておいたドメインを付加して判断してみる(`foo` -> `foo.localdomain.`)
3. それでも判断できないときは、ネットワークの構成時に得ていたドメインを付加して判断してみる

付加された文字列は一般的にルートドメインは付与されていませんが、暗黙で付与されたとみなして検索を行うようになっています。
```

これにより、各種TLDを含めてひとつのツリー構造に納めることができます。

例えば、DNSのドメインツリー構造は以下のように表現できます。

```{mermaid}
graph RL
    A[ルートドメイン]
    B[TLD: com]
    subgraph C[example]
        D[www]
    end
    E[TLD: jp]
    F[ac]
    subgraph G[example]
        H[www]
    end
    I[co]
    subgraph J[example]
        K[hogehoge]
    end
    subgraph L[someshop]
        M[www]
    end

    %% ツリー構造
    A --> B
    B --> C

    A --> E
    E --> F
    F --> G

    E --> I
    I --> J
    J --> K
    I --> L
    L --> M
```

このツリーにキャッシュサーバーがアクセスする場合、以下のような形になります。

```{mermaid}
graph RL
    A[ルートドメイン]
    B[TLD: com]
    subgraph C[example]
        D[www]
    end
    E[TLD: jp]
    F[ac]
    subgraph G[example]
        H[www]
    end
    I[co]
    subgraph J[example]
        K[hogehoge]
    end
    subgraph L[someshop]
        M[www]
    end

    CacheServer[キャッシュサーバー]

    %% ツリー構造
    A --> B
    B --> C

    A --> E
    E --> F
    F --> G

    E --> I
    I --> J
    I --> L

    %% キャッシュサーバーから各部への点線矢印（順序付き）
    CacheServer -.->|1| A
    CacheServer -.->|2| E
    CacheServer -.->|3| I
    CacheServer -.->|4| L
    CacheServer -.->|5| M
```
このように、キャッシュサーバーは順番に問い合わせを行います。

このように、キャッシュサーバーは必要に応じてルートドメインや各TLD、さらに下位のドメインへ問い合わせを行い、最終的に目的のホスト（ここでは `www.someshop.co.jp` など）にたどり着きます。

## 権威サーバー

権威サーバーは、それ自身がなんらかの情報を持つサーバーです。
コンテンツサーバーとも言えます。
ルートサーバーも権威サーバーのひとつとなります。
権威サーバーの持つ情報は各種あります。

- ドメイン名とIPアドレスの対応
- 自身の配下ドメインへの委任情報（NSレコードなど）
- ドメイン名の所有者情報

といったものが該当します。
権威サーバーは自身が情報を持つということから『コンテンツサーバー』とも呼ばれることがあります。
リゾルバや末端の(問い合わせを受ける)DNSサーバーは、役割としてはコンテンツサーバーに対する『キャッシュサーバー』という立ち位置に扱われます。

## NICの役割

ここで突然ですが、NIC(Network Information Center)という言葉が出てきます。
NICはグローバルアドレスの割り当ての際にRIRからおりてくる情報を管理する組織です。日本ではJPNICが該当します。
NICは、ドメイン名の登録や管理を行う組織であり、各国に存在します。

NICの管理業務として、その国(管理範囲)におけるDNSの管理が含まれています。
TLDのサーバーとそこに含めるSLDの登録・保守が入ります。

自分のドメインを持ちたいとき、最終的にはNICに連絡が行き、登録が行われることになります。
この際に登録される情報がwhois情報であり、ドメインの所有者として公開されます。
たとえば"kobedenshi.ac.jp"というドメインを取得している場合、[このように](https://whois.jprs.jp/?key=kobedenshi.ac.jp)公開されます[^jprs]。

## リソースレコード(RR)

DNSの権威サーバー(コンテンツサーバー)は、保有する情報に対して『それがなんの情報なのか』を示せるように、リソースレコードという形式で情報を保有しています。

私たちが問い合わせをするとき(もちろんキャッシュサーバーを通して)は、このリソースレコードを参照することになります。
例えるなら、DNSサーバーは関数みたいなもので、引数にリソースレコードの種類と、問い合わせたい情報を渡すようなものです。

```
result = DNS_Query("www.example.com", "A")
```

リソースレコードには、主に以下のようなものが存在します。

|種類 | 説明 | 渡す情報 |
|---|---|---|
| A | IPv4アドレス | ホスト名 |
| AAAA | IPv6アドレス | ホスト名 |
| CNAME | 別名(エイリアス) | ホスト名 |
| MX | メールサーバーの情報 | ドメイン名 |
| NS | ネームサーバーの情報 | ドメイン名 |
| TXT | 任意のテキスト情報 | ドメイン名 |
| SOA | スタートオブオーソリティ、権威サーバーの情報 | ドメイン名 |
| PTR | 逆引き(ホスト名からIPアドレス) | IPアドレス |

- MXレコードは、メールを送る際に『どのメールサーバーがこのメールを受け取ってくれるのか』を調べるために使います。
    - 冗長性のために複数のメールサーバーが取得できることがありますが、各メールサーバーには優先度が割り付けられており、それに従ってメールサーバーは選択されます。
- PTRレコードは、IPアドレスからホスト名を調べるために使います。通常と逆向き(ホスト→IPアドレスではなくIPアドレス→ホスト)の問い合わせを行うことから**逆引き**とも呼ばれています。
    - 逆引きをするときは、対象となるIPアドレスを逆順にして、末尾に`.in-addr.arpa`を付けて問い合わせます。
    - 例: 192.168.10.1 → 1.10.168.192 → 1.10.168.192.in-addr.arpa

通常これらはアプリケーション用のライブラリ(API)によって自動的にリゾルバに渡されて問い合わせが行われますが、直接DNSサーバーへ問い合わせるためのツールとして、`nslookup`や`dig`、`host`といったコマンドラインツールが存在します。

- Windowsでは`nslookup`が標準で用意されています。
- LinuxやmacOSでは`dig`や`host`が標準で用意されています。

`dig`コマンドは情報を詳細に出します、そこまで詳細なものが必要ないときは一般的に`host`コマンドが使われます[^host-v]。

Windowsでのnslookupの使用例はこのような形になります。

```pwsh
PS> nslookup www.kobedenshi.ac.jp
サーバー:  dns.google
Address:  8.8.8.8

権限のない回答:
名前:    www.kobedenshi.ac.jp
Address:  35.76.177.158

nslookup -type=mx kobedenshi.ac.jp
サーバー:  dns.google
Address:  8.8.8.8

権限のない回答:
kobedenshi.ac.jp        MX preference = 5, mail exchanger = alt2.aspmx.l.google.com
kobedenshi.ac.jp        MX preference = 1, mail exchanger = aspmx.l.google.com
kobedenshi.ac.jp        MX preference = 5, mail exchanger = alt1.aspmx.l.google.com
```

```{note}
『権威のない回答』と出ていますが、これはキャッシュサーバーにあたるリゾルバが権威サーバーに問い合わせて得たキャッシュからのためです。
あくまで『他のサーバーから得た情報を出している』というキャッシュサーバー自身は『権威はない』ということで、このような表記になっています。
```


Linux(授業用のVMなど)で同様のクエリを`host`で行うと、以下のようになります。

```bash
$ host www.kobedenshi.ac.jp
www.kobedenshi.ac.jp has address 35.76.177.158
$ host -t mx kobedenshi.ac.jp
kobedenshi.ac.jp mail is handled by 5 alt2.aspmx.l.google.com.
kobedenshi.ac.jp mail is handled by 1 aspmx.l.google.com.
kobedenshi.ac.jp mail is handled by 5 alt1.aspmx.l.google.com.
```

## DNSとUDP

DNSはUDPを使用して通信を行います。

- UDPはコネクションレスのため、実際にクエリを送信できたのかはわかりません。
- そのため『一定時間に返答があるか』で対応しています。
- DNSはその役割上『素早く処理ができる』ことが求められています。そのため速度を重視したUDPとなります。
  - 本当に求められているのはその後の通信のためです。
- クエリや応答のパケットが途中で分割されてしまうと、残りのデータを待つ必要があるため、DNSメッセージの伝統的なUDPペイロードサイズ上限である512バイトに収まるように構造が設計されていました。
- とはいえ、なんらかの理由で512バイトを超える場合は、TCPに切り替えて通信を行います。よってDNSはUDPが基本ですが、TCPも使います。
  - 通常クエリで512バイトを超えることはありませんが、DNSSECと呼ばれるセキュリティ拡張などでは超えてしまうことがあります。この場合、UDPでの応答時にフラグが立てられて、受信したクエリ側はTCPで再度問い合わせを行うことになります。
  - DNS間での情報の転送(ゾーン転送など)はTCPを使います。これは、DNSサーバー間での情報の完全な転送が必要なためです。


[^public_dns]: [詳細について](https://developers.google.com/speed/public-dns)、広く使われているのは8.8.8.8と8.8.4.4。
[^cloudflare_dns]: [詳細について](https://developers.cloudflare.com/)、広く使われているのは1.1.1.1。
[^NIS]: [NISについて](https://ja.wikipedia.org/wiki/Network_Information_Service)、グループ内のUNIX間での情報共有を目的としたシステムです。現在はあまり使われていません。
[^tld-ttl]: TLDのTTLは通常24時間から48時間程度です。そのため1〜2日に1回程度の利用となります。
[^jprs]: 日本でのNICはJPNICですが、ドメイン管理部分についてはJPRSという組織に業務が移管されています。
[^host-v]: といいつつ、`host -v`(verbose)オプションを付けると、かなり`dig`寄りの出力になります。
