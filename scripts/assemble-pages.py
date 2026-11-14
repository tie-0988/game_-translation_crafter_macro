#!/usr/bin/env python3
"""Assemble Pages without changing any vendored source or existing root page."""
from pathlib import Path
import re
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
bootstrap = '''<script src="./isolation-bootstrap.js"></script>
        <script src="./coi-serviceworker.js"></script>
        '''
assert html.count('<head>') == 1
html = html.replace('<head>', '<head>\n        ' + bootstrap, 1)
# Leave the upstream diagnostics intact, but run them after the isolation wait.
marker = '(() => {\n                const RELEASES_URL'
assert html.count(marker) == 1, 'Upstream pre-flight changed; review integration'
html = html.replace(marker, '(async () => {\n                await window.raphaelIsolationReady;\n                const RELEASES_URL', 1)
# Trunk emits a module with imports and a call to init(). Imports stay top-level;
# the loader body must not allocate shared Wasm memory on the first navigation.
modules = list(re.finditer(r'<script type="module">(.*?)</script>', html, re.S))
assert len(modules) == 1, 'Expected one Trunk loader module'
module = modules[0]
body = module.group(1)
# Static imports must remain at module scope. Trunk emits one-line imports.
imports = re.findall(r'^\s*import\s+.*?;\s*$', body, re.M)
assert imports, 'Trunk loader imports changed; review integration'
for statement in imports:
    body = body.replace(statement, '', 1)
replacement = '<script type="module">\n' + '\n'.join(imports) + '\nif (await window.raphaelIsolationReady) {\n' + body + '\n}\n</script>'
html = html[:module.start()] + replacement + html[module.end():]
html_path.write_text(html)
for name in ('coi-serviceworker.js', 'isolation-bootstrap.js', 'LICENSE.coi-serviceworker'):
    shutil.copy2(root / 'scripts/pages' / name, app / name)
shutil.copy2(root / 'raphael/LICENSE', app / 'LICENSE.raphael')
(site / '.nojekyll').touch()
print(f'Pages artifact: {site}')
