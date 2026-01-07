# MySQL環境の構築

では、LAMPの最後の一柱となるMySQLのインストールと設定を行います。
ただし、Ubuntu環境では互換システムとなっているMariaDBがデフォルトとなっているため、実際にはMariaDBをインストールします。

```{note}
Ubuntu 20.04以降では、MySQLではなくMariaDBがデフォルトのデータベースシステムとして提供されています。本ドキュメントではMariaDBを使用しますが、MySQLとほぼ同等の機能を提供します。

これは、本来はOSSとして存在していたMySQLをOracle社が買収したことに伴い、MySQLのオープンソース版を維持するためにフォークされたプロジェクトであるためです。
Ubuntu LinuxのベースとなっているDebian GNU/Linux側で収録するデータベースとしてMariaDBに切り替わったことにより、UbuntuでもMariaDBがデフォルトとなっています。
機能面での違いはほとんどありませんが、一部のコマンドや設定ファイルの場所などが異なる場合がありますので注意してください。

```

## インストール用のロールの作成

では、これまで同様にMariaDBを入れるためのロールを準備します。
ロール名はmariadbとしておきましょう。

```{code-block}
:language: bash
$ mkdir roles/mariadb
$ mkdir roles/mariadb/tasks
$ mkdir roles/mariadb/vars # NEW
```

今回{file}`vars`ディレクトリも作成しています。これはロール中で利用する(かもしれない)Ansible内の変数を格納するために使えるディレクトリです。
今回の場合、MariaDBにおけるrootのパスワードを格納するために使います。

## 変数の格納方法

ロールの中で使う変数は、{file}`vars/main.yml`というファイルに格納します。

```{literalinclude} src/mariadb/vars/main.yml
:language: yaml
:caption: roles/mariadb/vars/main.yml
```

見ての通りで、辞書として変数名と値を格納するだけです。
今回はMariaDBのrootユーザーのパスワードを変数として格納しています。

```{warning}
実際の運用においては、パスワードなどの機密情報(機微情報)を平文で保存することは避けるべきです。
可能であれば実行時に入力を促すほうが良いのですが、バッチ実行上の支障も出るかもしれません。

その際に助けになりそうなものとして、Ansible Vaultがあります。
Ansible Vaultは、Ansibleで使用する変数やファイルを暗号化して保存するための機能です。
これにより、機密情報を安全に管理し、必要なときにのみ復号して使用することができます。
詳細については、公式ドキュメントの[Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html)を参照してください。
```

## ロール内タスクの作成

つづいてタスクです。
タスクについては、少々トリッキーなことをしています。

```{literalinclude} src/mariadb/tasks/main.yml
:language: yaml
:caption: roles/mariadb/tasks/main.yml
:linenos:
```

以下の2箇所(いや3箇所か)は他のタスクでも行っていることですので軽く流しておきます。

- 2〜9行目: MariaDBのパッケージと、Pythonで制御するためのパッケージを入れています。Python制御はこの後のタスクで使用します。
- 45〜49行目: MariaDBサーバーの起動と自動起動の設定を行っています。

### パスワードをどう設定するのか

MySQLやMariaDBは、いわゆるクライアント、サーバー型のため、サーバー側ではデータベースの利用者に関する設定が必要です。
特にrootユーザーは重要で、Linux世界におけるroot同様に、データベース管理における管理者となっています。
そのため、rootのパスワードを設定しないと他人のデータベースにさわれたりして大変危険です。

Ubuntu版のMariaDBでは、初期状態において、以下の状態での接続においてはパスワード無しでrootで接続できてしまいます。

- ローカルホストからのUNIXドメインソケットを用いた接続
- かつ、(Linux側での)rootユーザーでの接続

これは、Linux側でrootユーザーであれば、MariaDBのrootユーザーにもなれる、ということを意味しています。
したがって、MariaDBのrootユーザーにパスワードを設定するには、Linux側でrootユーザーでMariaDBに接続し、パスワードを設定する必要があります。

### パスワード設定タスクの解説

そこで、実際に接続をしているタスク部分を抜粋します。

```{literalinclude} src/mariadb/tasks/main.yml
:language: yaml
:caption: roles/mariadb/tasks/main.yml (抜粋)
:lines: 16-24
:emphasize-lines: 1-8
:linenos:
:lineno-start: 16
```

ここでは、`mysql_user`モジュール[^mysql_user] を使用して、rootユーザーのパスワードを設定しています。
パラメーターが多岐にわたっておりますが、特に重要な部分は以下のとおりです。

- 肝心のパスワードは{file}`vars/main.yml`で定義した変数`mariadb_root_password`を使用しています。変数展開を使って渡しています(20行目)
- `login_unix_socket`パラメーターを使用して、UNIXドメインソケット経由で接続するように指定しています(21行目)。

ただ、このモジュールが有効なのは、パスワードがまだ設定されていない初期状態のみです。
一度このタスクを実行してパスワードが設定されると、以降はこのタスクは失敗します。
そのため、どうにかして一度だけ実行されるようにしなければなりません。

[^mysql_user]: [公式ドキュメントのmysql_userモジュール](https://docs.ansible.com/projects/ansible/latest/collections/community/mysql/mysql_user_module.html)

ここでは、24行目の`when`条件が登場するのですが、それについては次に説明します。

### 一度だけ実行するには?

Ansibleのタスクやロールの流れは、常に冪等性を注意しておく必要があります。
つまり、同じタスクを何度実行しても結果が変わらないようにする必要があります。
しかし、MariaDBのrootパスワード設定タスクは、一度実行してしまうと、以降は失敗してしまいます。
そこで、24行目の`when`条件を使用して、タスクの実行を制御しています。

でもそのための分岐はどのように実現しているのでしょうか。
それを行っているのが直前のタスクである11〜14行目です。

```{literalinclude} src/mariadb/tasks/main.yml
:language: yaml
:caption: roles/mariadb/tasks/main.yml (抜粋)
:lines: 11-14
:linenos:
:lineno-start: 11
```

`stat`というモジュールが登場しました[^stat]。
`path`で指定したファイルの存在や状態を保持するためのモジュールです。処理結果が存在するため、それを保存するために`register`を使用しています。
`register`で登録された変数(オブジェクト)は、以降参照することができます。

[^stat]: [公式ドキュメントのstatモジュール](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/stat_module.html)

つまり、このモジュールは、

- 該当ファイルが存在するかどうか
- 存在するならそれはファイルなのか、ディレクトリなのか、所有権は? アクセス権限は? といった情報を収集して変数で参照できるようにしてくれているのです。

そして24行目につながります。

```{literalinclude} src/mariadb/tasks/main.yml
:language: yaml
:caption: roles/mariadb/tasks/main.yml (抜粋)
:lines: 16-24
:emphasize-lines: 9
:linenos:
:lineno-start: 16
```

`when`条件は、このタスクが実行されるかを判定するために使います。
`not`が入っているので真偽反転を宣言したうえで、先程設定された`mycnf_file`変数のフィールド`stat.exists`を参照させています。その結果としてすでに存在している場合は偽となるために実行がスキップされます。

### `.my.cnf`の作成

パスワード設定後のタスクで、肝心の`.my.cnf`ファイルを作成しています(26〜43行目)。

```{literalinclude} src/mariadb/tasks/main.yml
:language: yaml
:caption: roles/mariadb/tasks/main.yml (抜粋)
:lines: 26-43
:linenos:
:lineno-start: 26
```

ここでは2つのタスクを実行しています。

- `.my.cnf`ファイルの作成(26〜34行目)
- `.my.cnf`ファイルでのパスワード更新(36〜43行目)
  - 実際にはログインができるかの検証です。

### ファイルの存在と作業の切り替え

つまり今回は、キーとなるファイル `.my.cnf`が存在するかに応じて、処理が分岐したことになります。

- ファイルが存在しない場合、ソケットで接続してrootパスワードを設定した後、`.my.cnf`ファイルを作成する
- ファイルが存在する場合、`.my.cnf`ファイルを使ってログインできるかを検証する

## ロールの適用と接続の確認

プレイブックに組み込んで実行してみましょう。

```{code-block}
:language: yaml
:caption: site.ymlにmariadbロールを追加

  roles:
    - httpd
    - php
    - mariadb # この行を追加
```

実行後、MariaDBに接続してみましょう。

```{code-block}
:language: bash
$ mysql -u root -p
Enter password: ********  # mariadb_root_passwordで設定したパスワードを入力
※ Linuxユーザーのパスワードではないので注意!
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 34
Server version: 10.11.14-MariaDB-0+deb12u2 Debian 12

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> 
```

プロンプトが出れば無事完了です。`exit`と入れれば抜けられます。

## やり直しの方法

中途半端に行った場合に、以降のタスク実行がうまく行かなくなることがあります。
この場合、MariaDBのインスタンスと`.my.cnf`ファイルを削除してやり直すことができます。

```{code-block} bash
sudo apt purge --auto-remove --purge -y mariadb-server
sudo rm -f /root/.my.cnf
```

そのうえで再度プレイブックを実行してみてください。

## ここまでで

ここまでで、LAMPの基礎環境の構築が進みました。
あとは実際にWebアプリケーションを配置してみましょう。
