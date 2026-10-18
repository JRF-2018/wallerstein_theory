# -*- coding: utf-8 -*-
"""図の共通スタイル（日本語フォント、検証済みの配色、控えめな軸と格子、細い線）"""
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 配色（dataviz スキルの参照パレット。カテゴリは固定順で使い、使い回さない）
BLUE, ORANGE, AQUA, YELLOW = '#2a78d6', '#eb6834', '#1baf7a', '#eda100'
MAGENTA, GREEN, VIOLET, RED = '#e87ba4', '#008300', '#6250d6', '#e34948'
CAT = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]
INK, INK2, MUTED, GRID, SURFACE = '#0b0b0b', '#52514e', '#8a8984', '#e4e3df', '#fcfcfb'
NEUTRAL = '#f0efec'
# 逐次（青の単色）と発散（青 ↔ 灰 ↔ 赤）
SEQ_BLUE = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']
DIV = ['#184f95', '#3987e5', '#9ec5f4', NEUTRAL, '#f2a3a2', '#e34948', '#a52726']


def setup():
    """matplotlib の既定値を設定する（日本語フォントがあれば使う）"""
    names = {f.name for f in font_manager.fontManager.ttflist}
    for cand in ('Noto Sans CJK JP', 'IPAexGothic', 'IPAGothic', 'Noto Sans JP', 'TakaoGothic'):
        if cand in names:
            matplotlib.rcParams['font.family'] = cand
            break
    matplotlib.rcParams.update({
        'axes.unicode_minus': False,
        'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
        'axes.edgecolor': MUTED, 'axes.labelcolor': INK2, 'axes.titlecolor': INK,
        'xtick.color': INK2, 'ytick.color': INK2, 'text.color': INK,
        'axes.grid': True, 'axes.axisbelow': True, 'grid.color': GRID, 'grid.linewidth': 0.8,
        'axes.spines.top': False, 'axes.spines.right': False,
        'lines.linewidth': 2.0, 'lines.markersize': 6,
        'axes.prop_cycle': matplotlib.cycler(color=CAT),
        'legend.frameon': False, 'figure.dpi': 110, 'savefig.dpi': 150,
        'axes.titlesize': 12, 'axes.labelsize': 10.5, 'font.size': 10,
    })
    return plt
