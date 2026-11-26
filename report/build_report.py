"""Build the report from report/report.md.

    python report/build_report.py

Writes report/report.html and report/report.pdf (printed by headless Google Chrome) and
report/blocks.json, which report/build_docx.js turns into report/report.docx.
Supports the Markdown subset used in report.md: #/##/### headings, paragraphs, **bold**,
*italic*, `code`, nested "- " lists, "1. " lists, tables, $$ equations $$,
![caption](image){width=0.8} figures and a \\pagebreak line.
"""

from __future__ import annotations

import html
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
INLINE = re.compile(r"(\\\*|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")
FIGURE = re.compile(r"!\[(.*)\]\((.*?)\)(?:\{width=([\d.]+)\})?")


def runs(text: str) -> list[dict]:
    """Split inline Markdown into runs: {"t": text, "b": bold, "i": italic, "c": code}."""
    out = []
    for part in INLINE.split(text):
        if not part:
            continue
        if part == "\\*":
            out.append({"t": "*"})
        elif part.startswith("**"):
            out.append({"t": part[2:-2], "b": True})
        elif part.startswith("`"):
            out.append({"t": part[1:-1], "c": True})
        elif part.startswith("*") and len(part) > 2:
            out.append({"t": part[1:-1], "i": True})
        else:
            out.append({"t": part})
    return out


def png_size(path: Path) -> tuple[int, int]:
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])


def parse(md: str) -> list[dict]:
    blocks, para, lines = [], [], md.splitlines()

    def flush():
        if para:
            blocks.append({"type": "p", "runs": runs(" ".join(para))})
            para.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            flush()
        elif s == "\\pagebreak":
            flush()
            blocks.append({"type": "pagebreak"})
        elif s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            blocks.append({"type": f"h{level}", "text": s[level:].strip()})
        elif s.startswith("$$"):
            flush()
            blocks.append({"type": "eq", "text": s.strip("$ ").strip()})
        elif m := FIGURE.match(s):
            flush()
            path = (HERE / m.group(2)).resolve()
            w, h = png_size(path)
            cap = m.group(1)
            num, _, rest = cap.partition(". ")
            blocks.append(
                {
                    "type": "figure",
                    "path": str(path),
                    "w": w,
                    "h": h,
                    "width": float(m.group(3) or 0.9),
                    "label": num + ".",
                    "caption": runs(rest),
                }
            )
        elif s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append([runs(c) for c in cells])
                i += 1
            blocks.append({"type": "table", "rows": rows})
            continue
        elif re.match(r"^\s*(- |\d+\. )", line):
            flush()
            kind = "ol" if re.match(r"^\s*\d+\. ", line) else "ul"
            items = []
            while i < len(lines) and re.match(r"^\s*(- |\d+\. )", lines[i]):
                raw = lines[i]
                level = (len(raw) - len(raw.lstrip())) // 2
                text = re.sub(r"^\s*(- |\d+\. )", "", raw)
                items.append({"level": level, "runs": runs(text)})
                i += 1
            blocks.append({"type": kind, "items": items})
            continue
        else:
            para.append(s)
        i += 1
    flush()
    return blocks


def html_runs(rs: list[dict]) -> str:
    out = []
    for r in rs:
        t = html.escape(r["t"])
        if r.get("c"):
            t = f"<code>{t}</code>"
        if r.get("b"):
            t = f"<strong>{t}</strong>"
        if r.get("i"):
            t = f"<em>{t}</em>"
        out.append(t)
    return "".join(out)


def html_list(b: dict) -> str:
    tag = b["type"]
    out, depth = [], -1
    for it in b["items"]:
        while depth < it["level"]:
            out.append(f"<{tag}>")
            depth += 1
        while depth > it["level"]:
            out.append(f"</{tag}>")
            depth -= 1
        out.append(f"<li>{html_runs(it['runs'])}</li>")
    out += [f"</{tag}>"] * (depth + 1)
    return "".join(out)


CSS = """
@page { size: A4; margin: 2.2cm 2.2cm 2.4cm;
        @bottom-center { content: counter(page); font: 9pt Georgia, serif; color: #666; } }
body { font: 11pt/1.45 Georgia, 'Times New Roman', serif; color: #191919; }
h1 { font: bold 20pt/1.2 Helvetica, Arial, sans-serif; margin: 0 0 6pt; }
h2 { font: bold 14pt Helvetica, Arial, sans-serif; margin: 18pt 0 6pt; break-after: avoid; }
h3 { font: bold 11.5pt Helvetica, Arial, sans-serif; margin: 12pt 0 4pt; break-after: avoid; }
p { margin: 0 0 7pt; text-align: justify; }
ul, ol { margin: 0 0 7pt; padding-left: 20pt; } li { margin-bottom: 2pt; }
.meta { color: #555; font-size: 10pt; text-align: left; }
.eq { text-align: center; font-style: italic; font-size: 11.5pt; margin: 6pt 0 9pt; }
figure { margin: 10pt auto 12pt; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; }
figcaption { font-size: 9pt; color: #444; text-align: left; margin-top: 4pt; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 6pt 0 10pt;
        break-inside: avoid; }
th, td { border: 0.5pt solid #bbb; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #eef2f7; }
code { font: 9.5pt Menlo, monospace; }
.pb { break-after: page; }
"""


def to_html(blocks: list[dict]) -> str:
    body, seen_h1 = [], False
    for k, b in enumerate(blocks):
        t = b["type"]
        if t == "h1":
            body.append(f"<h1>{html.escape(b['text'])}</h1>")
            seen_h1 = True
        elif t in ("h2", "h3"):
            body.append(f"<{t}>{html.escape(b['text'])}</{t}>")
        elif t == "p":
            meta = seen_h1 and k <= 2
            body.append(f"<p{' class=meta' if meta else ''}>{html_runs(b['runs'])}</p>")
        elif t in ("ul", "ol"):
            body.append(html_list(b))
        elif t == "eq":
            body.append(f"<div class=eq>{html.escape(b['text'])}</div>")
        elif t == "figure":
            body.append(
                f"<figure><img src='file://{b['path']}' style='width:{b['width'] * 100:.0f}%'>"
                f"<figcaption><strong>{html.escape(b['label'])}</strong> "
                f"{html_runs(b['caption'])}</figcaption></figure>"
            )
        elif t == "table":
            head, *rows = b["rows"]
            th = "".join(f"<th>{html_runs(c)}</th>" for c in head)
            tr = "".join(
                "<tr>" + "".join(f"<td>{html_runs(c)}</td>" for c in r) + "</tr>" for r in rows
            )
            body.append(f"<table><tr>{th}</tr>{tr}</table>")
        elif t == "pagebreak":
            body.append("<div class=pb></div>")
    return (
        f"<!doctype html><html><head><meta charset=utf-8><title>Does Forgiveness Pay?"
        f"</title><style>{CSS}</style></head><body>{''.join(body)}</body></html>"
    )


if __name__ == "__main__":
    blocks = parse((HERE / "report.md").read_text())
    (HERE / "blocks.json").write_text(json.dumps(blocks, ensure_ascii=False))
    (HERE / "report.html").write_text(to_html(blocks))
    subprocess.run(
        [
            CHROME,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--allow-file-access-from-files",
            f"--print-to-pdf={HERE / 'report.pdf'}",
            f"file://{HERE / 'report.html'}",
        ],
        check=True,
        capture_output=True,
    )
    print(f"wrote report.html, report.pdf, blocks.json ({len(blocks)} blocks)", file=sys.stderr)
