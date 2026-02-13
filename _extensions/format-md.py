"""
Preprocess Markdown/Quarto sources for Quarto rendering.

What it does:
- Reads: `_contents/[0-9]*.md` and `_contents/*.qmd`
- Writes: processed `.qmd` files into `contents/` (original files are untouched)

Transforms:
1) Merge adjacent citations into one cluster
   - Before: `[@a]; [@b]`
   - After:  `[@a; @b]`
2) Randomize numeric footnote identifiers to avoid collisions across files
   - Before: `text[^1] ...` and `[^1]: note`
   - After:  `text[^aB3x9] ...` and `[^aB3x9]: note` (example id)
3) Uniquify numeric link-reference identifiers across files
   - Before: `... [label][1] ...` and `[1]: https://example.org`
   - After:  `... [label][chapter-1] ...` and `[chapter-1]: https://example.org`
"""

from pathlib import Path
import random
import re
import string

SOURCE_DIR = Path("_contents")
OUTPUT_DIR = Path("contents")
RANDOM_ID_LEN = 5
RANDOM_ID_CHARS = string.ascii_letters + string.digits


def merge_adjacent_citations(text):
    """Merge adjacent citation blocks into a single cluster."""
    # Join patterns like `[@a]; [@b]` into `[@a; @b]`.
    text = re.sub(
        r"(\[@[^\]]+\])\s*;\s*(\[@[^\]]+\])",
        lambda m: m.group(1)[:-1] + "; " + m.group(2)[1:],
        text,
    )
    # Also handle cases where citation labels carry optional link wrappers.
    return re.sub(r"\][\(\[].*?;\s*\[", "; ", text)


def randomize_numeric_footnotes(text):
    """Randomize numeric footnote IDs (e.g. [^1]) to avoid collisions."""
    ids_in_refs = set(re.findall(r"\[\^(\d+)\]", text))
    ids_in_defs = set(re.findall(r"(?m)^[ \t]{0,3}\[\^(\d+)\]:", text))
    # Include both references and definitions so partial footnotes are still normalized.
    old_ids = ids_in_refs | ids_in_defs
    if not old_ids:
        return text

    new_ids = {}
    for old_id in old_ids:
        new_id = "".join(random.choices(RANDOM_ID_CHARS, k=RANDOM_ID_LEN))
        while new_id in new_ids.values():
            new_id = "".join(random.choices(RANDOM_ID_CHARS, k=RANDOM_ID_LEN))
        new_ids[old_id] = new_id

    for old_id, new_id in new_ids.items():
        text = re.sub(rf"\[\^{old_id}\]", f"[^{new_id}]", text)
        text = re.sub(rf"(?m)^([ \t]{{0,3}})\[\^{old_id}\]:", rf"\1[^{new_id}]:", text)

    return text


def uniquify_numeric_link_references(text, prefix):
    """Make numeric link-reference labels unique (e.g. [1] -> [chapter-1])."""
    old_ids = set(re.findall(r"(?m)^[ \t]{0,3}\[(\d+)\]:", text))
    if not old_ids:
        return text

    for old_id in old_ids:
        new_id = f"{prefix}-{old_id}"
        # `(?<!\^)` keeps footnotes like `[^1]` untouched.
        text = re.sub(rf"(?<!\^)\[{old_id}\](?!:)", f"[{new_id}]", text)
        text = re.sub(rf"(?m)^([ \t]{{0,3}})\[{old_id}\]:", rf"\1[{new_id}]:", text)

    return text


def process_file(source_file, output_file):
    text = source_file.read_text(encoding="utf-8")
    # Keep transform order stable: citations -> footnotes -> link references.
    text = merge_adjacent_citations(text)
    text = randomize_numeric_footnotes(text)
    text = uniquify_numeric_link_references(text, output_file.stem)
    output_file.write_text(text, encoding="utf-8")


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
