/-
  Sim 1（中核／周辺の創発）の補題

  2 地域の累積的因果モデルで、対称均衡の反対称な摂動に対する安定条件は K·h(φ) < 1 である。
    h(φ) = φ / ((1+φ)(a+bφ)),  a = 1−μ,  b = 1+μ  （0 < μ < 1）
  ここでは h の形（逆 U 字形）と、不安定化の条件を二次不等式に直す補題を示す。
-/
import Mathlib

namespace WallersteinTheory.CorePeriphery

/-- 安定条件に現れる関数 h(φ) = φ / ((1+φ)(a+bφ)) -/
noncomputable def h (a b φ : ℝ) : ℝ := φ / ((1 + φ) * (a + b * φ))

lemma den_pos {a b x : ℝ} (ha : 0 < a) (hb : 0 < b) (hx : 0 ≤ x) : 0 < (1 + x) * (a + b * x) := by
  have : 0 ≤ b * x := mul_nonneg hb.le hx
  positivity

/-- 差の分解: h(y) − h(x) = (y − x)(a − bxy) / (分母の積) -/
theorem h_sub {a b x y : ℝ} (ha : 0 < a) (hb : 0 < b) (hx : 0 ≤ x) (hy : 0 ≤ y) :
    h a b y - h a b x
      = (y - x) * (a - b * x * y) / (((1 + x) * (a + b * x)) * ((1 + y) * (a + b * y))) := by
  have hdx := den_pos ha hb hx
  have hdy := den_pos ha hb hy
  unfold h
  field_simp
  ring

/-- x < y のとき、h(x) < h(y) となるのは b x y < a のとき、かつそのときに限る -/
theorem h_lt_iff {a b x y : ℝ} (ha : 0 < a) (hb : 0 < b) (hx : 0 ≤ x) (hxy : x < y) :
    h a b x < h a b y ↔ b * x * y < a := by
  have hy : 0 ≤ y := le_trans hx hxy.le
  have hD : 0 < ((1 + x) * (a + b * x)) * ((1 + y) * (a + b * y)) :=
    mul_pos (den_pos ha hb hx) (den_pos ha hb hy)
  rw [← sub_pos, h_sub ha hb hx hy, div_pos_iff_of_pos_right hD,
    mul_pos_iff_of_pos_left (sub_pos.mpr hxy), sub_pos]

/-- h は [0, s] で狭義増加（s = √(a/b)、つまり b s² = a） -/
theorem h_strictMonoOn {a b s : ℝ} (ha : 0 < a) (hb : 0 < b) (hs : 0 < s) (hbs : b * s ^ 2 = a) :
    StrictMonoOn (h a b) (Set.Icc 0 s) := by
  intro x hx y hy hxy
  rw [h_lt_iff ha hb hx.1 hxy]
  have h1 : x * y < s * s := by nlinarith [hx.1, hy.2, hxy]
  nlinarith [mul_lt_mul_of_pos_left h1 hb]

/-- h は [s, ∞) で狭義減少 -/
theorem h_strictAntiOn {a b s : ℝ} (ha : 0 < a) (hb : 0 < b) (hs : 0 < s) (hbs : b * s ^ 2 = a) :
    StrictAntiOn (h a b) (Set.Ici s) := by
  intro x hx y hy hxy
  have hx0 : 0 ≤ x := le_trans hs.le hx
  have hnot : ¬ (b * x * y < a) := by
    have h1 : s * s < x * y := by nlinarith [show s ≤ x from hx, hxy]
    nlinarith [mul_lt_mul_of_pos_left h1 hb]
  have : ¬ h a b x < h a b y := by rwa [h_lt_iff ha hb hx0 hxy]
  have hne : h a b x ≠ h a b y := by
    intro heq
    have hy0 : 0 ≤ y := le_trans hx0 hxy.le
    have := h_sub ha hb hx0 hy0
    rw [heq, sub_self] at this
    have hD : 0 < ((1 + x) * (a + b * x)) * ((1 + y) * (a + b * y)) :=
      mul_pos (den_pos ha hb hx0) (den_pos ha hb hy0)
    have h2 : (y - x) * (a - b * x * y) = 0 := by
      rw [eq_comm, div_eq_zero_iff] at this
      exact this.resolve_right hD.ne'
    have h3 : a - b * x * y < 0 := by
      have h1 : s * s < x * y := by nlinarith [show s ≤ x from hx, hxy]
      nlinarith [mul_lt_mul_of_pos_left h1 hb]
    have h4 : 0 < y - x := sub_pos.mpr hxy
    nlinarith
  exact lt_of_le_of_ne (not_lt.mp this) (Ne.symm hne)

/-- 不安定化の条件 K h(φ) > 1 は、二次不等式 b φ² + (a + b − K) φ + a < 0 と同値（φ ≥ 0） -/
theorem unstable_iff {a b K φ : ℝ} (ha : 0 < a) (hb : 0 < b) (hφ : 0 ≤ φ) :
    1 < K * h a b φ ↔ b * φ ^ 2 + (a + b - K) * φ + a < 0 := by
  have hD := den_pos ha hb hφ
  unfold h
  rw [mul_div_assoc', lt_div_iff₀ hD]
  constructor <;> intro H <;> nlinarith [H]

/-- 本レポートの値（μ = 1/2、K = 5）では、不安定化の条件は 3φ² − 6φ + 1 < 0、
    つまり φ が (3 − √6)/3 ≈ 0.184 を超えたところから不安定になる。 -/
theorem unstable_iff_example {φ : ℝ} (hφ : 0 ≤ φ) :
    1 < 5 * h (1 / 2) (3 / 2) φ ↔ 3 * φ ^ 2 - 6 * φ + 1 < 0 := by
  rw [unstable_iff (by norm_num) (by norm_num) hφ]
  constructor <;> intro H <;> nlinarith [H]

end WallersteinTheory.CorePeriphery
