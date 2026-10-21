const fs = require("fs");
const {
  AlignmentType, BorderStyle, Document, Footer, Header, HeadingLevel, LevelFormat,
  Packer, PageNumber, Paragraph, ShadingType, Table, TableCell, TableRow, TextRun,
  VerticalAlign, WidthType, ExternalHyperlink, ImageRun,
} = require("docx");

const FONT = "Times New Roman";
const MONO = "Consolas";
const NAVY = "000000";
const ACCENT = "000000";
const GREY = "404040";
const PAGE_W = 11906;
const MARGIN = 1134;
const CONTENT_W = PAGE_W - 2 * MARGIN;

const thin = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const cellBorders = { top: thin, bottom: thin, left: thin, right: thin };

// Inline markup: **bold**, *italic*, `code`, [[placeholder]]
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[\[[^\]]+\]\])/g;
  let last = 0;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const tok = m[0];
    if (tok.startsWith("**")) out.push(new TextRun({ ...base, text: tok.slice(2, -2), bold: true }));
    else if (tok.startsWith("`")) out.push(new TextRun({ ...base, text: tok.slice(1, -1), font: MONO, size: (base.size ?? 24) - 3 }));
    else if (tok.startsWith("[[")) out.push(new TextRun({ ...base, text: `[${tok.slice(2, -2)}]`, italics: true }));
    else out.push(new TextRun({ ...base, text: tok.slice(1, -1), italics: true }));
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}

const p = (text, opts = {}) =>
  new Paragraph({
    children: typeof text === "string" ? runs(text, opts.run) : text,
    alignment: opts.align ?? AlignmentType.JUSTIFIED,
    spacing: { after: opts.after ?? 100, before: opts.before ?? 0, line: 288 },
    indent: opts.indent,
    keepNext: opts.keepNext,
  });

const h1 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun(text)],
    keepNext: true,
  });
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)], keepNext: true });
const h3 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(text)], keepNext: true });

const bullet = (text, level = 0) =>
  new Paragraph({
    numbering: { reference: "bullets", level },
    children: runs(text),
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 60, line: 276 },
  });

let numberInstance = 0;
function numbered(items) {
  numberInstance += 1;
  return items.map(
    (text) =>
      new Paragraph({
        numbering: { reference: "numbers", level: 0, instance: numberInstance },
        children: runs(text),
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 60, line: 276 },
      }),
  );
}

const rule = () =>
  new Paragraph({
    children: [],
    spacing: { before: 60, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "BFBFBF", space: 1 } },
  });

function cell(content, width, opts = {}) {
  const paras = (Array.isArray(content) ? content : [content]).map((c) =>
    c instanceof Paragraph
      ? c
      : new Paragraph({
          children: runs(String(c), { size: opts.size ?? 20, bold: opts.bold, color: opts.color }),
          alignment: opts.align ?? AlignmentType.LEFT,
          spacing: { after: 20, line: 252 },
        }),
  );
  return new TableCell({
    children: paras,
    width: { size: width, type: WidthType.DXA },
    borders: opts.borders ?? cellBorders,
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 70, bottom: 70, left: 110, right: 110 },
    verticalAlign: opts.vAlign ?? VerticalAlign.CENTER,
    columnSpan: opts.span,
  });
}

// widths are relative weights; centered = set of column indexes to center
function table(headers, rows, weights, { centered = [], firstColBold = false } = {}) {
  const total = weights.reduce((a, b) => a + b, 0);
  const widths = weights.map((w) => Math.floor((w / total) * CONTENT_W));
  widths[widths.length - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);
  const align = (i) => (centered.includes(i) ? AlignmentType.CENTER : AlignmentType.LEFT);
  const head = new TableRow({
    tableHeader: true,
    cantSplit: true,
    children: headers.map((h, i) => cell(h, widths[i], { fill: "E7E6E6", bold: true, align: AlignmentType.CENTER })),
  });
  const body = rows.map(
    (r) =>
      new TableRow({
        cantSplit: true,
        children: r.map((c, i) => cell(c, widths[i], { align: align(i), bold: firstColBold && i === 0 })),
      }),
  );
  return [
    new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: widths, rows: [head, ...body] }),
    new Paragraph({ children: [], spacing: { after: 80 } }),
  ];
}

// Key/value info block used under the report title
function infoTable(pairs) {
  const w1 = Math.floor(CONTENT_W * 0.27);
  const w2 = CONTENT_W - w1;
  return [
    new Table({
      width: { size: CONTENT_W, type: WidthType.DXA },
      columnWidths: [w1, w2],
      rows: pairs.map(
        ([k, v]) =>
          new TableRow({
            cantSplit: true,
            children: [cell(k, w1, { bold: true }), cell(v, w2)],
          }),
      ),
    }),
    new Paragraph({ children: [], spacing: { after: 120 } }),
  ];
}

function code(lines) {
  const box = { style: BorderStyle.SINGLE, size: 4, color: "808080", space: 4 };
  return lines.map(
    (line, i) =>
      new Paragraph({
        children: [new TextRun({ text: line.length ? line : " ", font: MONO, size: 17 })],
        border: {
          left: box,
          right: box,
          top: i === 0 ? box : undefined,
          bottom: i === lines.length - 1 ? box : undefined,
        },
        spacing: { after: i === lines.length - 1 ? 140 : 0, line: 240 },
        keepLines: true,
        keepNext: i < lines.length - 1,
      }),
  );
}

// Dashed frame where a screenshot or diagram should be pasted
function figureSlot(caption, hint, height = 2600) {
  const dash = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
  return [
    new Table({
      width: { size: CONTENT_W, type: WidthType.DXA },
      columnWidths: [CONTENT_W],
      rows: [
        new TableRow({
          height: { value: height, rule: "atLeast" },
          cantSplit: true,
          children: [
            cell(
              [
                new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "[Insert screenshot]", color: "808080", size: 22 })],
                }),
                new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: hint, color: GREY, italics: true, size: 18 })],
                }),
              ],
              CONTENT_W,
              { borders: { top: dash, bottom: dash, left: dash, right: dash } },
            ),
          ],
        }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 60, after: 180 },
      children: [new TextRun({ text: caption, italics: true, size: 19, color: GREY })],
    }),
  ];
}

// Row of images side by side, each with a short label underneath, then one caption
function imageRow(items, caption) {
  const colW = Math.floor(CONTENT_W / items.length);
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const noBorders = { top: none, bottom: none, left: none, right: none };
  const imgW = Math.floor((colW / 1440) * 96) - 14;
  const plainCell = (children) =>
    new TableCell({
      width: { size: colW, type: WidthType.DXA },
      borders: noBorders,
      margins: { top: 40, bottom: 40, left: 60, right: 60 },
      verticalAlign: VerticalAlign.TOP,
      children,
    });
  const labels = items.map(({ label }) =>
    plainCell([
      new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, children: [new TextRun({ text: label, size: 19, bold: true })] }),
    ]),
  );
  const images = items.map(({ path, label }) => {
    const { width, height } = pngSize(path);
    return plainCell([
      new Paragraph({
        alignment: AlignmentType.CENTER,
        keepNext: true,
        children: [
          new ImageRun({
            type: "png",
            data: fs.readFileSync(path),
            transformation: { width: imgW, height: Math.round((imgW * height) / width) },
            altText: { title: label, description: label, name: label },
          }),
        ],
      }),
    ]);
  });
  return [
    new Table({
      width: { size: colW * items.length, type: WidthType.DXA },
      columnWidths: items.map(() => colW),
      rows: [
        new TableRow({ cantSplit: true, children: labels }),
        new TableRow({ cantSplit: true, children: images }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 60, after: 180 },
      children: [new TextRun({ text: caption, italics: true, size: 19, color: GREY })],
    }),
  ];
}

function pngSize(path) {
  const buf = fs.readFileSync(path);
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

function link(label, url) {
  return new ExternalHyperlink({ link: url, children: [new TextRun({ text: label, style: "Hyperlink" })] });
}

function titleBlock(kicker, title, subtitle) {
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 40 },
      children: [new TextRun({ text: "VIETNAM–KOREA UNIVERSITY OF INFORMATION AND COMMUNICATION TECHNOLOGY (VKU)", size: 20, bold: true, color: GREY })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
      children: [new TextRun({ text: "Faculty of Computer Science", size: 20, color: GREY })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 60 },
      children: [new TextRun({ text: kicker.toUpperCase(), size: 24, bold: true })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 60 },
      children: [new TextRun({ text: title, size: 32, bold: true })],
    }),
    ...subtitle.split("\n").map(
      (line, i, all) =>
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: i === all.length - 1 ? 220 : 20 },
          children: [new TextRun({ text: line, size: 24, italics: true })],
        }),
    ),
  ];
}

async function build(file, headerText, children) {
  const doc = new Document({
    creator: "Ngon Sac Viet Team",
    title: headerText,
    styles: {
      default: { document: { run: { font: FONT, size: 24 } } },
      paragraphStyles: [
        {
          id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 28, bold: true, color: NAVY, font: FONT },
          paragraph: { spacing: { before: 300, after: 140 }, outlineLevel: 0 },
        },
        {
          id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 25, bold: true, color: ACCENT, font: FONT },
          paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 },
        },
        {
          id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, italics: true, color: NAVY, font: FONT },
          paragraph: { spacing: { before: 140, after: 80 }, outlineLevel: 2 },
        },
      ],
    },
    numbering: {
      config: [
        {
          reference: "bullets",
          levels: [
            { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } },
            { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1000, hanging: 270 } } } },
          ],
        },
        {
          reference: "numbers",
          levels: [
            { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 320 } } } },
          ],
        },
      ],
    },
    sections: [
      {
        properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: 1134, bottom: 1134, left: MARGIN, right: MARGIN } } },
        headers: {
          default: new Header({
            children: [
              new Paragraph({
                alignment: AlignmentType.RIGHT,
                border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF", space: 2 } },
                children: [new TextRun({ text: headerText, size: 17, color: GREY, italics: true })],
              }),
            ],
          }),
        },
        footers: {
          default: new Footer({
            children: [
              new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "Page ", size: 17, color: GREY }),
                  new TextRun({ children: [PageNumber.CURRENT], size: 17, color: GREY }),
                  new TextRun({ text: " of ", size: 17, color: GREY }),
                  new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 17, color: GREY }),
                ],
              }),
            ],
          }),
        },
        children,
      },
    ],
  });
  fs.writeFileSync(file, await Packer.toBuffer(doc));
  console.log("wrote", file);
}

module.exports = {
  AlignmentType, Paragraph, TextRun, runs, p, h1, h2, h3, bullet, numbered, rule, table, infoTable,
  code, figureSlot, imageRow, link, titleBlock, build, NAVY, ACCENT, GREY,
};
