# 準備

TCPプログラミングの演習を始めるための準備手順を説明します。
uvを使ったPythonの環境管理を行ってから作成します。
この部分は、UDPでのプログラミング環境構築と同じです。

1. network(VM)にログインする
2. 開発用のディレクトリを作り、そこでVS Codeを起動し直す
3. Pythonの利用を宣言する

このうち1.のnetwork(VM)にログインするは、すでに完了しているとします。2,3の話に移ります。

## 開発用のディレクトリ作成

開発用のディレクトリを作成します。ここでは、`~/tcp-programming`としておきます。

```bash
mkdir ~/tcp-programming
```

次に、VS Codeをこの開発用ディレクトリで開き直します。

```bash
cd ~/tcp-programming
code --reuse-window .
```

````{note}
- VS Codeの`--reuse-window`オプションは、すでに開いているウィンドウを再利用するためのものです。
- 場合によっては再度ログインの扱いとなり、パスワードを聞かれることがあります。
```bash
cd ~/tcp-programming
code --reuse-window .
```

````{note}


## Pythonの利用を宣言する

本科目でのPythonはuvを使って制御しています。そのため、Pythonの利用をuvで宣言します。開発環境に切り替えた後のVS Codeのターミナルで以下のコマンドを打ち込んでください。

```bash
uv init                 # uvの初期化
```

もし `main.py` が作成されている場合は、今回は使わないので削除してかまいません。
また、`README.md` も不要なので削除してかまいません。

結果として、以下のファイルがあればOKとなります。

- {file}`.python-version` ※ 隠しファイルで見えない場合もあります
- {file}`pyproject.toml`