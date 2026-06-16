# Reference Formatting Guide (Battery Electrolytes Domain)

Based on the thesis of 武士淳 (Wu Shichun), Tianjin Polytechnic University.

## Format Template

```
[N] 姓全大写 名缩写, 姓全大写 名缩写. 文章标题首字母大写[J]. 期刊全名, 年, 卷(期): 页码.
```

Examples from the thesis:
```
[1] PALACÍN M R. Recent advances in rechargeable battery materials: a chemist's perspective[J]. Chemical Society Reviews, 2009, 38(9): 2565.
[2] DONG L, ZHONG S, YUAN B, et al. Electrolyte Engineering for High-Voltage Lithium Metal Batteries[J]. Research, 2022, 2022: 2022/9837586.
```

Rules:
1. Authors: ALL CAPS last name followed by initials, comma-separated
2. More than ~6 authors → "et al." after the 3rd-6th author
3. Title: first word capitalized, proper nouns capitalized
4. Journal suffix: [J] for journal articles
5. Year, Volume(Issue): Pages — use en-dash (–) for page ranges
6. Period at end
7. For article-number references (no traditional pages), use the article number as-is (e.g., "2100107" or "1804822")

## Reference Lookup Workflow (API-based)

When user provides references in abbreviated format (author, journal abbreviation, volume, year, pages — no title), use this workflow to look up the full metadata:

1. **Try Crossref API first** — works well for known DOIs and title searches:
   ```bash
   curl -s "https://api.crossref.org/works?query=<search terms>&rows=1"
   ```
   Returns JSON with title, authors, journal, year, volume, issue, pages, DOI.

2. **For DOI-based lookup**:
   ```bash
   curl -s "https://api.openalex.org/works?filter=doi:<doi>"
   ```
   Returns detailed metadata including citation count, authors with full names.

3. **When OpenAlex search fails** (returns irrelevant results), use Crossref search instead — its relevance engine is better for exact paper matching.

4. **Key parameters**:
   - Crossref: `?query=<keywords>&rows=<N>&sort=relevance` (default) or `&filter=from-pub-date:YYYY-01-01`
   - OpenAlex: `?search=<query>&filter=publication_year:YYYY-YYYY&sort=cited_by_count:desc&per_page=<N>`

5. **Pitfalls**:
   - OpenAlex keyword search is unreliable for multi-word scientific queries — it does coarse keyword matching, not semantic search. Prefer direct DOI lookup or Crossref.
   - Crossref returns `published-print.date-parts` for year; fall back to `created.date-parts` if missing.
   - Some papers use article numbers instead of page ranges (e.g., "2100107" or "1804822") — use them as-is.
   - For papers with >6 authors, shorten to first 3-6 + "et al." per thesis convention.

6. **Paper finding for schematic/figures**: When user needs papers containing specific schematic types (e.g., "Li metal battery working principle schematic" + "cathode failure mechanism schematic"), target comprehensive review papers in high-impact journals (IF > 5, published <5 years ago). Known high-quality candidates:
   - Li-rich cathode reviews: Chen H et al., ChemSusChem 2024 (10.1002/cssc.202401120)
   - Cathode degradation reviews: Jiang M et al., Adv. Energy Mater. 2021 (10.1002/aenm.202103005)
   - High-voltage electrolyte reviews: Fan X et al., Chem. Soc. Rev. 2021 (10.1039/d1cs00412j)
   - Li metal battery reviews: Dong L et al., Research 2022 (10.34133/research.9837586)
   - Interface engineering reviews: Zhai P et al., Adv. Energy Mater. 2020 (10.1002/aenm.202001257)

## Formatted Reference Examples

[1] DONG K, DONG X, JIANG Q. How renewable energy consumption lower global CO₂ emissions? Evidence from countries with different income levels[J]. The World Economy, 2020, 43(6): 1665–1698.

[2] GUO K, QI S, WANG H, et al. High-voltage electrolyte chemistry for lithium batteries[J]. Small Science, 2022, 2(5): 2100107.

[3] HAN J G, KIM K, LEE Y, et al. Scavenging materials to stabilize LiPF₆-containing carbonate-based electrolytes for Li-ion batteries[J]. Advanced Materials, 2019, 31(20): 1804822.

[4] KRAUSE C H, RÖRING P, RÖSER S, et al. Toward adequate control of internal interfaces utilizing nitrile-based electrolytes[J]. The Journal of Chemical Physics, 2020, 152(17): 174701.

[5] LI J, XING L, ZHANG R, et al. Tris(trimethylsilyl)borate as an electrolyte additive for improving interfacial stability of high voltage layered lithium-rich oxide cathode/carbonate-based electrolyte[J]. Journal of Power Sources, 2015, 285: 360–366.

[6] LI S, ZHAO D, WANG P, et al. Electrochemical effect and mechanism of adiponitrile additive for high-voltage electrolyte[J]. Electrochimica Acta, 2016, 222: 668–677.

[7] LIM S H, CHO W, KIM Y J, et al. Insight into the electrochemical behaviors of 5V-class high-voltage batteries composed of lithium-rich layered oxide with multifunctional additive[J]. Journal of Power Sources, 2016, 336: 465–474.

[8] YE C, TU W, YIN L, et al. Converting detrimental HF in electrolytes into a highly fluorinated interphase on cathodes[J]. Journal of Materials Chemistry A, 2018, 6(36): 17642–17652.

[9] GU S J, CUI Y Y, WEN K H, et al. 3-Cyano-5-fluorobenzenzboronic acid as an electrolyte additive for enhancing the cycling stability of Li₁.₂Mn₀.₅₄Ni₀.₁₃Co₀.₁₃O₂ cathode at high voltage[J]. Journal of Alloys and Compounds, 2020, 829: 154491.

[10] HUANG T, ZHENG X Z, PAN Y, et al. Stabilizing Li-rich layered oxide cathode interface by using silicon-based electrolyte additive[J]. Journal of Colloid and Interface Science, 2024, 662: 527–534.

[11] LIU X X, LI Y, LIU J D, et al. 570 Wh kg⁻¹-grade lithium metal pouch cell with 4.9 V highly Li⁺ conductive armor-like cathode electrolyte interphase via partially fluorinated electrolyte engineering[J]. Advanced Materials, 2024, 36(24): 2401505.
