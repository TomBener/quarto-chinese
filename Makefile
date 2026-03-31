# `make` or `make all`: Render DOCX, HTML, PDF, EPUB and Reveal.js slides at once.
# `make docx`: Render DOCX.
# `make html`: Render HTML.
# `make epub`: Render EPUB.
# `make typst`: Render PDF via Typst.
# `make pdf`: Render PDF via LaTeX
# `make slides`: Render Reveal.js slides.
# `make print`: Render PDF for print.
# `make watermark`: Render PDF with watermark.
# `make citebib`: Extract all bibliographies cited as CSL JSON file `citebib.json`.
# `make normalize-itemkeys`: Rewrite Zotero item keys in `_contents/` to citation keys.
# `make citedoc`: Copy cited reference files to a specified directory.
# `make clean`: Remove auxiliary and output files.

# Render DOCX, HTML, EPUB, PDF (via LaTeX or Typst) at once
.PHONY: all
all: docx html epub typst pdf slides

# Extract all cited bibliographies
.PHONY: citebib
citebib:
	@python _extensions/citation-tools.py --extract

# Copy all cited files to a folder
.PHONY: citedoc
citedoc:
	@python _extensions/citation-tools.py --copy

# Target for generating and processing QMD files
.PHONY: dependencies
dependencies:
	@python _extensions/format-md.py

# Rewrite item-key citations in source files
.PHONY: normalize-itemkeys
normalize-itemkeys:
	@python _extensions/citation-tools.py --normalize-itemkeys

# Variables
# `-L _extensions/remove-doi-hyperlinks.lua` can be added to remove DOI hyperlinks
# `-L _extensions/capitalize-subtitle.lua` can be added to capitalize subtitles,
# as required by APA or similar styles
# Remove `--filter _extensions/sort-bib.py` if using numeric citation style
QUARTO := @quarto render index.qmd --to
FILTERS := -L _extensions/localize-cnbib.lua \
	-L _extensions/cnbib-quotes.lua \
	-L _extensions/docx-table-styles.lua \
	--filter _extensions/sort-bib.py
AUTOCORRECT := --filter _extensions/auto-correct.py

DOCX_TEMPLATE := _styles/pandoc-docx/reference.docx

# Generate DOCX reference template if it doesn't exist
.PHONY: docx-template
docx-template:
	@if [ ! -f $(DOCX_TEMPLATE) ]; then \
		cd _styles/pandoc-docx && ./pandoc-docx.sh zip; \
	fi

# Render DOCX
docx: dependencies docx-template
	$(QUARTO) $@ $(FILTERS)

# Render HTML
html: dependencies
	$(QUARTO) $@ $(FILTERS) $(AUTOCORRECT)

# Render EPUB
epub: dependencies
	$(QUARTO) $@ $(FILTERS) $(AUTOCORRECT)

# Render PDF via LaTeX
pdf: dependencies
	$(QUARTO) $@ $(FILTERS) $(if $(findstring pdf,$@),--output $(PDF_OUTPUT) $(PDF_OPTION))

# Render PDF via Typst
typst: dependencies
	$(QUARTO) $@ $(FILTERS)

# Initial PDF settings
PDF_OUTPUT := index.pdf

# Special handling for print PDF
.PHONY: print
print: PDF_OPTION := -V print
print: PDF_OUTPUT := print.pdf
print: pdf

# Special handling for watermark PDF
.PHONY: watermark
watermark: PDF_OPTION := -V watermark=true
watermark: PDF_OUTPUT := watermark.pdf
watermark: pdf

# Render Reveal.js slides
slides: dependencies
	@quarto render slides.qmd --to revealjs $(AUTOCORRECT)

# Clean up generated files
.PHONY: clean
clean:
	@$(RM) -r .quarto .jupyter_cache *_cache *_files _freeze contents outputs
