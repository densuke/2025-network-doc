# 作業の前の確認処理

この作業は、一度だけ行っておけば大丈夫です(VMを初期化したときなどは再実行が必要です)。

今後の作業で、Gitによるコミットを行います。
このときに設定ができてないとコミットができずに戸惑うことになるので、必ずやっておいてください。

## まず確認

ターミナルを開きます(ターミナルメニューもしくは{kbd}`Ctrl+Shift+` `)。
開いたら、以下のコマンドを実行してください。

```bash
$ git config --list | grep ^user   # ユーザー情報の取得
```

このときに何も出ないときは設定が一度必要になります。

## ユーザー設定

```bash
$ git config --global user.name "あなたの名前(ローマ字推奨)"  # 名前の設定
$ git config --global user.email "GitHub登録のメールアドレス"  # メールアドレス
```

```{warning}
よく手打ちで `email`を`emal` と打ってしまう人が見受けられます、注意して下さい。
```

確認してみましょう。

```bash
$ git config --list | grep ^user   # ユーザー情報の取得
user.name=SATO Daisuke
user.email=densuke@example.com
# ここで設定が正しいことを確認しておこう
```

もし間違っていたらもう一度同じ操作で上書きできます。
