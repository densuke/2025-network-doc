# Wordpressが動かないこととMySQLの関係

現状でWordpressのソースをドキュメントルートに配置して動かしてみたところ、以下のエラー画面にいきつくこととなります。

```{figure} images/wp-need-mysql.png
:width: 60%

Wordpressの初期画面(MySQLが必要)
```

これは重要なことを示しています。単純にエラーとしての出力に目が行ってしまいますが、それ以上の情報です。

- PHPが機能している(でないとこの画面は出ません)。
- Wordpressのコンテンツ自体は読み込まれている。
- (そのうえで)MySQLの拡張が利用できない。

つまり、PHPとMySQLの連携ができていないことが原因で、Wordpressが動作しないことがわかります。

## PHPとMySQL(MariaDB)の連携について

Wordpressは、バックエンド(永続ストレージ)のひとつとして、データベースを要求しています。
要求するデータベースはMySQL(および互換データベース)であり、今回はMariaDBを利用しています。
ところが不足している部分があります。 **PHPからMySQL(MariaDB)へ通信するための拡張モジュール** がインストールされていないのです。
そこで、この拡張モジュールを入れておきましょう。

## ロールをどうするか

結論から言えば、PHPのMySQL拡張モジュールに関しては、 `php8.2-mysql` というパッケージをインストールすることで解決します。しかし、このパッケージをどのようにインストールするかは一考に値します。

- 既存のphpロールに組み込む。
  - 悪くはないのですが、MySQL(MariaDB)と無関係に常に組み込まれることとなります。これはいいのでしょうか?

- 新規にphp-mysqlロールを作成する。
  - こちらのほうがよりモジュール化されており、必要なときにのみ組み込むことができます。将来的にMySQL以外のデータベースを利用する場合にも、phpロールを汚さずに済みます。

- Wordpressロールを作り、その中でphp-mysqlロールを組み込む。
  - こちらもモジュール化の観点からは悪くありません。しかし、Wordpressロールを作成するほどの規模感があるかどうかは疑問です。

色々考え方はできるかと思いますが、ここでは2つ目の『新規にphp-mysqlロールを作成する』方法を採用します。

## php-mysqlロールの作成とハンドラーの準備

PHPにMySQL拡張モジュールである `php8.2-mysql` パッケージをインストールするロールを作成します。
前節の通り、 `php-mysql` という名前でロールを作成しましょう。

```bash
mkdir -pv roles/php-mysql/tasks
```

そして、ロール内タスクを作製します。

```{code-block}
:language: yaml
:caption: roles/php-mysql/tasks/main.yml ※途中の段階ですが一旦作成する
---
- name: php-mysqlのインストール
  apt:
    name: php8.2-mysql
    state: present
```

一旦これを`site.yml`に組み込んで、動作確認を行ってみましょう。

```{code-block}
:language: yaml
:caption: site.yml
:emphasize-lines: 5

  roles:
    - httpd
    - php
    - mariadb
    - php-mysql

```

この状態でプレイブック`site.yml`を処理させると、とりあえず `php8.2-mysql` パッケージがインストールされます。

```{code-block}
:language: bash

$ uv run ansible-playbook -K site.yml  # makeで代行してもOK
...
$ dpkg -l php8.2-mysql # インストールされているか確認("ii"で始まればOK)
要望=(U)不明/(I)インストール/(R)削除/(P)完全削除/(H)保持
| 状態=(N)無/(I)インストール済/(C)設定/(U)展開/(F)設定失敗/(H)半インストール/(W)トリガ待ち/(T)トリガ保留
|/ エラー?=(空欄)無/(R)要再インストール (状態,エラーの大文字=異常)
||/ 名前           バージョン       アーキテクチ 説明
+++-==============-================-============-=================================
ii  php8.2-mysql   8.2.XXXXXXXXXXX   arm64        MySQL module for PHP
```

## 拡張モジュールの有効化はされているのか?

拡張モジュールはインストールされたと思いますが、PHP側で認識できているかわかりません。
お手軽に確認する方法の一つとして、`phpinfo()`を利用するということがあります。

1. ポート転送を確認し、ブラウザでサーバーに一旦アクセスする
2. URLを書き換えて、以前`phpinfo()`を確認するために組み込んでいる、 `/info.php` を付加してアクセスする

下へ進めていくと、認識されているモジュールの情報がアルファベット順に出てきます。
MySQL関係なため、Mで始めるところまでスクロールすると、以下のように出力が入っていると思われます。

```{figure} images/php-plugin-not-mysqli.png
:width: 75%

MySQL拡張モジュールの状況
```

`mysqlnd` や `pdo-mysql`というモジュールが入っている可能性がありますが、出ていないこともあります。
一見するとうまく行っているように見えるのですが、少しややこしいことになっているので注意が必要です。
実はMySQLに関する拡張モジュールは複数あり、以下のようになっています。

- mysql: 古い拡張モジュールで、現在は非推奨となっています。将来的に削除される可能性があります(そもそも存在しない可能性すらある)。
- mysqli: 改良版のMySQL拡張モジュールで、より多くの機能を提供します。MySQLデータベースとやり取りするために推奨されるモジュールです。
- pdo-mysql: PHP Data Objects(PDO)拡張モジュールのMySQLドライバです。PDOはデータベースアクセスのための抽象化レイヤーを提供し、異なるデータベースシステム間でのコードの移植性を向上させます。

```{note}
mysqlnd拡張モジュールは、MySQL Native Driverの略で、MySQLデータベースとPHP間の通信を最適化するためのドライバと考えてください。
通常このモジュールを直接叩くような使い方をせず、mysqliやpdo-mysqlなどの拡張モジュールがmysqlndを利用してMySQLと通信します。
```

現代的なPHPでのデータベースアクセスでは、`pdo-mysql`が主に利用されているため、こちらが自動的に有効化されている可能性がありますが、実はWordpressでは`mysqli`が利用されています。
そのため、`mysqli`が有効化されているかどうかを確認する必要があります。
先程のスクリーンショットのように`mysqli`が出てない場合は、有効化を行う必要があるということです。

有効化および無効化を行うためのツールとして、`a2enmod`と同じように`phpenmod`と`phpdismod`があります。

- `phpenmod mysqli`: `mysqli`モジュールを有効化します。
- `phpdismod mysqli`: `mysqli`モジュールを無効化します。

これをAnsibleのロールで実行させる方法については、php-fpmで行った`command`モジュールを使うことで対応できるのですが、気になるのが『何があれば成功したか』の指標となる`creates`オプションです。

試しに行って検証してみましょう。

```{code-block}
# モジュール定義があるかの確認
$ ls /etc/php/8.2/mods-available/m*
/etc/php/8.2/mods-available/mysqli.ini  /etc/php/8.2/mods-available/mysqlnd.ini

# fpmを使っている場合、有効なモジュール定義のリンクは以下に集められています
$ ls ls /etc/php/8.2/fpm/conf.d/
... 20-pdo_mysql.ini ...
```

どうやら、何らかの数字(実は読み込み優先度)が付与された`pdo_mysql.ini`が存在していることがわかります。
`mysqli`モジュールの場合は`20-mysqli.ini`という名前になるはずです。

試しに`phpenmod`で試してみましょう。

```{code-block}
:language: bash

$ sudo phpenmod mysqli # 有効化
$ ls /etc/php/8.2/fpm/conf.d/
... 20-mysqli.ini ...

$ sudo phpdismod mysqli # 無効化
$ ls /etc/php/8.2/fpm/conf.d/
... (20-mysqli.iniが無くなる) ...
```

数字(20)の付与された`mysqli.ini`が生成されたり消えたりすることがわかります。
これをキーとしてロールを作成すれば、冪等性が確保できそうです。

## 拡張モジュールの有効化と再起動

以上を踏まえて、ロールのタスクを追加しておきましょう。

```{code-block}
:language: yaml
:caption: roles/php-mysql/tasks/main.yml
:linenos:
:emphasize-lines: 7-11
---
- name: php-mysqlのインストール
  apt:
    name: php8.2-mysql
    state: present

- name: php-mysqlの有効化 
  command:
    cmd: phpenmod mysqli
    creates: /etc/php/8.2/fpm/conf.d/20-mysqli.ini
  notify: php-fpmの再起動
```

そして、有効化しても再起動をしないと反映されないため、ハンドラーの追加が必要です。
11行目にあるように、php-fpmの再起動となるため、この処理は`php`ロールのハンドラーを利用します。

```{code-block}
:language: yaml
:caption: roles/php/handlers/main.yml ※ phpの側ですので注意!

---
- name: php-fpmの再起動
  service:
    name: php8.2-fpm
    state: restarted
```

これで、`php-mysql`ロールの完成です。

実際に通して実行し、`phpinfo()`で確認してみましょう。

```{figure} images/php-plugin-mysqli.png
:width: 75%

MySQLi拡張モジュールの有効化確認
```

これで無事`mysqli`モジュールが有効化されました。
では、改めて `/wordpress` にアクセスするとどうでしょう。

```{figure} images/wp-setup.png
:width: 60%

Wordpressのセットアップ画面
```

表示が変わっていますね。無事MySQL拡張モジュールが有効化され、WordpressがMariaDBに接続できる準備ができたため、セットアップ画面が表示されました。
本来であれば、この後にデータベースの設定を行えばOKですが、直接おいたファイル群を使っているので、アーカイブの取得とセットアップをロールとして組み込むことにしましょう。
