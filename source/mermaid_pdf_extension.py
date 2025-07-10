import os
import hashlib
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


class MermaidDirective(SphinxDirective):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'alt': directives.unchanged,
        'align': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged,
        'scale': directives.unchanged,
    }

    def run(self):
        # Get the mermaid code from the directive content
        mermaid_code = "\n".join(self.content)
        
        # Calculate hash for the mermaid code
        mermaid_hash = hashlib.md5(mermaid_code.encode("utf-8")).hexdigest()
        
        # Construct the image filename based on the hash
        png_filename = f"mermaid_{mermaid_hash}.png"
        
        # The path Sphinx will look for the image relative to the source directory
        # Since we put images in source/_images, the path is _images/mermaid_hash.png
        image_path = os.path.join("_images", png_filename)

        # Create an image node
        image_node = nodes.image(uri=image_path, **self.options)
        
        return [image_node]

def setup(app):
    app.add_directive("mermaid", MermaidDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
