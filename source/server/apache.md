# 実践: Apache httpdサーバーを導入してみよう

以前の資料にて、実際にWebサーバーを導入する例としてApache HTTP Serverを取り上げました。
ここで改めて、Ansibleを用いた『冪等性』を意識した導入と設定を見てみましょう。

## Apacheの導入

Apache自体は、OSのパッケージ管理システム(Ubuntuのためapt)を用いたインストールとなります。
これ自体は、前回までの演習で触っているのでさほど難しいということはありません。

```{code-block}
:language: yaml

# Apache httpdのインストールと起動
    - name: Apache httpdのインストール
      apt:
        name: apache2
        state: present
```

ただし、ここまでの演習において、パッケージ導入がうまくいかない(リポジトリ情報がうまく取得できない)というケースが散見されていたので、おまじない代わりに事前に強制的にリポジトリを更新するようにしてみたいと思います。

タスク指定の冒頭で行っておくと良いでしょう。

```{code-block}
:language: yaml

  tasks:
    - name: 最新のパッケージリストの更新
      apt:
        update_cache: yes
```

ここで前回までの内容から不要なものを削除して、`tasks`以下をスッキリさせてみましょう。

```{code-block}
:language: yaml

  tasks:
    - name: 最新のパッケージリストの更新
      apt:
        update_cache: yes
      # Apache httpdのインストールと起動
    - name: Apache httpdのインストール
      apt:
        name: apache2
        state: present
```

この記述により、apache2パッケージの状態が確認され、入っていないようだったら追加処理が行われます。

## Systemdサービスの確認

サーバーは、インストールしただけでは動作しないことがあります。
一般にサーバー上のプロセス(サービス)は、OSの起動時に必要に応じて起動することになります。
そして、先程インストールされたとしたら、そもそも現在起動しているかも怪しいです。
そのため、サービスの状態として、以下の2点を考慮しておく必要があります。

- 現時点でサービスが起動しているか。
- OS起動時に自動的にサービスが起動するようになっているか。

この2点をチェックするために、Ansibleではserviceというモジュールがあります。
serviceモジュールを使って起動状態の確認と自動起動の確認をしておきましょう。

```{code-block}
:language: yaml

    - name: Apache httpdサービスの起動と有効化
      service:
        name: apache2
        state: started
        enabled: yes
```

- state: サービスの現在の状態(あるべき姿)を指定します。
  - started: サービスが起動していることを保証します。停止している場合は起動します。
  - stopped: サービスが停止していることを保証します。起動している場合は停止します。
  - restarted: サービスを再起動します。
  - reloaded: サービスの設定を再読み込みします(サービス自体を止めない)[^reload]。
- enabled: サービスの自動起動設定を指定します。
  - yes: OS起動時に自動的にサービスが起動するように設定します。
  - no: OS起動時にサービスが自動的に起動しないように設定します。

[^reload]: すべてのサービスが再読み込みをサポートしているわけではありません。サービスが対応していない場合、Ansibleはエラーを返します。

これでApache HTTP Serverがインストールされ、起動していることが保証されました。

## 動かない時のトラブルシューティング

授業で実際に行うと、うまく機能しないという報告が散見されています。
大きく3つの可能性が確認できましたので、以下に示しておきます。

### `uv`入っていますか?

PCの初期化や変更で、`uv`がVMに入っていない可能性があります。
リモート接続後、ターミナルにて、

```{code-block}
:language: bash

$ setup-uv

```

としてみてください。もし`uv`が入っていなければ、インストールが始まります。

### Playbook(というかYAMLの)記述ミス

YAMLの設定ミスの可能性もあります(インデントミスやスペルミス、ハイフン(`-`)の後に空白が無いなどのマーカーミス)。
こちらについては、Ansibleのチェックツールを使うと便利です。

```{code-block}
:language: bash

$ uv run ansible-playbook --syntax-check site.yml

```

YAMLの文法およびモジュールのパラメーターのチェックを行ってくれます。

```{code-block}
:language: bash
:caption: 特に問題がない場合

$ uv run ansible-playbook --syntax-check site.yml

playbook: site.yml
```

```{code-block}
:language: bash
:caption: モジュール名に誤りがありそうな場合

[ERROR]: couldn't resolve module/action 'ap'. This often indicates a misspelling, missing collection, or incorrect module path.
Origin: /home/linux/server-config-ajihurai/site.yml:30:7

28 #         update_cache: yes
29
30     - name: Apache httpdのインストール
         ^ column 7

```

カラム位置や行位置が少し先へ行っているので混乱するかもしれませんが、エラーとして『`ap`という解決できないモジュール(もしくはアクション)がある』ということから類推できると思います。

ちょっと怖いのが、モジュールの引数の問題です。
こちらは動作時にしか評価できない(`--syntax-check`では通過してしまう)仕様のため『やったフリ』をするチェックオプション(`-C`)で行う必要があります。

```{code-block}
:language: bash
:caption: モジュールの引数のミス(`name`を`nam`にした場合)

$ uv run ansible-playbook -C -K site.yml
BECOME password:

...

TASK [Apache httpdサービスの起動と有効化] *********************************************************************
[ERROR]: Task failed: Module failed: missing parameter(s) required by 'state': name
Origin: /home/linux/server-config-ajihurai/site.yml:34:7

32         name: apache2
33         state: present
34     - name: Apache httpdサービスの起動と有効化
         ^ column 7

fatal: [localhost]: FAILED! => {"changed": false, "msg": "missing parameter(s) required by 'state': name"}
```

この場合、`state`引数のために必要な`name`引数が無いというエラーが出ています。
少々解析が難しいかもしれませんが、そのあたりにあるというだけでも候補が絞りやすいと思います。

### aptがコケてしまう

`apt`モジュールでパッケージ操作を行うときに、パッケージキャッシュが正常に更新できずに失敗することが時折あるようです。
対策として、強制的に最新版のパッケージリストを取得するようにしてみましょう。

```{code-block}
:language: bash

$ sudo rm -fr /var/lib/apt
$ sudo rm -fr /var/cache/apt
$ sudo apt update # パッケージリストの更新(時間がかかります)

$ uv run ansible-playbook -K site.yml
```