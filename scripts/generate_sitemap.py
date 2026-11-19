#!/usr/bin/env python3
"""Generate a complete XML sitemap from tracked public HTML pages."""
from pathlib import Path
from datetime import datetime, timezone
from subprocess import run
from urllib.parse import quote
from xml.etree.ElementTree import Element, SubElement, ElementTree, register_namespace

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://highlandlakeslive.com"
EXCLUDE_PARTS = {".github", "node_modules", "vendor", "tests", "test", "drafts", "backup", "backups"}
register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

def last_commit_date(path):
    result = run(["git", "log", "-1", "--format=%cs", "--", path],
                 cwd=ROOT, capture_output=True, text=True, check=False)
    date = result.stdout.strip()
    return date if len(date) == 10 and date[4] == "-" and date[7] == "-" else None

def main():
    pages = sorted(p.relative_to(ROOT) for p in ROOT.rglob("*.html")
                   if not any(part.lower() in EXCLUDE_PARTS for part in p.relative_to(ROOT).parts)
                   and not p.name.lower().startswith(("test-", "draft-", "backup-")))
    urlset = Element(NS + "urlset")
    for relative in [Path("index.html")] + [p for p in pages if p != Path("index.html")]:
        if not (ROOT / relative).is_file():
            continue
        entry = SubElement(urlset, NS + "url")
        url = BASE + ("/" if relative == Path("index.html") else "/" + quote(relative.as_posix()))
        SubElement(entry, NS + "loc").text = url
        date = last_commit_date(relative.as_posix())
        if date:
            SubElement(entry, NS + "lastmod").text = date
    output = ROOT / "sitemap.xml"
    ElementTree(urlset).write(output, encoding="utf-8", xml_declaration=True)
    print(f"Generated {len(urlset)} URLs in {output}")

if __name__ == "__main__":
    main()
