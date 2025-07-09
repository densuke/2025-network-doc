import os
import re
import hashlib
import subprocess

SOURCE_DIR = "source"
MERMAID_TEMP_DIR = os.path.join(SOURCE_DIR, ".mermaid_temp")
MERMAID_IMAGES_DIR = os.path.join(SOURCE_DIR, "_images")

def ensure_dirs():
    os.makedirs(MERMAID_TEMP_DIR, exist_ok=True)
    os.makedirs(MERMAID_IMAGES_DIR, exist_ok=True)

def process_mermaid_blocks():
    ensure_dirs()
    
    for root, _, files in os.walk(SOURCE_DIR):
        for file_name in files:
            if file_name.endswith(".md"):
                filepath = os.path.join(root, file_name)
                # Read the file content
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Find all mermaid blocks
                mermaid_blocks = re.findall(r"""`{mermaid}\n(.*?)\n```""", content, re.DOTALL)
                
                if not mermaid_blocks:
                    continue

                for i, block in enumerate(mermaid_blocks):
                    mermaid_hash = hashlib.md5(block.encode("utf-8")).hexdigest()
                    mmd_filepath = os.path.join(MERMAID_TEMP_DIR, f"{mermaid_hash}.mmd")
                    png_filename = f"mermaid_{mermaid_hash}.png"
                    # 出力先をMarkdownファイルと同じディレクトリの _images サブディレクトリに
                    images_dir = os.path.join(root, "_images")
                    os.makedirs(images_dir, exist_ok=True)
                    png_filepath = os.path.join(images_dir, png_filename)

                    # Write mermaid code to a temporary .mmd file
                    with open(mmd_filepath, "w", encoding="utf-8") as f:
                        f.write(block)

                    # Generate PNG if it doesn't exist
                    if not os.path.exists(png_filepath):
                        print(f"Generating {png_filepath}...")
                        try:
                            subprocess.run(
                                ["npm", "run", "mermaid-single-debug"],
                                check=True,
                                capture_output=False,
                                text=True,
                                env={**os.environ, "MMD_FILE": mmd_filepath, "PNG_FILE": png_filepath}
                            )
                            subprocess.run(
                                ["npm", "run", "ch-ldd"],
                                check=True,
                                capture_output=False,
                                text=True,
                                env={**os.environ, "MMD_FILE": mmd_filepath, "PNG_FILE": png_filepath}
                            )
                            subprocess.run(
                                ["npm", "run", "mermaid-single"],
                                check=True,
                                capture_output=True,
                                text=True,
                                env={**os.environ, "MMD_FILE": mmd_filepath, "PNG_FILE": png_filepath}
                            )
                            print(f"Successfully generated {png_filepath}")
                        except subprocess.CalledProcessError as e:
                            print(f"Error generating {png_filepath}: {e.stderr}")
                            continue

# No longer modifying the markdown file content here.
# Sphinx will handle including the images from _images directory.

if __name__ == "__main__":
    process_mermaid_blocks()
