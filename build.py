#!/usr/bin/env python3
"""
Merge src/ into dist/index.html — single-file distribution.

Usage:
  python3 build.py            # Build once
  python3 build.py --watch    # Watch and rebuild (requires: pip install watchdog)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / 'src'
DIST = ROOT / 'dist'

JS_MODULES = [
    'core.js', 'json-tools.js', 'text-diff.js', 'encode.js', 'regex.js',
    'timestamp.js', 'hash.js', 'formatter.js',
    'string-tools.js', 'generator.js',
]


def build():
    html = (SRC / 'index.html').read_text('utf-8')

    # Inline CSS
    css = (SRC / 'css' / 'style.css').read_text('utf-8')
    html = html.replace(
        '<link rel="stylesheet" href="css/style.css">',
        '<style>\n' + css + '\n</style>'
    )
    print(f'  ✓ CSS inlined ({len(css)} chars)')

    # Inline JS modules
    for mod in JS_MODULES:
        js = (SRC / 'js' / mod).read_text('utf-8')
        tag = f'<script src="js/{mod}"></script>'
        inline = '<script>\n// ' + mod + '\n' + js + '\n</script>'
        html = html.replace(tag, inline)
        print(f'  ✓ JS: {mod} ({len(js)} chars)')

    DIST.mkdir(parents=True, exist_ok=True)
    out = DIST / 'index.html'
    out.write_text(html, 'utf-8')
    print(f'\n✅ {out}  ({len(html) / 1024:.1f} KB)')
    return True


def watch():
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print('pip install watchdog  (or just run: python3 build.py)')
        sys.exit(1)

    class H(FileSystemEventHandler):
        def on_modified(self, e):
            if e.src_path.endswith(('.html', '.css', '.js')):
                print(f'\n📝 {Path(e.src_path).name} changed')
                build()

    ob = Observer()
    ob.schedule(H(), str(SRC), recursive=True)
    ob.start()
    print(f'👀 Watching {SRC}/ ...')
    try:
        ob.join()
    except KeyboardInterrupt:
        ob.stop()


if __name__ == '__main__':
    if '--watch' in sys.argv or '-w' in sys.argv:
        build()
        watch()
    else:
        build()
