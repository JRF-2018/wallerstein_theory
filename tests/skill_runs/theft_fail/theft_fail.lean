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

namespace Mext.Theft_fail

/-! theft_fail.mext の原子命題
  1 = k1: #窃盗罪^刑法第235条 [L1]
  2 = f1: 甲が本件財布を持ち去った行為
  3 = r1: 窃盗罪／「他人の財物」
  4 = r2: 窃盗罪／%他人が所有する財産的価値のある有体物
  5 = f2: 本件財布はAが所有する
  6 = r3: 窃盗罪／「窃取」
  7 = r4: 窃盗罪／%占有者の意思に反して占有を自己又は第三者に移転すること
  8 = r5: 窃盗罪／%占有者の意思に反して
  9 = f3: A
  10 = v1: A@占有者
  11 = r6: 窃盗罪／%占有
  12 = r7: 窃盗罪／%人が物を実力的に支配する関係
  13 = f4: 公園のベンチにおいていた
  14 = f5: 最大20メートル離れて5分後に取りに戻った
  15 = x1: （L6 の AND・2項・1）
  16 = v2: （L6 の事実群）@Aが財布を実力的に支配している
  17 = r8: 窃盗罪／%自己又は第三者に移転
  18 = f6: 甲
  19 = v3: 甲@自己
  20 = f7: 持ち去った
  21 = v4: 持ち去った@移転
  22 = x2: （L8 の AND・2項・1）
  23 = x3: （L3 の AND・3項・1）
  24 = r9: 窃盗罪／%故意
  25 = r10: 窃盗罪／%事実の認識・認容
  26 = f8: 甲は前記事実を認識認容している
  27 = r11: 窃盗罪／%不法領得の意思
  28 = r12: 窃盗罪／%権利者を排除して他人の物を自己の所有物とし
  29 = v5: 持ち去った@権利者Aを排除して
  30 = r13: 窃盗罪／%経済的用法に従って利用処分する意思
  31 = f9: いやがらせをする目的だった
  32 = v6: いやがらせをする目的だった@財布そのものから効用を得るわけではない
  33 = x4: （L11 の AND・2項・1）
  34 = x5: （L1 の AND・4項・1）
-/

def T : Mext.Theory where
  W := [2, 5, 9, 13, 14, 18, 20, 26, 31]
  rules := [([5], 4), ([4], 3), ([10], 8), ([13, 14], 15), ([16], 12), ([12], 11), ([19, 21], 22), ([22], 17), ([8, 11, 17], 23), ([23], 7), ([7], 6), ([26], 25), ([25], 24), ([29], 28), ([32], -30), ([28, 30], 33), ([33], 27), ([3, 6, 24, 27], 34)]
  defaults := [
    ⟨[9], [10], [10]⟩,  -- e1
    ⟨[15], [16], [16]⟩,  -- e2
    ⟨[18], [19], [19]⟩,  -- e3
    ⟨[20], [21], [21]⟩,  -- e4
    ⟨[20], [29], [29]⟩,  -- e5
    ⟨[31], [32], [32]⟩,  -- e6
    ⟨[2, 34], [1], [1]⟩,  -- L1
    ⟨[], [-1, -1], [-1]⟩  -- L1.不成立
  ]

def E1 : List Int := [-1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 29, -30, 31, 32]
theorem E1_isExtension : Mext.isExtension T E1 = true := by decide +kernel

end Mext.Theft_fail
