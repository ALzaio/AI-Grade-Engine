"""Minimal client for OpenRouter's *decisions* endpoint (/api/alpha/decisions) + a tiny thread-pool helper.

Configuration (environment variables):
  OPENROUTER_API_KEY        your key (required)  -- or OPENROUTER_API_KEY_FILE=/path/to/file containing it
  DECIDER_GRADER_CACHE      directory for the on-disk response cache (default ~/.cache/decider_grader); set to "0" to disable
  ALLOW_PAID=1              allow non-":free" models (blocked by default, see _guard_paid)
"""
import json, hashlib, os, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
_lock = threading.Lock()


def _api_key():
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k and os.environ.get("OPENROUTER_API_KEY_FILE"):
        k = open(os.environ["OPENROUTER_API_KEY_FILE"], encoding="utf-8").read().strip()
    if not k:
        raise RuntimeError("Set OPENROUTER_API_KEY (or OPENROUTER_API_KEY_FILE).")
    return k.strip()


def _cache_dir():
    d = os.environ.get("DECIDER_GRADER_CACHE", os.path.join(os.path.expanduser("~"), ".cache", "decider_grader"))
    if d == "0":
        return None
    os.makedirs(d, exist_ok=True)
    return d


def _guard_paid(model):
    """Only ':free' models are allowed unless ALLOW_PAID=1 (paid reasoning models can bill thousands of hidden tokens per call)."""
    if model and not str(model).endswith(":free") and os.environ.get("ALLOW_PAID") != "1":
        raise RuntimeError(f"BLOCKED: paid model {model!r}. Set ALLOW_PAID=1 only if you accept the cost.")


def _post(body, timeout=120, retries=8):
    _guard_paid(body.get("model"))
    data = json.dumps(body).encode()
    last = ""
    for i in range(retries):
        req = urllib.request.Request(ENDPOINT, data, {"Authorization": "Bearer " + _api_key(), "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (429, 500, 502, 503, 504, 408):
                last = f"HTTP {e.code} {msg}"; time.sleep(3 * (i + 1)); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        except Exception as e:  # network hiccup
            last = repr(e); time.sleep(2 * (i + 1))
    raise RuntimeError("retries exhausted: " + last)


def decide(model, state, questions, nocache_tag=None):
    """Call the decisions endpoint. `questions` = {name: {"type": "choice", "instructions": str, "criteria": {option: description}}}.
    Returns the "answers" dict (each answer has .probabilities). Responses are cached on disk (keyed by the full request)."""
    body = {"model": model, "state": state, "questions": questions}
    cdir = _cache_dir()
    if cdir:
        key = hashlib.sha1(json.dumps({**body, "_t": nocache_tag}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        path = os.path.join(cdir, key + ".json")
        if os.path.exists(path):
            try:
                return json.load(open(path, encoding="utf-8"))["answers"]
            except Exception:
                pass
    out = _post(body)
    if cdir:
        tmp = path + "." + str(threading.get_ident()) + ".tmp"
        with _lock:
            json.dump(out, open(tmp, "w", encoding="utf-8"), ensure_ascii=False); os.replace(tmp, path)
    return out["answers"]


def pmap(fn, items, workers=6):
    """Parallel map (threads). Keep workers modest to stay inside the free-tier rate limits."""
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(fn, items))
