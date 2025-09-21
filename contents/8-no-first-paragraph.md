# 移除首段样式

在 Pandoc 生成的 Word 文档中，章节的第一段样式为 `First Paragraph`，这在英文写作中是需要的，因为英文文章的首段样式和其他段落样式不同，比如首段不缩进，而其他段落则缩进。但是在中文写作中，首段样式和其他段落样式是相同的，因此需要移除首段样式。

本项目提供了一个 Lua filter `no-first-paragraph.lua` 来实现这个需求，直接在 `_quarto.yml` 中添加这个 filter 即可。
