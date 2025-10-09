# Sort Chinese bibliography entries by Pinyin
# Be sure to remove the comment block ```{=comment}```

# Copyright: © 2024–Present Tom Ben
# License: MIT License

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
    # Sort English entries alphabetically
    doc.non_chinese_entries.sort(key=lambda x: pf.stringify(x).lower())

    # Sort Chinese entries by pinyin
    doc.chinese_entries.sort(key=lambda x: special_pinyin(pf.stringify(x)))

    # 合并所有条目并添加编号
    all_entries = doc.non_chinese_entries + doc.chinese_entries
    numbered_entries = []

    for i, entry in enumerate(all_entries, 1):
        # 直接修改原有条目，保持所有属性和 ID
        # 在第一个段落开头插入编号
        if entry.content and isinstance(entry.content[0], pf.Para):
            first_para = entry.content[0]
            # 在段落开头插入编号
            first_para.content.insert(0, pf.Str(f"[{i}] "))

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
