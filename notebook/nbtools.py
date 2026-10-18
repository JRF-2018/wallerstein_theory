# -*- coding: utf-8 -*-
"""IPYNB を組み立てるための小さな道具（nbformat を使う）"""
import os
import nbformat
from nbformat.v4 import new_markdown_cell, new_code_cell, new_notebook

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CELLS = []


def md(text):
    CELLS.append(new_markdown_cell(text.strip('\n')))


def code(src, tags=()):
    c = new_code_cell(src.strip('\n'))
    if tags:
        c.metadata['tags'] = list(tags)
    CELLS.append(c)


def writefile(path, append=False, lines=None):
    """リポジトリの実物のファイルを %%writefile セルとして載せる（本文とファイルが常に一致する）"""
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        text = f.read()
    if lines is not None:
        text = ''.join(text.splitlines(True)[lines[0]:lines[1]])
    flag = ' -a' if append else ''
    CELLS.append(new_code_cell(f'%%writefile{flag} {path}\n' + text.rstrip('\n')))


def build(path, title):
    nb = new_notebook(cells=CELLS)
    nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
    nb.metadata['language_info'] = {'name': 'python'}
    nb.metadata['title'] = title
    nbformat.write(nb, path)
    return nb
