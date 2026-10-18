#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wallerstein_matcha.ipynb をリポジトリのルートで実行し、出力を埋め込んで保存する"""
import os
import sys
import nbformat
from nbclient import NotebookClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
path = os.path.join(ROOT, 'wallerstein_matcha.ipynb')
nb = nbformat.read(path, as_version=4)
client = NotebookClient(nb, timeout=1800, kernel_name='python3', resources={'metadata': {'path': ROOT}})
client.execute()
nbformat.write(nb, path)
errs = [c for c in nb.cells if c.cell_type == 'code' and any(o.get('output_type') == 'error' for o in c.get('outputs', []))]
print('実行しました。エラーのあるセル:', len(errs))
for c in errs:
    print('----', c.source[:120])
