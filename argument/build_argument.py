#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_argument.py -- シミュレーションの結果（sims/out/*.json）から、第 3 部の Matcha-D の論証ファイルを機械的に作る

方針:
  * 事実（<= の後）には数値をそのまま書き、直前の // コメントに出典（JSON のどの値か）を示す。
  * 数値から法的概念への橋渡しは @評価 として書く。評価は争いうるあてはめで、スキルが審査する（neuro の部分）。
  * 閾値との比較で要件の成否（+ / !）を決める。これは著者（このスクリプト）の主張で、mext.py が照合する。
  * Matcha には変数がないので、規範は地域（中核・周辺）ごとの事件として具体化する。

使い方: python3 argument/build_argument.py   （argument/*.matcha を書き出す）
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SIMS = os.path.join(HERE, '..', 'sims', 'out')


def load():
    s1 = json.load(open(os.path.join(SIMS, 'sim1.json'), encoding='utf-8'))
    s2 = json.load(open(os.path.join(SIMS, 'sim2.json'), encoding='utf-8'))
    s3 = json.load(open(os.path.join(SIMS, 'sim3.json'), encoding='utf-8'))
    return s1, s2, s3


def f3(x):
    return f'{x:.3f}'.rstrip('0').rstrip('.') if isinstance(x, float) else str(x)


def facts(s1, s2, s3):
    """地域ごとの事実（数値と出典）"""
    ring = s1['ring10']['0.6']
    x = ring['x']
    tot = sum(x)
    core_i = ring['tiers'].index('中核')
    per_i = ring['tiers'].index('周辺')
    h2 = s2['handoff']
    g3 = s3['games']
    sw = s3['sweep']['周辺']
    ts = s3['timeseries']
    # 周辺の慣行: 退出オプションが閾値を超えるとき（o_F = 0.08）の B の割合。中核は同じ o_F 付近の値
    def freq_at(region, oF):
        r = s3['sweep'][region]
        k = min(range(len(r['oF'])), key=lambda i: abs(r['oF'][i] - oF))
        return r['freq_B'][k], r['oF'][k]
    fbP, oP = freq_at('周辺', ts['oF'])
    fbC, oC = freq_at('中核', ts['oF'])
    # 撤退ハザードの閾値: 周辺で非正規の割合が基準（変動する職の割合）を超え始める h_F
    mob = s2['mobility']
    base = mob['periphery'][0]['nonregular_share']
    hth = next(h for h, r in zip(mob['hF'], mob['periphery']) if r['nonregular_share'] > base + 1e-3)
    out = {}
    for R, key, idx, hF, fb, oF in (('中核', 'core', core_i, h2['hF_core'], fbC, oC),
                                     ('周辺', 'periphery', per_i, h2['hF_periphery'], fbP, oP)):
        hi = h2[key]['high']
        g = g3[R]
        out[R] = {
            'share': x[idx] / tot, 'share_src': f'sim1.json ring10["0.6"] 地域{idx} の工業能力 / 合計',
            'hF': hF, 'hF_src': f'sim2.json handoff.hF_{key}', 'h_threshold': hth,
            'h_threshold_src': 'sim2.json mobility: 周辺の非正規の割合が基準を超え始める h_F',
            'e0': 1 - hi['one_minus_e'], 'q': hi['q'], 'q_src': f'sim2.json handoff.{key}.high.q',
            'wN': hi['w_N'], 'wR': hi['w_R_bar'], 'w_src': f'sim2.json handoff.{key}.high',
            'wB': g['wB'], 'uW': g['uW'], 'g_src': f'sim3.json games.{R}',
            'freqB': fb, 'oF': oF, 'freq_src': f'sim3.json sweep.{R}.freq_B（o_F ≈ {f3(oF)}）',
            'oF_threshold': sw['oF_threshold'], 'piB': g3['周辺']['piB'],
            'P_weak': ts['penalty_weak'], 'P_strong': ts['penalty_strong'],
            'P_need': g3['周辺']['piB'] - ts['oF'],
            'nonreg': hi['nonregular_share'],
            'stable_nr_foreign': hi['stable_nonregular_foreign'],
            'stable_nr_domestic': hi['stable_nonregular_domestic'],
            'stable_src': f'sim2.json handoff.{key}.high.stable_nonregular_foreign / _domestic',
        }
    return out


def mark(cond):
    return '+' if cond else '!'


def concl(ok, effect, fail):
    """Matcha の約束: 成立（+）した主張の >> には効果を、不成立（!）の主張の >> には不成立からの帰結を書く"""
    return effect if ok else fail


NORMAL = '期間の定めのない雇用が通常である'          # 雇用形態: 事実上の規範秩序（何が「通常」とされるか）
OUGHT = '非正規の賃金は正規より低くてよい'           # 賃金: 法的評価（当為）
IS = '非正規の賃金は実際に正規より低い'              # 賃金: 事実（存在）


def employment(R, F, unknown=False):
    """雇用形態（事実上の規範秩序）: 中核の雇用慣行を原則とし、周辺を例外とする書き方（Grok 会話の「中央＝デフォルト」）。
    退出オプションを持つのは外資なので、対象は「外資の安定した職」とする。"""
    t = f'{R}の外資の安定した職'
    L = [f':: 雇用形態（{R}）―― 事実上の規範秩序として']
    L.append(f'#雇用安定の原則^中核の雇用慣行（労働契約法18条・労働者派遣法25条の趣旨を反映） <= {t}: (')
    L.append(f'    「業務が恒常的」 <= {R}の外資のこの職は需要の変動にさらされない')
    L.append(f') >> {NORMAL} as 雇用安定_{R}')
    L.append('')
    if unknown:
        L.append('// 地域の位置と外資の撤退ハザードが分からない場合（事実を書かない）')
        L.append(f'#周辺例外^世界システム上の位置（事実上の規範） <= {t}: (')
        L.append('    %周辺に位置する')
        L.append('    %外資の退出オプションがある')
        L.append(f') >> !{NORMAL} as 周辺例外_{R} !> $雇用安定_{R}')
        return '\n'.join(L) + '\n'
    per = F['share'] < 0.05
    exitopt = F['hF'] > F['h_threshold']
    ok = per and exitopt
    L.append(f'{mark(ok)}#周辺例外^世界システム上の位置（事実上の規範） <= {t}: (')
    L.append(f'    // 出典: {F["share_src"]} = {f3(F["share"])}')
    L.append(f'    {mark(per)}%周辺に位置する <= {R}の工業能力の世界シェアは{f3(F["share"])}である@'
             + ('周辺である' if per else '周辺ではない'))
    L.append(f'    // 出典: {F["hF_src"]} = {f3(F["hF"])}、閾値は {F["h_threshold_src"]} = {f3(F["h_threshold"])}')
    L.append(f'    {mark(exitopt)}%外資の退出オプションがある <= {R}の外資の撤退ハザード{f3(F["hF"])}は閾値{f3(F["h_threshold"])}を'
             + ('上回る@いつでも引き上げられる' if exitopt else '下回る@退出の脅しは雇用形態を左右しない'))
    if ok:
        L.append(f'    // 出典: {F["stable_src"]} = {f3(F["stable_nr_foreign"])} / {f3(F["stable_nr_domestic"])}')
        L.append(f'    +%正規が通常でなくなっている <= {R}の外資の安定した職の{f3(F["stable_nr_foreign"])}が非正規で、'
                 f'国内資本の{f3(F["stable_nr_domestic"])}と際立って異なる@外資の職では正規は通常ではない')
    L.append(f') >> {concl(ok, "!" + NORMAL, f"{R}では周辺例外は認められない")}'
             f' as 周辺例外_{R} !> $雇用安定_{R}')
    return '\n'.join(L) + '\n'


def inverted(R, F, unknown=False):
    """デフォルトを反転した理論: 非正規が通常で、正規は中核の特権という例外"""
    t = f'{R}の外資の安定した職'
    L = [f':: 雇用形態（{R}）―― デフォルトを反転した理論']
    L.append(f'#非正規原則^世界経済の慣行（事実上の規範） <= {t}')
    L.append(f'    >> !{NORMAL} as 非正規原則_{R}')
    L.append('')
    if unknown:
        L.append(f'#中核特権^世界システム上の位置 <= {t}: (')
        L.append('    %中核に位置する')
        L.append('    %外資の退出オプションがない')
        L.append(f') >> {NORMAL} as 中核特権_{R} !> $非正規原則_{R}')
        return '\n'.join(L) + '\n'
    core = F['share'] >= 0.5
    noexit = F['hF'] <= F['h_threshold']
    L.append(f'{mark(core and noexit)}#中核特権^世界システム上の位置 <= {t}: (')
    L.append(f'    // 出典: {F["share_src"]} = {f3(F["share"])}')
    L.append(f'    {mark(core)}%中核に位置する <= {R}の工業能力の世界シェアは{f3(F["share"])}である@'
             + ('中核である' if core else '中核ではない'))
    L.append(f'    // 出典: {F["hF_src"]} = {f3(F["hF"])}')
    L.append(f'    {mark(noexit)}%外資の退出オプションがない <= {R}の外資の撤退ハザード{f3(F["hF"])}は閾値{f3(F["h_threshold"])}を'
             + ('下回る@退出の脅しは雇用形態を左右しない' if noexit else '上回る@いつでも引き上げられる'))
    L.append(f') >> {concl(core and noexit, NORMAL, f"{R}では中核特権は認められない")}'
             f' as 中核特権_{R} !> $非正規原則_{R}')
    return '\n'.join(L) + '\n'


def wage(R, F, which=('補償', '身分')):
    """賃金: 当為（法的評価）の層で補償原則と身分秩序（民法92条）が対立し、存在（事実）の層で慣行が続く"""
    t = f'{R}の非正規の労働契約'
    L = [f':: 非正規の賃金（{R}）']
    if '補償' in which:
        L.append(f'#補償原則^補償賃金差の原則（Smith『国富論』第1編第10章、Rosen 1986） <= {t}: (')
        L.append(f'    // 出典: sim2.json の e0（非正規の層の固有の不就業率） = {f3(F["e0"])}')
        L.append(f'    %雇用が不安定 <= {R}の非正規の層は契約の切れ目で{f3(F["e0"])}の割合で職がない@危険を負っている')
        L.append(f') >> !{OUGHT} as 補償原則_{R}')
        L.append('')
    if '身分' in which:
        custom = F['freqB'] >= 0.9
        accept = F['wB'] > F['uW']
        ok = custom and accept
        L.append('// 当為の層: 任意法の領域で、慣習による意思があれば慣習に従う（民法92条）')
        L.append(f'{mark(ok)}#身分秩序^民法92条（事実たる慣習） <= {t}: (')
        L.append(f'    // 出典: {F["freq_src"]} = {f3(F["freqB"])}')
        L.append(f'    {mark(custom)}%慣習が成立している <= {R}で成立した契約のうち身分秩序によるものの割合は{f3(F["freqB"])}である@'
                 + ('慣習が成立している' if custom else '慣習は成立していない'))
        L.append(f'    // 出典: {F["g_src"]}.wB = {f3(F["wB"])}、uW = {f3(F["uW"])}（正規職の列に並ぶ価値）')
        L.append(f'    {mark(accept)}%慣習による意思がある <= {R}の身分賃金{f3(F["wB"])}は正規職の列に並ぶ価値{f3(F["uW"])}を'
                 + ('上回る@労働者は身分賃金を受け入れる' if accept else '下回る@労働者は身分賃金を受け入れない'))
        L.append(f') >> {concl(ok, OUGHT, f"{R}では身分秩序による賃金の切り下げは認められない")} as 身分秩序_{R}')
        L.append('')
        L.append('// 存在の層: 慣行が事実として続いているか')
        L.append(f'{mark(custom)}#身分秩序の実態^Sim3の観測 <= {t}: (')
        L.append(f'    {mark(custom)}%慣行が続いている <= {R}で成立した契約のうち身分秩序によるものの割合は{f3(F["freqB"])}である@'
                 + ('身分秩序の慣行が続いている' if custom else '身分秩序の慣行はない'))
        L.append(f') >> {concl(custom, IS, f"{R}では非正規の賃金が実際に低いとはいえない")} as 実態_{R}')
    return '\n'.join(L) + '\n'


def cand_status(R):
    """アブダクションの候補: 身分秩序を、要件なしの普遍的な規範として立てる"""
    t = f'{R}の非正規の労働契約'
    return '\n'.join([f':: 非正規の賃金（{R}）―― 候補: 身分秩序のみ（普遍的な規範）',
                       f'#身分秩序^身分による賃金の序列（普遍的な規範として） <= {t}',
                       f'    >> {OUGHT} as 身分秩序_{R}']) + '\n'


def power(F):
    """力による優先順位（Sim 3: 企業の退出オプションが閾値を超えると、身分秩序がリスク支配的になる）"""
    L = [':: 力による優先順位（周辺）',
         f'// 出典: sim3.json timeseries.oF = {f3(F["oF"])} は sweep.周辺.oF_threshold = {f3(F["oF_threshold"])} を上回る。',
         '// このとき適応的プレイで確率的に安定なのは身分秩序であり、論理の外（力関係）から優先順位が与えられる。',
         ':: 優先 $身分秩序_周辺 > $補償原則_周辺']
    return '\n'.join(L) + '\n'


def law(R, F, strong):
    """法的介入: パート有期法9条（差別的取扱いの禁止＝均等待遇）。
    当為の層: 強行規定なので、民法92条の慣習（身分秩序）に常に優る（効力、de jure）。
    存在の層: 執行が身分秩序を維持できなくする水準を超えるときにだけ、慣行が崩れる（実効性、de facto）。"""
    t = f'{R}の非正規の労働契約'
    P = F['P_strong'] if strong else F['P_weak']
    ok = P > F['P_need']
    L = [f':: 法的介入（{R}、{"強い" if strong else "弱い"}執行）']
    L.append('// 当為の層（効力）: 強行規定は事実たる慣習に優る')
    L.append(f'+#均等待遇^パート有期法9条（強行規定） <= {t}: (')
    L.append(f'    +「通常の労働者と同視すべき短時間・有期雇用労働者」: (')
    L.append(f'        // 出典: {F["stable_src"]} = {f3(F["stable_nr_foreign"])}（安定した職、つまり正規と同じ職務を非正規が担っている）')
    L.append(f'        +「職務の内容が通常の労働者と同一」 <= {R}の外資の安定した職の{f3(F["stable_nr_foreign"])}を非正規が担っている@正規と同じ職務を担っている')
    L.append('        // 仮定: Sim 2 の安定した職は、正規・非正規を問わず同じ職に継続して配置される（モデルの設定）')
    L.append(f'        +「職務の内容及び配置の変更の範囲が通常の労働者と同一の範囲で変更されると見込まれる」 <= {R}の非正規も同じ安定した職に継続して配置される@配置の変更の範囲が同一')
    L.append('    )')
    L.append(f') >> !{OUGHT} as 均等待遇_{R} !> $身分秩序_{R}')
    L.append('')
    L.append('// 存在の層（実効性）: 執行の強さが慣行を崩すか')
    L.append(f'{mark(ok)}#均等待遇の実効^パート有期法9条の執行 <= {t}: (')
    L.append(f'    // 出典: sim3.json timeseries.penalty_{"strong" if strong else "weak"} = {f3(P)}、'
             f'身分秩序を維持できなくする水準 π_B − o_F = {f3(F["P_need"])}')
    L.append(f'    {mark(ok)}%実効的な執行 <= {R}での執行による身分秩序の利潤の減少{f3(P)}は維持できなくする水準{f3(F["P_need"])}を'
             + ('上回る@身分秩序を維持できない' if ok else '下回る@身分秩序は慣性で続く'))
    L.append(f') >> {concl(ok, "!" + IS, f"{R}では均等待遇は実効を欠く")} as 均等待遇の実効_{R} !> $実態_{R}')
    return '\n'.join(L) + '\n'


HEADER = ('// このファイルは argument/build_argument.py が sims/out/*.json から生成した。手で直さない。\n'
          '// Matcha-D（非公式の拡張: as / !> / >> not・>> !）で書いている。\n')


def main():
    s1, s2, s3 = load()
    F = facts(s1, s2, s3)
    files = {
        'employment_core.matcha': employment('中核', F['中核']),
        'employment_periphery.matcha': employment('周辺', F['周辺']),
        'employment_unknown.matcha': employment('地域U', None, unknown=True),
        'inverted_core.matcha': inverted('中核', F['中核']),
        'inverted_periphery.matcha': inverted('周辺', F['周辺']),
        'inverted_unknown.matcha': inverted('地域U', None, unknown=True),
        'wage_core.matcha': wage('中核', F['中核']),
        'wage_periphery.matcha': wage('周辺', F['周辺']),
        'power_periphery.matcha': power(F['周辺']),
        'law_periphery_weak.matcha': law('周辺', F['周辺'], strong=False),
        'law_periphery_strong.matcha': law('周辺', F['周辺'], strong=True),
        # アブダクションの候補（規範の組）
        'cand_compensation_core.matcha': wage('中核', F['中核'], which=('補償',)),
        'cand_compensation_periphery.matcha': wage('周辺', F['周辺'], which=('補償',)),
        'cand_status_core.matcha': cand_status('中核'),
        'cand_status_periphery.matcha': cand_status('周辺'),
    }
    for name, text in files.items():
        with open(os.path.join(HERE, name), 'w', encoding='utf-8') as f:
            f.write(HEADER + text)
    with open(os.path.join(HERE, 'facts.json'), 'w', encoding='utf-8') as f:
        json.dump(F, f, ensure_ascii=False, indent=1)
    print('\n'.join(files))


if __name__ == '__main__':
    main()
