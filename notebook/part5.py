# -*- coding: utf-8 -*-
"""IPYNB: 第 11 章（Lean）、第 12 章（考察と限界）、第 13 章（参考文献・付録）"""
from nbtools import md, code, writefile
from part4 import THEORIES


def ch11():
    md(r'''
## 11. Lean による一括検証

Lean 4（v4.34.1）と Mathlib で、次の 5 種類のことを示す。ファイルを `%%writefile` で書き出し、最後に `lake build` でまとめて検査する。

1. **Sim 1**（`CorePeriphery.lean`）:
   - 差の分解 h(y) − h(x) = (y−x)(a − bxy) / (正の分母)。
   - h は [0, √(a/b)] で狭義増加、[√(a/b), ∞) で狭義減少（逆 U 字形）。
   - 不安定化の条件 K h(φ) > 1 ⟺ bφ² + (a+b−K)φ + a < 0。本レポートの値では 3φ² − 6φ + 1 < 0。
2. **Sim 2**（`LaborMarket.lean`）:
   - w_N < w̄_R ⟺ q < c、および q < c ⟺ λ < c（c = 1 − e₀。非正規の割合 ν が消える）。
   - 労働余剰がなければ補償賃金になる。
3. **Sim 3**（`Convention.lean`）:
   - リスク支配度は退出オプションについて狭義増加する。
   - 閾値の公式と、法的介入で A がリスク支配的になる条件。
4. **MEXT の検査器の健全性**（`MextSpec.lean`）:
   - Bool の判定 `isExtension T E = true` から、Reiter の Extension の定義 `ReiterExtension T E` が従う。E が無矛盾で、W を含み、規則と正当化が E と無矛盾なデフォルトとで閉じた最小の集合である、ということである。
   - 反復回数（規則の数 + デフォルトの数 + 1）で不動点に達することを、鳩の巣原理で示す。
   - 証明の方針と補題の分割は Claude Opus 5.5 が作り、証明は Claude Sonnet 5.5 のサブエージェントが書いた。
5. **第 3 部の各理論の Extension**（`Arg*.lean`、`mext lean --import-spec` で生成）: 各 Extension が Reiter の Extension であること。

これで示せるのは、列挙された各集合が Extension であること（健全性）である。列挙が漏れなくなされていること（完全性）は mext のアルゴリズムに依存する。
''')
    writefile('lakefile.lean')
    writefile('WallersteinTheory/CorePeriphery.lean')
    writefile('WallersteinTheory/LaborMarket.lean')
    writefile('WallersteinTheory/Convention.lean')
    writefile('WallersteinTheory/MextSpec.lean')
    src = "for t, _ in THEORIES:\n"
    src += "    n = re.sub(r'_([a-z])', lambda m: m.group(1).upper(), t)\n"
    src += "    !python3 -m mext lean argument/{t}.mext --import-spec WallersteinTheory.MextSpec --namespace {n} -o WallersteinTheory/Arg{n}.lean\n"
    src += "!python3 -m mext lean examples/tweety.mext --import-spec WallersteinTheory.MextSpec --namespace Tweety -o WallersteinTheory/ExampleTweety.lean\n"
    src += "!tail -12 WallersteinTheory/ArgT4wLawWeak.lean\n"
    code(src)
    writefile('WallersteinTheory.lean')
    code(r'''
if RUN_LEAN:
    # Colab などで初めて実行する場合は、Mathlib のキャッシュを取得する（数 GB）
    !lake exe cache get > /dev/null 2>&1
    !lake build 2>&1 | grep -v "^✔" | tail -5
    open('/tmp/axioms.lean', 'w').write('import WallersteinTheory\n'
        '#print axioms Mext.isExtension_sound\n'
        '#print axioms Mext.ArgT4wLawWeak.E2_reiter\n'
        '#print axioms WallersteinTheory.LaborMarket.inversion_iff_labor_surplus\n'
        '#print axioms WallersteinTheory.CorePeriphery.h_strictAntiOn\n'
        '#print axioms WallersteinTheory.Convention.penalty_reverses\n')
    !lake env lean /tmp/axioms.lean
else:
    print('RUN_LEAN = False なので省略')
''')
    md(r'''
依存する公理は、Lean の標準の 3 つ（propext、Classical.choice、Quot.sound）だけである。`sorry` は使っていない。

`decide +kernel` はカーネルによる評価なので、`native_decide` のようにコンパイラを信頼する公理（`Lean.ofReduceBool`）も入らない。
''')


def ch12():
    md(r'''
## 12. 考察と限界

### 12.1 形式化によって見えるようになった留保

決定論的な検査（構文、Extension、Lean）はすべて通っている。そのうえで、AI の審査が指摘し、形式化によって人が追えるようになった留保は二つの場所に集まっている。

1. **事実から評価へのあてはめ**（neuro の部分）。
   - 周辺例外の根拠: 外資の安定した職のうち非正規は 0.497 で、過半に届かない。「国内資本（0）と際立って異なるので、外資の職では正規は通常ではない」という評価は争いうる。撤退ハザードを 0.35 にすれば過半を超えるが、Sim 2 と Sim 3 で揃えている値（0.25）を変えることになる。
   - 周辺の身分秩序の要件「慣習による意思がある」: 外部機会が乏しいために身分賃金を受け入れざるを得ないことを、民法 92 条の任意の「意思」と読んでよいか（窮迫による受諾）。試算では、受け入れを強いられたものとすると、力による優先順位があっても補償原則が勝つ（`notebook_runs/T3_power/`）。
2. **優先順位の出どころ**（論理の外）。T3 の `:: 優先 $身分秩序_周辺 > $補償原則_周辺` には、法的な根拠がない。その根拠は、Sim 3 が示す力関係（退出オプション）である。

これらは本レポートの論証の弱点である。同時に、本レポートが**形式化によって可視化したかったもの**でもある。

- 「周辺では身分秩序が通る」という結論が、どの評価とどの力関係に支えられているかが、行番号と原子の名前で特定できる。
- 反論する側が何を立証すればよいかも、特定できる（`explain` と試算）。

### 12.2 アレーティアと弁証法

Gemini・Grok との会話で JRF は、規範の存在を「ある規範が特定の事例に適用できること」で示すという考え（アレーティア、弁証法）を提起した。本レポートの枠組みでは、次のように対応する。

- **アレーティア**: Matcha の `%定義 <= 事実@評価` は、抽象的な規範（`%定義`）が具体的な事実と交差し、評価を経て結論として現れる過程である。本レポートでは、その評価を争いうるデフォルトとし、AI が審査した。規範の「開示」は、形式の外の判断を経て初めて起こる。
- **弁証法**: Sim 3 は、事実（反復される契約）から規範（慣習）が生じ、法（強行規定）がそれと衝突し、存在と当為が分離する過程を示した。形式言語はこの過程そのものを記述しない。各段階で成り立つ規範の体系（Extension）を記述し、その間の移行をシミュレーションに委ねる。Grok の会話の言い方でいえば、「規範の適用は形式言語で、規範の生成・変化はシミュレーションで」という分業である。

### 12.3 モデルの限界

- **Sim 1**: 賃金費用を入れても安定した三層構造は出なかった。半周辺は移行期と「二つの中核の間」にだけ現れる。周辺の所得の総額へのショックは中核に波及する。
- **Sim 2**: 補償賃金と身分賃金の双安定は出なかった。反転の条件は労働余剰だけで決まり、資本の移動性は量と深さを決める。これは定式化（Harris–Todaro 型の無差別条件）に強く依存している。
- **Sim 3**: Young の適応的プレイの結果は、誤りの確率と見本の大きさに依存する。リスク支配の閾値（解析）と、シミュレーションでの転換点はわずかにずれた。
- **パラメータ**: いずれのモデルも、パラメータは例示のための値であり、実証的に推定したものではない。日本の「内なる周辺化」は仮説の例示にとどまる。
- **AI の判断**: AI の判断は確率的であり、同じ入力でも揺れうる。本レポートは、AI の判断を `[ai]` に理由付きで記録し、決定論的な部分から分離した。これで揺れの範囲を監査できるようにした。審査を反映しない版（asis）と試算（alt）も残している。

### 12.4 今後の課題

- ヘゲモニーの循環（コンドラチェフ波）のシミュレーション（計画では任意とした Sim 4）。
- 実データ（非正規雇用率、外資比率、交易条件）による較正。
- Matcha-D の、複数の事件にまたがる規範（変数）の扱い。
- Extension の列挙の完全性の Lean による証明。
''')


def ch13():
    md(r'''
## 13. 参考文献・付録
''')
    code(r'''
show_md('docs/references.md')
''')
    md(r'''
### 付録 A: ファイルの一覧

| パス | 内容 |
|---|---|
| `sims/` | シミュレーション（Sim 1〜3）、図（`fig/`）、数値（`out/`）、要約（`SUMMARY.md`） |
| `argument/` | 第 3 部の生成器（`build_argument.py`）、生成した `.matcha`、理論の `.mext`、分析（`ANALYSIS.md`）、AI の審査の記録（`skill_runs_v1/`: 改訂前、`skill_runs/`: 改訂後） |
| `notebook_runs/` | このノートブックで表示する、スキルの CLI 実行の記録 |
| `examples/` | Matcha-D の例題 |
| `tests/` | 構文チェッカのテストのコーパス（Elecode・花房氏の例を引用元つきで含む）、スキルの試験の記録（`skill_runs/`、`skill_runs2/`） |
| `WallersteinTheory/` | Lean の証明 |
| `docs/` | 文法、MEXT の仕様、参考文献、会話ログ（Grok、Gemini） |

道具一式（構文チェッカ、mext、スキル）は https://github.com/JRF-2018/mext にある。

### 付録 B: 作成の過程

- JRF の指示書に従い、まず全体計画を書き、JRF が確認した（指示書と計画書は、ローカルの環境に依存する記述を含むため公開していない）。そのうえで、P1（構文チェッカ）、P2（Extension とスキル）、P3（シミュレーション）、P4（論証）、P5（Lean）、P6（このノートブック）の順に、各段階で JRF の確認を受けた。
- スキルは、文脈を共有しないサブエージェントによる試験（4 件）と CLI による試験（2 回）を経て改訂した。
- 第 3 部の論証は、スキルによる AI の審査（2 回）を経て改訂した。
- Lean の健全性定理は、Claude Sonnet 5.5 のサブエージェントが証明を書いた。

### 付録 C: 会話ログ

- `docs/grok_conversation-20261012.md`: 「法の形式言語とウォーラーステインの世界システム論のモデル」with Grok 4.7
- `docs/gemini_conversation-20261016.md`: 「Matcha とデフォルト論理」with Gemini 3.6 Flash

（AI の回答には誤りが含まれうる。たとえば Grok の挙げた Roberts (2013) は確認できず、本レポートでは使っていない。）
''')
