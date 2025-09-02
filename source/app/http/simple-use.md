# HTTPを簡単に使うには

HTTPをお手軽に使う方法として、Webサーバーを導入することもありますが、Webサーバーをお手軽に立てる方法として、PythonのHTTPサーバーモジュールを使う方法があります。
Pythonの標準モジュールでは`http`が存在しています。この中に含まれるモジュールを使うことで、お手軽Webサーバーを構築できます。

## 簡易Webサーバーの起動

```{code-block}
:language: bash

$ echo 'Hello, Simple World!' > index.html
$ python -m http.server # localhost:8000 でサーバーが起動する
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

サーバーが起動したら、別ターミナルを開いて接続テストを行います。

## cURLを使ったHTTPリクエスト

cURLは、コマンドラインからHTTPリクエストを送信するためのツールです。Webブラウザーを使わずに、HTTPの仕組みを直接確認できるため、学習や開発に非常に便利です。

### 基本的なGETリクエスト

```{code-block}
:language: bash

$ curl http://localhost:8000/
Hello, Simple World!
```

この例では、ルートディレクトリ(`/`)にアクセスしており、先ほど作成した`index.html`の内容が返されています。

### ヘッダー情報を含む詳細な出力

cURLで`-v`オプション(verboseモード)を使うと、リクエストとレスポンスの詳細を確認できます。

```{code-block}
:language: bash

$ curl -v http://localhost:8000/
* Trying 127.0.0.1:8000...
* Connected to localhost (127.0.0.1) port 8000
> GET / HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/8.7.1
> Accept: */*
>
< HTTP/1.0 200 OK
< Server: SimpleHTTP/0.6 Python/3.13.0
< Date: Mon, 01 Sep 2025 12:34:56 GMT
< Content-type: text/html
< Content-Length: 21
< Last-Modified: Mon, 01 Sep 2025 12:30:00 GMT
<
Hello, Simple World!
```

### レスポンスヘッダーの理解

上記の出力で、`<`で始まる行がサーバーからのレスポンスヘッダーです。各ヘッダーの意味を理解しましょう。

- `HTTP/1.0 200 OK`: HTTPバージョンとステータスコード(200は成功を意味)
- `Server: SimpleHTTP/0.6 Python/3.13.0`: サーバーソフトウェアの種類とバージョン
- `Date`: レスポンスが生成された日時
- `Content-type: text/html`: レスポンスボディのデータ形式
- `Content-Length: 21`: レスポンスボディのバイト数
- `Last-Modified`: ファイルの最終更新日時

### ヘッダーのみ取得

レスポンスヘッダーだけを確認したい場合は、`-I`オプション(HEAD メソッド)を使用します。

```{code-block}
:language: bash

$ curl -I http://localhost:8000/
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.13.0
Date: Mon, 01 Sep 2025 12:34:56 GMT
Content-type: text/html
Content-Length: 21
Last-Modified: Mon, 01 Sep 2025 12:30:00 GMT
```

### 存在しないファイルへのアクセス

存在しないファイルにアクセスした場合の動作も確認してみましょう。

```{code-block}
:language: bash

$ curl -v http://localhost:8000/notfound.html
* Trying 127.0.0.1:8000...
* Connected to localhost (127.0.0.1) port 8000
> GET /notfound.html HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/8.7.1
> Accept: */*
>
< HTTP/1.0 404 Not Found
< Server: SimpleHTTP/0.6 Python/3.13.0
< Date: Mon, 01 Sep 2025 12:35:30 GMT
< Content-type: text/html;charset=utf-8
< Content-Length: 469
<
<!DOCTYPE HTML>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Error response</title>
</head>
<body>
<h1>Error response</h1>
<p>Error code: 404</p>
<p>Message: File not found.</p>
<p>Error code explanation: HTTPStatus.NOT_FOUND - Nothing matches the given URI.</p>
</body>
</html>
```

この場合、ステータスコードが`404 Not Found`になり、エラーページが返されることがわかります。

## より実践的な例

### 複数ファイルの用意

実際のWebサイトのように、複数のファイルを用意して動作を確認してみましょう。

```{code-block}
:language: bash

$ mkdir css images
$ echo '<link rel="stylesheet" href="css/style.css">' > index.html
$ echo '<h1>Welcome to My Site</h1>' >> index.html
$ echo '<img src="images/logo.png" alt="Logo">' >> index.html

$ echo 'h1 { color: blue; }' > css/style.css

# 画像ファイルの代わりにテキストファイルを配置(デモ用)
$ echo 'This is a placeholder for an image' > images/logo.png
```

### 異なるContent-Typeの確認

CSSファイルにアクセスした場合のContent-Typeを確認してみましょう。

```{code-block}
:language: bash

$ curl -I http://localhost:8000/css/style.css
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.13.0
Date: Mon, 01 Sep 2025 12:40:00 GMT
Content-type: text/css
Content-Length: 18
Last-Modified: Mon, 01 Sep 2025 12:38:00 GMT
```

ファイル拡張子に応じて、適切な`Content-type`が設定されていることがわかります。

### ディレクトリリスティング

ディレクトリにアクセスした場合の動作も確認してみましょう。

```{code-block}
:language: bash

$ curl http://localhost:8000/css/
<!DOCTYPE HTML>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Directory listing for /css/</title>
</head>
<body>
<h1>Directory listing for /css/</h1>
<hr>
<ul>
<li><a href="style.css">style.css</a></li>
</ul>
<hr>
</body>
</html>
```

PythonのHTTPサーバーは、ディレクトリ内のファイル一覧を自動的に表示する機能があります。

## サーバーの停止

確認できたら、簡易サーバーを起動した端末にて`Ctrl-C`で停止しておきましょう。

```{code-block}
:language: bash

^C
Keyboard interrupt received, exiting.
```

## まとめ

この章では以下について学習しました:

- PythonのHTTPサーバーモジュールを使った簡易Webサーバーの起動
- cURLを使ったHTTPリクエストの送信方法
- HTTPレスポンスヘッダーの読み方と意味
- ステータスコード(200、404)の実際の動作
- ファイル種類に応じたContent-Typeの違い
- ディレクトリリスティング機能

これらの基本的な操作を理解することで、HTTPプロトコルの動作をより具体的に把握できるようになります。

