# DNS

UDPを使ったプロトコルのひとつであるDNSを通して、UDPの理解を少しだけ深めてみましょう。
DNSは、日常のインターネット利用において非常に重要な役割を果たしています。DNSは、ドメイン名をIPアドレスに変換するためのシステムであり、インターネット上のリソースにアクセスする際に必要不可欠です。

## DNSの基本

DNSは、ドメイン名をIPアドレスに変換するための階層的なシステムです。以下のような構成要素があります。
- ルートDNSサーバ
- TLD(トップレベルドメイン)サーバ
- 権威DNSサーバ
- DNSリゾルバ(キャッシュサーバー)
- クライアント

```{mermaid}
flowchart TD
    Client[クライアント]
    Resolver[DNSリゾルバ]
    Root[ルートDNSサーバー]
    TLD[TLDサーバー]
    Authoritative[権威DNSサーバー]
    DNS_Server[DNSサーバー]

    Client -->|DNSリクエスト| Resolver
    Resolver -->|問い合わせ| DNS_Server
    DNS_Server -->|応答| Resolver
    Root -->|TLDサーバー情報| DNS_Server
    TLD -->|権威サーバー情報| DNS_Server
    Authoritative -->|最終的な応答/ヒント| DNS_Server
    Resolver -->|応答| Client
    DNS_Server -->|問い合わせ| Root
    DNS_Server -->|問い合わせ| TLD
    DNS_Server -->|問い合わせ| Authoritative

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

```{note}
Windowsでは、DNS Clientというサービスが動いていることがあります。
これはローカルのキャッシュDNSサーバーみたいなもので、DNSリゾルバと実際に呼ぶDNS(キャッシュ)サーバーの間に入る形で機能します。
役割は『DNSサーバーからの応答をキャッシュする』です。
```

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

この場合、多数存在するTLDを階層構造の頂点としてまとめるのが、**ルートドメイン**というものです。これは単純に"`.`"であり、TLDの右側に位置します。
ルートドメインの表記は『これ以上後はない』を意味するため、UNIXなどのOSで登場する『ルートディレクトリ』のような意味合いとなります。

- `www.example.com`のような末尾にピリオドがないホスト名は、リゾルバの設定によってはローカルの検索ドメインが付加されて解釈されることがあります。
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

    %% キャッシュサーバーから各部への点線矢印(順序付き)
    CacheServer -.->|1| A
    CacheServer -.->|2| E
    CacheServer -.->|3| I
    CacheServer -.->|4| L
    CacheServer -.->|5| M
```
このように、キャッシュサーバーは順番に問い合わせを行います。

このように、キャッシュサーバーは必要に応じてルートドメインや各TLD、さらに下位のドメインへ問い合わせを行い、最終的に目的のホスト(ここでは `www.someshop.co.jp` など)にたどり着きます。

## 権威サーバー

権威サーバーは、それ自身がなんらかの情報を持つサーバーです。
コンテンツサーバーとも言えます。
ルートサーバーも権威サーバーのひとつとなります。
権威サーバーの持つ情報は各種あります。

- ドメイン名とIPアドレスの対応
- 自身の配下ドメインへの委任情報(NSレコードなど)
- ドメイン名の所有者情報

といったものが該当します。
権威サーバーは自身が情報を持つということから『コンテンツサーバー』とも呼ばれることがあります。
リゾルバや末端の(問い合わせを受ける)DNSサーバーは、役割としてはコンテンツサーバーに対する『キャッシュサーバー』という立ち位置に扱われます。

## NICの役割

ここで突然ですが、NIC(Network Information Center)という言葉が出てきます。
NICは、主に国別トップレベルドメイン(ccTLD)の管理指針を定めたり、ドメイン名の登録規則を策定したりする組織です。日本ではJPNICがこれに該当し、実際の`.jp`ドメインの管理・運用は株式会社日本レジストリサービス(JPRS)が行っています。
NICは、ドメイン名の登録や管理を行う組織であり、各国に存在します。

NICの管理業務として、その国(管理範囲)におけるDNSの管理が含まれています。
TLDのサーバーとそこに含めるSLDの登録・保守が入ります。

自分のドメインを持ちたいとき、最終的にはNICに連絡が行き、登録が行われることになります。
この際に登録される情報がwhois情報であり、ドメインの所有者として公開されます。
たとえば `kobedenshi.ac.jp` というドメインを取得している場合、[このように](https://whois.jprs.jp/?key=kobedenshi.ac.jp)公開されます[^jprs]。

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
| PTR | 逆引き(IPアドレスからホスト名) | IPアドレス |

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
- とはいえ、応答メッセージがUDPペイロードサイズの制限(伝統的には512バイト)を超える場合は、TCPに切り替えて通信を行います。よってDNSはUDPが基本ですが、TCPも使います。
  - 通常クエリで512バイトを超えることはありませんが、DNSSECと呼ばれるセキュリティ拡張などでは超えてしまうことがあります。この場合、UDPでの応答時にフラグが立てられて、受信したクエリ側はTCPで再度問い合わせを行うことになります。
  - DNS間での情報の転送(ゾーン転送など)はTCPを使います。これは、DNSサーバー間での情報の完全な転送が必要なためです。


[^public_dns]: [詳細について](https://developers.google.com/speed/public-dns)、広く使われているのは8.8.8.8と8.8.4.4。
[^cloudflare_dns]: [詳細について](https://developers.cloudflare.com/)、広く使われているのは1.1.1.1。
[^NIS]: [NISについて](https://ja.wikipedia.org/wiki/Network_Information_Service)、グループ内のUNIX間での情報共有を目的としたシステムです。現在はあまり使われていません。
[^tld-ttl]: TLDのTTLは通常24時間から48時間程度です。そのため1〜2日に1回程度の利用となります。
[^jprs]: 日本でのNICはJPNICですが、ドメイン管理部分についてはJPRSという組織に業務が移管されています。
[^host-v]: といいつつ、`host -v`(verbose)オプションを付けると、かなり`dig`寄りの出力になります。

## 現代的なDNS技術

```{note}
この部分は高度な専門技術に関する内容です。応用情報技術者試験レベルを超える内容のため、初学者の方はスルーしても構いません。
```

2025年現在、DNSはセキュリティとプライバシーの強化、高可用性、そして新しいネットワーク環境への対応で大幅に進歩しています。

### DNS暗号化技術

#### DNS over HTTPS (DoH)

HTTP/2またはHTTP/3を使用してDNSクエリを暗号化する技術です。

- **RFC 8484準拠**: HTTPS上でのDNSメッセージ交換標準
- **ブラウザサポート**: Firefox、Chrome、Edge等が標準サポート
- **CDN統合**: Cloudflare(1.1.1.1)、Google(8.8.8.8)等でのDoH提供
- **プライバシー保護**: ISPや中間者によるDNS監視の防止

#### DNS over TLS (DoT)

TLSを使用してDNSクエリを暗号化する技術です。

- **RFC 7858準拠**: ポート853でのセキュアDNS通信
- **軽量**: HTTPSより低オーバーヘッドでの暗号化
- **モバイル対応**: Android 9以降で標準サポート
- **エンタープライズ**: 企業ネットワークでの導入増加

#### DNS over QUIC (DoQ)

QUICプロトコルを使用した最新のDNS暗号化技術です。

- **RFC 9250**: 2022年制定の新しい標準
- **高性能**: 0-RTT接続による高速化
- **耐障害性**: パケット損失に対する高い耐性
- **将来性**: HTTP/3同様の技術基盤

### DNSSEC (DNS Security Extensions)

DNSレスポンスの完全性と認証を保証する技術です。

#### 暗号学的保証

- **デジタル署名**: DNSレコードへの暗号学的署名
- **チェーンオブトラスト**: ルートから末端ドメインまでの信頼チェーン
- **レスポンス検証**: DNSハイジャック・汚染攻撃の防止

#### 実装状況と課題

- **トップレベルドメイン**: 主要TLDでのDNSSEC対応完了
- **権威サーバー**: 多くの権威DNSサーバーでサポート
- **リゾルバサポート**: Google Public DNS、Cloudflare等で標準対応
- **複雑性**: 鍵管理と設定の複雑さが課題

### 現代的なDNS運用技術

#### Anycast DNS

- **地理的分散**: 世界中の複数拠点からのDNS提供
- **負荷分散**: クエリ負荷の自動分散
- **耐障害性**: 単一拠点障害時の自動フェイルオーバー
- **レイテンシ最適化**: 地理的に最適なサーバーからの応答

#### DNS Load Balancing

- **Health Check**: サーバーの生存監視と自動切り替え
- **Weighted Round Robin**: 重み付けによる負荷分散
- **GeoDNS**: ユーザーの地理的位置に基づく最適化
- **Failover**: プライマリサーバー障害時の自動切り替え

### IPv6対応とDual Stack

#### IPv6でのDNS

- **AAAAレコード**: IPv6アドレスの正引き対応
- **PTRレコード IPv6**: IPv6の逆引き(.ip6.arpa)
- **Dual Stack DNS**: IPv4/IPv6両対応のDNSサーバー運用

#### DNS64/NAT64連携

IPv6オンリー環境からIPv4サービスへのアクセスを実現します。

- **DNS64**: IPv4アドレスをIPv6アドレスにマッピング
- **NAT64**: IPv6-IPv4間のアドレス変換
- **Well-Known Prefix**: 64:ff9b::/96等の標準プレフィックス使用

### DNS over HTTPSの実装例

#### パブリックDNS over HTTPSサービス

| プロバイダ | DoH URL | 特徴 |
|-----------|---------|------|
| Cloudflare | https://cloudflare-dns.com/dns-query | 高速、プライバシー重視 |
| Google | https://dns.google/dns-query | 安定性、広範囲カバレッジ |
| Quad9 | https://dns.quad9.net/dns-query | セキュリティ特化 |
| CleanBrowsing | https://doh.cleanbrowsing.org/doh/family-filter/ | フィルタリング機能 |

### 新しいDNSレコードタイプ

#### 現代的なレコードタイプ

- **CAA レコード**: SSL証明書発行権限の制限
- **TLSA レコード**: DANE(DNS-based Authentication of Named Entities)
- **SVCB/HTTPS レコード**: HTTP/3、QUIC等のサービス発見
- **ZONEMD レコード**: DNSゾーンの完全性検証

### セキュリティ強化技術

#### DNS Filtering

- **マルウェア対策**: 悪意のあるドメインへのアクセスブロック
- **フィッシング対策**: 既知の詐欺サイトのブロック
- **コンテンツフィルタリング**: 企業・教育機関でのアクセス制御

#### DNS Monitoring と Analytics

- **異常検知**: 機械学習を活用したDNS異常行動の検出
- **脅威インテリジェンス**: リアルタイムでの脅威情報統合
- **パフォーマンス監視**: DNSクエリレスポンス時間の最適化

### エッジコンピューティングとDNS

#### Edge DNS

- **CDN統合**: コンテンツ配信との密な連携
- **Edge Computing**: エッジでのDNS処理と最適化
- **Local Breakout**: 企業ネットワークでのローカルDNS処理

#### Cloud-Native DNS

- **Kubernetes統合**: Service Discovery との統合
- **Microservices**: マイクロサービス間でのDNSベース名前解決
- **Container DNS**: Docker、Podman等でのDNS自動化

これらの技術により、DNSは単なる名前解決から、現代ネットワークのセキュリティとパフォーマンスの要となる重要インフラへと発展しています。
