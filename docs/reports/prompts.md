# Decider prompt search (Arabic short answers) - REPORT

Protocol: 2-fold split by question (q 0-22 vs 23-45, swapped); isotonic fit on the training fold only; pooled out-of-fold predictions; paired question-level bootstrap (2000 resamples, 46 questions) of MAE difference vs the current engine setup (v1+v2+v3, one request) recomputed the same way. Letters: predicted cutoffs .87/.80/.70/.55/.40, true .93/.83/.70/.55/.40. Sample: 21 answers per question = 966 rows; 25 candidate questions per row sent in 7 batched requests (<=6 questions each). Winners re-validated on all 2102 rows. English set (real_en.json) NOT run (no gain to confirm on Arabic).
Scripts: cands.py (all prompt texts/options), run.py, analyze.py, val.py; raw output analysis_21.txt, val_all.txt.

## Sample (966 rows) - see analysis_21.txt for the full table
N rows=966, questions=46, gold-mean MAE baseline(const)=23.11
| candidate | MAE % | diff vs engine v1+v2+v3 [95% CI] | Pearson | letter exact % | within-1 % | MAE fold0/fold1 |
|---|---|---|---|---|---|---|
| ENGINE v1+v2+v3 | 13.02 | +0.00 [+0.00,+0.00] | 0.798 | 42.0 | 82.5 | 12.4/13.6 |
**single questions**
| v1 | 13.05 | +0.03 [-0.11,+0.18] | 0.797 | 42.1 | 81.7 | 12.5/13.6 |
| v2 | 13.29 | +0.27 [+0.04,+0.49] | 0.788 | 42.5 | 80.2 | 12.8/13.8 |
| v3 | 12.79 | -0.23 [-0.45,+0.01] | 0.804 | 42.5 | 82.0 | 12.3/13.3 |
| v4 | 13.12 | +0.10 [-0.46,+0.64] | 0.796 | 41.0 | 82.1 | 12.9/13.3 |
| v5 | 13.57 | +0.55 [+0.03,+1.14] | 0.780 | 39.8 | 79.2 | 13.8/13.3 |
| L5 | 12.99 | -0.03 [-0.27,+0.22] | 0.800 | 41.8 | 81.4 | 12.6/13.4 |
| N11 | 12.88 | -0.14 [-0.34,+0.06] | 0.803 | 43.3 | 82.7 | 12.4/13.4 |
| M5 | 12.73 | -0.29 [-0.50,-0.09] | 0.807 | 42.7 | 83.4 | 12.3/13.1 |
| PB | 12.78 | -0.24 [-0.51,+0.06] | 0.805 | 43.4 | 81.8 | 12.5/13.1 |
| pbp | 13.12 | +0.11 [-0.23,+0.46] | 0.796 | 41.4 | 82.9 | 12.6/13.6 |
| extra | 12.86 | -0.15 [-0.39,+0.09] | 0.802 | 40.2 | 82.5 | 12.4/13.4 |
| persona | 12.96 | -0.06 [-0.30,+0.18] | 0.800 | 41.5 | 83.0 | 12.5/13.5 |
| strict2 | 12.90 | -0.11 [-0.54,+0.31] | 0.801 | 42.8 | 82.5 | 12.4/13.4 |
| lenient | 13.25 | +0.23 [-0.23,+0.66] | 0.790 | 40.6 | 81.1 | 12.8/13.7 |
| count | 15.06 | +2.04 [+0.87,+3.26] | 0.735 | 35.9 | 74.6 | 14.4/15.7 |
| ar1 | 13.20 | +0.18 [-0.08,+0.45] | 0.792 | 40.9 | 81.7 | 12.7/13.7 |
| ar2 | 13.38 | +0.37 [+0.06,+0.66] | 0.785 | 39.9 | 80.2 | 13.0/13.7 |
| ar3 | 12.65 | -0.36 [-0.61,-0.10] | 0.808 | 41.6 | 83.4 | 12.2/13.1 |
| arN11 | 13.04 | +0.03 [-0.23,+0.29] | 0.796 | 42.2 | 82.1 | 12.6/13.5 |
| v1_noq | 13.26 | +0.25 [-0.46,+0.96] | 0.789 | 42.4 | 81.9 | 12.6/13.9 |
| v2_noq | 13.44 | +0.43 [-0.28,+1.14] | 0.785 | 38.7 | 81.9 | 12.9/14.0 |
| v3_noq | 13.19 | +0.18 [-0.57,+0.92] | 0.794 | 42.7 | 81.5 | 12.5/13.9 |
| v1_af | 12.75 | -0.26 [-0.67,+0.12] | 0.806 | 43.1 | 82.3 | 12.3/13.2 |
| v2_af | 13.31 | +0.30 [-0.15,+0.73] | 0.790 | 40.2 | 81.0 | 12.9/13.7 |
| v3_af | 12.70 | -0.31 [-0.71,+0.06] | 0.808 | 43.2 | 83.2 | 12.2/13.2 |
**raw-uncalibrated sanity**: engine raw-expected MAE vs gold with isotonic only (above)
**fixed ensembles**
| v1+v2+v3 (engine) | 13.02 | +0.00 [+0.00,+0.00] | 0.798 | 42.0 | 82.5 | 12.4/13.6 |
| v1+v2 | 13.12 | +0.11 [-0.03,+0.24] | 0.794 | 41.0 | 82.0 | 12.5/13.7 |
| v1+v3 | 12.86 | -0.16 [-0.28,-0.03] | 0.802 | 43.1 | 82.9 | 12.3/13.5 |
| v2+v3 | 12.93 | -0.09 [-0.20,+0.01] | 0.799 | 42.8 | 81.9 | 12.3/13.5 |
| Arabic ar1+ar2+ar3 | 12.97 | -0.05 [-0.23,+0.12] | 0.798 | 43.0 | 81.3 | 12.5/13.5 |
| noq v1+v2+v3 | 13.21 | +0.20 [-0.51,+0.92] | 0.790 | 41.8 | 82.0 | 12.5/13.9 |
| ansfirst v1+v2+v3 | 12.92 | -0.09 [-0.48,+0.27] | 0.802 | 42.1 | 81.6 | 12.5/13.3 |
| engine + N11 + M5 + PB | 12.78 | -0.24 [-0.42,-0.05] | 0.803 | 42.2 | 82.8 | 12.3/13.3 |
| numeric N11+M5+PB | 12.73 | -0.29 [-0.49,-0.08] | 0.807 | 42.3 | 82.9 | 12.3/13.1 |
| engine + ar1+ar2+ar3 | 12.95 | -0.07 [-0.19,+0.06] | 0.799 | 42.1 | 82.1 | 12.4/13.5 |
| engine + pbp+extra+persona | 12.87 | -0.15 [-0.30,+0.00] | 0.801 | 42.3 | 82.1 | 12.4/13.3 |
| all 6-grade (v1-v5,pbp,extra,persona,strict2,lenient) | 12.82 | -0.20 [-0.45,+0.05] | 0.803 | 41.4 | 82.3 | 12.4/13.2 |
| ALL candidates | 12.88 | -0.14 [-0.55,+0.28] | 0.807 | 41.4 | 83.1 | 12.3/13.5 |
**greedy forward selection (chosen on train fold only), ensemble size k -> OOF metrics**
| k | MAE % | diff vs engine | Pearson | letter exact | sets chosen (fold0-test / fold1-test) |
|---|---|---|---|---|---|
| 1 | 13.63 | +0.61 [+0.07,+1.20] | 0.783 | 41.2 | v5 / strict2 |
| 2 | 12.88 | -0.14 [-0.58,+0.30] | 0.804 | 40.9 | v3_af / v3_af |
| 3 | 12.85 | -0.17 [-0.57,+0.24] | 0.804 | 41.9 | PB / v1_noq |
| 4 | 12.74 | -0.28 [-0.62,+0.05] | 0.807 | 41.8 | strict2 / M5 |
| 5 | 12.78 | -0.24 [-0.60,+0.15] | 0.806 | 42.4 | ar1 / v2_noq |
| 6 | 12.91 | -0.11 [-0.44,+0.24] | 0.801 | 41.7 | v2 / pbp |
| 7 | 12.82 | -0.20 [-0.51,+0.11] | 0.804 | 42.0 | M5 / ar3 |
| 8 | 12.82 | -0.20 [-0.48,+0.07] | 0.804 | 42.4 | v1 / persona |
final selected sets: fold1-trained ['v5', 'v3_af', 'PB', 'strict2', 'ar1', 'v2', 'M5', 'v1']  fold0-trained ['strict2', 'v3_af', 'v1_noq', 'M5', 'v2_noq', 'pbp', 'ar3', 'persona']
**ensemble size, random subsets drawn from pool of 6-grade English default-state questions (v1,v2,v3,v4,v5,pbp,extra,persona,strict2,lenient)**
k=1: mean MAE 13.07  (min 12.79, max 13.57)
k=2: mean MAE 12.92  (min 12.71, max 13.27)
k=3: mean MAE 12.87  (min 12.71, max 13.17)
k=4: mean MAE 12.84  (min 12.72, max 12.98)
k=5: mean MAE 12.84  (min 12.72, max 13.02)
k=6: mean MAE 12.81  (min 12.73, max 12.89)

## Validation on all 2102 rows
N rows=2102 questions=46
| candidate | MAE % | diff vs engine [95% CI] | Pearson | letter exact | within-1 | MAE f0/f1 |
|---|---|---|---|---|---|---|
| ENGINE v1+v2+v3 | 13.12 | +0.00 [+0.00,+0.00] | 0.802 | 42.2 | 82.4 | 12.8/13.4 |
| v1 only | 13.16 | +0.03 [-0.08,+0.16] | 0.801 | 41.4 | 82.8 | 13.0/13.3 |
| v3 only | 13.10 | -0.02 [-0.19,+0.15] | 0.803 | 41.3 | 83.0 | 12.8/13.4 |
| M5 only | 12.97 | -0.15 [-0.31,+0.00] | 0.807 | 41.2 | 83.0 | 12.7/13.3 |
| N11 only | 13.20 | +0.07 [-0.07,+0.22] | 0.801 | 41.2 | 82.4 | 12.9/13.5 |
| PB only | 13.22 | +0.09 [-0.13,+0.33] | 0.799 | 41.5 | 81.7 | 13.1/13.3 |
| ar3 only | 13.21 | +0.09 [-0.12,+0.30] | 0.800 | 39.8 | 83.1 | 13.0/13.4 |
| numeric N11+M5+PB | 13.10 | -0.02 [-0.17,+0.13] | 0.804 | 41.5 | 82.8 | 12.8/13.4 |
| v3+M5+PB+N11 | 13.08 | -0.04 [-0.17,+0.10] | 0.804 | 41.5 | 82.9 | 12.8/13.3 |
| v1+v3+ar3+M5+PB+N11 | 13.07 | -0.05 [-0.18,+0.10] | 0.804 | 40.3 | 82.6 | 12.9/13.3 |
| engine+N11+M5+PB (6) | 13.09 | -0.03 [-0.11,+0.05] | 0.804 | 42.0 | 82.7 | 12.8/13.3 |
| v3+ar3+M5 | 13.02 | -0.10 [-0.24,+0.05] | 0.806 | 40.9 | 82.8 | 12.7/13.3 |
| v1+v3+ar3 | 13.09 | -0.04 [-0.16,+0.09] | 0.803 | 40.8 | 83.2 | 12.8/13.4 |

## Conclusions
- KEEP CURRENT. No candidate beats v1+v2+v3 beyond noise. On the 966 sample the best single questions (M5 marks-out-of-5 12.73, ar3 Arabic v3 12.65, PB 12.78, v3 12.79) were 0.2-0.4 pt below the engine (13.02), nominally significant on that sample; on all 2102 rows the gaps shrink to -0.15 (M5) .. +0.09, CIs include 0, i.e. regression to the mean / selection among 25 candidates. Best ensemble on all rows: v3+ar3+M5 13.02 vs 13.12 (-0.10 [-0.24,+0.05]) - not significant.
- Option sets: 5 levels (12.99), 11 levels (12.88), marks/5 (12.73), percent bands (12.78) all within +-0.3 of 6 grades. Numeric ensembles 13.10 vs 13.12 on full data.
- Framings: strict examiner (v4) 13.12, strict2 12.90, point-by-point 13.12, penalise-extra 12.86, teacher persona 12.96, lenient 13.25, v5 'reference may have more detail' 13.57 (worse, +0.55 [0.03,1.14]) - confirms rejection.
- Arabic instructions: ar1 13.20, ar2 13.38 (worse), ar3 12.65 sample / 13.21 full: no robust gain.
- Question omitted: worse by 0.2-0.4 pt (not significant, keep question). Answer before reference: -0.1 pt ensemble (n.s.).
- Point-count question (0,1,2,3,4+): clearly worse, 15.06 (+2.04 [0.87,3.26]), Pearson .735. Do not use.
- Ensemble size (random subsets of 10 six-grade prompts): k=1 13.07, 2 12.92, 3 12.87, 4 12.84, 5 12.84, 6 12.81 (sample). 1->3 gains ~0.2 pt, 3->6 ~0.06 pt: diminishing, not worth extra tokens. Greedy (train-fold-selected) sets reach 12.74-12.85, same ceiling ~12.7-12.8%.
- Ceiling: all prompts give MAE 12.7-13.3, Pearson .79-.81; errors are dominated by label noise (teacher-vs-teacher 11.3%) and per-question bias, not by prompt wording. Prompt tuning is exhausted; further gains need per-question anchors (ShortAnchoredEngine) not prompts.
- Optional (low-risk, unproven): replace v2 by an M5 'marks out of 5' question (v1+v3+M5); expected effect about -0.1..-0.2 pt, within noise. Not recommended as a change.
Exact M5 text if wanted: instructions "Give marks out of 5 to the student answer, using the reference answer as the mark scheme."; options 0 wrong or irrelevant, no marks / 1 a little of the required content / 2 some of the required content, less than half / 3 about two thirds of the required content / 4 almost all required content / 5 full marks: all required content correct; values k/5.
