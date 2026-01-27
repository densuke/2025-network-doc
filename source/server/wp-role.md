# ロールベースでのWordpress導入

いよいよ準備ができました。
これでWordpressの導入をしていきましょう。

Wordpressの導入は、ロールを用いて行うこととします。
また、Wordpress自体はPHPとMySQL(MariaDB)の両方が必要であり、さらに`php-mysql`の拡張も必要です。
これらも依存関係として組み込むことで、インストール漏れが起きないようにしないといけません。

ということで、やることは以下の通りです。

- Wordpressロールの作成
- 依存関係の設定
- データベースの準備
- Wordpressのダウンロードと配置

なお今回は、データベースの作成についてはすでに作成済みの管理者権限をそのまま用いて行います。
本格的に体験するうえでは、ユーザーを専用に作ることを推奨しますが、これは皆さんへの研究課題としておきます。

とりあえずロール用にディレクトリ作成を先に行ってから進めましょう。

```{code-block}
:language: bash

$ mkdir -pv roles/wordpress/tasks
$ mkdir -pv roles/wordpress/meta
```

## 依存関係の設定

ここまでの流れとして、Wordpressを使うためには、`php-mysql`のPHP拡張モジュールが必要です。
さらに、`php-mysql`ロールを動かすためには`php`ロールが必要です。
当然バックエンドとしてのデータベースも必要なため、`mariadb`ロールも必要です。

以上を踏まえると、 `roles/wordpress/meta/main.yml` には以下のように依存関係を設定しておくことが必要です。
設定しなくても進めることはできますが、その場合はロールの順序に気をつけないといけません。

```{code-block}
:language: yaml
:caption: roles/wordpress/meta/main.yml

---
dependencies:
    - role: php-mysql
    - role: php
    - role: mariadb
```

## データベースの準備

続いて、データベースを準備します。
mysqlの関連モジュールとして、データベースを作成するものがあるので、今回はこちらを使ってみましょう。

```{code-block}
:language: yaml
:caption: roles/wordpress/tasks/main.yml ※途中の段階ですが一旦作成

- name: データベースの作成
  mysql_db:
    name: "wordpress"
    state: present
    encoding: utf8mb4
    collation: utf8mb4_general_ci
    login_host: localhost
    login_user: root
```

パスワードの設定がないように見えますが、これは今回の一連のロール中で`mariadb`ロールのrootに関して、 {file}`/root/.my.cnf` にログイン情報を保存しているためです。
こちらが自動的に参照されるためパスワードの記載が不要となっています。


```{warning}
今回は練習のためrootユーザーをそのまま使っています。
本格的な運用においては、必ず専用のユーザーを作製して、切り分けて使うようにしましょう。
```

なお、文字エンコーディングについては、以下の設定にしています。

- `encodeing: utf8mb4` → UTF-8の4バイト文字まで対応
- `collation: utf8mb4_general_ci` → 大文字小文字を区別しない(ci; Case Insensitive)照合順序

## Wordpressのダウンロードと配置

続いて、Wordpressのダウンロードと配置を行います。
Wordpressのダウンロードとアーカイブ操作は以前扱っていますが、この部分を担当するモジュールとして、`unarchive`モジュールがあります。

```{code-block}
:language: yaml
:caption: roles/wordpress/tasks/main.yml (一部分)

- name: ソースコードの展開
  unarchive:
    src: https://ja.wordpress.org/wordpress-6.9-ja.tar.gz
    remote_src: yes
    dest: /var/www/html
    creates: /var/www/html/wordpress
    owner: www-data
    group: www-data
    mode: '0755'
```

`unarchive`は地味に便利で、なんとURLから直接ダウンロードして展開まで行ってくれます。
ただしそれを行うために、 `remote_src: yes` を指定する必要があります。
展開先(`dest`)、所有権/アクセス権調整も一緒に行えて便利です。

```{note}
残念なのが、ダウンロードしたファイルの正真性確認ができないことです。
そのため、より厳密に行いたいのであれば、`get_url`モジュールなどで一旦ダウンロードしてから(こちらには機能がある)、`unarchive`で展開する方法が推奨されます。
```

以上をにより、Wordpressに必要となるデータベースの準備とWordpress本体の展開までを組み込むことが可能となっています。
