#!/usr/bin/env python3
"""Two-pass screening: hard keyword exclusion + heuristic relevance scoring."""
import json, re, math

EXCLUDE_TITLE_TERMS = [
    "cancer", "tumor", "therapy", "drug delivery", "biosensor", "SERS",
    "photothermal therapy", "antibacterial", "cytotoxicity", "in vivo",
    "clinical", "vaccine", "gene delivery", "catalysis", "sensor",
    "nanozyme", "food safety", "drug carrier",
    "silver", "palladium", "platinum", "iron oxide", "quantum dot",
    "TiO2", "ZnO", "graphene oxide", "carbon nanotube",
]

INCLUDE_TITLE_TERMS = [
    "synthesis", "growth mechanism", "seed-mediated", "Turkevich", "Brust",
    "citrate reduction", "nucleation", "shape control",
    "anisotropic", "nanorod", "nanocrystal", "colloidal gold",
    "LSPR", "surface plasmon", "kinetic", "thermodynamic",
    "monodisperse", "in situ", "TEM", "SAXS",
]

EXCLUDE_ABSTRACT_KEYWORDS = [
    "drug delivery", "cancer therapy", "photothermal therapy",
    "biosensor", "SERS substrate", "antibacterial activity",
    "cytotoxicity", "in vivo study", "clinical trial",
]


def score_title(title):
    t = title.lower()
    for term in EXCLUDE_TITLE_TERMS:
        if term.lower() in t:
            return -100.0
    score = 0.0
    if "turkevich" in t: score += 80
    if "brust" in t and "schiffrin" in t: score += 75
    if "seed-mediated" in t: score += 60
    if "growth mechanism" in t: score += 50
    if "nucleation" in t: score += 35
    if "anisotropic" in t: score += 30
    return score


def score_abstract(abstract):
    if not abstract or len(abstract) < 10:
        return -10.0
    a = abstract.lower()
    score = 0.0
    for term in EXCLUDE_ABSTRACT_KEYWORDS:
        if term in a: score -= 20
    synthesis_signals = ["synthesis", "nucleation", "growth mechanism",
                         "seed-mediated", "citrate reduction",
                         "in situ tem", "kinetic control"]
    for term in synthesis_signals:
        if term in a: score += 5
    if "gold" in a: score += 3
    return min(score, 40.0)


def main():
    import sys, os
    INPUT = sys.argv[1] if len(sys.argv) > 1 else "/opt/data/reviews/gold-nanomaterials-review/data/all_papers.json"
    OUTPUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "/opt/data/reviews/gold-nanomaterials-review/screening"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(INPUT) as f:
        papers = json.load(f)

    included, maybes, excluded = [], [], []
    for p in papers:
        title = p.get("title", "") or ""
        abstract = p.get("abstract", "") or ""
        citation = p.get("cited_by_count", 0) or 0
        year = p.get("year") or 0

        t_score = score_title(title)
        if t_score < -50:
            excluded.append({**p, "screen_score": t_score, "screen_label": "exclude"})
            continue

        a_score = score_abstract(abstract)
        cit_bonus = min(10, math.log10(citation + 1) * 3) if citation > 0 else 0

        if year >= 2020: recency = 5
        elif year >= 2015: recency = 3
        elif year >= 2010: recency = 2
        elif year >= 2000: recency = 1
        else: recency = 0

        total = t_score + a_score + cit_bonus + recency
        entry = {**p, "screen_score": round(total, 1), "screen_label": ""}

        if total >= 40:
            entry["screen_label"] = "include"
            included.append(entry)
        elif total >= 10:
            entry["screen_label"] = "maybe"
            maybes.append(entry)
        else:
            entry["screen_label"] = "exclude"
            excluded.append(entry)

    for name, lst in [("included", included), ("maybes", maybes), ("excluded", excluded)]:
        path = f"{OUTPUT_DIR}/{name}_papers.json"
        lst.sort(key=lambda x: -x["screen_score"])
        with open(path, "w") as f:
            json.dump(lst, f, indent=2, ensure_ascii=False)

    print(f"Included: {len(included)}, Maybes: {len(maybes)}, Excluded: {len(excluded)}")


if __name__ == "__main__":
    main()
