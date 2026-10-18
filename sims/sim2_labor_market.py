#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sim 2: 周辺における非正規雇用 ―― 外資の退出オプションと二重労働市場

地域 r（中核 C / 周辺 P）に、労働者 L 人と、異質な企業（職のまとまり）が多数ある。
  職の総数 J = λ L（λ < 1 なら労働余剰。Lewis 1954）
  企業 i: 技能の上乗せ s_i（正規で長く働くと生産性が (1+s_i) 倍）、需要の変動にさらされる職の割合 σ_i、
          外資か国内資本か（外資の撤退ハザード h_F、国内資本 h_D）
  変動する職は非正規。安定した職は、正規の価値 V_R が非正規の価値 V_N を上回るときに正規にする:
    V_R = (1+s) p − w_R(s) − (h + ρ) F p        （撤退・離職のとき解雇費用 F p がかかる）
    V_N = p − w_N − c p                         （非正規は入れ替えの費用 c p だけ）
  正規の賃金（ナッシュ交渉）: w_R(s) = b + β((1+s) p − b)
  非正規の賃金（Harris & Todaro 1970 型の無差別条件。企業は非正規の職を埋められる最低の賃金を提示する）:
    非正規の層は契約の切れ目のため、固有の割合 e0 で職がない。非正規の職 J_N を埋めるには J_N/(1−e0) 人が要る。
    それ以外の労働者は正規職の列に並ぶので、正規職に就ける確率は
      q = min(1, J_R / (L − J_N/(1−e0)))
    列に並ぶ期待所得  q w̄_R + (1−q) b  =  非正規の期待所得  (1−e0) w_N + e0 b
    → w_N = b + q (w̄_R − b) / (1 − e0)
  したがって  w_N < w̄_R  ⟺  q < 1 − e0  （補償賃金の原則が「身分賃金」に反転する条件。Lean で示す）
  労働余剰がなければ q = 1 で w_N > w̄_R（補償賃金、Rosen 1986）。余剰が大きいほど q は小さくなる。
  さらに、J_R = (1−ν)λL、J_N = νλL（ν: 非正規の職の割合）を代入すると、q < 1 − e₀ ⟺ λ < 1 − e₀ となり、ν が消える。
  つまり賃金の序列が反転するかは労働余剰（職の充足率 λ）だけで決まり、資本の移動性は非正規の「量」と反転の「深さ」を決める。
外資の利潤は中核へ送金される（周辺から中核への余剰移転）。
"""
import json
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


class Region:
    def __init__(self, name, p=1.0, b=0.3, lam=0.7, foreign=0.6, hF=0.15, hD=0.02, L=1.0,
                 F=1.0, beta=0.4, rho=0.02, c=0.05, s_max=0.6, sigma_max=0.6, e0=0.2, n_firms=4000, seed=1):
        self.name, self.p, self.b, self.lam, self.foreign = name, p, b, lam, foreign
        self.hF, self.hD, self.L, self.F, self.beta, self.rho, self.c = hF, hD, L, F, beta, rho, c
        self.e0 = e0
        rng = np.random.default_rng(seed)
        self.s = rng.uniform(0, s_max, n_firms)
        self.sigma = rng.uniform(0, sigma_max, n_firms)
        self.is_foreign = rng.uniform(0, 1, n_firms) < foreign
        self.size = lam * L / n_firms          # 各企業の職の数

    def h(self):
        return np.where(self.is_foreign, self.hF, self.hD)

    def firm_choice(self, wN):
        p, b = self.p, self.b
        wR = b + self.beta * ((1 + self.s) * p - b)
        VR = (1 + self.s) * p - wR - (self.h() + self.rho) * self.F * p
        VN = p - wN - self.c * p
        reg = VR > VN
        stable = (1 - self.sigma) * self.size
        J_R = np.where(reg, stable, 0.0)
        J_N = self.size - J_R
        return reg, wR, J_R, J_N, VR, VN

    def queue_prob(self, JR, JN):
        rest = self.L - JN / (1 - self.e0)
        return 1.0 if rest <= JR else JR / rest

    def equilibrium(self, iters=600, damp=0.3, start='high'):
        """start='high': 補償賃金の水準から、start='low': 生存水準 b から反復を始める。
        両者が違う点に収束すれば、補償賃金の均衡と身分賃金の均衡が両方とも存在する（複数均衡）。"""
        wN = self.b if start == 'low' else self.b + (self.b + self.beta * (self.p - self.b) - self.b) / (1 - self.e0) * 1.2
        for _ in range(iters):
            reg, wR, J_R, J_N, VR, VN = self.firm_choice(wN)
            JR, JN = J_R.sum(), J_N.sum()
            q = self.queue_prob(JR, JN)
            wRbar = (wR * J_R).sum() / JR if JR > 0 else self.b + self.beta * (self.p - self.b)
            target = self.b + q * (wRbar - self.b) / (1 - self.e0)
            wN_new = (1 - damp) * wN + damp * target
            if abs(wN_new - wN) < 1e-10:
                wN = wN_new
                break
            wN = wN_new
        reg, wR, J_R, J_N, VR, VN = self.firm_choice(wN)
        JR, JN = J_R.sum(), J_N.sum()
        q = self.queue_prob(JR, JN)
        e = self.e0
        wRbar = (wR * J_R).sum() / JR if JR > 0 else self.b + self.beta * (self.p - self.b)
        # 外資の利潤（中核への送金）: 正規・非正規それぞれの職の価値の合計
        profit = np.where(reg, (1 - self.sigma) * self.size * VR, 0.0) + J_N * VN
        foreign_profit = float(profit[self.is_foreign].sum())
        # 身分賃金による移転: 補償賃金（q = 1 のときの水準）と実際の非正規賃金の差 × 外資の非正規の職
        wN_comp = self.b + (wRbar - self.b) / (1 - self.e0)
        status_rent = float(max(wN_comp - wN, 0.0) * J_N[self.is_foreign].sum())
        stable = (1 - self.sigma) * self.size
        def stable_nonreg(mask):
            st = stable[mask].sum()
            return float(stable[mask][~reg[mask]].sum() / st) if st > 0 else float('nan')
        wage_bill = float((wR * J_R).sum() + wN * JN)
        output = float((np.where(reg, (1 + self.s), 1.0) * (1 - self.sigma) * self.size).sum() * self.p
                       + (self.sigma * self.size).sum() * self.p)
        return {'region': self.name, 'start': start, 'w_N': float(wN), 'w_R_bar': float(wRbar), 'q': float(q), 'e': float(e),
                'one_minus_e': float(1 - e), 'nonregular_share': float(JN / (JR + JN)),
                'inverted': bool(wN < wRbar), 'foreign_profit': foreign_profit,
                'w_N_compensating': float(wN_comp), 'status_rent_to_core': status_rent,
                'stable_nonregular_foreign': stable_nonreg(self.is_foreign),
                'stable_nonregular_domestic': stable_nonreg(~self.is_foreign),
                'labor_share': wage_bill / output, 'output': output}


def both(region):
    """高い出発点と低い出発点からの均衡。regime: 'compensating'（補償のみ）/'status'（身分のみ）/'both'（両方）"""
    hi, lo = region.equilibrium(start='high'), region.equilibrium(start='low')
    kinds = {('status' if r['inverted'] else 'compensating') for r in (hi, lo)}
    distinct = abs(hi['w_N'] - lo['w_N']) > 1e-4 or abs(hi['q'] - lo['q']) > 1e-4
    regime = 'both' if (distinct and len(kinds) == 2) else kinds.pop()
    return hi, lo, regime


def sweep_mobility(hF_values, **kw):
    return [Region(hF=h, **kw).equilibrium() for h in hF_values]


def main(make_figs=True):
    out = {}
    s1 = json.load(open(os.path.join(HERE, 'out', 'sim1.json'), encoding='utf-8'))['handoff']
    # Sim 1 から: 中核と周辺の工業生産性の比
    pC, pP = s1['A_core'] / s1['A_periphery'], 1.0
    out['params'] = {'p_core': pC, 'p_periphery': pP}
    core_kw = dict(name='中核', p=pC, b=0.45 * pC, lam=0.97, foreign=0.1, hD=0.02)
    per_kw = dict(name='周辺', p=pP, b=0.30 * pP, lam=0.70, foreign=0.6, hD=0.02)
    # (i) 外資の撤退ハザード（資本の移動性）を上げていく
    hs = np.linspace(0.0, 0.4, 41)
    out['mobility'] = {'hF': hs.tolist(),
                       'core': sweep_mobility(hs, **core_kw),
                       'periphery': sweep_mobility(hs, **per_kw)}
    # (ii) 相図: 職の充足率 λ × 外資の撤退ハザード h_F（周辺の他のパラメータで）
    lams = np.linspace(0.5, 1.0, 26)
    hs2 = np.linspace(0.0, 0.4, 21)
    gap = np.zeros((len(lams), len(hs2)))
    nonreg = np.zeros_like(gap)
    regime = np.zeros_like(gap)            # 0 = 補償のみ, 1 = 両方（複数均衡）, 2 = 身分のみ
    code = {'compensating': 0, 'both': 1, 'status': 2}
    for i, lam in enumerate(lams):
        for j, h in enumerate(hs2):
            kw = dict(per_kw)
            kw['lam'] = lam
            hi, lo, rg = both(Region(hF=h, n_firms=1500, **kw))
            gap[i, j] = hi['w_N'] / hi['w_R_bar'] - 1
            nonreg[i, j] = hi['nonregular_share']
            regime[i, j] = code[rg]
    out['phase'] = {'lam': lams.tolist(), 'hF': hs2.tolist(), 'wage_gap': gap.tolist(), 'nonregular': nonreg.tolist(),
                    'regime': regime.tolist(), 'regime_code': code}
    # (iii) 内なる周辺化: 中核の国内資本も移動しやすくなり（h_D↑）、職の充足率も下がる（λ↓）経路
    path = []
    for k in range(81):
        t = k / 80
        kw = dict(core_kw)
        kw['hD'] = 0.02 + 0.18 * t
        kw['lam'] = 0.97 - 0.22 * t
        hi, lo, rg = both(Region(hF=0.05 + 0.25 * t, **kw))
        hi['t'] = t
        hi['low'] = lo
        hi['regime'] = rg
        path.append(hi)
    out['inner_periphery'] = path
    # (iv) 周辺の非正規化と中核への余剰移転
    out['transfer'] = [{'hF': float(h), **{k: r[k] for k in ('status_rent_to_core', 'foreign_profit', 'labor_share', 'nonregular_share')}}
                       for r, h in zip(out['mobility']['periphery'], hs)]
    # 第 3 部への引き渡し: 代表的な周辺（h_F = 0.25）と中核（h_F = 0.05）の値
    hp, lp, rp = both(Region(hF=0.25, **per_kw))
    hc, lc, rc = both(Region(hF=0.05, **core_kw))
    out['handoff'] = {'periphery': {'high': hp, 'low': lp, 'regime': rp},
                      'core': {'high': hc, 'low': lc, 'regime': rc}, 'hF_periphery': 0.25, 'hF_core': 0.05}
    with open(os.path.join(HERE, 'out', 'sim2.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    if make_figs:
        figures(out)
    return out


def figures(out):
    from vizstyle import setup, BLUE, ORANGE, AQUA, INK2, MUTED, DIV
    plt = setup()
    figdir = os.path.join(HERE, 'fig')
    mob = out['mobility']
    hs = mob['hF']
    # 図 2-1: 資本の移動性と非正規比率・賃金比
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8))
    ax = axes[0]
    for key, col in (('core', BLUE), ('periphery', ORANGE)):
        ax.plot(hs, [r['nonregular_share'] for r in mob[key]], color=col, label=mob[key][0]['region'])
    ax.set_xlabel('外資の撤退ハザード h_F（資本の移動性）')
    ax.set_ylabel('非正規の職の割合')
    ax.set_title('資本の移動性と非正規化')
    ax.legend(loc='upper left')
    ax = axes[1]
    for key, col in (('core', BLUE), ('periphery', ORANGE)):
        ax.plot(hs, [r['w_N'] / r['w_R_bar'] for r in mob[key]], color=col, label=mob[key][0]['region'])
    ax.axhline(1, color=MUTED, lw=1, ls='--')
    ax.annotate('補償賃金（非正規が高い）', (0.25, 1.0), xytext=(0, 6), textcoords='offset points', color=INK2)
    ax.annotate('身分賃金（非正規が低い）', (0.25, 1.0), xytext=(0, -14), textcoords='offset points', color=INK2)
    ax.set_xlabel('外資の撤退ハザード h_F（資本の移動性）')
    ax.set_ylabel('非正規の賃金 / 正規の平均賃金')
    ax.set_title('賃金の序列の反転')
    ax.legend(loc='lower left')
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, 'sim2_mobility.png'))
    plt.close(fig)
    # 図 2-2: 相図（周辺のパラメータ。色は w_N/w̄_R − 1、0 で反転）
    ph = out['phase']
    G = np.array(ph['wage_gap'])
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
    cmap = LinearSegmentedColormap.from_list('div', DIV[::-1])
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    lim = np.nanmax(np.abs(G))
    im = ax.imshow(G, origin='lower', aspect='auto', cmap=cmap, norm=TwoSlopeNorm(0, -lim, lim),
                   extent=(ph['hF'][0], ph['hF'][-1], ph['lam'][0], ph['lam'][-1]))
    ax.contour(ph['hF'], ph['lam'], G, levels=[0], colors=[INK2], linewidths=1.5)
    ax.grid(False)
    ax.set_xlabel('外資の撤退ハザード h_F')
    ax.set_ylabel('職の充足率 λ（労働者 1 人あたりの職）')
    ax.set_title('非正規の賃金プレミアム w_N / w̄_R − 1（実線は 0）')
    fig.colorbar(im, ax=ax, fraction=0.05, pad=0.02)
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, 'sim2_phase.png'))
    plt.close(fig)
    # 図 2-3: 内なる周辺化と、q と 1−e の交差
    ip = out['inner_periphery']
    t = [r['t'] for r in ip]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8))
    ax = axes[0]
    ax.plot(t, [r['q'] for r in ip], color=BLUE, label='q（正規職に就ける確率）')
    ax.plot(t, [r['one_minus_e'] for r in ip], color=ORANGE, label='1 − e0（非正規の就業率）')
    ax.set_xlabel('中核のグローバル化の進行（0 → 1）')
    ax.set_ylabel('確率')
    ax.set_title('中核での反転条件 q < 1 − e0')
    ax.legend(loc='center left')
    ax = axes[1]
    ax.plot(t, [r['nonregular_share'] for r in ip], color=BLUE, label='非正規の職の割合')
    ax.plot(t, [r['w_N'] / r['w_R_bar'] for r in ip], color=AQUA, label='非正規の賃金 / 正規の平均賃金')
    ax.axhline(1, color=MUTED, lw=1, ls='--')
    ax.set_xlabel('中核のグローバル化の進行（0 → 1）')
    ax.set_title('内なる周辺化（仮説の例示）')
    ax.legend(loc='center left')
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, 'sim2_inner_periphery.png'))
    plt.close(fig)
    # 図 2-4: 身分賃金による周辺から中核への移転
    tr = out['transfer']
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot([r['hF'] for r in tr], [r['status_rent_to_core'] for r in tr], color=ORANGE)
    ax.set_xlabel('外資の撤退ハザード h_F')
    ax.set_ylabel('移転額（周辺の労働者 1 人あたり）')
    ax.set_title('身分賃金による周辺から中核への移転')
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, 'sim2_transfer.png'))
    plt.close(fig)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, HERE)
    o = main()
    for key in ('core', 'periphery'):
        for r in o['mobility'][key][::10]:
            print(key, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    print('handoff', json.dumps(o['handoff'], ensure_ascii=False)[:800])
    for r in o['inner_periphery'][::5]:
        print('inner', round(r['t'], 2), round(r['q'], 3), round(r['one_minus_e'], 3), round(r['nonregular_share'], 3), round(r['w_N'] / r['w_R_bar'], 3))
