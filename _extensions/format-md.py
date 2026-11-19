"""
Preprocess Markdown/Quarto sources for Quarto rendering.

What it does:
- Reads: `_contents/[0-9]*.md` and `_contents/*.qmd`
- Writes: processed `.qmd` files into `contents/` (original files are untouched)

Transforms (fenced code blocks and inline code are left untouched):
1) Merge adjacent citations into one cluster
   - Before: `[@a]; [@b]; [@c]`
   - After:  `[@a; @b; @c]`
2) Make numeric footnote identifiers unique across files
   - Before: `text[^1] ...` and `[^1]: note`
   - After:  `text[^chapter-1] ...` and `[^chapter-1]: note`
3) Make numeric link-reference identifiers unique across files
   - Before: `... [label][1] ...` and `[1]: https://example.org`
   - After:  `... [label][chapter-1] ...` and `[chapter-1]: https://example.org`
"""

from pathlib import Path
import re

SOURCE_DIR = Path("_contents")
OUTPUT_DIR = Path("contents")

FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
# Inline code cannot span a blank line
INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)((?:(?!\n[ \t]*\n).)+?)(?<!`)\1(?!`)", re.S)
ADJACENT_CITATIONS_RE = re.compile(r"(\[@[^\]]+\])\s*;\s*(\[@[^\]]+\])")


def split_fenced_code(text):
    """Split text into (is_code, chunk) pairs; fenced code blocks are code."""
    chunks = []
    prose = []
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        fence = FENCE_OPEN_RE.match(lines[i])
        if not fence:
            prose.append(lines[i])
            i += 1
            continue
        if prose:
            chunks.append((False, "".join(prose)))
            prose = []
        marker = fence.group(1)
        close_re = re.compile(rf"^ {{0,3}}{re.escape(marker[0])}{{{len(marker)},}}[ \t]*$")
        code = [lines[i]]
        i += 1
        while i < len(lines):
            code.append(lines[i])
            i += 1
            if close_re.match(code[-1].rstrip("\r\n")):
                break
        chunks.append((True, "".join(code)))
    if prose:
        chunks.append((False, "".join(prose)))
    return chunks


def transform_prose(text, transform):
    """Apply `transform` to the text outside fenced code blocks and inline code."""
    parts = []
    for is_code, chunk in split_fenced_code(text):
        if is_code:
            parts.append(chunk)
            continue
        pos = 0
        for match in INLINE_CODE_RE.finditer(chunk):
            parts.append(transform(chunk[pos:match.start()]))
            parts.append(match.group(0))
            pos = match.end()
        parts.append(transform(chunk[pos:]))
    return "".join(parts)


def prose_only(text):
    """Return the text outside fenced code blocks."""
    return "".join(chunk for is_code, chunk in split_fenced_code(text) if not is_code)


def merge_adjacent_citations(text):
    """Merge adjacent citation blocks into a single cluster."""
    # Repeat until nothing changes, so three or more clusters merge into one.
    while True:
        merged = ADJACENT_CITATIONS_RE.sub(
            lambda m: m.group(1)[:-1] + "; " + m.group(2)[1:], text)
        if merged == text:
            return merged
        text = merged


def uniquify_numeric_footnotes(text, prefix):
    """Prefix numeric footnote IDs (e.g. [^1] -> [^chapter-1]) to avoid collisions."""
    return re.sub(r"\[\^(\d+)\]", rf"[^{prefix}-\1]", text)


def uniquify_numeric_link_references(text, prefix, ids):
    """Make numeric link-reference labels unique (e.g. [1] -> [chapter-1])."""
    for old_id in ids:
        # `(?<!\^)` keeps footnotes like `[^1]` untouched.
        text = re.sub(rf"(?<!\^)\[{old_id}\]", f"[{prefix}-{old_id}]", text)
    return text


def process_file(source_file, output_file):
    text = source_file.read_text(encoding="utf-8")
    prefix = output_file.stem
    # Only labels that have a `[n]: url` definition in this file are renamed.
    link_ids = set(re.findall(r"(?m)^[ \t]{0,3}\[(\d+)\]:", prose_only(text)))

    def transform(chunk):
        # Keep transform order stable: citations -> footnotes -> link references.
        chunk = merge_adjacent_citations(chunk)
        chunk = uniquify_numeric_footnotes(chunk, prefix)
        return uniquify_numeric_link_references(chunk, prefix, link_ids)

    output_file.write_text(transform_prose(text, transform), encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    for source_file in sorted(SOURCE_DIR.glob("[0-9]*.md")):
        output_file = OUTPUT_DIR / f"{source_file.stem}.qmd"
        process_file(source_file, output_file)

    for source_file in sorted(SOURCE_DIR.glob("*.qmd")):
        output_file = OUTPUT_DIR / source_file.name
        process_file(source_file, output_file)


if __name__ == "__main__":
    main()
