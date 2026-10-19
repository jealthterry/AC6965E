"""Split page bodies into translation units and inject translations back.

The same `collect()` runs at extraction time and at render time, so units line up exactly.
Inline markup inside a unit is replaced by placeholders:  ⟦n⟧...⟦/n⟧  (paired)  and  ⟦n/⟧  (void).
"""
import copy, glob, hashlib, json, os, re
from collections import Counter
from bs4 import BeautifulSoup, Comment, NavigableString, Tag

HAN = r"㐀-䶿一-鿿豈-﫿"
CJK_PUNCT = r"　-〿！-｠￠-￦"
CJK_RE = re.compile(f"[{HAN}{CJK_PUNCT}]")
HAN_RE = re.compile(f"[{HAN}]")

BLOCK_TAGS = {
    "address", "article", "aside", "blockquote", "caption", "center", "col", "colgroup", "dd", "details", "dialog",
    "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6",
    "header", "hr", "li", "main", "nav", "ol", "p", "pre", "section", "summary", "table", "tbody", "td", "tfoot",
    "th", "thead", "tr", "ul", "video", "audio", "iframe",
}
VOID_TAGS = {"br", "img", "wbr", "input", "hr", "area", "source", "embed"}
SKIP_TAGS = {"script", "style", "noscript", "svg", "math"}
TOKEN_RE = re.compile(r"⟦(/?)(\d+)(/?)⟧")
SECNUM_RE = re.compile(r"^((?:\d+\.)+)\s+")
WS_RE = re.compile(r"[ \t\r\n\f]+")


def has_cjk(s):
    return bool(CJK_RE.search(s))


def norm_ws(s):
    return WS_RE.sub(" ", s).strip()


def is_code_literal(t):
    return isinstance(t, Tag) and t.name == "code" and "literal" in (t.get("class") or [])


def excluded(t):
    cls = t.get("class") or []
    return (t.name == "a" and "headerlink" in cls) or (t.name == "span" and "section-number" in cls)


def is_container(t):
    return t.name in BLOCK_TAGS or t.name in SKIP_TAGS or t.find(list(BLOCK_TAGS)) is not None


def text_of(nodes):
    return "".join(n.get_text() if isinstance(n, Tag) else str(n) for n in nodes if not isinstance(n, Comment))


def unit_id(kind, zh):
    return "u" + hashlib.sha1((kind + "\x00" + zh).encode("utf-8")).hexdigest()[:10]


class SegError(Exception):
    pass


def shallow_clone(soup, t):
    attrs = {k: (list(v) if isinstance(v, list) else v) for k, v in t.attrs.items()}
    return soup.new_tag(t.name, attrs=attrs)


class RunSeg:
    kind = "text"

    def __init__(self, nodes):
        self.nodes = nodes
        self.phs = []
        raw = self._ser(nodes)
        self.lead = bool(raw) and raw[0] in " \t\r\n\f"
        self.trail = bool(raw) and raw[-1] in " \t\r\n\f"
        self.text = norm_ws(raw)
        self.ctx = None

    def _add(self, entry):
        self.phs.append(entry)
        return len(self.phs)

    def _ser(self, nodes):
        out = []
        for n in nodes:
            if isinstance(n, Comment):
                continue
            if isinstance(n, NavigableString):
                out.append(str(n))
                continue
            if n.name in VOID_TAGS:
                out.append(f"⟦{self._add(('void', n))}/⟧")
            elif is_code_literal(n):
                i = self._add(("code", n))
                out.append(f"⟦{i}⟧{norm_ws(n.get_text())}⟦/{i}⟧")
            else:
                chain, cur = [n], n
                while True:
                    kids = [c for c in cur.children
                            if not (isinstance(c, NavigableString) and (isinstance(c, Comment) or not str(c).strip()))]
                    if (len(kids) == 1 and isinstance(kids[0], Tag) and kids[0].name not in VOID_TAGS
                            and not is_code_literal(kids[0])):
                        cur = kids[0]
                        chain.append(cur)
                    else:
                        break
                i = self._add(("pair", chain))
                out.append(f"⟦{i}⟧" + self._ser(list(cur.children)) + f"⟦/{i}⟧")
        return "".join(out)

    def _make(self, soup, idx, kids):
        kind, ref = self.phs[idx - 1]
        if kind == "code":
            if not has_cjk(ref.get_text()):
                return copy.copy(ref)
            new = shallow_clone(soup, ref)
            txt = norm_ws(text_of(kids))
            if ref.find("span", class_="pre") is not None:
                for i, tok in enumerate(txt.split(" ")):
                    if i:
                        new.append(NavigableString(" "))
                    sp = soup.new_tag("span", attrs={"class": ["pre"]})
                    sp.string = tok
                    new.append(sp)
            else:
                new.string = txt
            return new
        clones = [shallow_clone(soup, t) for t in ref]
        for a, b in zip(clones, clones[1:]):
            a.append(b)
        for k in kids:
            clones[-1].append(k)
        return clones[0]

    def build(self, soup, text):
        stack = [(None, [])]
        seen = Counter()
        pos = 0
        for m in TOKEN_RE.finditer(text):
            if m.start() > pos:
                stack[-1][1].append(NavigableString(text[pos:m.start()]))
            close, idx, void = m.group(1), int(m.group(2)), m.group(3)
            if not 1 <= idx <= len(self.phs):
                raise SegError(f"unknown placeholder {m.group(0)}")
            kind, ref = self.phs[idx - 1]
            if void:
                if kind != "void":
                    raise SegError(f"{m.group(0)} should be paired")
                stack[-1][1].append(copy.copy(ref))
                seen[idx] += 1
            elif not close:
                if kind == "void":
                    raise SegError(f"{m.group(0)} should be void")
                stack.append((idx, []))
            else:
                if stack[-1][0] != idx:
                    raise SegError(f"mismatched {m.group(0)}")
                _, kids = stack.pop()
                stack[-1][1].append(self._make(soup, idx, kids))
                seen[idx] += 1
            pos = m.end()
        if pos < len(text):
            stack[-1][1].append(NavigableString(text[pos:]))
        if len(stack) != 1:
            raise SegError("unclosed placeholder")
        missing = set(range(1, len(self.phs) + 1)) - set(seen)
        dup = [k for k, v in seen.items() if v > 1]
        if missing or dup:
            raise SegError(f"missing {sorted(missing)} duplicated {dup}")
        return stack[0][1]

    def inject(self, soup, translated):
        new_nodes = self.build(soup, translated)
        if self.lead:
            new_nodes.insert(0, NavigableString(" "))
        if self.trail:
            new_nodes.append(NavigableString(" "))
        first = self.nodes[0]
        for nn in new_nodes:
            first.insert_before(nn)
        for n in self.nodes:
            n.extract()


class CodeSeg:
    kind = "code"

    def __init__(self, node, ctx):
        self.node = node
        self.text = str(node)
        self.ctx = ctx

    def inject(self, soup, translated):
        self.node.replace_with(NavigableString(translated))


class AttrSeg:
    kind = "attr"

    def __init__(self, el, att):
        self.el, self.att = el, att
        self.text = norm_ws(el[att])
        self.ctx = None

    def inject(self, soup, translated):
        self.el[self.att] = translated


def code_segs(pre):
    full = pre.get_text()
    segs, offset = [], 0
    for s in pre.find_all(string=True):
        if isinstance(s, Comment):
            continue
        t = str(s)
        if has_cjk(t):
            ctx = None
            if "\n" not in t.strip("\n"):
                a = full.rfind("\n", 0, offset) + 1
                b = full.find("\n", offset + len(t))
                line = full[a:b if b >= 0 else len(full)]
                if line.strip() != t.strip():
                    ctx = line[:300]
            segs.append(CodeSeg(s, ctx))
        offset += len(t)
    return segs


def collect(root):
    segs = []

    def flush(run):
        core = [n for n in run if not (isinstance(n, NavigableString) and (isinstance(n, Comment) or not str(n).strip()))]
        if not core or not has_cjk(text_of(core)):
            return
        if len(core) == 1 and isinstance(core[0], Tag) and core[0].name not in VOID_TAGS and not is_code_literal(core[0]):
            walk(core[0])
            return
        segs.append(RunSeg(run))

    def walk(el):
        if el.name in SKIP_TAGS:
            return
        if el.name == "pre":
            segs.extend(code_segs(el))
            return
        run = []
        for child in list(el.children):
            if isinstance(child, Comment):
                flush(run)
                run = []
            elif isinstance(child, NavigableString):
                run.append(child)
            elif excluded(child):
                flush(run)
                run = []
            elif child.name == "pre" or is_container(child):
                flush(run)
                run = []
                walk(child)
            else:
                run.append(child)
        flush(run)

    walk(root)
    for el in root.find_all(True):
        for att in ("alt", "title"):
            v = el.get(att)
            if isinstance(v, str) and has_cjk(v):
                segs.append(AttrSeg(el, att))
    return segs


def frag_soup(html_text):
    s = BeautifulSoup('<div id="__root">' + html_text + "</div>", "lxml")
    return s, s.find(id="__root")


# ---------------------------------------------------------------------------- render-time helper
class Translator:
    def __init__(self, tm):
        self.tm = tm  # (kind, zh) -> en
        self.missing = Counter()
        self.errors = []
        self.missing_ui = set()
        self.label_zh = None

    @classmethod
    def load(cls, scratch):
        tr = os.path.join(scratch, "tr")
        units = json.load(open(os.path.join(tr, "units.json"), encoding="utf-8"))
        by_id = {u["id"]: u for u in units}
        en = {}
        # translator output first, prefilled (fixed) titles last so they always win
        for f in sorted(glob.glob(os.path.join(tr, "out", "*.json"))) + sorted(glob.glob(os.path.join(tr, "prefill", "*.json"))):
            try:
                en.update(json.load(open(f, encoding="utf-8")))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"  skipping unreadable {os.path.basename(f)}: {e}")
        tm = {}
        for uid, text in en.items():
            u = by_id.get(uid)
            if u is not None and isinstance(text, str):
                tm[(u["kind"], u["zh"])] = text
        t = cls(tm)
        t.ir = json.load(open(os.path.join(scratch, "ir.json"), encoding="utf-8"))
        return t

    def apply(self, path, root):
        soup = root
        while soup.parent is not None:
            soup = soup.parent
        for a in root.select("a.reference.internal"):
            a["data-zh"] = norm_ws(a.get_text())
        segs = collect(root)
        ordered = [s for s in segs if s.kind == "attr"] + [s for s in segs if s.kind != "attr"]
        for seg in ordered:
            en = self.tm.get((seg.kind, seg.text))
            if en is None:
                self.missing[(path, seg.kind, seg.text[:80])] += 1
                continue
            try:
                seg.inject(soup, en)
            except SegError as e:
                self.errors.append((path, str(e), seg.text[:80]))

    def _labels_zh(self):
        """(page, anchor) -> zh plain text for headings / figure & table captions."""
        if self.label_zh is not None:
            return self.label_zh
        lab = {}
        for path, p in self.ir.items():
            s, root = frag_soup(p["body"])
            lab.update(labels_of(path, root))
        self.label_zh = lab
        return lab

    def fix_xrefs(self, path, root, head_en):
        """Make cross-reference link texts match the translated titles of their targets."""
        lab_zh = self._labels_zh()
        lab_en_local = labels_of(path, root)
        for a in root.select("a.reference.internal[data-zh]"):
            href = a.get("href", "")
            if href.startswith("@site/"):
                page, _, frag = href[len("@site/"):].partition("#")
            elif href.startswith("#"):
                page, frag = path, href[1:]
            else:
                continue
            zh_target = lab_zh.get((page, frag))
            if zh_target is None:
                continue
            zh_link = a["data-zh"]
            m = SECNUM_RE.match(zh_link)
            num = m.group(1) if m else ""
            if norm_ws(zh_target) == zh_link:
                num = ""
            elif not (num and norm_ws(zh_target) == zh_link[m.end():]):
                continue
            if page == path and (page, frag) in lab_en_local:
                en_text = lab_en_local[(page, frag)]
            elif (page, frag) in head_en:
                en_text = head_en[(page, frag)][1]
            else:
                en_text = self._figure_label_en(page, frag)
            if not en_text or has_cjk(en_text):
                continue
            inner = a
            while True:
                kids = [c for c in inner.children if isinstance(c, Tag)]
                if len(kids) == 1 and not inner.find(string=lambda s: s.strip() and s.parent is inner):
                    inner = kids[0]
                else:
                    break
            inner.clear()
            inner.append(NavigableString((num + " " if num else "") + en_text))

    def _figure_label_en(self, page, frag):
        cache = getattr(self, "_fig_cache", {})
        self._fig_cache = cache
        if page not in cache:
            s, root = frag_soup(self.ir[page]["body"]) if page in self.ir else (None, None)
            if root is None:
                cache[page] = {}
            else:
                self.apply(page, root)
                cache[page] = labels_of(page, root)
        return cache[page].get((page, frag))

    def report(self):
        print(f"  untranslated units: {sum(self.missing.values())} ({len(self.missing)} distinct)")
        for (p, k, t), n in list(self.missing.items())[:30]:
            print(f"    [{k}] {p}: {t}")
        print(f"  injection errors: {len(self.errors)}")
        for e in self.errors[:30]:
            print("    ", e)
        if self.missing_ui:
            print(f"  untranslated UI strings: {len(self.missing_ui)}")
            for m in sorted(self.missing_ui)[:30]:
                print("    ", m)


def labels_of(path, root):
    lab = {}
    for h in root.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        sec = h.find_parent("section")
        parts = [c.get_text() if isinstance(c, Tag) else str(c) for c in h.children
                 if not (isinstance(c, Tag) and excluded(c))]
        text = norm_ws("".join(parts))
        if sec is not None and sec.get("id"):
            lab.setdefault((path, sec["id"]), text)
            for sp in sec.find_all("span", recursive=False):
                if sp.get("id"):
                    lab.setdefault((path, sp["id"]), text)
        if h.name == "h1":
            lab.setdefault((path, ""), text)
    for fig in root.find_all(["figure", "table", "div"]):
        fid = fig.get("id")
        if not fid:
            continue
        cap = fig.find("span", class_="caption-text")
        if cap is not None:
            lab.setdefault((path, fid), norm_ws(cap.get_text()))
    return lab
