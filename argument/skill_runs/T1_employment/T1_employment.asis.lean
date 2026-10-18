/-
  MEXT の Extension 検証（mext.py が自動生成）
  リテラルは整数で表す: 原子 i は i、その否定は -i。
  Γ(E) を有限回の反復で計算し、Γ(E) = E を decide +kernel（カーネルでの評価）で確かめる。
-/
namespace Mext

structure Dflt where
  pre : List Int
  just : List Int
  concl : List Int
deriving Repr

structure Theory where
  W : List Int
  rules : List (List Int × Int)
  defaults : List Dflt

def subsetL (a b : List Int) : Bool := a.all (fun x => b.contains x)

def sameSet (a b : List Int) : Bool := subsetL a b && subsetL b a

def consistentL (S : List Int) : Bool := S.all (fun x => !S.contains (-x))

/-- E に照らして正当化が無矛盾なデフォルト -/
def okDefaults (T : Theory) (E : List Int) : List Dflt :=
  T.defaults.filter (fun d => d.just.all (fun j => !E.contains (-j)))

/-- 1 ステップ: 規則と（前提が満たされた）デフォルトの結論を加える -/
def step (T : Theory) (ds : List Dflt) (S : List Int) : List Int :=
  let fromRules := (T.rules.filter (fun r => subsetL r.1 S)).map (fun r => r.2)
  let fromDefs := ((ds.filter (fun d => subsetL d.pre S)).map (fun d => d.concl)).flatten
  (S ++ fromRules ++ fromDefs).eraseDups

def iter (T : Theory) (ds : List Dflt) : Nat → List Int → List Int
  | 0, S => S
  | n + 1, S => iter T ds n (step T ds S)

/-- Γ(E)（反復回数は規則とデフォルトの数 + 1 で十分） -/
def gamma (T : Theory) (E : List Int) : List Int :=
  iter T (okDefaults T E) (T.rules.length + T.defaults.length + 1) T.W

/-- E は Extension か（無矛盾で、Γ(E) = E） -/
def isExtension (T : Theory) (E : List Int) : Bool :=
  consistentL E && sameSet (gamma T E) E

end Mext

namespace Mext.T1_employment_asis

/-! T1_employment.asis.mext の原子命題
  1 = k1: #雇用安定の原則^中核の雇用慣行（労働契約法18条・労働者派遣法25条の趣旨を反映） [雇用安定_中核]
  2 = f1: 中核の安定した職
  3 = r1: 雇用安定_中核／「業務が恒常的」
  4 = f2: 中核のこの職は需要の変動にさらされない
  5 = c1: 期間の定めのない雇用が通常である〔中核の安定した職〕
  6 = k2: #周辺例外^世界システム上の位置（事実上の規範） [周辺例外_中核]
  7 = r2: 周辺例外_中核／%周辺に位置する
  8 = f3: 中核の工業能力の世界シェアは0.974である
  9 = v1: 中核の工業能力の世界シェアは0.974である@周辺ではない
  10 = r3: 周辺例外_中核／%外資の退出オプションがある
  11 = f4: 中核の外資の撤退ハザード0.05は閾値0.09を下回る
  12 = v2: 中核の外資の撤退ハザード0.05は閾値0.09を下回る@退出の脅しは雇用形態を左右しない
  13 = x1: （employment_core:L8 の AND・2項・1）
  14 = c2: 中核では周辺例外は認められない〔中核の安定した職〕
  15 = k3: #雇用安定の原則^中核の雇用慣行（労働契約法18条・労働者派遣法25条の趣旨を反映） [雇用安定_周辺]
  16 = f5: 周辺の安定した職
  17 = r4: 雇用安定_周辺／「業務が恒常的」
  18 = f6: 周辺のこの職は需要の変動にさらされない
  19 = c3: 期間の定めのない雇用が通常である〔周辺の安定した職〕
  20 = k4: #周辺例外^世界システム上の位置（事実上の規範） [周辺例外_周辺]
  21 = r5: 周辺例外_周辺／%周辺に位置する
  22 = f7: 周辺の工業能力の世界シェアは0.003である
  23 = v3: 周辺の工業能力の世界シェアは0.003である@周辺である
  24 = r6: 周辺例外_周辺／%外資の退出オプションがある
  25 = f8: 周辺の外資の撤退ハザード0.25は閾値0.09を上回る
  26 = v4: 周辺の外資の撤退ハザード0.25は閾値0.09を上回る@いつでも引き上げられる
  27 = r7: 周辺例外_周辺／%正規が通常でなくなっている
  28 = f9: 周辺の職の0.513が非正規である
  29 = v5: 周辺の職の0.513が非正規である@正規は通常ではない
  30 = x2: （employment_periphery:L8 の AND・3項・1）
  31 = k5: #雇用安定の原則^中核の雇用慣行（労働契約法18条・労働者派遣法25条の趣旨を反映） [雇用安定_地域U]
  32 = f10: 地域Uの安定した職
  33 = r8: 雇用安定_地域U／「業務が恒常的」
  34 = f11: 地域Uのこの職は需要の変動にさらされない
  35 = c4: 期間の定めのない雇用が通常である〔地域Uの安定した職〕
  36 = k6: #周辺例外^世界システム上の位置（事実上の規範） [周辺例外_地域U]
  37 = r9: 周辺例外_地域U／%周辺に位置する
  38 = r10: 周辺例外_地域U／%外資の退出オプションがある
  39 = x3: （employment_unknown:L9 の AND・2項・1）
  40 = ab1: ab(雇用安定_中核)
  41 = ab2: ab(雇用安定_周辺)
  42 = ab3: ab(雇用安定_地域U)
-/

def T : Mext.Theory where
  W := [2, 4, 8, 11, 16, 18, 22, 25, 28, 32, 34]
  rules := [([4], 3), ([-4], -3), ([-3], -1), ([9], -7), ([12], -10), ([7, 10], 13), ([-7], -13), ([-10], -13), ([-13], -6), ([18], 17), ([-18], -17), ([-17], -15), ([23], 21), ([-23], -21), ([26], 24), ([-26], -24), ([29], 27), ([-29], -27), ([21, 24, 27], 30), ([-21], -30), ([-24], -30), ([-27], -30), ([-30], -20), ([34], 33), ([-34], -33), ([-33], -31), ([37, 38], 39), ([-37], -39), ([-38], -39), ([-39], -36)]
  defaults := [
    ⟨[2, 3], [1, 5, -40], [1, 5]⟩,  -- 雇用安定_中核
    ⟨[8], [9, -7], [9]⟩,  -- e1
    ⟨[11], [12, -10], [12]⟩,  -- e2
    ⟨[2, 13], [6], [6, 40]⟩,  -- 周辺例外_中核
    ⟨[], [-6, 14], [14]⟩,  -- 周辺例外_中核.不成立
    ⟨[16, 17], [15, 19, -41], [15, 19]⟩,  -- 雇用安定_周辺
    ⟨[22], [23, 21], [23]⟩,  -- e3
    ⟨[25], [26, 24], [26]⟩,  -- e4
    ⟨[28], [29, 27], [29]⟩,  -- e5
    ⟨[16, 30], [20, -19], [20, -19, 41]⟩,  -- 周辺例外_周辺
    ⟨[32, 33], [31, 35, -42], [31, 35]⟩,  -- 雇用安定_地域U
    ⟨[32, 39], [36, -35], [36, -35, 42]⟩  -- 周辺例外_地域U
  ]

def E1 : List Int := [1, 2, 3, 4, 5, -6, -7, 8, 9, -10, 11, 12, -13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
theorem E1_isExtension : Mext.isExtension T E1 = true := by decide +kernel

def E2 : List Int := [1, 2, 3, 4, 5, -6, -7, 8, 9, -10, 11, 12, -13, 14, 16, 17, 18, -19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 41]
theorem E2_isExtension : Mext.isExtension T E2 = true := by decide +kernel

end Mext.T1_employment_asis
