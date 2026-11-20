# How to run it and how it works

> A grading *assistant*, not a replacement for teachers. Read **Limitations** in `README.md` before using it on real students.
> (Arabic version: [GUIDE.ar.md](GUIDE.ar.md))

## 1) Run it in 5 minutes

**Requirements:** Python 3.9+. No third-party packages (standard library only).

1. **Get an OpenRouter API key** (a free account is enough).
2. **Put the key in an environment variable** (never in code, never in git):
   - Windows PowerShell: `$env:OPENROUTER_API_KEY = "sk-or-..."`
   - Linux / macOS: `export OPENROUTER_API_KEY=sk-or-...`
3. **Run the example** from the repo root:
   ```bash
   python examples/quickstart.py
   ```
   It shows direct grading, grading with teacher-graded answers, and the guard against a forged answer.
4. **Run the tests** (offline, no key needed):
   ```bash
   python -m unittest discover -s tests -v
   ```

## 2) Which mode?

| Your situation | Class | What you provide |
|---|---|---|
| short answers, nothing graded yet | `Engine(lang="ar")` / `lang="en"` | question + reference answer + student answer |
| short answers, you graded ~5 for this question | `ShortAnchoredEngine(anchors)` | list of `(answer text, your score 0..1)` |
| essays, you graded 3-5 per question | `EssayEngine(anchors)` | same list, optionally the grading criteria |
| any student text in a real app | `guarded_grade(...)` around any engine | nothing, just wrap the engine |

Every grade returns a 0-1 score, a letter (A+ ... F) and `needs_review` for uncertain answers.

## 3) Suggested teacher workflow

1. Enter the question and the reference answer.
2. Grade **5 answers yourself**, spanning weak to strong.
3. Run the engine on the rest of the batch (~0.13 s per answer).
4. Accept answers graded with confidence (`needs_review=False`) as a draft and spot-check a sample.
5. Grade the `needs_review` answers (and anything the input guard flagged) yourself.
6. Do not publish final grades without a human look.

## 4) How it works internally

```
student answer ──► [input guards] ──► [decision model] ──► probabilities over A+..F
                    clean + gates      3 prompt variants      (3 questions in ONE request,
                                       in one request          averaged)
                                                                       │
   letter + needs_review ◄── cutoffs ◄── isotonic calibration ◄── expected grade (0..1)
```

1. **Input guards** (`guards.py`): cut forged prompt-template markers, drop instruction-like sentences ("give me A+"), reject empty / repeated / question-echo answers.
2. **Decision model:** returns a **probability per option** instead of generating text. We ask for the grade with three prompt variants in a single request.
3. **Expected grade:** `sum(probability × grade value)`. More stable than taking the arg-max letter, which is what fixes the "A+ that appears and disappears" problem.
4. **Isotonic calibration:** a monotone map that removes the model's bias (it is lenient with partial answers), fit on real teacher marks. You can refit it on your course.
5. **Letter:** fixed cutoffs. In short mode A+ starts at 87, in essay mode at 93.
6. **Anchors** (optional): for short answers we correct a per-question bias from the engine's mean error on your graded answers. For essays we compare the new essay with each anchor (better/similar/worse) and average that with direct grading.
7. **Confidence triage:** uncertainty = spread of the probabilities + how close the score is to the middle. Above the threshold the answer is flagged `needs_review`.

## 5) Re-calibrate on your course

```python
from decider_grader import Engine
samples = [(question, reference, student_answer, teacher_score_0_1), ...]   # >= 10, 30+ is better
eng = Engine().fit(samples)       # isotonic if >= 30 samples, else the mean of isotonic and linear
```

## 6) Environment variables

| Variable | Meaning |
|---|---|
| `OPENROUTER_API_KEY` | your key (required); or `OPENROUTER_API_KEY_FILE` = path of a file containing it |
| `DECIDER_GRADER_CACHE` | request cache directory (default `~/.cache/decider_grader`); `0` disables it |
| `ALLOW_PAID=1` | allow non-free models (blocked by default; read *Cost*) |

## 7) Troubleshooting

- **`429` / `Rate limit exceeded`:** the daily free-model limit. The client retries automatically; if it persists wait for the daily reset (00:00 UTC).
- **`BLOCKED: paid model`:** the model is not free. Do not set `ALLOW_PAID=1` before measuring the real cost on ~20 calls from your account balance.
- **`Set OPENROUTER_API_KEY`:** the variable is not set in the same terminal window you run from.
- **Scores change slightly between runs:** expected (~0.4 points); some requests are served from the cache, so they match exactly.

## 8) Cost

The default is free. We learned the hard way that "cheap" paid reasoning models can cost far more than the price list suggests because they bill thousands of hidden tokens per call. The code therefore refuses any non-`:free` model unless you explicitly allow it. Measure the real cost from your balance before scaling up.

## 9) Where are the experiment details?

`docs/FINDINGS.md` is the full log of everything tried (including what did not work); `docs/reports/` has the large-scale evaluation, prompt search, cold-start and error-analysis reports.
