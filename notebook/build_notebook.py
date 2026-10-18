#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wallerstein_matcha.ipynb を組み立てる（実行は notebook/run_notebook.py）"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbtools
import part1, part2, part3, part4, part5

part1.front(); part1.setup(); part1.ch1(); part1.ch2()
part2.ch3(); part2.ch4()
part3.ch5(); part3.ch6(); part3.ch7(); part3.ch8()
part4.ch9(); part4.ch10()
part5.ch11(); part5.ch12(); part5.ch13()
out = os.path.join(nbtools.ROOT, 'wallerstein_matcha.ipynb')
nbtools.build(out, 'Matcha を使った neuro-symbolic な法的推論とウォーラーステイン理論')
print(out, len(nbtools.CELLS), 'cells')
