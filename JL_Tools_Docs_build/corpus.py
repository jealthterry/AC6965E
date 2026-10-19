"""Load every source page (MHTML saves, archived pages, saved home page) and their resources."""
import email, glob, gzip, json, os, re
from email import policy

ROOT = r"C:\AC6965E\Jieli"
SCRATCH = os.path.dirname(os.path.abspath(__file__))
BASE = "https://doc.zh-jieli.com/Tools/zh-cn/"
HOME_HTML = os.path.join(ROOT, "程序开发相关工具", "欢迎使用杰理工具文档 — JL Project Documentation.html")
HOME_FILES = os.path.join(ROOT, "程序开发相关工具", "欢迎使用杰理工具文档 — JL Project Documentation_files")
WB_DIR = os.path.join(SCRATCH, "wayback")


def load_mhtml(path):
    with open(path, "rb") as fh:
        msg = email.message_from_binary_file(fh, policy=policy.default)
    parts = [p for p in msg.walk() if not p.is_multipart()]
    html = parts[0].get_payload(decode=True).decode("utf-8")
    url = parts[0]["Content-Location"]
    res = {}
    for p in parts[1:]:
        res[p["Content-Location"]] = (p.get_content_type(), p.get_payload(decode=True))
    return url, html, res


def load_all():
    """Returns pages: {path: dict(html, source, file, archived)} and resources: {url: (ctype, bytes)}."""
    pages, resources = {}, {}
    for f in sorted(glob.glob(os.path.join(ROOT, "*", "*.mhtml"))):
        url, html, res = load_mhtml(f)
        assert url.startswith(BASE), url
        path = url[len(BASE):]
        pages[path] = dict(html=html, source="mhtml", file=f, archived=None)
        for k, v in res.items():
            if not k.startswith("cid:"):
                resources.setdefault(k, v)
    meta = json.load(open(os.path.join(WB_DIR, "meta.json")))
    for path, ts in meta.items():
        f = os.path.join(WB_DIR, "pages", path)
        html = open(f, encoding="utf-8").read()
        pages[path] = dict(html=html, source="wayback", file=f, archived=ts)
    pages["index.html"] = dict(html=open(HOME_HTML, encoding="utf-8").read(), source="home", file=HOME_HTML, archived=None)
    # archived images
    img_meta_p = os.path.join(WB_DIR, "images.json")
    if os.path.exists(img_meta_p):
        for rel, info in json.load(open(img_meta_p)).items():
            fp = os.path.join(WB_DIR, "images", rel)
            if os.path.exists(fp):
                ctype = "image/png" if rel.lower().endswith(".png") else "image/jpeg"
                resources.setdefault(BASE + rel, (ctype, open(fp, "rb").read()))
    return pages, resources
