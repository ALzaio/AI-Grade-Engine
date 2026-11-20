# Engine at scale: AR-ASAG (short) and AR-AES (essays)
All numbers in percent. [..] = 95% bootstrap CI, resampling QUESTIONS (1000 resamples; 2000 for the headline paired tests). Engine/common/existing files untouched. Scripts: lib.py, a_grade.py, a_analyze.py, b_grade.py, b_analyze.py; raw per-answer predictions: a_results.json, b_results.json.

## C. What is robust and what is noise (read first)
Robust (CI excludes the alternative):
- Short answers: Engine MAE ~14% [12.8, 15.0] vs human-human 11.3% [10.1, 12.6]; the engine is roughly 2.5 pp worse than a second teacher, and only 10/46 questions are at or below human-human MAE. r = 0.79-0.80. Within-one-letter ~80%.
- Uncertainty triage works: auto-grading the most certain 40% gives MAE 10.9 [9.6, 12.4] vs 13.9 overall (the same subset gets lower human-human disagreement too, 9.2% vs 11.3%, i.e. part of "uncertainty" is intrinsically ambiguous answers). The needs_review flag auto-grades only 48% (not the advertised ~60%) at MAE 11.5%.
- Essays: blend beats direct by -2.2 pp [-4.0, -0.4] and anchored by -2.2 pp [-3.9, -0.9] (paired). Blend (11.1%) is also better than human A-vs-B (15.2%) by -4.0 pp [-7.0, -0.0] (borderline). Anchored alone vs direct alone: no difference (+0.04 [-2.0, +2.5]).
- Anchored alone: delta 0.55 is clearly worse than 0.3/0.4; k=3 is worse than k>=5 (paired CIs exclude 0).

Noise / not resolved:
- Direct or anchored vs the human A-vs-B MAE on essays (CIs span 0; humans are noisy, 12 questions only).
- Within the blend, k in {5, 9} and delta in {0.3, 0.4} are statistically indistinguishable (k=9,d=.3 best at 10.9; k5,d.4 = 11.1, diff +0.27 [-0.14, +0.85]). The current default (k=5, delta=.4) is therefore fine; going to k=9 buys at most ~0.3 pp for ~2x prompt length.
- Anchored alone prefers a lower delta (0.3) and more anchors (k=9: 12.0 vs 13.3), but this is a shrink effect: blending removes most of the gap.
- Letter exact accuracy differences between methods (40.6 / 40.9 / 46.6) overlap in CIs; the human A-vs-B letter agreement (43.2) is not different from the engine's.
- A+ precision/recall on essays: very wide CIs (30-77%); do not read anything into direct vs anchored. A+ precision on short answers is only 40.6 [32.3, 49.6] at recall 80 [69, 88] (CUT_SHORT lowers the A+ cutoff so recall is high, precision low).
- Per-question differences in the table on essays (n~100-270 each) are descriptive only; 12 clusters => CIs are wide and likely a bit optimistic (small-cluster bootstrap).
- Question-type and length-tercile differences on short answers: all CIs overlap heavily; no robust effect. (Weak hint: answer-length has no effect on MAE, but exact-letter accuracy drops from 46 to 31 for long answers; and "difference" questions have the lowest correlation, 68.)

Surprises: (1) the "anchored beats direct" claim (11.9 vs 15.7 on 120 essays) does NOT reproduce at scale: both are 13.3 here; only the blend is better. (2) Caveat on the human ceiling: gold = mean of two raters, so engine-vs-gold error is computed against a less noisy target than a single human-vs-human difference; MAE vs human-human is not strictly like-for-like (it flatters the engine somewhat). On essays the engine (blend 11.1%) is below the A-vs-B gap (15.2%), on short answers above it (13.9 vs 11.3). (3) Systematic bias on short answers: the worst questions (e.g. the two "ما الفرق" worm/virus questions) are over-scored by ~15-19 pp (mean pred 81 vs gold 62).

## A. Short answers: AR-ASAG, all 2102 answers, 46 questions
Frozen Engine() with default calibration (fit on 100 AR-ASAG + 100 SciEntsBank answers). Overlap: the 100 AR calibration answers (real_ar.json; 102 rows matched by text incl. duplicates) are inside this set (about 5%); the pure hold-out row below excludes them and numbers are unchanged. hold_ar.json (288 answers) is also included (never used for calibration). True letters from gold avg/5 with cutoffs [.93,.83,.70,.55,.40]; predicted letters use the Engine's CUT_SHORT [.87,.80,.70,.55,.40]. Types: classified from the question's opening verb. Length terciles are over all answers (words).


### Headline (all answers; full set, includes the 100 calibration answers)
| metric | value [CI] |
|---|---|
| Engine MAE (% of full mark) | 13.9 [12.8, 15.0] |
| Pearson r (x100) | 79.5 [76.3, 82.4] |
| within 10% | 45.8 [41.6, 49.9] |
| within 20% | 74.5 [70.8, 78.4] |
| letter exact | 37.9 [34.8, 41.4] |
| letter within one | 80.2 [77.6, 83.1] |
| A+ precision | 40.6 [32.3, 49.6] |
| A+ recall | 79.9 [69.4, 88.5] |
| HUMAN Mark1 vs Mark2 MAE | 11.3 [10.1, 12.6] |
| HUMAN within 10% | 62.9 [58.9, 66.5] |
| HUMAN within 20% | 86.0 [82.5, 89.2] |
| HUMAN Pearson (x100) | 83.6 [79.7, 87.0] |
| HUMAN letter agreement (exact) | 55.7 [52.2, 59.4] |
| HUMAN letter within one | 84.7 [81.2, 88.1] |

### Pure hold-out (excluding the 102 calibration answers; n=2000)
| metric | value [CI] |
|---|---|
| MAE | 13.9 [12.8, 15.0] |
| Pearson (x100) | 79.2 [75.7, 82.3] |
| within 10% | 45.6 [41.4, 49.7] |
| within 20% | 74.2 [70.4, 78.0] |
| letter exact | 37.5 [34.3, 41.1] |
| letter within one | 80.0 [77.3, 82.9] |
| A+ precision | 40.6 [31.9, 49.9] |
| A+ recall | 80.2 [69.6, 89.3] |

### Triage: auto-grade the most certain X% (MAE on the auto-graded part)
| policy | share auto-graded | MAE on auto-graded [CI] |
|---|---|---|
| uncertainty rank top 40% | 40% | 10.9 [9.6, 12.4] |
| uncertainty rank top 60% | 60% | 12.1 [10.9, 13.3] |
| uncertainty rank top 80% | 80% | 13.0 [11.9, 14.2] |
| uncertainty rank top 100% | 100% | 13.9 [12.8, 15.0] |
| needs_review flag false | 48.4 [43.1, 53.6] | 11.5 [10.5, 12.7] |

(MAE of flagged-for-review answers: 16.1%; human-human MAE on them 13.3%; human-human on the auto-graded: 9.2%)

### By question type
| group | n | #questions | MAE [CI] | human MAE | Pearson | letter exact | within 10% |
|---|---|---|---|---|---|---|---|
| consequences (ما النتائج) | 288 | 6 | 12.9 [10.1, 15.5] | 10.5 | 84 | 44 | 51 |
| define (عرف) | 297 | 6 | 15.0 [11.5, 18.4] | 12.7 | 78 | 33 | 43 |
| difference (ما الفرق) | 222 | 5 | 14.9 [10.9, 18.6] | 10.4 | 68 | 27 | 41 |
| justify (علل) | 475 | 10 | 14.5 [12.8, 16.3] | 12.8 | 77 | 35 | 43 |
| list (ماهي/أذكر) | 557 | 13 | 12.6 [11.0, 14.3] | 10.7 | 84 | 44 | 50 |
| other (كيف/ما نوع/فيم/بماذا) | 263 | 6 | 14.3 [12.0, 17.9] | 9.9 | 76 | 39 | 44 |

### By answer length tercile (words: short<=14, medium<=23, long>23)
| group | n | #questions | MAE [CI] | human MAE | Pearson | letter exact | within 10% |
|---|---|---|---|---|---|---|---|
| short | 731 | 44 | 14.0 [12.8, 15.3] | 10.2 | 79 | 46 | 47 |
| medium | 707 | 45 | 14.1 [13.0, 15.2] | 11.9 | 77 | 36 | 45 |
| long | 664 | 44 | 13.5 [11.9, 15.0] | 11.9 | 72 | 31 | 46 |

### Per question: 5 worst by MAE
| question | n | Engine MAE | human-human MAE | mean gold | mean pred |
|---|---|---|---|---|---|
| ما نوع الجريمة الإلكترونية التي قد تكون أنت  ضحيته | 37 | 22.9 | 16.8 | 34 | 50 |
| عرف مصطلح تبييض أو غسيل الأموال | 52 | 21.6 | 23.6 | 39 | 55 |
| ما الفرق بين الدود والفيروسات؟ | 50 | 19.4 | 13.5 | 62 | 81 |
| ما الفرق بين الفيروس و برنامج الإنزال ؟ | 42 | 19.0 | 11.7 | 58 | 75 |
| علّل لماذا لا تفكر المؤسسات غالبا في دعم سياسة الأ | 51 | 18.5 | 22.4 | 47 | 58 |

5 best:

| question | n | Engine MAE | human-human MAE |
|---|---|---|---|
| ماهي أشكال المضايقات التي يمكن أن يتعرض لها مستخدم | 48 | 8.8 | 6.9 |
| ما الفرق بين عمل قراصنة القبعات البيضاء و عمل قراص | 48 | 8.3 | 8.8 |
| أذكر الصفات السلوكية التي تستخدم عادة في القياس ال | 25 | 8.0 | 5.2 |
| ماهي النتائج المترتبة عن  إصابة  النظام المعلوماتي | 49 | 8.0 | 10.6 |
| عرف مصطلح الجريمة الإلكترونية | 47 | 7.4 | 10.4 |

Per-question MAE spread: median 13.5%, min 7.4%, max 22.9%; questions with Engine MAE <= human MAE: 10/46
Correlation across questions between Engine MAE and human MAE: 0.37

## B. Essays: AR-AES. AR-AES: 1938 essays graded, 12 questions (anchors excluded). Of these 575 were already used elsewhere (real_aes/hold_aes); anchors were drawn ONLY from essays not in real_aes/hold_aes. 9 anchors/question stratified by Average_Score at ranks round(t*(n-1)/8), t=0..8, from unused essays; k=5 uses ranks 0,2,4,6,8 of those 9 (evenly spaced quintile-like), k=3 uses 0,4,8, k=9 all 9; the same 9 are excluded from the eval set for every config so all configs grade the same essays.
Direct = Engine().grade (default calibration, fit on short answers). Anchored = AnchoredEngine(k=5, delta=.4) with rubric criteria. Blend = mean of both (EssayEngine logic). Letters for all methods use cutoffs [.93,.83,.70,.55,.40]. Bootstrap resamples the 12 questions (1000) -- with only 12 clusters CIs are wide and slightly optimistic.

### Main comparison
| metric | direct | anchored k5 d.4 | blend | HUMAN A vs B |
|---|---|---|---|---|
| MAE | 13.3 [12.0, 14.8] | 13.3 [12.0, 15.0] | 11.1 [10.1, 12.1] | 15.2 [11.8, 17.8] |
| within 10% | 47.7 [42.2, 53.4] | 48.0 [40.9, 53.8] | 55.9 [50.1, 61.4] | 48.3 [42.8, 55.4] |
| within 20% | 76.6 [72.0, 80.7] | 76.7 [71.6, 80.8] | 84.2 [80.5, 87.9] | 72.7 [65.3, 82.5] |
| Pearson x100 | 79.6 [69.8, 84.7] | 81.6 [73.7, 85.6] | 85.0 [79.2, 87.8] | 74.0 [67.6, 80.4] |
| letter exact | 40.6 [32.3, 48.1] | 40.9 [32.4, 47.1] | 46.6 [42.4, 50.3] | 43.2 [38.5, 49.6] |
| letter within one | 78.7 [70.3, 85.9] | 78.5 [72.5, 83.2] | 84.8 [81.5, 88.4] | 71.9 [65.8, 80.5] |
| A+ precision | 47.8 [30.3, 76.8] | 64.8 [54.0, 79.2] | 69.2 [55.6, 82.8] | - |
| A+ recall | 63.2 [46.8, 76.0] | 52.4 [36.5, 71.5] | 52.6 [40.5, 64.3] | - |

### Paired bootstrap of MAE difference (percentage points; negative = first is better)
| comparison | diff [95% CI] | P(diff<0) | significant? |
|---|---|---|---|
| blend - direct | -2.17 [-4.01, -0.39] | 0.993 | yes |
| blend - anchored | -2.21 [-3.92, -0.88] | 1.000 | yes |
| anchored - direct | +0.04 [-1.95, +2.48] | 0.498 | no |
| direct - humanMAE(A vs B) | -1.86 [-5.17, +2.83] | 0.797 | no |
| anchored - humanMAE(A vs B) | -1.82 [-5.26, +2.62] | 0.796 | no |
| blend - humanMAE(A vs B) | -4.03 [-6.98, -0.02] | 0.976 | yes |

### Anchored grid: MAE % [CI] (anchored alone)
| k \ delta | 0.3 | 0.4 | 0.55 |
|---|---|---|---|
| 3 | 13.3 [12.0, 15.1] | 13.3 [11.8, 15.3] | 14.6 [12.7, 17.1] |
| 5 | 12.4 [11.4, 13.8] | 13.3 [12.0, 15.0] | 14.9 [13.0, 17.6] |
| 9 | 12.0 [11.2, 12.8] | 13.8 [12.8, 14.9] | 15.9 [14.4, 18.1] |

### Blend (direct + anchored) grid: MAE % [CI]
| k \ delta | 0.3 | 0.4 | 0.55 |
|---|---|---|---|
| 3 | 11.9 [10.8, 13.0] | 11.7 [10.6, 12.9] | 11.8 [10.5, 13.2] |
| 5 | 11.2 [10.2, 12.2] | 11.1 [10.1, 12.1] | 11.5 [10.4, 12.6] |
| 9 | 10.9 [10.0, 11.8] | 10.9 [10.1, 11.9] | 11.4 [10.5, 12.4] |

Best anchored: k=9, delta=0.3. Paired MAE difference of each other config minus best (anchored):
| config | diff pp [CI] | significant? |
|---|---|---|
| k=3, d=0.3 | +1.35 [+0.24, +2.92] | yes |
| k=3, d=0.4 | +1.34 [+0.03, +3.16] | yes |
| k=3, d=0.55 | +2.65 [+0.98, +5.00] | yes |
| k=5, d=0.3 | +0.43 [-0.13, +1.29] | no |
| k=5, d=0.4 | +1.35 [+0.55, +2.37] | yes |
| k=5, d=0.55 | +2.94 [+1.35, +5.07] | yes |
| k=9, d=0.4 | +1.79 [+1.33, +2.38] | yes |
| k=9, d=0.55 | +3.96 [+2.66, +5.54] | yes |

Best blend: k=9, delta=0.3. Paired MAE difference of each other config minus best (blend):
| config | diff pp [CI] | significant? |
|---|---|---|
| k=3, d=0.3 | +1.03 [+0.56, +1.68] | yes |
| k=3, d=0.4 | +0.85 [+0.22, +1.69] | yes |
| k=3, d=0.55 | +0.98 [+0.17, +2.06] | yes |
| k=5, d=0.3 | +0.35 [+0.04, +0.73] | yes |
| k=5, d=0.4 | +0.27 [-0.14, +0.85] | no |
| k=5, d=0.55 | +0.59 [-0.03, +1.59] | no |
| k=9, d=0.4 | +0.08 [-0.12, +0.29] | no |
| k=9, d=0.55 | +0.54 [+0.05, +1.13] | yes |

### Per question (12): MAE %
| Q | n | direct | anchored | blend | human A-B | mean gold |
|---|---|---|---|---|---|---|
| Q1 | 270 | 12.3 | 11.2 | 10.8 | 21.3 | 65 |
| Q2 | 270 | 12.8 | 14.0 | 12.2 | 20.5 | 48 |
| Q3 | 270 | 10.4 | 11.1 | 9.5 | 19.7 | 57 |
| Q4 | 172 | 15.9 | 16.5 | 7.3 | 14.9 | 76 |
| Q5 | 172 | 15.6 | 12.0 | 11.2 | 10.3 | 75 |
| Q6 | 172 | 8.4 | 18.6 | 12.9 | 12.6 | 86 |
| Q7 | 107 | 14.7 | 11.9 | 11.8 | 10.7 | 81 |
| Q8 | 107 | 13.8 | 16.7 | 13.5 | 8.4 | 49 |
| Q9 | 107 | 16.4 | 11.7 | 12.7 | 8.2 | 57 |
| Q10 | 97 | 14.8 | 10.5 | 9.9 | 10.5 | 68 |
| Q11 | 97 | 16.7 | 15.5 | 12.9 | 13.5 | 68 |
| Q12 | 97 | 15.2 | 11.2 | 11.6 | 10.6 | 78 |

anchors-excluded essays never used before: n=1363; MAE direct 12.9, anchored 13.6, blend 10.9, human 16.1

previously used essays: n=575; MAE direct 14.3, anchored 12.7, blend 11.6, human 12.9

Mean predicted vs gold: direct 69, anchored 62, gold 66

Runtime/cost: 2102 short answers in ~200 s; essays 1938 x (1 direct + 9 anchored configs; only 3 distinct requests per essay, delta is computed from the same cached response) in ~7 min with 6 threads, no errors. Note: anchors are teacher-graded essays, so the anchored/blend numbers need ~5-9 teacher-graded essays per question; "direct" does not.
