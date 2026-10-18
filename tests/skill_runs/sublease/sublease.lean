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

namespace Mext.Sublease

/-! sublease.mext の原子命題
  1 = k1: #解除^民法612条2項 [無断転貸解除]
  2 = f1: 本件賃貸借
  3 = r1: 解除／「賃借人が賃借物について権利を譲り渡し、又は賃借物を転貸」
  4 = f2: 乙は丙に本件建物を転貸した
  5 = r2: 解除／「第三者に賃借物の使用又は収益をさせた」
  6 = f3: 丙は本件建物で営業している
  7 = r3: 解除／%解除の意思表示
  8 = f4: 甲は乙に解除を通知した
  9 = x1: （L2 の AND・3項・1）
  10 = c1: 甲は本件賃貸借を解除できる
  11 = k2: #承諾の抗弁^民法612条1項 [承諾]
  12 = r4: 承諾の抗弁／「賃貸人の承諾」
  13 = f5: 甲は転貸を口頭で承諾した
  14 = k3: #非背信性の抗弁^最判昭和28年9月25日民集7巻9号979頁 [非背信性]
  15 = r5: 非背信性の抗弁／%賃貸人に対する背信的行為と認めるに足りない特段の事情
  16 = f6: 丙は乙の同居の親族で使用状況は従前と変わらない
  17 = v1: 丙は乙の同居の親族で使用状況は従前と変わらない@信頼関係は破壊されていない
  18 = ab1: ab(無断転貸解除)
-/

def T : Mext.Theory where
  W := [2, 4, 6, 8, 13, 16]
  rules := [([4], 3), ([6], 5), ([8], 7), ([3, 5, 7], 9), ([13], 12), ([17], 15)]
  defaults := [
    ⟨[2, 9], [1, 10, -18], [1, 10]⟩,  -- 無断転貸解除
    ⟨[2, 12], [11, -10], [11, -10, 18]⟩,  -- 承諾
    ⟨[16], [17], [17]⟩,  -- e1
    ⟨[2, 15], [14, -10], [14, -10, 18]⟩  -- 非背信性
  ]

def E1 : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 17]
theorem E1_isExtension : Mext.isExtension T E1 = true := by decide +kernel

def E2 : List Int := [2, 3, 4, 5, 6, 7, 8, 9, -10, 11, 12, 13, 14, 15, 16, 17, 18]
theorem E2_isExtension : Mext.isExtension T E2 = true := by decide +kernel

end Mext.Sublease
