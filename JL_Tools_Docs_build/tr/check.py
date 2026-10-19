"""Validate a translated batch:  python tr/check.py b07"""
import json, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
FULLWIDTH = re.compile(r"[　-〿！-｠]")
TOKEN = re.compile(r"⟦/?\d+/?⟧")
TOK_PARTS = re.compile(r"⟦(/?)(\d+)(/?)⟧")


def strip_parens(s):
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\([^()]*\)", "", s)
        s = re.sub(r"（[^（）]*）", "", s)
    return s


def nesting_ok(s):
    stack = []
    for m in TOK_PARTS.finditer(s):
        close, n, void = m.groups()
        if void:
            continue
        if close:
            if not stack or stack[-1] != n:
                return False
            stack.pop()
        else:
            stack.append(n)
    return not stack


def main(batch):
    inp = json.load(open(os.path.join(HERE, "batches", batch + ".json"), encoding="utf-8"))
    units = [u for g in inp["pages"] for u in g["units"]]
    out_p = os.path.join(HERE, "out", batch + ".json")
    try:
        out = json.load(open(out_p, encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: {out_p} does not exist")
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {out_p}: {e}")
        return 1
    errors, warns = [], []
    ids = {u["id"] for u in units}
    for k in out:
        if k not in ids:
            warns.append(f"{k}: id is not part of this batch (ignored)")
    for u in units:
        uid, zh, role = u["id"], u["zh"], u.get("role", "")
        en = out.get(uid)
        if en is None:
            errors.append(f"{uid}: missing translation")
            continue
        if not isinstance(en, str) or not en.strip():
            errors.append(f"{uid}: empty translation")
            continue
        if Counter(TOKEN.findall(zh)) != Counter(TOKEN.findall(en)):
            errors.append(f"{uid}: placeholders differ: zh {sorted(TOKEN.findall(zh))} vs en {sorted(TOKEN.findall(en))}")
        elif not nesting_ok(en):
            errors.append(f"{uid}: placeholders not properly nested: {en[:120]}")
        if role == "code":
            zl, el = zh.split("\n"), en.split("\n")
            if len(zl) != len(el):
                errors.append(f"{uid}: code unit must keep the same number of lines ({len(zl)} vs {len(el)})")
            else:
                for a, b in zip(zl, el):
                    if not HAN.search(a) and not FULLWIDTH.search(a) and a != b:
                        errors.append(f"{uid}: code line without Chinese was changed: {a!r} -> {b!r}")
                        break
            pz = re.match(r"^[\s#/;*]*", zh).group(0)
            pe = re.match(r"^[\s#/;*]*", en).group(0)
            if pz != pe:
                warns.append(f"{uid}: code prefix changed {pz!r} -> {pe!r}")
            if en == zh and HAN.search(zh):
                warns.append(f"{uid}: code unit left unchanged (ok only if it is a real file name / literal): {zh[:60]!r}")
        else:
            if en.strip() == zh.strip() and HAN.search(zh):
                errors.append(f"{uid}: not translated: {zh[:60]!r}")
            if role.startswith("h") and len(role) == 2 and HAN.search(en):
                errors.append(f"{uid}: Chinese is not allowed in headings: {en[:80]!r}")
            rest = strip_parens(TOKEN.sub("", en))
            if HAN.search(rest):
                warns.append(f"{uid}: Chinese outside parentheses (ok only for real file names): {en[:100]!r}")
            if FULLWIDTH.search(rest):
                warns.append(f"{uid}: full-width punctuation left: {en[:100]!r}")
            plain_zh = TOKEN.sub(" ", zh)
            for tok in set(re.findall(r"[A-Za-z0-9_./\\:+\-]*[A-Za-z_][A-Za-z0-9_./\\:+\-]*", plain_zh)):
                tok = tok.strip(".:-")
                if len(tok) >= 3 and re.search(r"[\d_.]", tok) and tok not in en:
                    warns.append(f"{uid}: token {tok!r} from the source is missing")
            han = len(HAN.findall(zh))
            if han >= 12 and len(TOKEN.sub("", en)) < han:
                warns.append(f"{uid}: translation looks too short ({han} Chinese chars -> {len(en)} chars)")
    for e in errors:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
    print(f"{batch}: {len(units)} units, {len(out)} translations, {len(errors)} errors, {len(warns)} warnings"
          + (" -> OK" if not errors else " -> FIX THE ERRORS"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
