# Regulotype notes

A small static research notebook. Markdown is the source of truth; `build.py` renders it into `docs/`. No web framework, JavaScript package manager, remote service, or publishing step is involved.

## Setup, build, and preview

Requires Python 3.9 or newer and **Python-Markdown**. The figure script uses only Python's standard library. No Word conversion, math-rendering, or plotting package is required to build the site.

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Open <http://127.0.0.1:8000/>. Stop the server with Ctrl+C. After editing, run `python3 build.py` again and refresh the browser; there is no file watcher. If port 8000 is occupied, choose another port.

A project-local `.venv` has already been prepared in this workspace. Without activating it, use:

```bash
.venv/bin/python build.py
.venv/bin/python -m http.server 8000 --bind 127.0.0.1 --directory docs
```

## Layout

```text
regulotype-notes/
├── README.md
├── build.py
├── site.json
├── requirements.txt
├── .gitignore
├── notes/
│   └── 2026-09-12-conceptual-landscape.md
├── figures/
│   └── notes_regulotypes_conceptual_landscape.py
├── static/
│   ├── css/{main,notes,widgets}.css
│   ├── js/{notes,widgets}.js
│   ├── fonts/Excalifont-Regular.woff2
│   └── images/favicon.svg
├── templates/
│   ├── base.html
│   ├── note.html
│   └── index.html
├── source/
│   ├── README.md
│   └── archive/
│       ├── Regulotype Related Model & Concepts.docx
│       ├── figure7.html
│       └── notes_regulotypes_conceptual_landscape.py
└── docs/                         # generated; never edit
    ├── index.html
    ├── notes/2026-09-12-conceptual-landscape.html
    ├── css/
    ├── js/
    ├── fonts/
    ├── images/
    ├── .nojekyll
    └── .generated-by-build
```

- `build.py`: reads metadata and Markdown, inserts generated figures, renders templates, and rebuilds `docs/`. It resolves its own directory, so it also works when invoked from elsewhere. Rendering completes before old generated output is removed. An unrecognized `docs/` directory is protected from replacement.
- `site.json`: website title and homepage description.
- `notes/`: all research prose, tables, equations, references, and figure captions. This is the editing location.
- `figures/`: importable Python figure generators. Figure 7 returns SVG directly; the build inserts it inline without an iframe or standalone preview page.
- `static/css/main.css`: body typography, site header, and index layout. `notes.css`: article, contents, tables, equations, references, and print styling. `widgets.css`: Excalifont, figure palette, and animation primitives.
- `static/js/notes.js`: indicates when tables can scroll horizontally. `widgets.js`: plays figures on first entry into view and restarts them from Replay. Figures remain visible without JavaScript and with reduced motion.
- `templates/base.html`: shared HTML shell. `note.html`: note header, contents navigation, and article. `index.html`: homepage listing. Templates use Python `string.Template` placeholders such as `${title}`; use `$$` for a literal dollar sign in template files.
- `source/`: preserved inputs and migration provenance; excluded from the generated site. The external originals and older files in the parent project remain in place.
- `docs/`: disposable build output, ignored by Git. Only generated HTML and static assets belong here. `.nojekyll` makes the static output compatible with a possible future GitHub Pages setup; this project does not configure or publish one.

## Add another research note

Create `notes/YYYY-MM-DD-lowercase-slug.md`, for example a mathematical formulation, simulation design, identifiability, or evaluation note:

```markdown
---
title: Mathematical formulation
date: 2026-09-13
summary: Working formulation and assumptions.
---

## Overview

Write the research content here.
```

Run the build; the new page appears on the homepage automatically. The filename determines `docs/notes/YYYY-MM-DD-lowercase-slug.html`. Notes are listed newest first. Metadata uses simple unquoted `key: value` lines, not full YAML. `title` is required; `date` defaults to the filename and `summary` is optional. The note template supplies the page's H1, so start content at `##`.

Standard Markdown, pipe tables, fenced code blocks, and raw HTML are supported. Native MathML preserves the converted equations without a CDN or runtime dependency. Existing equations can be edited directly in Markdown; LaTeX delimiters are not processed. Inline HTML such as `<sub>` and `<sup>` also works. Notes are trusted project source, not a renderer for untrusted submissions.

## Figures and assets

Use `<!-- figure:conceptual-landscape -->` on its own line to insert Figure 7. Its caption is authored alongside that marker in the note. For a new generated figure, add an import and a name/function pair to `FIGURES` in `build.py`; each function should return an HTML/SVG fragment without file-writing side effects.

Static images go in `static/images/`. From a note, use `![Description](../images/example.png)`. Pages use relative links, so the site can later be served from a project subdirectory. Static assets are copied to the root of `docs/`.

To inspect the figure markup alone:

```bash
python3 figures/notes_regulotypes_conceptual_landscape.py
```

The SVG, typography, references, and equations work offline after the build. External reference links naturally require internet access. Wide comparison tables and Figure 7 scroll within their own regions on narrow screens.

See [source/README.md](source/README.md) for content conversion details and original visual-style attribution.
