#!/usr/bin/env python3
"""Assemble Pages without changing any vendored source or existing root page."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
site = root / '_site'
if site.exists():
    shutil.rmtree(site)
site.mkdir()

# Retain all existing top-level static HTML files, plus documentation.
for source in root.iterdir():
    if source.is_file() and (source.suffix == '.html' or source.name in {'README.md', 'PLAN.md'}):
        shutil.copy2(source, site / source.name)

app = site / 'raphael'
shutil.copytree(root / 'raphael/distrib', app)
html_path = app / 'index.html'
html = html_path.read_text()
# coi-serviceworker is the only source of COOP/COEP on GitHub Pages: the
# upstream `_headers` file only applies to Cloudflare deployments, so the
# served document carries no such headers by itself. Load the library
# first in <head> and leave its defaults alone (no `window.coi` override):
# it registers the worker, reloads once the worker can serve the document
# with COOP/COEP, and only then do the upstream pre-flight check and the
# Trunk loader run, as emitted upstream, in the reloaded worker-controlled
# document. Do not gate either of them on a custom readiness promise: a
# fixed-delay promise that resolves `false` cannot track registration and
# activation, and a `window.coi` override that disables the library's
# degrade reload leaves a worker-controlled but still non-isolated
# document with no reload left, so the upstream check fails it instead.
bootstrap = '''<script src="./coi-serviceworker.js"></script>
'''
assert html.count('<head>') == 1
html = html.replace('<head>', '<head>\n    ' + bootstrap, 1)
assert 'raphaelIsolationReady' not in html, 'Upstream loader must not depend on a custom readiness promise'
html_path.write_text(html)
for name in ('coi-serviceworker.js', 'LICENSE.coi-serviceworker'):
    shutil.copy2(root / 'scripts/pages' / name, app / name)
shutil.copy2(root / 'raphael/LICENSE', app / 'LICENSE.raphael')
(site / '.nojekyll').touch()
print(f'Pages artifact: {site}')
