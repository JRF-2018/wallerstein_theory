/-
  Sim 2（周辺の非正規雇用）の補題

  Harris–Todaro 型の無差別条件から、非正規の賃金は
    w_N = b + q (w − b) / c      （c = 1 − e₀: 非正規の就業率、w = 正規の平均賃金、b = 生存水準）
  正規職に就ける確率は、職の充足率 λ と非正規の職の割合 ν を使って
    q = (1 − ν) λ / (1 − ν λ / c)
  である（列に並ぶ人がいる、つまり分母が正のとき）。
  (1) w_N < w  ⟺  q < c       （補償賃金の原則が「身分賃金」に反転する条件）
  (2) q < c    ⟺  λ < c       （ν が消える。反転するかは労働余剰だけで決まる）
-/
import Mathlib

namespace WallersteinTheory.LaborMarket

/-- 非正規の賃金（Harris–Todaro 型の無差別条件） -/
noncomputable def wageN (b w c q : ℝ) : ℝ := b + q * (w - b) / c

/-- 正規職に就ける確率 -/
noncomputable def queueProb (lam nu c : ℝ) : ℝ := (1 - nu) * lam / (1 - nu * lam / c)

/-- (1) 非正規の賃金が正規より低いのは、q < c のとき、かつそのときに限る -/
theorem wageN_lt_iff {b w c q : ℝ} (hc : 0 < c) (hbw : b < w) :
    wageN b w c q < w ↔ q < c := by
  unfold wageN
  have hwb : 0 < w - b := sub_pos.mpr hbw
  constructor
  · intro H
    have : q * (w - b) / c < w - b := by linarith
    rw [div_lt_iff₀ hc] at this
    nlinarith
  · intro H
    have : q * (w - b) < c * (w - b) := mul_lt_mul_of_pos_right H hwb
    have : q * (w - b) / c < w - b := by
      rw [div_lt_iff₀ hc]; linarith
    linarith

/-- (2) q < c となるのは、職の充足率 λ が c を下回るとき、かつそのときに限る（ν によらない） -/
theorem queueProb_lt_iff {lam nu c : ℝ} (hc : 0 < c) (hden : 0 < 1 - nu * lam / c) :
    queueProb lam nu c < c ↔ lam < c := by
  unfold queueProb
  rw [div_lt_iff₀ hden]
  have : c * (1 - nu * lam / c) = c - nu * lam := by
    field_simp
  rw [this]
  constructor <;> intro H <;> nlinarith [H]

/-- (1) と (2) を合わせる: 賃金の序列が反転するのは λ < c のとき、かつそのときに限る -/
theorem inversion_iff_labor_surplus {b w c lam nu : ℝ} (hc : 0 < c) (hbw : b < w)
    (hden : 0 < 1 - nu * lam / c) :
    wageN b w c (queueProb lam nu c) < w ↔ lam < c := by
  rw [wageN_lt_iff hc hbw, queueProb_lt_iff hc hden]

/-- 労働余剰がなく q = 1 なら、非正規の賃金は正規より高い（補償賃金差、c < 1 のとき） -/
theorem compensating_when_no_surplus {b w c : ℝ} (hc : 0 < c) (hc1 : c < 1) (hbw : b < w) :
    w < wageN b w c 1 := by
  unfold wageN
  have hwb : 0 < w - b := sub_pos.mpr hbw
  rw [one_mul]
  have : w - b < (w - b) / c := by
    rw [lt_div_iff₀ hc]; nlinarith
  linarith

end WallersteinTheory.LaborMarket
