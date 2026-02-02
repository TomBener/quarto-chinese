# Preprocess Markdown/Quarto sources for Quarto rendering.
#
# What it does
# - Reads: `contents/[0-9]*.md` and `contents/*.qmd`
# - Writes: processed `.qmd` files into `contents_tmp/` (original files are untouched)
#
# Transforms
# 1) Merge adjacent citations into one cluster
#    - Before: `[@a][; [@b]`
#    - After:  `[@a; @b]`
#
# 2) Randomize numeric footnote identifiers to avoid collisions across files
#    - Before: `text[^1] ...\n\n[^1]: note`
#    - After:  `text[^aB3x9] ...\n\n[^aB3x9]: note`  (example id)

# Copyright: © 2024–Present Tom Ben
# License: MIT License

import re
import glob
import os
import random
import string


def get_md_files():
    # Get all *.md files
    return [f for f in glob.glob("contents/[0-9]*.md")]


def randomize_footnote_identifiers(qmd_content):
    # Find all existing footnote identifiers (numbers)
    existing_ids = set(re.findall(r'\[\^(\d+)\]', qmd_content))

    # Generate a unique random identifier for each existing footnote
    unique_ids = {}
    for id in existing_ids:
        # Generate a random string of 5 characters
        new_id = ''.join(random.choices(
            string.ascii_letters + string.digits, k=5))
        while new_id in unique_ids.values():
            new_id = ''.join(random.choices(
                string.ascii_letters + string.digits, k=5))
        unique_ids[id] = new_id

    # Replace all footnote references and definitions with new identifiers
    for old_id, new_id in unique_ids.items():
        qmd_content = re.sub(rf'\[\^{old_id}\]', f'[^{new_id}]', qmd_content)
        qmd_content = re.sub(rf'\[\^{old_id}\]:', f'[^{new_id}]:', qmd_content)

    return qmd_content


def process_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Merge multiple adjacent citations into one
    content = re.sub(r"\][\(\[].*?;\s*\[", "; ", content)

    # Randomize footnote identifiers
    content = randomize_footnote_identifiers(content)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    md_files = get_md_files()

    # Create contents_tmp directory if it doesn't exist
    tmp_dir = "contents_tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # Convert *.md files to *.qmd files in contents_tmp directory
    qmd_files = [os.path.join(tmp_dir, os.path.basename(
        f).replace(".md", ".qmd")) for f in md_files]

    for md_file, qmd_file in zip(md_files, qmd_files):
        process_file(md_file, qmd_file)

    # Process existing .qmd files in contents directory and output to contents_tmp
    os.chdir('contents')
    existing_qmd_files = glob.glob('*.qmd')

    for qmd_file in existing_qmd_files:
        output_file = os.path.join('..', tmp_dir, qmd_file)
        process_file(qmd_file, output_file)


if __name__ == "__main__":
    main()
