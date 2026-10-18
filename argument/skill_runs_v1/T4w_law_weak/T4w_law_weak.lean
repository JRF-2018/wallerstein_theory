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

namespace Mext.T4w_law_weak

/-! T4w_law_weak.mext の原子命題
  1 = k1: #補償原則^補償賃金差の原則（Smith『国富論』第1編第10章、Rosen 1986）
  2 = f1: 中核の非正規の労働契約
  3 = r1: 補償原則_中核／%雇用が不安定
  4 = f2: 非正規の層は契約の切れ目で0.2の割合で職がない
  5 = v1: 非正規の層は契約の切れ目で0.2の割合で職がない@危険を負っている
  6 = c1: 非正規の賃金は正規より低くてよい〔中核の非正規の労働契約〕
  7 = k2: #身分秩序^民法92条（事実たる慣習）
  8 = r2: 身分秩序_中核／%慣習が成立している
  9 = f3: 成立した契約のうち身分秩序によるものの割合は0である
  10 = v2: 成立した契約のうち身分秩序によるものの割合は0である@慣習は成立していない
  11 = r3: 身分秩序_中核／%労働者が身分賃金を受け入れる
  12 = f4: 身分賃金2.209は正規職の列に並ぶ価値2.548を下回る
  13 = v3: 身分賃金2.209は正規職の列に並ぶ価値2.548を下回る@受け入れない
  14 = x1: （wage_core:L9 の AND・2項・1）
  15 = c2: 中核では身分秩序による賃金の切り下げは認められない〔中核の非正規の労働契約〕
  16 = k3: #補償原則^補償賃金差の原則（Smith『国富論』第1編第10章、Rosen 1986） [補償原則_周辺]
  17 = f5: 周辺の非正規の労働契約
  18 = r4: 補償原則_周辺／%雇用が不安定
  19 = c3: 非正規の賃金は正規より低くてよい〔周辺の非正規の労働契約〕
  20 = k4: #身分秩序^民法92条（事実たる慣習） [身分秩序_周辺]
  21 = r5: 身分秩序_周辺／%慣習が成立している
  22 = f6: 成立した契約のうち身分秩序によるものの割合は0.978である
  23 = v4: 成立した契約のうち身分秩序によるものの割合は0.978である@慣習が成立している
  24 = r6: 身分秩序_周辺／%労働者が身分賃金を受け入れる
  25 = f7: 身分賃金0.629は正規職の列に並ぶ価値0.563を上回る
  26 = v5: 身分賃金0.629は正規職の列に並ぶ価値0.563を上回る@受け入れる
  27 = x2: （wage_periphery:L9 の AND・2項・1）
  28 = k5: #均衡待遇の実効^パート有期法9条
  29 = r7: 均衡待遇_周辺／「通常の労働者と同視すべき短時間・有期雇用労働者」
  30 = f8: 安定した職を非正規で埋めている
  31 = v6: 安定した職を非正規で埋めている@職務の内容と配置の変更の範囲が同一
  32 = r8: 均衡待遇_周辺／%実効的な執行
  33 = f9: 執行による身分秩序の利潤の減少0.102は維持できなくする水準0.241を下回る
  34 = v7: 執行による身分秩序の利潤の減少0.102は維持できなくする水準0.241を下回る@身分秩序は慣性で続く
  35 = x3: （law_periphery_weak:L4 の AND・2項・1）
  36 = c4: 周辺では均衡待遇は実効を欠く〔周辺の非正規の労働契約〕
  37 = ab1: ab(身分秩序_周辺)
-/

def T : Mext.Theory where
  W := [2, 4, 9, 12, 17, 22, 25, 30, 33]
  rules := [([5], 3), ([-5], -3), ([-3], -1), ([10], -8), ([13], -11), ([8, 11], 14), ([-8], -14), ([-11], -14), ([-14], -7), ([5], 18), ([-5], -18), ([-18], -16), ([23], 21), ([-23], -21), ([26], 24), ([-26], -24), ([21, 24], 27), ([-21], -27), ([-24], -27), ([-27], -20), ([31], 29), ([-31], -29), ([34], -32), ([29, 32], 35), ([-29], -35), ([-32], -35), ([-35], -28)]
  defaults := [
    ⟨[4], [5, 3], [5]⟩,  -- e1
    ⟨[2, 3], [1, -6], [1, -6]⟩,  -- 補償原則_中核
    ⟨[9], [10, -8], [10]⟩,  -- e2
    ⟨[12], [13, -11], [13]⟩,  -- e3
    ⟨[2, 14], [7], [7]⟩,  -- 身分秩序_中核
    ⟨[], [-7, 15], [15]⟩,  -- 身分秩序_中核.不成立
    ⟨[4], [5, 18], [5]⟩,  -- e4
    ⟨[17, 18], [16, -19], [16, -19]⟩,  -- 補償原則_周辺
    ⟨[22], [23, 21], [23]⟩,  -- e5
    ⟨[25], [26, 24], [26]⟩,  -- e6
    ⟨[17, 27], [20, 19, -37], [20, 19]⟩,  -- 身分秩序_周辺
    ⟨[30], [31, 29], [31]⟩,  -- e7
    ⟨[33], [34, -32], [34]⟩,  -- e8
    ⟨[17, 35], [28], [28, 37]⟩,  -- 均衡待遇_周辺
    ⟨[], [-28, 36], [36]⟩  -- 均衡待遇_周辺.不成立
  ]

def E1 : List Int := [1, 2, 3, 4, 5, -6, -7, -8, 9, 10, -11, 12, 13, -14, 15, 16, 17, 18, -19, 21, 22, 23, 24, 25, 26, 27, -28, 29, 30, 31, -32, 33, 34, -35, 36]
theorem E1_isExtension : Mext.isExtension T E1 = true := by decide +kernel

def E2 : List Int := [1, 2, 3, 4, 5, -6, -7, -8, 9, 10, -11, 12, 13, -14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, -28, 29, 30, 31, -32, 33, 34, -35, 36]
theorem E2_isExtension : Mext.isExtension T E2 = true := by decide +kernel

end Mext.T4w_law_weak
