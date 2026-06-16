---
name: precision-review-search
description: >-
  Precision search and screening pipeline for systematic reviews in
  chemistry/materials — when broad database searches (OpenAlex/PubMed/CrossRef)
  return too much noise. Instead of relying on a single pipeline tool (PISMA),
  this skill: (1) decomposes the topic into 10-15 precise sub-topic queries,
  (2) searches OpenAlex + PubMed directly per sub-topic, (3) deduplicates,
  (4) screens with a two-pass keyword+heuristic filter, (5) manually adds
  foundational/classic papers that automated searches miss,
  (6) compiles a final corpus ready for writing.
  Produces 600-1500 papers instead of PISMA's typical ~100.
author: Amaranth (via wiki-for-amaranth.pages.dev)
license: MIT
metadata:
  hermes:
    tags: [search, review, papers, screening, openalex, pubmed]
    source: "https://wiki-for-amaranth.pages.dev/skill-share/review-writing/"
---

# Precision Review Search Pipeline

## When to use this instead of PISMA

For broad topics where:
- The search query is generic ("gold nanoparticle synthesis")
- Most papers found are about *applications* not *mechanisms*
- You need papers from 1951-2026 (PISMA defaults to ~5 year range)
- The per-source limit (500) is too small

→ Use this precision search + screening pipeline instead.

## Pipeline Overview

```
Step 1 ─ DECOMPOSE       Break topic into 10-15 precise sub-topic queries
Step 2 ─ SEARCH          For each sub-topic: OpenAlex + PubMed, 1951-2026
Step 3 ─ DEDUP           Cross-source deduplication by DOI + normalized title
Step 4 ─ SCREEN          Two-pass: hard keyword exclusion → heuristic scoring
Step 5 ─ CURATE          Manual addition of classic/foundational papers
Step 6 ─ COMPILE         Final corpus
Step 7 ─ CLASSIFY        Assign papers to thematic section buckets
```

## Corpus Sizing by Review Type

| Review Type | Corpus Size | Target Citations |
|-------------|:-----------:|:----------------:|
| Mini Review | 50-200 | 50-200 |
| Big Review | 600-1,500 | 250-400 |
| Mega Review | 1,500-3,000+ | 400-800+ |

## Step 1 ─ Decompose the Topic

Do NOT use a single broad query. Break the topic into 10-15 precise sub-topics.

Example for "gold nanomaterial synthesis":
| # | Sub-topic | Query Focus |
|---|-----------|-------------|
| 1 | Turkevich method | citrate reduction, nucleation mechanism |
| 2 | Brust-Schiffrin | two-phase synthesis, thiol stabilization |
| 3 | Seed-mediated growth | nanorod/anisotropic, Murphy/El-Sayed |
| 4 | Nucleation kinetics | classical vs non-classical |
| 5 | Anisotropic growth | facet-dependent, capping agent |

## Step 4 ─ Screen (Two-Pass)

### Pass 1: Hard Title Exclusion
Papers with application keywords in the title are immediately excluded: cancer, therapy, drug delivery, biosensor, SERS, antibacterial, cytotoxicity, in vivo, clinical, vaccine.

### Pass 2: Heuristic Scoring
Score = `title_score + abstract_score + citation_bonus + recency_bonus`

| Range | Label | Action |
|-------|-------|--------|
| ≥ 40 | include | Core corpus |
| 10-39 | maybe | Review manually |
| < 10 | exclude | Discard |

## Related Skills

- `review-chem-bio-pipeline` — Full pipeline
- `review-chem-bio-writing` — Writing conventions

## License

MIT License. From Amaranth's wiki-for-Amaranth wiki.
