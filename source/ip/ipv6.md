# IPv6

IPv6は、IPv4でうまく対応できなかった部分に対応するために開発された『次世代のIP』となります。
どの部分が変更されているのかについて、確認していきましょう。

## IPv4ではなにが問題だったのか?

IPv4は、1980年代に開発され、インターネットの基盤として広く使われてきました。
しかし、1980年台ということもあり、現代(2020年台)においては多くの問題が発生しています。
これらはプロトコルとして発表された頃から指摘があったものも含まれていますが、様々な理由により、現在でも稼働し続けているのがIPv4です。

では、なにが問題なのでしょうか?
大まかには以下のようものが考えられます。

- アドレス空間の枯渇
- セキュリティの脆弱性
- ネットワークの複雑化

### アドレス空間の枯渇

IPv4では、32ビットのアドレス空間を提供しています。
これにより、32ビットである約43億のアドレス空間を用いることができたわけですが、同時に『上限が約43億』ということもあり、インターネットが普及した現代においてはアドレスが不足しています。

- IANAによるアドレス配布(グループの割り当て)は、2011年に終了しています[^iana-exhaust]。
- 各地域のRIR(Regional Internet Registry)によるアドレス配布も、2015年には枯渇しています。
- その後も、各国のISP(インターネットサービスプロバイダ)などが独自にアドレスを割り当てているものの、IPv4アドレスは枯渇しています。
- 2025年現在では、IPv4アドレスは高額で取引される希少なリソースとなっており、IPv4アドレスブロックの売買市場が形成されています。例えば、/24ブロック(256アドレス)が市場価格に応じて取引されることもあります。
- なお、IPv4アドレスの価格は市場の需要と供給により変動するため、具体的な価格については最新の情報を確認してください。
- このような状況により、多くの組織がCarrier Grade NAT(CGN)やIPv6デュアルスタック、IPv6移行技術(464XLAT、DNS64/NAT64等)を活用してIPv4アドレス不足に対応しています。

```{note}
現在では、各RIRの間で『返却されて余った部分を他のRIRへ融通する』ことが認められています。
そのため、細かい範囲での移動が発生しており、現在のアドレスがどのRIRの管理下にあるのかはかなりカオスです。

各RIRでは、定期的(毎日)その情報がリストとして公開されるようになっています。

- [ARINでの例(最新版)](https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest)


[^iana-exhaust]: IANA (Internet Assigned Numbers Authority): インターネットにおけるIPアドレスやドメイン名などの資源を管理する国際的な組織
```

そういったこともあってか、IPv6では128ビットのアドレス空間となりました。
これにより、IPv6では約340澗(3.4×10^38)のアドレス空間を提供することができます。

想像しにくい数字になっていますが、以下のように考えてみると『すごく大きい』ことは感じられるかと思います。

- IPv6の各アドレスを虫ピンと仮定する
- これを地球表面に等間隔に刺していくと仮定する
    - 海や山は考慮せず、単純な球体と仮定しておく
- この場合、1平方メートルあたり、6.7*10^23の虫ピンが刺さると考えられる[^ipv6-address]。

[^ipv6-address]: 1平方メートルあたりの虫ピンの数は、地球の表面積(約510,000,000平方キロメートル)をIPv6アドレス数(340澗)で割った値です。

このような巨大な空間のため、IPv4のように『接続時にひとつのアドレスを貸し出す』というレベルではなく、ルーター(アクセスポイントなど)に対して、ブロックでの貸し出しが行えるような状況となっています。

IPv6アドレスは、16ビット毎をコロン(`:`)で区切って表記されますが、同時に渡されるネットマスクのビット長がIPv4と違ってかなり広い扱いになっています。
例えば、`2001:db8::/32`のように、ネットマスクのビット長が32ビットであることを示しています。
そのため、残り96ビット(128-32=96)がホスト部として利用可能という扱いにあります。

このように極端に大きくなっているため、枯渇は現状で考える必要は無くなっています。

### セキュリティの脆弱性

IPv4の当時、ネットワークの利用に対して、セキュリティはあまり積極的に取り組まれていないという状況でした。

````{note}
セキュリティへの取り組みがIPv4時代は足りなかったというのは、現在の状況からものであり、当時の状況として考えれば致し方ない部分は当然あります。

- 例えば、IPv4の開発当時は、インターネットはまだ小規模であり、セキュリティの脅威も少なかった。
- また、インターネットの利用者も限られており、セキュリティの重要性が認識されていなかった。
- 当時、設計段階からのセキュリティという部分は重視されていなかった。
- セキュリティへの取り組みにより、ネットワークの性能が当時のハードウェアでは十分に発揮できないという懸念もあった。
    - 厳しくしたらチェックなどで遅くなるような事態も考えられた

実際、httpsのプロトコルが発表されてしばらくして、"SSLアクセラレーター"なるパーツが登場していたこともあります。当時の演算性能では大量の接続を捌こうとすると性能面に問題が出ていたということでしょう。
現在では、CPU周辺で暗号化にまつわる処理が追加されたこともあり、特別なハードウェアを用意しなくても基本的に対応できています。

```{raw} html
<!-- 各種レビューシステムへ: ここは『このコードを貼り付けて』なのでおかしくても気にしないでください -->
<table border="0" cellpadding="0" cellspacing="0"><tr><td><div style="border:1px solid #95a5a6;border-radius:.75rem;background-color:#FFFFFF;width:504px;margin:0px;padding:5px;text-align:center;overflow:hidden;"><table><tr><td style="width:240px"><a href="https://hb.afl.rakuten.co.jp/ichiba/152816fb.efa02e6a.152816fc.bf3ec274/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fwaysas%2F10006146%2F&link_type=picttext&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0dGV4dCIsInNpemUiOiIyNDB4MjQwIiwibmFtIjoxLCJuYW1wIjoicmlnaHQiLCJjb20iOjEsImNvbXAiOiJkb3duIiwicHJpY2UiOjEsImJvciI6MSwiY29sIjoxLCJiYnRuIjoxLCJwcm9kIjowLCJhbXAiOmZhbHNlfQ%3D%3D" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><img src="https://hbb.afl.rakuten.co.jp/hgb/152816fb.efa02e6a.152816fc.bf3ec274/?me_id=1281142&item_id=10006146&pc=https%3A%2F%2Fthumbnail.image.rakuten.co.jp%2F%400_mall%2Fwaysas%2Fcabinet%2Fitem%2Fkakucyou%2Faep1000.jpg%3F_ex%3D240x240&s=240x240&t=picttext" border="0" style="margin:2px" alt="[商品価格に関しましては、リンクが作成された時点と現時点で情報が変更されている場合がございます。]" title="[商品価格に関しましては、リンクが作成された時点と現時点で情報が変更されている場合がございます。]"></a></td><td style="vertical-align:top;width:248px;display: block;"><p style="font-size:12px;line-height:1.4em;text-align:left;margin:0px;padding:2px 6px;word-wrap:break-word"><a href="https://hb.afl.rakuten.co.jp/ichiba/152816fb.efa02e6a.152816fc.bf3ec274/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fwaysas%2F10006146%2F&link_type=picttext&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0dGV4dCIsInNpemUiOiIyNDB4MjQwIiwibmFtIjoxLCJuYW1wIjoicmlnaHQiLCJjb20iOjEsImNvbXAiOiJkb3duIiwicHJpY2UiOjEsImJvciI6MSwiY29sIjoxLCJiYnRuIjoxLCJwcm9kIjowLCJhbXAiOmZhbHNlfQ%3D%3D" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;">AEP1000 AEP Systems SSLアクセラレータ 64bit PCI対応【中古】</a><br><span >価格：9,800円(税込、送料無料)</span> <span style="color:#BBB">(2025/6/2時点)</span></p><div style="margin:10px;"><a href="https://hb.afl.rakuten.co.jp/ichiba/152816fb.efa02e6a.152816fc.bf3ec274/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fwaysas%2F10006146%2F&link_type=picttext&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0dGV4dCIsInNpemUiOiIyNDB4MjQwIiwibmFtIjoxLCJuYW1wIjoicmlnaHQiLCJjb20iOjEsImNvbXAiOiJkb3duIiwicHJpY2UiOjEsImJvciI6MSwiY29sIjoxLCJiYnRuIjoxLCJwcm9kIjowLCJhbXAiOmZhbHNlfQ%3D%3D" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><img src="https://static.affiliate.rakuten.co.jp/makelink/rl.svg" style="float:left;max-height:27px;width:auto;margin-top:0" ></a><a href="https://hb.afl.rakuten.co.jp/ichiba/152816fb.efa02e6a.152816fc.bf3ec274/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fwaysas%2F10006146%2F%3Fscid%3Daf_pc_bbtn&link_type=picttext&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0dGV4dCIsInNpemUiOiIyNDB4MjQwIiwibmFtIjoxLCJuYW1wIjoicmlnaHQiLCJjb20iOjEsImNvbXAiOiJkb3duIiwicHJpY2UiOjEsImJvciI6MSwiY29sIjoxLCJiYnRuIjoxLCJwcm9kIjowLCJhbXAiOmZhbHNlfQ==" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><div style="float:right;width:41%;height:27px;background-color:#bf0000;color:#fff!important;font-size:12px;font-weight:500;line-height:27px;margin-left:1px;padding: 0 12px;border-radius:16px;cursor:pointer;text-align:center;"> 楽天で購入 </div></a></div></td></tr></table></div><br><p style="color:#000000;font-size:12px;line-height:1.4em;margin:5px;word-wrap:break-word"></p></td></tr></table>
```

````

また、IPv4では、ペイロード(上位レイヤーに渡すデータ実体)にはセキュリティ的な取り組みは行われて折らず、そのまま内容が確認できてしまいます。
そのため、通信内容や改ざんが容易に行えてしまう状況でした。
この部分は、少なくともWeb周辺は『常時SSL化』という状況が進んで改善されたものの、それは上位層の取り組みによるものです。

そのため、IPv4では後にIPsecというセキュリティ機能が追加されました。
IPsecは、IPのレベルでの暗号化を実現しており、ペイロード部分が上位層に関係なく暗号化されることから、通信時の漏洩時にも内容がわからない(正しくは『わかりにくくなる』)という効果があります。
ですが、この部分はオプション(任意)という扱いでした。
こういうこともあり、必ずしも全ての通信で利用されるわけではありませんでした[^ipsec-use]。

[^ipsec-use]: 設定の複雑さなどもあってか、拠点間VPNなどの限定された用途意外で使われることはほとんどありませんでした。

そのため、IPv6では、プロトコル設計においてIPsecを必須とすることとしようとしました(RFC2460においては必須(MUST)扱い)。ですがその後改訂(RFC4294等)において推奨(SHOULD)のレベルに変更されました。
そして、現在での標準(RFC8200)ではIPsecサポートは必須ではなくなりました[^ipv6-ipsec]。

しかし、2025年現在では、TLS 1.3の普及やHTTP/3の採用により、アプリケーション層でのセキュリティが主流となっており、ネットワーク層でのIPsecよりも実用的なセキュリティソリューションが確立されています。また、Zero Trust Network Architecture(ZTNA)やSoftware-Defined Perimeter(SDP)といった新しいセキュリティモデルの採用により、ネットワーク境界でのセキュリティから、個別の通信セッションレベルでのセキュリティへとパラダイムが移行しています。

[^ipv6-ipsec]: IPsecの実装と運用の複雑さが、実際の採用を妨げる要因となりました。現在では、よりシンプルで効率的なTLSベースのセキュリティが主流となっており、IPsecは主にサイト間VPNやネットワークレベルの特定用途で使用されています。

これ以外にも、セキュリティに関わる取り組みが追加されています。

- ネットワーク設定の際の制御メッセージを悪用した攻撃が考えられて、フィルタリングや監視の機能がサポートされました(ルーターにおけるRAガードやDHCPv6対策など)
- ランダムアドレスを生成することでプライバシーを高める機能がサポートされました(RFC4941)
- 近隣探索(Neighbor Discovery Protocol; NDP、ARPのIPv6版みたいなもの)において、セキュリティを高めるための機能が追加されました(RFC3971)
- その他

### ネットワークの複雑化

IPv4では、ネットワークの構成が比較的単純でした。

- 各ネットワークは、クラスA/B/Cのいずれかに分類されていました。
- 各ネットワークは、サブネットマスクを用いて分割されていました。
- 各ネットワークは、ルーターを用いて接続されていました。
- 各ネットワークは、NAT(Network Address Translation)を用いて接続されていました。

このような構成は、ネットワークの規模が小さい場合には問題ありませんでした。
しかし、ネットワークの規模が大きくなると、以下のような問題が発生しました。

- ネットワークの構成が複雑化し、管理が困難になった。
- ネットワークの構成が複雑化し、トラブルシューティングが困難になった。
- ネットワークの構成が複雑化し、セキュリティの脆弱性が増大した。
- ネットワークの構成が複雑化し、パフォーマンスが低下した。

このような問題に対応するため、IPv6では以下のような取り組みが行われました。

- ネットワークの構成をシンプルにするため、アドレス空間を大きくしました。
- ネットワークの構成をシンプルにするため、アドレスの割り当てをブロック単位で行うようにしました。
- ネットワークの構成をシンプルにするため、NATを廃止しました。
    - ただし完全に無くなったわけでは無く、
      IPv6のNAT64などのように、IPv4との接続のためにNATを利用することはあります。
- ネットワークのアドレス割り当て(構成)は原則として自動化を基本とすることとしました。
    - そのため、DHCPv6やRA(Router Advertisement)などの仕組みがサポートされました。

また、ルーターの負荷を下げる方法のひとつとして、パスMTU探索の必須化が行われ、ルーターでのパケットの再構成・再分割を行わないようにしました。

```{note}
IPv6におけるアドレス自動化は前述の通り、DHCPv6やRAによる自動構成がが行われるのですが、クライアント側実装による差違が発生していて少々問題となっています。

- Windows: DHCPv6を優先して利用する
- macOS: RAを優先して利用する
- Linux: RAを優先して利用する
- Android: RAを優先して利用する(SLAACのため、DHCPv6は利用しない)
- iOS/iPadOS: RAを優先して利用する

実際のところ、あまりDHCPv6を使っている状況は見かけることがありません。
```

## IPv6の基本構造

IPv6は、IPv4と同様にIPプロトコルの一種であり、ネットワーク層で動作します。
ですが、構造が複雑になってしまったヘッダ部分などを見直しています。
そのためヘッダ構造がまず違っているので、ここではIPv4と軽く比べてみましょう。

### IPv4ヘッダ構造

```{info}
本授業ではここまで細かいところまで知る必要はありません。
あくまで比較用というレベルですので、記述は簡素にしています。
詳しく知りたい方は自分で調べてください。
```

IPv4のヘッダは、以下のような構造になっています[^ipv4-header]。

```{figure} images/ipv4-header.png

IPv4のヘッダ構造(Wikipediaより引用)
```

[^ipv4-header]: [IPv4 - Wikipedia](https://ja.wikipedia.org/wiki/IPv4#%E3%83%91%E3%82%B1%E3%83%83%E3%83%88)より抜粋。

- ヘッダ長は4の倍数(4オクテットがいくつあるかということ)であり、通常は5(=20オクテット)です
- フラグ領域に、経路MTU探索の際に登場した`DF`(Don't Fragment)フラグが存在します
- 拡張領域は、オプションとして存在し、通常は利用されません
  - パケットのタイムスタンプやルーター情報などを含めることがあります

オプション部分が少々厄介で、この部分が原因でヘッダの長さ(通常「5」)が変わることがあります。
そのため、ルーターはペイロード(データ実体)の開始部分を各パケットごとにスキャンする必要があります。

### IPv6ヘッダ構造

IPv4と比較すると、サイズこそ長くなっている(アドレス自体がが無いため)ですが、ヘッダサイズが原則固定となるように設定されています[^ipv6-header]。

```{figure} images/ipv6-header.png

IPv6のヘッダ構造(Wikipediaより引用)
```

[^ipv6-header]: [IPv6 - Wikipedia](https://ja.wikipedia.org/wiki/IPv6#%E3%83%91%E3%82%B1%E3%83%83%E3%83%88)より抜粋。

- Traffic class:
    - IPv4のType of Service(TOS)に相当する部分で、QoS(サービス品質)を示すためのフィールドです。
    - ただし現状ではほとんど使われないため、0で埋められることが多いです。
- Flow label:
    - 特定のフロー(通信の流れ)を識別するためのフィールドです。
    - QoSやトラフィックエンジニアリングに利用されます。
    - ただし現状では使用されておらず、実質0で埋められています。
- Payload length:
    - ペイロードの長さを示すフィールドで、ヘッダの後に続くデータのサイズをバイト単位で示します。
- Next header:
    - IPv4のProtocolフィールドに相当する部分で、次に処理されるプロトコルを示します。
    - 例えば、TCPやUDPなどの上位プロトコルを示します。
- Hop limit:
    - IPv4のTime to Live(TTL)に相当する部分で、パケットがネットワークを通過する際のホップ数を制限します。
    - ルーターを通過するたびに1ずつ減少し、0になるとパケットは破棄されます。
- Source address:
    - 送信元のIPv6アドレスを示すフィールドです。
- Destination address:
    - 宛先のIPv6アドレスを示すフィールドです。

IPv6では、**ヘッダのサイズが固定されている**ため、ルーターはペイロードの開始位置を簡単に特定できます[^size-fix]。
また、ペイロード長もヘッダから固定的に抜き出せるため、処理が効率化されています。

````{note}
Traffic ClassやFlow labelは実際ほとんど使われておりません。
試しに`scapy`を使って作ってみると、初期値はゼロで埋め尽くされています。

```python
>>> IPv6(dst="::1").show()
###[ IPv6 ]###
  version   = 6
  tc        = 0 <- Traffic Class
  fl        = 0 <- Flow Label
  plen      = None
  nh        = No Next Header
  hlim      = 64
  src       = ::1
  dst       = ::1
```

````

[^size-fix]: C言語的に考えれば、そのメモリ状態をIPv6を示す構造体にキャストする程度の処理で簡単に個別のフィールドが抜き出せるいうことです。



## IPv6アドレスの表記

IPv6のアドレスは128ビットと非常に長いため、表記が難しくなることが多いです。
たとえばIPv6アドレスをフル(省略無し)で記述すると、以下のような形になります。

```
2001:0db8:0000:0000:0000:0000:0000:0001
```

このように、IPv6アドレスは8つの16ビット(4桁の16進数)ブロックで構成され、コロンで区切られます。  
しかし、この表記は非常に長く、扱いにくいです。そのため、省略をする方法が提示されており、通常この形で短く表記していきます。

- 16進数表記で0から始まるブロック(0x0123など)は、先頭の0を省略できます
    - 0x0123 -> 0x123
    - 0x0000 -> 0x0
- 連続する0のブロックは、`::`で省略できます、ただし1カ所しかできません
    - 2001:0db8:0000:0000:0000:0000:0000:0001 -> 2001:db8::1
    - 2001:0db8:0000:0000:0000:0000:0000:0000 -> 2001:db8::
    - 連続する0のブロックが複数ある場合は、最初の部分だけを省略できます
        - 2001:0db8:0000:0000:1234:0000:0000:0001 -> 2001:db8::1234:0:0:1
        - 複数の場所で省略を認めた場合、どちらがいくつの連続化が確定できないため

このような表記から、前述のアドレスは`2001:db8::1`のように短縮されます。

また、ネットマスクも基本的にビット長で書き、`/64`のように表記します。
このように、IPv6アドレスは非常に長いですが、省略表記を使うことで扱いやすくなっています。

```{note}
IPv6アドレスの表記は、RFC 5952で定義されています。
詳しくは、[RFC 5952 - A Recommendation for IPv6 Address Text Representation](https://datatracker.ietf.org/doc/html/rfc5952)を参照してください。
```

## IPv6アドレスの種類

IPv6のアドレス空間は非常に広いため、IPv4と違って個別の機器に割り当てても不足するようなことは考えにくいです。
ですが、通信の効率化などの目的で、いくつかの用途別のアドレス空間を定義しています。

- **グローバルユニキャストアドレス**
    - インターネット上で一意に識別されるアドレスです。
    - `2000::/3`で始まるアドレス空間です。
- **リンクローカルユニキャストアドレス**
    - 同一データリンク内でのみ有効なアドレスです。
    - 先頭ビットが`1111 1110 10`で始まるアドレスです(`fe80::/10`)。
- ユニークローカルアドレス
    - ユニークローカルアドレスは、プライベートネットワーク内で使用されるアドレスです。
    - NATやVPNの内側などで利用します
    - 先頭ビットが`1111 1100`で始まるアドレスです。
- その他
    - ループバックアドレスは、`::1`で表され、ローカルホストを指します。
    - マルチキャストアドレスは `ff00::/8` で始まるアドレスで、特定のグループにデータを送信するために使用されます。
    - 文書記述用の予約アドレス：`2001:db8::/32`は、文書やサンプルコード用に予約されたアドレス空間です（RFC3849）。実際のネットワークでは使用されず、教材や技術文書での例示にのみ使用されます。

## IPv6パケットの分割処理

IPv6では、パケットの分割処理は事前に『経路MTU探索を行う』ことで分割させないという方針が採られています。
しかし、組み込み機器のようにリソース制限が厳しく、経路MTU探索の処理が難しい場合を考慮して、IPv6の最小MTUサイズである1280オクテットを前提として、探索を省略し、必要であれば送信元で1280オクテットに分割して送信することが認められています[^mtu1280]。

[^mtu1280]: この場合、万一より小さなMTUを求めるデータリンクがあった場合は分割が発生することがあります。現実的な問題としてこれより小さいMTUのデータリンクはそうそうお目にかかれません。

