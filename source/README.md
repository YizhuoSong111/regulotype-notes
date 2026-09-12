# Original source material

`archive/` contains unmodified copies of the supplied Word document, Figure 7 HTML preview, and latest Python script from `/Users/yizhuosong/Desktop/Regulotype Related Methods/`. All files at that original location and the older materials in the parent project remain untouched.

The active website reads `notes/`, `figures/`, `static/`, and `templates/` only. Nothing under `source/` is included in `docs/`.

Migration notes:

- Both tables retain every populated row: five methods in Table 1 and seven in Table 2. The empty final row in Table 1 was omitted.
- All 21 Word equations were converted to native MathML, including the annotated arrows, delimiters, subscripts, superscripts, and Symbol-font arrows.
- The eight numbered references retain the document's wording, evidence notes, and source URLs. Citation numbers now link to the reference entries.
- The overview, conceptual landscape, and axis interpretation were assembled from the figure script's existing caption, accessibility description, and method descriptions, plus the SURGE comparison in Table 2. No literature re-evaluation or new scientific claims were added.
- Four additional source links (scDALI, PICALO, CellCap, contrastiveVI) came from comments in the supplied figure script. Their bibliographic details were not invented.
- Method/author line breaks and spacing around equations were normalized. Scientific wording and preprint qualifiers were retained, including the source's GEDI specialization caveat.
- The active figure script retains the original geometry, labels, method descriptions, colors, and timing. Its caption now lives in Markdown; styles and replay behavior live in `static/`. Its former standalone preview CLI remains available in the archived script.

The organization follows the source/output pattern in [Kaiqian Zhang's repository](https://github.com/kaiqianzhang/kaiqianzhang.github.io). The supplied Figure 7 code already credits its visual style sources; these comments are retained. The local Excalifont file is copied unchanged from the supplied asset.
