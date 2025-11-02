"""
Sort citation clusters so that non-Chinese references keep the order the author
provided while Chinese references are grouped at the end (ordered by Pinyin,
then year, then title). Citation prefixes/suffixes such as “see” or “p. 23” are
kept with their original references.

Run this filter before citeproc and make sure the CSL style does not define a
<sort> block for in-text citations so the custom ordering is preserved.

Copyright: © 2025–Present Tom Ben
License: MIT License
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from functools import lru_cache
from typing import Dict, Iterable, List, Sequence, Set, Tuple

import panflute as pf
from panflute import elements as pf_elements
from pypinyin import Style, pinyin

# Patch until panflute release adds `typst` and `comment` raw formats.
# https://github.com/sergiocorreia/panflute/blob/f99f82d62b245abb7f29e2d2d3bb560099d12cb8/panflute/elements.py#L1249
ADDITIONAL_RAW_FORMATS = {'typst', 'comment'}
if hasattr(pf_elements, 'RAW_FORMATS'):
    pf_elements.RAW_FORMATS = set(pf_elements.RAW_FORMATS)
    pf_elements.RAW_FORMATS.update(ADDITIONAL_RAW_FORMATS)

# 多音字姓氏的特殊拼音
SURNAME_MAP = {
    "葛": "ge3",
    "阚": "kan4",
    "区": "ou1",
    "朴": "piao2",
    "覃": "qin2",
    "仇": "qiu2",
    "任": "ren2",
    "单": "shan4",
    "解": "xie4",
    "燕": "yan1",
    "尉": "yu4",
    "乐": "yue4",
    "曾": "zeng1",
    "查": "zha1",
}


@lru_cache(maxsize=None)
def contains_chinese(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text or "")


@lru_cache(maxsize=None)
def normalize(text: str) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    without_marks = "".join(
        ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", without_marks).strip().lower()


@lru_cache(maxsize=None)
def to_pinyin(text: str) -> str:
    if not text:
        return ""

    syllables = pinyin(text, style=Style.TONE3, errors="ignore", strict=False)
    joined = "".join(part for group in syllables for part in group)
    if not joined:
        return normalize(text)

    surname = text[0]
    if surname in SURNAME_MAP:
        override = SURNAME_MAP[surname]
        original = pinyin(surname, style=Style.TONE3,
                          errors="ignore", strict=False)
        if original and original[0]:
            joined = override + joined[len(original[0][0]):]
    return joined


def stringify(meta_value) -> str:
    if isinstance(meta_value, pf.Element):
        return pf.stringify(meta_value)
    return str(meta_value)


def metadata_paths(doc: pf.Doc) -> List[str]:
    meta = doc.get_metadata("bibliography", default=[])
    if isinstance(meta, pf.MetaList):
        return [stringify(item) for item in meta]
    if isinstance(meta, (pf.MetaInlines, pf.MetaString)):
        return [stringify(meta)]
    if isinstance(meta, list):
        return [stringify(item) for item in meta]
    if isinstance(meta, str):
        return [meta]
    return []


def load_entries(doc: pf.Doc, keep_ids: Set[str]) -> Dict[str, dict]:
    base_dir = (
        doc.get_metadata("quarto-input-dir", default=None)
        or doc.get_metadata("working-directory", default=None)
        or os.getcwd()
    )

    entries: Dict[str, dict] = {}
    for raw_path in metadata_paths(doc):
        if not raw_path:
            continue

        path = os.path.expanduser(raw_path)
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(base_dir, path))
        if not os.path.exists(path) or not path.lower().endswith(".json"):
            continue

        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue

        if isinstance(data, dict):
            data = [data]

        for entry in data or []:
            entry_id = entry.get("id")
            if entry_id and (not keep_ids or entry_id in keep_ids):
                entries[entry_id] = entry
    return entries


def people_names(entry: dict) -> List[str]:
    contributors: Sequence = entry.get("author") or entry.get("editor") or []
    names: List[str] = []
    for person in contributors:
        if isinstance(person, dict):
            literal = person.get("literal")
            if literal:
                names.append(str(literal))
            else:
                family = person.get("family", "")
                given = person.get("given", "")
                combined = f"{family} {given}".strip()
                if combined:
                    names.append(combined)
        elif person:
            names.append(str(person))
    return names


def detect_chinese(entry: dict) -> bool:
    fields = [entry.get("title", ""), entry.get("container-title", "")]
    fields.extend(people_names(entry))
    return any(contains_chinese(str(field)) for field in fields if field)


def author_key(entry: dict, chinese: bool) -> str:
    names = people_names(entry)
    if not names:
        title = entry.get("title", "")
        return to_pinyin(title) if chinese and contains_chinese(title) else normalize(title)

    converted: Iterable[str] = (
        to_pinyin(name) if chinese and contains_chinese(
            name) else normalize(name)
        for name in names
    )
    return "".join(converted)


def title_key(entry: dict, chinese: bool) -> str:
    title = entry.get("title", "")
    if chinese and contains_chinese(title):
        return to_pinyin(title)
    return normalize(title)


def extract_year(entry: dict) -> int:
    def from_obj(obj) -> int | None:
        if isinstance(obj, dict):
            parts = obj.get("date-parts") or obj.get("literal")
            if isinstance(parts, list) and parts:
                first = parts[0]
                if isinstance(first, list) and first:
                    first = first[0]
                if isinstance(first, int):
                    return first
                if isinstance(first, str) and first.isdigit():
                    return int(first)
            if isinstance(parts, str):
                match = re.search(r"(\d{4})", parts)
                if match:
                    return int(match.group(1))
        elif isinstance(obj, list) and obj:
            return from_obj({"date-parts": obj})
        elif isinstance(obj, str):
            match = re.search(r"(\d{4})", obj)
            if match:
                return int(match.group(1))
        return None

    for key in ("issued", "original-date", "event-date", "year", "date"):
        year = from_obj(entry.get(key))
        if year:
            return year
    return 9999


def gather_citations(elem: pf.Element, doc: pf.Doc) -> None:
    if isinstance(elem, pf.Cite):
        for citation in elem.citations:
            doc._cited_ids.add(citation.id)


def prepare(doc: pf.Doc) -> None:
    doc._cited_ids = set()
    doc.walk(gather_citations)

    bibliography = load_entries(doc, doc._cited_ids)
    sort_info: Dict[str, Tuple[bool, str, int, str]] = {}

    for key, entry in bibliography.items():
        chinese = detect_chinese(entry)
        sort_info[key] = (
            chinese,
            author_key(entry, chinese),
            extract_year(entry),
            title_key(entry, chinese),
        )

    doc._sort_info = sort_info  # type: ignore[attr-defined]


def sort_key(doc: pf.Doc, citation: pf.Citation, original_index: int) -> Tuple[int, str, int, str, int]:
    info = getattr(doc, "_sort_info", {}).get(citation.id)
    if not info:
        fallback = normalize(citation.id)
        return (0, fallback, 9999, fallback, original_index)

    is_chinese, author, year, title = info
    group = 1 if is_chinese else 0
    return (group, author, year, title, original_index)


def restore_prefix(elem: pf.Cite, prefix: List[pf.Element]) -> None:
    if prefix and elem.citations:
        combined = list(prefix) + list(elem.citations[0].prefix)
        elem.citations[0].prefix = pf.ListContainer(*combined)


def action(elem: pf.Element, doc: pf.Doc) -> pf.Element | None:
    if not isinstance(elem, pf.Cite) or len(elem.citations) < 2:
        return None

    cluster_prefix: List[pf.Element] = []
    if elem.citations[0].prefix:
        cluster_prefix = list(elem.citations[0].prefix)
        elem.citations[0].prefix = pf.ListContainer()

    sortable = list(enumerate(elem.citations))

    if len(sortable) < 2:
        restore_prefix(elem, cluster_prefix)
        return None

    sorted_subset = sorted(
        sortable,
        key=lambda item: sort_key(doc, item[1], item[0]),
    )

    for target_index, (_, citation) in zip((idx for idx, _ in sortable), sorted_subset):
        elem.citations[target_index] = citation

    restore_prefix(elem, cluster_prefix)
    return elem


def main(doc: pf.Doc | None = None) -> None:
    pf.run_filter(action, prepare=prepare, doc=doc)


if __name__ == "__main__":
    main()
