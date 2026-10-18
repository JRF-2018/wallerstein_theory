import WallersteinTheory.MextSpec

/- MEXT の Extension 検証（mext.py が自動生成）。検査器と健全性定理は WallersteinTheory.MextSpec にある。 -/

namespace Mext.Tweety

/-! tweety.mext の原子命題
  1 = k1: #飛行^鳥の通念 [鳥は飛ぶ]
  2 = f1: トゥイーティー
  3 = r1: 鳥は飛ぶ／%鳥である
  4 = f2: トゥイーティーは鳥である
  5 = c1: トゥイーティーは飛ぶ〔トゥイーティー〕
  6 = k2: #非飛行^ペンギンの通念 [ペンギン例外]
  7 = r2: ペンギン例外／%ペンギンである
  8 = f3: トゥイーティーはペンギンである
  9 = ab1: ab(鳥は飛ぶ)
-/

def T : Mext.Theory where
  W := [2, 4, 8]
  rules := [([4], 3), ([-4], -3), ([-3], -1), ([8], 7), ([-8], -7), ([-7], -6)]
  defaults := [
    ⟨[2, 3], [1, 5, -9], [1, 5]⟩,  -- 鳥は飛ぶ
    ⟨[2, 7], [6, -5], [6, -5, 9]⟩  -- ペンギン例外
  ]

def E1 : List Int := [1, 2, 3, 4, 5, 7, 8]
theorem E1_isExtension : Mext.isExtension T E1 = true := by decide +kernel
/-- E1 は Reiter の Extension である（健全性定理による） -/
theorem E1_reiter : Mext.ReiterExtension T E1 := Mext.isExtension_sound T E1 E1_isExtension

def E2 : List Int := [2, 3, 4, -5, 6, 7, 8, 9]
theorem E2_isExtension : Mext.isExtension T E2 = true := by decide +kernel
/-- E2 は Reiter の Extension である（健全性定理による） -/
theorem E2_reiter : Mext.ReiterExtension T E2 := Mext.isExtension_sound T E2 E2_isExtension

end Mext.Tweety
