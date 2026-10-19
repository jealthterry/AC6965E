"""Check that every local link / image / stylesheet in the rendered site resolves (file + #anchor)."""
import os, re, sys, collections
from urllib.parse import unquote, urldefrag
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding="utf-8")
SITE = sys.argv[1]
ids_cache = {}
problems = collections.Counter()
examples = collections.defaultdict(list)
external = collections.Counter()
n_links = 0


def ids_of(fp):
    if fp not in ids_cache:
        s = BeautifulSoup(open(fp, encoding="utf-8").read(), "lxml")
        ids_cache[fp] = {e["id"] for e in s.find_all(id=True)}
    return ids_cache[fp]


for dp, dn, fn in os.walk(SITE):
    for f in fn:
        if not f.endswith(".html"):
            continue
        fp = os.path.join(dp, f)
        soup = BeautifulSoup(open(fp, encoding="utf-8").read(), "lxml")
        ids_cache[fp] = {e["id"] for e in soup.find_all(id=True)}
        for el in soup.find_all(["a", "img", "link", "script"]):
            for att in ("href", "src"):
                v = el.get(att)
                if not v:
                    continue
                n_links += 1
                if v.startswith(("http://", "https://")):
                    external[re.sub(r"^https?://([^/]+).*", r"\1", v)] += 1
                    continue
                if v.startswith(("mailto:", "javascript:", "data:")):
                    continue
                path, frag = urldefrag(v)
                path = path.split("?")[0]
                target = os.path.normpath(os.path.join(dp, unquote(path))) if path else fp
                rel = os.path.relpath(fp, SITE)
                if "JL_Tools_Docs_" in path:  # cross-language link, checked separately
                    continue
                if not os.path.exists(target):
                    problems["missing file"] += 1
                    examples["missing file"].append(f"{rel}: {v}")
                    continue
                if frag and target.endswith(".html") and frag not in ids_of(target):
                    problems["missing anchor"] += 1
                    examples["missing anchor"].append(f"{rel}: {v}")
print("links checked:", n_links)
print("external hosts:", dict(external))
print("problems:", dict(problems) or "none")
for k, v in examples.items():
    for e in v[:25]:
        print(f"  [{k}] {e}")
