"""Normalise every source page into an intermediate representation (IR).

Links inside the IR use:
  @site/<path>[#frag]   -> another page / file of the offline site
  #frag                 -> same page
  http(s)://...         -> external (left online)
Images are staged into stage/_images/.
"""
import hashlib, json, os, re, shutil, sys
from urllib.parse import urljoin, urldefrag, unquote, quote
from bs4 import BeautifulSoup, NavigableString, Tag
from corpus import load_all, BASE, HOME_FILES, SCRATCH

sys.stdout.reconfigure(encoding="utf-8")
STAGE = os.path.join(SCRATCH, "stage")
IR_PATH = os.path.join(SCRATCH, "ir.json")

pages, resources = load_all()
page_paths = set(pages)
missing_images, image_hashes = {}, {}
os.makedirs(os.path.join(STAGE, "_images"), exist_ok=True)


def stage_image(abs_url, data_bytes=None):
    """Copy image into stage/_images, return site path or None."""
    name = unquote(abs_url.split("?")[0].rsplit("/", 1)[-1])
    if data_bytes is None:
        if abs_url in resources:
            data_bytes = resources[abs_url][1]
        else:
            return None
    h = hashlib.sha1(data_bytes).hexdigest()
    if name in image_hashes and image_hashes[name] != h:
        root, ext = os.path.splitext(name)
        name = f"{root}_{h[:6]}{ext}"
    image_hashes[name] = h
    dest = os.path.join(STAGE, "_images", name)
    if not os.path.exists(dest):
        open(dest, "wb").write(data_bytes)
    return "@site/_images/" + name


def norm_link(page_path, href):
    if href is None:
        return None
    href = href.strip()
    if href.startswith(("mailto:", "javascript:", "data:")):
        return href
    if href.startswith("#"):
        return href
    absu = urljoin(BASE + page_path, href)
    u, frag = urldefrag(absu)
    if u.startswith("http://doc.zh-jieli.com/"):
        u = "https://" + u[len("http://"):]
    if u.startswith(BASE):
        rel = unquote(u[len(BASE):]) or "index.html"
        if rel.endswith("/"):
            rel += "index.html"
        if rel == page_path:
            return "#" + frag if frag else "#"
        if rel in page_paths:
            return "@site/" + rel + ("#" + frag if frag else "")
        if rel in ("genindex.html", "search.html"):
            return "@site/search.html"
        return absu  # unknown doc page: keep online link
    return absu


def fix_odd_tags(body):
    """Raw '<dev name>' style placeholders that the original site parsed as HTML tags."""
    for p in body.find_all("p"):
        if p.find("dev") and "isd_download.exe isd_config.ini -package-only" in p.get_text():
            prefix = p.get_text().split("`")[0]
            p.clear()
            p.append(NavigableString(prefix))
            code = Tag(name="code", attrs={"class": ["docutils", "literal", "notranslate"]})
            cmd = "isd_download.exe isd_config.ini -package-only -dev <dev name> -key <your key file> -output-fw <output fw file>"
            for i, tok in enumerate(cmd.split(" ")):
                if i:
                    code.append(NavigableString(" "))
                sp = Tag(name="span", attrs={"class": ["pre"]})
                sp.string = tok
                code.append(sp)
            p.append(code)


def process(path, info):
    soup = BeautifulSoup(info["html"], "lxml")
    title = soup.title.get_text().split(" — ")[0].strip()
    menu = soup.select_one("div.wy-menu.wy-menu-vertical")
    crumbs = soup.select_one("ul.wy-breadcrumbs")
    body = soup.select_one('div[itemprop="articleBody"]')
    footer = soup.select_one("div.rst-footer-buttons")
    lastup = soup.select_one("span.lastupdated")

    # ---- body
    fix_odd_tags(body)
    for el in body.find_all(["script", "style"]):
        el.decompose()
    for img in body.find_all("img"):
        src = img.get("src", "")
        if "_files/" in src and path == "index.html":
            fp = os.path.join(HOME_FILES, unquote(src.split("_files/")[-1]))
            site = stage_image(BASE + "_images/" + os.path.basename(fp), open(fp, "rb").read())
        else:
            absu = urljoin(BASE + path, src)
            site = stage_image(absu)
            if site is None:
                missing_images.setdefault(absu, []).append(path)
                site = absu
        img["src"] = site
        for a in ("srcset", "loading"):
            if a in img.attrs:
                del img[a]
    for a in body.find_all("a"):
        if a.has_attr("href"):
            a["href"] = norm_link(path, a["href"])
        if "style" in a.attrs and "cursor" in a["style"]:
            del a["style"]
    for el in body.find_all(True):
        for att in ("aria-expanded",):
            if att in el.attrs:
                del el[att]
    # ---- menu
    for b in menu.select("button.toctree-expand"):
        b.decompose()
    for el in menu.find_all(True):
        for att in ("aria-expanded", "data-spy", "style"):
            if att in el.attrs:
                del el[att]
        if el.name == "ul" and el.get("class") == []:
            del el["class"]
    for a in menu.find_all("a"):
        a["href"] = norm_link(path, a.get("href"))
    # ---- breadcrumbs
    crumb_list = []
    for li in crumbs.find_all("li", recursive=False):
        if "wy-breadcrumbs-aside" in (li.get("class") or []):
            continue
        a = li.find("a")
        if a is not None and "icon-home" in (a.get("class") or []):
            continue
        if a is not None:
            crumb_list.append({"href": norm_link(path, a["href"]), "html": a.decode_contents()})
        else:
            crumb_list.append({"href": None, "html": li.decode_contents().replace("»", "").strip()})
    # ---- prev / next
    nav = {}
    if footer:
        for a in footer.find_all("a"):
            rel = a.get("rel")
            rel = rel[0] if isinstance(rel, list) else rel
            nav[rel] = {"href": norm_link(path, a["href"]), "title": a.get("title", "")}
    return {
        "path": path,
        "title": title,
        "source": info["source"],
        "archived": info["archived"],
        "menu": menu.decode_contents().strip(),
        "crumbs": crumb_list,
        "body": body.decode_contents().strip(),
        "prev": nav.get("prev"),
        "next": nav.get("next"),
        "lastupdated": re.sub(r"\s+", " ", lastup.get_text()).strip() if lastup else "",
    }


ir = {}
for path in sorted(pages):
    ir[path] = process(path, pages[path])
json.dump(ir, open(IR_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# report
print("pages:", len(ir))
print("images staged:", len(image_hashes))
print("missing images:", len(missing_images))
for u, ps in sorted(missing_images.items()):
    print("  ", u, "<-", ps[:3])
ext = set()
for p in ir.values():
    for m in re.finditer(r'href="(https?://[^"]+)"', p["body"]):
        if "doc.zh-jieli.com" in m.group(1):
            ext.add(m.group(1))
print("doc-site links left online:", sorted(ext)[:20])
