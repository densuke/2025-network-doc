# ルーティングとICMP

ルータを使って中継しながら、パケットを目的地(IP)へ届けることがIP層の重要な役割です。
とはいえIP層での中継の最中に、問題が生じることが多くあります。

このような場合に、送信元などに通知をすることで対応を求めることがあります。
その際に使われるのが、ICMP(Internet Control Message Protocol)というプロトコルです。
ICMPはIP層のプロトコルで、IPパケットの中にICMPメッセージを格納して送信します。

どういうときにICMPが使われることになるのかを、コマンドを組み合わせながら少し確認していきましょう。

## ICMPパケットの基本構造

ICMPパケットは、IPパケットのペイロードに存在します。

```
  +------------+-----------+-------------+-----------
  | MACヘッダ   | IPヘッダ   | ICMPヘッダ   | データ...
  +------------+-----------+-------------+-----------
```

そして、ICMPヘッダとデータ部分に注目すると、以下のようになっています。

- 1オクテットの『タイプ』
- 1オクテットの『コード』
- 2オクテットの『チェックサム』
- メッセージヘッダの残り (4オクテット):
  - Echo/Echo Reply (タイプ8/0)の場合:
    - 識別子 (2オクテット)
    - シーケンス番号 (2オクテット)
  - その他のメッセージ (例: 到達不能メッセージ タイプ3)の場合:
    - メッセージタイプに応じたフィールド、または未使用
- データ部:
  - メッセージタイプに応じたデータ。
    - 例: Echoメッセージの場合は任意のデータ、エラーメッセージの場合は元のIPヘッダとデータの一部
  - この部分にどのようなデータが入るべきかは
    [RFC792(日本語訳)](http://srgia.com/docs/rfc792j.html)に記載されています。

## TTLについて

ICMPのメッセージには、TTLに関するものがいくつかあります。

- TTL: Time To Live
  - 要は『そのパケットにおける賞味期限』というところ
  - 基本ルールとして、ルータを通過する際にかかった時間(秒数)分だけ減らすというものですが…
    - 1秒未満でも1減らす(実質通過するごとに1減る)
    - 0になったら破棄する
- TTLが0になったらそれ以上ルーターを通過できない
  - ルータはTTLが0になったパケットを破棄し、ICMPメッセージを送信する
    - ICMPのTypeは`11`(TTL expired)
    - ICMPのCodeは`0`

ICMPでは、タイプ(Type)とコード(Code)という2つの値で問題の種別を伝えています。
- Type: ICMPメッセージの種類
- Code: Typeの中での詳細な種類
  - Typeが同じでも、Codeが違うと別の意味になることがある

前述の"TTL expired"は、Typeが`11`でCodeが`0`のものです。

## pingとtraceroute、ICMPエコー要求

`ping` コマンドは、ICMPのEcho Requestを送信し、相手からの応答を待つコマンドです。
受け取った側は、ICMP Echo Replyを返します。

- ICMP Echo Request Message
  - Type: `8`
  - Code: `0`
  - データ部分には、識別子(区別用でランダムな数値など)とシーケンス番号が付与されています
  - それ以降はけっこう適当なデータが含まれることが多い模様(タイムスタンプやデータの繰り返し)
- ICMP Echo Reply Message
  - Type: `0`
  - Code: `0`
  - "Echo Request"の応答とするものであり、データはそのまま返される

送り出した時間と戻ってきた時間を利用して、実際に相手に対してどれぐらい時間がかかったのかを計測することができます。
今回の仮想マシン(VM)には、`ping`コマンドはインストールされています。

```bash
# IPアドレス1.1.1.1に対してpingを送信
ping -c 4 1.1.1.1
```

```{note}
`-c 4`は、4回だけpingを送信するオプションです。
なお、 `-c4` と繋げて書いても(この文脈では)問題ありません。
```

実行すると、以下のように応答があるかもしれません(実は『無い』こともあります)。

```bash
$ ping -c 4 1.1.1.1
PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.
64 bytes from 1.1.1.1: icmp_seq=1 ttl=255 time=9.99 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=255 time=7.62 ms
64 bytes from 1.1.1.1: icmp_seq=3 ttl=255 time=24.6 ms
64 bytes from 1.1.1.1: icmp_seq=4 ttl=255 time=8.06 ms

--- 1.1.1.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 7.624/12.568/24.604/7.005 ms
```

- 特に指定が無ければデータ部分が64バイトのパケットを生成しています
- `icmp_seq`は、ICMPのシーケンス番号です
- `ttl`は、TTLの値です
- `time`は、往復時間(RTT; Round Trip Time)です

その上で、指定回数(今回は4回)の送出を行い、集計を返しています。
- `packets transmitted`は、送信したパケット数です
- `received`は、受信したパケット数です
- `packet loss`は、失われたパケット数です(今回は0のため0%、ロス無し)
- `time`は、全体の時間です
- `rtt`は、往復時間の統計です
  - `min`は、最小値
  - `avg`は、平均値
  - `max`は、最大値
  - `mdev`は、標準偏差(偏差値… うっ、頭が…)

ネットワークにおけるRTTは、距離(物理ではない)や混雑の度合いなどで案外ばらつきがあります。
安定的な通信のためには、行き先が近い方がよいのですが、回線品質やルーターの混雑度合いなども影響を受けます。

### TTLとping

`ping`コマンドでは、TTLが出力されていましたが、この値を調整することができます。

```bash
ping -t 128 -c 4 1.1.1.1
```

```{note}
`-t 128`は、TTLの値を128に設定するオプションです。

実はこのTTL設定オプション、各OSで異なっているため注意が必要です。
- Linuxは `-t TTL`
- Windowsは `-i TTL`
- macOSは `-m TTL`
```

実行するとこのような感じです。
```bash
$ ping -t128 -c4 1.1.1.1
PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.
64 bytes from 1.1.1.1: icmp_seq=1 ttl=255 time=8.43 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=255 time=10.7 ms
64 bytes from 1.1.1.1: icmp_seq=3 ttl=255 time=18.7 ms
64 bytes from 1.1.1.1: icmp_seq=4 ttl=255 time=8.50 ms

--- 1.1.1.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3007ms
rtt min/avg/max/mdev = 8.430/11.600/18.748/4.228 ms
```

```{note}
出力のTTL値が255なのは、戻りパケットのTTL値(受け取ったIPパケットから)です。
実はVirtualBoxを使っている場合、NATモードと呼ばれるネットワーク転送(中継)を行っており、
中継の際にパケットを書き換えてしまい255にされるようです。

この辺りが気になる方は、ホストOS側のpingを使って試すといいでしょう。
```

### TTLを小さくしてみる

もし、このTTLを(1以上の)とんでもなく小さくしたらどうなるでしょうか。
注記の通りで、VirtualBoxを経由する場合はあまり効果がないのですが、ホスト側で試した場合、少々困った挙動が確認できる場合があります。

たとえば著者(佐藤)の自宅ですが、macOSにて確認すると(よって-mを使用)、以下のような現象が起きます。

```zsh
% ping -m 5 -c 4 1.1.1.1 # TTL=5
PING 1.1.1.1 (1.1.1.1): 56 data bytes
64 bytes from 1.1.1.1: icmp_seq=0 ttl=58 time=9.946 ms
64 bytes from 1.1.1.1: icmp_seq=1 ttl=58 time=11.490 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=58 time=8.109 ms
64 bytes from 1.1.1.1: icmp_seq=3 ttl=58 time=7.557 ms

--- 1.1.1.1 ping statistics ---
4 packets transmitted, 4 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 7.557/9.276/11.490/1.555 ms

% ping -m 4 -c 4 1.1.1.1 # TTL=4
PING 1.1.1.1 (1.1.1.1): 56 data bytes
36 bytes from 162.158.4.43: Time to live exceeded
Vr HL TOS  Len   ID Flg  off TTL Pro  cks      Src      Dst
 4  5  00 5400 bcdb   0 0000  01  01 2ee7 192.168.11.61  1.1.1.1

Request timeout for icmp_seq 0
36 bytes from 162.158.4.43: Time to live exceeded
Vr HL TOS  Len   ID Flg  off TTL Pro  cks      Src      Dst
 4  5  00 5400 02b7   0 0000  01  01 e90b 192.168.11.61  1.1.1.1

Request timeout for icmp_seq 1
(以下略)
```

おかしなものとなりました。
これは、出力にあるように"Time to live exceeded"というメッセージが出力されていることから、TTLが0になってしまったために、ルータが破棄してしまったことを示しています。

ルーターは仕事として、通過するパケットの値を削っていきます。
本来は通過にかかる時間(秒数)分削るのですが、1秒未満の場合は1削るため、実質通過するたびに1削られます。
ということで、TTLを4にした場合、経路中のルーターの処理で0となってしまい、その時点でエラーを起こしてしまってます。

- ルーターはTTLが0になったパケットを破棄し、ICMPメッセージを送信する
    - ICMPのTypeは`11`(TTL expired)
    - ICMPのCodeは`0`

IPパケットヘッダに含まれている送信元(= ルーターのIP)から、どこのルーターで止まったかがわかるという仕組みです。

### tracerouteコマンド

この『TTLを意図的に小さくする』行為を行うと、経路中のルーターがどこでパケットを破棄したのかを調査することができます。
この仕組みを使ったのが`traceroute`コマンドです。
Windows環境では`tracert`コマンドに相当します。

`traceroute`コマンドは、TTLを1から始めて、1ずつ増やしながらパケットを送信します。
この仕組みにより、**パケットがどのような経路をたどったのかがわかる**という構造になっています。

```{note}
この操作は仮想マシン上で実行しても、およそ正しい効果が期待できません。
それ以上に、そもそもtracerouteが機能しないこともあります(後述)。

```

```bash
traceroute 1.1.1.1
```

```zsh
# macOS環境での実行例
% traceroute 1.1.1.1
traceroute to 1.1.1.1 (1.1.1.1), 64 hops max, 40 byte packets
 1  192.168.11.1 (192.168.11.1)  3.285 ms  3.263 ms  3.099 ms
 2  dj2-cr000.transix.jp (14.1.5.157)  10.588 ms  8.609 ms  9.323 ms
 3  * 210.173.184.71 (210.173.184.71)  22.329 ms  11.291 ms
 4  162.158.4.47 (162.158.4.47)  11.529 ms
    162.158.4.29 (162.158.4.29)  12.274 ms
    162.158.4.43 (162.158.4.43)  32.048 ms
 5  one.one.one.one (1.1.1.1)  10.176 ms  9.417 ms  8.840 ms
```

1.1.1.1(CloudflareのDNSサーバ、えらいホスト名が付いてますね)に対して、tracerouteを実行した結果となります。

最初はTTLを1にした場合です。最初のルーター(192.168.11.1、自宅のアクセスポイント)が通過の際に1減らして0になったことでエラーとなりました。
次に2に設定することでルーターを飛び越えられましたが、14.1.5.157にて止められています。
以降、1ずつ増やすことで通過できるところが増えていき、最終的に戻ってきたパケットが1.1.1.1になるまで行っていきます。

```{note}
この場合に、ルーターを跨ぐ回数に着目し『ホップ数』(飛び越える数)と表現することもあります。
```

多くのOSの`traceroute`(`tracert`)コマンドは、このTTL上限を30に設定しています。

## ICMP到達不能メッセージ

ICMPのメッセージの中には『到達不能』という状態を示すものがあります。
到達不能メッセージはタイプ3で示され、以下のコードが存在します。

- Code 0: ネットワーク到達不能
  - 宛先ネットワークに到達できない
- Code 1: ホスト到達不能
  - 宛先ホストに到達できない
- Code 2: プロトコル到達不能
  - 宛先ホストのプロトコルに到達できない
- Code 3: ポート到達不能
  - 宛先ホストのポートに到達できない
- Code 4: フラグメント必要
  - フラグメントが必要だが、フラグメントビットがセットされていない
  - IPパケットのフラグメントフラグ(DF)がセットされていると、パケットの分割が必要でも禁止となるためそれ以上の通信ができなくなってしまう

他にもいくつか存在しますが、上記のような理由を含めて『通信が行えない』事を送信元に返します。

このため、データ部分にはそれがわかるように元のパケットヘッダ情報を含めるようにしています。

## ICMP時間超過メッセージ

TTLを消費しきったときに発生するものです。
原因としては大きく2つが考えられます。
タイプは11のエラーとして報告され、コードは2つ存在します。

- コード 0
  - 前述した`ping`や`traceroute`のように、TTLを操作するとき
  - ルーティング上のミスでループをしてしまっているようなパケット
- コード 1
  - フラグメント(パケット分割処理)に時間がかかりすぎた場合

といったもので発生することになります。データ部分には元のIPパケットのヘッダ情報が含まれます。

## ICMPリダイレクトメッセージ

ICMPリダイレクトメッセージは、ルーティングの際に『よりよいルーティング先がある』時に送信されます。
タイプは5で、データ部分には新しいルーターのアドレス情報や元のIPパケットのヘッダ情報が含まれます。

この時、本来の送信したいパケット自体は転送されているため、ある意味提案とも言えるメッセージの扱いです。
正常に処理されるのであれば、受け取ったルーティング情報を送信元のルーティングテーブルに追加するなどの対策の後、次回以降はそちらを使うことになるでしょう。

## セキュリティ的問題

ICMPのパケットは、相手にホストの存在を知られる可能性もあるということから、ルーターなどがフィルタリングによりパケットを拒否するようなことも多々起きています。

そのため、環境によっては、pingやtraceroute(tracert)が機能しないこともあります。

### 現代的なICMPセキュリティ考慮事項

2025年現在、ICMPに関する主なセキュリティ課題として以下が挙げられます:

- **情報漏洩の防止**: ICMPエラーメッセージには元のIPパケットの一部が含まれるため、ネットワーク構成や内部アドレスが外部に漏洩する可能性があります。多くの組織では、境界ファイアウォールでICMPメッセージをフィルタリングしています。

- **DDoS攻撃への悪用**: ICMPフラッド攻撃やSmurf攻撃(ブロードキャストpingを使った増幅攻撃)により、ネットワークリソースが枯渇させられる可能性があります。

- **偽装攻撃**: ICMPリダイレクトメッセージを偽装してルーティングテーブルを改竄し、中間者攻撃を行う手法が知られています。

- **Network Discovery**: 攻撃者がpingスイープやtracerouteを使ってネットワークトポロジーを調査し、攻撃対象を特定することがあります。

これらの理由から、現代の企業ネットワークやクラウド環境では、ICMPトラフィックの制限や監視が標準的なセキュリティ対策となっています。

### ブロードキャストへのping

実は、ブロードキャストアドレスに対するpingが可能です。
たとえば 10.16.0.0/16であれば、

```bash
ping 10.16.255.255
```

で可能です。ただしOSの種類によってはブロードキャストを明示するフラグ(`-b`など)が必要な場合もあります。
この場合、正常に機能すると、そのネットワークに存在するホストが応答することがあります。

この挙動は、ネットワークの管理者が動いているホストを確認するために使うなど、古くは使われていましたが、
現在ではセキュリティへの懸念(存在が知られることによる攻撃を招くことがある)から、あまり使われていないようです。
OS側でもブロックしていることも多いため、あまり期待しない方がいいでしょう。

なおこのブロードキャストは、大きく2つの形式があります。

- ローカルブロードキャスト
  - 自分がいるネットワークに対するブロードキャスト、まだ許せます
- グローバルブロードキャスト
  - ルーターを跨いだ先にあるどこかのネットワークに対するブロードキャスト
  - 攻撃と思われるもののため、ルーターなどは拒否します

