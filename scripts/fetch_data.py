"""Fetch the public datasets used in the experiments into ./data (git-ignored). You run this; nothing is redistributed by this repo.

 * AR-ASAG  (Arabic short answers; Ouahrani & Bennouar, LREC 2020; Mendeley Data DOI 10.17632/dj95jh332j.1)
            -> the file with questions, model answers, student answers and both teachers' marks (~540 KB)
 * SciEntsBank (English short answers, SemEval-2013 Task 7; Hugging Face 'nkazi/SciEntsBank', CC-BY-4.0) -> first N test rows via the datasets-server API
 * AR-AES (Arabic essays; Ghazawi & Simpson, arXiv:2407.11212): the data link is given in the paper (OSF); download it manually.

CHECK THE LICENCES/TERMS OF EACH DATASET before using or sharing the data.
Usage:  python scripts/fetch_data.py [--en-rows 200]
"""
import argparse
import json
import os
import urllib.request

ARASAG_URL = "https://data.mendeley.com/public-files/datasets/dj95jh332j/files/770ef112-8ea6-4ba2-aee0-8a39cb4857c4/file_downloaded"
HF_ROWS = "https://datasets-server.huggingface.co/rows?dataset=nkazi/SciEntsBank&config=default&split=test_ua&offset={off}&length={n}"


def get(url, timeout=90):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--en-rows", type=int, default=200); a = ap.parse_args()
    os.makedirs("data", exist_ok=True)
    print("AR-ASAG ...", end=" ", flush=True)
    open("data/ar_asag_full.txt", "wb").write(get(ARASAG_URL)); print("ok -> data/ar_asag_full.txt")
    rows, off = [], 0
    while len(rows) < a.en_rows:
        n = min(100, a.en_rows - len(rows))
        rows += [r["row"] for r in json.loads(get(HF_ROWS.format(off=off, n=n)))["rows"]]; off += n
    json.dump(rows, open("data/scientsbank_sample.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"SciEntsBank: {len(rows)} rows -> data/scientsbank_sample.json")
    print("AR-AES: download manually from the link in https://arxiv.org/abs/2407.11212 (OSF) and put it in data/.")


if __name__ == "__main__":
    main()
