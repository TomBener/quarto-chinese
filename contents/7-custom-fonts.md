# 使用自定义字体

在文章的某些段落，或者出于排版需要，或者出于学校要求，我们可能需要使用自定义字体。本项目提供了一个
Lua filter `_extensions/custom-fonts/custom-fonts.lua`，可以实现在 DOCX、PDF（LaTeX/Typst）、HTML 和 EPUB
输出中使用自定义字体。当然，前提是你的系统中已经安装了这些字体。

在 Markdown 中，我们可以使用 `{.fangsong}` 和 `{.kaiti}` 类来指定使用自定义字体。例如：

```markdown
[这是一段使用仿宋字体的文本]{.fangsong}，之后还是使用默认字体。

[这是一段使用楷体的文本，]{.kaiti}之后还是使用默认字体。
```

生成的效果如下：

[这是一段使用仿宋字体的文本]{.fangsong}，之后还是使用默认字体。

[这是一段使用楷体的文本]{.kaiti}，之后还是使用默认字体。

## 不同格式的实现方式

### DOCX 格式

使用 OpenXML 格式指定特定的中文字体（需安装方正字体，或者替换为其他字体）：

- 仿宋：`FZFangSong-Z02`
- 楷体：`FZKai-Z03`

### PDF 格式（LaTeX）

使用 `ctex` 宏包提供的字体命令：

- 仿宋：`\fangsong`
- 楷体：`\kaishu`

### PDF 格式（Typst）

通过 Typst 的 `#text(font: "...")[...]` 语法直接切换字体，渲染时会写入 `custom.typst` 中声明的字体：

- 仿宋：`#text(font: "FZFangSong-Z02")[...]`
- 楷体：`#text(font: "FZKai-Z03")[...]`

### HTML 和 EPUB 格式

使用 CSS `font-family` 属性，提供多层字体回退：

- 仿宋：`FZFangSong-Z02, FangSong, STFangsong, 仿宋, serif`
- 楷体：`FZKai-Z03, KaiTi, STKaiti, 楷体, serif`

使用 Markdown 类的方式有以下优点：

- **格式统一**：在所有输出格式中保持一致的语法
- **代码简洁**：无需学习各种格式的特定命令
- **维护便利**：一处修改，所有格式同步更新
- **跨平台兼容**：提供多种字体回退选项
