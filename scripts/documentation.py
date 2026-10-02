#!/usr/bin/env python3
"""Refresh the document index and check local Markdown file links."""
import argparse
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- documentation:start -->"
END = "<!-- documentation:end -->"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--cached", "--others",
         "--exclude-standard", "-z", "--", "*.md"],
        check=True, capture_output=True, text=True,
    )
    documents = sorted(set(result.stdout.rstrip("\0").split("\0")) - {""})
    knowledge = ROOT / "docs/KB.md"
    content = knowledge.read_text()
    index = START + "\n" + "\n".join(f"- `{name}`" for name in documents) + "\n" + END
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if args.write:
        if START in content or END in content:
            if content.count(START) != 1 or content.count(END) != 1 or not pattern.search(content):
                parser.error("docs/KB.md must contain one complete documentation index")
            content = pattern.sub(lambda match: index, content)
        else:
            content = content.rstrip() + "\n\n## Document index\n\n" + index + "\n"
        knowledge.write_text(content)
    elif pattern.findall(content) != [index]:
        parser.error("document index is stale; run python3 scripts/documentation.py --write")

    errors = []
    for name in documents:
        source = ROOT / name
        if not source.is_file():
            errors.append(f"{name}: document is missing")
            continue
        # ponytail: inline links only; use a Markdown parser if reference links are added.
        for target in re.findall(r"\]\(([^)]+)\)", source.read_text()):
            url = urlsplit(target.strip("<>"))
            if not url.scheme and url.path:
                destination = (source.parent / unquote(url.path)).resolve()
                if not destination.is_relative_to(ROOT) or not destination.is_file():
                    errors.append(f"{name}: missing local file link: {target}")
    if errors:
        parser.error("\n".join(errors))
    print(f"Documentation check passed ({len(documents)} documents).")


if __name__ == "__main__":
    main()
