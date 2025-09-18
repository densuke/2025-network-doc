# 演習: Base64エンコーディングについて

Base64については前述の通りですが、かなり簡単な実装のため、ここではPythonで確認してみましょう。

## ライブラリによる変換

Pythonでは、標準で`base64`というモジュールが用意されており、インポートすることでBase64のエンコード・デコードが可能です。

```python
import base64
```

Base64でエンコードするには、対象となる文字列はバイト列でないといけません。そのため、文字列をバイト列に変換する必要があります。

```python
# 文字列をバイト列に変換
byte_string = "hello, world".encode("utf-8")
```

このバイト列をBase64でエンコードするには、`base64.b64encode`関数を使います。

```python
# Base64でエンコード
b64_encoded = base64.b64encode(byte_string)
print(b64_encoded)  # b'aGVsbG8sIHdvcmxk'
```

逆にデコードするときは、`base64.b64decode`関数を使います。
渡すのはエンコードされた文字列であり、型はバイト列である必要があります。

```python
# Base64でデコード
decoded_bytes = base64.b64decode(b64_encoded)
print(decoded_bytes)  # b'hello, world'
```
デコードされたバイト列を文字列に戻すには、`decode`メソッドを使います。

```python
# バイト列を文字列に変換
decoded_string = decoded_bytes.decode("utf-8")
print(decoded_string)  # hello, world
```
これらをまとめると、以下のようになります。

```{literalinclude} src/b64/b64-encode-libonly.py
:language: python
:caption: b64-encode.py ※ライブラリのみ使用
```

```{literalinclude} src/b64/b64-decode.py
:language: python
:caption: b64-decode.py
```

## アルゴリズムの実装

Base64のアルゴリズムは非常にシンプルなので、自分で実装することもかなり簡単です。 以下は、Base64のエンコードを自分で実装した例です。

```{literalinclude} src/b64/b64-encode.py
:language: python
:caption: b64-encode.py ※アルゴリズムを自前で実装(抜粋)
:linenos:
:lines: 26-54
```

要所の解説です。

```python
bits = "".join(format(byte, "08b") for byte in s)
```
ここでは、バイト列をビット列に変換しています。各バイトを8ビットの2進数に変換し、それらを連結しています。
bitsは0か1の文字列になります。

```
(変換例)
0110100001101111011001110110010101101000011011110110011101100101
```
これを6ビットずつに区切ります。

```python
for i in range(0, len(bits), 6): # 0,6,12, ...
        chunk = bits[i : i + 6] # 6ビット分取得する
        if len(chunk) < 6:  # 足りないときは末尾に0をパディング
            chunk += "0" * (6 - len(chunk))  # パディング
```

変換先となる文字列は、Base64では以下のように定義されています(英字52文字+数字10文字+記号2文字)。

```
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

得られたchunkを10進数に変換し、その値を上記の文字列から取り出して連結します。

```python
        index = int(chunk, 2)
        encoded += base64_chars[index]
```

最後に、エンコード後の文字列の長さが4の倍数になるように、`=`でパディングします。

```python
    padding = (3 - len(s) % 3) % 3
    encoded += "=" * padding
```

こうすることで、Base64のエンコードが完了します。
