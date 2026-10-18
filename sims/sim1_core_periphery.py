#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sim 1: 中核／半周辺／周辺の創発（累積的因果モデル）

N 地域がリング状に並ぶ。各地域は移動しない労働（1 単位）と、工業の能力 x_i（技術・資本の蓄積）を持つ。
  工業の生産性        A_i = (1 + x_i)^ψ                       （学習には収穫逓減）
  需要の配分          S_ij = A_i^θ φ_ij / Σ_k A_k^θ φ_kj       （地域 j の工業品購入のうち i から買う割合）
                      φ_ij = φ^{d_ij}                          （φ: 貿易の自由度。0 = 交易なし、1 = 貿易費用なし）
  所得                Y = b + R,  R = μ S Y                    （b: 一次産業の所得、μ: 工業品への支出割合）
  能力の変化          dx_i/dt = β R_i − δ x_i                  （生産からの学習 ＝ Verdoorn 則、減耗）

対称な均衡 x* = β μ / ((1−μ) δ) の、2 地域での反対称な摂動に対する安定条件:
  K h(φ) < 1,   K = 4 μ θ ψ β / ((1−μ)(1+x*) δ),   h(φ) = φ / ((1+φ)(1−μ+(1+μ)φ))
h は φ = √((1−μ)/(1+μ)) で最大となる（Lean で補題として示す）。
"""
import json
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def ring_dist(N):
    i = np.arange(N)
    d = np.abs(i[:, None] - i[None, :])
    return np.minimum(d, N - d)


class Model:
    def __init__(self, N=2, mu=0.5, theta=5.0, psi=0.5, beta=1.0, delta=1.0, b=None):
        self.N, self.mu, self.theta, self.psi, self.beta, self.delta = N, mu, theta, psi, beta, delta
        self.D = ring_dist(N)
        self.b = np.ones(N) if b is None else np.asarray(b, float)

    def x_star(self):
        return self.beta * self.mu / ((1 - self.mu) * self.delta)

    def K(self):
        return 4 * self.mu * self.theta * self.psi * self.beta / ((1 - self.mu) * (1 + self.x_star()) * self.delta)

    def h(self, phi):
        mu = self.mu
        return phi / ((1 + phi) * (1 - mu + (1 + mu) * phi))

    def shares(self, x, phi):
        A = (1 + x) ** self.psi
        W = (A ** self.theta)[:, None] * phi ** self.D
        return W / W.sum(axis=0, keepdims=True)

    def incomes(self, x, phi, b=None):
        b = self.b if b is None else b
        S = self.shares(x, phi)
        Y = np.linalg.solve(np.eye(self.N) - self.mu * S, b)
        R = self.mu * S @ Y
        return Y, R, S

    def run(self, x0, phi, T=200.0, dt=0.05, b=None):
        x = np.array(x0, float)
        for _ in range(int(T / dt)):
            _, R, _ = self.incomes(x, phi, b)
            x += dt * (self.beta * R - self.delta * x)
            x = np.maximum(x, 0.0)
        return x


def unequal_exchange(m, x, phi):
    """体化労働の交換比率: 輸出に体化された労働 / 輸入に体化された労働（> 1 なら不利な交換）
    工業品 1 価値単位あたりの労働 = 1/A_i、一次産品は 1。工業品の収支の差は一次産品で決済される。"""
    Y, R, S = m.incomes(x, phi)
    A = (1 + x) ** m.psi
    lab = 1.0 / A
    N = m.N
    ratios = []
    for i in range(N):
        exp_M = R[i] - S[i, i] * m.mu * Y[i]                    # 工業品の輸出額
        imp_M = m.mu * Y[i] * (1 - S[i, i])                     # 工業品の輸入額
        imp_hours = sum(S[j, i] * m.mu * Y[i] * lab[j] for j in range(N) if j != i)
        prim = imp_M - exp_M                                    # 一次産品の純輸出（> 0 なら輸出）
        exp_hours = exp_M * lab[i] + max(prim, 0.0)
        imp_hours += max(-prim, 0.0)
        ratios.append(exp_hours / imp_hours)
    return np.array(ratios)


def tiers(x):
    """工業能力 x で三層に分ける。
    中核: 最大値の 50% 以上。半周辺: 中核以外の中央値の 2 倍を超え、かつ 0.02 以上上回る。周辺: それ以外。
    （最大が最小の 1.5 倍未満なら、まだ分化していないので全部「対称」とする）"""
    x = np.asarray(x)
    if x.max() < 1.5 * max(x.min(), 1e-9):     # 最大が最小の 1.5 倍未満ならまだ分化していない
        return ['対称'] * len(x)
    core = x >= 0.5 * x.max()
    base = np.median(x[~core]) if (~core).any() else 0.0
    out = []
    for v, c in zip(x, core):
        out.append('中核' if c else ('半周辺' if (v > 2 * base and v > base + 0.02) else '周辺'))
    return out


def main(make_figs=True):
    out = {}
    rng = np.random.default_rng(20261019)
    m2 = Model(N=2)
    xs = m2.x_star()
    K = m2.K()
    # 解析的な閾値: K h(φ) = 1 の根
    mu = m2.mu
    a, bb = 1 - mu, 1 + mu
    # K φ = (1+φ)(a + bb φ)  →  bb φ² + (a + bb − K) φ + a = 0
    disc = (a + bb - K) ** 2 - 4 * bb * a
    roots = sorted([(-(a + bb - K) - np.sqrt(disc)) / (2 * bb), (-(a + bb - K) + np.sqrt(disc)) / (2 * bb)]) if disc >= 0 else []
    phi_c = [r for r in roots if 0 < r < 1]
    out['two_region'] = {'x_star': xs, 'K': K, 'phi_critical': phi_c,
                         'phi_hmax': float(np.sqrt(a / bb)), 'h_max': float(m2.h(np.sqrt(a / bb)))}

    # --- 2 地域: 分岐図（φ を上げていく掃引と、下げていく掃引）
    phis = np.linspace(0.02, 0.98, 49)
    up, down = [], []
    x = np.array([xs * 1.001, xs * 0.999])
    for p in phis:
        x = m2.run(x + rng.normal(0, 1e-4, 2), p, T=150)
        up.append((x[0] - x[1]) / (x[0] + x[1]))
    for p in phis[::-1]:
        x = m2.run(x, p, T=150)
        down.append((x[0] - x[1]) / (x[0] + x[1]))
    down = down[::-1]
    out['two_region']['sweep'] = {'phi': phis.tolist(), 'asym_up': up, 'asym_down': down}

    # --- 10 地域のリング: φ ごとの最終状態
    N = 10
    m10 = Model(N=N)
    ring = {}
    for p in (0.1, 0.3, 0.6, 0.9):
        x0 = m10.x_star() * (1 + rng.normal(0, 0.01, N))
        x = m10.run(x0, p, T=400)
        Y, R, S = m10.incomes(x, p)
        ux = unequal_exchange(m10, x, p)
        ring[str(p)] = {'x': x.tolist(), 'Y': Y.tolist(), 'tiers': tiers(x), 'unequal_exchange': ux.tolist()}
    out['ring10'] = ring

    # --- グローバル化の時間経路（20 地域、φ を 0.1 から 0.9 へ徐々に上げる）
    N20 = 20
    m20 = Model(N=N20)
    x = m20.x_star() * (1 + rng.normal(0, 0.01, N20))
    path = {'t': [], 'phi': [], 'n_core': [], 'n_semi': [], 'top_share': [], 'x': []}
    steps = 80
    for k in range(steps + 1):
        p = 0.1 + 0.8 * k / steps
        x = m20.run(x + rng.normal(0, 1e-4, N20), p, T=25)
        tr = tiers(x)
        path['t'].append(k)
        path['phi'].append(p)
        path['n_core'].append(tr.count('中核'))
        path['n_semi'].append(tr.count('半周辺'))
        path['top_share'].append(float(x.max() / x.sum()))
        path['x'].append(x.tolist())
    out['globalization'] = path

    # --- 周辺のショックは中核に及ぶか（φ=0.6 の 10 地域の階層構造のもとで）
    p = 0.6
    x = np.array(ring['0.6']['x'])
    Y0, _, _ = m10.incomes(x, p)
    tr = tiers(x)
    per = [i for i, t in enumerate(tr) if t == '周辺']
    core = [i for i, t in enumerate(tr) if t == '中核']
    b1 = m10.b.copy()
    b1[per] *= 0.8                                            # 周辺の一次産業所得を 20% 下げる
    Y1, _, _ = m10.incomes(x, p, b1)                           # 短期（能力 x は固定）
    x_long = m10.run(x, p, T=400, b=b1)                        # 長期（能力も調整）
    Y2, _, _ = m10.incomes(x_long, p, b1)
    pct = lambda new, old, idx: float(100 * (new[idx].mean() / old[idx].mean() - 1)) if idx else None
    out['insulation'] = {
        'phi': p, 'periphery': per, 'core': core,
        'short_run_pct': {'periphery': pct(Y1, Y0, per), 'core': pct(Y1, Y0, core)},
        'long_run_pct': {'periphery': pct(Y2, Y0, per), 'core': pct(Y2, Y0, core)},
    }

    # --- Sim 2 への引き渡し: φ=0.6 の中核と周辺の 1 人あたり所得の比
    out['handoff'] = {
        'phi': p, 'Y_core': float(np.mean(Y0[core])) if core else None,
        'Y_periphery': float(np.mean(Y0[per])) if per else None,
        'A_core': float(np.mean((1 + x[core]) ** m10.psi)) if core else None,
        'A_periphery': float(np.mean((1 + x[per]) ** m10.psi)) if per else None,
    }
    with open(os.path.join(HERE, 'out', 'sim1.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    if make_figs:
        figures(m2, out)
    return out


def figures(m2, out):
    from vizstyle import setup, BLUE, ORANGE, AQUA, INK2, MUTED, SEQ_BLUE
    plt = setup()
    figdir = os.path.join(HERE, 'fig')
    tw = out['two_region']
    # 図 1-1: 安定条件 K h(φ) と分岐図
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ph = np.linspace(0.001, 1, 400)
    ax = axes[0]
    ax.plot(ph, m2.K() * m2.h(ph), color=BLUE)
    ax.axhline(1, color=MUTED, lw=1, ls='--')
    for pc in tw['phi_critical']:
        ax.axvline(pc, color=MUTED, lw=1, ls=':')
        ax.annotate(f'φ* ≈ {pc:.3f}', (pc, 0.15), xytext=(6, 0), textcoords='offset points', color=INK2)
    ax.set_xlabel('貿易の自由度 φ')
    ax.set_ylabel('K·h(φ)')
    ax.set_title('対称均衡の安定条件（1 を超えると不安定）')
    ax = axes[1]
    sw = tw['sweep']
    ax.plot(sw['phi'], sw['asym_up'], color=BLUE, marker='o', ms=4, label='φ を上げる')
    ax.plot(sw['phi'], sw['asym_down'], color=ORANGE, marker='s', ms=4, label='φ を下げる')
    ax.set_xlabel('貿易の自由度 φ')
    ax.set_ylabel('非対称度 (x1 − x2) / (x1 + x2)')
    ax.set_title('2 地域の分岐と履歴効果')
    ax.legend(loc='upper left')
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, 'sim1_bifurcation.png'))
    plt.close(fig)
    # 図 1-2: 10 地域のリング（φ ごとの工業能力）
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.4), sharey=True)
    colmap = {'中核': BLUE, '半周辺': AQUA, '周辺': ORANGE, '対称': MUTED}
    for ax, (p, d) in zip(axes, out['ring10'].items()):
        x = np.array(d['x'])
        ax.bar(range(len(x)), x, color=[colmap[t] for t in d['tiers']], width=0.8)
        ax.set_title(f'φ = {p}')
        ax.set_xlabel('地域（リング上の位置）')
        ax.set_xticks(range(len(x)))
    axes[0].set_ylabel('工業能力 x')
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=c, label=t) for t, c in colmap.items() if t != '対称'],
               loc='upper center', ncol=3, bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(os.path.join(figdir, 'sim1_ring10.png'))
    plt.close(fig)
    # 図 1-3: グローバル化の経路（20 地域）
    g = out['globalization']
    X = np.array(g['x'])                      # 時点 × 地域
    share = X / X.sum(axis=1, keepdims=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={'width_ratios': [1.4, 1]})
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('seqblue', ['#fcfcfb'] + SEQ_BLUE)
    ax = axes[0]
    im = ax.imshow(share.T, aspect='auto', origin='lower', cmap=cmap, vmin=0, vmax=share.max(),
                   extent=(g['phi'][0], g['phi'][-1], -0.5, X.shape[1] - 0.5))
    ax.grid(False)
    ax.set_xlabel('貿易の自由度 φ（時間とともに上昇）')
    ax.set_ylabel('地域')
    ax.set_yticks(range(0, X.shape[1], 2))
    ax.set_title('工業能力の世界シェア')
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    ax = axes[1]
    ax.step(g['phi'], g['n_core'], where='mid', color=BLUE, label='中核の数')
    ax.step(g['phi'], g['n_semi'], where='mid', color=AQUA, label='半周辺の数')
    ax.set_xlabel('貿易の自由度 φ')
    ax.set_ylabel('地域の数')
    ax.set_title('中核の統合と、移行期の半周辺')
    ax.legend(loc='upper right')
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, 'sim1_globalization.png'))
    plt.close(fig)

if __name__ == '__main__':
    import sys
    sys.path.insert(0, HERE)
    o = main()
    print(json.dumps({k: v for k, v in o.items() if k != 'ring10'}, ensure_ascii=False, indent=1)[:3000])
    for p, d in o['ring10'].items():
        print(p, [f'{y:.2f}' for y in d['Y']], d['tiers'], [f'{u:.2f}' for u in d['unequal_exchange']])
