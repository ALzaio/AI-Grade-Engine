# decider-grader

Grade free-text student answers (short answers and essays) with a fast, cheap **decision model**
(a model that returns a probability for each option instead of generating text), plus calibration,
teacher-graded "anchors", confidence triage and prompt-injection guards.

> **Status: research prototype / grading *assistant*.** It saves a teacher's time and is close to
> human-human agreement on the data we tested, but it is **not** a replacement for a human for official grades.
> See [Limitations](#limitations) before using it on real students.

*(Arabic summary at the bottom / الملخص بالعربية في الأسفل)*

**Guides:** [How to run it and how it works](docs/GUIDE.md) · [دليل التشغيل وآلية العمل (بالعربية)](docs/GUIDE.ar.md)

## Why this design

Asking a model to pick a letter grade directly was inconsistent (an "A+" appearing and disappearing between runs).
This engine instead:

1. asks the decision model a few `choice` questions (different prompt variants, one request) and takes the **probability-weighted expected grade**;
2. maps it through an **isotonic calibration** (fit on real teacher marks) to a 0-1 score;
3. turns the score into A+..F with fixed cutoffs, and flags uncertain answers for **human review**;
4. optionally uses a few **teacher-graded anchors per question** (a per-question offset for short answers, comparisons for essays).

Re-running the same answer changes the score by ~0.4 points on average (A+ decision flips in ~1% of cases).

## Install

No dependencies (standard library only), Python 3.9+.

```bash
git clone <your-fork-url> && cd decider-grader
export OPENROUTER_API_KEY=sk-or-...      # Windows PowerShell: $env:OPENROUTER_API_KEY="sk-or-..."
python examples/quickstart.py
```

The default model is OpenRouter's **free** `perplexity/pplx-decider-v1.3:free` on the *alpha* decisions endpoint
(`/api/alpha/decisions`). It is an experimental API and may change or disappear; free models have daily limits.
Non-free models are **blocked** unless you set `ALLOW_PAID=1` (see *Cost* below).

## Usage

```python
from decider_grader import Engine, ShortAnchoredEngine, EssayEngine, guarded_grade

# 1) short answer, nothing graded yet
eng = Engine(lang="ar")          # or lang="en"; calibration fit on real Arabic / English answers
r = eng.grade("ما وظيفة الميتوكندريا؟", "تنتج الطاقة على شكل ATP عبر التنفس الهوائي.", "تنتج الطاقة ATP بالتنفس الهوائي")
# {'score': 0.99, 'letter': 'A+', 'needs_review': False, ...}

# 2) short answers with ~5 teacher-graded answers for this question: per-question bias correction
anchors = [("answer text", 0.9), ("another", 0.4), ...]       # (student answer, teacher score in 0..1)
eng = ShortAnchoredEngine(anchors, engine=Engine(lang="ar"))

# 3) essays with 3-5 teacher-graded essays per question: mean(direct, anchored comparisons)
eng = EssayEngine(anchors)
r = eng.grade(question, reference, essay, criteria=None)

# 4) ALWAYS wrap student text with the guards in a real deployment
r = guarded_grade(eng, question, reference, student_text, essay=False)
```

## Measured accuracy (real teacher-graded data, Arabic)

"Error" = mean absolute difference between the engine and the average of two teachers' marks, in points out of 100.
Confidence intervals resample **questions** (not answers). Two teachers differ from each other by the "humans" column.

| mode | data | error (95% CI) | two teachers differ by |
|---|---|---|---|
| `Engine(lang="ar")`, nothing graded | 2102 short answers, 46 questions (AR-ASAG) | **13.0%** (calibration fit by cross-validation over questions) | 11.3% |
| `ShortAnchoredEngine`, 5 graded answers/question | same 2102 answers | **12.8%** (-1.1 [-1.5, -0.6] vs no anchors) | 11.3% |
| `EssayEngine`, 5 graded essays/question | 1938 short essays, 12 questions (AR-AES) | **11.1%** [10.1, 12.1] | 15.2% [11.8, 17.8] |

The accuracy numbers are cross-validated over questions. The calibration **shipped** in `default_calibration.json` is fit on all
2102 Arabic (AR-ASAG) and 100 English (SciEntsBank) answers, so measured on those same answers it looks better than it is:
re-calibrate on your own course data for honest numbers.

Letters (A+ ≥ 93 in essay mode, ≥ 87 in short mode; A ≥ 83/80, B ≥ 70, C ≥ 55, D ≥ 40): exact letter 38-46%, within one letter 80-86%;
two human teachers agree on the exact letter only 49-56% of the time.
Triage: auto-grading the ~50% most certain answers gives 7-11% error on those; the rest go to the teacher.
A+ in short answers is the weak spot (it finds ~80% of the true A+ answers but only 41-57% of its A+ calls are right).

Everything above and everything that did **not** work (25 prompt variants, label-free batch tricks, a rubric member in the
ensemble, adaptive weights, a paid model, ...) is documented in [`docs/FINDINGS.md`](docs/FINDINGS.md) and `docs/reports/`.

## Limitations

- Tested mostly on **Arabic** data from one university. English is **weaker and thinly tested**: on 600 SciEntsBank answers from 11
  unseen-domain questions (labels are only correct / partially correct / incorrect) the engine separates *correct* from
  *incorrect* well (AUC 0.92) but scores *partially correct* answers too high (mean 0.72 vs 0.86 for correct and 0.31 for
  incorrect): 3-way accuracy 59%, 72% for correct-vs-not. Use English results with caution and re-calibrate.
- "Essays" in the data are short (≈68 words). Long essays are **untested**.
- Error of 11-13 points means a 70 can really be 57-83. Do not publish final grades without human review.
- Prompt-injection guards stop the simple attacks we tried (forged prompt blocks, "give me A+", empty/echo/repeated-reference
  answers) but **not** keyword stuffing, and hand-written attacks are not adaptive attackers. Guard code reads student text with the model too.
- Calibration constants were fit on the public datasets below; re-calibrate per course with `Engine.fit([...])` (>=10 graded answers).
- The decision-model endpoint is an alpha API.

## Cost

The default model is free. We learned the hard way that "cheap" paid reasoning models can bill thousands of hidden tokens
per call, so `client._guard_paid` refuses any non-`:free` model unless `ALLOW_PAID=1`. Measure real spend on 20 calls first.

## Data (not included)

The datasets are **not** redistributed here. Fetch them yourself and check their licences:

- **AR-ASAG** (Arabic short answers, Ouahrani & Bennouar, LREC 2020) — Mendeley Data, DOI 10.17632/dj95jh332j.1
- **AR-AES** (Arabic essays, Ghazawi & Simpson, arXiv 2407.11212) — link in the paper (OSF)
- **SciEntsBank** (English short answers, SemEval-2013 Task 7) — Hugging Face `nkazi/SciEntsBank`, CC-BY-4.0

`python scripts/fetch_data.py` downloads AR-ASAG and a sample of SciEntsBank into `data/` (git-ignored).

## Tests

```bash
python -m unittest discover -s tests -v     # offline, no key needed (the model is faked)
```

## License

MIT (see `LICENSE`). Datasets and the OpenRouter models have their own terms.

---

## الملخص بالعربية

محرّك تصحيح للإجابات الحرة (جمل قصيرة ومقالات) يعتمد على **نماذج القرار** (decision models) السريعة والرخيصة:
بدل أن نطلب من النموذج اختيار الحرف مباشرة (وهذا غير متسق)، نأخذ احتمالات الدرجات ونحسب منها درجة، ثم نعاير الدرجة على
تصحيحات معلمين حقيقيين، ونفرز الإجابات غير المؤكدة للمراجعة البشرية. ويستخدم، اختيارياً، بضع إجابات يصححها المعلم لكل سؤال.

- **الدقة:** متوسط الخطأ 11-13 نقطة من 100 على بيانات عربية حقيقية، وبمستوى اتفاق معلمين مع بعضهما تقريباً.
- **ليس بديلاً عن المعلم:** هو مساعد يوفر الوقت. لا تعتمده كدرجة رسمية وحيدة.
- **حدوده:** اختُبر أساساً على العربية من جامعة واحدة، والمقالات قصيرة، والإنجليزية بعينة صغيرة.
- **مجاني بشكل افتراضي**، ويرفض أي نموذج مدفوع ما لم تضبط `ALLOW_PAID=1`.
- **البيانات غير مرفقة:** نزّلها من مصادرها وتحقق من تراخيصها (`scripts/fetch_data.py`).
