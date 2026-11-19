--- Convert body paragraphs to use "Body Text" style instead of "First Paragraph" style in DOCX output
--- This is particularly useful for Chinese documents where the "First Paragraph" style is not needed

--- Copyright: © 2025–Present Tom Ben
--- License: MIT License

-- Only body paragraphs are wrapped. The filter does not go into:
-- - footnotes (inline Note elements), which keep "Footnote Text";
-- - block quotes, which keep "Block Text";
-- - tables and figures;
-- - Divs that already set `custom-style` (e.g. `.right` / `.center` from text-align).
local function wrap_paragraphs(blocks)
    local out = pandoc.Blocks {}
    for _, block in ipairs(blocks) do
        if block.t == "Para" then
            out:insert(pandoc.Div(block, pandoc.Attr("", {}, { ["custom-style"] = "Body Text" })))
        elseif block.t == "Div" and not block.attributes["custom-style"] then
            block.content = wrap_paragraphs(block.content)
            out:insert(block)
        elseif block.t == "BulletList" or block.t == "OrderedList" then
            local items = pandoc.List {}
            for _, item in ipairs(block.content) do
                items:insert(wrap_paragraphs(item))
            end
            block.content = items
            out:insert(block)
        else
            out:insert(block)
        end
    end
    return out
end

function Pandoc(doc)
    -- If not DOCX output, return the document unchanged
    if FORMAT ~= "docx" then
        return nil
    end
    doc.blocks = wrap_paragraphs(doc.blocks)
    return doc
end
