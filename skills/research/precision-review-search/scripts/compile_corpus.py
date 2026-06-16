#!/usr/bin/env python3
"""Compile final corpus: merge included + top maybes + classics."""
import json, os, sys

CLASSICS = [
    {"title": "Experimental relations of gold (and other metals) to light",
     "year": 1857, "authors": ["Faraday M"], "doi": "", "source": "classic",
     "screen_score": 100, "screen_label": "classic"},
    {"title": "A study of the nucleation and growth processes in the synthesis of colloidal gold",
     "year": 1951, "authors": ["Turkevich J", "Stevenson PC", "Hillier J"],
     "doi": "10.1039/df9511100055", "source": "classic",
     "screen_score": 100, "screen_label": "classic"},
    {"title": "Controlled nucleation for the regulation of the particle size in monodisperse gold suspensions",
     "year": 1973, "authors": ["Frens G"],
     "doi": "10.1038/physci241020a0", "source": "classic",
     "screen_score": 100, "screen_label": "classic"},
    {"title": "Synthesis of thiol-derivatised gold nanoparticles in a two-phase liquid-liquid system",
     "year": 1994, "authors": ["Brust M", "Walker M", "Bethell D", "Schiffrin DJ", "Whyman R"],
     "doi": "10.1039/c39940000801", "source": "classic",
     "screen_score": 100, "screen_label": "classic"},
]


def main():
    import sys
    included_path = sys.argv[1] if len(sys.argv) > 1 else \
        "/opt/data/reviews/gold-nanomaterials-review/screening/included_papers.json"
    maybes_path = sys.argv[2] if len(sys.argv) > 2 else \
        "/opt/data/reviews/gold-nanomaterials-review/screening/maybes_papers.json"
    output_path = sys.argv[3] if len(sys.argv) > 3 else \
        "/opt/data/reviews/gold-nanomaterials-review/data/final_corpus.json"

    included = json.load(open(included_path)) if os.path.exists(included_path) else []
    maybes = json.load(open(maybes_path)) if os.path.exists(maybes_path) else []

    # Take top maybes
    maybes.sort(key=lambda x: -x.get("screen_score", 0))
    top_maybes = [p for p in maybes if p.get("screen_score", 0) >= 20]

    # Deduplicate classics against existing
    seen_dois = set()
    for p in included + top_maybes:
        doi = (p.get("doi") or "").strip().lower()
        if doi:
            seen_dois.add(doi)

    deduped_classics = [c for c in CLASSICS if not c.get("doi") or c["doi"].lower() not in seen_dois]

    corpus = included + top_maybes + deduped_classics
    corpus.sort(key=lambda x: -(x.get("year") or 0))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)

    print(f"Final corpus: {len(corpus)} papers")
    print(f"  Included: {len(included)}, Top maybes: {len(top_maybes)}, Classics: {len(deduped_classics)}")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
