"""Stale zh pages (.ai-rules.md §2.3): the one implementation of the rule.

zh-sources.json holds, per page, what the en page was when its zh page was last translated:
"blob", its git blob (the base of the next incremental translation), and "body", the sha256 of
its text below the frontmatter. A zh page carries no frontmatter, so only the body counts.
A zh page is stale when it does not exist yet, when it has no entry, or when the en body's hash
differs from the entry's. Hashes are computed here, so neither git nor history is needed.

As an MkDocs hook it puts a notice under the title of every stale zh page that exists.
As a script:

    python3 hooks/zh_stale.py               list stale pages, one "<reason>\t<page>" per line
    python3 hooks/zh_stale.py --count       print how many there are
    python3 hooks/zh_stale.py --record P    record en page P as it is now, as P's zh page's source
"""
import hashlib
import json
import sys
from pathlib import Path

MANIFEST = "zh-sources.json"
NOTICE = "> **此頁落後英文版。** 英文版在這份翻譯之後已有更新，兩者不一致時以英文版為準。"


def body(data):
    if data.startswith(b"---\n"):
        end = data.find(b"\n---\n", 4)
        if end != -1:
            return data[end + 5:]
    return data


def entry(data):
    return {
        "blob": hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest(),
        "body": hashlib.sha256(body(data)).hexdigest(),
    }


def load(root):
    path = Path(root) / MANIFEST
    return json.loads(path.read_text()) if path.exists() else {}


def save(root, manifest):
    text = json.dumps(dict(sorted(manifest.items())), indent=2, ensure_ascii=False)
    (Path(root) / MANIFEST).write_text(text + "\n")


def stale_pages(root):
    """{page: reason} for every stale zh page; reason is missing, unrecorded or changed."""
    root = Path(root)
    recorded = load(root)
    stale = {}
    for en in sorted((root / "docs").glob("*.md")):
        page = en.name
        if not (root / "docs" / "zh" / page).exists():
            stale[page] = "missing"
        elif page not in recorded:
            stale[page] = "unrecorded"
        elif recorded[page]["body"] != entry(en.read_bytes())["body"]:
            stale[page] = "changed"
    return stale


_stale = {}


def on_config(config):
    global _stale
    _stale = stale_pages(Path(config["config_file_path"]).parent)


def on_page_markdown(markdown, page, config, files):
    src = page.file.src_uri
    if not src.startswith("zh/") or src.count("/") != 1 or src[3:] not in _stale:
        return markdown
    lines = markdown.split("\n")
    at = next((i + 1 for i, line in enumerate(lines) if line.startswith("# ")), 0)
    return "\n".join(lines[:at] + ["", NOTICE, ""] + lines[at:])


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    args = sys.argv[1:]
    if args[:1] == ["--record"] and len(args) == 2:
        manifest = load(root)
        manifest[args[1]] = entry((root / "docs" / args[1]).read_bytes())
        save(root, manifest)
    elif args == ["--count"]:
        print(len(stale_pages(root)))
    elif not args:
        for page, reason in stale_pages(root).items():
            print(f"{reason}\t{page}")
    else:
        sys.exit(__doc__)
