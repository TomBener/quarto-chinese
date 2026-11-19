--- Modified from https://github.com/bcdavasconcelos/citetools/blob/main/_extensions/citetools/citation-backlinks.lua

--- citation-backlinks.lua – adds citation backlinks to the bibliography
-- https://github.com/tarleb/citation-backlinks
--- Copyright: © 2022–2024 John MacFarlane and Albert Krewinkel and Bernardo Vasconcelos
--- License: MIT – see LICENSE for details

-- Makes sure users know if their pandoc version is too old for this
-- filter.
PANDOC_VERSION:must_be_at_least '2.17'

-- cites is a table mapping citation item identifiers
-- to an array of cite identifiers
local cites = {}

-- counter for cite identifiers
local cite_number = 1

local function with_label(s, el)
  if FORMAT == "latex" then
    return { pandoc.RawInline("latex", "\\label{" .. s .. "}"), el }
  end
  if FORMAT == "typst" then
    return { el, pandoc.RawInline("typst", " #label(\"" .. s .. "\")") }
  end
  if FORMAT == "docx" or FORMAT == "html" then
    return { el }
  end
end

function Cite(el)
  local cite_id = "cite_" .. cite_number
  cite_number = cite_number + 1
  for _, citation in ipairs(el.citations) do
    -- Only process the citation if they are cited in the text, excluding 'nocite'!!
    if citation.mode == 'NormalCitation' then
      if cites[citation.id] then
        table.insert(cites[citation.id], cite_id)
      else
        cites[citation.id] = { cite_id }
      end
    end
  end
  if FORMAT == "typst" then
    return pandoc.Span(with_label(cite_id, el))
  else
    return pandoc.Span(with_label(cite_id, el), pandoc.Attr(cite_id))
  end
end

function append_inline(blocks, inlines)
  local last = blocks[#blocks]
  if last.t == 'Para' or last.t == 'Plain' then
    -- append to last block
    last.content:extend(inlines)
  else
    -- append as additional block
    blocks[#blocks + 1] = pandoc.Plain(inlines)
  end
  return blocks
end

-- LaTeX backlinks show page numbers. Several citations on one page would print
-- the same page more than once, so each page is compared in LaTeX with the page
-- of the previous citation and printed only when it differs. Citations come in
-- document order, so equal pages are always next to each other.
-- `\getpagerefnumber` comes from refcount, which hyperref loads.
local function latex_page_backlinks(cite_ids)
  local function page_link(id)
    return "\\hyperref[" .. id .. "]{\\pageref{" .. id .. "}}"
  end
  local parts = { page_link(cite_ids[1]) }
  for k = 2, #cite_ids do
    parts[#parts + 1] = "\\edef\\cblprev{\\getpagerefnumber{" .. cite_ids[k - 1] .. "}}"
      .. "\\edef\\cblcur{\\getpagerefnumber{" .. cite_ids[k] .. "}}"
      .. "\\ifx\\cblprev\\cblcur\\else, " .. page_link(cite_ids[k]) .. "\\fi"
  end
  return pandoc.RawInline("latex", table.concat(parts))
end

function Div(el)
  local citation_id = el.identifier:match("ref%-(.+)")

  if citation_id and FORMAT == "latex" then
    local cite_ids = cites[citation_id] or {}
    if #cite_ids > 0 then
      append_inline(el.content, pandoc.Inlines {
        pandoc.Space(), pandoc.Str("["), latex_page_backlinks(cite_ids), pandoc.Str("]")
      })
    end
    return el
  end

  if citation_id then
    local backlinks = pandoc.Inlines { pandoc.Space(), pandoc.Str("[") }
    for i, cite_id in ipairs(cites[citation_id] or {}) do
      local marker = pandoc.Str(i)
      if #backlinks > 2 then
        table.insert(backlinks, pandoc.Str(","))
        table.insert(backlinks, pandoc.Space())
      end
      table.insert(backlinks, pandoc.Link(marker, "#" .. cite_id))
    end
    if #backlinks > 2 then
      append_inline(el.content, backlinks .. { pandoc.Str("]") })
    end
    return el
  end
end
