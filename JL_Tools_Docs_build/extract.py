"""Build the translation work: unique units (deduplicated), page order, batches for translators."""
import json, os, re, sys
from collections import OrderedDict
from bs4 import Tag
from segment import collect, frag_soup, unit_id, HAN_RE, BLOCK_TAGS, RunSeg

sys.stdout.reconfigure(encoding="utf-8")
TR = "tr"
os.makedirs(os.path.join(TR, "batches"), exist_ok=True)
os.makedirs(os.path.join(TR, "out"), exist_ok=True)
os.makedirs(os.path.join(TR, "prefill"), exist_ok=True)
ir = json.load(open("ir.json", encoding="utf-8"))
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 4200   # Han characters per batch

# reading order: follow "next" links from the home page, then anything left over
order, seen, cur = [], set(), "index.html"
while cur and cur not in seen and cur in ir:
    order.append(cur)
    seen.add(cur)
    nxt = ir[cur].get("next")
    cur = nxt["href"][len("@site/"):].split("#")[0] if nxt and nxt["href"].startswith("@site/") else None
order += [p for p in sorted(ir) if p not in seen]


def role_of(seg):
    if seg.kind == "code":
        return "code"
    if seg.kind == "attr":
        return "attr"
    el = seg.nodes[0].parent
    while el is not None and el.name not in BLOCK_TAGS:
        el = el.parent
    if el is None:
        return "p"
    r = el.name
    if r in ("p", "div") and el.find_parent(["td", "th"]) is not None:
        r = "cell"
    if r in ("td", "th"):
        r = "cell"
    if r == "p" and el.find_parent("figcaption") is not None:
        r = "caption"
    if r == "figcaption":
        r = "caption"
    return r


units = OrderedDict()
for path in order:
    s, root = frag_soup(ir[path]["body"])
    for seg in collect(root):
        uid = unit_id(seg.kind, seg.text)
        if uid not in units:
            u = {"id": uid, "kind": seg.kind, "role": role_of(seg), "zh": seg.text, "page": path}
            if seg.ctx:
                u["ctx"] = seg.ctx
            units[uid] = u
        units[uid].setdefault("count", 0)
        units[uid]["count"] += 1

json.dump(list(units.values()), open(os.path.join(TR, "units.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# prefilled units are excluded from batches
prefilled = {}
for f in os.listdir(os.path.join(TR, "prefill")):
    prefilled.update(json.load(open(os.path.join(TR, "prefill", f), encoding="utf-8")))

todo = [u for u in units.values() if u["id"] not in prefilled]
han = lambda u: len(HAN_RE.findall(u["zh"]))
total = sum(han(u) for u in todo)
print(f"pages {len(order)}; unique units {len(units)} (of {sum(u['count'] for u in units.values())} occurrences); "
      f"to translate {len(todo)} units, {total} Han chars; prefilled {len(prefilled)}")

# pack into batches, keeping page groups together where possible
titles = {p: ir[p]["title"] for p in ir}
batches, cur_b, cur_n = [], [], 0
for path in order:
    pu = [u for u in todo if u["page"] == path]
    while pu:
        room = TARGET - cur_n
        take, n = [], 0
        for u in pu:
            if take and n + han(u) > room and cur_n + n > TARGET * 0.5:
                break
            take.append(u)
            n += han(u)
        if not take or (cur_b and cur_n + n > TARGET * 1.15 and cur_n > TARGET * 0.6):
            batches.append(cur_b)
            cur_b, cur_n = [], 0
            continue
        cur_b.append({"page": path, "page_title": titles[path], "units": take})
        cur_n += n
        pu = pu[len(take):]
        if cur_n >= TARGET:
            batches.append(cur_b)
            cur_b, cur_n = [], 0
if cur_b:
    batches.append(cur_b)

for f in os.listdir(os.path.join(TR, "batches")):
    os.remove(os.path.join(TR, "batches", f))
for i, b in enumerate(batches, 1):
    name = f"b{i:02d}"
    for g in b:
        g["units"] = [{k: u[k] for k in ("id", "role", "zh", "ctx") if k in u} for u in g["units"]]
    json.dump({"batch": name, "pages": b}, open(os.path.join(TR, "batches", name + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    nh = sum(len(HAN_RE.findall(u["zh"])) for g in b for u in g["units"])
    nu = sum(len(g["units"]) for g in b)
    print(f"  {name}: {nu:4d} units, {nh:5d} Han chars, pages: {', '.join(g['page'].replace('.html', '') for g in b)[:150]}")
json.dump(order, open(os.path.join(TR, "order.json"), "w"), indent=0)
