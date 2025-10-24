# Sort bibliography entries, placing Chinese entries (sorted by Pinyin) after non-Chinese entries (sorted alphabetically).
# Add numeric labels to each entry with consistent spacing.
# Be sure to remove the comment block ```{=comment}```

# Copyright: © 2024–Present Tom Ben
# License: MIT License

import re
import panflute as pf
from pypinyin import pinyin, Style


def contains_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)


def special_pinyin(text):
    """Get Pinyin representation for sorting Chinese names.

    Handles polyphonic Chinese surnames with special pronunciation.
    """
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

    if not contains_chinese(text):
        return None

    name = text.split(",")[0] if "," in text else text
    surname = name[0]

    # 获取完整姓名的拼音
    full_pinyin = pinyin(name, style=Style.TONE3)
    full_pinyin_text = "".join([i[0] for i in full_pinyin])

    # 如果姓氏在多音字列表中，替换拼音的首个发音
    if surname in surname_map:
        surname_py = surname_map[surname]
        surname_py_len = len(pinyin(surname, style=Style.TONE3)[0][0])
        full_pinyin_text = surname_py + full_pinyin_text[surname_py_len:]

    return full_pinyin_text


# Minimum separation between the numeric label and the bibliography text.
# Accepts either a float (em) or a string with unit (e.g. "10pt", "0.5cm").
BIB_NUMBER_SPACING = "0.5em"
# Use figure space (U+2007) to pad DOCX labels so digits align with consistent width.
DOCX_FIGURE_SPACE = '\u2007'


def format_width(width):
    """Return width as a LaTeX/CSS-friendly string with em as the unit."""
    if isinstance(width, (int, float)) and width > 0:
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
    formatted_width = format_width(width)
    if not formatted_width:
        return 4

    match = re.match(r'([\d.]+)(em|pt|cm)', formatted_width)
    if not match:
        return 4

    value = float(match.group(1))
    unit = match.group(2)

    # Approximation: 1em ≈ 4 spaces, 1pt ≈ 0.33 spaces, 1cm ≈ 10 spaces
    spaces_map = {'em': int(value * 4),
                  'pt': int(value / 3), 'cm': int(value * 10)}
    return max(1, spaces_map.get(unit, 4))


def create_custom_space(width=None):
    """Create cross-format horizontal space."""
    width = width or BIB_NUMBER_SPACING
    formatted_width = format_width(width)
    num_spaces = width_to_spaces(formatted_width)
    docx_spaces = ' ' * num_spaces

    return [
        pf.RawInline(f"\\hspace{{{formatted_width}}}", format="latex"),
        pf.RawInline(f'<span style="display:inline-block;width:{formatted_width};"></span>',
                     format="html"),
        pf.RawInline(f'<w:r><w:t xml:space="preserve">{docx_spaces}</w:t></w:r>',
                     format="openxml")
    ]


def create_label_inline(label_text, width_em, max_label_chars):
    """Create a width-constrained, right-aligned label for multiple formats."""
    formatted_width = format_width(width_em)
    if not formatted_width:
        return [pf.Str(label_text)]

    docx_text = label_text
    if max_label_chars is not None:
        padding_chars = max(max_label_chars - len(label_text), 0)
        if padding_chars > 0:
            docx_padding = DOCX_FIGURE_SPACE * padding_chars
            docx_text = f"{docx_padding}{label_text}"

    return [
        pf.RawInline(
            f"\\makebox[{formatted_width}][r]{{{label_text}}}", format="latex"),
        pf.RawInline(f'<span style="display:inline-block;width:{formatted_width};text-align:right;">{label_text}</span>',
                     format="html"),
        pf.RawInline(
            f'<w:r><w:t xml:space="preserve">{docx_text}</w:t></w:r>', format="openxml")
    ]


def prepare(doc):
    """Initialize lists for Chinese and non-Chinese bibliography entries."""
    doc.chinese_entries = []
    doc.non_chinese_entries = []


def action(elem, doc):
    """Separate bibliography entries into Chinese and non-Chinese groups."""
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
    """Sort and number all bibliography entries."""
    # 英文文献按照字母顺序排序
    doc.non_chinese_entries.sort(key=lambda x: pf.stringify(x).lower())

    # 中文文献按照拼音排序
    doc.chinese_entries.sort(key=lambda x: special_pinyin(pf.stringify(x)))

    # 合并所有条目并添加编号
    all_entries = doc.non_chinese_entries + doc.chinese_entries
    if not all_entries:
        return

    max_label_chars = len(f"[{len(all_entries)}]")
    # 每个字符约 0.43em，确保最宽标签从左侧开始
    label_column_width_em = max_label_chars * 0.43
    base_gap_em = to_em(BIB_NUMBER_SPACING) or 0.5

    for i, entry in enumerate(all_entries, 1):
        # 在第一个段落开头插入编号
        if entry.content and isinstance(entry.content[0], pf.Para):
            first_para = entry.content[0]
            label_text = f"[{i}]"
            elements_to_prepend = create_label_inline(
                label_text, label_column_width_em, max_label_chars)

            if base_gap_em > 0:
                elements_to_prepend.extend(create_custom_space(base_gap_em))

            # 逆序插入，确保顺序正确
            for inline in reversed(elements_to_prepend):
                first_para.content.insert(0, inline)

    # 用排序后的条目替换 Div 中的内容
    for elem in doc.content:
        if isinstance(elem, pf.Div) and "references" in elem.classes:
            elem.content = all_entries
            break


def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc)


if __name__ == '__main__':
    main()
