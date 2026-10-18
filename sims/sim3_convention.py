#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sim 3: 事実から慣習規範へ ―― 非正規の賃金をめぐる慣行の進化（Young 1993 の適応的プレイ）

企業と労働者の二つの母集団が、非正規の契約をどちらの慣行で結ぶかを選ぶ協調ゲーム:
  A = 補償原則（非正規はリスクの分だけ高く払う。賃金 w_A = Sim 2 の補償賃金の水準）
  B = 身分秩序（非正規は身分が低いので安くてよい。賃金 w_B = Sim 2 の周辺の非正規賃金の比率）
慣行が一致すれば契約が成立し、労働者は w_X、企業は π_X = p − w_X − c p を得る。
食い違えば契約は成立せず、労働者は外部オプション u_W = q w̄_R + (1−q) b（Harris–Todaro の列に並ぶ価値）を、
企業は退出オプション o_F（資本の移動性による、移転先での価値）を得る。

B が A よりリスク支配的（Harsanyi & Selten 1988）である条件:
  (w_B − u_W)(π_B − o_F) > (w_A − u_W)(π_A − o_F)
Young (1993) によれば、2×2 の協調ゲームの適応的プレイで確率的に安定な慣行は、リスク支配的な均衡である。
企業の退出オプション o_F が大きいほど B が有利になる（π_A < π_B のとき。Lean で示す）。
"""
import json
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def payoffs(region):
    """Sim 2 の結果から、慣行 A / B の賃金と利潤、労働者の外部オプションを作る"""
    return region


def risk_dominance_B(g, oF):
    """B のリスク支配度: (w_B−u)(π_B−o) − (w_A−u)(π_A−o)。B が均衡でなければ −inf"""
    wA, wB, piA, piB, u = g['wA'], g['wB'], g['piA'], g['piB'], g['uW']
    if wB <= u or piB <= oF:
        return -np.inf
    if wA <= u or piA <= oF:
        return np.inf
    return (wB - u) * (piB - oF) - (wA - u) * (piA - oF)


def penalty_needed(g, oF):
    """B を罰する法（同一労働同一賃金の執行）が、企業の B の利潤を P だけ下げるとき、A をリスク支配的にする最小の P"""
    wA, wB, piA, piB, u = g['wA'], g['wB'], g['piA'], g['piB'], g['uW']
    if wB <= u:
        return 0.0                     # B はもともと均衡でない
    return max(0.0, piB - oF - (wA - u) * (piA - oF) / (wB - u))


def adaptive_play(g, oF, T=40000, m=20, k=6, eps=0.03, penalty=0.0, seed=1, start='A'):
    """Young (1993) の適応的プレイ。毎期 1 組の企業と労働者が出会い、それぞれ相手の母集団の直近 m 回の
    行動から k 個を見本として取り、その頻度に対する最適反応を選ぶ（確率 eps で無作為に選ぶ）。
    戻り値: 各期に結ばれた契約が B だったかどうか（食い違いは None）"""
    rng = np.random.default_rng(seed)
    wA, wB, piA, piB, u = g['wA'], g['wB'], g['piA'], g['piB'] - penalty, g['uW']
    hist_F = [start] * m
    hist_W = [start] * m
    outcome = np.zeros(T, dtype=np.int8)       # 1 = B で成立, 0 = A で成立, -1 = 不成立
    for t in range(T):
        sW = rng.choice(hist_W, size=k, replace=False)   # 企業が見る労働者の行動
        sF = rng.choice(hist_F, size=k, replace=False)   # 労働者が見る企業の行動
        fA = np.mean(sW == 'A')
        gA = np.mean(sF == 'A')
        # 企業の期待利得
        eFA = fA * piA + (1 - fA) * oF
        eFB = (1 - fA) * piB + fA * oF
        aF = 'A' if eFA > eFB else ('B' if eFB > eFA else rng.choice(['A', 'B']))
        # 労働者の期待利得
        eWA = gA * wA + (1 - gA) * u
        eWB = (1 - gA) * wB + gA * u
        aW = 'A' if eWA > eWB else ('B' if eWB > eWA else rng.choice(['A', 'B']))
        if rng.random() < eps:
            aF = rng.choice(['A', 'B'])
        if rng.random() < eps:
            aW = rng.choice(['A', 'B'])
        outcome[t] = (1 if aF == 'B' else 0) if aF == aW else -1
        hist_F = hist_F[1:] + [aF]
        hist_W = hist_W[1:] + [aW]
    return outcome


def custom_time(outcome, window=500, thr=0.9):
    """慣習の成立（opinio juris の代理指標）: 直近 window 期の成立した契約のうち B の割合が thr 以上になった最初の時点"""
    b = (outcome == 1).astype(float)
    ok = (outcome >= 0).astype(float)
    cb, co = np.cumsum(b), np.cumsum(ok)
    for t in range(window, len(outcome)):
        nb = cb[t] - cb[t - window]
        no = co[t] - co[t - window]
        if no > 0 and nb / no >= thr:
            return t
    return None


def build_games():
    s2 = json.load(open(os.path.join(HERE, 'out', 'sim2.json'), encoding='utf-8'))
    pc = s2['params']['p_core']
    out = {}
    per = s2['handoff']['periphery']['high']
    core = s2['handoff']['core']['high']
    ratio_B = per['w_N'] / per['w_R_bar']           # 身分秩序のもとでの非正規 / 正規 の賃金比（周辺の実績値）
    for name, r, p, b in (('周辺', per, 1.0, 0.30), ('中核', core, pc, 0.45 * pc)):
        c = 0.05 * p
        wA = r['w_N_compensating']
        wB = ratio_B * r['w_R_bar']
        uW = r['q'] * r['w_R_bar'] + (1 - r['q']) * b
        out[name] = {'p': p, 'b': b, 'q': r['q'], 'wA': wA, 'wB': wB, 'piA': p - wA - c, 'piB': p - wB - c,
                     'uW': uW, 'w_R_bar': r['w_R_bar']}
    return out


def main(make_figs=True):
    games = build_games()
    out = {'games': games}
    # (i) 退出オプション o_F に対するリスク支配度（解析）と、確率的に安定な慣行の頻度（シミュレーション）
    res = {}
    for name, g in games.items():
        oFs = np.linspace(0, 0.9 * g['piA'], 13)
        rd = [risk_dominance_B(g, o) for o in oFs]
        freqB = []
        for j, o in enumerate(oFs):
            fs = []
            for sd in range(3):                       # 乱数の種を変えて 3 回の平均
                oc = adaptive_play(g, o, T=30000, seed=100 + 10 * j + sd)
                done = oc[oc >= 0]
                fs.append(np.mean(done == 1))
            freqB.append(float(np.mean(fs)))
        res[name] = {'oF': oFs.tolist(), 'risk_dom_B': [float(x) if np.isfinite(x) else (1e9 if x > 0 else -1e9) for x in rd],
                     'freq_B': freqB, 'penalty_needed': [penalty_needed(g, o) for o in oFs]}
    # 解析的な閾値: リスク支配度が 0 になる o_F（周辺）
    g = games['周辺']
    wA, wB, piA, piB, u = g['wA'], g['wB'], g['piA'], g['piB'], g['uW']
    # (wB−u)(πB−o) = (wA−u)(πA−o)  →  o* = ((wB−u)πB − (wA−u)πA) / ((wB−u) − (wA−u))
    res['周辺']['oF_threshold'] = ((wB - u) * piB - (wA - u) * piA) / ((wB - u) - (wA - u))
    out['sweep'] = res
    # (ii) 周辺の時系列（はじめは補償原則 A の慣行から出発）と、慣習の成立時点
    g = games['周辺']
    oF = 0.08                                  # リスク支配の閾値（約 0.053）を超える退出オプション
    oc = adaptive_play(g, oF, T=40000, seed=7, start='A')
    ct = custom_time(oc)
    # (iii) 法的介入（同一労働同一賃金の執行で、企業の B の利潤を P 下げる）を 20000 期目から
    #   弱い介入: A をリスク支配的にするのに必要な量の 1.2 倍（B はまだ均衡）
    #   強い介入: B が企業にとって均衡でなくなる量（P > π_B − o_F）の 1.1 倍
    P_weak = 1.2 * penalty_needed(g, oF)
    P_strong = 1.1 * (g['piB'] - oF)
    oc_w = np.concatenate([oc[:20000], adaptive_play(g, oF, T=20000, seed=8, start='B', penalty=P_weak)])
    oc_s = np.concatenate([oc[:20000], adaptive_play(g, oF, T=20000, seed=9, start='B', penalty=P_strong)])
    out['timeseries'] = {'oF': oF, 'custom_time': ct, 'penalty_weak': P_weak, 'penalty_strong': P_strong,
                         'rolling_B': rolling(oc).tolist(), 'rolling_B_weak_law': rolling(oc_w).tolist(),
                         'rolling_B_strong_law': rolling(oc_s).tolist()}
    with open(os.path.join(HERE, 'out', 'sim3.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    if make_figs:
        figures(out)
    return out


def rolling(oc, window=500, step=100):
    b = (oc == 1).astype(float)
    ok = (oc >= 0).astype(float)
    cb, co = np.concatenate([[0], np.cumsum(b)]), np.concatenate([[0], np.cumsum(ok)])
    xs = []
    for t in range(window, len(oc) + 1, step):
        no = co[t] - co[t - window]
        xs.append((cb[t] - cb[t - window]) / no if no else np.nan)
    return np.array(xs)


def figures(out):
    from vizstyle import setup, BLUE, ORANGE, AQUA, INK2, MUTED
    plt = setup()
    figdir = os.path.join(HERE, 'fig')
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8))
    ax = axes[0]
    for name, col in (('中核', BLUE), ('周辺', ORANGE)):
        r = out['sweep'][name]
        g = out['games'][name]
        x = np.array(r['oF']) / g['piB']
        ax.plot(x, r['freq_B'], color=col, marker='o', ms=5, label=name)
        if 'oF_threshold' in r:
            th = r['oF_threshold'] / g['piB']
            ax.axvline(th, color=col, lw=1, ls=':')
            ax.annotate('リスク支配の閾値\n（解析）', (th, 0.55), xytext=(-6, 0), textcoords='offset points',
                        color=INK2, ha='right')
    ax.set_xlabel('企業の退出オプション o_F / 身分秩序での利潤 π_B')
    ax.set_ylabel('成立した契約のうち身分秩序 B の割合')
    ax.set_ylim(-0.03, 1.03)
    ax.set_title('慣行の選択（適応的プレイ）')
    ax.legend(loc='center right')
    ax = axes[1]
    ts = out['timeseries']
    t = np.arange(len(ts['rolling_B'])) * 100 + 500
    ax.plot(t, ts['rolling_B'], color=ORANGE, label='介入なし')
    ax.plot(t, ts['rolling_B_weak_law'], color=BLUE, ls='--', lw=2.4, label='弱い介入（リスク支配だけを逆転）')
    ax.annotate('弱い介入では B が続く（線が重なる）', (30000, 1.0), xytext=(0, -16), textcoords='offset points',
                color=INK2, ha='center')
    ax.plot(t, ts['rolling_B_strong_law'], color=AQUA, label='強い介入（B を維持できなくする）')
    ax.axvline(20000, color=MUTED, lw=1, ls=':')
    if ts['custom_time'] is not None:
        ax.axvline(ts['custom_time'], color=INK2, lw=1, ls='--')
        ax.annotate('慣習の成立', (ts['custom_time'], 0.5), xytext=(4, 0), textcoords='offset points', color=INK2)
    ax.set_xlabel('期')
    ax.set_ylabel('直近 500 期の B の割合')
    ax.set_ylim(-0.03, 1.03)
    ax.set_title('周辺: 補償原則から身分秩序へ、そして法的介入')
    ax.legend(loc='lower right')
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, 'sim3_convention.png'))
    plt.close(fig)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, HERE)
    o = main()
    print(json.dumps(o['games'], ensure_ascii=False, indent=1))
    for name, r in o['sweep'].items():
        print(name, [round(x, 3) for x in r['oF']], [round(x, 3) if abs(x) < 1e8 else x for x in r['risk_dom_B']], r['freq_B'], [round(x, 3) for x in r['penalty_needed']])
    ts = o['timeseries']
    print('custom_time', ts['custom_time'], 'P_weak', ts['penalty_weak'], 'P_strong', ts['penalty_strong'])
