# Sort Chinese bibliography entries by Pinyin
# Be sure to remove the comment block ```{=comment}```

# Copyright: © 2024–Present Tom Ben
# License: MIT License

import re
import panflute as pf
from pypinyin import pinyin, Style


def contains_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)


def special_pinyin(text):
    # 多音字的姓氏拼音
    surname_map = {
        '葛': 'ge3',
        '阚': 'kan4',
        '区': 'ou1',
        '朴': 'piao2',
        '覃': 'qin2',
        '仇': 'qiu2',
        '任': 'ren2',
        '单': 'shan4',
        '解': 'xie4',
        '燕': 'yan1',
        '尉': 'yu4',
        '乐': 'yue4',
        '曾': 'zeng1',
        '查': 'zha1',
    }

    if contains_chinese(text):
        name = text.split(",")[0] if "," in text else text
        surname = name[0]

        # 获取完整姓名的拼音
        full_pinyin = pinyin(name, style=Style.TONE3)
        full_pinyin_text = "".join([i[0] for i in full_pinyin])

        # 如果姓氏在多音字列表中，替换拼音的首个发音
        if surname in surname_map:
            surname_py = surname_map[surname]
            # 根据姓氏的长度替换拼音
            surname_py_len = len(pinyin(surname, style=Style.TONE3)[0][0])
            full_pinyin_text = surname_py + full_pinyin_text[surname_py_len:]

        return full_pinyin_text
    else:
        return None


# Minimum separation between the numeric label and the bibliography text.
# Accepts either a float (em) or a string with unit (e.g. "10pt", "0.5cm").
BIB_NUMBER_SPACING = "0.5em"

# Optional override for the label column width.  Set to None to size automatically
# based on the number of entries in the bibliography.
BIB_LABEL_WIDTH = None

# Estimated width (in em) for each character inside the label, including brackets.
CHAR_EM_WIDTH = 0.5


def format_width(width):
    """Return width as a LaTeX/CSS-friendly string with em as the unit."""
    if isinstance(width, (int, float)):
        return f"{width:.4f}em"
    return width


def to_em(width):
    """Convert supported units to em for internal calculations."""
    if width is None:
        return None
    if isinstance(width, (int, float)):
        return float(width)

    match = re.match(r'([\d.]+)(em|pt|cm)', width)
    if not match:
        return None

    value = float(match.group(1))
    unit = match.group(2)

    if unit == 'em':
        return value
    if unit == 'pt':
        return value / 12  # 1em ≈ 12pt
    if unit == 'cm':
        return value / 0.423  # 1em ≈ 0.423cm (12pt)
    return None


def width_to_spaces(width):
    """Approximate width in characters/spaces for formats without precise control."""
    width = format_width(width)
    if not width:
        return 4

    match = re.match(r'([\d.]+)(em|pt|cm)', width)
    if match:
        value = float(match.group(1))
        unit = match.group(2)

        if unit == 'em':
            num_spaces = int(value * 4)  # 1em ≈ 4 spaces
        elif unit == 'pt':
            # 12pt ≈ 4 spaces, so 1pt ≈ 0.33 spaces
            num_spaces = int(value / 3)
        elif unit == 'cm':
            num_spaces = int(value * 10)  # rough approximation
        else:
            num_spaces = 4  # fallback
    else:
        num_spaces = 4  # fallback

    return max(1, num_spaces)


def create_custom_space(width=None):
    """Create cross-format horizontal space"""
    if width is None:
        width = BIB_NUMBER_SPACING

    formatted_width = format_width(width)
    num_spaces = width_to_spaces(formatted_width)
    docx_spaces = ' ' * num_spaces

    return [
        pf.RawInline(f"\\hspace{{{formatted_width}}}", format="latex"),
        pf.RawInline(
            f'<span style="display:inline-block;width:{formatted_width};"></span>', format="html"),
        pf.RawInline(
            f'<w:r><w:t xml:space="preserve">{docx_spaces}</w:t></w:r>', format="openxml")
    ]


def compute_label_column_width(total_entries):
    """Return the width (em) allocated to the label column."""
    override = to_em(BIB_LABEL_WIDTH)
    if override:
        return override

    digits = max(1, len(str(total_entries)))
    # Include brackets in width estimate
    total_chars = digits + 2
    return total_chars * CHAR_EM_WIDTH


def prepare(doc):
    doc.chinese_entries = []
    doc.non_chinese_entries = []


def action(elem, doc):
    if isinstance(elem, pf.Div) and "references" in elem.classes:
        for e in elem.content:
            if isinstance(e, pf.Div) and "csl-entry" in e.classes:
                entry_text = pf.stringify(e)
                if contains_chinese(entry_text):
                    doc.chinese_entries.append(e)
                else:
                    doc.non_chinese_entries.append(e)
        elem.content = []


def finalize(doc):
    # 英文文献按照字母顺序排序
    doc.non_chinese_entries.sort(key=lambda x: pf.stringify(x).lower())

    # 中文文献按照拼音排序
    doc.chinese_entries.sort(key=lambda x: special_pinyin(pf.stringify(x)))

    # 合并所有条目并添加编号
    all_entries = doc.non_chinese_entries + doc.chinese_entries
    numbered_entries = []
    max_label_width_em = compute_label_column_width(len(all_entries))
    base_gap_em = to_em(BIB_NUMBER_SPACING) or 0.5

    for i, entry in enumerate(all_entries, 1):
        # 直接修改原有条目，保持所有属性和 ID
        # 在第一个段落开头插入编号
        if entry.content and isinstance(entry.content[0], pf.Para):
            first_para = entry.content[0]
            label_text = f"[{i}]"
            label_chars = len(label_text)
            actual_label_width_em = max(label_chars * CHAR_EM_WIDTH, 0.4)
            actual_label_width_em = min(
                actual_label_width_em, max_label_width_em)
            # Keep the paragraph indentation consistent while avoiding excessive space for short labels.
            gap_em = max(max_label_width_em - actual_label_width_em +
                         base_gap_em, base_gap_em * 0.5)

            for space_elem in reversed(create_custom_space(gap_em)):
                first_para.content.insert(0, space_elem)
            first_para.content.insert(0, pf.Str(label_text))

        numbered_entries.append(entry)

    # 用排序后的条目替换 Div 中的内容
    for elem in doc.content:
        if isinstance(elem, pf.Div) and "references" in elem.classes:
            elem.content = numbered_entries
            break


def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc)


if __name__ == '__main__':
    main()
