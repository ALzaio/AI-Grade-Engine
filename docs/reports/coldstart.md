# Cold-start (label-free, batch-based) improvements - Arabic set (46 questions, 2102 answers)
Protocol: pure-Python (no numpy); 5-fold by QUESTION, 3 fold seeds averaged; anything fitted (w, k, global affine a+b*s) fitted on train questions only; paired question bootstrap (3000) 95% CI of difference. "raw" = engine_score as-is (MAE 13.88, exact 37.9, within-1 80.2). "affC" = global affine calibration CV (MAE 13.45, exact 39.4, w1 81.6; d vs raw -0.43 [-1.07,+0.17], not significant itself). Scripts: cs.py, run1..4.py.

## Ceiling (oracles, use teacher labels)
- Per-question offset known: MAE 11.77 (-2.11 [-2.83,-1.48]), exact 46.8 (+8.9), w1 84.6.
- Per-question affine known: MAE 11.42, exact 48.7, w1 86.0. Half the true offset: 12.44.
- Per-question bias SD is 6.8 points (mean +5.5: engine over-scores). So a perfect label-free question-bias detector would be worth ~2 MAE points; the question is whether batch statistics reveal it.

## Results (d = MAE difference, percentage points, [95% CI])
1. Rank/quantile normalisation to pooled engine distribution: best w=0-0.1; d +0.08 [-0.01,+0.19] raw; +0.03 vs affC (exact -0.22 significant, worse). Harmful/useless. (Teacher grade distributions differ per question genuinely.)
2. Shrink to question mean/median: chosen w 0-0.1; d +0.04 [-0.03,+0.12] vs affC. Variance scaling around the batch mean: k=0.9-1.0, d +0.02. Nothing.
3. Predicting question bias from batch stats (mean raw_expected, mean/median/sd of score, frac>=.9, frac<.4, mean answer length, ref length, ridge on all, LOO lambda): correlations with true bias all |r|<=0.17 except ref length -0.30. Subtracting the predicted bias gives -0.45..-0.51 MAE vs raw, but that is only the global mean-shift (same as affC, -0.43); after global affine it is +0.04..+0.09 (worse/neutral, CIs include 0; within-1 +0.4..+0.5 on mean-based variants). Question-level over/under-scoring is NOT predictable from batch statistics at this sample size (46 questions).
4. kNN smoothing with char-3-gram TF-IDF (within question): chosen w=0.2, k=10, sim^3 weights, sim>=0.2. Without affine d +0.07 (worse); on top of affC d -0.07 [-0.26,+0.13] MAE, exact -0.06 [-1.35,+1.32], within-1 +1.17 [+0.10,+2.31]. Pairs' gold differences do fall with similarity (|dgold| .33 at sim<.1 -> .16 at sim>.5) but engine scores already agree for similar answers (|dengine| .12 at sim>.5), so smoothing adds little. Only within-1 gain is nominally significant; MAE not; multiple-comparison caution.
5. Pseudo-anchors (top3/bottom3 stretch to fixed targets): selected only very weak settings (w=0.25); d -0.16 [-0.50,+0.21] vs raw, +0.13 vs affC. No gain. Note top-3 engine mean 0.94 vs gold 0.87 (over-scores the top), bottom-3 0.235 vs 0.215 fine - the overshoot is a global effect already captured by affine.
6. Combination kNN + anchors + affine: d -0.03 [-0.21,+0.15] vs affC; exact -0.41, w1 +1.00 [+0.02,+2.02]. No additive gain.

## Honest conclusions
- No label-free batch method gives a MAE improvement distinguishable from noise (all CIs include 0; most point estimates 0 or slightly worse). The oracle ceiling (2 pts) is bound up in question-specific bias that batch stats do not reveal.
- Only robust thing: a global affine/offset calibration (-0.4, itself CI includes 0; consistent with the known 13.0% calibration).
- kNN smoothing is a possible tiny tweak (within-1 +1 pt, MAE -0.07) but I would not adopt it without confirmation on a second dataset.
## Recommendation
Adopt nothing new from cold-start batch tricks. Keep global calibration (s' = clip(a + b*s), fit on all labeled data pooled). Optional/low-priority: kNN smoothing s'_i = 0.8*s_i + 0.2*sum_j(sim_ij^3 s_j)/sum_j(sim_ij^3) over the <=10 nearest answers in the same question with TF-IDF char-3-gram cosine >= 0.2 (applied after calibration), expect <=+1 pt within-1, ~0 MAE. To capture the 2-point ceiling, a few teacher labels per question (offset estimation) are needed - the cold-start batch alone cannot.
