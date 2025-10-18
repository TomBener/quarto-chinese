# Convert *.md files to *.qmd files and pre-process them
# Randomize footnote identifiers in multiple Quarto files to avoid conflicts
# Convert reference-style links to inline links
# Remove line breaks within a straight angle quotation mark
# Reformat display math equations in Ulysses

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


def convert_reference_to_inline(qmd_content):
    # Extract reference links
    reference_links = {}
    reference_pattern = re.compile(r'\n\[(\d+)\]:\s*(.*)')
    for match in reference_pattern.findall(qmd_content):
        reference_links[match[0]] = match[1]

    # Remove the reference link definitions from the qmd_content
    qmd_content = reference_pattern.sub('', qmd_content)

    # Replace reference-style link usages with inline links
    def replace_link(match):
        text = match.group(1)
        key = match.group(2)
        url = reference_links.get(key, '')
        return f'[{text}]({url})'

    usage_pattern = re.compile(r'\[(.*?)\]\[(\d+)\]')
    qmd_content = usage_pattern.sub(replace_link, qmd_content)

    return qmd_content


def remove_linebreaks_in_quotes(text):
    # Regular expression pattern to find blocks within single Chinese quotes
    pattern = r'「[^」]*?」'

    # Function to replace newlines in the found quoted text
    def replace_newlines(m):
        # Remove all newlines within the quote block
        return m.group(0).replace('\n', '')

    # Use re.sub to replace the newline characters in each match
    cleaned_text = re.sub(pattern, replace_newlines, text)

    return cleaned_text


def reformat_math_equations(content):
    # Reformat display math with labels to block format
    labeled_pattern = r"\$(.+?)\$ *(\{#.+?\})"

    def replace_with_labeled_block(match):
        equation = match.group(1).strip()
        label = match.group(2).strip()
        return f"$$\n{equation}\n$$ {label}"

    content = re.sub(labeled_pattern, replace_with_labeled_block, content)

    # Reformat display math without labels to block format
    # Match `$$ ... $$` without label
    display_pattern = r"(?<!\$)\$\$([^\$]+?)\$\$(?!\{#)"

    def replace_with_display_block(match):
        equation = match.group(1).strip()
        return f"$$\n{equation}\n$$"

    content = re.sub(display_pattern, replace_with_display_block, content)

    return content


def process_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove links with `[@]` and a space before it
    content = re.sub(r"\s*\[@\].*?[\]\)]", "", content)
    # Remove square brackets enclosing the caption
    content = re.sub(r"^\[(.*)\}\]$", r"\n  :\1}", content, flags=re.MULTILINE)
    # Merge multiple adjacent citations into one
    content = re.sub(r"\][\(\[].*?;\s*\[", "; ", content)
    # Replace '{{\<...\>}}' with '{{<...>}}'
    content = re.sub(r"\{\{\\<(.*)\\>}}", r"{{<\1>}}", content)
    # Remove comment blocks to avoid errors of Python filter
    content = re.sub(r"^```{=comment}.*?^```$", "",
                     content, flags=re.DOTALL | re.MULTILINE)

    # Randomize footnote identifiers
    content = randomize_footnote_identifiers(content)
    # Convert reference-style links to inline links
    content = convert_reference_to_inline(content)
    # Remove line breaks in quotes
    content = remove_linebreaks_in_quotes(content)
    # Reformat math equations
    content = reformat_math_equations(content)

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
