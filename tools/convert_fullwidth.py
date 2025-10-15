#!/usr/bin/env python3
"""
Convert full-width punctuation to ASCII equivalents in .md files under /app/source and top-level md files.
Skips fenced code blocks (```), indented code blocks, and preserves inline code (text within backticks).
Excludes these characters from conversion: U+3002 (。), U+3001 (、), full-width corner quotes 「」 and 『』, and full-width tilde 〜.

Run from repo root: python3 tools/convert_fullwidth.py
"""
import sys
from pathlib import Path
import re

# Mapping of fullwidth punctuation to ASCII
MAPPING = {
    '！': '!', '＂': '"', '＃': '#', '＄': '$', '％': '%', '＆': '&', '＇': "'",
    '（': '(', '）': ')', '＊': '*', '＋': '+', '，': ',', '－': '-', '．': '.',
    '／': '/', '：': ':', '；': ';', '＜': '<', '＝': '=', '＞': '>', '？': '?',
    '＠': '@', '［': '[', '＼': '\\', '］': ']', '＾': '^', '＿': '_', '｀': '`',
    '｛': '{', '｜': '|', '｝': '}',
}
# Exclusions (do not convert these)
EXCLUDE_CHARS = set(['。', '、', '「', '」', '『', '』', '〜'])

# Build pattern for characters to replace
replace_chars = ''.join(re.escape(ch) for ch in MAPPING.keys() if ch not in EXCLUDE_CHARS)
pattern = re.compile('[' + replace_chars + ']') if replace_chars else None

# Find files
root = Path('/app')
files = list(root.rglob('*.md'))
# Also include top-level md files in repo root
files += [p for p in root.glob('*.md') if p not in files]

changed_files = []

for fp in files:
    try:
        text = fp.read_text(encoding='utf-8')
    except Exception:
        continue
    orig = text
    out_lines = []
    in_fence = False
    fence_marker = None
    in_dollarmath = False
    for line in text.splitlines(keepends=True):
        # detect fenced code blocks ``` or ```lang or ```{...}
        m = re.match(r'^(`{3,}|~{3,})(.*)\n?$', line)
        if m:
            fence = m.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = fence
                out_lines.append(line)
                continue
            else:
                # closing fence matches any fence marker length
                in_fence = False
                fence_marker = None
                out_lines.append(line)
                continue
        if in_fence:
            out_lines.append(line)
            continue
        # skip indented code blocks (4 spaces or a tab)
        if re.match(r'^(    |\t)', line):
            out_lines.append(line)
            continue
        # detect $$ math block start/end
        if line.strip().startswith('$$'):
            if not in_dollarmath:
                in_dollarmath = True
                out_lines.append(line)
                continue
            else:
                in_dollarmath = False
                out_lines.append(line)
                continue
        if in_dollarmath:
            out_lines.append(line)
            continue
        # handle inline code: split by backticks groups and only replace on even segments
        parts = re.split(r'(`+)', line)
        for i in range(0, len(parts), 2):
            seg = parts[i]
            if pattern:
                def repl(m):
                    ch = m.group(0)
                    # if excluded, keep
                    if ch in EXCLUDE_CHARS:
                        return ch
                    return MAPPING.get(ch, ch)
                seg = pattern.sub(repl, seg)
            parts[i] = seg
        new_line = ''.join(parts)
        out_lines.append(new_line)
    new_text = ''.join(out_lines)
    if new_text != orig:
        fp.write_text(new_text, encoding='utf-8')
        changed_files.append(str(fp.relative_to(root)))

print('Modified files:')
for p in changed_files:
    print(p)
print('\nTotal modified:', len(changed_files))
