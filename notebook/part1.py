# -*- coding: utf-8 -*-
"""IPYNB の前半: はじめに、環境構築、第 1 章（法の形式言語）、第 2 章（デフォルト論理）"""
from nbtools import md, code


def front():
    md(r'''
# Matcha を使った neuro-symbolic な法的推論とウォーラーステイン理論
## ―― デフォルト論理で読む周辺の非正規労働

- 文責（Author）: JRF
- 執筆: Claude Opus 5.5（Anthropic）が主として書いた。Lean の健全性定理の証明の一部は Claude Sonnet 5.5 のサブエージェントが書いた。
- 日付: 2026年10月
- リポジトリ: https://github.com/JRF-2018/wallerstein_theory （道具一式は https://github.com/JRF-2018/mext ）
- ライセンス: MIT License

### 要旨

高校の世界史の図録に、世界システム論の「周辺」について次の記述がある。「奴隷や契約労働者など、様々な形の非自由労働が展開した。政治的には、国家機構が弱体化し、外国資本が自由に活動する植民地的な状況がみられる」（『詳説世界史図録』p.167）。本レポートは、この「周辺では非正規の労働が広がる」という命題を、二つの道具で検討する。

1. **シミュレーション**:
   - 中核・半周辺・周辺がどう分かれるか（Sim 1）。
   - その階層の下で、外資の退出オプションと労働余剰が非正規雇用をどう増やすか（Sim 2）。
   - 「リスクを負う非正規ほど高賃金であるべき」という補償賃金の原則が、どう「身分が低いから安くてよい」という慣習へ反転し、定着するか（Sim 3）。
2. **法的推論の形式言語 Matcha とデフォルト論理**:
   - シミュレーションの結果を確定事実として Matcha で書き、デフォルト論理の Extension（矛盾なく保持できる判断の世界）として分析する。
   - 決定論的なプログラム（構文チェック、Extension の計算、Lean による証明）と、AI（Claude）の判断（命題の同一視、あてはめの実質審査）を分け、AI の判断をすべて人が追える形で記録する（neuro-symbolic な法的推論）。

主な結論は次のとおりである。

- (a) 「中核が原則、周辺が例外」という書き方は、事実の分かっている地域では、それを反転した書き方と同じ結論を出す。違うのは事実の分からない地域だけであり、デフォルトとは**立証責任の配分**にほかならない。
- (b) 賃金の規範の対立（補償原則と身分秩序）は、論理の内部では決まらない。**市場（労働余剰）が規範の適用の前提を決め、力（資本の退出オプション）が規範の間の優先順位を決める**。
- (c) 均等待遇（パート有期法 9 条）は強行規定として当為の層では身分秩序に優る。一方、執行が弱ければ、存在の層では慣行が続く。「法の上では許されないが、事実としては切り下げが続く」状態が、**二つの層の結論の食い違い**として形式的に表れる。
- (d) 観測された慣行を説明できる規範の組は、事実を要件とする慣習と、力から来る優先順位を併せたものだけである（アブダクション）。
''')
    md(r'''
### 目次

- 0. はじめに: 問題意識と方法
- 環境構築
- 1. 法の形式言語の現在
- 2. デフォルト論理入門
- 3. Matcha の文法と構文チェッカ
- 4. Matcha-D・MEXT・スキル: デフォルト論理の基盤
- 5. ウォーラーステインの世界システム論
- 6. Sim 1: 中核／半周辺／周辺の創発
- 7. Sim 2: 周辺における非正規雇用
- 8. Sim 3: 事実から慣習規範へ
- 9. シミュレーションから Matcha-D へ
- 10. 分析
- 11. Lean による一括検証
- 12. 考察と限界
- 13. 参考文献・付録
''')
    md(r'''
## 0. はじめに: 問題意識と方法

### 0.1 問題意識

- 図録の記述が高校の世界史に載っているのは、「失われたウン十年」の日本で非正規雇用がなぜ広がったのか、という問題意識が背後にあるからではないか。JRF はそう考えた（JRF のブログ、2026年10月）。
- 川北稔編『知の教科書 ウォーラーステイン』には、「ある国の経済開発は、別のどこかの地域を『低開発化』していることが多い」（p.9）とある。中核国家のイデオロギーとしての自由主義の記述もある（p.76）。
- 「低開発化の是認または押し付け」が非正規雇用の拡大とつながっているのではないか、というのが出発点である。
- ただし、日本についての仮説（「内なる周辺化」）は、本レポートでは Sim 2 の例示として触れるにとどめる。

### 0.2 方法: 形式言語とシミュレーションの分業

Grok との会話（`docs/grok_conversation-20261012.md`）で、形式化の方向は次のように整理された。

- **階層の発生**と**階層の下での労働市場**は、分けてシミュレーションする。
- 法的形式言語は「すでに規範として措定されたルールの記述・適用」が得意で、「事実から規範が生じる過程」は苦手である。
- 一案として「中央をデフォルト、周辺を例外として書く」が考えられる。
- 結論として「**Matcha＋独自の例外記述にして、文法チェック以外は AI に判定してもらう**」方針になった。

Gemini との会話（`docs/gemini_conversation-20261016.md`）では、次のアーキテクチャが固まった。

- デフォルト論理の Extension を AI が「やや曖昧に」構築する。
- 構文チェックは決定論的プログラムで行う。
- Lean は Extension を確定してから使う。

本レポートの設計原理は、**機械「的」に変換された部分を人が追いやすいことに形式化の意義がある**、という点にある。そのため次のようにする。

- シミュレーションの数値から Matcha の事実への変換は、決定論的なスクリプトで行い、各事実に出典（どの数値か）を付ける。
- AI の判断は、MEXT ファイルの `[ai]` 節にすべて理由とともに書く。
- Extension の計算と Lean の証明は、AI の判断から独立に再現できる。
''')


def setup():
    md(r'''
## 環境構築

このノートブックは、リポジトリ https://github.com/JRF-2018/wallerstein_theory のルートで実行することを想定している。必要なものは次のとおり。

- **Python 3.8 以降**、numpy、matplotlib（シミュレーションと図）。
- **mext**（Matcha の構文チェッカとデフォルト論理の道具）: `pip install git+https://github.com/JRF-2018/mext@v0.1.0` 。
  - このノートブックは mext の **v0.1.0**（タグ）で作った。後の版で出力が変わらないよう、版を固定して入れる。任意の文書を分析するスキル（mext分析・matcha分析）などは 0.2.0 以降にある。
- **Claude Code CLI と、スキル matcha-default-extensions**（AI による審査。任意）。
  - Google Colab では、ターミナルで次を実行して Claude Code CLI を入れ、一度 `claude` を起動して認証（authenticate）しておく。

    ```
    BIN_DIR=/usr/local/bin curl -fsSL https://claude.ai/install | sh
    ```

  - スキルは、ターミナルで `claude plugin marketplace add JRF-2018/mext#v0.1.0` と `claude plugin install mext@jrf-mext` を実行して入れる（`#v0.1.0` で版を固定する）。
  - このノートブックでは、`claude` を呼ぶセルの出力として、保存済みの出力（`notebook_runs/`）を表示する。`RUN_CLAUDE = True` にすると実際に呼ぶ（時間と利用料がかかる）。
- **Lean 4 と Mathlib**（第 11 章の一括検証。任意）。
  - Colab では elan を入れ、`lake exe cache get` で Mathlib のキャッシュを取得してから `lake build` する（数 GB の取得が要る）。
  - `RUN_LEAN = True` にすると実行する。
''')
    code(r'''
# Colab で実行する場合は、次の 3 行のコメントを外す
# !git clone https://github.com/JRF-2018/wallerstein_theory
# %cd wallerstein_theory
# !pip install -q git+https://github.com/JRF-2018/mext@v0.1.0
''')
    code(r'''
import os, sys, json, subprocess, re
from IPython.display import Markdown, Image, display

RUN_CLAUDE = False    # True にすると claude CLI を実際に呼ぶ（保存済みの出力の代わりに）
RUN_LEAN = True       # False にすると Lean の検査を省く

# mext が pip で入っていなければ、隣に clone した mext リポジトリ（../mext）を使う
try:
    import mext
except ImportError:
    for cand in ('../mext',):
        if os.path.isdir(os.path.join(cand, 'mext')):
            sys.path.insert(0, os.path.abspath(cand))
            os.environ['PYTHONPATH'] = os.path.abspath(cand) + os.pathsep + os.environ.get('PYTHONPATH', '')
            break
    import mext
print('mext', mext.__version__)
# ! で呼ぶ python3 をこのカーネルと同じ Python にし、mext の場所を伝える。図は画面なしで描く
os.environ['PATH'] = os.path.dirname(sys.executable) + os.pathsep + os.environ['PATH']
os.environ['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(mext.__file__))) + os.pathsep + os.environ.get('PYTHONPATH', '')
os.environ['MPLBACKEND'] = 'Agg'


def show_md(path, sections=None, max_lines=None):
    """Markdown ファイルを表示する。sections に見出しの番号の接頭辞（例 ['1.', '4.']）を渡すと、その節だけを表示する"""
    text = open(path, encoding='utf-8').read()
    if sections:
        parts = re.split(r'(?m)^(?=## )', text)
        text = ''.join(p for p in parts if any(p.startswith('## ' + s) for s in sections) or not p.startswith('## '))
    if max_lines:
        lines = text.splitlines()
        if len(lines) > max_lines:
            text = '\n'.join(lines[:max_lines]) + f'\n\n…（以下 {len(lines) - max_lines} 行を省略。全文は {path}）'
    display(Markdown(text))


# プラグインとして入れたスキルは名前空間つきで呼ぶ。スキルを .claude/skills/ にコピーした場合は '/matcha-default-extensions'。
# （notebook_runs/ の保存済みの出力は、作業用ディレクトリの .claude/skills/ に置いた同じスキルで作った）
SKILL_CMD = '/mext:matcha-default-extensions'


def claude_skill(target, run_dir):
    """スキル matcha-default-extensions を claude CLI で呼ぶ（RUN_CLAUDE が False なら保存済みの出力を表示）"""
    cmd = ['claude', '-p', f'{SKILL_CMD} {target}', '--permission-mode', 'acceptEdits',
           '--allowedTools', 'Bash(python3:*)', 'Bash(cp:*)', 'Bash(lean:*)', 'Bash(diff:*)', 'Read', 'Write', 'Edit']
    print('$ ' + ' '.join(cmd[:3]) + ' …')
    if RUN_CLAUDE:
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        open(os.path.join(run_dir, 'cli_stdout.txt'), 'w', encoding='utf-8').write(out)
    print(open(os.path.join(run_dir, 'cli_stdout.txt'), encoding='utf-8').read())
''')


def ch1():
    md(r'''
## 1. 法の形式言語の現在

法理論・法的推論を形式言語で記述する試みは、「Computational Law」「Rules as Code」「AI & Law」の名で半世紀近く続いている（Grok 会話の整理を、書誌を確認したうえで要約する）。

| 系統 | 代表例 | 特徴 |
|---|---|---|
| 法令の実行可能な仕様 | **Catala**（Merigoux, Chataing & Protzenko 2021） | 法令の文言とコードを並べて書く（literate programming）。一般則と例外の優先関係を `label … exception …` で書く。優先度付きデフォルト論理（Lawsky 2017）を言語の核に持つ |
| 要件事実論の論理プログラム | **PROLEG**（Satoh ら 2011） | `結論 <= 要件.` と `exception(結論, 例外).` で原則と例外を分ける。立証責任を失敗による否定（NAF）に対応させる |
| 論理プログラムとしての法令 | British Nationality Act（Sergot ら 1986）、**Logical English**（Kowalski & Datoo 2022） | 英語に近い構文の論理プログラム |
| 判例の比較 | HYPO（Ashley 1990）、CATO（Aleven 2003） | 判例を要因（factors）の集合として比較する |
| 議論の理論 | Dung (1995)、Prakken & Sartor (1997)、Horty (2012) | 論証の攻撃・支持と、デフォルトとしての理由 |
| 答案構成の記法 | **Matcha**（花房孟胤、Elecode） | 主張・根拠・要件・定義・事実・評価・論点・結論を記号で書く。司法試験の答案構成を形式化する |

### 1.1 Matcha

Matcha は、法的推論の基本構造（法的根拠 → 法的主張 → 要件 → あてはめ → 結論）を記号で書く言語である。

```
#主張^法的根拠 <= 事実:
    「要件」: %定義 <= 事実@評価
>> 結論
```

| 記号 | 意味 |
|---|---|
| `#主張` / `^根拠` | 法的主張と、その根拠（条文・判例・学説） |
| `<= 事実` | 事実のあてはめ |
| `「要件」` / `%定義` | 法文上の要件と、定義（規範）による言い換え |
| `@評価` | 事実への評価 |
| `&` / `\|` / 改行 | AND / OR / AND の省略 |
| `? 問題提起 ~> 理由 => %規範` | 論点（理由を述べて規範を立てる） |
| `+` / `!` | 主張・要件の成立／不成立 |
| `:: 見出し`、`as 名前`、`$名前` | 見出し、名前付け、参照 |

花房氏は、Matcha を法律以外の三段論法（「SHEET BOXING はアートか」をプラトン・カント・ダントーの立場から論じる）にも使っている。Matcha は「法律には形式言語がない」という問題意識から作られた。

一方、Matcha には**例外を明示する構文がない**。デフォルト論理の基盤にするには、例外の記法を足す必要がある（第 4 章の Matcha-D）。

### 1.2 本レポートの立場

Grok との会話で、JRF は次のように論じた。法の論理で重要なのは「何が構成要素か」が事案との対話の中でアレーティア的・弁証法的に現れることであり、それは PROLEG でも扱えない。扱えない限り、try/except 型の手続きでも「書けてしまう」。

本レポートは、この点を形式言語の限界として受け入れ、次の分業をとる。

- 構成要素が決まった後の**適用**は、デフォルト論理で厳密に扱う。
- 構成要素を決める**あてはめ**（事実 → 評価）と、規範の**優先順位の出どころ**は、形式の外（AI の判断と、シミュレーションが示す力関係）に置く。

形式化の意義は、その外にあるものが**どこにあるかを人が追えるようにすること**にある。
''')


def ch2():
    md(r'''
## 2. デフォルト論理入門

（Gemini との会話を、本レポートで使う形に整理する。）

### 2.1 デフォルトと Extension

**デフォルト理論** (W, D) は、確定事実の集合 W と、デフォルトルールの集合 D からなる（Reiter 1980）。デフォルトは

$$\frac{\alpha : \beta}{\gamma}$$

の形をとり、「α が成り立ち、β と矛盾しないなら、γ と結論してよい」を意味する（α: 前提、β: 正当化、γ: 結論）。

論理式の集合 E が **Extension** であるとは、E = Γ(E) となることをいう。Γ(E) は、次の条件を満たす最小の集合である。

- W を含む。
- 論理的に閉じている。
- 前提 α が成り立ち、正当化の否定 ¬β が **E に含まれない**デフォルトの結論 γ を含む。

Extension は「矛盾なく、限界まで適用し尽くした判断の世界」にあたる。

- **Tweety**: W = {鳥(Tweety)}、D = {鳥 : 飛ぶ / 飛ぶ} なら、Extension は一つで、飛ぶ ∈ E。
- **Nixon diamond**: W = {クエーカー, 共和党員}、D = {クエーカー : 平和主義 / 平和主義, 共和党員 : ¬平和主義 / ¬平和主義} なら、Extension は二つに分かれる。
- **懐疑的帰結**（すべての Extension で成り立つ）と**信憑的帰結**（いずれかで成り立つ）を区別する。

### 2.2 失敗による否定と安定モデル

正当化の条件「¬β が E に含まれない」は、Prolog の**失敗による否定**（NAF: 証明できないことをもって否定とみなす）と同じ型の非単調性を持つ。

- Gelfond & Lifschitz (1988) の安定モデル意味論は、相互に否定し合う規則（p ← not q、q ← not p）から、整合的なモデルの集合を与える。
- 古典否定を持つ**拡張論理プログラム**の解集合は、リテラル型のデフォルト理論の Extension と一対一に対応する（Gelfond & Lifschitz 1991）。

本レポートの道具（第 4 章）は、この対応のもとで Extension を厳密に計算する。

### 2.3 法的な例外と優先順位

法の「原則と例外」は、デフォルト論理では二通りに表せる。

1. **正当化に例外の否定を入れる**（半正規デフォルト）: α : γ ∧ ¬δ / γ。たとえば「損害 : 賠償責任 ∧ ¬正当防衛 / 賠償責任」。
2. **例外を独立のデフォルトにし、優先順位を与える**: 「特別法は一般法に優先する」を d₂ ≻ d₁ として与え、優先順位を尊重する Extension（preferred Extension）だけを選ぶ（Brewka 1994、Brewka & Eiter 1999）。

これは法手続の**立証責任**と対応する（Gemini 会話 §3）。

- 原告は原則の前提 α を立証する。
- 被告は例外 δ を立証して、デフォルトの正当化を崩しにいく。
- 例外が立証されなければ、NAF によって原則がそのまま通る。

この対応は、本レポートの分析（§10.1）の鍵になる。
''')
