# -*- coding: utf-8 -*-
"""IPYNB: 第 3 章（Matcha の文法とチェッカ）、第 4 章（Matcha-D・MEXT・スキル）"""
from nbtools import md, code, writefile


def ch3():
    md(r'''
## 3. Matcha の文法と構文チェッカ

Matcha の公式の BNF は公開されていない。本レポートは、Elecode のページと花房氏の連載（第 4・5 回）の用例から文法を読み取り、決定論的な構文チェッカ `matcha-check`（mext パッケージ）を実装した。全文は `docs/matcha_grammar.md` にある。

### 3.1 文法（EBNF の抜粋）

```ebnf
element     = [ mark ] ( claim | requirement | issue | ref | group | plain ) , postfix ;
mark        = "+" | "!" ;
claim       = "#" [ text ] [ "^" text ] ;
requirement = ( "「" text "」" [ text ] | "%" text ) [ "^" text ] ;
issue       = "?" text ;
postfix     = { "<=" operand(fact) | ":" operand(elem) | "~>" operand(fact) | "=>" operand(elem)
              | ">>" [ "not" | "!" ] text | "as" label | "!>" "$" label } ;
fact        = ( text [ "as" label ] | group | element ) [ "@" text ] ;
list(c)     = item(c) { ( "&" | "|" | NEWLINE ) item(c) } ;
```

Matcha は括弧 `( )` でも字下げでもブロックを書ける。行頭が `<=` `@` `:` `~>` `=>` の行は前の行の続き（継続行）である。行頭の `>>` は、同じ深さで始まった行の先頭の要素の結論になる。全角の記号（`＠` など）も受け付ける。行頭の `::` は見出し、`//` から行末までは行コメントで、どちらも花房氏の連載第 4 回の用例（`::（１）について`、`// 略`）による（Elecode のページの記号の説明にはない）。

### 3.2 例: Elecode の窃盗罪

Elecode の記載例（引用元はファイルの先頭のコメント）を、構文木として表示する。
''')
    writefile('examples/theft.matcha')
    code(r'''
!python3 -m mext.matcha_check --tree examples/theft.matcha
''')
    md(r'''
### 3.3 誤りの検出

構文チェッカは、括弧の閉じ忘れ、`&` と `|` の混在、要素の間の区切りの欠落、未定義のラベルなどを検出する。次は、Gemini の会話に出てきた「Matcha 風」の記法である（Gemini は当初 Matcha を読めず、`AND`／`NOT` を使った疑似コードを出した）。
''')
    writefile('tests/corpus_neg/gemini_01.matcha')
    code(r'''
!python3 -m mext.matcha_check tests/corpus_neg/gemini_01.matcha
''')
    md(r'''
### 3.4 原典の誤記らしきものの検出

花房氏の連載の民法の答案（設問2、時効取得）を検査すると、成否の印の不整合の警告が出る。

- `+#時効取得` の下に `!「二十年間」` があり、結論も「時効取得できない」である。
- AND の下位要件が不成立なのに、主張全体が成立とされている。原典の `+` は `!` の誤記と思われる。

形式化によって、人の目では見落としやすい不整合が機械的に見つかる例である。
''')
    code(r'''
!sed -n '1p;34,36p;50,55p' tests/corpus/hanafusa_p5_14.matcha
!python3 -m mext.matcha_check tests/corpus/hanafusa_p5_14.matcha
''')
    md(r'''
回帰テストでは、Elecode・花房氏の例（全 45 ファイル）と、誤りを含む例が、すべて期待どおりに判定される。
''')
    code(r'''
!python3 tests/run_tests.py
''')


def ch4():
    md(r'''
## 4. Matcha-D・MEXT・スキル: デフォルト論理の基盤

### 4.1 Matcha-D: 例外の記法（非公式の拡張）

Matcha 本体には手を入れず、最小の記法を足す（**Matcha-D は Elecode／花房氏とは無関係の非公式の拡張である**）。

| 記法 | 意味 | デフォルト論理での読み |
|---|---|---|
| `>> 結論 as d` | 主張 d に名前を付ける（`as` は Matcha 既存） | デフォルト d |
| `X !> $d` | X は d の例外 | X は d に優先し、X が働けば d の正当化が崩れる |
| `>> not 結論` / `>> !結論` | 結論の否定 | 古典否定 ¬結論 |
| `:: 優先 $d2 > $d1` | 優先順位だけを宣言する | d2 ≻ d1 |

要素の前の `!`（`!#主張`）は「この主張は成立しない（立証されない）」という**著者の判定**である。これに対し `>> !X` は「X が偽である」という**主張の内容**である。前者は「立証に失敗した」、後者は「反対事実が立証された」にあたるので、区別する。記号は同じでも、位置（`>>` の直後かどうか）で区別される。

### 4.2 Matcha からデフォルト理論への変換（決定論的）

基本方針は、要件の構成（言い換え・AND・OR）を**必要十分条件**として読むことである。

- 下位が成り立てば上位が成り立つ（r ← 下位）。
- 下位のどれかが否定されれば上位も否定される（¬r ← ¬下位）。

これで「立証されていない」（E に含まれない）と「否定の根拠がある」（¬r が E に含まれる）が区別される。

| Matcha | デフォルト論理 |
|---|---|
| `<= 事実`（評価なし） | 事実 f ∈ W、要件 r ↔ f（当然のあてはめ） |
| `「要件」 <= 事実@評価` | 評価デフォルト f : v, r / v と r ↔ v（評価は争いうるあてはめ） |
| `#主張 <= 対象: 要件… >> 結論 as d` | 主張デフォルト d: 対象 ∧ 要件 : k, c / k, c と ¬k ← ¬要件 |
| `X !> $d` | X の結論に ab(d) を足し、d の正当化に ¬ab(d) を足す。さらに X ≻ d |
| 不成立（`!`）の要件の `<= 事実@評価` | ¬r ← v（要件を満たさない根拠） |
| 不成立の主張の `>> 結論` | ⊤ : ¬k, c / c（主張が成り立たないことからの結論）。d ≻ これ |
| 成否の印 `+` / `!` | 各 Extension に含まれる／含まれないかを照合する |

Extension は、拡張論理プログラムとの対応（Gelfond & Lifschitz 1991）のもとで全列挙する。衝突しうるデフォルトだけについて部分集合を試すので、漏れはない。

**preferred Extension** は、Brewka & Eiter (1999) の考え方による次の定義で選ぶ。

- E の生成デフォルトを、前提が満たされた順に一つずつ適用していく列がある。
- 各段で、より優先される対立デフォルトのうち前提が（最終的な）E で満たされるものは、その時点ですでに打ち負かされている。

### 4.3 MEXT: Extension を記述する言語（本レポートの考案）

MEXT（Matcha EXTension notation）は、デフォルト理論とその Extension を、人が読めて機械が検証できる形で書くテキスト形式である。ファイルは三層に分かれる。

1. **人・AI が書く層**:
   - `[ai]`: 命題の同一視（`same`）・否定（`neg`）、結論の型（`failure`／`effect`）、あてはめの審査（`review "事実@評価" ok|doubtful|reject`）。それぞれ理由付き。
   - `[extra]`: 背景知識。
   - `[claimed]`: 予測した Extension。
2. **決定論的に生成される層**: `[atoms]` `[W]` `[rules]` `[defaults]` `[priority]` `[extensions]` `[marks]` `[summary]`。
3. **検証の層**: `mext verify`（主張された Extension の検証）と `mext lean`（Lean による証明）。

例として、Tweety を Matcha-D で書く。
''')
    writefile('examples/tweety.matcha')
    code(r'''
!python3 -m mext init examples/tweety.matcha -o examples/tweety.mext
!python3 -m mext solve examples/tweety.mext
!sed -n '/自動生成/,$p' examples/tweety.mext
''')
    md(r'''
- Reiter の Extension は二つある（E1: 飛ぶ、E2: 飛ばない）。
- E1 では「鳥は飛ぶ」が先に適用され、ペンギン例外の正当化（¬飛ぶ）が崩れている。
- 優先順位（ペンギン例外 ≻ 鳥は飛ぶ）を尊重する preferred Extension は E2 だけである。

`explain` は導出の根拠をたどる。含まれない文言については、含まれない理由（欠けている前提、矛盾する正当化）をたどる。
''')
    code(r'''
!python3 -m mext explain examples/tweety.mext E2 "¬トゥイーティーは飛ぶ"
!python3 -m mext explain examples/tweety.mext E2 "トゥイーティーは飛ぶ"
''')
    md(r'''
Nixon diamond は優先順位を持たないので、Extension が二つに分かれ、懐疑的帰結は何も言えない。
''')
    writefile('examples/nixon.matcha')
    code(r'''
!python3 -m mext init --solve examples/nixon.matcha -o examples/nixon.mext
!python3 -m mext report examples/nixon.mext | sed -n '/### Extension/,$p'
''')
    md(r'''
`lean` は、各 Extension E について Γ(E) = E を Lean で確かめるファイルを出力する。Γ を Lean の関数として定義し、`decide +kernel` で Bool の判定を示す。

偽の主張（Extension でない集合）は拒否される。さらに第 11 章で、この Bool の判定が Reiter の定義を満たすことを導く健全性定理を示す。
''')
    code(r'''
!python3 -m mext lean examples/tweety.mext -o /tmp/Tweety.lean
!tail -8 /tmp/Tweety.lean
import shutil
if shutil.which('lean'):
    !lean /tmp/Tweety.lean && echo "Lean: OK"
else:
    print('lean が見つからないので省略（第 11 章を参照）')
''')
    md(r'''
### 4.4 スキル matcha-default-extensions

スキルの本体は、mext リポジトリ（https://github.com/JRF-2018/mext ）の `skills/matcha-default-extensions/SKILL.md` にある。本リポジトリには含まれない（Claude Code のプラグインとして入れる。「環境構築」の節を参照）。スキルは、`.matcha` ファイル（または複数ファイルの理論、既存の `.mext`）を受け取り、次の手順を踏む。

1. 構文チェック（決定論的）。
2. ひな形の作成（決定論的。Extension はまだ計算しない）。
3. **AI の判断を `[ai]` に書く**: 同一視・否定・結論の型・あてはめの審査。理由付き。
4. **Extension の予測を `[claimed]` に書く**: 求解の前に、原文を読んだ直感で書く。Gemini 会話の「AI が Extension をやや曖昧に構築する」にあたる。
5. 求解・検証・説明・Lean（決定論的）。審査を反映しない版や、試算も作る。
6. レポートを書く: 構文、AI の判断、Extension、著者の印との照合、あてはめの実質的妥当性、懐疑的・信憑的帰結、反論の候補（立証責任）、予測の検証、結論（形式的妥当性と実質的妥当性を分ける）。

**スキルを作る過程の記録**: JRF の提案どおり、私（Claude Opus 5.5）と文脈を共有しないサブエージェント 4 体に、スキルの指示書だけを渡して試した（`tests/skill_runs/`）。その結果、道具の設計の欠陥が三つ見つかり、直した。

- preferred の最初の定義では、例外の前提に評価が一つ入るだけで優先が効かなくなった。
- カント例で、否定の根拠が結論につながっていなかった（要件を必要十分条件として読むように改めた）。
- 反対の事実を足すと Extension が消えた（あてはめを争いうるデフォルトにした）。

2 回目は IPYNB と同じ CLI の経路で試した（`tests/skill_runs2/`）。

### 4.5 デモ: 傷害罪と正当防衛（Gemini 会話の例）

Gemini 会話の「不法行為と正当防衛」の例を、刑法の傷害罪と正当防衛に置き換えて Matcha-D で書く。
''')
    writefile('notebook_runs/self_defense/self_defense.matcha')
    code(r'''
claude_skill('notebook_runs/self_defense/self_defense.matcha', 'notebook_runs/self_defense')
''')
    code(r'''
show_md('notebook_runs/self_defense/self_defense.report.md', max_lines=160)
''')
    md(r'''
### 4.6 デモ: 窃盗罪の不成立（Elecode の例）と、著者の成否の照合

Elecode の不成立の記載例では、利用処分意思が「いやがらせをする目的だった@財布そのものから効用を得るわけではない」によって否定される。その結果、窃盗罪は成立しない。

`!` の要件の下の `<= 事実@評価` は、要件を満たさない根拠（¬要件）として変換される。著者の `+`／`!` の印は、Extension とすべて一致するはずである。
''')
    code(r'''
!sed -n '1,4p;12,16p' notebook_runs/theft_fail/theft_fail.matcha
claude_skill('notebook_runs/theft_fail/theft_fail.matcha', 'notebook_runs/theft_fail')
''')
    code(r'''
show_md('notebook_runs/theft_fail/theft_fail.report.md', sections=['4.', '5.', '6.', '10.'], max_lines=140)
''')
