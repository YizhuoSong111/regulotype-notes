#!/usr/bin/env python3
"""Build Markdown research notes into docs/. No network access or publishing."""

from datetime import date
from html import escape
from pathlib import Path
from string import Template
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
import json
import re
import shutil
import sys

try:
    import markdown
    from markdown.extensions import Extension
    from markdown.treeprocessors import Treeprocessor
except ImportError:
    sys.exit('Missing Python-Markdown. Install it with: python3 -m pip install -r requirements.txt')

from figures.notes_regulotypes_conceptual_landscape import figure7

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'docs'
MARKER = '.generated-by-build'
FIGURES = {'conceptual-landscape': figure7}


class ResearchTables(Treeprocessor):
    """Give wide comparison tables headers and keyboard-accessible scrolling."""

    def run(self, root):
        count = 0
        for parent in list(root.iter()):
            for index, child in enumerate(list(parent)):
                if child.tag != 'table':
                    continue
                count += 1
                for header in child.findall('./thead/tr/th'):
                    header.set('scope', 'col')
                for row in child.findall('./tbody/tr'):
                    if len(row):
                        row[0].tag = 'th'
                        row[0].set('scope', 'row')
                wrapper = ET.Element('div', {
                    'class': 'table-scroll', 'tabindex': '0', 'role': 'region',
                    'aria-label': f'Table {count}. Scroll horizontally to read all columns.',
                })
                parent.remove(child)
                wrapper.append(child)
                parent.insert(index, wrapper)


class ResearchExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(ResearchTables(md), 'research-tables', 4)


def template(name, **values):
    """Templates use only ${name}; escape text before passing it here."""
    source = (ROOT / 'templates' / name).read_text(encoding='utf-8')
    return Template(source).substitute(values)


def read_note(path):
    """Read simple key: value metadata; deliberately not a YAML parser."""
    source = path.read_text(encoding='utf-8')
    parts = source.split('---\n', 2)
    if len(parts) != 3 or parts[0]:
        raise ValueError(f'{path.name}: start with a --- metadata block')
    meta = {}
    for line in parts[1].splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(':')
        if not separator or key.strip() in meta:
            raise ValueError(f'{path.name}: invalid or duplicate metadata: {line}')
        meta[key.strip()] = value.strip()
    if not meta.get('title'):
        raise ValueError(f'{path.name}: title is required')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*', path.stem):
        raise ValueError(f'{path.name}: use YYYY-MM-DD-lowercase-slug.md')
    meta['date'] = date.fromisoformat(meta.get('date', path.stem[:10])).isoformat()
    meta['summary'] = meta.get('summary', '')
    meta['filename'] = path.with_suffix('.html').name
    return meta, parts[2]


def render_markdown(source):
    parser = markdown.Markdown(
        extensions=['tables', 'fenced_code', 'md_in_html', 'toc', ResearchExtension()],
        extension_configs={'toc': {'toc_depth': '2'}},
    )
    body = parser.convert(source)

    def insert_figure(match):
        name = match.group(1)
        if name not in FIGURES:
            raise ValueError(f'Unknown figure: {name}')
        return FIGURES[name]()

    # Resolve after Markdown parsing so SVG text and attributes stay untouched.
    body = re.sub(r'<!--\s*figure:([a-z0-9-]+)\s*-->', insert_figure, body)
    return body, parser.toc


def build():
    config = json.loads((ROOT / 'site.json').read_text(encoding='utf-8'))
    notes = [read_note(path) for path in sorted((ROOT / 'notes').glob('*.md'))]
    notes.sort(key=lambda note: (note[0]['date'], note[0]['filename']), reverse=True)
    if OUTPUT.is_symlink() or (OUTPUT.exists() and not (OUTPUT / MARKER).is_file()):
        raise ValueError('docs/ is not recognized as generated output; move it aside before building.')

    def page(content, title, description, prefix):
        return template('base.html', content=content, prefix=prefix,
                        site_title=escape(config['title']), title=escape(title),
                        description=escape(description, quote=True))

    # Finish rendering before replacing the previous successful build.
    with TemporaryDirectory(prefix='.site-build-', dir=ROOT) as staging:
        target = Path(staging) / 'site'
        shutil.copytree(ROOT / 'static', target)
        (target / 'notes').mkdir()
        items = []
        for meta, source in notes:
            body, toc = render_markdown(source)
            content = template('note.html', body=body, toc=toc,
                               title=escape(meta['title']), date=meta['date'],
                               date_label=date.fromisoformat(meta['date']).strftime('%d %B %Y'))
            html = page(content, f"{meta['title']} · {config['title']}", meta['summary'], '../')
            (target / 'notes' / meta['filename']).write_text(html, encoding='utf-8')
            items.append(
                '<li class="note-entry">'
                f'<h2><a href="notes/{meta["filename"]}">{escape(meta["title"])}</a></h2>'
                f'<p>{escape(meta["summary"])}</p>'
                f'<time datetime="{meta["date"]}">{meta["date"]}</time></li>'
            )
        listing = '<ul class="note-list">' + ''.join(items) + '</ul>' if items else '<p>No research notes yet.</p>'
        index = template('index.html', title=escape(config['title']),
                         description=escape(config['description']), notes=listing)
        (target / 'index.html').write_text(page(index, config['title'], config['description'], './'), encoding='utf-8')
        (target / '.nojekyll').touch()
        (target / MARKER).write_text('Generated by build.py. Edit notes/, figures/, static/, or templates/.\n')
        if OUTPUT.exists():
            shutil.rmtree(OUTPUT)
        target.rename(OUTPUT)
    print(f'Built {len(notes)} research note(s) → {OUTPUT}')


if __name__ == '__main__':
    try:
        build()
    except (OSError, ValueError, KeyError) as error:
        sys.exit(f'Build failed: {error}')
