"""Find Chinese left in the rendered English site (outside the allowed 'label (中文)' pattern)."""
import os, re, sys
from collections import Counter
from bs4 import BeautifulSoup, NavigableString
sys.stdout.reconfigure(encoding="utf-8")
SITE = r"C:\AC6965E\Jieli\JL_Tools_Docs_en"
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def strip_parens(s):
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\([^()]*\)", "", s)
        s = re.sub(r"（[^（）]*）", "", s)
    return s


per_page = Counter()
samples = []
in_code = 0
paren_han = 0
for dp, dn, fn in os.walk(SITE):
    for f in fn:
        if not f.endswith(".html"):
            continue
        fp = os.path.join(dp, f)
        rel = os.path.relpath(fp, SITE)
        soup = BeautifulSoup(open(fp, encoding="utf-8").read(), "lxml")
        for el in soup.select(".lang-switch, #jl-logo"):
            el.decompose()
        main = soup.select_one('[itemprop="articleBody"]')
        scopes = [soup.select_one(".wy-menu-vertical"), soup.select_one(".wy-breadcrumbs"), main, soup.title]
        for scope in scopes:
            if scope is None:
                continue
            # judge text block by block so "label (中文)" spanning inline tags is recognised
            blocks = scope.find_all(["p", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "figcaption", "dt", "dd", "a", "span", "title"])
            seen = set()
            for s in scope.find_all(string=HAN):
                if s.find_parent("pre") is not None:
                    in_code += 1
                    continue
                blk = s.parent
                while blk is not None and blk.name not in ("p", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "figcaption", "dt", "dd", "title", "div"):
                    blk = blk.parent
                key = id(blk)
                if key in seen:
                    continue
                seen.add(key)
                text = re.sub(r"\s+", " ", (blk or s).get_text())
                if HAN.search(strip_parens(text)):
                    per_page[rel] += 1
                    samples.append((rel, text.strip()[:140]))
                else:
                    paren_han += 1
print("blocks with Chinese only inside parentheses (expected labels):", paren_han)
print("Chinese text nodes inside code blocks:", in_code)
print("blocks with Chinese outside parentheses:", sum(per_page.values()), "on", len(per_page), "pages")
for p, n in per_page.most_common(40):
    print(f"  {n:4d}  {p}")
print()
for rel, t in samples[:int(sys.argv[1]) if len(sys.argv) > 1 else 60]:
    print(f"[{rel}] {t}")
