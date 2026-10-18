import WallersteinTheory.MextSpec

/- MEXT の Extension 検証（mext.py が自動生成）。検査器と健全性定理は WallersteinTheory.MextSpec にある。 -/

namespace Mext.T6CandStatus

/-! T6_cand_status.mext の原子命題
  1 = k1: #身分秩序^身分による賃金の序列（普遍的な規範として） [身分秩序_中核]
  2 = f1: 中核の非正規の労働契約
  3 = c1: 非正規の賃金は正規より低くてよい〔中核の非正規の労働契約〕
  4 = k2: #身分秩序^身分による賃金の序列（普遍的な規範として） [身分秩序_周辺]
  5 = f2: 周辺の非正規の労働契約
  6 = c2: 非正規の賃金は正規より低くてよい〔周辺の非正規の労働契約〕
-/

def T : Mext.Theory where
  W := [2, 5]
  rules := []
  defaults := [
    ⟨[2], [1, 3], [1, 3]⟩,  -- 身分秩序_中核
    ⟨[5], [4, 6], [4, 6]⟩  -- 身分秩序_周辺
  ]

def E1 : List Int := [1, 2, 3, 4, 5, 6]
theorem E1_isExtension : Mext.isExtension T E1 = true := by decide +kernel
/-- E1 は Reiter の Extension である（健全性定理による） -/
theorem E1_reiter : Mext.ReiterExtension T E1 := Mext.isExtension_sound T E1 E1_isExtension

end Mext.T6CandStatus
