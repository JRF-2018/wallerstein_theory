/-
  Sim 3（慣行の進化）の補題

  慣行 A（補償原則）と B（身分秩序）の協調ゲーム。B が A よりリスク支配的である度合い:
    RD(o) = (w_B − u)(π_B − o) − (w_A − u)(π_A − o)
  （w: 労働者の賃金、π: 企業の利潤、u: 労働者の外部オプション、o: 企業の退出オプション）
  (1) w_B < w_A なら、RD は o について狭義増加（退出オプションが大きいほど身分秩序が有利）
  (2) RD(o) > 0 ⟺ o > o*（閾値の公式）
  (3) 法的介入で B の利潤を P 下げると、P が閾値 P* を超えるとき RD < 0（A がリスク支配的）
-/
import Mathlib

namespace WallersteinTheory.Convention

/-- B のリスク支配度 -/
def RD (wA wB piA piB u o : ℝ) : ℝ := (wB - u) * (piB - o) - (wA - u) * (piA - o)

/-- RD は o の一次関数で、傾きは w_A − w_B -/
theorem RD_eq (wA wB piA piB u o : ℝ) :
    RD wA wB piA piB u o = ((wB - u) * piB - (wA - u) * piA) + (wA - wB) * o := by
  unfold RD; ring

/-- (1) 補償賃金が身分賃金より高ければ（w_B < w_A）、RD は退出オプション o について狭義増加 -/
theorem RD_strictMono {wA wB piA piB u : ℝ} (h : wB < wA) :
    StrictMono (fun o => RD wA wB piA piB u o) := by
  intro o1 o2 ho
  simp only [RD_eq]
  nlinarith [sub_pos.mpr h, ho]

/-- (2) 閾値: RD(o) > 0 ⟺ o > ((w_A − u) π_A − (w_B − u) π_B) / (w_A − w_B) -/
theorem RD_pos_iff {wA wB piA piB u o : ℝ} (h : wB < wA) :
    0 < RD wA wB piA piB u o ↔ ((wA - u) * piA - (wB - u) * piB) / (wA - wB) < o := by
  have hd : 0 < wA - wB := sub_pos.mpr h
  rw [RD_eq, div_lt_iff₀ hd]
  constructor <;> intro H <;> nlinarith [H]

/-- (3) 法的介入: B の利潤を P だけ下げたとき、P が P* = π_B − o − (w_A − u)(π_A − o)/(w_B − u)
    を超えれば、A がリスク支配的になる（w_B > u、つまり B が労働者にとって受け入れ可能なとき） -/
theorem penalty_reverses {wA wB piA piB u o P : ℝ} (hu : u < wB)
    (hP : piB - o - (wA - u) * (piA - o) / (wB - u) < P) :
    RD wA wB piA (piB - P) u o < 0 := by
  have hd : 0 < wB - u := sub_pos.mpr hu
  unfold RD
  have : (wA - u) * (piA - o) / (wB - u) > piB - o - P := by linarith
  rw [gt_iff_lt, lt_div_iff₀ hd] at this
  nlinarith [this]

end WallersteinTheory.Convention
