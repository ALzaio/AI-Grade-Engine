# Short-answer (AR-ASAG) error analysis and cheap-fix test

Scripts: ea.py (ranking), rd.py (reading answers), feats.py (new decider features, cached; feats.json), evalfix.py (2-fold by question), diag.py (diagnostics).

## 1. Error analysis
Engine MAE 13.88% (2102 rows); mean bias +5.4 points (over-scoring). Errors above 20 points: 25.5% of rows; 74% of those are over-scoring (18.9% of all rows over by >20 pts, 6.7% under by >20 pts).
Worst questions by MAE (bias = engine - gold): q7 phishing-prize crime type 22.9% (+16.6); q3 money laundering define 21.6% (+16.4); q43 worm vs virus 19.4% (+18.9); q45 virus vs dropper 19.0% (+16.6); q34 why orgs skip early security 18.5% (+10.8); q39 importance of security in design 18.3% (+7.4); q5 organised cybercrime define 17.9% (+8.1); q11 psych-social-engineering methods 16.9% (+10.7). Best: q0 7.4%, q16 8.0%, q25 8.0%, q41 8.3%. Mean teacher-teacher gap per question is 5-24% (q3 23.6%, q34 22.4%, q7 16.8%), so a few of the worst are partly teacher noise.

Failure modes among the 64 most over-scored rows of the 8 worst questions (manual tally, approximate):
- Answer gives a plausible but DIFFERENT reason/related content than the reference (q34, q39, q7): ~22
- Related but wrong/other concept, or generic definition (q3 laundering described as "transferring money", q5, q7 "social engineering"): ~16
- One side only / partial comparison (q43, q45: virus described, worm/dropper side vague or generic malware facts): ~16
- Misses the specific enumerated items (q11: "psychological manipulation" without phone/web/e-mail/face-to-face): ~10
Under-scoring (engine lower than gold by >20 pts) is only 140 rows, and only 4 of them are 6 words or fewer: terse-but-correct answers are NOT the main under-scoring cause (q34/q5 under-scoring are cases where a teacher gave 0.8-1.0 to answers with different wording).
Key structural finding: the teachers are strict; a partially right answer gets 0.15-0.40 where the engine gives 0.5-0.9 (211 of 397 over-scored rows have gold <= 0.25). Per-question bias is mostly question-level (corr of bias with question gold mean -0.54), i.e. engine score is compressed toward the middle. Even an ORACLE that removes each question's bias leaves MAE at 12.0% (vs 13.9%), so the ceiling for any bias-type fix is ~1.9 points; the remainder is within-question noise (within-question corr engine-gold 0.75).

## 2. Candidate fixes (each one extra decider request per answer; free model)
Common frame: "Question / Model answer (reference) / Student answer", answers given as 4 ordered levels with values 1 / .66 / .33 / 0 (full/most/some/none).
- B cov: "The reference answer lists the specific main points the question requires. How many of those main points does the student answer explicitly state correctly? Do not give credit for related-but-different points." levels: all / most (>=2/3) / some (~1/3) / none-or-different.
- C spec: "Does the student answer give the SPECIFIC content that the question asks for (as in the reference answer), or only generic statements that are true of the whole topic but would fit many different questions?"
- err: "Does the student answer contain claims that are wrong or that contradict the reference answer?"
- A strict: existing engine prompt v4 ("strict university examiner ... generic statements deserve a very low mark"), grade expectation.
- D typed: prompt chosen by the leading verb (define/reason/compare/list-consequences-methods), e.g. compare: "The question asks for the DIFFERENCE between two items. Does the student answer correctly state the distinguishing characteristic of EACH of the two items, as in the reference (the contrast itself)? Properties of only one item, or generic facts shared by both, do not count as the difference." (exact texts in feats.py TYP/GEN)
Combiners (fitted on the training fold only; both pre-specified, not selected on test): resid = linear regression gold ~ [iso(raw_expected), new features]; iso2 = isotonic on linear combo of raw_expected + features.

## 3. Results (2-fold by question: train 0-22 -> test 23-45 and swap; pooled predictions; 46 questions)
Letter cutoffs as specified. Paired question-level bootstrap (4000, size-weighted) of MAE difference, negative = better than reference.
Reference rows: engine_score MAE 13.88%, letter exact 37.9% / within-1 80.2%. A fold-fitted isotonic of raw_expected (the fair baseline, since engine_score's calibration saw all questions) gets 13.12% (-0.76 [-1.41,-0.08] vs engine_score), exact 42.2% / w1 82.4%.

| fix (combiner) | MAE | vs engine_score [95% CI] | vs fold baseline [95% CI] | exact / w1 |
|---|---|---|---|---|
| B cov (resid) | 13.08 | -0.79 [-1.44,-0.15] | -0.04 [-0.14,+0.05] | 42.3 / 82.4 |
| C spec (resid) | 13.13 | -0.74 [-1.39,-0.08] | +0.01 [-0.01,+0.04] | 42.0 / 82.6 |
| err (resid) | 13.10 | -0.78 | -0.02 [-0.10,+0.05] | 41.9 / 82.6 |
| A strict v4 (resid) | 13.03 | -0.85 [-1.50,-0.20] | -0.09 [-0.23,+0.04] | 42.0 / 82.4 |
| D typed (resid) | 13.11 | -0.77 | -0.01 [-0.15,+0.13] | 41.6 / 81.8 |
| D+B (resid) | 13.09 | -0.79 | -0.04 [-0.17,+0.09] | 42.0 / 82.2 |
| cov+spec+v4 (resid) | 13.01 | -0.87 [-1.51,-0.22] | -0.12 [-0.28,+0.04] | 41.9 / 82.5 |
| all5 (resid) | 13.06 | -0.82 | -0.06 [-0.26,+0.12] | 41.5 / 82.4 |
| iso2 variants | 13.10-13.39 | -0.77 .. -0.48 | -0.02 .. +0.27 (all CIs include 0) | 39.7-41.8 / 81.4-82.4 |

Per type, engine_score MAE: define (6 q) 15.0, reason (10 q) 14.5, compare (5 q) 14.9, list (25 q) 13.1; fold baseline 13.6/13.6/13.1/12.8 (most of the gain over engine_score is the fold-fit calibration itself, not the new features).
Diagnostics: every new feature correlates 0.75-0.80 with gold, the same as the existing score (raw 0.795), and correlates ~0 with the engine residual (-0.006 .. -0.023); per-question mean feature does not predict per-question bias (|r|<=0.11, except 'err' -0.35, which still did not help). On the worm/virus questions the typed 'compare' feature correlates 0.67 with gold vs 0.80 for the raw score. The typed compare prompt also gives a high mean (0.87) on compare answers where gold is 0.69: the free decider is just as lenient on the one-sided answers when asked directly.

## 4. Recommendation
Adopt NONE of the new decider features. No candidate improves MAE over the fair fold-fitted baseline by more than 0.12 points, every CI includes 0, letters do not improve, and the extra request per answer is cost with no measurable benefit. The apparent -0.8 point gain vs engine_score is just refitting the isotonic calibration (it is a 2-fold fit and engine_score was not out-of-sample per question for the test side in the same way), so do not credit it to the features; treat it as noise-level and not evidence either way (46 questions; CI width ~1.3 points).
What does work (already in the repo): per-question bias correction with ~5 teacher anchors (ShortAnchoredEngine, 13.9 -> 12.8%), which targets the question-level bias that explains ~1.9 of the 2.6 points gap to human level. If no anchors are available, a cheap, untested-here option is only a lower-confidence shrink; not recommended without data. Honest caveat: the decider seems unable to be as strict as the teachers (partial answers get 0.7+ regardless of prompt), so prompt-engineering of this model is likely capped; a stronger decider or per-question anchors is the next lever.
