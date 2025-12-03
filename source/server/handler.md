# ハンドラー

タスクの中には、作業後に別の作業を呼び出す必要がある場合もあります。
たとえば、サーバーの設定ファイルを更新した後に、Apacheを再起動して反映させるというケースです。
このような目的のために、handlerとnotifyという仕組みが用意されています。

- notify: handlerの呼び出し
- handler: 通知を受けて実行するタスク

## 実例: ファイルを置いたら再起動

実際に行ってみましょう。
前節にて、Apacheのドキュメントルートにファイルを配置するコードを入れています。
本来不要ですが、ファイルを更新したらApacheを再起動するということを考えてみます。

```{note}
本来は不要な行為です。
むしろすべきは『設定ファイルを更新したときに反映のために再起動させる』でしょう。
ここまでの話ではまだ設定ファイルを操作していないので、あくまで例示として試してください。
```

ハンドラーは、タスク(tasks)と同じインデントレベルで定義します。

```{code-block}
:language: yaml

  handlers:
    - name: Apacheを再起動
      service:
        name: apache2
        state: restarted
```

これで、どこかから「Apacheを再起動」という通知が来た場合に、実行が予約されることになります。

そして、ファイルをコピーするタスクがありましたが、そこに`notify`を追加します。

```{code-block}
:language: yaml

    - name: サンプルファイルを配置(コンテンツ)
      copy:
        src: sample.html
        dest: /var/www/html/sample.html
        owner: www-data
        group: www-data
        mode: '0644'
      notify: Apacheを再起動
```

この状態でプレイブックを実行しても、何も起きません(スルーします)。
すでにファイルをコピーしているため、冪等性が保たれたと判断された状態です。
そこで、`sample.html`を少し変更してみましょう。

```{code-block}
:language: html
:caption: sample.htmlの変更例(titleタグの中を変更)

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ドキュメント</title>
</head>
<body>
    
</body>
</html>
```

この状態で再度プレイブックを呼び出すと、ファイルが更新されたことを検知して、`notify`で指定したハンドラーが呼び出されます。結果として、Apacheが再起動されることになります。

このように、なにかのタスクにおける変更点をトリガーとして別のタスクを呼び出せるようになっています。
主な用途としては、設定ファイルの更新に伴うサービスの再起動などが考えられます。
実際にPHP環境の構築においてハンドラー定義が発生することになるので、その際に再度確認しておきましょう。
