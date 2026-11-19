# 中文参考文献按照拼音排序

在著者年份制的参考文献表中，中文参考文献一般需要按照拼音排序。
基于 GB/T 7714-2015 的 BibLaTeX 样式包 [biblatex-gb7714-2015][1] 支持
使用 `biber` 对中文文献按照拼音排序，但对于 Pandoc 使用的 Citeproc 来说，并不支持这个功能。
因此，中文参考文献的排序问题一直是一个头疼的问题。

[1]: https://github.com/hushidong/biblatex-gb7714-2015

本项目使用 Python filter `_extensions/sort-bib.py` 来解决这个问题，
借助 Python 的 `pypinyin` 库获取中文文献的著者拼音，
然后通过 Panflute [@correia2024] 修改 Pandoc AST，
根据拼音对中文文献进行排序。
同一著者的文献再按出版年排序，
同一年的按年份后缀 a、b、c 排序。
对姓氏读音的多音字，脚本做了特殊处理：

```py
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
```

对于参考文献中中文和英文文献哪个在前的问题，
各个学校和期刊的要求不一样，有的要求中文在前，有的要求非中文（英文）在前。
`_extensions/sort-bib.py` 默认是英文（或其他非中文）在前，如果你需要中文在前，可以把文件开头的配置改为：

```py
CHINESE_FIRST = True
```

需要注意的是，`_extensions/sort-bib.py` 只需用于 author-date 引用格式，
numeric 引用格式不需要排序，因为数字本身就是有序的。

使用 `_extensions/itemkey-to-citekey`，可以直接在 Markdown 中使用 Zotero Item Key
来引用文献，例如使用 `[@FUTCYFS3; @ATQ7MWG6]` 来引用文献，而不需要使用 Citation Key。
[@FUTCYFS3; @ATQ7MWG6]

这种引用方式对 AI Agents 来说非常友好，因为 Item Key 基本不会改变，AI Agents 可以直接从 Zotero 数据库中获取 Item Key 来引用文献，比 Citation Key 更加稳定可靠。
