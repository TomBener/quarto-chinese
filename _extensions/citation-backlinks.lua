--- Modified from https://github.com/bcdavasconcelos/citetools/blob/main/_extensions/citetools/citation-backlinks.lua

--- Todo: even with link-citations and link-fields turned off, citation-backlinks still adds a single backlink to each reference in the final bibliography div.

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

function Div(el)
  local citation_id = el.identifier:match("ref%-(.+)")
  local tex_return_link = pandoc.RawInline("latex", "\\Acrobatmenu{GoBack}{$\\hookleftarrow$}")

  if citation_id then
    local backlinks = pandoc.Inlines { pandoc.Space(), pandoc.Str("[") }
    if FORMAT == "latex" then
      table.insert(backlinks, tex_return_link)
    end

    for i, cite_id in ipairs(cites[citation_id] or {}) do
      local marker = pandoc.Str(i)
      if FORMAT == "latex" then
        marker = pandoc.RawInline("latex", "\\pageref{" .. cite_id .. "}")
      end
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
