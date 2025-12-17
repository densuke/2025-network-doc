# PHP環境の導入

PHPはサーバーサイドのスクリプト環境としては非常にメジャーであり、デファクトスタンダードの地位を確立しています。
多くのサービスでも使われているため、PHPの導入は重要となります。
ここではPHPの導入に関する注意点と、Ansibleによる導入方法を進めていきます。この中でPlaybookの書き方についての知識も追加していきます。

## PHPの『呼び出しかた』について

PHPは単体で動作せず、基本的にWebサーバーのバックエンドとして動作する構成となっています。
そのため、WebブラウザはPHPのコードを直接呼び出すようなことは行わず、常にWebサーバーを介した呼び出しとなっています。

```{mermaid}
sequenceDiagram
    actor Browser as ブラウザ
    participant WebServer as Webサーバー
    participant PHP as PHP
    
    Browser->>WebServer: HTTPリクエスト
    WebServer->>PHP: PHP実行依頼
    PHP->>PHP: スクリプト処理
    PHP->>WebServer: 処理結果
    WebServer->>Browser: HTMLレスポンス
```

## PHPとApacheの連携方法について

PHPとApacheの連携については、大きく2つの方法があります。
ただその前に、少しだけApacheの内部構造についても知っておくとよいでしょう。

### Apacheのプロセス管理モデル

Apacheでは、多くのOSに対応できるようにするために、いくつかの部分において抽象化の層を持っています。
その中でプロセスを扱う部分で、MPM(Multi-Processing Module)と呼ばれる仕組みがあります。
代表的なMPMとして、以下の3つを挙げることができます。

- prefork: プロセスベースのモデルで、各リクエストに対してプロセスを割り当てます。PHPのようなスレッド非対応のモジュールと組み合わせることが多いです。
- worker: スレッドベースのモデルで、各リクエストに対してスレッドを割り当てます。高いパフォーマンスを提供しますが、スレッド非対応のモジュールとは組み合わせられません。
- event: workerの拡張で、接続の管理を効率化するためのモデルです。高いパフォーマンスとスケーラビリティを提供します。

ある意味安全性が高いのはpreforkモデルです。プロセスは独立しているため、1つのプロセスがクラッシュしても他のプロセスに影響を与えにくいです。
一方でリソースの消費が大きくなる傾向があります。この問題は後に出るmod_phpの登場でさらに顕著になります。
一方で、workerやeventモデルはスレッド(thread)というプロセス内で小分けにされたような単位で動作するため、リソースの消費が少なくなります。
その代わりにプロセスの中で存在するスレッドはメモリを全て共有する状態にあるため、作りが悪い(行儀が悪い)と他のスレッドのデータを破壊するようなこともあるため危険です。

これらはApacheの設定で切り替えることができます。

### PHPとの連携方法

PHPとのApacheの連携については、以下の2つの方法が存在します。

- Apacheの拡張モジュールとして実装する(mod_php): Apache自体にPHP言語のランタイムを追加するというかなり強引な方法です。Apacheが起動する過程(初期化処理)でPHPのランタイムが初期化されて準備完了となっています。そのためすぐにPHPスクリプトが実行できるようになります。また、PHPスクリプトのコンパイルキャッシュなども保持されているためパフォーマンスも良好となります。ただし、Apacheのプロセスが全てPHPのランタイムを抱え込む形になるため、メモリ消費が非常に大きくなります。また、Apacheのプロセスモデルとしてpreforkを使うことが前提となるため、workerやeventモデルを使うことができません。
- 外部プロセスとして実装する(FastCGI + PHP-FPM): Apacheからは外部プロセスとしてPHPのランタイムを呼び出す形となります。具体的にはFastCGIというプロトコルを使ってApacheとPHP-FPM(PHP FastCGI Process Manager)というPHPのランタイムを管理するプロセスと通信します。この方法ではApacheのプロセスはPHPのランタイムを抱え込む必要が無いため、workerやeventモデルを使うことができます。また、PHPのランタイムも必要に応じて起動・停止できるため、メモリ消費を抑えることができます。一方で、ApacheとPHP-FPM間の通信コストが発生するため、mod_phpに比べてパフォーマンスが劣る場合があります。

パフォーマンス上の理由とすると、mod_phpのほうが有利かもしれませんが、その一方でリソースの浪費やPHPプロセスをその気になればホスト単位で分離することも可能(Webサーバーの動いているサーバーとPHPランタイムの動くサーバーをホスト的に分離する)などの柔軟性から、現代ではFastCGI + PHP-FPMの組み合わせが主流となっています。

なお、PHPとのネットワーク的な接続に関しては大きく2つがあります。

- IPアドレス(ホスト名)ベース
- UNIXドメインソケットベース(ローカル上での接続であればこちらのほうが性能が良い)

ということで、今回は後者のPHP-FPMを使った方式を採用します。

このことから、Apache側の歩み寄りも必要となっていきます。

- PHP側: PHP-FPMをインストールしてサービスの起動をさせる
- Apache側: mod_proxy_fcgiモジュールを有効化して、FastCGIでPHP-FPMにリクエストを転送する設定を行う
- 接続方法はUNIXドメインソケットを使うように設定する

## PHPロールを作成する

では、ここまでの計画を基に、PHPのロールを作製してみましょう。
基本的な手順はhttpdロールと同じです。
なお今回使うPHPは8.2を使います。これはUbuntu 24.04 LTSで標準サポートとなっているバージョンのためです。

```{note}
最新のPHPを使いたい場合は、PPA(Personal Package Archive)を使って導入する方法がUbuntu的には一般的と思われます。
`ondrej/php`を追加し、そこから各バージョンをインストールするのがいいでしょう。

参考: [https://launchpad.net/~ondrej/+archive/ubuntu/php](https://launchpad.net/~ondrej/+archive/ubuntu/php)
```

### 基本構造(ディレクトリ)の作成

まず、`roles`ディレクトリ内に必要なディレクトリを作製します。

```{code-block}
:language: bash

$ mkdir -pv roles/php/tasks
$ mkdir -pv roles/php/handlers
$ mkdir -pv roles/php/meta  # NEW!
```

{file}`meta`ディレクトリは今回初出となります。phpロールに関するメタデータ(依存関係など)を記述するためのディレクトリです。

### タスクの作成

タスクの作成に関しては、Apache2(httpd)ロールと基本的に同じです。

- パッケージの導入
- サービスの起動と有効化

```{literalinclude} src/php-main.yml
:language: yaml
:caption: roles/php/tasks/main.yml
:linenos:
:lines: 1-9
```

1〜4行目がphp(php8.2-fpm)パッケージのインストール、5〜9行目がサービスの有効化と起動ということはもうおわかりでしょう。

### phpロールを組み込む

あとは `site.yml`にphpロールを追加するだけです。

```{literalinclude} src/site-roles.yml
:language: yaml
:caption: site.yml(ロール部分)
```

これでphpのロールが組み込まれました。
この状態でエラーがないかのチェックと、実際の適用を行ってみましょう。

```{code-block}
:language: bash

$ uv run ansible-playbook -K --syntax-check site.yml
$ uv run ansible-playbook -K site.yml
```

問題なく動作すれば、PHPのインストールとサービスの起動が完了しています。

一応確認方法として、`systemctl`を使ってチェックすると良いでしょう。

```{code-block}
:language: bash

$ systemctl status httpd
$ systemctl status php8.2-fpm
```

```{note}
確認ができたらそれぞれ{kbd}`q`で抜けてください
```

### Apacheとの連携

PHPのランタイム(php8.2-fpm)は動くようになりましたが、必要に応じてApache(httpd)側から呼び出されるように設定する必要があります。

- proxy_fcgiモジュール: Apache側でFastCGIプロトコルを使用する
- setenvifモジュール: 環境変数を設定する

UbuntuのApacheパッケージは、拡張機能(モジュール)の構成は個別にファイルで配置されています。
配置場所は {file}`/etc/apache2/mods-available/`ディレクトリです。

```{code-block}
:language: bash

$ ls /etc/apache2/mods-available
access_compat.load    authz_user.load     dir.load                  log_debug.load       proxy_fcgi.load      setenvif.conf
actions.conf          autoindex.conf      dump_io.load              log_forensic.load    proxy_fdpass.load    setenvif.load
actions.load          autoindex.load      echo.load                 lua.load             proxy_ftp.conf       slotmem_plain.load
alias.conf            brotli.load         env.load                  macro.load           proxy_ftp.load       slotmem_shm.load
...
```

使いたいモジュールの設定を、{file}`/etc/apache2/mods-enabled/`にシンボリックリンクを張ることで、次の起動時から有効化されます。
ただこの処理は少々面倒なため、ユーティリティとして`a2enmod`コマンドが用意されています[^a2enmod]。

[^a2enmod]: `a2enmod`は"Apache2 enable module"の略です。

```{code-block}
:language: bash

$ sudo a2enmod proxy_fcgi setenvif
Enabling module proxy_fcgi.
To activate the new configuration, you need to run:
  systemctl restart apache2
```

書かれている通りで、この後`apache2`サービスを再起動することで有効化されるとなっています。

この場合、コマンドを実行する必要があります。対応するアクションとして、`command`アクションがあるので、こちらを使って対応しましょう。

```{literalinclude} src/php-main.yml
:language: yaml
:caption: roles/php/tasks/main.yml(追加部分)
:linenos:
:emphasize-lines: 11-20
```

`command`アクションは大きく2つの使い方があります。

- `command`の直下にコマンドを記述する(単純に実行する)
- `command`の下に辞書を用意する ←今回はこちらを使用
  - `cmd`: 実行するコマンドライン
  - `creates`: 指定したファイルが存在する場合は実行しない(冪等性の確保)

`creates`で指定されたファイルが存在する場合、すでに作業が終わっていると判断されてスキップされます(ここが冪等性の確保)。
実行された場合は、`notify`でApache側の再起動を促すようにしています。

モジュール以外の設定についても同様で、`php8.2-fpm`をインストールした時点で、 `/etc/apache2/conf-available/php8.2-fpm.conf` という設定ファイルが配置されています。こちらを`a2enconf`コマンドで有効化する必要があり、こちらも変更後にApacheの再起動が必要となります(18-22行目)。
見ての通り、ハンドラーの呼び出し(`notify: Apache2の再起動`)はphpのロールでの定義ではありませんが、名前さえわかれば外部から呼び出すことができます。
なお、同じハンドラーが複数呼ばれる場合があっても、1回しか実行されません。

### 依存関係とメタデータ

このPHPのロールは、必要に応じてApache向けのロール(httpd)内ハンドラーを呼び出しています。
つまりこのロールは、httpdロールに**依存している**ということになります。

もしこの時に、`site.yml`のロール記述で、

```{code-block}
:language: yaml

  roles:
    - php
    - httpd
```

と書いていた場合、phpロールが先に実行されます(リストであることに注意)。そのためphp内でhttpdのハンドラーを呼び出したくても、その時点では存在が知られていない可能性があります(未知のハンドラー名が出ても困るという問題)。
この問題を解決するために、phpロールがhttpdロールに依存していることを明示的に宣言する必要があります。
これを行うのが、`meta/main.yml`ファイルです。

```{literalinclude} src/php-meta.yml
:language: yaml
:caption: roles/php/meta/main.yml
```

ここでは`dependencies`キーを使って、依存しているロール名をリストで指定します。
これにより、Ansibleはphpロールを実行する前にhttpdロールを実行するようになります。
今回は行いませんが、この記述により暗黙でもhttpdロールが実行されることになるため、`site.yml`でhttpdロールを明示的に指定する必要もなくなります。

```{note}
ただし、きちんと依存するロールであっても記述するようにしましょう。これは可読性の問題からも重要です。
```

改めてplaybookを起動して、必要な設定が入るかどうかをチェックしておきましょう。
