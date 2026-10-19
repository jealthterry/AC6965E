"""Render the offline site from ir.json.

usage: python render.py zh|en
"""
import base64, html, json, os, posixpath, re, shutil, sys
from urllib.parse import quote
from bs4 import BeautifulSoup, NavigableString, Tag

sys.stdout.reconfigure(encoding="utf-8")
SCRATCH = os.path.dirname(os.path.abspath(__file__))
ROOT = r"C:\AC6965E\Jieli"
HOME_FILES = os.path.join(ROOT, "程序开发相关工具", "欢迎使用杰理工具文档 — JL Project Documentation_files")
RTD_FONTS = os.path.join(SCRATCH, "rtd", "sphinx_rtd_theme", "static", "css", "fonts")
ONLINE_BASE = "https://doc.zh-jieli.com/Tools/zh-cn/"
SAVED_DATE = "2026-10-18"

LANG = sys.argv[1] if len(sys.argv) > 1 else "zh"
OUT = os.path.join(ROOT, "JL_Tools_Docs_" + LANG)
OTHER = "en" if LANG == "zh" else "zh"

T = {
    "zh": dict(
        html_lang="zh-CN",
        site="JL Project Documentation",
        short="JieLi_Tools",
        search_ph="搜索文档",
        other_label="English",
        other_title="查看英文译文",
        prev="上一页",
        next="下一页",
        copyright="© Copyright 2010-2022, 杰理科技股份有限公司.",
        online="在线原文",
        home_note=("这是杰理工具文档（doc.zh-jieli.com/Tools）的离线副本，保存于 {date}。"
                   "无需联网即可浏览；搜索在本地完成。工具下载链接仍指向杰理官方服务器，需要联网。"),
        archived_note=("原保存文件中缺少本页，本页已从 Internet Archive 存档（{date}）恢复，"
                       "内容可能与官网最新版本略有差异。"),
        search_title="搜索",
        search_intro="输入关键词搜索全部文档（支持多个关键词，用空格分隔）。",
        search_none="没有找到匹配的结果。",
        search_found="找到 {n} 个结果",
        captions={},
    ),
    "en": dict(
        html_lang="en",
        site="JL Project Documentation",
        short="JieLi_Tools",
        search_ph="Search docs",
        other_label="中文原文",
        other_title="View the original Chinese page",
        prev="Previous",
        next="Next",
        copyright="© Copyright 2010-2022, Jieli Technology Co., Ltd.",
        online="Online original (Chinese)",
        home_note=("This is an offline copy of the Jieli Tools documentation (doc.zh-jieli.com/Tools), saved on {date}, "
                   "with an unofficial English translation made by Claude (AI) from the Chinese original. "
                   "Text inside screenshots is still in Chinese; where the text names an on-screen label, "
                   "the original Chinese label is usually given in parentheses so you can match it in the screenshot or tool. "
                   "Use the <b>中文原文</b> link at the top of each page to compare with the original. "
                   "Tool download links still point to Jieli's servers and need an internet connection."),
        archived_note=("This page was missing from the saved files and was restored from an Internet Archive snapshot "
                       "({date}); it may differ slightly from the current online version."),
        search_title="Search",
        search_intro="Search all pages. Separate multiple keywords with spaces.",
        search_none="No matching results.",
        search_found="{n} results",
        captions={},
    ),
}[LANG]

ir = json.load(open(os.path.join(SCRATCH, "ir.json"), encoding="utf-8"))

# ---------------------------------------------------------------- translation support (en)
TR = None
if LANG == "en":
    import segment
    TR = segment.Translator.load(SCRATCH)
    T["captions"] = json.load(open(os.path.join(SCRATCH, "captions_en.json"), encoding="utf-8"))


# ---------------------------------------------------------------- helpers
def depth_prefix(path):
    d = path.count("/")
    return "../" * d


def resolve(href, page_path):
    """@site/x#f -> relative URL from page_path."""
    if not href or not href.startswith("@site/"):
        return href
    target = href[len("@site/"):]
    frag = ""
    if "#" in target:
        target, frag = target.split("#", 1)
        frag = "#" + frag
    base_dir = posixpath.dirname(page_path)
    rel = posixpath.relpath(target, base_dir or ".")
    return quote(rel, safe="/._-~") + frag


def fix_links(soup_el, page_path):
    for el in soup_el.find_all(["a", "img", "link"]):
        for att in ("href", "src"):
            v = el.get(att)
            if v and v.startswith("@site/"):
                el[att] = resolve(v, page_path)
        if el.name == "a":
            href = el.get("href", "")
            if href.startswith(("http://", "https://")):
                el["target"] = "_blank"
                el["rel"] = "noopener"


def frag_soup(html_text):
    s = BeautifulSoup('<div id="__root">' + html_text + "</div>", "lxml")
    return s, s.find(id="__root")


SECNUM = re.compile(r"^\s*((?:\d+\.)+)\s*")


# ---------------------------------------------------------------- page titles (for menu, crumbs, prev/next)
def page_heading_map():
    """(page, anchor) -> (number, plain title) in the output language."""
    m = {}
    for path, p in ir.items():
        s, root = frag_soup(p["body"])
        if TR:
            TR.apply(path, root)
        first = True
        for h in root.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            sec = h.find_parent("section")
            num_el = h.find("span", class_="section-number")
            num = num_el.get_text() if num_el else ""
            parts = []
            for c in h.children:
                if isinstance(c, Tag) and ("section-number" in (c.get("class") or []) or "headerlink" in (c.get("class") or [])):
                    continue
                parts.append(c.get_text() if isinstance(c, Tag) else str(c))
            text = re.sub(r"\s+", " ", "".join(parts)).strip()
            ids = []
            if sec is not None and sec.get("id"):
                ids.append(sec["id"])
                for sp in sec.find_all("span", recursive=False):
                    if sp.get("id"):
                        ids.append(sp["id"])
            for i in ids:
                m.setdefault((path, i), (num, text))
            if first and h.name == "h1":
                m[(path, "")] = (num, text)
                first = False
        if (path, "") not in m:
            m[(path, "")] = ("", p["title"])
    return m


HEAD = page_heading_map()


def title_of(path):
    num, text = HEAD.get((path, ""), ("", ir[path]["title"]))
    return num, text


def target_key(href, page_path):
    if href is None:
        return None
    if href.startswith("@site/"):
        t = href[len("@site/"):]
        page, _, frag = t.partition("#")
        return (page, frag)
    if href.startswith("#"):
        return (page_path, href[1:])
    return None


# ---------------------------------------------------------------- building blocks
def build_menu(p):
    s, root = frag_soup(p["menu"])
    for a in root.find_all("a"):
        key = target_key(a.get("href"), p["path"])
        if TR and key:
            if key in HEAD:
                num, text = HEAD[key]
                if not num:
                    mm = SECNUM.match(a.get_text())
                    num = (mm.group(1) + " ") if mm else ""
                a.clear()
                a.append(NavigableString((num.strip() + " " if num.strip() else "") + text))
            else:
                TR.missing_ui.add(("menu", p["path"], a.get_text()))
    for cap in root.select("span.caption-text"):
        if T["captions"]:
            zh = cap.get_text().strip()
            cap.string = T["captions"].get(zh, zh)
            if zh not in T["captions"]:
                TR.missing_ui.add(("caption", zh))
    for a in root.find_all("a"):
        ul = a.find_next_sibling("ul")
        if ul is not None:
            b = s.new_tag("button", attrs={"class": "toctree-expand", "title": "Open/close menu", "type": "button"})
            a.insert(0, b)
    fix_links(root, p["path"])
    return root.decode_contents()


def build_crumbs(p):
    pre = depth_prefix(p["path"])
    out = [f'<li><a href="{pre}index.html" class="icon icon-home" aria-label="Home"></a> »</li>']
    for c in p["crumbs"]:
        if c["href"]:
            key = target_key(c["href"], p["path"])
            if TR and key and key[0] in ir:
                num, text = title_of(key[0])
                inner = (f'<span class="section-number">{html.escape(num)}</span>' if num else "") + html.escape(text)
            else:
                inner = c["html"]
            out.append(f'<li><a href="{resolve(c["href"], p["path"])}">{inner}</a> »</li>')
        else:
            if TR and p["path"] in ir:
                num, text = title_of(p["path"])
                inner = (f'<span class="section-number">{html.escape(num)}</span>' if num else "") + html.escape(text)
            else:
                inner = c["html"]
            out.append(f"<li>{inner}</li>")
    other = f'{pre}../JL_Tools_Docs_{OTHER}/{quote(p["path"], safe="/._-~")}'
    out.append(f'<li class="wy-breadcrumbs-aside"><a class="lang-switch" href="{other}" title="{T["other_title"]}">{T["other_label"]}</a></li>')
    return "\n".join(out)


def nav_button(p, which):
    n = p.get(which)
    if not n:
        return ""
    href = resolve(n["href"], p["path"])
    key = target_key(n["href"], p["path"])
    if key and key[0] in ir:
        num, text = title_of(key[0])
        title = (num + text).strip()
    else:
        title = n["title"]
    if which == "prev":
        return (f'<a href="{href}" class="btn btn-neutral float-left" title="{html.escape(title)}" accesskey="p" rel="prev">'
                f'<span class="fa fa-arrow-circle-left" aria-hidden="true"></span> {T["prev"]}</a>')
    return (f'<a href="{href}" class="btn btn-neutral float-right" title="{html.escape(title)}" accesskey="n" rel="next">'
            f'{T["next"]} <span class="fa fa-arrow-circle-right" aria-hidden="true"></span></a>')


def build_body(p):
    s, root = frag_soup(p["body"])
    if TR:
        TR.apply(p["path"], root)
        TR.fix_xrefs(p["path"], root, HEAD)
    for el in root.find_all(attrs={"data-zh": True}):
        del el["data-zh"]
    notes = []
    if p["path"] == "index.html":
        notes.append(f'<div class="admonition note offline-note"><p class="admonition-title">{"Note" if LANG == "en" else "说明"}</p>'
                     f'<p>{T["home_note"].format(date=SAVED_DATE)}</p></div>')
    if p["archived"]:
        d = p["archived"]
        notes.append(f'<div class="admonition warning offline-note"><p class="admonition-title">{"Note" if LANG == "en" else "注意"}</p>'
                     f'<p>{T["archived_note"].format(date=d[:4] + "-" + d[4:6] + "-" + d[6:8])}</p></div>')
    fix_links(root, p["path"])
    body_html = root.decode_contents()
    if notes:
        # place the note right after the first heading
        i = body_html.find("</h1>")
        if i >= 0:
            i += len("</h1>")
            body_html = body_html[:i] + "\n" + "\n".join(notes) + body_html[i:]
        else:
            body_html = "\n".join(notes) + body_html
    return body_html, root


PAGE_TMPL = """<!DOCTYPE html>
<html class="writer-html5" lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — {site}</title>
<link rel="stylesheet" href="{pre}_static/css/theme.css" type="text/css">
<link rel="stylesheet" href="{pre}_static/pygments.css" type="text/css">
<link rel="stylesheet" href="{pre}_static/jl/custom.css" type="text/css">
<link rel="stylesheet" href="{pre}_static/jl/custom.light.css" type="text/css">
<link rel="stylesheet" href="{pre}_static/offline.css" type="text/css">
</head>
<body class="wy-body-for-nav">
<div class="wy-grid-for-nav">
  <nav data-toggle="wy-nav-shift" class="wy-nav-side">
    <div class="wy-side-scroll">
      <div class="wy-side-nav-search">
        <a id="jl-logo-link" href="{pre}index.html"><img id="jl-logo" src="{pre}_static/jl/logo.png" alt="JieLi"></a>
        <form id="rtd-search-form" class="wy-form" action="{pre}search.html" method="get">
          <input type="text" name="q" placeholder="{search_ph}" aria-label="{search_ph}">
        </form>
      </div>
      <div class="wy-menu wy-menu-vertical" role="navigation" aria-label="Navigation menu">
{menu}
      </div>
    </div>
  </nav>
  <section data-toggle="wy-nav-shift" class="wy-nav-content-wrap">
    <nav class="wy-nav-top" aria-label="Mobile navigation menu">
      <i data-toggle="wy-nav-top" class="fa fa-bars"></i>
      <a href="{pre}index.html">{short}</a>
    </nav>
    <div class="wy-nav-content">
      <div class="rst-content">
        <div role="navigation" aria-label="Page navigation">
          <ul class="wy-breadcrumbs">
{crumbs}
          </ul>
          <hr>
        </div>
        <div role="main" class="document" itemscope="itemscope" itemtype="http://schema.org/Article">
          <div itemprop="articleBody">
{body}
          </div>
        </div>
        <footer>
          <div class="rst-footer-buttons" role="navigation" aria-label="Footer">
            {prev}
            {next}
          </div>
          <hr>
          <div role="contentinfo">
            <p>{copyright} <span class="lastupdated">{lastupdated}</span></p>
            <p class="offline-source">{online_label}: <a href="{online_url}" target="_blank" rel="noopener">{online_url}</a></p>
          </div>
        </footer>
      </div>
    </div>
  </section>
</div>
{scripts}
</body>
</html>
"""


def write_page(path, title, menu, crumbs, body, prev="", nxt="", lastupdated="", scripts=""):
    pre = depth_prefix(path)
    out = PAGE_TMPL.format(
        lang=T["html_lang"], title=html.escape(title), site=T["site"], pre=pre, search_ph=T["search_ph"],
        menu=menu, short=T["short"], crumbs=crumbs, body=body, prev=prev, next=nxt,
        copyright=T["copyright"], lastupdated=html.escape(lastupdated), online_label=T["online"],
        online_url=ONLINE_BASE + (path if path != "search.html" else "index.html"),
        scripts=scripts or f'<script src="{pre}_static/offline.js"></script>',
    )
    dest = os.path.join(OUT, *path.split("/"))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)


# ---------------------------------------------------------------- search index
def index_sections(path, page_title, root):
    for hl in root.select("a.headerlink"):
        hl.decompose()
    entries = []
    for sec in root.find_all("section"):
        h = sec.find(["h1", "h2", "h3", "h4", "h5", "h6"], recursive=False)
        if h is None:
            continue
        htext = re.sub(r"\s+", " ", h.get_text()).strip()
        texts = []
        for child in sec.children:
            if isinstance(child, Tag) and child.name in ("section",) or child is h:
                continue
            t = child.get_text(" ") if isinstance(child, Tag) else str(child)
            texts.append(t)
        body = re.sub(r"\s+", " ", " ".join(texts)).strip()
        entries.append({"p": path, "a": sec.get("id", ""), "h": htext, "t": page_title, "x": body})
    if not entries:
        entries.append({"p": path, "a": "", "h": page_title, "t": page_title,
                        "x": re.sub(r"\s+", " ", root.get_text(" ")).strip()})
    return entries


# ---------------------------------------------------------------- static assets
def copy_static():
    st = os.path.join(OUT, "_static")
    os.makedirs(os.path.join(st, "css", "fonts"), exist_ok=True)
    os.makedirs(os.path.join(st, "jl"), exist_ok=True)
    shutil.copy(os.path.join(HOME_FILES, "theme.css"), os.path.join(st, "css", "theme.css"))
    shutil.copy(os.path.join(HOME_FILES, "pygments.css"), os.path.join(st, "pygments.css"))
    for f in ("custom.css", "custom.light.css", "logo.png"):
        shutil.copy(os.path.join(HOME_FILES, f), os.path.join(st, "jl", f))
    for f in os.listdir(RTD_FONTS):
        shutil.copy(os.path.join(RTD_FONTS, f), os.path.join(st, "css", "fonts", f))
    fa = base64.b64encode(open(os.path.join(RTD_FONTS, "fontawesome-webfont.woff2"), "rb").read()).decode()
    css = open(os.path.join(SCRATCH, "offline.css"), encoding="utf-8").read()
    css = css.replace("__FA_WOFF2__", fa)
    open(os.path.join(st, "offline.css"), "w", encoding="utf-8", newline="\n").write(css)
    js = open(os.path.join(SCRATCH, "offline.js"), encoding="utf-8").read()
    js = js.replace("__LANG__", LANG)
    open(os.path.join(st, "offline.js"), "w", encoding="utf-8", newline="\n").write(js)
    img_src = os.path.join(SCRATCH, "stage", "_images")
    img_dst = os.path.join(OUT, "_images")
    os.makedirs(img_dst, exist_ok=True)
    for f in os.listdir(img_src):
        d = os.path.join(img_dst, f)
        s = os.path.join(img_src, f)
        if not os.path.exists(d) or os.path.getsize(d) != os.path.getsize(s):
            shutil.copy(s, d)


# ---------------------------------------------------------------- main
def main():
    if os.path.isdir(OUT):
        for name in os.listdir(OUT):
            if name != "_images":
                full = os.path.join(OUT, name)
                shutil.rmtree(full) if os.path.isdir(full) else os.remove(full)
    os.makedirs(OUT, exist_ok=True)
    copy_static()
    search = []
    for path, p in ir.items():
        num, text = title_of(path)
        title = (num + text).strip() if path != "index.html" else text
        body_html, root = build_body(p)
        write_page(path, title, build_menu(p), build_crumbs(p), body_html,
                   nav_button(p, "prev"), nav_button(p, "next"), p["lastupdated"])
        search += index_sections(path, title, root)
    # search page
    home = ir["index.html"]
    sp = dict(home, path="search.html", crumbs=[{"href": None, "html": T["search_title"]}])
    menu = build_menu(sp).replace(' class="current"', "")
    body = (f'<h1>{T["search_title"]}</h1><p>{T["search_intro"]}</p>'
            f'<form class="offline-search-form" onsubmit="return false;"><input type="search" id="offline-q" '
            f'placeholder="{T["search_ph"]}" autofocus></form>'
            f'<p id="offline-search-status" data-none="{T["search_none"]}" data-found="{T["search_found"]}"></p>'
            f'<ul id="offline-search-results" class="search"></ul>')
    write_page("search.html", T["search_title"], menu, build_crumbs(sp), body,
               scripts='<script src="_static/search_index.js"></script>\n<script src="_static/offline.js"></script>')
    with open(os.path.join(OUT, "_static", "search_index.js"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("window.SEARCH_INDEX = ")
        json.dump(search, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";\n")
    print(f"[{LANG}] wrote {len(ir)} pages + search ({len(search)} sections) -> {OUT}")
    if TR:
        TR.report()


main()
