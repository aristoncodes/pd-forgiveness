// Build report/report.docx from report/blocks.json (written by report/build_report.py).
//
//   python report/build_report.py      # report.md -> blocks.json, report.html, report.pdf
//   npm install docx                   # once (any folder on NODE_PATH works)
//   node report/build_docx.js
//
// A4, Georgia 11 pt body, Arial headings, page numbers in the footer.
const fs = require("fs");
const path = require("path");
const {
  AlignmentType, BorderStyle, Document, Footer, HeadingLevel, ImageRun, LevelFormat, Packer,
  PageBreak, PageNumber, Paragraph, ShadingType, Table, TableCell, TableRow, TextRun, WidthType,
} = require("docx");

const HERE = __dirname;
const blocks = JSON.parse(fs.readFileSync(path.join(HERE, "blocks.json"), "utf8"));
const TEXT_WIDTH_DXA = 9412; // A4 (11906) minus 2 × 1247 (2.2 cm) margins
const TEXT_WIDTH_PX = 627; // the same width at 96 px per inch
const BODY = "Georgia";
const HEAD = "Arial";

function runs(rs, extra = {}) {
  return rs.map((r) => new TextRun({
    text: r.t, bold: r.b || extra.bold, italics: r.i || extra.italics,
    font: r.c ? "Menlo" : extra.font, size: r.c ? 19 : extra.size, color: extra.color,
  }));
}

function table(rows) {
  const n = rows[0].length;
  const len = (cell) => cell.map((r) => r.t).join("").length;
  const weight = [...Array(n).keys()].map((j) =>
    Math.max(6, Math.min(60, Math.max(...rows.map((row) => len(row[j] || []))))));
  const total = weight.reduce((a, b) => a + b, 0);
  const widths = weight.map((w) => Math.floor((w / total) * TEXT_WIDTH_DXA));
  widths[n - 1] += TEXT_WIDTH_DXA - widths.reduce((a, b) => a + b, 0);
  const border = { style: BorderStyle.SINGLE, size: 4, color: "BBBBBB" };
  const borders = { top: border, bottom: border, left: border, right: border };
  return new Table({
    width: { size: TEXT_WIDTH_DXA, type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((row, i) => new TableRow({
      tableHeader: i === 0,
      cantSplit: true,
      children: row.map((cell, j) => new TableCell({
        width: { size: widths[j], type: WidthType.DXA },
        borders,
        margins: { top: 40, bottom: 40, left: 80, right: 80 },
        shading: i === 0 ? { type: ShadingType.CLEAR, color: "auto", fill: "EEF2F7" } : undefined,
        children: [new Paragraph({ children: runs(cell, { size: 18, bold: i === 0 }) })],
      })),
    })),
  });
}

const children = [];
let seenTitle = false;
blocks.forEach((b, k) => {
  switch (b.type) {
    case "h1":
      children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun(b.text)] }));
      seenTitle = true;
      break;
    case "h2":
      children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(b.text)] }));
      break;
    case "h3":
      children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(b.text)] }));
      break;
    case "p": {
      const meta = seenTitle && k <= 2;
      children.push(new Paragraph({
        alignment: meta ? AlignmentType.LEFT : AlignmentType.JUSTIFIED,
        spacing: { after: 140 },
        children: runs(b.runs, meta ? { size: 20, color: "555555" } : {}),
      }));
      break;
    }
    case "ul":
    case "ol":
      b.items.forEach((it) => children.push(new Paragraph({
        numbering: { reference: b.type === "ul" ? "bullets" : `numbers-${k}`, level: it.level },
        spacing: { after: 60 },
        children: runs(it.runs),
      })));
      break;
    case "eq":
      children.push(new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 100, after: 160 },
        children: [new TextRun({ text: b.text, italics: true, font: "Cambria Math", size: 23 })],
      }));
      break;
    case "figure": {
      const w = Math.round(TEXT_WIDTH_PX * b.width);
      children.push(new Paragraph({
        alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 160, after: 60 },
        children: [new ImageRun({
          type: "png", data: fs.readFileSync(b.path),
          transformation: { width: w, height: Math.round((w * b.h) / b.w) },
          altText: { title: b.label, description: b.caption.map((r) => r.t).join(""), name: b.label },
        })],
      }));
      children.push(new Paragraph({
        spacing: { after: 220 },
        children: [new TextRun({ text: `${b.label} `, bold: true, size: 18, color: "444444" }),
          ...runs(b.caption, { size: 18, color: "444444" })],
      }));
      break;
    }
    case "table":
      children.push(table(b.rows));
      children.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      break;
    case "pagebreak":
      children.push(new Paragraph({ children: [new PageBreak()] }));
      break;
  }
});

const numberedLists = blocks.map((b, k) => [b, k]).filter(([b]) => b.type === "ol");
const level = (i, format, text) => ({
  level: i, format, text, alignment: AlignmentType.LEFT,
  style: { paragraph: { indent: { left: 400 + 360 * i, hanging: 300 } } },
});
const heading = (size, before, after) => ({
  run: { font: HEAD, size, bold: true, color: "191919" },
  paragraph: { spacing: { before, after }, keepNext: true, keepLines: true },
});

const doc = new Document({
  creator: "pd-forgiveness",
  title: "Does Forgiveness Pay?",
  styles: {
    default: { document: { run: { font: BODY, size: 22 }, paragraph: { spacing: { line: 300 } } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", ...heading(40, 0, 120) },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        ...heading(28, 320, 120), paragraph: { spacing: { before: 320, after: 120 }, keepNext: true, keepLines: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        ...heading(23, 220, 80), paragraph: { spacing: { before: 220, after: 80 }, keepNext: true, keepLines: true, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [level(0, LevelFormat.BULLET, "•"), level(1, LevelFormat.BULLET, "–")] },
      ...numberedLists.map(([, k]) => ({
        reference: `numbers-${k}`,
        levels: [level(0, LevelFormat.DECIMAL, "%1."), level(1, LevelFormat.LOWER_LETTER, "%2.")],
      })),
    ],
  },
  sections: [{
    properties: {
      page: { size: { width: 11906, height: 16838 },
              margin: { top: 1247, bottom: 1361, left: 1247, right: 1247 } },
    },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "666666" })],
    })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(path.join(HERE, "report.docx"), buf);
  console.log(`wrote report.docx (${children.length} elements)`);
});
