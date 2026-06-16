#!/usr/bin/env python3
"""Precision search for gold nanoparticle synthesis & mechanism papers.

Searches OpenAlex + PubMed for each sub-topic query, collects metadata,
deduplicates by DOI, saves to JSON for review.
"""
import json, time, sys, re
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError

QUERIES = [
    ("turkevich_citrate",
     'title_and_abstract.search:"Turkevich method" AND (gold OR colloidal gold OR citrate reduction)',
     "Turkevich method gold citrate", 1951, 2026),
    ("brust_schiffrin",
     'title_and_abstract.search:"Brust-Schiffrin" AND gold',
     "Brust Schiffrin gold nanoparticle", 1994, 2026),
]


def openalex_search(query, per_page=50, max_results=200):
    results = []
    cursor = "*"
    base = "https://api.openalex.org/works"
    params = f"?filter={quote(query)}&per_page={per_page}&sort=relevance_score:desc&cursor="
    attempt = 0
    while cursor and len(results) < max_results and attempt < 20:
        url = f"{base}{params}{cursor}"
        try:
            req = Request(url, headers={"User-Agent": "ReviewBot/1.0"})
            resp = urlopen(req, timeout=30)
            data = json.loads(resp.read())
            works = data.get("results", [])
            if not works:
                break
            for w in works:
                results.append({
                    "id": w.get("id"),
                    "title": w.get("title", ""),
                    "abstract": w.get("abstract_inverted_index", ""),
                    "year": w.get("publication_year"),
                    "doi": (w.get("doi") or "").lower().strip(),
                    "source": "openalex",
                    "query_label": query[:60],
                    "cited_by_count": w.get("cited_by_count", 0),
                    "authors": [a.get("author", {}).get("display_name", "")
                                for a in w.get("authorships", [])[:5]],
                    "venue": (w.get("primary_location") or {}).get("source", {}).get("display_name", ""),
                })
            cursor = data.get("meta", {}).get("next_cursor")
            attempt += 1
            time.sleep(0.2)
        except HTTPError as e:
            if e.code == 429:
                time.sleep(2)
                continue
            break
        except Exception as e:
            print(f"  OpenAlex error: {e}", file=sys.stderr)
            break
    return results


def pubmed_search(query, max_results=100):
    results = []
    esearch_url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term={quote(query)}&retmax={max_results}&retmode=json&sort=relevance"
    )
    try:
        req = Request(esearch_url, headers={"User-Agent": "ReviewBot/1.0"})
        resp = urlopen(req, timeout=30)
        search_data = json.loads(resp.read())
    except Exception as e:
        print(f"  PubMed search error: {e}", file=sys.stderr)
        return results
    ids = search_data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return results
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        efetch_url = (f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                      f"?db=pubmed&id={','.join(batch)}&retmode=xml&rettype=abstract")
        try:
            req = Request(efetch_url, headers={"User-Agent": "ReviewBot/1.0"})
            resp = urlopen(req, timeout=30)
            xml = resp.read().decode("utf-8")
            articles = xml.split("<PubmedArticle>")[1:]
            for art in articles:
                title = _extract_xml(art, "ArticleTitle")
                abstract = _extract_xml(art, "AbstractText")
                year = _extract_xml(art, "PubDate")
                year_num = None
                if year:
                    m = re.search(r"(\d{4})", year)
                    if m:
                        year_num = int(m.group(1))
                results.append({
                    "id": _extract_xml(art, "PMID"),
                    "title": title.strip() if title else "",
                    "abstract": abstract.strip() if abstract else "",
                    "year": year_num,
                    "doi": "",
                    "source": "pubmed",
                    "query_label": query[:60],
                    "cited_by_count": 0,
                    "authors": [],
                    "venue": _extract_xml(art, "Journal") or "",
                })
            time.sleep(0.4)
        except Exception as e:
            print(f"  PubMed fetch error: {e}", file=sys.stderr)
            time.sleep(1)
    return results


def _extract_xml(text, tag):
    parts = text.split(f"<{tag}>")
    if len(parts) < 2:
        return ""
    parts2 = parts[1].split(f"</{tag}>")
    return parts2[0].strip() if len(parts2) > 1 else ""


def deduplicate(papers):
    seen_dois = set()
    seen_titles = set()
    unique = []
    for p in papers:
        doi = p.get("doi", "").strip().lower().rstrip("/")
        if doi and doi in seen_dois:
            continue
        title = p.get("title", "").strip().lower()
        title_simple = re.sub(r"[^a-z0-9]", "", title)[:80]
        if title_simple and title_simple in seen_titles:
            continue
        if doi:
            seen_dois.add(doi)
        if title_simple:
            seen_titles.add(title_simple)
        unique.append(p)
    return unique


if __name__ == "__main__":
    import os
    OUTPUT = "/opt/data/reviews/gold-nanomaterials-review/data/all_papers.json"
    os.makedirs(os.path.dirname(OUTPUT) or ".", exist_ok=True)
    all_papers = []
    print(f"Searching {len(QUERIES)} sub-topics over OpenAlex + PubMed...")
    for label, oa_query, pm_query, y_start, y_end in QUERIES[:]:  # Limit for template
        print(f"[{label}] Searching...")
        oa_results = openalex_search(oa_query)
        all_papers.extend(oa_results)
        pm_results = pubmed_search(pm_query)
        all_papers.extend(pm_results)
        time.sleep(0.5)
    print(f"Total before dedup: {len(all_papers)}")
    all_papers = deduplicate(all_papers)
    print(f"Total after dedup: {len(all_papers)}")
    with open(OUTPUT, "w") as f:
        json.dump(all_papers, f, indent=2, ensure_ascii=False)
    print(f"Saved to {OUTPUT}")
