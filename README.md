# Quarto Template for Chinese Academic Writing

[![Publish](https://github.com/TomBener/quarto-chinese/actions/workflows/quarto-publish.yml/badge.svg)](https://github.com/TomBener/quarto-chinese/actions/workflows/quarto-publish.yml)

[中文介绍](https://sspai.com/post/97056)

This repository provides a comprehensive guide and toolset for writing academic
papers in Chinese, such as the localization and sorting of Chinese citations and
bibliographies, conversion of Chinese quotation marks, and correcting spaces between
Chinese and English characters. With the help of these templates and scripts,
you can write your academic papers in Markdown, and convert them into various
formats like Word, HTML, LaTeX, PDF, and EPUB via Quarto.

## Features

- **Render Multiple Formats**: Render DOCX, HTML, PDF, EPUB, and Reveal.js slides at once with the same source file, and PDF can be customized for print or with watermark.
- **Localize Chinese Bibliographies**: Change `et al.` to `等` and other English localization strings to Chinese in citations and references, both author-date and numeric styles are supported.
- **Sort Chinese Bibliographies**: Sort Chinese bibliographies by Pinyin, and can be customized to sort Chinese entries first or last.
- **Correct Chinese Quotes**: Tweak Chinese quotes for sophisticated typesetting.
- **Correct Spaces**: Improve copywriting, correct spaces, words, and punctuations between CJK.
- **Extract Bibliographies**: Extract all bibliographies cited in the document as a BibTeX/BibLaTeX file, and copy cited reference files to a specified directory.
- **Generate Backlinks**: Generate backlinks for bibliography entries to the corresponding citations.
- **Remove DOI Hyperlinks**: Remove DOI hyperlinks formatted by `citeproc` if they are not needed in the bibliography.
- **Right Align Text**: Right align certain text in DOCX, PDF, HTML and EPUB.
- **Custom Fonts**: Use custom fonts in DOCX, PDF, HTML and EPUB.[^epub]

## Prerequisites

- [Quarto](https://quarto.org), with [Pandoc](https://pandoc.org) included, and
  you can install TinyTeX via `quarto install tinytex --update-path`.
- Python, and the following packages:
  - [autocorrect_py](https://github.com/huacnlee/autocorrect/tree/main/autocorrect-py)
  - [pypinyin](https://github.com/mozillazg/python-pinyin)
  - [panflute](https://github.com/sergiocorreia/panflute)
- R, and the following packages:
  - [rmarkdown](https://github.com/rstudio/rmarkdown)
  - [knitr](https://github.com/yihui/knitr)
  - [ggplot2](https://github.com/tidyverse/ggplot2)

## Usage

> [!NOTE]
> Currently [Lua filters](https://github.com/quarto-dev/quarto-cli/issues/7888) cannot be run after `citeproc` in Quarto.
> As a workaround, some extensions are run on the command line in the Makefile. This can be improved in the future.

This project uses a [Makefile](Makefile) to manage the build process. Here are the available commands:

- `make` or `make all`: Render DOCX, HTML, PDF, EPUB and Reveal.js slides at once.
- `make docx`: Render DOCX.
- `make html`: Render HTML.
- `make pdf`: Render PDF.
- `make epub`: Render EPUB.
- `make slides`: Render Reveal.js slides.
- `make print`: Render PDF for print.
- `make watermark`: Render PDF with watermark.
- `make citebib`: Extract all bibliographies cited as BibLaTeX file `citebib.bib`.
- `make citedoc`: Copy cited reference files to a specified directory.
- `make clean`: Remove auxiliary and output files.

## Extensions

> [!TIP]
> These extensions can also be used individually in your Pandoc or Quarto project.

- [auto-correct](_extensions/auto-correct.py): Improve copywriting, correct spaces, words, and punctuations between CJK and English with AutoCorrect.
- [citation-backlinks](_extensions/citation-backlinks.lua): Generate backlinks for bibliography entries to the corresponding citations.
- [citation-tools](_extensions/citation-tools.py): Extract citation keys from Markdown files, and copy cited reference files to a specified directory.
- [cnbib-quotes](_extensions/cnbib-quotes.lua): Process quotes for Chinese bibliographies in HTML and EPUB outputs.
- [confetti](_extensions/confetti/): Send some 🎊 in Reveal.js slides.
- [custom-fonts](_extensions/custom-fonts/): Use custom fonts in DOCX, PDF, HTML and EPUB.
- [docx-quotes](_extensions/docx-quotes/): Convert straight angle quotation marks to curly quotation marks in DOCX.
- [format-md](_extensions/format-md.py): Preprocess Markdown files for conversion with Quarto.
- [get-bib](_extensions/get-bib.lua): Extract all bibliographies cited in the document as a BibLaTeX file.[^bib]
- [ignore-softbreaks](_extensions/ignore-softbreaks/): Emulate Pandoc’s extension `east_asian_line_breaks` [in Quarto](https://github.com/quarto-dev/quarto-cli/issues/8520).
- [latex-quotes](_extensions/latex-quotes/): Replaces straight quotes with German quotes for intermediate in LaTeX output, and specific processing for headers to avoid issues in PDF bookmarks.
- [links-to-citations](_extensions/links-to-citations/): Remove local links but keep the link text as normal citations.
- [localize-cnbib](_extensions/localize-cnbib.lua): Localize Chinese bibliographies, change `et al.` to `等` and other English localization strings to Chinese.
- [no-first-paragraph](_extensions/no-first-paragraph/): Remove the `First Paragraph` style by applying `Body Text` to all paragraphs in DOCX.
- [remove-doi-hyperlinks](_extensions/remove-doi-hyperlinks.lua): Remove [DOI hyperlinks](https://github.com/jgm/pandoc/issues/10393) formatted by `citeproc` in the bibliography.[^doi]
- [remove-spaces](_extensions/remove-spaces/): Remove spaces before or after Chinese characters in DOCX.
- [right-align](_extensions/right-align/): Right align certain text in DOCX, PDF, HTML and EPUB.
- [sort-cnbib](_extensions/sort-cnbib.py): Sort Chinese bibliographies by Pinyin, and can be customized to sort Chinese entries first or last.

## License

This project is licensed under the MIT License, see the [LICENSE](LICENSE) file for details.

[^bib]: The `get-bib` tool is based on Pandoc, for a better and more flexible implementation, use `citation-tools` instead.
[^doi]: This Lua filter is disabled by default. To enable it, add `-L _extensions/remove-doi-hyperlinks.lua` to the `FILTERS` variable in the Makefile, and remove `<text variable="DOI" prefix="DOI: "/>` in the CSL file.
[^epub]: Note that EPUB readers may override the font settings based on user preferences.
