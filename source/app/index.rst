.. ネットワーク(2025)関連資料 documentation master file, created by
   sphinx-quickstart on Wed Apr  2 08:42:26 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

アプリケーション層
========================================

アプリケーション層は、ユーザーが直接操作するアプリケーションと、それを支えるネットワークサービスとのインターフェースを提供します。
非常に多くのプロトコルが存在するため、この中では代表的なもののみ取りあげています。

.. todo::
    - http
    - TLS/SSLについて(厳密にはアプリケーション層ではないが、重要なため)
    - smtpというよりはメール周辺
    - その他必要に応じて

.. toctree::
    :maxdepth: 1
    :caption: 目次:

    http/index.rst
    smtp/index.rst
    