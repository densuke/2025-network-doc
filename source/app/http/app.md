# 簡単なWebアプリケーションを作ってみよう

では、実際に簡単なWebアプリケーションを作ってみましょう。
ここでは、PythonのFlaskというフレームワークを使って、簡単なWebアプリケーションを作成します。

例えば、ユーザー情報が納められたJSONファイルを用意して、その中からユーザーIDに対応するユーザー名を返すAPIを作成してみます。
ディレクトリ(フォルダー)`api-example`を作成し、この中で作業してみましょう。

```{code-block}
:language: bash

$ mkdir api-example
$ cd api-example
$ code --reuse-window . # VSCodeを起動し直す
```

## シンプルなAPIサーバーとテスト

まずはユーザー情報のJSONファイルを用意してみましょう。
手打ちでは少し辛いと思いますので、コピー&ペーストで作成すると良いでしょう。

ファイル名は `users.json` とします。

```{literalinclude} src/api/users.json
:caption: users.json
:language: json
```

つづいて、このJSONファイルを読み込んで情報を返すWebアプリケーションとなります。
ここではFlaskを使ったコードとしてみます。 `app.py` というファイル名で作成してください。

```{literalinclude} src/api/app-simple.py
:caption: app.py
:language: python
```

それでは、実際に動かすためにuvで環境を構築してみましょう。

```{code-block}
:language: bash

$ uv init
$ uv add flask
$ uv run app.py
```

これで別のターミナルをVSCodeで開くと、 http://localhost:5000/ にてアクセスできるようになっています。

```{code-block}
:language: bash

$ curl localhost:5000/users/1
{
  "id": 1,
  "name": "Alice"
}
$ curl localhost:5000/users/42
{
  "error": "User not found"
}
```

## 普通のWebページとして見てみる

そのまままブラウザで http://localhost:5000/users/1 にアクセスしてみると、JSONのまま表示されることがわかります.
その一方で、ブラウザで http://localhost:5000/ にアクセスしても、404 Not found の表示となってしまいます。そこで、トップページを用意して、ちょっとしたフォームにより指定ユーザーIDの情報が出せるようなページを作ってみます。

```{literalinclude} src/api/index.html
:caption: index.html
:language: html
```

そして、`app.py`に手を入れて、トップページが出るようにしてみましょう。

```{literalinclude} src/api/app.py
:language: python
:caption: app.py
:diff: src/api/app-simple.py
```

一度`uv run`している所を止めて、再度起動してみましょう。
今度は http://localhost:5000/ にアクセスすると、トップページが表示されることがわかります。
ユーザーID(1,2,3)や存在しない番号(42)を入れて送信すると、結果が出力されるのがわかると思います。

