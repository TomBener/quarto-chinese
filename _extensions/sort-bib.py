# Sort bibliography entries, placing Chinese entries (sorted by Pinyin) after non-Chinese entries (sorted alphabetically).
# Must be run after Citeproc

# Copyright: © 2024–Present Tom Ben
# License: MIT License

# ============ CONFIGURATION ============
# Set to True to place Chinese entries first, False to place them last
CHINESE_FIRST = False
# =======================================

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


# 著者-出版年制把年份紧跟在著者之后输出（`著者, 年份. 题名. 出版信息.`），
# 故从条目开头锚定提取，而不是取全文最后一个年份——后者会抓到条目末尾的
# 访问日期（示例文献库 128 条中有 9 条的访问年与出版年不同）。
# 年份前必须有逗号，可避开团体著者名中的数字（如「《1949 年鉴》编委会」）。
AUTHOR_YEAR_RE = re.compile(r'^(.*?),\s*(1[0-9]{3}|20\d{2})([a-z]?)(?![0-9A-Za-z])')

# 团体著者可能以书名号、引号或括号起头（如「《王震传》编写组」），排序时忽略
LEADING_PUNCT_RE = re.compile(r'^[《〈「『“"\'(（\[]+')


def sort_key(entry_elem):
    """Sort by author, then year, then the citeproc year suffix (1978a, 1978b).

    旧实现把整条文字作为排序键。中文条目走 `special_pinyin(整条)`，而该函数
    内部在首个逗号处截断，键退化成「第一著者姓名」：同一著者名下的条目键全部
    相同，年份不参与排序，排列顺序只是 citeproc 的输出顺序，于是 2020 年的
    著作可能排在 2010 年之前。

    年份后缀在此前是间接成立的：本样式的 <bibliography> 没有 <sort>，citeproc
    按引用顺序输出并按同一顺序赋后缀，先引用者得 `a`，稳定排序又保留了它。
    这里把著者、年份、后缀三项显式取出作键，年份据此正确排序，后缀也直接参与
    比较，不再依赖引用顺序恰好对齐。
    """
    entry_text = pf.stringify(entry_elem)
    match = AUTHOR_YEAR_RE.match(entry_text)
    if match:
        author, year, suffix = match.group(1), int(match.group(2)), match.group(3)
    else:
        # 无可识别年份（如「出版年不详」）的条目按著者排，并置于同著者条目之后
        author, year, suffix = entry_text.split('.', 1)[0], 9999, ''

    author = LEADING_PUNCT_RE.sub('', author).strip()
    # 中文著者按拼音，西文著者按字母；special_pinyin 只取第一著者
    key = special_pinyin(author) if contains_chinese(author) else author.lower()
    return (key, year, suffix)


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
    # Chinese entries by Pinyin, non-Chinese alphabetically; both then by
    # year and year suffix
    doc.chinese_entries.sort(key=sort_key)
    doc.non_chinese_entries.sort(key=sort_key)

    # 用排序后的条目替换 Div 中的内容
    for elem in doc.content:
        if isinstance(elem, pf.Div) and "references" in elem.classes:
            # Determine order based on configuration
            if CHINESE_FIRST:
                elem.content = doc.chinese_entries + doc.non_chinese_entries
            else:
                elem.content = doc.non_chinese_entries + doc.chinese_entries
            break


def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc)


if __name__ == '__main__':
    main()
