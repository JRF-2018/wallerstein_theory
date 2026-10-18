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

namespace Mext.Kant

/-! kant.mext の原子命題
  1 = k1: #SHEET_BOXINGプロジェクトはアートといえるか^カントの判断力批判 [L1]
  2 = r1: SHEET_BOXINGプロジェクトはアートといえるか／%天才によって規則を生み出したこと
  3 = r2: SHEET_BOXINGプロジェクトはアートといえるか／%芸術に規則を与える生得的な心的資質
  4 = f1: ボクシングの戦術表現につき新しい記号体系を与えた
  5 = r3: SHEET_BOXINGプロジェクトはアートといえるか／%目的なき合目的性が備えていること
  6 = r4: SHEET_BOXINGプロジェクトはアートといえるか／%それ自体に目的を持たないにもかかわらず合目的的に感じられること
  7 = f2: 拳譜は、ボクシングの戦術的側面を記録し議論するという目的を持っている
  8 = r5: SHEET_BOXINGプロジェクトはアートといえるか／%美的理念を有する
  9 = r6: SHEET_BOXINGプロジェクトはアートといえるか／%多くの思考を引き起こすが、それに完全に対応する特定の概念によって規定されない
  10 = f3: ノーテーションの1類型であると説明できる
  11 = x1: （L2 の AND・3項・1）
-/

def T : Mext.Theory where
  W := [4, 7, 10]
  rules := [([4], 3), ([3], 2), ([7], -6), ([6], 5), ([10], -9), ([9], 8), ([2, 5, 8], 11), ([-6], -5), ([-9], -8), ([-5], -1), ([-8], -1)]
  defaults := [
    ⟨[11], [1], [1]⟩,  -- L1
    ⟨[], [-1, -1], [-1]⟩  -- L1.不成立
  ]

def E1 : List Int := [-1, 2, 3, 4, -5, -6, 7, -8, -9, 10]
theorem E1_isExtension : Mext.isExtension T E1 = true := by decide +kernel

end Mext.Kant
