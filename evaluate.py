"""Measure how accurate the skill extraction is.
 
Usage:
  python evaluate.py                    keyword matching only
  python evaluate.py semantic           meaning-based only
  python evaluate.py hybrid             keyword + semantic
  python evaluate.py all                all three, as a table for your README
  python evaluate.py hybrid --t=0.70    change the semantic threshold
  add --with-soft to also score soft skills (Communication, Teamwork, ...)
 
test_data.json is a list of items like:
  {"job_text": "full job description...", "true_skills": ["Python", "SQL"]}
true_skills = the skills YOU read in that job description.
"""
import json
import sys
from collections import Counter
 
from matcher import SKILLS, SOFT_SKILLS, find_skills
 
try:
    sys.stdout.reconfigure(encoding="utf-8")  # so Arabic prints correctly
except Exception:
    pass
 
CANONICAL = {name.lower(): name for name in SKILLS}
 
 
def normalize(names):
    return {CANONICAL.get(n.strip().lower(), n.strip()) for n in names}
 
 
def get_extractor(mode):
    if mode == "keyword":
        return find_skills
    # Imported only when needed, because loading the model takes a moment.
    import semantic_matcher
 
    if mode == "semantic":
        return semantic_matcher.find_semantic_skills
    if mode == "hybrid":
        return semantic_matcher.find_skills_hybrid
    raise ValueError(f"Unknown mode: {mode}")
 
 
def score(data, extractor, include_soft=False, verbose=True):
    tp = fp = fn = 0
    missed, wrong, not_in_dictionary = Counter(), Counter(), Counter()
 
    for i, item in enumerate(data, 1):
        truth = normalize(item["true_skills"])
        predicted = set(extractor(item["job_text"]))
 
        if not include_soft:
            truth -= SOFT_SKILLS
            predicted -= SOFT_SKILLS
 
        false_neg = truth - predicted
        false_pos = predicted - truth
 
        tp += len(truth & predicted)
        fn += len(false_neg)
        fp += len(false_pos)
 
        for skill in false_neg:
            missed[skill] += 1
            if skill not in SKILLS:
                not_in_dictionary[skill] += 1
        for skill in false_pos:
            wrong[skill] += 1
 
        if verbose and (false_neg or false_pos):
            print(
                f"Job {i}: missed {sorted(false_neg)} | "
                f"wrongly found {sorted(false_pos)}"
            )
 
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
 
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "missed": missed,
        "wrong": wrong,
        "not_in_dictionary": not_in_dictionary,
    }
 
 
def print_details(result):
    if result["missed"]:
        print("\nMost missed skills (add or fix aliases):")
        for skill, count in result["missed"].most_common(10):
            print(f"  {skill}: {count}")
    if result["wrong"]:
        print("\nMost wrongly found skills (remove or tighten the alias):")
        for skill, count in result["wrong"].most_common(10):
            print(f"  {skill}: {count}")
    if result["not_in_dictionary"]:
        print("\nNot in the dictionary yet (add them to SKILLS in matcher.py):")
        print("  " + ", ".join(sorted(result["not_in_dictionary"])))
 
 
def main():
    args = sys.argv[1:]
    include_soft = "--with-soft" in args
 
    for arg in args:
        if arg.startswith("--t="):
            import semantic_matcher
 
            semantic_matcher.THRESHOLD = float(arg[4:])
 
    modes = [a for a in args if a in ("keyword", "semantic", "hybrid", "all")]
    mode = modes[0] if modes else "keyword"
 
    with open("test_data.json", encoding="utf-8") as f:
        data = json.load(f)
 
    if not data:
        print("test_data.json is empty.")
        return
 
    if mode == "all":
        print(f"Job descriptions tested: {len(data)}\n")
        print("| Method | Precision | Recall | F1 |")
        print("|---|---|---|---|")
        for name in ("keyword", "semantic", "hybrid"):
            r = score(data, get_extractor(name), include_soft, verbose=False)
            print(
                f"| {name} | {r['precision']:.0%} | {r['recall']:.0%} | {r['f1']:.0%} |"
            )
        return
 
    result = score(data, get_extractor(mode), include_soft)
    print(f"\n=== Results ({mode}) ===")
    print(f"Job descriptions tested: {len(data)}")
    print(f"Precision: {result['precision']:.0%}  (of the skills found, how many were right)")
    print(f"Recall:    {result['recall']:.0%}  (of the real skills, how many were found)")
    print(f"F1 score:  {result['f1']:.0%}")
    print_details(result)
 
 
if __name__ == "__main__":
    main()
 
