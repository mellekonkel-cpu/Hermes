---
name: review-chem-bio-pipeline
description: >-
  End-to-end pipeline for producing critical reviews in chemistry and biology
  (Chinese or English). Covers BOTH fundamental physical/inorganic chemistry
  (nanomaterial synthesis, growth mechanisms, optical/thermal/
  electrical/magnetic properties) AND applied bioanalytical chemistry
  (biosensing, POCT, DNA nanotechnology, biomaterials).
  NOT a general-purpose review writer — this is a structured workflow that:
  (1) queries real academic databases directly (PubMed, Semantic Scholar,
  OpenAlex, CrossRef, bioRxiv, PubChem),
  (2) deduplicates and classifies results by theme,
  (3) builds an intellectual genealogy tracing the field's growth,
  (4) writes with Claim-Evidence-Limitation paragraph structure,
  (5) generates publication-quality figures with enforced style consistency
  via SciencePlots + matplotlib/seaborn templates.
  Reference user-writing-style for output conventions. Default output language
  is Chinese unless the user specifies English.
author: Amaranth (via wiki-for-amaranth.pages.dev)
license: MIT
metadata:
  hermes:
    tags: [review, chemistry, biology, academic-writing, pipeline]
    source: "https://wiki-for-amaranth.pages.dev/skill-share/review-writing/"
---

# Review Pipeline: Chemistry & Biology

## Phase 0 ─ Thesis Chapter 1 to Review Decomposition

### When to Use This Phase

Trigger: The user says "把我论文第一章拆成几篇综述" or equivalent. Their thesis Chapter 1 is a comprehensive literature review spanning multiple sub-topics, and they want to extract 2-3 independent review papers from it.

### Decomposition Workflow

```
Step 1 ─ Map thesis sections to separable review topics
  Scan the Chapter 1 table of contents and paragraph-level coverage.
  Identify natural thematic clusters that could stand alone as reviews.
  Each cluster must have:
    - A distinct core question (not just "review of X")
    - A non-overlapping reference set (or minimal overlap)
    - A different target journal / reader community

Step 2 ─ Define each review's core angle
  For each candidate review, answer:
    - What unsolved problem does this review address?
    - What is the argument/thesis (not just a summary)?
    - What is NOT covered (exclusion boundary)?
  Ensure the three reviews do not compete on angle —
    each should serve a different reader and a different journal.

Step 3 ─ Allocate references
  Split the thesis Chapter 1's reference list among the reviews.
  References that span multiple themes become supplementary citations
  in the review where they're most relevant; cross-link titles suffice
  in the other reviews.

Step 4 ─ Map to target journals
  For each review, determine:
    - Primary journal (ideal fit, high impact)
    - Secondary journal (good fit, more accessible)
    - Backup journal (broader scope, lower barrier)

Step 5 ─ Assess existing work
  Check if any candidate review already has a draft or outline
  (e.g., an earlier session produced a partial draft).
  If so, incorporate that work rather than restarting from scratch.
```

## Domain Scope Warning (READ FIRST)
> This skill covers BOTH fundamental physical/inorganic chemistry (synthesis, growth mechanisms, optical/thermal/electrical/magnetic properties of nanomaterials) AND applied bioanalytical chemistry (biosensing, POCT, DNA nanotechnology, drug delivery).
>
> **Critical pitfall:** Never assume the user's sub-domain based on their academic background. The same person may work on fundamental AuNP synthesis one month and DNAzyme biosensors the next. Always confirm scope during Phase 1 before proceeding.
>
> The skill defaults to NO applied/application framing unless the user explicitly confirms it. When in doubt, choose the fundamental track.

## Pipeline Overview

```
Phase 1 ─ ANALYZE         Analyze the topic, define scope, formulate argument thesis
Phase 2 ─ SEARCH          Query databases directly, collect raw records
Phase 3 ─ DEDUP           Cross-database deduplication + PRISMA tracking
Phase 4 ─ CLASSIFY        Categorize records into thematic buckets
Phase 5 ─ ORGANIZE        Build section outline from classified papers
Phase 6 ─ WRITE           Draft sections with C-E-L-T paragraph structure
Phase 7 ─ FIGURES         Generate consistent figures via SciencePlots
Phase 8 ─ VERIFY          Check citations, data consistency, language
```

## Related Skills

- `review-chem-bio-writing` — Writing conventions, citation format, de-AI cleanup
- `precision-review-search` — Focused precision search alternative to PISMA
- `paper-figure-mapper` — Figure identification and prompt generation

## License

MIT License. From Amaranth's wiki-for-Amaranth wiki.
