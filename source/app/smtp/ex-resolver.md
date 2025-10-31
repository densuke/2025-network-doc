# 演習: MXとDNSの気持ちになってみる

ここまでで、メールの送信先をメールサーバーはDNSの助けを借りることがわかりました。
ではその様子を簡単なPythonコードで追いかけてみましょう。

## メールアドレスからドメインパートを切り出す

まずはメールアドレスからドメインパートを切り出す関数を書いてみましょう。
この処理は本気になるとすごい正規表現が必要ですが、簡素に行うのであれば、単純に文字列(メール・アドレス)を`@`で分割して後ろの部分を取れば良いでしょう。

```{literalinclude} app/23-smtp-01/mail_mx_resolver.py
:language: python
:linenos:
:lines: 8-31
:lineno-start: 8
:emphasize-lines: 16-18
```

```{note}
厳密に切り出すということであれば、そこそこ長大な正規表現が求められます。
とはいえ、実際の運用でそこまで厳密性を求めることもないと思います。

最近のドキュメントとしては、以下が良いかと思います。

- [君はメールアドレスの正規表現を適当にググって使っていないか？ - Zenn](https://zenn.dev/igz0/articles/email-validation-regex-best-practices)
```

## ドメインからMXレコードを引く

次に、ドメインからMXレコードを引く関数を書いてみましょう。
Pythonでは`dnspython`というライブラリを使うと簡単にDNSクエリが実行できます。
このライブラリは標準ではインストールされていないため、事前に`pip install dnspython`でインストールしておいてください。

```{note}
実習環境では`uv`を用いて配布しているため、`uv sync`でインストールを自動化されています。
手動で入れたいときは`uv add dnspython`で行います。
```

```{literalinclude} app/23-smtp-01/mail_mx_resolver.py
:language: python
:linenos:
:lines: 34-61
:lineno-start: 34
:emphasize-lines: 14-17
```

ここでは、渡された文字列(ドメイン)に対して、MXレコードを引いています。
MXレコードには送信先ホスト名とそれに対する優先度(preference)が含まれています。
よって値を辞書にして、辞書のリストとして返しています。

## IPアドレスの取得

最後に、ホスト名からIPアドレス(ここではIPv4に限定)を取得するようにしてみます。
同様に`dnspython`を使ってAレコードを引きます。

```{literalinclude} app/23-smtp-01/mail_mx_resolver.py
:language: python
:linenos:
:lines: 64-77
:lineno-start: 64
:emphasize-lines: 10-12
```

残りの部分はソースを読めばわかると思いますので、参照しておいてください。