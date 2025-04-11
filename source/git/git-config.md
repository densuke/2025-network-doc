# gitの設定

最後に `git` コマンドの設定を行います。
入力するのは2つの項目です。

- あなたの名前(ローマ字)
  - 日本語でも可能ですが、ローマ字の方が無難です
- GitHub登録のメールアドレス

```bash
$ git config --global user.name "あなたの名前"
$ git config --global user.email "GitHub登録のメールアドレス"
```

登録情報の確認をしておきます。

```bash
$ git config --list | fgrep user.  # user.を含むもののみフィルタ出力
user.name=SATO Daisuke
user.email=dXXXXXXXXXXXXXX@st.kobedenshi.ac.jp
```

という具合に出ていればOKです。
