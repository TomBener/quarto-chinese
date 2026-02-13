# 参考文献本地化

Pandoc 使用 CSL（[Citation Style Language](https://citationstyles.org/)）来格式化参考文献信息，
然而 CSL 不支持多语言的参考文献格式化，例如在 Pandoc 中将语言设置为 `en-US` 时，
所有文献的本地化字符都会被转换为英文，例如 `et al.`、`vol.`、`ed.` 等。

本项目使用 Lua filter `_extensions/localize-cnbib.lua` 来解决这个问题。

## "et al." 替换为「等」

在 author-date 样式中，正文中超过一个作者时，
只显示第一作者，英文文献后用 `et al.` 表示
[@acemoglu2019; @gao2023a; @pang2004;
@krewinkel2017; @flint2018]。
对于中文文献，`et al.` 则应该替换为 `等`
[@qinhui2019; @yishabai2018; @jiazhen1979; @zhaojizhi2024]。

对于参考文献表来说，超过 3 个作者时，也应该使用 `et al.` 或 `等` 来表示
[@lushaowei2015; @yang2023e]，
以及更多例子
[@acemoglu2019; @geyanfeng2020;
@caojingjing2020; @amarante2022; @daviet2022]。

## "vol." 替换为「第X卷」

在中文文献中，`vol.` 应该替换为 `第 X 卷`
[@gezhaoguang2000a; @zgrmdxqsyjs1983]。
但英文文献中 `vol.` 仍然需要保留
[@fletcher1978; @fairbank1968a; @fletcher1978a; @fletcher1978b]。

## "ed." 和 "eds." 替换为「编」

在中文文献中，`eds.` 和 `ed.` 应该替换为 `编`
[@lihongzhang2007; @liangqichao2018; @yishabai2018;
@feixiaotong1989; @zuozongtang1986]，
不过 `ed.` 既可以表示 `编`，也可以表示 `版`，相对比较复杂，
请参考下面的例子。

## "ed." 替换为「编」或「版」

`ed.` 既可以表示 `编`
[@feixiaotong1989; @zuozongtang1986]，
也可以表示 `版`
[@qinhui2019; @taoxisheng2016]，
虽然非常灵活，但也给替换带来了一定的困难，
不过好在判断条件比较明确。

## "tran." 和 "trans." 替换为「译」

在中文文献中，`tran.` 和 `trans.` 应该替换为 `译`
[@hanqilan2004; @yishabai2018; @maikeerhekete2012; @ludefu2019]。

值得一提的是，Lua filter `_extensions/localize-cnbib.lua` 同时
支持 author-date 和 numeric 两种引用格式，
并且在 `link-citation` 开启或关闭时都能正常工作。
当然，上述替换只考虑了常见中文文献字符本地化的情况，
如果有其他字符需要本地化，请自行修改 `_extensions/localize-cnbib.lua` 文件，
或者提交 issue 给我。

需要注意，本项目中 `gb-author-date.csl` 和 `gb-numeric.csl` 是
我根据 Zotero Styles 网站下载的 CSL 样式文件修改而来。
与原始样式文件相比，我修改之后的样式文件更加符合 GB/T 7714-2015 的标准，
`_extensions/localize-cnbib.lua` 也是根据这两个样式文件的格式来编写的，
因此 `_extensions/localize-cnbib.lua` 可能无法正常工作在其他 CSL 样式文件上。
