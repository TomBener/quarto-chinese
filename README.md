# Quarto Template for Chinese Academic Writing

[![Publish](https://github.com/TomBener/quarto-chinese/actions/workflows/quarto-publish.yml/badge.svg)](https://github.com/TomBener/quarto-chinese/actions/workflows/quarto-publish.yml)

[中文介绍](https://sspai.com/post/97056)

This repository provides a comprehensive guide and toolset for writing academic
papers in Chinese, such as the localization and sorting of Chinese citations and
bibliographies, conversion of Chinese quotation marks, and correcting spaces between
Chinese and English characters. With the help of these templates and scripts,
you can write your academic papers in Markdown, and convert them into various
formats like Word, HTML, LaTeX/PDF, Typst/PDF, EPUB, and Reveal.js slides via Quarto.

## Features

- **Render Multiple Formats**: Render DOCX, HTML, PDF (LaTeX), PDF (Typst), EPUB, and Reveal.js slides at once with the same source file, and PDF can be customized for print or with watermark.
- **Localize Chinese Bibliographies**: Change `et al.` to `等` and other English localization strings to Chinese in citations and references, both author-date and numeric styles are supported.
- **Sort Chinese Bibliographies**: Sort Chinese bibliographies by Pinyin while keeping non-Chinese entries alphabetized, and customize whether Chinese entries appear first or last.
- **Correct Chinese Quotes**: Automatically tailor quotation marks for DOCX, HTML/EPUB bibliographies, LaTeX body text, LaTeX headings, and Typst outputs.
- **Correct Spaces**: Improve copywriting, correct spaces, words, and punctuations between CJK and Western text.
- **Extract Bibliographies**: Filter cited references to a CSL JSON file and copy cited attachments to a specified directory.
- **Generate Backlinks**: Generate backlinks for bibliography entries to the corresponding citations.
- **Remove DOI Hyperlinks**: Remove DOI hyperlinks formatted by `citeproc` if they are not needed in the bibliography.
- **Align Text Blocks**: Right- or center-align specific text in DOCX, PDF, HTML, EPUB, and Typst.
- **Custom Fonts**: Use custom fonts in DOCX, PDF, HTML, EPUB, and Typst.

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

- `make` or `make all`: Render DOCX, HTML, EPUB, PDF (LaTeX), PDF (Typst) and Reveal.js slides at once.
- `make docx`: Render DOCX.
- `make html`: Render HTML.
- `make pdf`: Render PDF via LaTeX.
- `make typst`: Render PDF via Typst.
- `make epub`: Render EPUB.
- `make slides`: Render Reveal.js slides.
- `make print`: Render PDF for print.
- `make watermark`: Render PDF with watermark.
- `make citebib`: Extract all cited references into `citebib.json` (filtered CSL JSON).
- `make citedoc`: Copy cited reference files to a specified directory.
- `make clean`: Remove auxiliary and output files.

## Extensions

> [!TIP]
> These extensions can also be used individually in your Pandoc or Quarto project.

- [auto-correct](_extensions/auto-correct.py): Improve copywriting, correct spaces, words, and punctuations between CJK and English with AutoCorrect.
- [citation-backlinks](_extensions/citation-backlinks.lua): Generate backlinks for bibliography entries to the corresponding citations.
- [capitalize-subtitle](_extensions/capitalize-subtitle.lua): Capitalize the first word after colons or em dashes inside bibliography subtitles, following APA style.
- [citation-tools](_extensions/citation-tools.py): Extract citation keys to a filtered CSL JSON file, and copy cited reference files to a specified directory.
- [cnbib-quotes](_extensions/cnbib-quotes.lua): Process quotes for Chinese bibliographies in HTML and EPUB outputs.
- [confetti](_extensions/confetti/): Send some 🎊 in Reveal.js slides.
- [custom-fonts](_extensions/custom-fonts/): Use custom fonts in DOCX, PDF, HTML, EPUB, and Typst.[^epub]
- [docx-quotes](_extensions/docx-quotes/): Convert straight angle quotation marks to curly quotation marks in DOCX.
- [format-md](_extensions/format-md.py): Preprocess Markdown files for conversion with Quarto.
- [get-bib](_extensions/get-bib.lua): Extract all bibliographies cited in the document as a BibLaTeX file.[^bib]
- [ignore-softbreaks](_extensions/ignore-softbreaks/): Emulate Pandoc’s extension `east_asian_line_breaks` [in Quarto](https://github.com/quarto-dev/quarto-cli/issues/8520).
- [latex-body-quotes](_extensions/latex-body-quotes/): Replace Chinese corner quotes with guillemets in LaTeX body text.
- [latex-header-quotes](_extensions/latex-header-quotes/): Keep LaTeX/PDF headers readable while rendering body quotes correctly.
- [links-to-citations](_extensions/links-to-citations/): Remove local links but keep the link text as normal citations.
- [localize-cnbib](_extensions/localize-cnbib.lua): Localize Chinese bibliographies, change `et al.` to `等` and other English localization strings to Chinese.
- [no-first-paragraph](_extensions/no-first-paragraph/): Remove the `First Paragraph` style by applying `Body Text` to all paragraphs in DOCX.
- [remove-doi-hyperlinks](_extensions/remove-doi-hyperlinks.lua): Remove [DOI hyperlinks](https://github.com/jgm/pandoc/issues/10393) formatted by `citeproc` in the bibliography.[^doi]
- [remove-spaces](_extensions/remove-spaces/): Remove spaces before or after Chinese characters in DOCX.
- [sort-bib](_extensions/sort-bib.py): Sort bibliographies by grouping Chinese entries (sorted by Pinyin) and non-Chinese entries (alphabetical).
- [text-align](_extensions/text-align/): Right- or center-align specific blocks across DOCX, PDF, HTML, EPUB, and Typst outputs.
- [typst-quotes](_extensions/typst-quotes/): Replace Chinese corner quotes for Typst output so the PDF looks correct.

## License

This project is licensed under the MIT License, see the [LICENSE](LICENSE) file for details.

[^bib]: The `get-bib` tool is based on Pandoc, for a better and more flexible implementation, use `citation-tools` instead.
[^doi]: This Lua filter is disabled by default. To enable it, add `-L _extensions/remove-doi-hyperlinks.lua` to the `FILTERS` variable in the Makefile, and remove `<text variable="DOI" prefix="DOI: "/>` in the CSL file.
[^epub]: Note that EPUB readers may override the font settings based on user preferences.
