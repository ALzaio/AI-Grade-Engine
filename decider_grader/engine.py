"""Grading engine: decision-model (pplx free) based. Features -> calibration -> grade."""
import json, math, os, statistics as st
from .client import decide, pmap
MODEL = "perplexity/pplx-decider-v1.3:free"
GR = ["A+", "A", "B", "C", "D", "F"]; GV = {"A+": 1.0, "A": .9, "B": .75, "C": .62, "D": .47, "F": .1}
VARIANTS = {
 "v1": ("Grade the student answer against the reference answer's key content.",
        {"A+": "all key points correct and complete, no errors", "A": "almost all key points, trivial gaps", "B": "most key points, some missing", "C": "about half of key points", "D": "few key points", "F": "wrong or irrelevant"}),
 "v2": ("You are a fair teacher. Compare the student's answer with the reference answer. Judge meaning, not wording: paraphrases, synonyms and informal language are fine. Penalise only missing or wrong content.",
        {"F": "wrong, irrelevant, or contradicts the reference", "D": "only a small part of the required content", "C": "roughly half of the required content", "B": "most required content, one notable gap", "A": "all required content with a minor flaw", "A+": "all required content, correct"}),
 "v4": ("You are a strict university examiner. Mark ONLY what the question specifically asks for, using the reference answer as the mark scheme. An answer that discusses the same general topic but does not provide the specific items the question asks for (for example gives a different definition, a different concept, or generic statements) deserves a very low mark. Vague, generic or only partly relevant statements earn little credit.",
        {"F": "does not give the specific content asked for (even if on the same topic), or wrong", "D": "touches one required item only vaguely", "C": "gives some of the specific required items, with gaps or inaccuracies", "B": "gives most required items correctly", "A": "gives all required items, minor flaw", "A+": "gives all required items fully and correctly"}),
 "v5": ("The reference answer is a thorough model answer and may contain more detail than a full-mark answer needs. A student who states the MAIN ideas of the reference correctly deserves full marks even if the answer is much shorter, uses different wording, or omits minor details. Reduce the mark only for wrong statements or for missing MAIN ideas.",
        {"A+": "states all the main ideas correctly (full marks), even if brief or paraphrased", "A": "states all main ideas but with a small inaccuracy or one minor gap", "B": "misses one main idea or has a noticeable inaccuracy", "C": "states only about half of the main ideas", "D": "states little of the main content", "F": "wrong, irrelevant, or contradicts the reference"}),
 "v3": ("Decide the mark for this answer using the reference answer as the mark scheme. Count how much of the reference content is present and correct.",
        {"A+": "100% of the reference content is present and correct", "A": "about 85-95%", "B": "about 65-80%", "C": "about 45-60%", "D": "about 20-40%", "F": "under 15%, or wrong"}),
}
def features(q, ref, ans, variants=("v1", "v2", "v3"), checklist=None):
    """Return averaged probability vector over grades (len 6)."""
    acc = {g: 0.0 for g in GR}
    for v in variants:
        ins, crit = VARIANTS[v]
        extra = ("Checklist of required points:\n" + "\n".join(f"- {p}" for p in checklist) + "\n") if checklist else ""
        r = decide(MODEL, f"Question: {q}\nModel answer (reference): {ref}\n{extra}Student answer: {ans}", {"g": {"type": "choice", "instructions": ins, "criteria": crit}})["g"]["probabilities"]
        for g in GR: acc[g] += r.get(g, 0) / len(variants)
    return [acc[g] for g in GR]
def features_batched(q, ref, ans, variants=("v1", "v2", "v3"), checklist=None):
    """Same as features() but all prompt variants go in ONE decisions request (1 call instead of len(variants))."""
    extra = ("Checklist of required points:\n" + "\n".join(f"- {p}" for p in checklist) + "\n") if checklist else ""
    qs = {v: {"type": "choice", "instructions": VARIANTS[v][0], "criteria": VARIANTS[v][1]} for v in variants}
    r = decide(MODEL, f"Question: {q}\nModel answer (reference): {ref}\n{extra}Student answer: {ans}", qs)
    return [sum(r[v]["probabilities"].get(g, 0) for v in variants) / len(variants) for g in GR]
def expected(f): return sum(GV[g] * p for g, p in zip(GR, f))
# ---- calibrators (pure python) ----
def fit_linear(x, y):
    mx, my = st.mean(x), st.mean(y); v = sum((a-mx)**2 for a in x); b = sum((a-mx)*(c-my) for a, c in zip(x, y)) / v if v else 0
    return (my - b*mx, b)
def solve(M, v):
    n = len(v); M = [r[:] + [v[i]] for i, r in enumerate(M)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i])); M[i], M[p] = M[p], M[i]
        for r in range(n):
            if r != i:
                f = M[r][i] / M[i][i]; M[r] = [a - f*b for a, b in zip(M[r], M[i])]
    return [M[i][n] / M[i][i] for i in range(n)]
def fit_ridge(X, y, lam=1.0):
    d = len(X[0]) + 1; Xb = [[1.0] + r for r in X]
    A = [[sum(Xb[k][i]*Xb[k][j] for k in range(len(Xb))) + (lam if i == j and i > 0 else 0) for j in range(d)] for i in range(d)]
    b = [sum(Xb[k][i]*y[k] for k in range(len(Xb))) for i in range(d)]
    return solve(A, b)
def clip(x): return min(1.0, max(0.0, x))
def cv(feats, gold, qi, kind):
    out = [0.0]*len(gold)
    for q in sorted(set(qi)):
        trn = [i for i in range(len(gold)) if qi[i] != q]; tst = [i for i in range(len(gold)) if qi[i] == q]
        if kind == "none":
            for i in tst: out[i] = expected(feats[i])
        elif kind == "linear":
            a, b = fit_linear([expected(feats[i]) for i in trn], [gold[i] for i in trn])
            for i in tst: out[i] = clip(a + b*expected(feats[i]))
        else:
            w = fit_ridge([feats[i] for i in trn], [gold[i] for i in trn], lam=float(kind.split(":")[1]))
            for i in tst: out[i] = clip(w[0] + sum(a*b for a, b in zip(w[1:], feats[i])))
    return out

# ================= public API =================
def pav(xs, ys):
    """isotonic regression -> list of knots [(x, y)] (monotone non-decreasing)"""
    S = []
    for x, y in sorted(zip(xs, ys)):
        S.append([y, 1, x, x])
        while len(S) > 1 and S[-2][0]/S[-2][1] > S[-1][0]/S[-1][1]:
            b = S.pop(); a = S.pop(); S.append([a[0]+b[0], a[1]+b[1], a[2], b[3]])
    return [((s[2]+s[3])/2, s[0]/s[1]) for s in S]
def interp(knots, x):
    if x <= knots[0][0]: return knots[0][1]
    if x >= knots[-1][0]: return knots[-1][1]
    for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
        if x0 <= x <= x1: return y1 if x1 == x0 else y0 + (y1-y0)*(x-x0)/(x1-x0)
_DEF = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_calibration.json")))
CUT_SHORT = [.87, .80, .70, .55, .40]    # direct mode (short answers): calibrated scores rarely reach .93, so A+ starts lower (A+ F1 on real data: AR .35->.45, EN .72->.78)
CUT_ESSAY = [.93, .83, .70, .55, .40]    # anchored mode (essays): scores are not compressed
def letter(s, cut=CUT_ESSAY): return next((l for l, t in zip(["A+", "A", "B", "C", "D"], cut) if s >= t), "F")
class Engine:
    """grade(question, reference, answer) -> {'score': 0..1, 'letter': 'A+'..'F', 'probs': {...}}.
    fit([(question, reference, answer, teacher_score_0_1), ...]) with >=10 teacher-graded answers calibrates per course
    (isotonic when n>=30, average of isotonic and linear when 10<=n<30)."""
    def __init__(self, cal=None, checklist=None, lang=None):
        # lang='ar' uses the calibration fit on 2102 Arabic short answers (MAE 13.9 -> 13.0%); lang='en' the English one; None = pooled default
        self.cal = cal or _DEF; self.checklist = checklist
        if cal is None and lang in _DEF.get("by_lang", {}):
            self.cal = dict(_DEF); self.cal["knots"] = _DEF["by_lang"][lang]["knots"]; self.cal["mode"] = "iso"
    def raw(self, q, ref, ans, checklist=None):
        return features_batched(q, ref, ans, checklist=checklist or self.checklist)
    def _map(self, e):
        c = self.cal; iso = interp([tuple(k) for k in c["knots"]], e)
        return iso if c.get("mode") == "iso" else (iso + clip(c["intercept"] + c["slope"] * e)) / 2
    def fit(self, samples):
        if len(samples) < 10: raise ValueError("need >= 10 teacher-graded samples")
        E = [expected(self.raw(q, r, a)) for q, r, a, _ in samples]; G = [s for *_, s in samples]
        a, b = fit_linear(E, G)
        self.cal = {"knots": pav(E, G), "intercept": a, "slope": b, "mode": "iso" if len(samples) >= 30 else "avg"}; return self
    @staticmethod
    def uncertainty(f, s):
        ent = -sum(p * math.log(p + 1e-9) for p in f)
        return ent / 1.2 + (1 - abs(s - .5) * 2)          # higher = less sure (spread over grades and/or score near the middle)
    def grade(self, q, ref, ans, checklist=None, coverage=None):
        """needs_review is True for the least-certain answers. Default threshold auto-grades ~60% of answers
        (on real data: avg error 7% on those vs 12% overall); pass a different threshold via cal['review_threshold']."""
        f = self.raw(q, ref, ans, checklist); s = clip(self._map(expected(f))); u = self.uncertainty(f, s)
        thr = self.cal.get("review_threshold", 1.0)
        return {"score": round(s, 3), "letter": letter(s, CUT_SHORT), "needs_review": u > thr, "uncertainty": round(u, 3), "probs": dict(zip(GR, [round(x, 3) for x in f]))}

# ================= anchored mode (best for essays) =================
class AnchoredEngine:
    """Teacher grades ~5 anchor answers per question (spanning low..high). New answers are compared with each anchor by the
    decision model ('better/similar/worse'); the score is the anchors' mean of (anchor_score + delta*2*(P(better)-P(worse))).
    On real essays (AR-AES) MAE 11.9% = human-human level (12.2%), vs 15.7% for direct grading."""
    def __init__(self, anchors, k=5, delta=0.4):
        # anchors: list of (answer_text, teacher_score_0_1)
        s = sorted(anchors, key=lambda x: x[1]); k = min(k, len(s)); self.delta = delta
        self.anchors = [s[round(t * (len(s) - 1) / (k - 1))] for t in range(k)] if k > 1 else s[:1]
    def grade(self, q, ref, ans, criteria=None):
        """ONE decisions request: all anchors + a better/similar/worse question per anchor (MAE 12.3% vs 11.9% with separate requests, 5x cheaper)."""
        crit = ("Grading criteria:\n" + "\n".join(f"- {c}" for c in criteria) + "\n") if criteria else ""
        anchors = "\n\n".join(f"ANCHOR {n+1} (teacher gave {round(sc*100)}%):\n{t}" for n, (t, sc) in enumerate(self.anchors))
        C = {"better": "NEW covers clearly more of the required content than this anchor", "similar": "NEW covers about the same required content as this anchor", "worse": "NEW covers clearly less of the required content than this anchor"}
        qs = {f"a{n+1}": {"type": "choice", "instructions": f"Using the grading criteria and the typical answer, how does the NEW answer compare with ANCHOR {n+1}?", "criteria": C} for n in range(len(self.anchors))}
        r = decide(MODEL, f"Question: {q}\nTypical answer: {ref}\n{crit}\n{anchors}\n\nNEW answer:\n{ans}", qs)
        ests = [clip(sc + self.delta * 2 * (r[f"a{n+1}"]["probabilities"].get("better", 0) - r[f"a{n+1}"]["probabilities"].get("worse", 0))) for n, (_, sc) in enumerate(self.anchors)]
        s = clip(st.mean(ests)); spread = st.pstdev(ests)
        return {"score": round(s, 3), "letter": letter(s), "spread": round(spread, 3), "needs_review": spread > 0.17}


class EssayEngine:
    """Best mode for long answers: mean of (a) direct calibrated grading and (b) anchored comparison with ~5 teacher-graded anchors.
    Hold-out (180 unseen essays, frozen settings): MAE 11.6%; vs a single teacher 13.7-13.9% while two teachers differ by 14.2%.
    (alone: direct 13.3%, anchored 13.6% -- their errors are complementary.)"""
    def __init__(self, anchors, direct=None, k=5, delta=0.4):
        self.direct = direct or Engine(); self.anch = AnchoredEngine(anchors, k, delta)
    def grade(self, q, ref, ans, criteria=None):
        d = self.direct.grade(q, ref, ans)["score"]; a = self.anch.grade(q, ref, ans, criteria)
        s = clip((d + a["score"]) / 2)
        return {"score": round(s, 3), "letter": letter(s, CUT_ESSAY), "direct": d, "anchored": a["score"], "disagreement": round(abs(d - a["score"]), 3)}


class ShortAnchoredEngine:
    """Short answers with ~5 teacher-graded answers for THIS question: per-question bias correction.
    offset = mean(teacher_score - engine_score) over the anchors; grade = clip(engine_score + 0.5*offset).
    Large-scale test (2102 real Arabic short answers, 46 questions, 5 anchors/question, question-level bootstrap):
    MAE 13.9% -> 12.8% (paired diff -1.1 [-1.5,-0.6]); human-human 11.3%. No extra requests per answer (5 one-off requests per question)."""
    def __init__(self, anchors, engine=None, weight=0.5):
        self.engine = engine or Engine(); self.w = weight; self.anchors = anchors
        self._off = None
    def _offset(self, q, ref):
        if self._off is None:
            errs = [sc - self.engine.grade(q, ref, t)["score"] for t, sc in self.anchors]; self._off = st.mean(errs)
        return self._off
    def grade(self, q, ref, ans, checklist=None):
        r = self.engine.grade(q, ref, ans, checklist); s = clip(r["score"] + self.w * self._offset(q, ref))
        r.update({"score": round(s, 3), "letter": letter(s, CUT_SHORT), "question_offset": round(self._off, 3)}); return r
