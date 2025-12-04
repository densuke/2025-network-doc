# ロールによるひとまとめ

Ansibleでは、ロール(Role)という仕組みがあります。
これを用いることで、関連するタスクやハンドラー、データなどをひとまとめにして管理することができます。
ロールにより役割などを考えて論理的に構造を整理できるようになります。

## ロールの構成

ロールは、特定のディレクトリを用意して、その中に配置をしていきます。基本的な構造としては、以下のようになります。

```{code-block}
:language: text

roles/
    <rolename>/
        tasks/
            main.yml
        handlers/
            main.yml
        files/
        templates/
        vars/
            main.yml
        defaults/
            main.yml
        meta/
            main.yml
```

- tasks/: タスクを配置するディレクトリ
- handlers/: ハンドラーを配置するディレクトリ
- files/: ファイルを配置するディレクトリ
- templates/: テンプレートファイルを配置するディレクトリ
- vars/: 変数を配置するディレクトリ
- defaults/: デフォルト変数を配置するディレクトリ
- meta/: ロールのメタデータを配置するディレクトリ

といってもいきなり全てを用意する必要はなく、今回はせいぜい`tasks`と`handlers`、`files`あたりを使うだけです。

## httpdロールを作成する

では、現状の構成を基に、httpdロールを作成してみましょう。

まず、`roles`ディレクトリを作成します。
その中に`httpd`ディレクトリを作製し、さらにその中に`tasks`ディレクトリを作成します。

```{code-block}
:language: bash

$ mkdir -pv roles/httpd/tasks
```

```{note}
`-p`オプションは、親ディレクトリがないときにまとめて作るためのオプションでしたね。
`tasks`ディレクトリの親となる`httpd`が無いため、作成しようとしますが、こちらも`roles`が無いためにエラーとなってしまいます。
そのため、`roles`から順にまとめて作成するために`-p`オプションを付与しています。
```

### タスクの作成

タスクはロール内の`tasks/main.yml`に記述します。では、先程までに作成してきたplaybookの内容をこちらに移動してみましょう。
この中はすでにタスクの一覧であることが判明しているため、トップレベルにタスク達を記述すればOKです(インデントが先頭になっていることに注意)。

```{code-block}
:language: yaml
:caption: roles/httpd/tasks/main.yml

---
- name: Apache httpdのインストール
  apt:
    name: apache2
    state: present
- name: Apache httpdサービスの起動と有効化
  service:
    name: apache2
    state: started
    enabled: yes
```

### ハンドラーの作成

同様に、ハンドラーもロール内の`handlers/main.yml`に記述します。では、こちらも先程までに作成してきたplaybookの内容をこちらに移動してみましょう。

```{code-block}
:language: yaml
:caption: roles/httpd/handlers/main.yml

---
- name: Apacheを再起動
  service:
    name: apache2
    state: restarted
```

### Playbookの修正

これで一通りロールに移動させたので、playbookを修正してロールを呼び出すようにしましょう。
まずはコメントアウトの形にして、動作をチェックしてから本格的に削除させましょう。

```{note}
なお巻き添えで『最新のパッケージリストの更新』もコメントアウトしています。
これは仕様上、ロールが先に実行されてしまうため、この位置に書いても『必要でApacheをインストールした』ときには更新が行われており、意味がなくなってしまうためです。
```

```{code-block}
- name: サーバーの構成
  hosts: all
  become: true

  roles: # 追加
    - httpd

  tasks:
#    - name: 最新のパッケージリストの更新
#      apt:
#        update_cache: yes
#    - name: Apache httpdのインストール
#      apt:
#        name: apache2
#        state: present
#    - name: Apache httpdサービスの起動と有効化
#      service:
#        name: apache2
#        state: started
#        enabled: yes
    - name: サンプルファイルを配置(コンテンツ)
      copy:
        src: sample.html
        dest: /var/www/html/sample.html
        owner: www-data
        group: www-data
        mode: '0644'
      notify: Apacheを再起動
#  handlers:
#    - name: Apacheを再起動
#      service:
#        name: apache2
#        state: restarted
```

このようにすると、かなりスッキリするようになります。挙動の変化がないかをチェックしておきましょう。

```{code-block}
:language: bash

# 先にこれまでの処理内容を一旦削除する
$ sudo rm /var/www/html/sample.html
$ sudo apt purge --auto-remove -y apache2
$ uv run ansible-playbook  -K site.yml
...
TASK [httpd : Apache httpdのインストール] ****************************************
changed: [localhost]
...
```

ロール内タスクは『ロール名: タスク名』という形で表示されていることがわかります。
一通り動くことがわかったら、コメントにしていたところを削除して再度確認しておきましょう。

```{code-block}
:language: bash
:caption: site.yml

- name: サーバーの構成
  hosts: all
  become: true

  roles:
    - httpd

  tasks:
    - name: サンプルファイルを配置(コンテンツ)
      copy:
        src: sample.html
        dest: /var/www/html/sample.html
        owner: www-data
        group: www-data
        mode: '0644'
      notify: Apacheを再起動
```

かなりスッキリしましたね。こちらも動作確認しておきましょう。

```{code-block}
:language: bash

$ uv run ansible-playbook -K site.yml
PLAY [サーバーの構成] ****************************************

TASK [Gathering Facts] ************************************
ok: [localhost]

TASK [httpd : Apache httpdのインストール] ********************
ok: [localhost]

TASK [httpd : Apache httpdサービスの起動と有効化] **************
ok: [localhost]

TASK [サンプルファイルを配置(コンテンツ)] ************************
ok: [localhost]

PLAY RECAP *************************************************
localhost : ok=4 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0   
```

このように、かなりスッキリした記述となります。

