"""Identity round trip: inject every unit's own source text and compare the DOM."""
import json, re, sys
from collections import Counter
from bs4 import Tag
from segment import collect, frag_soup, norm_ws, SegError, TOKEN_RE

sys.stdout.reconfigure(encoding="utf-8")
ir = json.load(open("ir.json", encoding="utf-8"))


def signature(root):
    tags = [(t.name, tuple(sorted((k, " ".join(v) if isinstance(v, list) else v) for k, v in t.attrs.items())))
            for t in root.find_all(True)]
    text = norm_ws(root.get_text(" "))
    text = re.sub(r"\s+", "", text)
    return tags, text


bad = 0
kinds = Counter()
ph_counts = Counter()
for path, p in ir.items():
    s1, r1 = frag_soup(p["body"])
    before = signature(r1)
    s2, r2 = frag_soup(p["body"])
    segs = collect(r2)
    for seg in segs:
        kinds[seg.kind] += 1
        ph_counts[len(TOKEN_RE.findall(seg.text)) // 2] += 1
    try:
        for seg in [x for x in segs if x.kind == "attr"] + [x for x in segs if x.kind != "attr"]:
            seg.inject(s2, seg.text)
    except SegError as e:
        print("ERROR", path, e)
        bad += 1
        continue
    after = signature(r2)
    if before[0] != after[0]:
        bad += 1
        a, b = before[0], after[0]
        i = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
        print("TAG DIFF", path, "at", i, a[i:i + 2], b[i:i + 2], len(a), len(b))
    elif before[1] != after[1]:
        bad += 1
        a, b = before[1], after[1]
        i = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), 0)
        print("TEXT DIFF", path, repr(a[i - 30:i + 30]), "||", repr(b[i - 30:i + 30]))
print("pages:", len(ir), "bad:", bad, "segments by kind:", dict(kinds))
print("placeholder pairs per segment (approx):", sorted(ph_counts.items())[:12])
