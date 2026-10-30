#!/usr/bin/env python3
"""Turns the site's old address into a forwarder to the new one (30 Oct 2026).

Until 30 Oct 2026 the site was Chucky-42/huzur-vakti, served at
chucky-42.github.io/huzur-vakti/. It now lives at huzurvakti.github.io
(repo huzurvakti/huzurvakti.github.io). GitHub Pages cannot send a real
redirect, so every page of the new site gets a small page at its old address
that sends the visitor on to the same page there: a script that keeps the
query (/indir/?k=...) and the #fragment, an instant meta refresh for browsers
without scripts, and rel=canonical, which together Google reads as a
permanent move. Anything else under the old address is caught by 404.html.

Kept as they are: video/ (the "Video of the Day" list and covers that app
versions up to 3.32.1 read from here), static/ (old shared links' preview
image), sitemap.xml and robots.txt (so Google recrawls the old pages and finds
the forwarders) and Search Console's ownership file.

    python eski_adres.py <clone of Chucky-42/huzur-vakti>

then commit and push that clone. Run it again only if the new site gains pages
that should also answer at the old address.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

NEW = 'https://huzurvakti.github.io/'
OLD_PREFIX = '/huzur-vakti/'
NEW_DOCS = Path(__file__).resolve().parent / 'docs'
KEEP = {'video', 'static', 'sitemap.xml', 'robots.txt', '.nojekyll', 'google43636d30a11e4600.html'}


def forwarder(url, title):
    u = html.escape(url, quote=True)
    return f'''<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="canonical" href="{u}">
<script>location.replace({json.dumps(url)} + location.search + location.hash)</script>
<meta http-equiv="refresh" content="0; url={u}">
</head><body><p>Huzur Vakti: <a href="{u}">{u}</a></p></body></html>
'''


NOT_FOUND = f'''<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Huzur Vakti</title>
<script>
location.replace({json.dumps(NEW)} + location.pathname.replace(/^\\/huzur-vakti\\/?/, '') + location.search + location.hash)
</script>
</head><body><p>Huzur Vakti: <a href="{NEW}">{NEW}</a></p></body></html>
'''


def main(old_repo):
    docs = Path(old_repo) / 'docs'
    if not (docs / 'video').is_dir():
        raise SystemExit(f'{docs} does not look like the old site (no video/)')
    for item in docs.iterdir():
        if item.name in KEEP:
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()
    count = 0
    for page in NEW_DOCS.rglob('index.html'):
        rel = page.parent.relative_to(NEW_DOCS).as_posix()
        if rel.split('/')[0] in KEEP:
            continue
        rel = '' if rel == '.' else rel + '/'
        title = re.search(r'<title>(.*?)</title>', page.read_text(encoding='utf-8'), re.S)
        title = html.unescape(title.group(1).strip()) if title else 'Huzur Vakti'
        target = docs / rel / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(forwarder(NEW + rel, title), encoding='utf-8')
        count += 1
    (docs / '404.html').write_text(NOT_FOUND, encoding='utf-8')
    print(f'{count} yönlendirme sayfası yazıldı → {NEW}')


if __name__ == '__main__':
    main(sys.argv[1])
