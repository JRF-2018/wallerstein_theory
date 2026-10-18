# -*- coding: utf-8 -*-
"""IPYNB: 第 9 章（シミュレーションから Matcha-D へ）、第 10 章（分析）"""
from nbtools import md, code, writefile

THEORIES = [
    ('T1_employment', 'employment_core employment_periphery employment_unknown'),
    ('T1i_inverted', 'inverted_core inverted_periphery inverted_unknown'),
    ('T2_wage', 'wage_core wage_periphery'),
    ('T3_power', 'wage_core wage_periphery power_periphery'),
    ('T4w_law_weak', 'wage_core wage_periphery power_periphery law_periphery_weak'),
    ('T4s_law_strong', 'wage_core wage_periphery power_periphery law_periphery_strong'),
    ('T5_cand_compensation', 'cand_compensation_core cand_compensation_periphery'),
    ('T6_cand_status', 'cand_status_core cand_status_periphery'),
]


def ch9():
    md(r'''
## 9. シミュレーションから Matcha-D へ

### 9.1 機械的な変換と、その出典

`argument/build_argument.py` は、シミュレーションの結果（`sims/out/*.json`）を読み、第 3 部の論証の `.matcha` を生成する。

この生成器は汎用の道具ではなく、本レポートの論証のためだけに書いた使い捨てのコードである。それでも、`.matcha` を手で（あるいは AI に直接）書かせずに、わざわざ生成器を介した理由がある。

> AI を使うけれども、システムにはできる限り **AI が生成した決定論的コード**を使い、後から検証（注意労働）できるようにしておく。

これがこれからのセオリーだと本レポートは考える。AI に `.matcha` を直接書かせると、数値の転記や閾値との比較の誤りが、どこで入ったかを後から追えない。生成器にしておけば、どの数値がどの JSON から来て、どの比較で `+`／`!` が決まったかを、コードを読めば誰でも確かめられる。シミュレーションのパラメータを変えれば、論証も同じ手続きで作り直せる。AI の判断が本当に必要なところ（事実から評価へのあてはめ）だけが `[ai]` に残る。

- 各事実（`<=` の後）には数値をそのまま書き、直前の `//` コメントに出典（JSON のどの値か）を示す。
- 数値から法的概念への橋渡しは `@評価` として書く（例: 「撤退ハザード 0.25 は閾値 0.09 を上回る@いつでも引き上げられる」）。これが AI の審査の対象になる **neuro の部分**である。
- 閾値との比較で要件の成否（`+`／`!`）を決める。これは生成器（著者）の主張で、mext が Extension と照合する。
- Matcha の約束に従い、不成立の主張の `>>` には不成立からの帰結を書く。
- Matcha には変数がないので、規範は地域（中核・周辺・事実の分からない地域U）ごとの事件として具体化する。
- 賃金の論証は二層に分ける。**当為**（法的評価: 「非正規の賃金は正規より低くてよい」）と、**存在**（事実: 「非正規の賃金は実際に正規より低い」）である。
''')
    writefile('argument/build_argument.py')
    code(r'''
!python3 argument/build_argument.py
''')
    md(r'''
生成されたファイルの例（周辺の雇用形態、周辺の賃金、弱い執行の法的介入）:
''')
    code(r'''
!cat argument/employment_periphery.matcha
!cat argument/wage_periphery.matcha
!cat argument/law_periphery_weak.matcha
''')
    md(r'''
### 9.2 理論の組み立て

Matcha には import がないので、一つの理論を複数のファイルで書く場合は、MEXT のヘッダに `theory:` を複数行書く（`mext init A.matcha B.matcha -o X.mext`）。ラベルの名前空間は共有され、別ファイルの主張を `!> $ラベル` や `:: 優先` で指せる。

| 理論 | 内容 |
|---|---|
| T1 | 雇用形態（中核の雇用慣行を原則、周辺を例外とする） |
| T1i | デフォルトを反転した理論（非正規を原則、正規を中核の特権とする） |
| T2 | 賃金（補償原則と身分秩序の対立） |
| T3 | T2 ＋ 力による優先順位（Sim 3） |
| T4w / T4s | T3 ＋ 均等待遇（パート有期法 9 条）。弱い執行／強い執行 |
| T5 / T6 | アブダクションの対抗候補（補償原則のみ／身分秩序のみ） |
''')
    src = "THEORIES = [\n" + ''.join(f"    ('{t}', '{fs}'),\n" for t, fs in THEORIES) + "]\n"
    src += r'''OBS = ('観測*: -"非正規の賃金は正規より低くてよい〔中核の非正規の労働契約〕", '
       '"非正規の賃金は正規より低くてよい〔周辺の非正規の労働契約〕"  ; Sim 3 で観測された、当事者に受け入れられている規範')
!python3 -m mext.matcha_check --shared-labels --quiet argument/wage_core.matcha argument/wage_periphery.matcha argument/power_periphery.matcha argument/law_periphery_weak.matcha
for t, fs in THEORIES:
    files = ' '.join(f + '.matcha' for f in fs.split())
    !cd argument && python3 -m mext init {files} -o {t}.mext > /dev/null
    if t in ('T2_wage', 'T3_power', 'T5_cand_compensation', 'T6_cand_status'):
        p = f'argument/{t}.mext'
        s = open(p, encoding='utf-8').read()
        s = re.sub(r'\[claimed\]\n(;[^\n]*\n)*', '[claimed]\n' + OBS + '\n', s, count=1)
        open(p, 'w', encoding='utf-8').write(s)
    !cd argument && python3 -m mext solve {t}.mext
'''
    code(src)
    md(r'''
### 9.3 各理論の結論

各理論の preferred Extension の懐疑的帰結（すべてで成り立つ結論）と、信憑的にしか成り立たない結論を、事件（地域）ごとにまとめる。
''')
    code(r'''
from mext import core as mx
targets = ['中核の外資の安定した職', '周辺の外資の安定した職', '地域Uの外資の安定した職',
           '中核の非正規の労働契約', '周辺の非正規の労働契約']
rows = []
for t, _ in THEORIES:
    mf = mx.MextFile(f'argument/{t}.mext').load()
    th, _ = mx.build(mf)
    ex, pr, _ = mx.solve(th)
    sk, cr = mx.summarize(th, ex, pr)
    for tg in targets:
        lits = lambda S: [l for l in (S or []) if th.by_id[abs(l)].kind == 'concl' and th.by_id[abs(l)].text.endswith(f'〔{tg}〕')]
        ks = lits(sk)
        cs = [l for l in lits(cr) if l not in (sk or [])]
        if ks or cs:
            rows.append(f"| {t} | {tg} | {'；'.join(th.lit_text(l).split('〔')[0] for l in ks) or '―'} | "
                        f"{'；'.join(th.lit_text(l).split('〔')[0] for l in cs) or '―'} |")
    print(f'{t}: Extension {len(ex)} 個、preferred {sum(pr)} 個')
display(Markdown('| 理論 | 事件 | 懐疑的帰結 | 信憑的にのみ |\n|---|---|---|---|\n' + '\n'.join(rows)))
''')


def ch10():
    md(r'''
## 10. 分析

### 10.1 デフォルトとは「情報がないときに成り立つもの」であり、立証責任の配分である

T1（中核が原則）と T1i（非正規が原則）は、**事実の分かっている中核と周辺について、まったく同じ結論を出す**。違うのは、事実の分からない地域U についてだけである（T1 では正規、T1i では非正規）。

`explain` で見ると、その理由が分かる。T1 では、地域U の周辺例外は「あてはめる事実が書かれていない」ために働かない。
''')
    code(r'''
def pref_ext(path):
    mf = mx.MextFile(path).load(); th, _ = mx.build(mf); ex, pr, _ = mx.solve(th)
    return f'E{pr.index(True) + 1}'
E = pref_ext('argument/T1_employment.mext')
!python3 -m mext explain argument/T1_employment.mext {E} "#周辺例外^世界システム上の位置（事実上の規範） [周辺例外_地域U]" --depth 4
E = pref_ext('argument/T1i_inverted.mext')
!python3 -m mext explain argument/T1i_inverted.mext {E} "#中核特権^世界システム上の位置 [中核特権_地域U]" --depth 4
''')
    md(r'''
- T1 では、例外を主張する側（使用者）が「周辺に位置する」と「外資の退出オプションがある」を立証しなければならない。
- T1i では、逆に正規雇用を主張する側（労働者）が「中核に位置する」と「退出オプションがない」を立証しなければならない。

「中核＝デフォルト、周辺＝例外」（Grok 会話）という書き方は、記述として正しいかどうかの問題ではない。**立証責任をどちらに負わせるか**という規範的な選択である。

ウォーラーステインの「周辺は例外ではなく、システムに構造的に必要な部分」という論点は、形式的には次のように読める。

- デフォルトと例外の割り当ては事実からは決まらない（T1 と T1i は既知の事実について同値）。
- その割り当ては中核の視点によって選ばれている。中核のイデオロギーとしての自由主義（川北編 p.76）は、「中核の慣行を通常とし、周辺の慣行を説明を要する例外とする」視点にあたる。

### 10.2 規範の対立と、論理の外から来る優先順位

- T2 では、周辺の非正規の賃金について、補償原則と身分秩序（民法 92 条の事実たる慣習）がどちらも適用されうる。結論は二つの preferred Extension に分かれる（Nixon diamond）。
- 優先順位はデフォルト論理の内部では決まらない。T3 は、Sim 3 の結果（企業の退出オプションが閾値を超えると、身分秩序がリスク支配的になる）を根拠に、`:: 優先` を外から与えている。
- 中核では、そもそも対立が生じない。身分秩序の要件「慣習による意思がある」が、事実（身分賃金 2.209 < 正規職の列に並ぶ価値 2.548）によって否定されるからである。

**市場（労働余剰）が規範の適用の前提（要件）を決め、力（退出オプション）が規範の間の優先順位を決める**。

スキルによる T3 の審査を示す（求解していない `.mext` を渡したので、AI の予測は結果を見ないで行われた）。
''')
    code(r'''
claude_skill('notebook_runs/T3_power/T3_power.mext', 'notebook_runs/T3_power')
''')
    code(r'''
show_md('notebook_runs/T3_power/T3_power.report.md', sections=['2.', '6.', '8.', '10.'], max_lines=170)
''')
    md(r'''
### 10.3 慣習と法: 効力（当為）と実効性（存在）

パート有期法 9 条（通常の労働者と同視すべき短時間・有期雇用労働者に対する差別的取扱いの禁止＝均等待遇）は強行規定である。民法 92 条の事実たる慣習は、任意規定と異なる慣習にしか効力を持たない。

- **当為の層**: 9 条は身分秩序に常に優る。T4w でも T4s でも、周辺の当為の結論は「低くてはならない」になる。
- **存在の層**: 執行の強さが慣行の持続を決める（Sim 3 の慣習の慣性）。
  - 弱い執行では「均等待遇の実効」の要件が否定され、「実際に低い」が残る。
  - 強い執行では「実際に低くない」に変わる。

T4w は、「法の上では許されないが、事実としては切り下げが続く」という状態（Kelsen の効力と実効性の乖離）を、**二つの層の結論の食い違い**として形式的に示している。

**この区別は、AI の審査によって見つかった**。

- 最初の版（`argument/skill_runs_v1/`）は、9 条の効力そのものを執行の強さで外していた。スキルの審査は、これを「実効と効力の混同（最重要）」と指摘した。9 条は強行規定で民法 92 条の慣習に優る、というのがその根拠である。
- 同時に、「均衡待遇」という呼び名の誤り（9 条は均等待遇、均衡待遇は 8 条）、存在から当為を導いている箇所、事実の原子が地域をまたいで共有されている問題も指摘された。
- これを受けて生成器を直した。決定論的な検査（構文・Extension・Lean）では見つからない種類の誤りを、AI の実質審査が見つけ、人と生成器が直す。本レポートの neuro-symbolic な分業が働いた実例である。
''')
    code(r'''
show_md('argument/skill_runs_v1/T4w_law_weak/T4w_law_weak.report.md', sections=['10.'], max_lines=40)
''')
    md(r'''
改訂後の T4w に対するスキルの審査:
''')
    code(r'''
claude_skill('notebook_runs/T4w_law_weak/T4w_law_weak.mext', 'notebook_runs/T4w_law_weak')
''')
    code(r'''
show_md('notebook_runs/T4w_law_weak/T4w_law_weak.report.md', sections=['4.', '6.', '10.'], max_lines=170)
''')
    md(r'''
### 10.4 アブダクション: 観測された慣行を説明する規範はどれか

観測（Sim 3）は「中核では非正規の賃金は低くない（B 0%）、周辺では低い（B 97%）」である。これを `[claimed]` に書き、候補となる規範の組を `verify` で検査する。

- 信憑的（いずれかの preferred Extension で成り立つ）と、懐疑的（すべてで成り立つ）の両方を見る。
- 事実 → 評価（判例・慣習）→ 規範、というアブダクション（Grok 会話の論点）を、「候補の規範が観測された評価を Extension として再現するか」という形で検査できる。
''')
    code(r'''
rows = []
for t, label in (('T5_cand_compensation', '補償原則のみ'), ('T6_cand_status', '身分秩序のみ（普遍的な規範として）'),
                 ('T2_wage', '補償原則 ＋ 身分秩序（要件付き）'), ('T3_power', '補償原則 ＋ 身分秩序 ＋ 力による優先順位')):
    a = subprocess.run(['python3', '-m', 'mext', 'verify', f'argument/{t}.mext'], capture_output=True, text=True).stdout
    b = subprocess.run(['python3', '-m', 'mext', 'verify', '--skeptical', f'argument/{t}.mext'], capture_output=True, text=True).stdout
    rows.append(f"| {label}（{t}） | {'✓' if 'OK' in a else '✗'} | {'✓' if 'OK' in b else '✗'} |")
display(Markdown('| 候補の規範の組 | 観測と両立（信憑的） | 観測を導く（懐疑的） |\n|---|---|---|\n' + '\n'.join(rows)))
''')
    md(r'''
観測を導くのは、事実を要件とする慣習（身分秩序）に、力から来る優先順位を加えた組だけである。

### 10.5 雇用形態の論証への審査

雇用形態の理論 T1 に対するスキルの審査を示す。
''')
    code(r'''
claude_skill('notebook_runs/T1_employment/T1_employment.mext', 'notebook_runs/T1_employment')
''')
    code(r'''
show_md('notebook_runs/T1_employment/T1_employment.report.md', sections=['6.', '8.', '10.'], max_lines=160)
''')
    md(r'''
### 10.6 周辺の不平等は中核に及ばない、の意味

- Sim 1 の需要の経路では、周辺の所得の総額へのショックは中核にも波及した（正直に記録した結果）。
- しかし賃金の規範については、中核と周辺は分離されている。中核の結論は、どの理論（T2〜T4s）でも同じである。周辺の慣行がどう変わっても、中核の Extension は変わらない。
- 周辺の身分賃金による差額は、外資を通じて中核に移転する（Sim 2）。
''')
