# How the offline Jieli Tools docs were built

These scripts turned the saved `.mhtml` pages in the five folders next to this one into two browsable
sites:

* `JL_Tools_Docs_zh` — the Chinese original as an offline site
* `JL_Tools_Docs_en` — the same site with an English translation

You only need this folder if you want to regenerate the sites, for example after saving more pages.
It is safe to delete.

## Requirements

Python 3 with `beautifulsoup4` and `lxml`:

```
python -m pip install beautifulsoup4 lxml
```

## Rebuild

Run these commands from this folder:

```
python prepare.py        # read the .mhtml pages + wayback/ pages, write ir.json and stage/_images
python render.py zh      # write ..\JL_Tools_Docs_zh
python render.py en      # write ..\JL_Tools_Docs_en, using the translations in tr\out and tr\prefill
python linkcheck.py ..\JL_Tools_Docs_zh
python linkcheck.py ..\JL_Tools_Docs_en
python audit_en.py       # list any Chinese left outside "label (中文)" brackets in the English site
```

The paths to the source folders and output folders are set at the top of `corpus.py` and `render.py`
(`ROOT = C:\AC6965E\Jieli`).

## What is where

| Path | Contents |
|---|---|
| `corpus.py`, `prepare.py` | Read the `.mhtml` files, the home page and the pages restored from the Internet Archive. Normalise links. Collect images. |
| `render.py`, `offline.css`, `offline.js` | Page template, sidebar, breadcrumbs, local search and image zoom. |
| `segment.py` | Splits page text into translation units and puts translations back without breaking the HTML. |
| `extract.py` | Builds `tr/units.json` and the translation batches `tr/batches/*.json`. |
| `tr/GUIDE.md` | Translation rules and glossary that the translators followed. |
| `tr/check.py` | Validator for a translated batch. |
| `tr/out/*.json` | Translations, one file per batch, as `{unit id: English}`. |
| `tr/prefill/*.json` | Fixed page titles and manual overrides. These take priority over `tr/out`. |
| `wayback/` | 30 pages and 66 images that were missing from the saves, restored from the Internet Archive. |
| `rtd/` | Fonts from the open-source Read the Docs theme. |

## Adding newly saved pages

1. Save the page from doc.zh-jieli.com as an `.mhtml` file into one of the five folders. Use the
   browser's "Save as… Webpage, Single File" option.
2. Run `prepare.py` and `render.py zh`.
3. For English:
   1. Run `python extract.py`. This lists the units that have no translation yet.
   2. Translate the new batch file in `tr/batches` into `tr/out/<batch>.json`.
   3. Run `python tr/check.py <batch>`.
   4. Run `render.py en`.
