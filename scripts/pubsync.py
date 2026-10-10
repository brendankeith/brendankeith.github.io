#!/usr/bin/env python3
"""Diff Brendan Keith's arXiv listing against _pages/publications.md.

Google Scholar has no API and blocks automated access, so arXiv (which Scholar
indexes within days) is the source of truth for new preprints. Publication
status comes from arXiv's journal_ref/DOI fields; anything else (Crossref,
Scholar alert emails) is checked by the weekly agent, not here.

Usage:  python3 scripts/pubsync.py [path/to/publications.md]
Prints a JSON report:
  new_preprints     arXiv records whose ID appears nowhere on the page
  now_published     entries still under "## Preprints" whose arXiv record
                    now carries a journal_ref or DOI
"""
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

AUTHOR_QUERY = 'au:"Brendan Keith"'
API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
# arXiv records that are intentionally not listed on the page.
IGNORE = {
    "1710.05223",  # DPG* Method -- listed under "Other" as a technical report
    "1909.04029",  # MethodsX paper -- listed with journal DOI only
}


def fetch_arxiv(max_results=100):
    q = urllib.parse.urlencode(
        {
            "search_query": AUTHOR_QUERY,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results,
        }
    )
    with urllib.request.urlopen(f"{API}?{q}", timeout=60) as r:
        root = ET.fromstring(r.read())
    out = []
    for e in root.findall("a:entry", NS):
        aid = re.sub(r"v\d+$", "", e.find("a:id", NS).text.split("/abs/")[-1])
        jr, doi = e.find("x:journal_ref", NS), e.find("x:doi", NS)
        out.append(
            {
                "id": aid,
                "title": " ".join(e.find("a:title", NS).text.split()),
                "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
                "category": e.find("x:primary_category", NS).get("term"),
                "published": e.find("a:published", NS).text[:10],
                "journal_ref": jr.text.strip() if jr is not None else None,
                "doi": doi.text.strip() if doi is not None else None,
            }
        )
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "_pages/publications.md"
    page = open(path, encoding="utf-8").read()
    preprints = page.split("## Preprints", 1)[1].split("\n## ", 1)[0]
    on_page = set(re.findall(r"(\d{4}\.\d{4,5})", page))
    in_preprints = set(re.findall(r"arxiv\.org/abs/(\d{4}\.\d{4,5})", preprints))

    records = fetch_arxiv()
    report = {
        "new_preprints": [r for r in records if r["id"] not in on_page and r["id"] not in IGNORE],
        "now_published": [
            r for r in records if r["id"] in in_preprints and (r["journal_ref"] or r["doi"])
        ],
        "still_preprint": sorted(in_preprints),
    }
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
