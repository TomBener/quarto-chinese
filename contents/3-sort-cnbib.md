# 中文参考文献按照拼音排序

在著者年份制的参考文献表中，中文参考文献一般需要按照拼音排序。
基于 GB/T 7714-2015 的 BibLaTeX 样式包 [biblatex-gb7714-2015][1] 支持
使用 `biber` 对中文文献按照排序，但对于 Pandoc 使用的 Citeproc 来说，并不支持这个功能。
因此，中文参考文献的排序问题一直是一个头疼的问题。

[1]: https://github.com/hushidong/biblatex-gb7714-2015

本项目使用 Python filter `_extensions/sort-bib.py` 来解决这个问题，
借助 Python 的 `pypinyin` 库获取中文文献的著者拼音，
然后通过 Panflute [@correia2024] 修改 Pandoc AST，
根据拼音对中文文献进行排序，并且对姓氏读音的多音字进行了特殊处理：

```py
def special_pinyin(text):
    # 多音字的姓氏拼音
    surname_map = {
        '葛': 'ge3',
        '阚': 'kan4',
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
        return surname_map.get(surname, "".join([i[0] for i in pinyin(name, style=Style.TONE3)]))
    else:
        return None
```

对于参考文献中中文和英文文献哪个在前的问题，
各个学校和期刊的要求不一样，有的要求中文在前，有的要求非中文（英文）在前。
`_extensions/sort-bib.py` 默认是英文（或其他非中文）在前，如果你需要中文在前，可以将对应代码修改为：

```py
for elem in doc.content:
        if isinstance(elem, pf.Div) and "references" in elem.classes:
            elem.content = doc.chinese_entries + doc.non_chinese_entries
            break
```

需要注意的是，`_extensions/sort-bib.py` 只需用于 author-date 引用格式，
numeric 引用格式不需要排序，因为数字本身就是有序的。
