"""Generate the inline SVG for Figure 7 using Python's standard library.

Run: python3 figures/notes_regulotypes_conceptual_landscape.py
The site builder imports figure7(); importing this module writes no files.
Caption and surrounding prose live in notes/. Shared styles and playback
live in static/css/widgets.css and static/js/widgets.js.

Preserved from the supplied 2026-09-12 script. Original style references:
https://github.com/kaiqianzhang/kaiqianzhang.github.io/blob/main/figures/notes_regulotypes_overview_contribute.py
https://kaiqianzhang.github.io/css/widgets.css
https://kaiqianzhang.github.io/js/widgets.js
"""

from html import escape
from math import hypot


TEACHER='var(--n-teacher)'; STUDENT='var(--n-student)'; DATA='var(--n-data)'
KEPT='var(--n-kept)'; LOSS='var(--n-loss)'; PRUNED='var(--n-pruned)'
DIM='var(--n-dim)'; EDGE='var(--n-edge)'

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
             "<div class='figure-scroll' tabindex='0' role='region' aria-label='Conceptual landscape; scroll horizontally on narrow screens'>",
             "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 880 600' "
             "role='img' aria-label='%s'>" % escape(ARIA_LABEL, quote=True)]
    lines += [line for line in body if line.strip()]
    lines.append('</svg></div>')
    lines.append('</div>')
    return '\n'.join(lines)


if __name__ == "__main__":
    print(figure7())
