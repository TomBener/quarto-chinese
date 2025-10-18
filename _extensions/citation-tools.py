"""
Citation Tools for Academic Writing

This script provides utilities for managing citations in academic writing:
1. Extract citation keys from Markdown files and create a filtered bibliography
2. Copy cited reference files to a specified directory for backup or sharing

Typical usage:
    python citation-tools.py --extract
    python citation-tools.py --copy

Copyright: © 2025–Present Tom Ben
License: MIT License
"""

import os
import re
import shutil
import argparse
import json
from pathlib import Path


def extract_citation_keys(markdown_file):
    """Extract citation keys from a markdown file."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1: [@key] or [@key1; @key2] format
    pattern1 = r'\[@([a-zA-Z0-9\-]+)(?:[\s\]\;\,]|$)'

    # Pattern 2: standalone @key format
    pattern2 = r'(?<![a-zA-Z0-9])@([a-zA-Z0-9\-]+)(?:[\s\.\,\;\:\)\]\}]|$)'

    keys1 = re.findall(pattern1, content)
    keys2 = re.findall(pattern2, content)

    # Combine keys and filter out figure and table references
    all_keys = set(keys1 + keys2)
    return {key for key in all_keys if not (
        key.startswith('fig-') or key.startswith('tbl-'))}


def load_csl_entries(csl_json_file):
    """Load CSL JSON entries from file."""
    with open(csl_json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a list of CSL JSON entries, got {type(data)} instead.")

    return data


def parse_file_field(file_field):
    """Return a list of file paths from a CSL JSON file field."""
    if not file_field or not isinstance(file_field, str):
        return []

    return [path.strip() for path in file_field.split(';') if path.strip()]


def build_citation_file_index(entries):
    """Build a dictionary mapping citation IDs to attached file paths."""
    index = {}

    for entry in entries:
        key = entry.get('id')
        if not key:
            continue
        paths = parse_file_field(entry.get('file'))
        if paths:
            index[key] = paths

    return index


def extract_csl_json_entries(csl_json_file, citation_keys, remove_fields=None):
    """Extract CSL JSON entries for the given citation keys."""
    if remove_fields is None:
        remove_fields = ['file']

    entries = load_csl_entries(csl_json_file)
    citation_keys = set(citation_keys)
    filtered_entries = []

    for entry in entries:
        key = entry.get('id')
        if key and key in citation_keys:
            entry_copy = {k: v for k, v in entry.items()
                          if k not in remove_fields}
            filtered_entries.append(entry_copy)

    filtered_entries.sort(key=lambda item: item.get('id', ''))
    return json.dumps(filtered_entries, ensure_ascii=False, indent=2) + '\n'


def copy_cited_files(args):
    """Copy cited files from bibliography to a new folder."""
    # Clean output directory if requested
    if args.clean and os.path.exists(args.output_dir):
        print(f"Cleaning output directory: {args.output_dir}")
        shutil.rmtree(args.output_dir)

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Parse bibliography (silently)
    entries = load_csl_entries(args.bib)
    citation_files = build_citation_file_index(entries)

    # Find all Markdown files in content directory
    markdown_files = list(Path(args.content_dir).glob('[0-9]*.md'))

    # Extract all citation keys from Markdown files
    all_keys = set()
    for md_file in markdown_files:
        all_keys.update(extract_citation_keys(md_file))

    # Copy files to output directory
    copied_count = 0
    missing_count = 0
    file_not_found_count = 0
    missing_keys = []
    not_found_pairs = []

    for key in all_keys:
        if key in citation_files:
            paths = citation_files[key]
            existing_path = next(
                (path for path in paths if os.path.exists(path)), None)
            source_path = existing_path or paths[0]
            _, file_extension = os.path.splitext(source_path)
            dest_path = os.path.join(args.output_dir, f"{key}{file_extension}")

            try:
                if existing_path and os.path.exists(existing_path):
                    shutil.copy2(existing_path, dest_path)
                    copied_count += 1
                else:
                    file_not_found_count += 1
                    not_found_pairs.append((key, source_path))
            except Exception as e:
                print(f"Error copying {key}: {e}")
        else:
            missing_count += 1
            missing_keys.append(key)

    # Print simplified summary
    print(f"Markdown files in content directory: {len(markdown_files)}")
    print(f"Total unique citation keys found: {len(all_keys)}")
    print(f"Files successfully copied: {copied_count}")
    print(f"Citation keys without file paths: {missing_count}")
    print(
        f"Files not found (path exists in bibliography but file missing): {file_not_found_count}")

    if missing_keys:
        print("\nCitation keys without file paths:")
        for key in sorted(missing_keys):
            print(f"  - {key}")

    if not_found_pairs:
        print("\nCitation keys where file wasn't found:")
        for key, path in sorted(not_found_pairs):
            print(f"  - {key}: {path}")

    return all_keys


def extract_citations(args):
    """Extract citations from Markdown files and save them to a CSL JSON file."""
    # Find all Markdown files in content directory
    markdown_files = list(Path(args.content_dir).glob('[0-9]*.md'))

    # Extract all citation keys from Markdown files
    all_keys = set()
    for md_file in markdown_files:
        all_keys.update(extract_citation_keys(md_file))

    # Extract CSL JSON entries
    json_content = extract_csl_json_entries(
        args.bib, all_keys, args.remove_fields)

    # Write to output file
    with open(args.output_bib, 'w', encoding='utf-8') as f:
        f.write(json_content)

    # Print simplified summary
    print(f"Markdown files in content directory: {len(markdown_files)}")
    print(f"Total unique citation keys found: {len(all_keys)}")
    print(f"Extracted citations to `{args.output_bib}`")

    return all_keys


def main():
    """Parse command line arguments and execute the appropriate function."""
    # Get script location and project root
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent if script_dir.name == "_extensions" else script_dir

    parser = argparse.ArgumentParser(
        description='Citation tools for extracting and copying cited references')

    # Common arguments
    default_bib = os.path.expanduser(
        "~/Library/CloudStorage/Dropbox/pkm/bibliography.json")
    default_content_dir = str(project_root / "contents")

    # Add command flags instead of subcommands
    parser.add_argument('--extract', action='store_true',
                        help='Extract citations to a filtered CSL JSON file')
    parser.add_argument('--copy', action='store_true',
                        help='Copy cited files to a directory')

    # Common arguments for both commands
    parser.add_argument('--bib',
                        default=default_bib,
                        help=f'Path to bibliography.json file (default: {default_bib})')
    parser.add_argument('--content_dir',
                        default=default_content_dir,
                        help=f'Path to content directory with Markdown files (default: {default_content_dir})')

    # Arguments specific to extract
    parser.add_argument('--output_bib',
                        default=str(project_root / "citebib.json"),
                        help=f'Path to output CSL JSON file (default: {project_root}/citebib.json)')
    parser.add_argument('--remove_fields',
                        nargs='+',
                        default=['file'],
                        help='Fields to remove from CSL JSON entries (default: file)')

    # Arguments specific to copy
    parser.add_argument('--output_dir',
                        default=os.path.expanduser(
                            "~/Downloads/cited-docs"),
                        help='Path to output directory for copied files (default: ~/Downloads/cited-docs)')
    parser.add_argument('--clean',
                        action='store_true',
                        help='Clean the output directory before copying files')

    args = parser.parse_args()

    if args.extract:
        extract_citations(args)
    elif args.copy:
        copy_cited_files(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
