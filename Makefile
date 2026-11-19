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

# Generate the DOCX reference template, and rebuild it when the files it is
# made from change (e.g. after the pandoc-docx submodule is updated)
# `[Content_Types].xml` is left out: make reads its brackets as a pattern
DOCX_TEMPLATE_SRC := $(shell find _styles/pandoc-docx/reference -type f ! -name '.DS_Store' ! -name '[[]*' 2>/dev/null)

$(DOCX_TEMPLATE): $(DOCX_TEMPLATE_SRC)
	@cd _styles/pandoc-docx && ./pandoc-docx.sh zip

.PHONY: docx-template
docx-template: $(DOCX_TEMPLATE)

# Render DOCX
docx: dependencies docx-template
	$(QUARTO) $@ $(FILTERS)

# Render HTML
html: dependencies
	$(QUARTO) $@ $(FILTERS) $(AUTOCORRECT)

# Render EPUB
epub: dependencies
	$(QUARTO) $@ $(FILTERS) $(AUTOCORRECT)

# Render PDF via LaTeX: $(1) is the output file, $(2) adds options
render_pdf = $(QUARTO) pdf $(FILTERS) --output $(1) $(2)

pdf: dependencies
	$(call render_pdf,index.pdf)

# Render PDF via Typst
typst: dependencies
	$(QUARTO) $@ $(FILTERS)

# Render PDF for print
.PHONY: print
print: dependencies
	$(call render_pdf,print.pdf,-V print)

# Render PDF with watermark
.PHONY: watermark
watermark: dependencies
	$(call render_pdf,watermark.pdf,-V watermark=true)

# Render Reveal.js slides
slides: dependencies
	@quarto render slides.qmd --to revealjs $(AUTOCORRECT)

# Clean up generated files
.PHONY: clean
clean:
	@$(RM) -r .quarto .jupyter_cache *_cache *_files _freeze contents outputs
