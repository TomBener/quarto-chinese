-- Process quotes for Chinese bibliographies in HTML, EPUB and LaTeX

--- Copyright: © 2024–Present Tom Ben
--- License: MIT License

function is_chinese(text)
    return text:find("[\228-\233][\128-\191][\128-\191]")
end

function quotes_in_bib(block)
    local left_quote = "\226\128\156"  -- “
    local right_quote = "\226\128\157" -- ”

    local elements = block.c
    for i, el in ipairs(elements) do
        -- Check if element is a string containing either quote mark
        if el.t == "Str" and (el.text == left_quote or el.text == right_quote) then
            -- Get adjacent text to check for Chinese characters
            local prev_text = i > 1 and elements[i - 1].t == "Str" and elements[i - 1].text or ""
            local next_text = i < #elements and elements[i + 1].t == "Str" and elements[i + 1].text or ""

            -- Only replace quotes adjacent to Chinese text
            if is_chinese(prev_text) or is_chinese(next_text) then
                local replaced_text

                -- HTML/EPUB: Use Chinese corner brackets
                if FORMAT:match 'html' or FORMAT:match 'epub' then
                    replaced_text = (el.text == left_quote) and "「" or "」"
                    -- LaTeX: Use guillemets for intermediate processing
                elseif FORMAT:match 'latex' then
                    replaced_text = (el.text == left_quote) and "«" or "»"
                end

                if replaced_text then
                    elements[i] = pandoc.Str(replaced_text)
                end
            end
        end
    end
    return block
end

function Pandoc(doc)
    for i, block in ipairs(doc.blocks) do
        if block.t == "Div" then
            doc.blocks[i] = pandoc.walk_block(block, { Span = quotes_in_bib })
        end
    end
    return doc
end
