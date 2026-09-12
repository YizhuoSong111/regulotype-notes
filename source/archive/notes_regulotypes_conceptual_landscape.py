"""Generate Figure 7: the conceptual territory around regulotypes.

Python's standard library only; SVG is constructed directly as in
notes_regulotypes_overview_contribute.py. S(), txt(), and REPLAY retain that
script's interface and markup. The reference is deliberately not imported:
it calls main() on import and rewrites the original note.

Usage:
    python3 notes_regulotypes_conceptual_landscape.py
    python3 notes_regulotypes_conceptual_landscape.py --output figure7.html
    python3 notes_regulotypes_conceptual_landscape.py --preview preview.html

figure7() returns an inline snippet for the existing notes site, whose
widgets.css, notes.css, and widgets.js supply its fonts, palette, and replay
driver. --preview wraps the same snippet in a self-contained HTML page with
the corresponding figure styles and animation driver. An optional --font
WOFF2 embeds the site's Excalifont in that preview; otherwise the original
font stack falls back to an installed hand-drawn face.

This script never reads or modifies a Markdown note. Insert the snippet
after Figure 6 when integrating it into the site.

Style sources, inspected 2026-09-11:
https://github.com/kaiqianzhang/kaiqianzhang.github.io/blob/main/figures/notes_regulotypes_overview_contribute.py
https://kaiqianzhang.github.io/css/widgets.css
https://kaiqianzhang.github.io/css/notes.css
https://kaiqianzhang.github.io/js/widgets.js
"""

import argparse
import base64
from html import escape
from math import hypot
from pathlib import Path


TEACHER='var(--n-teacher)'; STUDENT='var(--n-student)'; DATA='var(--n-data)'
KEPT='var(--n-kept)'; LOSS='var(--n-loss)'; PRUNED='var(--n-pruned)'
DIM='var(--n-dim)'; EDGE='var(--n-edge)'

# Editable prose; the Figure 7 label is added separately in figure7().
CAPTION = (
    "Conceptual territory around regulotypes. CellRegMap, scDALI and GASPACHO "
    "model genetic or allelic variation in cellular context; scooby predicts "
    "variant effects conditional on a cell embedding. SURGE and PICALO learn "
    "contexts from genetic interactions (PICALO: bulk data), while LIVI "
    "projects inherited effects onto cells and programs. From general "
    "perturbations, CellCap learns shared response programs, GEDI models "
    "covariate-dependent shifts, and MrVI, LEMUR and contrastiveVI expose "
    "response-related cellular structure. Regulotypes propose learning and "
    "validating a shared cross-locus cis-response profile as a cellular "
    "representation. Directions overlap; proximity is not a performance "
    "ranking or evidence of an unoccupied niche. Experimental gene "
    "perturbations belong to the lower, non-inherited side. Positions are "
    "conceptual rather than quantitative."
)

ARIA_LABEL = (
    "Conceptual map of methods around Regulotype. From left to right: state "
    "defines response, then response defines representation. From bottom to "
    "top: general condition or sample perturbation, then inherited genetic "
    "perturbation. CellRegMap, scDALI and GASPACHO are upper-left. PICALO "
    "and SURGE approach from learning genetic contexts, with SURGE closer "
    "to the upper-right. PICALO is marked as a bulk-data method. scooby "
    "and LIVI occupy the upper-middle. CellCap and GEDI are lower-middle; "
    "contrastiveVI, MrVI and LEMUR are lower-right. Two conceptual arrows "
    "approach Regulotype in the upper-right, the proposed intersection "
    "where a shared cross-locus cis-response profile represents a cell. "
    "The lower side includes experimental perturbations. Positions reflect "
    "overlapping conceptual directions, not measured scores or a training sequence."
)


def S(d=None, dur=None, fill=None, stroke=None, sw=None, length=None, op=None):
    p=[]
    if d is not None: p.append('--d:%.2fs'%d)
    if dur is not None: p.append('--dur:%.2fs'%dur)
    if length is not None: p.append('--len:%.0f'%length)
    if fill is not None: p.append('fill:%s'%fill)
    if stroke is not None: p.append('stroke:%s'%stroke)
    if sw is not None: p.append('stroke-width:%s'%sw)
    if op is not None: p.append('opacity:%s'%op)
    return ';'.join(p)


def txt(x,y,s,cls='lbl',fill=None,d=0.0,anim='a-rise'):
    # As in the reference, s is SVG text content, including intentional tspans.
    return "<text x='%.1f' y='%.1f' class='%s %s' style='%s'>%s</text>"%(x,y,cls,anim,S(d=d,fill=fill),s)


REPLAY = ("<button class='replay' type='button'><svg viewBox='0 0 24 24' "
          "aria-hidden='true'><path d='M20.5 12a8.5 8.5 0 1 1-2.5-6'/>"
          "<path d='M20.5 3.5v5h-5'/></svg>replay</button>")


def multiline(x, y, rows, cls='lbl sm', colour=DIM, delay=0.0, gap=19):
    out = []
    for k, row in enumerate(rows):
        # Excalifont does not contain this symbol. Give only the arrow a
        # system-font fallback so its meaning survives offline rendering too.
        content = escape(row).replace('→', "<tspan font-family='sans-serif'>→</tspan>")
        out.append(txt(x, y + gap*k, content, cls, colour, delay + 0.06*k))
    return out


def method_point(x, y, name, colour, delay, detail='', emphasis=False,
                 aggregate=False):
    """Dot and label; an open dot plus 'bulk' distinguishes PICALO's scale."""
    out = ["<g><title>%s</title>" % escape(detail or name)]
    if emphasis:
        out.append("<circle cx='%.1f' cy='%.1f' r='10' fill='none' "
                   "class='a-pop' style='%s'/>"
                   % (x, y, S(d=delay, dur=0.5, stroke=colour, sw=1.5)))
    out.append("<circle cx='%.1f' cy='%.1f' r='%.1f' class='a-pop' style='%s'/>"
               % (x, y, 4.7 if emphasis else 3.8,
                  S(d=delay, dur=0.5, fill='none' if aggregate else colour,
                    stroke=colour if aggregate else None,
                    sw=1.4 if aggregate else None)))
    if emphasis:
        out.append(txt(x, y-22, escape(name), 'lbl bg mid', colour,
                       delay+0.06, 'a-pop'))
    else:
        out.append(txt(x+12, y+5, escape(name), 'lbl', colour, delay+0.06))
    if aggregate:
        out.append(txt(x+12, y+24, 'bulk', 'lbl sm', DIM, delay+0.12))
    out.append('</g>')
    return out


def svg_arrow(path, tip, tangent, delay, dur=0.7, colour=DIM, sw=1.15,
              length=None, opacity=1.0, head=6):
    """Draw a path and a small polygon aligned with its final tangent.

    Omit length for curves: the site's existing driver measures them before
    playback. Opacity belongs on the group because a-pop ends at opacity 1.
    """
    tx, ty = tip
    dx, dy = tangent
    scale = hypot(dx, dy)
    if scale == 0:
        raise ValueError('Arrow tangent must have nonzero length')
    ux, uy = dx/scale, dy/scale
    bx, by = tx-head*ux, ty-head*uy
    half = head*0.48
    points = '%.1f,%.1f %.1f,%.1f %.1f,%.1f' % (
        tx, ty, bx-half*uy, by+half*ux, bx+half*uy, by-half*ux)
    return [
        "<g opacity='%s' aria-hidden='true'>" % opacity,
        "<path d='%s' fill='none' class='a-draw' stroke-linecap='round' "
        "stroke-linejoin='round' style='%s'/>"
        % (path, S(d=delay, dur=dur, stroke=colour, sw=sw, length=length)),
        "<polygon points='%s' class='a-pop' style='%s'/>"
        % (points, S(d=delay+dur-0.12, dur=0.25, fill=colour)),
        '</g>',
    ]


def figure7():
    """Return the notes-site Figure 7 snippet; no file or import side effects."""
    body = []

    # A conceptual plane: no ticks, numeric coordinates, or fitted distances.
    body += svg_arrow('M48 285 L835 285', (835, 285), (1, 0),
                      0.0, dur=0.5, colour=EDGE, sw=1.4, length=789)
    body += svg_arrow('M380 520 L380 56', (380, 56), (0, -1),
                      0.08, dur=0.5, colour=EDGE, sw=1.4, length=466)
    body.append(txt(48, 309, 'cell state defines response', 'lbl', DIM, 0.45))
    body += multiline(835, 309, ('response defines', 'cellular representation'),
                      'lbl end', DIM, 0.50)
    body.append(txt(380, 35, 'inherited genetic perturbation',
                    'lbl mid', DIM, 0.55))
    body += multiline(380, 550, ('general condition /', 'sample perturbation'),
                      'lbl mid', DIM, 0.60)

    # Hand-placed semantic positions, not quantitative method rankings or a
    # literal order of training steps. SURGE learns U and effect loadings
    # jointly from expression and genotype; it is NOT given expression-only
    # contexts. CellCap retains a basal-state model; contrastiveVI's salient
    # variation is not automatically a causal response. These distinctions
    # are also described in the caption and each method's SVG title.
    # Sources for the expanded map:
    # SURGE: https://pmc.ncbi.nlm.nih.gov/articles/PMC10801966/
    # PICALO: https://pmc.ncbi.nlm.nih.gov/articles/PMC10802033/
    # scDALI: https://pmc.ncbi.nlm.nih.gov/articles/PMC8734213/
    # CellCap (preprint): https://pmc.ncbi.nlm.nih.gov/articles/PMC10979976/
    # contrastiveVI: https://pubmed.ncbi.nlm.nih.gov/37550579/
    # GEDI: https://doi.org/10.1038/s41467-024-50963-0
    methods = [
        (90, 130, 'CellRegMap', TEACHER, 0.85,
         'CellRegMap: cell-resolved allelic effects modeled as functions of cellular context.'),
        (159, 190, 'scDALI', TEACHER, 1.00,
         'scDALI: state-dependent allelic imbalance, using a state kernel from total counts. Allelic imbalance is not the dosage slope of a specified cis SNP.'),
        (238, 99, 'GASPACHO', TEACHER, 1.15,
         'GASPACHO: expression-derived state first, then genetic effects varying along state.'),
        (428, 101, 'PICALO', TEACHER, 1.30,
         'PICALO: learns principal interaction components from eQTL interactions. Its main demonstrations use bulk data, not individual-cell representations.'),
        (560, 102, 'SURGE', TEACHER, 1.44,
         'SURGE: jointly learns continuous cellular contexts and cross-locus genetic-effect loadings from expression and genotype. A direct genetic-context-learning precedent, rather than a fixed-context model.'),
        (420, 211, 'scooby', TEACHER, 1.58,
         'scooby: cell-specific sequence-model variant counterfactuals, using an independently learned cell embedding.'),
        (510, 177, 'LIVI', TEACHER, 1.72,
         'LIVI: inherited genetic effects projected into responsive cells and programs after learning a phenotype representation.'),
        (435, 342, 'CellCap', DATA, 1.95,
         'CellCap (preprint): learns shared transcriptional response programs and cell-state-dependent amplitudes under experimental perturbations. It explicitly retains a basal-state model.'),
        (520, 388, 'GEDI', DATA, 2.10,
         'GEDI: models covariate-dependent shifts and deformations of a shared cell manifold. Its demonstrated response fields concern general sample covariates.'),
        (554, 448, 'contrastiveVI', DATA, 2.25,
         'contrastiveVI: separates shared background variation from target-specific latent variation used for cell clustering. Target-specific variation is not automatically a causal response.'),
        (699, 382, 'MrVI', DATA, 2.40,
         'MrVI: cells represented by sample or background responses, rather than specified inherited alleles.'),
        (716, 452, 'LEMUR', DATA, 2.55,
         'LEMUR: coherent groups based on modeled condition responses; general covariates rather than inherited alleles.'),
    ]
    for x, y, name, colour, delay, detail in methods:
        body += method_point(x, y, name, colour, delay, detail,
                             aggregate=name == 'PICALO')

    # Two approaches to the same proposed intersection. Curves are muted and
    # kept away from method labels; arrow 2 crosses the axis left of its label.
    body += svg_arrow('M329 214 C346 75 548 42 708 80',
                      (708, 80), (160, 38), 2.90, dur=0.65, opacity=0.62)
    #body += multiline(343, 248, ('context-dependent genetic effect',
    #                             '→ response-defined identity'),
    #                  'lbl sm end', DIM, 2.95)
    body += svg_arrow('M680 405 C634 302 739 242 825 197 '
                      'C872 173 864 105 741 87',
                      (741, 87), (-123, -18), 3.02, dur=0.65, opacity=0.62)
    #body += multiline(641, 515, ('generic response-defined state',
    #                             '→ inherited-genetic-response-defined state'),
    #                  'lbl sm mid', DIM, 3.08)

    body += method_point(
        725, 85, 'Regulotype', STUDENT, 3.86,
        'Regulotype: proposed synthesis, learning and validating a shared '
        'cross-locus cis-response profile as a cellular representation. '
        'Simply stacking existing effect estimates does not establish a new '
        'mathematical object or validate the representation.', emphasis=True)
    body += multiline(725, 145, ('cross-locus cis-response profile',
                                 'as a cellular representation'),
                      'lbl sm mid', DIM, 4.14)
    body.append(txt(725, 193, 'proposed intersection', 'lbl sm mid',
                    STUDENT, 4.26))

    lines = ["<div class='nfig wide'>", REPLAY,
             "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 880 600' "
             "role='img' aria-label='%s'>" % escape(ARIA_LABEL, quote=True)]
    lines += [line for line in body if line.strip()]
    lines.append('</svg>')
    lines.append("<div class='caption'><span class='caption-label'>Figure 7.</span> "
                 + escape(CAPTION) + '</div>')
    lines.append('</div>')
    return '\n'.join(lines)


# Preview-only subset of the existing widgets/notes styles. The inline
# snippet above intentionally carries no replacement stylesheet or driver.
PREVIEW_CSS = """
:root {
  --n-teacher:#2F7C87; --n-student:#6E4FA2; --n-data:#A8811A;
  --n-kept:#5C8A55; --n-loss:#B0537F; --n-pruned:#A8613C;
  --n-dim:#6A6076; --n-edge:#DCD3EC; --n-panel:#FCFBFE;
  --n-panel-2:#F6F3FB; --n-ink:#2B2536; --page:#fff;
}
[data-theme='dark'] {
  --n-teacher:#6FC3CE; --n-student:#B79BE8; --n-data:#E3C158;
  --n-kept:#93C98A; --n-loss:#F08CBB; --n-pruned:#E09B72;
  --n-dim:#ABA2B8; --n-edge:#443C57; --n-panel:#1F1D28;
  --n-panel-2:#262232; --n-ink:#EDE8F3; --page:#16171C;
}
body { margin:0; padding:24px; background:var(--page); color:var(--n-ink); }
.article { max-width:880px; margin:0 auto; }
.article .nfig, .article .nfig text {
  font-family:'Excalifont','Chalkboard SE','Comic Sans MS',cursive;
}
.article .nfig {
  position:relative; margin:16px 0; padding:16px 16px 6px;
  border:1px solid var(--n-edge); border-radius:14px; background:var(--n-panel);
}
.article .nfig svg { display:block; width:100%; height:auto; overflow:visible; }
.article .nfig > .caption {
  margin:12px 2px 8px; font-size:14px; line-height:1.55; color:var(--n-dim);
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
}
.article .caption-label { color:var(--n-student); font-weight:700; }
.article .replay {
  position:absolute; top:10px; right:10px; z-index:2; display:inline-flex;
  align-items:center; gap:5px; padding:3px 9px; font-size:12px;
  color:var(--n-dim); background:var(--n-panel-2);
  border:1px solid var(--n-edge); border-radius:999px; cursor:pointer;
}
.article .replay:hover { color:var(--n-student); border-color:var(--n-student); }
.article .replay:focus-visible { outline:2px solid var(--n-student); outline-offset:3px; }
.article .replay svg {
  width:11px; height:11px; fill:none; stroke:currentColor;
  stroke-width:2; stroke-linecap:round;
}
.article .nfig .lbl { fill:var(--n-ink); font-size:15px; }
.article .nfig .lbl.sm { font-size:14px; fill:var(--n-dim); }
.article .nfig .lbl.bg { font-size:18px; }
.article .nfig .mid { text-anchor:middle; }
.article .nfig .end { text-anchor:end; }
.article .nfig .a-draw {
  stroke-dasharray:var(--len,400); stroke-dashoffset:var(--len,400);
  animation:w-draw var(--dur,0.9s) ease forwards var(--d,0s);
}
.article .nfig .a-rise {
  opacity:0; animation:w-rise var(--dur,0.55s) ease forwards var(--d,0s);
}
.article .nfig .a-pop {
  opacity:0; transform:scale(0.6); transform-box:fill-box; transform-origin:center;
  animation:w-pop var(--dur,0.5s) cubic-bezier(0.2,1.5,0.4,1) forwards var(--d,0s);
}
.article .nfig [class*='a-'] { animation-play-state:paused; }
.article .nfig.is-playing [class*='a-'] { animation-play-state:running; }
@keyframes w-draw { to { stroke-dashoffset:0; } }
@keyframes w-rise {
  from { opacity:0; transform:translateY(10px); }
  to { opacity:1; transform:translateY(0); }
}
@keyframes w-pop { to { opacity:1; transform:scale(1); } }
@media (prefers-reduced-motion:reduce) {
  .article .nfig [class*='a-'] {
    animation:none !important; opacity:1 !important;
    transform:none !important; stroke-dashoffset:0 !important;
  }
}
@media (max-width:600px) { body { padding:8px; } .article .nfig { padding:12px 8px 6px; } }
@media print {
  .article .replay { display:none; }
  .article .nfig [class*='a-'] {
    animation:none !important; opacity:1 !important;
    transform:none !important; stroke-dashoffset:0 !important;
  }
}
"""

PREVIEW_JS = """
(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const stages = document.querySelectorAll('.nfig');
  function play(stage) {
    const nodes = stage.querySelectorAll('.a-draw, .a-pop, .a-rise');
    stage.classList.remove('is-playing');
    nodes.forEach(node => { node.style.animation = 'none'; });
    void stage.offsetWidth;
    nodes.forEach(node => { node.style.animation = ''; });
    stage.classList.add('is-playing');
  }
  stages.forEach(stage => {
    stage.querySelectorAll('.a-draw').forEach(path => {
      if (!path.style.getPropertyValue('--len')) {
        path.style.setProperty('--len', Math.ceil(path.getTotalLength() + 2));
      }
    });
    stage.querySelector('.replay').addEventListener('click', () => play(stage));
  });
  if (reduced || !('IntersectionObserver' in window)) {
    stages.forEach(play);
  } else {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) { play(entry.target); observer.unobserve(entry.target); }
      });
    }, {threshold:0.25, rootMargin:'0px 0px -8% 0px'});
    stages.forEach(stage => observer.observe(stage));
  }
})();
"""


def preview_html(snippet, font=None, dark=False):
    font_css = ''
    if font is not None:
        data = base64.b64encode(Path(font).read_bytes()).decode('ascii')
        font_css = ("@font-face { font-family:'Excalifont'; "
                    "src:url(data:font/woff2;base64,%s) format('woff2'); }" % data)
    return '\n'.join([
        '<!doctype html>',
        "<html lang='en'%s>" % (" data-theme='dark'" if dark else ''),
        "<head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        '<title>Figure 7 · Conceptual territory around regulotypes</title>',
        '<style>', font_css, PREVIEW_CSS, '</style>',
        '<noscript><style>.article .nfig [class*="a-"] {animation:none !important; '
        'opacity:1 !important; transform:none !important; stroke-dashoffset:0 !important;}'
        '.article .replay {display:none;}</style></noscript>',
        "</head><body class='notes-site notes-note'><main class='article'>",
        snippet, '</main><script>', PREVIEW_JS, '</script></body></html>',
    ])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', '-o', type=Path, help='write the inline HTML snippet')
    parser.add_argument('--preview', type=Path, help='write a standalone animated HTML preview')
    parser.add_argument('--font', type=Path, help='embed Excalifont WOFF2 in --preview')
    parser.add_argument('--dark', action='store_true', help='use the existing dark palette in --preview')
    args = parser.parse_args(argv)
    if (args.font or args.dark) and not args.preview:
        parser.error('--font and --dark require --preview')
    if args.output and args.preview and args.output.resolve() == args.preview.resolve():
        parser.error('--output and --preview must name different files')
    for path in (args.output, args.preview):
        if path and path.suffix.lower() not in ('.html', '.htm'):
            parser.error('output files must end in .html or .htm; notes are never modified')
    snippet = figure7()
    try:
        # Build both outputs first so a bad font cannot leave a partial result.
        preview = preview_html(snippet, args.font, args.dark) if args.preview else None
        for path, content in ((args.output, snippet), (args.preview, preview)):
            if path:
                path.write_text(content + '\n', encoding='utf-8')
    except OSError as exc:
        parser.error(str(exc))
    if not args.output and not args.preview:
        print(snippet)


if __name__ == '__main__':
    main()
