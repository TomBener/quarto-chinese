# 段落右对齐或居中

一般而言，段落是左对齐的，但有时我们希望某些段落右对齐或居中。本项目提供了一个
Lua filter `_extensions/text-align/text-align.lua`，可以实现段落右对齐或居中，例如：

```markdown
::: {.right}
这段文字会右对齐

支持 DOCX、PDF（LaTeX/Typst）、HTML 和 EPUB 等格式。

::: {.content-visible when-format="html"}
{{</* meta date-modified */>}}
:::

::: {.content-visible unless-format="html"}
{{</* meta date */>}}
:::
:::
```

生成的效果如下：

::: {.right}
这段文字会右对齐

支持 DOCX、PDF（LaTeX/Typst）、HTML 和 EPUB 等格式。

::: {.content-visible when-format="html"}
{{< meta date-modified >}}
:::

::: {.content-visible unless-format="html"}
{{< meta date >}}
:::
:::

如果希望段落居中，只需使用 `.center` 类：

```markdown
::: {.center}
这段文字会水平居中显示
:::
```

生成的效果如下：

::: {.center}
这段文字会水平居中显示
:::
