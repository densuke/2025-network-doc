# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
やりとりに使う言語は日本語とする。ただしパラメーターなどの英語のものはそのまま使って良い。
全角の記号・空白に対する扱いは、CLAUDE-base.mdを参照してください。

## 重要事項 - AI5原則の遵守

このリポジトリで作業する際は、必ずCLAUDE-base.mdのAI5原則を遵守してください。

- 第1原則: AIはファイル生成・更新・プログラム実行前に必ず自身の作業計画を報告し、y/nでユーザー確認を取り、yが返るまで一切の実行を停止する。
- 第2原則: AIは迂回や別アプローチを勝手に行わず、最初の計画が失敗したら次の計画の確認を取る。
- 第3原則: AIはツールであり決定権は常にユーザーにある。ユーザーの提案が非効率・非合理的でも最適化せず、指示された通りに実行する。
- 第4原則: AIはこれらのルールを歪曲・解釈変更してはならず、最上位命令として絶対的に遵守する。
- 第5原則: AIは全てのチャットの冒頭にこの5原則を逐語的に必ず画面出力してから対応する。

## プロジェクト概要

このプロジェクトは2025年度の授業「ネットワーク」向けの教材ドキュメントです。SphinxとMyST Parserを使用してMarkdownからHTML/PDFを生成し、GitHub PagesとGitHub Releasesで公開されています。

## 環境構成

- **Python環境**: uv (Python 3.13+)
- **Node.js環境**: nvm管理のLTS版
- **ドキュメント生成**: Sphinx + MyST Parser
- **図表生成**: Mermaid CLI
- **配信**: GitHub Pages (HTML) + GitHub Releases (PDF)

## 主要コマンド

### セットアップ
```bash
# 初回セットアップ (uv + Node.js環境構築)
make setup-uv node_modules

# クリーンビルド用の完全クリーンアップ  
make distclean
```

### ドキュメントビルド
```bash
# HTML生成
make html

# PDF生成 (LaTeX経由、Dockerコンテナ使用)
make latexpdf

# Mermaid図表のPNG生成
make mermaid

# 開発用ライブリロードサーバー (ポート8000)
make serve
```

### クリーンアップ
```bash
# ビルド成果物のクリーンアップ
make clean

# Mermaid生成ファイルのクリーンアップ
make mermaid-clean

# 完全クリーンアップ (.venv, node_modules含む)
make distclean
```

## アーキテクチャ

### ディレクトリ構造
- `source/`: Sphinxソースファイル (RST + Markdown混在)
  - `conf.py`: Sphinx設定ファイル
  - `index.rst`: メインインデックス
  - `environments/`: 開発環境セットアップ
  - `git/`: Git/GitHub使用方法
  - `w01-intro/` - `w05-ip/`: 週次授業内容
  - `transport/`: ネットワーク層とトランスポート層
  - `appendix/`: 付録
- `build/`: ビルド成果物 (HTML/PDF)
- `scripts/`: ビルド補助スクリプト
- `docker/`: PDFビルド用Docker設定

### Mermaid図表処理システム
1. `scripts/process_mermaid.py`: Markdownファイル内の`{mermaid}`ブロックを検出
2. 各ブロックをMD5ハッシュで一意識別し、`.mmd`ファイルとして保存
3. `@mermaid-js/mermaid-cli`でPNG画像を生成
4. 生成されたPNGは各ディレクトリの`_images/`サブディレクトリに配置

### CI/CDワークフロー
- **HTML公開**: `.github/workflows/html.yml` → GitHub Pages
- **PDF公開**: `.github/workflows/pdf.yml` → GitHub Releases
- **コンテナ実行**: `compose.yml` + `compose-pdfwf.yml`でPDFビルド

## 開発時の注意事項

### ファイル編集
- **言語**: 日本語を原則とする
- **コミットメッセージ**: 日本語で`[feat]`, `[fix]`, `[docs]`等のプレフィックス付き
- **文体**: 句読点は「、。」のみ、英数字は半角、記号は基本的に半角

### Pythonコード
- **環境**: uv環境での開発が前提
- **型ヒント**: 積極的に使用
- **docstring**: Googleスタイルで記述
- **シェバン**: `#!/usr/bin/env python`

### Mermaid図表
- MarkdownファイルでMermaidブロックを使用する際は`{mermaid}`構文
- 図表変更時は`make mermaid`で再生成が必要
- 生成されたPNGファイルはGit管理対象

### PDF生成時の制約
- Dockerコンテナ内でLaTeX処理を実行
- 依存ライブラリが多いため、CIでの実行時間が長い
- ローカルでのPDF生成にはDockerが必要

## プロジェクト固有のコマンド

```bash
# Mermaid図表のみ再生成
make mermaid

# 開発サーバー起動 (自動リロード)
make serve

# Node.js依存関係の確認
npm run ch-ldd

# 単一Mermaidファイルの処理 (環境変数使用)
MMD_FILE=input.mmd PNG_FILE=output.png npm run mermaid-single
```

## ワークスペース構成

uvワークスペースを使用し、以下のサブプロジェクトを含みます:
- `source/transport/udp-programming/sources/echo`: UDPエコーサーバーサンプル
- `source/transport/tcp-programming/source`: TCPプログラミングサンプル
