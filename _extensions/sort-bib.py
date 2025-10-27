# Sort bibliography entries, placing Chinese entries (sorted by Pinyin) after non-Chinese entries (sorted alphabetically).
# Must be run after Citeproc

# Copyright: © 2024–Present Tom Ben
# License: MIT License

import re
import panflute as pf
from panflute import elements as pf_elements
from pypinyin import pinyin, Style


# Patch until panflute release adds `typst` and `comment` raw formats.
# https://github.com/sergiocorreia/panflute/blob/f99f82d62b245abb7f29e2d2d3bb560099d12cb8/panflute/elements.py#L1249
ADDITIONAL_RAW_FORMATS = {'typst', 'comment'}
if hasattr(pf_elements, 'RAW_FORMATS'):
    pf_elements.RAW_FORMATS = set(pf_elements.RAW_FORMATS)
    pf_elements.RAW_FORMATS.update(ADDITIONAL_RAW_FORMATS)


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
    doc.chinese_entries.sort(key=lambda x: special_pinyin(pf.stringify(x)))

    # 用排序后的条目替换 Div 中的内容
    for elem in doc.content:
        if isinstance(elem, pf.Div) and "references" in elem.classes:
            # 按拼音排序中文参考文献条目，并将其附加到非中文条目的末尾
            # 交换加号前后的顺序可以改变中文和非中文参考文献条目的顺序
            elem.content = doc.non_chinese_entries + doc.chinese_entries
            break


def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc)


if __name__ == '__main__':
    main()
