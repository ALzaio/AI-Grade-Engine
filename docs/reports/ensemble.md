# Agent ensemble study (180 hold-out essays, 12 questions)

Scripts: `lib.py` (shared), `stage1.py` (base scores), `stage2.py` (learning curve + anchor selection runs), `stage3.py` (tasks 1 and 3), `stage4.py` (task 2). Cached outputs: `base.json`, `curve.json`. All numbers in percent. No existing file was edited. Free decider only.
Reproduction check: direct 13.3, anchored 13.6, blend2 11.6 (matches the frozen results).
Noise: 12 questions x 15 essays; question-level bootstrap CIs are wide (about +-1.5 to 2 points). Differences below ~0.5 point are noise. Letters use CUT_ESSAY for gold and for all blends (direct alone also shown with CUT_SHORT).

## Task 1: third member (180 hold-out essays)

| mode | MAE % | Pearson | letters exact % | within-1 % | A+ precision % | A+ recall % |
|---|---|---|---|---|---|---|
| direct (default calibration, short cuts) | 13.3 | 0.772 | 36 | 79 | 43 | 69 |
| direct (essay cuts) | 13.3 | 0.772 | 36 | 81 | 45 | 54 |
| anchored k5 d.4 | 13.6 | 0.751 | 39 | 78 | 72 | 51 |
| rubric per-criterion (raw) | 14.9 | 0.692 | 37 | 74 | 53 | 49 |
| rubric (LOQO isotonic) | 15.3 | 0.666 | 31 | 77 | 29 | 11 |
| blend2 = (direct+anch)/2 | 11.6 | 0.818 | 46 | 86 | 75 | 51 |
| direct+rubric /2 | 13.5 | 0.768 | 36 | 81 | 54 | 54 |
| anch+rubric /2 | 12.4 | 0.768 | 44 | 79 | 61 | 49 |
| blend3 equal (d,a,rubric raw) | 12.1 | 0.802 | 41 | 84 | 66 | 54 |
| blend3 equal (rubric LOQO-iso) | 12.1 | 0.803 | 43 | 82 | 67 | 40 |
| LOQO ridge(lam=1) on d,a | 12.5 | 0.795 | 39 | 83 | 82 | 26 |
| LOQO simplex-MAE grid on d,a | 12.0 | 0.808 | 44 | 83 | 72 | 51 |
| LOQO ridge(lam=1) on d,a,r | 12.9 | 0.780 | 40 | 81 | 75 | 26 |
| LOQO NNLS (no intercept) d,a,r | 12.7 | 0.784 | 38 | 81 | 67 | 34 |
| LOQO simplex-MAE grid d,a,r | 12.5 | 0.787 | 44 | 81 | 72 | 51 |

Mean learned weights across LOQO folds: ridge [b0,d,a,r]=[0.03, 0.46, 0.39, 0.09]; NNLS [d,a,r]=[0.56, 0.41, 0.02]; simplex grid [d,a,r]=[0.48, 0.5, 0.02]; simplex(d,a)=[0.5, 0.5]

Paired question-level bootstrap, MAE difference in points (negative = first better), 95% CI:
- blend3 vs blend2: +0.47 [-0.47, +1.57]
- blend3(iso rubric) vs blend2: +0.51 [-0.25, +1.36]
- NNLS vs blend2: +1.12 [+0.36, +2.17]
- simplex d,a,r vs blend2: +0.87 [+0.00, +2.37]
- ridge d,a,r vs blend2: +1.27 [+0.54, +2.36]
- blend2 vs direct: -1.65 [-3.82, +0.66]
- blend2 vs anch: -1.98 [-3.94, -0.30]
- blend3 vs rubric: -2.78 [-4.55, -1.39]

Per-question MAE %:

| Q | n | direct | anch | rubric | blend2 | blend3 | human A-B |
|---|---|---|---|---|---|---|---|
| Q1 | 15 | 13.3 | 10.7 | 11.6 | 11.1 | 10.6 | 18.7 |
| Q2 | 15 | 11.3 | 14.7 | 13.2 | 11.4 | 11.2 | 19.3 |
| Q3 | 15 | 11.2 | 8.3 | 14.6 | 9.2 | 10.1 | 21.3 |
| Q4 | 15 | 10.7 | 11.6 | 11.8 | 6.9 | 8.4 | 13.3 |
| Q5 | 15 | 18.6 | 9.7 | 14.3 | 10.6 | 11.8 | 10.8 |
| Q6 | 15 | 10.8 | 13.0 | 11.2 | 11.5 | 10.9 | 14.7 |
| Q7 | 15 | 12.3 | 14.7 | 11.0 | 11.4 | 10.9 | 10.7 |
| Q8 | 15 | 10.5 | 27.8 | 33.6 | 17.4 | 22.8 | 6.7 |
| Q9 | 15 | 13.3 | 18.5 | 13.4 | 15.5 | 12.8 | 14.7 |
| Q10 | 15 | 17.1 | 15.8 | 20.5 | 16.1 | 17.0 | 13.3 |
| Q11 | 15 | 16.0 | 11.4 | 13.7 | 8.8 | 9.3 | 15.3 |
| Q12 | 15 | 13.9 | 6.7 | 9.4 | 9.4 | 9.1 | 12.0 |


## Task 2a: learning curve (teacher-graded essays per question -> anchors; random draws, 10 reps; k=min(5,n) stratified)

| n | reps | anchored MAE % (mean +- sd) | blend MAE % | blend Pearson | blend letters exact % | blend within-1 % | anch exact % | blend A+ P % | blend A+ R % |
|---|---|---|---|---|---|---|---|---|---|
| 0 (direct only) | - | - | 13.3 | 0.772 | 36 | 81 | - | 45 | 54 |
| 2 | 10 | 17.3 +- 1.6 | 12.3 +- 0.6 | 0.798 | 41 +- 3 | 80 +- 3 | 34 | 62 | 53 |
| 3 | 10 | 15.7 +- 1.1 | 11.7 +- 0.5 | 0.815 | 45 +- 2 | 83 +- 2 | 35 | 68 | 57 |
| 5 | 10 | 14.1 +- 1.6 | 11.4 +- 0.6 | 0.827 | 45 +- 3 | 83 +- 2 | 39 | 66 | 59 |
| 8 | 10 | 13.0 +- 0.6 | 11.2 +- 0.2 | 0.831 | 44 +- 2 | 84 +- 1 | 41 | 68 | 55 |
| 10 | 1 | 13.6 +- 0.0 | 11.6 +- 0.0 | 0.818 | 46 +- 0 | 86 +- 0 | 39 | 75 | 51 |

Paired question-level bootstrap on rep-averaged blend MAE (pts, negative = better) vs direct-only, and vs n=5:
- n=2 blend minus direct: -0.96 [-2.46, +0.50]
- n=3 blend minus direct: -1.57 [-3.21, -0.02]
- n=5 blend minus direct: -1.90 [-3.44, -0.42]
- n=8 blend minus direct: -2.02 [-3.65, -0.44]
- n=10 blend minus direct: -1.65 [-3.81, +0.64]
- n=8 blend minus n=5 blend: -0.13 [-0.53, +0.25]
- n=10 blend minus n=5 blend: +0.25 [-0.67, +1.32]

n=5 anchored: per-question MAE mean +- sd across draws (shows draw sensitivity):

| Q | anch n=5 | blend n=5 | anch n=10 strat |
|---|---|---|---|
| Q1 | 12.9 +- 2.4 | 11.3 +- 1.4 | 10.7 |
| Q2 | 15.5 +- 2.4 | 11.4 +- 0.8 | 14.7 |
| Q3 | 9.7 +- 2.2 | 8.5 +- 0.4 | 8.3 |
| Q4 | 19.8 +- 8.0 | 9.0 +- 2.5 | 11.6 |
| Q5 | 12.3 +- 2.8 | 11.3 +- 1.3 | 9.7 |
| Q6 | 14.3 +- 1.5 | 12.1 +- 0.6 | 13.0 |
| Q7 | 11.1 +- 2.8 | 10.1 +- 0.8 | 14.7 |
| Q8 | 17.6 +- 5.8 | 12.8 +- 2.6 | 27.8 |
| Q9 | 14.6 +- 2.1 | 13.3 +- 1.2 | 18.5 |
| Q10 | 15.9 +- 2.3 | 15.8 +- 0.9 | 15.8 |
| Q11 | 14.8 +- 5.4 | 9.9 +- 1.4 | 11.4 |
| Q12 | 10.8 +- 3.6 | 10.7 +- 0.9 | 6.7 |

## Task 2b: anchor selection strategy (pool of 10 teacher-graded per question, 5 used per essay)

| strategy | anchored MAE % | blend MAE % | blend Pearson | blend exact % | blend within-1 % | A+ P % | A+ R % | blend minus random (pts) [95% CI] |
|---|---|---|---|---|---|---|---|---|
| random 5 of 10 (mean of 10 draws; = n=5 row) | 14.1 | 11.4 +- 0.6 | 0.827 | 45 | 83 | 66 | 59 | 0 |
| stratified by score (current: 5 evenly spaced ranks) | 13.6 | 11.6 | 0.818 | 46 | 86 | 75 | 51 | +0.25 [-0.67, +1.32] |
| extremes+middle (2 lowest, median, 2 highest) | 12.4 | 11.1 | 0.838 | 46 | 85 | 71 | 57 | -0.26 [-0.96, +0.50] |
| kNN k=5 (char-3gram TF-IDF cosine, per essay) | 15.9 | 11.6 | 0.818 | 40 | 84 | 68 | 54 | +0.28 [-0.56, +1.08] |
| kNN k=3 | 17.1 | 11.8 | 0.803 | 47 | 83 | 62 | 60 | +0.48 [-0.42, +1.43] |
| hybrid: lowest + highest + 3 nearest | 13.0 | 11.0 | 0.834 | 44 | 87 | 80 | 46 | -0.31 [-1.21, +0.59] |
- extremes+middle blend minus stratified blend: -0.51 [-1.86, +0.70]
- kNN k=5 blend minus stratified blend: +0.03 [-1.29, +1.06]
- hybrid blend minus stratified blend: -0.56 [-1.56, +0.29]
## Task 3: adaptive weighting from anchor self-validation

| Q | LOO err direct (anchors) | LOO err anch (anchors) | hold-out direct | hold-out anch |
|---|---|---|---|---|
| Q1 | 8.5 | 8.8 | 13.3 | 10.7 |
| Q2 | 14.9 | 9.6 | 11.3 | 14.7 |
| Q3 | 7.3 | 8.4 | 11.2 | 8.3 |
| Q4 | 15.5 | 15.3 | 10.7 | 11.6 |
| Q5 | 14.9 | 8.7 | 18.6 | 9.7 |
| Q6 | 8.7 | 13.1 | 10.8 | 13.0 |
| Q7 | 20.1 | 14.3 | 12.3 | 14.7 |
| Q8 | 25.9 | 19.7 | 10.5 | 27.8 |
| Q9 | 17.2 | 14.7 | 13.3 | 18.5 |
| Q10 | 15.4 | 7.7 | 17.1 | 15.8 |
| Q11 | 19.6 | 13.2 | 16.0 | 11.4 |
| Q12 | 12.5 | 11.4 | 13.9 | 6.7 |

Pearson over 12 questions of (anchor-LOO err_anch - err_dir) vs (hold-out err_anch - err_dir): -0.108
Pearson of anchor-LOO err vs hold-out err: direct 0.044, anchored 0.670

| rule | MAE % | Pearson | exact | within-1 | A+ P | A+ R | paired vs blend2 (pts) [95% CI] | Q5 MAE | Q8 MAE |
|---|---|---|---|---|---|---|---|---|---|
| fixed 50/50 (blend2) | 11.6 | 0.818 | 46 | 86 | 75 | 51 | +0.00 [+0.00, +0.00] | 10.6 | 17.4 |
| direct only | 13.3 | 0.772 | 36 | 81 | 45 | 54 | +1.65 [-0.66, +3.82] | 18.6 | 10.5 |
| anchored only | 13.6 | 0.751 | 39 | 78 | 72 | 51 | +1.98 [+0.31, +3.95] | 9.7 | 27.8 |
| R1 inverse-error | 11.6 | 0.813 | 46 | 86 | 76 | 54 | +0.00 [-0.33, +0.34] | 9.5 | 18.8 |
   - weights w_anch: Q1=0.49, Q2=0.61, Q3=0.47, Q4=0.50, Q5=0.63, Q6=0.40, Q7=0.58, Q8=0.57, Q9=0.54, Q10=0.67, Q11=0.60, Q12=0.52
| R2 inverse-square | 11.7 | 0.806 | 45 | 85 | 70 | 54 | +0.13 [-0.39, +0.73] | 9.2 | 20.2 |
   - weights w_anch: Q1=0.48, Q2=0.71, Q3=0.43, Q4=0.51, Q5=0.75, Q6=0.30, Q7=0.66, Q8=0.63, Q9=0.58, Q10=0.80, Q11=0.69, Q12=0.55
| R3 softmax T=0.02 | 13.0 | 0.764 | 41 | 81 | 69 | 51 | +1.34 [+0.05, +3.04] | 9.6 | 26.9 |
   - weights w_anch: Q1=0.46, Q2=0.94, Q3=0.37, Q4=0.52, Q5=0.96, Q6=0.10, Q7=0.95, Q8=0.96, Q9=0.78, Q10=0.98, Q11=0.96, Q12=0.64
| R3 softmax T=0.05 | 12.1 | 0.793 | 43 | 84 | 70 | 54 | +0.49 [-0.28, +1.56] | 9.3 | 23.1 |
   - weights w_anch: Q1=0.48, Q2=0.75, Q3=0.45, Q4=0.51, Q5=0.78, Q6=0.29, Q7=0.76, Q8=0.77, Q9=0.62, Q10=0.82, Q11=0.78, Q12=0.56
| R3 softmax T=0.1 | 11.7 | 0.807 | 45 | 86 | 70 | 54 | +0.13 [-0.36, +0.77] | 9.3 | 20.5 |
   - weights w_anch: Q1=0.49, Q2=0.63, Q3=0.47, Q4=0.50, Q5=0.65, Q6=0.39, Q7=0.64, Q8=0.65, Q9=0.56, Q10=0.68, Q11=0.65, Q12=0.53
| R4 gate ratio>1.3 | 13.1 | 0.761 | 43 | 79 | 76 | 54 | +1.48 [+0.06, +3.36] | 9.7 | 27.8 |
   - weights w_anch: Q1=0.50, Q2=1.00, Q3=0.50, Q4=0.50, Q5=1.00, Q6=0.00, Q7=1.00, Q8=1.00, Q9=0.50, Q10=1.00, Q11=1.00, Q12=0.50
| R5 shrunk .5*R1+.25 | 11.6 | 0.816 | 46 | 86 | 75 | 51 | -0.00 [-0.17, +0.17] | 10.0 | 18.1 |
   - weights w_anch: Q1=0.49, Q2=0.55, Q3=0.48, Q4=0.50, Q5=0.57, Q6=0.45, Q7=0.54, Q8=0.53, Q9=0.52, Q10=0.58, Q11=0.55, Q12=0.51
| oracle best fixed w (optimistic) | 10.1 | 0.848 | 49 | 89 | 70 | 60 | -1.47 [-2.63, -0.62] | 9.2 | 10.5 |
   - weights w_anch: Q1=0.95, Q2=0.25, Q3=1.00, Q4=0.50, Q5=0.70, Q6=0.00, Q7=0.40, Q8=0.00, Q9=0.05, Q10=0.75, Q11=0.70, Q12=1.00
| 3-member inverse-error (d,a,rubric) | 11.9 | 0.806 | 41 | 83 | 64 | 51 | +0.25 [-0.62, +1.26] | 10.7 | 22.3 |

## Findings

**Task 1 (third member).** The rubric per-criterion score is a weaker standalone member (MAE 14.9, Pearson 0.69) and does NOT improve the ensemble: blend3 equal 12.1 vs blend2 11.6 (paired +0.47 [-0.47,+1.57], not significant but never better). Learned weights (leave-one-question-out) are worse than equal weights: NNLS 12.7, ridge 12.9, simplex-MAE grid 12.5 (paired vs blend2 +0.9 to +1.3, CIs exclude 0 for NNLS/ridge). The learned weight on the rubric is about 0 (NNLS 0.02, grid 0.02), and learned (d,a) weights are about 0.5/0.5. blend3 helps on bad-for-anchored questions (Q9) but loses on Q8 where rubric fails (33.6). Verdict: skip the rubric member (it also costs one extra call).

**Task 2a (learning curve).** Blend MAE vs teacher-graded essays per question: n=0 13.3, n=2 12.3, n=3 11.7, n=5 11.4 +- 0.6, n=8 11.2 +- 0.2, n=10 11.6 (single stratified draw). Gains saturate at n=3-5; n=8 vs n=5 is -0.13 [-0.53,+0.25]. Anchored alone needs n>=8 to match direct (n=5: 14.1 +- 1.6, n=3: 15.7) and is very draw-sensitive per question (Q4 sd 8.0, Q8 5.8, Q11 5.4), whereas the blend damps that variance (sd 0.6 overall). n=2 already gives about -1.0 but CI includes 0. Practical: 3 graded essays/question is enough to get most of the gain; 5 is a safe default; the blend is the only mode that is reliably at least as good as direct.

**Task 2b (selection, pool 10 -> 5).** Blend MAE: random 11.4 +- 0.6 (10 draws), stratified 11.6, extremes+middle 11.1, kNN-5 11.6, kNN-3 11.8, hybrid (lowest + highest + 3 nearest by char-3gram TF-IDF) 11.0. Nobody beats random/stratified by more than 0.6 points and every paired CI contains 0 (e.g. hybrid vs stratified -0.56 [-1.56,+0.29]). kNN alone is worse for anchored scoring (15.9 vs 13.6): similar anchors give little contrast, so score information is lost. Extremes+middle (anchored alone 12.4 vs 13.6) and the hybrid are the best point estimates, consistent with "anchors should span the range", but evidence is weak (single draw each, hold-out only).

**Task 3 (adaptive weights).** Per-question LOO errors on the anchors do not predict hold-out behaviour: correlation of (err_anch - err_dir) between anchors and hold-out is -0.11 (anchored error itself correlates 0.67, direct error 0.04). Direct on Q8 anchors has LOO error 25.9 but 10.5 on hold-out (the older cohort differs), so rules push weight toward anchored exactly on Q8 (w_anch 0.57-0.96), the question where anchored fails (27.8). Results: R1 inverse error 11.6 (paired 0.00 [-0.33,+0.34]); R2 11.7; softmax T=.1 11.7, T=.05 12.1, T=.02 13.0; gating 13.1; shrunk R5 11.6. None beats fixed 50/50; sharper rules are significantly worse. Q5 improves slightly (10.6 -> 9.5 with R1) but Q8 worsens (17.4 -> 18.8). The oracle per-question best weight (10.1, uses hold-out labels) shows the headroom is real but is not recoverable from 10 anchors. Verdict: keep fixed 50/50.

## Recommendation (what to adopt)

1. Keep `EssayEngine` as is: `score = clip((direct + anchored)/2)`, `delta=0.4`, anchors cut via CUT_ESSAY. Do not add the rubric member and do not learn or adapt weights (all tested variants are equal or worse; rubric adds a call).
2. Anchor count: require >= 3 teacher-graded essays per question (blend 11.7), recommend 5 (11.4 +- 0.6), ~8 gives marginal extra (11.2). With n<=2 prefer blend still (12.3) but expect high variance. With 0 anchors use direct only (13.3).
3. Anchor selection when more than 5 are available: use a score-spanning set. Best point estimate: lowest, highest and the 3 other anchors (nearest by char-3gram TF-IDF to the essay, or just the median and quartiles); fall back to the current stratified selection, which is within noise (<=0.6). Do not use kNN-only selection (anchored alone 15.9). If the teacher grades new essays, ask for a spread of scores including a weak and a strong one rather than random ones.
4. Open issue: Q8 (anchored 27.8, rubric 33.6, direct 10.5) and Q5 (direct 18.6) remain unfixed; a weight per question cannot be learned reliably from 10 older anchors. A held-out validation on fresh graded essays from the same cohort would be needed.
