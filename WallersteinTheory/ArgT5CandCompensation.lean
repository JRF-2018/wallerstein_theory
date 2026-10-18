import WallersteinTheory.MextSpec

/- MEXT の Extension 検証（mext.py が自動生成）。検査器と健全性定理は WallersteinTheory.MextSpec にある。 -/

namespace Mext.T5CandCompensation

/-! T5_cand_compensation.mext の原子命題
  1 = k1: #補償原則^補償賃金差の原則（Smith『国富論』第1編第10章、Rosen 1986） [補償原則_中核]
  2 = f1: 中核の非正規の労働契約
  3 = r1: 補償原則_中核／%雇用が不安定
  4 = f2: 中核の非正規の層は契約の切れ目で0.2の割合で職がない
  5 = v1: 中核の非正規の層は契約の切れ目で0.2の割合で職がない@危険を負っている
  6 = c1: 非正規の賃金は正規より低くてよい〔中核の非正規の労働契約〕
  7 = k2: #補償原則^補償賃金差の原則（Smith『国富論』第1編第10章、Rosen 1986） [補償原則_周辺]
  8 = f3: 周辺の非正規の労働契約
  9 = r2: 補償原則_周辺／%雇用が不安定
  10 = f4: 周辺の非正規の層は契約の切れ目で0.2の割合で職がない
  11 = v2: 周辺の非正規の層は契約の切れ目で0.2の割合で職がない@危険を負っている
  12 = c2: 非正規の賃金は正規より低くてよい〔周辺の非正規の労働契約〕
-/

def T : Mext.Theory where
  W := [2, 4, 8, 10]
  rules := [([5], 3), ([-5], -3), ([-3], -1), ([11], 9), ([-11], -9), ([-9], -7)]
  defaults := [
    ⟨[4], [5, 3], [5]⟩,  -- e1
    ⟨[2, 3], [1, -6], [1, -6]⟩,  -- 補償原則_中核
    ⟨[10], [11, 9], [11]⟩,  -- e2
    ⟨[8, 9], [7, -12], [7, -12]⟩  -- 補償原則_周辺
  ]

def E1 : List Int := [1, 2, 3, 4, 5, -6, 7, 8, 9, 10, 11, -12]
theorem E1_isExtension : Mext.isExtension T E1 = true := by decide +kernel
/-- E1 は Reiter の Extension である（健全性定理による） -/
theorem E1_reiter : Mext.ReiterExtension T E1 := Mext.isExtension_sound T E1 E1_isExtension

end Mext.T5CandCompensation
