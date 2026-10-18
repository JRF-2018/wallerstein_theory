#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
conv2md.py -- JRF と AI の会話ログ（テキスト）を公開用 Markdown に変換する

- 発言は行頭の「jrf> 」「Grok> 」「Gemini> 」などで始まる。
- JRF の発言は Markdown の特殊文字（[ ] * _ ` < # など）をエスケープし、改行を保つ。URL はそのまま。
- AI の回答は blockquote にする。発言のまとまりの間には二重の横線を入れる。
- 数式: \\[ … \\] は $$ … $$ に、\\( … \\) は $ … $ に変える。数式内の * は \\ast に変える
  （GitHub の Markdown が強調と誤解しないため）。

使い方: python3 conv2md.py INPUT.txt OUTPUT.md
"""
import re
import sys

SPEAKER_RE = re.compile(r'^(jrf|Grok|Gemini|Claude|ChatGPT)> ?(.*)$')
URL_RE = re.compile(r'https?://[^\s<>《》「」]+')


def escape_plain(s):
    """JRF の発言用: URL 以外の Markdown 特殊文字をエスケープする"""
    out, pos = [], 0
    for m in URL_RE.finditer(s):
        out.append(_esc(s[pos:m.start()]))
        out.append('<' + m.group(0) + '>')
        pos = m.end()
    out.append(_esc(s[pos:]))
    t = ''.join(out)
    # 行頭の #, >, -, +, 数字. は見出し・引用・リストと誤解されるのでエスケープ
    t = re.sub(r'^(\s*)([#>+\-])', r'\1\\\2', t)
    t = re.sub(r'^(\s*\d+)\.', r'\1\\.', t)
    return t


def _esc(s):
    return re.sub(r'([\\`*_\[\]<>|~])', r'\\\1', s)


def convert_math(text):
    def disp(m):
        body = m.group(1).replace('*', r'\ast ')
        return '$$' + body.strip() + '$$'

    def inl(m):
        body = m.group(1).replace('*', r'\ast ')
        return '$' + body.strip() + '$'

    text = re.sub(r'\\\[(.*?)\\\]', disp, text, flags=re.S)
    text = re.sub(r'\\\((.*?)\\\)', inl, text, flags=re.S)
    # 既存の $$…$$, $…$ の中の * も置き換える（コードブロックの外のみ）
    parts = re.split(r'(```.*?```)', text, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'\$\$(.*?)\$\$', lambda m: '$$' + m.group(1).replace('*', r'\ast ') + '$$', parts[i], flags=re.S)
        parts[i] = re.sub(r'(?<!\$)\$([^$\n]+?)\$(?!\$)', lambda m: '$' + m.group(1).replace('*', r'\ast ') + '$', parts[i])
    return ''.join(parts)


def parse(text):
    lines = text.splitlines()
    header, blocks, cur = [], [], None
    for ln in lines:
        m = SPEAKER_RE.match(ln)
        if m:
            cur = {'who': m.group(1), 'lines': [m.group(2)]}
            blocks.append(cur)
        elif cur is None:
            header.append(ln)
        else:
            cur['lines'].append(ln)
    for b in blocks:
        while b['lines'] and not b['lines'][-1].strip():
            b['lines'].pop()
    return [h.strip() for h in header if h.strip()], blocks


def render(header, blocks):
    out = []
    if header:
        out.append('# ' + header[0])
        for h in header[1:]:
            out.append('')
            out.append('*' + h + '*')
        out.append('')
        out.append('（会話ログの原文を公開用に整形したもの。JRF の発言は原文のまま、AI の回答は引用で示す。'
                   'AI の回答には誤りが含まれうる。）')
        out.append('')
    first = True
    for b in blocks:
        if b['who'] == 'jrf':
            if not first:
                out += ['', '---', '', '---', '']
            first = False
            out.append('**JRF>**')
            out.append('')
            for ln in b['lines']:
                out.append(escape_plain(ln) + '  ' if ln.strip() else '')
            out.append('')
        else:
            out.append(f'**{b["who"]}>**')
            out.append('')
            body = convert_math('\n'.join(b['lines']))
            for ln in body.split('\n'):
                out.append('> ' + ln if ln.strip() else '>')
            out.append('')
    return '\n'.join(out).rstrip() + '\n'


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding='utf-8') as f:
        header, blocks = parse(f.read())
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(render(header, blocks))


if __name__ == '__main__':
    main()
