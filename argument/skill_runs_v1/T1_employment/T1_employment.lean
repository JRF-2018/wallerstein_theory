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

namespace Mext.T1_employment

/-! T1_employment.mext の原子命題
  1 = k1: #雇用安定の原則^労働者派遣法25条・労働契約法18条の趣旨
  2 = f1: 中核の安定した職
  3 = r1: 雇用安定_中核／「業務が恒常的」
  4 = f2: 需要の変動にさらされない職である
  5 = c1: 期間の定めのない雇用とすべきである〔中核の安定した職〕
  6 = k2: #周辺例外^世界システム上の位置（事実上の規範）
  7 = r2: 周辺例外_中核／%周辺に位置する
  8 = f3: 工業能力の世界シェアは0.974である
  9 = v1: 工業能力の世界シェアは0.974である@周辺ではない
  10 = r3: 周辺例外_中核／%外資の退出オプションがある
  11 = f4: 外資の撤退ハザード0.05は閾値0.09を下回る
  12 = v2: 外資の撤退ハザード0.05は閾値0.09を下回る@退出の脅しは雇用形態を左右しない
  13 = x1: （employment_core:L8 の AND・2項・1）
  14 = c2: 中核では周辺例外は認められない〔中核の安定した職〕
  15 = k3: #雇用安定の原則^労働者派遣法25条・労働契約法18条の趣旨 [雇用安定_周辺]
  16 = f5: 周辺の安定した職
  17 = r4: 雇用安定_周辺／「業務が恒常的」
  18 = c3: 期間の定めのない雇用とすべきである〔周辺の安定した職〕
  19 = k4: #周辺例外^世界システム上の位置（事実上の規範） [周辺例外_周辺]
  20 = r5: 周辺例外_周辺／%周辺に位置する
  21 = f6: 工業能力の世界シェアは0.003である
  22 = v3: 工業能力の世界シェアは0.003である@周辺である
  23 = r6: 周辺例外_周辺／%外資の退出オプションがある
  24 = f7: 外資の撤退ハザード0.25は閾値0.09を上回る
  25 = v4: 外資の撤退ハザード0.25は閾値0.09を上回る@いつでも引き上げられる
  26 = x2: （employment_periphery:L8 の AND・2項・1）
  27 = k5: #雇用安定の原則^労働者派遣法25条・労働契約法18条の趣旨 [雇用安定_地域U]
  28 = f8: 地域Uの安定した職
  29 = r7: 雇用安定_地域U／「業務が恒常的」
  30 = c4: 期間の定めのない雇用とすべきである〔地域Uの安定した職〕
  31 = k6: #周辺例外^世界システム上の位置（事実上の規範） [周辺例外_地域U]
  32 = r8: 周辺例外_地域U／%周辺に位置する
  33 = r9: 周辺例外_地域U／%外資の退出オプションがある
  34 = x3: （employment_unknown:L9 の AND・2項・1）
  35 = ab1: ab(雇用安定_中核)
  36 = ab2: ab(雇用安定_周辺)
  37 = ab3: ab(雇用安定_地域U)
-/

def T : Mext.Theory where
  W := [2, 4, 8, 11, 16, 21, 24, 28]
  rules := [([4], 3), ([-4], -3), ([-3], -1), ([9], -7), ([12], -10), ([7, 10], 13), ([-7], -13), ([-10], -13), ([-13], -6), ([4], 17), ([-4], -17), ([-17], -15), ([22], 20), ([-22], -20), ([25], 23), ([-25], -23), ([20, 23], 26), ([-20], -26), ([-23], -26), ([-26], -19), ([4], 29), ([-4], -29), ([-29], -27), ([32, 33], 34), ([-32], -34), ([-33], -34), ([-34], -31)]
  defaults := [
    ⟨[2, 3], [1, 5, -35], [1, 5]⟩,  -- 雇用安定_中核
    ⟨[8], [9, -7], [9]⟩,  -- e1
    ⟨[11], [12, -10], [12]⟩,  -- e2
    ⟨[2, 13], [6], [6, 35]⟩,  -- 周辺例外_中核
    ⟨[], [-6, 14], [14]⟩,  -- 周辺例外_中核.不成立
    ⟨[16, 17], [15, 18, -36], [15, 18]⟩,  -- 雇用安定_周辺
    ⟨[21], [22, 20], [22]⟩,  -- e3
    ⟨[24], [25, 23], [25]⟩,  -- e4
    ⟨[16, 26], [19, -18], [19, -18, 36]⟩,  -- 周辺例外_周辺
    ⟨[28, 29], [27, 30, -37], [27, 30]⟩,  -- 雇用安定_地域U
    ⟨[28, 34], [31, -30], [31, -30, 37]⟩  -- 周辺例外_地域U
  ]

def E1 : List Int := [1, 2, 3, 4, 5, -6, -7, 8, 9, -10, 11, 12, -13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
theorem E1_isExtension : Mext.isExtension T E1 = true := by decide +kernel

def E2 : List Int := [1, 2, 3, 4, 5, -6, -7, 8, 9, -10, 11, 12, -13, 14, 16, 17, -18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 36]
theorem E2_isExtension : Mext.isExtension T E2 = true := by decide +kernel

end Mext.T1_employment
