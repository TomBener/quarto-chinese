::: {.callout-tip title="项目地址"}
<https://github.com/TomBener/quarto-chinese>
:::

# 前言

学术论文写作，是科研工作的核心环节。
写好一篇学术论文，不仅需要有大量的文献阅读、扎实的实证研究，
还需要有清晰的逻辑思维、精准的表达能力。
除此之外，「用什么工具写」也是一个非常重要的问题。
在绝大多数情况下，学术论文的写作工具是 [Microsoft Word](https://microsoft.com/en-us/microsoft-365/word)，
无论是学术期刊、学位论文、还是科研项目报告，
Word 似乎都是不假思索的首选项。
然而，作为一款文字处理软件，
Word 却并不是最适合学术论文写作的工具。
尤其是在参考文献管理、公式编辑、版本控制等方面。
在理工科领域，[LaTeX](https://latex-project.org) 是一种非常流行的学术论文写作工具。
与 Word 不同，LaTeX 是一种排版系统，
而不是所见即所得的文字处理软件，
尽管它的排版效果非常出色，但学习曲线也相对陡峭。

在学术论文写作方面，Word 使用体验较差，LaTeX 学习曲线陡峭且只能生成 PDF，
这两者似乎都不是完美的选择。
有没有一种既易于上手，又能够满足学术论文写作需求的工具呢？
答案是肯定的，这个工具就是 [Markdown](https://daringfireball.net/projects/markdown)。
作为一种轻量级标记语言，Markdown 的语法简单、易读易写。
使用 Markdown 写作，不需要关心排版样式，只需要关注写作内容本身，
在 [Pandoc](https://pandoc.org)
[@macfarlane2024]
的加持下，Markdown 可以输出多种格式的文档，
例如 Word、HTML、LaTeX、PDF、EPUB 等。
基于 Pandoc 开发的 [Quarto](https://quarto.org)
[@allaire2024]，
不仅能够直接在论文中运行 Python、R 等代码，
还增加了很多学术写作的实用功能，例如交叉引用、参考文献预览、
可视化编辑等，是学术写作的理想工具
[@tenen2014]。

```{r}
#| fig-cap: 在 Quarto 中使用 R 绘图
#| code-fold: true
#| code-line-numbers: true
#| label: fig-mtcars

library(ggplot2)
mtcars2 <- mtcars
mtcars2$am <- factor(
    mtcars$am,
    labels = c("automatic", "manual")
)
ggplot(mtcars2, aes(hp, mpg, color = am)) +
    geom_point() +
    geom_smooth() +
    theme(legend.position = "bottom")
```

不论是 LaTeX、Markdown、Pandoc 还是 Quarto，
都是基于英语写作的写作工具，对于中文写作者来说，
这些工具的中文支持并不是很好，比如中文自由换行、
中西文引号、中英文空格、中文按拼音排序等问题，
都需要额外的配置和处理。

本项目的目的，就是基于 Quarto 提供一套完整的 Markdown 学术写作方案，
解决中文写作者在使用 Markdown 写作时遇到的各种问题，
包括中文引号处理、中西文自动添加空格、
参考文献列表按拼音排序（包括多音字）、
中文参考文献本地化等，最终输出为格式完美的 Word、HTML、
LaTeX/PDF、Typst/PDF、EPUB 以及 Reveal.js 幻灯片等格式。
