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

namespace Mext.Self_defense

/-! self_defense.mext の原子命題
  1 = k1: #傷害罪^刑法204条 [傷害]
  2 = f1: 甲がAを殴打した行為
  3 = r1: 傷害／「人の身体を傷害した」
  4 = f2: Aは全治2週間の打撲を負った
  5 = r2: 傷害／%故意
  6 = f3: 甲はAを殴るつもりだった
  7 = x1: （L2 の AND・2項・1）
  8 = c1: 甲に傷害罪が成立する〔甲がAを殴打した行為〕
  9 = k2: #正当防衛^刑法36条1項 [正当防衛]
  10 = r3: 正当防衛／「急迫不正の侵害」
  11 = f4: Aが刃物で甲に切りかかってきた
  12 = v1: Aが刃物で甲に切りかかってきた@急迫不正の侵害
  13 = r4: 正当防衛／「自己又は他人の権利を防衛するため」
  14 = f5: 甲は身を守ろうとして殴った
  15 = v2: 甲は身を守ろうとして殴った@防衛の意思
  16 = r5: 正当防衛／「やむを得ずにした行為」
  17 = f6: 素手で一回殴っただけである
  18 = v3: 素手で一回殴っただけである@防衛行為として相当
  19 = x2: （L7 の AND・3項・1）
  20 = ab1: ab(傷害)
-/

def T : Mext.Theory where
  W := [2, 4, 6, 11, 14, 17]
  rules := [([4], 3), ([-4], -3), ([6], 5), ([-6], -5), ([3, 5], 7), ([-3], -7), ([-5], -7), ([-7], -1), ([12], 10), ([-12], -10), ([15], 13), ([-15], -13), ([18], 16), ([-18], -16), ([10, 13, 16], 19), ([-10], -19), ([-13], -19), ([-16], -19), ([-19], -9)]
  defaults := [
    ⟨[2, 7], [1, 8, -20], [1, 8]⟩,  -- 傷害
    ⟨[11], [12, 10], [12]⟩,  -- e1
    ⟨[14], [15, 13], [15]⟩,  -- e2
    ⟨[17], [18, 16], [18]⟩,  -- e3
    ⟨[2, 19], [9, -8], [9, -8, 20]⟩  -- 正当防衛
  ]

def E1 : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
theorem E1_isExtension : Mext.isExtension T E1 = true := by decide +kernel

def E2 : List Int := [2, 3, 4, 5, 6, 7, -8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
theorem E2_isExtension : Mext.isExtension T E2 = true := by decide +kernel

end Mext.Self_defense
