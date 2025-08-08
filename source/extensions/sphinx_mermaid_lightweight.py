#!/usr/bin/env python
"""
Lightweight Mermaid Extension for Sphinx

Playwright/Puppeteerへの依存性を排除したMermaid図表レンダリング拡張
3段階フォールバック方式:
1. mermaid.ink API (プライマリ)
2. Kroki API (セカンダリ)
3. ローカルmermaid-cli (フォールバック)

Author: Claude Code Assistant
License: Compatible with project license
"""

import base64
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.builders.latex import LaTeXBuilder
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

# ロガーの設定
logger = logging.getLogger(__name__)


class MermaidLightweightDirective(SphinxDirective):
    """
    軽量Mermaidディレクティブ

    {mermaid}ブロックを処理し、外部APIまたはローカルツールで
    PDF/SVG/PNGを生成する。
    """
    
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        'caption': directives.unchanged,
        'name': directives.unchanged,
        'class': directives.class_option,
        'format': directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        """
        ディレクティブの実行
        
        Returns:
            生成されたノードのリスト
        """
        # Mermaidコードの取得
        mermaid_code = '\n'.join(self.content)
        if not mermaid_code.strip():
            logger.warning('Empty mermaid directive content', location=self.get_location())
            return []

        # ノード作成
        node = mermaid_node()
        node['code'] = mermaid_code
        node['options'] = self.options
        node['lineno'] = self.lineno
        
        # キャプションの処理
        if 'caption' in self.options:
            caption_node = nodes.caption(self.options['caption'], self.options['caption'])
            node += caption_node

        return [node]


class mermaid_node(nodes.General, nodes.Inline, nodes.Element):
    """Mermaid図表ノード"""
    pass


class MermaidRenderer:
    """
    Mermaid図表レンダラー
    
    3段階フォールバック方式でMermaid図表を生成:
    1. mermaid.ink API
    2. Kroki API  
    3. ローカルmermaid-cli
    """
    
    def __init__(self, app: Sphinx):
        self.app = app
        self.config = app.config
        self.env = app.env
        
        # キャッシュディレクトリの設定
        self.cache_dir = Path(app.outdir) / '_mermaid_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_hash(self, content: str) -> str:
        """コンテンツのハッシュを生成"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def get_cache_path(self, content_hash: str, format: str) -> Path:
        """キャッシュファイルのパスを取得"""
        return self.cache_dir / f"mermaid-{content_hash}.{format}"
    
    def is_cached(self, content_hash: str, format: str) -> bool:
        """キャッシュの存在確認"""
        cache_path = self.get_cache_path(content_hash, format)
        return cache_path.exists()
    
    def crop_pdf_margins(self, pdf_data: bytes) -> Optional[bytes]:
        """
        PDFの余白をクロッピング
        
        Args:
            pdf_data: 元のPDFデータ
            
        Returns:
            クロッピングされたPDFデータ、失敗時はNone
        """
        try:
            # pdfcropコマンドまたはgs (Ghostscript) を使用してPDFをクロッピング
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_file:
                input_file.write(pdf_data)
                input_path = input_file.name
            
            output_path = f"{input_path}.cropped.pdf"
            
            try:
                # まずpdfcropを試行
                result = subprocess.run([
                    'pdfcrop', input_path, output_path
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    with open(output_path, 'rb') as f:
                        cropped_data = f.read()
                    logger.info("PDF cropped successfully using pdfcrop")
                    return cropped_data
                
                # pdfcropが失敗した場合、Ghostscriptを使用
                logger.info("pdfcrop failed, trying Ghostscript")
                result = subprocess.run([
                    'gs', '-sDEVICE=pdfwrite', '-dNOPAUSE', '-dBATCH', '-dSAFER',
                    '-dUseCropBox', '-dUseArtBox', '-dUseTrimBox', '-dUseBleedBox',
                    f'-sOutputFile={output_path}', input_path
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    with open(output_path, 'rb') as f:
                        cropped_data = f.read()
                    logger.info("PDF cropped successfully using Ghostscript")
                    return cropped_data
                
            finally:
                # 一時ファイル削除
                for path in [input_path, output_path]:
                    if os.path.exists(path):
                        os.unlink(path)
            
        except Exception as e:
            logger.warning(f"PDF cropping failed: {e}")
        
        return None
    
    def render_with_mermaid_ink(self, mermaid_code: str, format: str = 'pdf') -> Optional[bytes]:
        """
        mermaid.ink APIを使用してレンダリング
        
        Args:
            mermaid_code: Mermaidコード
            format: 出力フォーマット (pdf, svg, png)
            
        Returns:
            レンダリングされた画像データ、失敗時はNone
        """
        try:
            # Base64エンコード
            encoded_code = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('ascii')
            
            # API URL構築
            if format == 'pdf':
                url = f"https://mermaid.ink/pdf/{encoded_code}"
            elif format == 'svg':
                url = f"https://mermaid.ink/svg/{encoded_code}"
            else:  # png
                url = f"https://mermaid.ink/img/{encoded_code}"
            
            logger.info(f"Rendering Mermaid via mermaid.ink: {format}")
            
            # APIリクエスト
            request = Request(url)
            request.add_header('User-Agent', 'sphinx-mermaid-lightweight/1.0')
            
            with urlopen(request, timeout=30) as response:
                if response.status == 200:
                    raw_data = response.read()
                    
                    # PDFの場合は余白をクロッピング
                    if format == 'pdf' and getattr(self.config, 'mermaid_crop_pdf', True):
                        cropped_data = self.crop_pdf_margins(raw_data)
                        if cropped_data:
                            logger.info("Applied PDF cropping for mermaid.ink output")
                            return cropped_data
                        else:
                            logger.info("PDF cropping failed, using original PDF")
                    
                    return raw_data
                else:
                    logger.warning(f"mermaid.ink API returned status {response.status}")
                    return None
                    
        except (HTTPError, URLError, Exception) as e:
            logger.warning(f"mermaid.ink API failed: {e}")
            return None
    
    def render_with_kroki(self, mermaid_code: str, format: str = 'pdf') -> Optional[bytes]:
        """
        Kroki APIを使用してレンダリング
        
        Args:
            mermaid_code: Mermaidコード
            format: 出力フォーマット (pdf, svg, png)
            
        Returns:
            レンダリングされた画像データ、失敗時はNone
        """
        try:
            # Kroki API エンドポイント
            kroki_url = getattr(self.config, 'mermaid_kroki_url', 'https://kroki.io')
            
            # Base64エンコード
            encoded_code = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('ascii')
            
            # API URL構築
            url = f"{kroki_url}/mermaid/{format}/{encoded_code}"
            
            logger.info(f"Rendering Mermaid via Kroki: {format}")
            
            # APIリクエスト
            request = Request(url)
            request.add_header('User-Agent', 'sphinx-mermaid-lightweight/1.0')
            
            with urlopen(request, timeout=30) as response:
                if response.status == 200:
                    return response.read()
                else:
                    logger.warning(f"Kroki API returned status {response.status}")
                    return None
                    
        except (HTTPError, URLError, Exception) as e:
            logger.warning(f"Kroki API failed: {e}")
            return None
    
    def render_with_mermaid_cli(self, mermaid_code: str, format: str = 'pdf') -> Optional[bytes]:
        """
        ローカルmermaid-cliを使用してレンダリング
        
        Args:
            mermaid_code: Mermaidコード
            format: 出力フォーマット (pdf, svg, png)
            
        Returns:
            レンダリングされた画像データ、失敗時はNone
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as mmd_file:
                mmd_file.write(mermaid_code)
                mmd_path = mmd_file.name
            
            output_path = f"{mmd_path}.{format}"
            
            try:
                # mermaid-cli実行
                cmd = ['mmdc', '-i', mmd_path, '-o', output_path]
                if format == 'pdf':
                    cmd.extend(['--pdfFit'])
                
                logger.info(f"Rendering Mermaid via mermaid-cli: {format}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0 and os.path.exists(output_path):
                    with open(output_path, 'rb') as f:
                        return f.read()
                else:
                    logger.warning(f"mermaid-cli failed: {result.stderr}")
                    return None
                    
            finally:
                # 一時ファイル削除
                for path in [mmd_path, output_path]:
                    if os.path.exists(path):
                        os.unlink(path)
                        
        except Exception as e:
            logger.warning(f"mermaid-cli execution failed: {e}")
            return None
    
    def render(self, mermaid_code: str, format: str = 'pdf') -> Optional[Path]:
        """
        Mermaid図表をレンダリング
        
        Args:
            mermaid_code: Mermaidコード
            format: 出力フォーマット
            
        Returns:
            生成されたファイルのパス、失敗時はNone
        """
        # コンテンツハッシュ生成
        content_hash = self.generate_hash(mermaid_code)
        
        # キャッシュ確認
        cache_path = self.get_cache_path(content_hash, format)
        if self.is_cached(content_hash, format):
            # デバッグ情報: キャッシュファイルのサイズ
            file_size = cache_path.stat().st_size
            logger.info(f"Using cached Mermaid: {cache_path.name} (size: {file_size} bytes)")
            return cache_path
        
        # フォールバック方式でレンダリング試行
        renderers = [
            ('mermaid.ink', self.render_with_mermaid_ink),
            ('Kroki', self.render_with_kroki),
            ('mermaid-cli', self.render_with_mermaid_cli)
        ]
        
        for renderer_name, renderer_func in renderers:
            # 設定による無効化チェック
            if renderer_name == 'mermaid.ink' and not getattr(self.config, 'mermaid_use_ink', True):
                continue
            if renderer_name == 'Kroki' and not getattr(self.config, 'mermaid_use_kroki', True):
                continue
            if renderer_name == 'mermaid-cli' and not getattr(self.config, 'mermaid_use_cli', True):
                continue
            
            # レンダリング試行
            result = renderer_func(mermaid_code, format)
            if result:
                # キャッシュに保存
                with open(cache_path, 'wb') as f:
                    f.write(result)
                # デバッグ情報: 生成されたファイルのサイズ
                file_size = len(result)
                logger.info(f"Successfully rendered Mermaid via {renderer_name}: {cache_path.name} (size: {file_size} bytes)")
                return cache_path
        
        # 全てのレンダラーが失敗
        logger.error(f"All Mermaid renderers failed for hash {content_hash}")
        return None


def render_mermaid_html(self, node: mermaid_node) -> None:
    """HTML出力用のMermaidレンダリング"""
    mermaid_code = node['code']
    
    # HTMLではJavaScript版Mermaidを使用
    html = f'''
    <div class="mermaid">
{mermaid_code}
    </div>
    '''
    
    self.body.append(html)

def depart_mermaid_html(self, node: mermaid_node) -> None:
    """HTML出力用のMermaid終了処理"""
    pass


def render_mermaid_latex(self, node: mermaid_node) -> None:
    """LaTeX/PDF出力用のMermaidレンダリング"""
    # LaTeXTranslatorからbuilderを経由してアプリケーションインスタンスを取得
    app = self.builder.app
    renderer = MermaidRenderer(app)
    mermaid_code = node['code']
    
    # LaTeX出力用フォーマットを決定（PDFまたはPNG）
    latex_format = getattr(app.config, 'mermaid_latex_format', 'pdf')
    
    # 画像ファイル生成
    image_path = renderer.render(mermaid_code, latex_format)
    
    if image_path:
        # 相対パス計算
        rel_path = os.path.relpath(image_path, self.builder.outdir)
        
        # Mermaid図表用のスマートサイジング（グローバル設定をバイパス）
        # adjustboxの代わりに直接includegraphicsでスマート制御
        max_width = getattr(app.config, "mermaid_max_width", "0.8\\textwidth")
        max_height = getattr(app.config, "mermaid_max_height", "0.6\\textheight")
        
        # figure環境で[H]オプション+adjustboxを使用してスマート調整
        latex_code = f'''\\begin{{figure}}[H]
\\centering
\\adjustbox{{max width={max_width},max height={max_height},center}}{{\\includegraphics{{{rel_path}}}}}  
\\end{{figure}}'''
        
        self.body.append(latex_code)
    else:
        # フォールバック: エラーメッセージ
        error_msg = f"% Mermaid rendering failed\\n% Code: {mermaid_code[:50]}..."
        self.body.append(error_msg)

def depart_mermaid_latex(self, node: mermaid_node) -> None:
    """LaTeX/PDF出力用のMermaid終了処理"""
    pass


def setup(app: Sphinx) -> Dict[str, Any]:
    """
    拡張のセットアップ
    
    Args:
        app: Sphinxアプリケーションインスタンス
        
    Returns:
        拡張メタデータ
    """
    # ディレクティブ登録
    app.add_directive('mermaid', MermaidLightweightDirective)
    app.add_node(mermaid_node, 
                 html=(render_mermaid_html, depart_mermaid_html), 
                 latex=(render_mermaid_latex, depart_mermaid_latex))
    
    # 設定値の追加
    app.add_config_value('mermaid_use_ink', True, 'env')
    app.add_config_value('mermaid_use_kroki', True, 'env')
    app.add_config_value('mermaid_use_cli', True, 'env')
    app.add_config_value('mermaid_kroki_url', 'https://kroki.io', 'env')
    
    # LaTeX画像サイズ制御の設定値
    app.add_config_value('mermaid_max_width', '\\textwidth', 'env')
    app.add_config_value('mermaid_max_height', '0.8\\textheight', 'env')
    
    # 追加設定値
    app.add_config_value('mermaid_latex_format', 'pdf', 'env')  # LaTeX出力フォーマット (pdf/png)
    app.add_config_value('mermaid_crop_pdf', True, 'env')      # PDFクロッピング有効/無効
    
    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
