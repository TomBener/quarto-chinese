"""
Citation Tools for Academic Writing

This script provides utilities for managing citations in academic writing:
1. Extract citation keys from Markdown files and create a filtered CSL JSON bibliography
2. Copy cited reference files to a specified directory for backup or sharing
3. Extract Chinese-only bibliography entries based on Chinese characters in the title

Typical usage:
    python citation-tools.py --extract
    python citation-tools.py --extract-cn
    python citation-tools.py --copy

Copyright: © 2025–Present Tom Ben
License: MIT License
"""

import os
import re
import shutil
import json
import argparse
from pathlib import Path


def extract_citation_keys(markdown_file):
    """Extract citation keys from a markdown file."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1: [@key] or [@key1; @key2] format
    pattern1 = r'\[@([a-zA-Z0-9\-]+)(?:[\s\]\;\,]|$)'

    # Pattern 2: standalone @key format (includes possessive 's)
    pattern2 = r'(?<![a-zA-Z0-9])@([a-zA-Z0-9\-]+)(?:[\s\.\,\;\:\)\]\}\']|$)'

    keys1 = re.findall(pattern1, content)
    keys2 = re.findall(pattern2, content)

    # Combine keys and filter out figure and table references
    all_keys = set(keys1 + keys2)
    return {key for key in all_keys if not (
        key.startswith('fig-') or key.startswith('tbl-'))}


def parse_json_file(json_file):
    """Parse CSL JSON file and extract citation keys with file paths."""
    with open(json_file, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    # Dictionary to store citation key -> file path mappings
    citations = {}

    for entry in entries:
        if 'id' in entry:
            key = entry['id']
            if 'file' in entry and entry['file']:
                # CSL JSON stores file path directly in 'file' field
                file_path = entry['file'].strip()
                if file_path:
                    citations[key] = file_path

    return citations


def extract_full_json_entries(json_file, citation_keys, remove_fields=None):
    """Extract full CSL JSON entries for the given citation keys."""
    if remove_fields is None:
        remove_fields = ['file']

    with open(json_file, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    # Filter entries by citation keys
    filtered_entries = []
    entry_dict = {}

    for entry in entries:
        if 'id' in entry and entry['id'] in citation_keys:
            # Create a copy to avoid modifying the original
            filtered_entry = entry.copy()

            # Remove specified fields
            for field in remove_fields:
                filtered_entry.pop(field, None)

            # Store in dictionary with key for sorting
            entry_dict[entry['id']] = filtered_entry

    # Sort entries by citation key
    sorted_entries = [entry_dict[key] for key in sorted(entry_dict.keys())]

    return sorted_entries


def copy_cited_files(args):
    """Copy cited files from bibliography to a new folder."""
    # Clean output directory if requested
    if args.clean and os.path.exists(args.output_dir):
        print(f"Cleaning output directory: {args.output_dir}")
        shutil.rmtree(args.output_dir)

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Parse bibliography (silently)
    citations = parse_json_file(args.bib)

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
        if key in citations:
            source_path = citations[key]
            _, file_extension = os.path.splitext(source_path)
            dest_path = os.path.join(args.output_dir, f"{key}{file_extension}")

            try:
                if os.path.exists(source_path):
                    shutil.copy2(source_path, dest_path)
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

    # Extract full JSON entries
    json_entries = extract_full_json_entries(
        args.bib, all_keys, args.remove_fields)

    # Write to output file with proper formatting
    with open(args.output_bib, 'w', encoding='utf-8') as f:
        json.dump(json_entries, f, ensure_ascii=False, indent=2)

    # Print simplified summary
    print(f"Markdown files in content directory: {len(markdown_files)}")
    print(f"Total unique citation keys found: {len(all_keys)}")
    print(f"Extracted citations to `{args.output_bib}`")

    return all_keys


def has_chinese_characters(text):
    """Check if the given text contains Chinese characters."""
    # Unicode range for Chinese characters (CJK Unified Ideographs)
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def extract_chinese_citations(args):
    """Extract citations with Chinese titles from Markdown files and save them to a CSL JSON file."""
    # Find all Markdown files in content directory
    markdown_files = list(Path(args.content_dir).glob('[0-9]*.md'))

    # Extract all citation keys from Markdown files
    all_keys = set()
    for md_file in markdown_files:
        all_keys.update(extract_citation_keys(md_file))

    # Read the entire JSON file
    with open(args.bib, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    # Filter entries with Chinese titles
    chinese_entries = {}

    for entry in entries:
        if 'id' in entry and entry['id'] in all_keys:
            # Check if title contains Chinese characters
            if 'title' in entry and has_chinese_characters(entry['title']):
                # Create a copy to avoid modifying the original
                filtered_entry = entry.copy()

                # Remove specified fields
                for field in args.remove_fields:
                    filtered_entry.pop(field, None)

                # Store in dictionary with key for sorting
                chinese_entries[entry['id']] = filtered_entry

    # Sort entries by citation key
    sorted_entries = [chinese_entries[key]
                      for key in sorted(chinese_entries.keys())]

    # Write to output file with proper formatting
    with open(args.output_bib, 'w', encoding='utf-8') as f:
        json.dump(sorted_entries, f, ensure_ascii=False, indent=2)

    # Print summary
    print(f"Markdown files in content directory: {len(markdown_files)}")
    print(f"Total unique citation keys found: {len(all_keys)}")
    print(f"Chinese citation entries found: {len(chinese_entries)}")
    print(f"Extracted Chinese citations to `{args.output_bib}`")

    return set(chinese_entries.keys())


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
    default_content_dir = str(project_root / "_contents")

    # Add command flags instead of subcommands
    parser.add_argument('--extract', action='store_true',
                        help='Extract citations to a CSL JSON file')
    parser.add_argument('--extract-cn', action='store_true',
                        help='Extract Chinese citations to a CSL JSON file')
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
                        help='Fields to remove from JSON entries (default: file)')

    # Arguments specific to copy
    parser.add_argument('--output_dir',
                        default=os.path.expanduser(
                            "~/Downloads/cited-docs"),
                        help='Path to output directory for copied files (default: ~/Downloads/cited-docs)')
    parser.add_argument('--clean',
                        action='store_true',
                        help='Clean the output directory before copying files')

    args = parser.parse_args()

    # Set different default output files based on the command
    if args.extract and args.output_bib == str(project_root / "citebib.json"):
        # Keep the default for --extract
        pass
    elif args.extract_cn and args.output_bib == str(project_root / "citebib.json"):
        # Change default for --extract-cn to citecn.json
        args.output_bib = str(project_root / "citecn.json")

    if args.extract:
        extract_citations(args)
    elif args.extract_cn:
        extract_chinese_citations(args)
    elif args.copy:
        copy_cited_files(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
