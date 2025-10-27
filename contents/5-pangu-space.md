# 中西文盘古之白

[pangu.js][1] 中提到：

[1]: https://github.com/vinta/pangu.js

> 有研究显示，打字的时候不喜欢在中文和英文之间加空格的人，
> 感情路都走得很辛苦，有七成的比例会在 34 岁的时候跟自己不爱的人结婚，
> 而其余三成的人最后只能把遗产留给自己的猫。
> 毕竟爱情跟书写都需要适时地留白。

尽管手动在中英文、数字之间加一个空格是一个好 [习惯](https://www.zhihu.com/question/19587406)，
然而在实际写作中，我们往往会忘记这个细节，因此在排版时，我们可以借助工具来自动完成这个工作。

本项目提供了一个 Python filter `_extensions/auto-correct.py` 来解决这个问题，
借助 [AutoCorrect](https://github.com/huacnlee/autocorrect) [@lee2024c] 的 Python 库，
「自动纠正」或「检查并建议」文案，给 CJK（中文、日语、韩语）与英文混写的场景，
补充正确的空格，纠正单词，同时尝试以安全的方式自动纠正标点符号等。

通过 `auto-correct.py` filter，可以实现修改 Pandoc AST，
在 Pandoc 转换过程中自动纠正中英文、数字之间的空格问题，
无需在得到目标格式后再进行修改，特别是对于某些格式（如 EPUB）来说，
无法在转换完成后再进行修改，因此这个 filter 的优势就体现出来了。

需要注意的是，LaTeX 和 Word 会自动处理中英文之间的空格，
因此无需使用这个 Python filter，只有在转换为其他格式时才需要使用，
例如 HTML、EPUB 等格式。
