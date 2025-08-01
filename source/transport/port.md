# ポートの概念

実際の通信において、ポートという概念が登場します。
ローカルでのサーバー開発において、地味にトラブルの元にもなるため、ポートの概念の理解は重要です。

## ポートとは?

イーサネット(Wi-Fi)では、両者(自分と接続先)のことをMACアドレスで比較していました。
IPでは、両者のことをIPアドレスで比較していました。
このつながりで、トランスポート層ではポート番号が登場します。

良くあるたとえでは『道路はIP』『車はポート』というものがあります。
道路の存在により、2点間の通信経路が確立されています。その中を走る車が情報であり、車を見分けるために使っているのがポートという風に考えてみるといいでしょう。

もうすこし具体的なところでは、以下のようになります。

- IPではあくまで信号という形でデータが流れています
- トランスポートでは、信号の中に『どのアプリケーションが受け取るべきか』という情報が含まれています。

このため、トランスポートのレベルでは、ポート番号を使ってアプリケーションを識別し、適切なアプリケーションにデータを届ける役割を果たしています。

## ポート番号の範囲
ポート番号は、0から65535までの範囲で指定されます。ポート番号には以下のような分類があります。
- **ウェルノウンポート(0-1023)**: これらのポート番号は、特定のサービスやプロトコルに予約されています。例えば、HTTPはポート80、HTTPSはポート443、FTPはポート21などです。
- **登録済みポート(1024-49151)**: これらのポート番号は、特定のアプリケーションやサービスに登録されており、一般的に使用されます。例えば、MySQLはポート3306、PostgreSQLはポート5432などです。
- **動的ポート(49152-65535)**: これらのポート番号は、クライアントアプリケーションが一時的に使用するために割り当てられます。通常、クライアントがサーバーに接続する際に、動的に選択されます。別名として『エフェメラルポート』とも呼ばれます[^ephemeral][^rfc6056]。

```{note}
なお、ウェルノウンポートは、現代では『**システムポート**』と呼ばれているそうですが、佐藤は未だかつてその呼び方を見たことがありません。
```

[^ephemeral]: エフェメラルポートは、英語で「一時的な」「揮発性のある」という意味を持つ言葉です。ポート番号が一時的に使用されることから、この名前が付けられています。

## ポートは発信側だって使うことになる

ポートについて「ああ、Webサーバーだと80番だよね」という感じで話を聞くことがありますが、80番ポートを使うということはトランスポートでの通信となるわけで、同レベルでの通信であれば自分の側にもポート番号が必要です。
では、その『自分の使うポート番号』はどうやって決まるのでしょうか。

このことに関しては、雑に2つに分類することができます。

- 自分で決める
- おまかせ(システムに決めてもらう)

自分で決める場合、ポート番号を明示的に「この番号から発信する」と宣言することになります。
ポート番号自体は前述の通り、0〜65535の範囲で指定できますが、『空いていれば使える』ため、他のアプリケーションが使用中のポートは使用できません。
**ポート番号は早い者勝ち**というルールとなっているのです。
この問題は、サーバーの開発を行うときに地味に効いてくる問題です。

おまかせの場合、システムが自動的に空いているポート番号を選択してくれます。
システム(OS)は通常、自分のシステム内で『現在使用中』のポート情報はビットマップ的に管理しています。
そのため、空いているポート番号を効率的に見つけることができます。
この場合、ポート番号はシステムが自動的に選択するため、開発者は特に意識する必要はありません。

この時に「どのあたりのポート番号を拾いやすいか」については、OSの実装によって少し差が出ているようです。

- Windowsの場合、49152〜65535の範囲から選択されることが多い(ポート数は16384)。
- Linuxの場合、32768〜60999の範囲から選択されることが多い(ポート数は28232、他より少し多い)
- macOSの場合、49152〜65535の範囲から選択されることが多い(ポート数は16384)

````{note}
各OSの範囲は以下の方法で確認できます。


### Windowsの場合

```pwsh
PS> netsh int ipv4 show dynamicport tcp
プロトコル tcp の動的ポートの範囲
---------------------------------
開始ポート      : 49152
ポート数        : 16384
```

### Linuxの場合

```bash
$ cat /proc/sys/net/ipv4/ip_local_port_range
32768   60999
```

### macOSの場合

```zsh
% sysctl net.inet.ip.portrange.first
net.inet.ip.portrange.first: 49152
% sysctl net.inet.ip.portrange.last
net.inet.ip.portrange.last: 65535
```

こうして確認するとLinuxだけずれている感じになりますが、過去からの経緯というものがあるのでしょう。
````

[^rfc6056]: RFC 6056は、エフェメラルポートの範囲に関する標準化文書であり、ポート番号の割り当てに関するガイドラインを提供しています。RFC 6056は、特に動的ポートの使用に関する推奨事項を含んでいます。この中では1024〜65535がエフェメラルポートの範囲として定義されています。定義はされていますが実際はかなり狭いです。これは現実的な使用状況を考慮した結果などが反映されていると考えてください。
