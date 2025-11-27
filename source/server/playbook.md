# Playbookについて

Ansibleでは、Ansibleコマンドからモジュールを呼び出して各インベントリに対して処理を実行していますが、処理内容が多岐にわたるといちいち指示していくのは面倒となります。
そこで処理内容をまとめて記述するための方法として、Playbookという仕組みが用意されています。

ここでは、Playbookの概要と、実際に作って挙動を見てみることにしましょう。

## Playbookの概要

Playbookは、YAML形式で記述されたファイルで、複数の処理内容をまとめて記述することができます。
Playbookは、以下のような構成要素から成り立っています。
- Play: Playbookの基本単位で、1つ以上のPlayから構成されます。各Playは、対象ホストグループ、使用するモジュール、変数などを定義します。
- Task: 各Play内で実行される個々の処理内容を定義します。各Taskは、使用するモジュールとその引数を指定します。
- Role: 複数のTaskや変数、テンプレートなどをまとめた再利用可能な単位です。Roleを使用することで、共通の設定や処理を簡単に適用できます。

### Play

Playは、対象となるホストグループの指定とタスク及びロールの実行順序を定義します。
YAMLとしては『リストの一つの要素』という形になります。

````{note}
YAMLのリストは、ハイフン(-)で始まる行で要素を区切ります。

```{code-block}
:language: yaml

- 42
- "Hello, World!"
- name: sample
  hosts: all
```

リストの最後の要素は辞書になっています{code}`{"name": "sample", "hosts": "all"}`。

````


```{code-block}
:language: yaml
:caption: Playbookの例

- name: サーバーの構成
  hosts: all
  become: true

  tasks:
    - name: task1
    - name: task2
    ...
```


### Task

タスク(Task)は、Play内で実行される個々の処理内容を定義します。各タスクは、使用するモジュールとその引数を指定します。
タスクは、Playの中で`tasks`キーの下にリスト形式で記述されます。
各タスクには、何をするのかがわかるように、`name`キーで名前を付けることが推奨されます。

```{code-block}
:language: yaml
:caption: Taskの例(Play内)

- name: サーバーの構成
  hosts: all
  become: true

  tasks:
    - name: 接続確認
      ping:
```

この例では、`ping`モジュールを使用して接続確認を行うタスクが定義されています。

### Role

ロール(Role)は、複数のタスクや変数、テンプレートなどをまとめた再利用可能な単位です。Roleを使用することで、共通の設定や処理を簡単に適用できます。
Roleは、Playの中で`roles`キーの下にリスト形式で記述されます。
現時点ではまだロールは使わないので、実際に使うときに改めて説明します。

## Playbookの実行

では実際にPlaybookを作製してみましょう。

```{literalinclude} src/site.yml
:caption: site.yml
:language: yaml
```

```{note}
授業用リポジトリ上にすでに作ってあるため、取得している方は作成は不要です。
```

そして、`ansible.cfg`ファイルにて、オプションをひとつ、追加しておいてください(保存操作を忘れずに)。

```{code-block} ini
:emphasize-lines: 4

[defaults]
inventory = ./inventory/hosts.yml
interpreter_python=/usr/bin/python3
nocows = 1
```
そして、以下のコマンドでPlaybookを呼び出して実行します。

```{code-block} bash
$ uv run ansible-playbook -K site.yml
PLAY [サーバーの構成] ****************************************

TASK [Gathering Facts] ***************************************
ok: [localhost]

TASK [接続確認] **********************************************
ok: [localhost]

PLAY RECAP ***************************************************
localhost    : ok=2 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0  
```

`-K`オプションは、必要に応じて`sudo`のパスワードを求めるためのオプションです。
Playbookの実行が完了すると、各ホストに対して定義されたタスクが順次実行されます。

```{note}
先程`ansible.cfg`に`nocows`を定義しましたが、実はあれは本当におまけです。
試しに無効化(`#nocows = 1`)して実行し直すとわかります。比較して好きな方で続けて構いません。
```

## パッケージ操作のタスクを追加してみよう

`htop`パッケージをインストールする操作を`ansible`コマンドで試していましたが、これをPlaybookで記述してみましょう。
`site.yml`の`tasks`セクションに以下のタスクを追加してください。

```{code-block}yaml
    - name: htopパッケージのインストール
      apt:
        name: htop
        state: present
        update_cache: yes
```

このPlaybookを実行すると、タスクが追加されたことで`htop`パッケージがインストールされます。

```{code-block} bash
$ uv run ansible-playbook -K site.yml
...

このようにタスクを記述することで、必要な作業を確認してくれます。
そして、宣言された内容に対する冪等性を維持しようと必要なタスクを実行します。

## 練習

`apt`モジュールを使って、同様に以下のパッケージもインストールするように記述してください。

- curl
- git
- gh

これらはおそらくインストール済みのため、書いておいても特に実害はありません。