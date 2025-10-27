-- Process quotes for Chinese bibliographies in HTML, EPUB, LaTeX and Typst

--- Copyright: © 2024–Present Tom Ben
--- License: MIT License

function is_chinese(text)
    return text:find("[\228-\233][\128-\191][\128-\191]")
end

local left_double_quote = "\226\128\156"  -- “
local right_double_quote = "\226\128\157" -- ”
local left_single_quote = "\226\128\152"  -- ‘
local right_single_quote = "\226\128\153" -- ’

local function stringify_inline(inline)
    if inline.t == "Str" then
        return inline.text
    end
    if pandoc.utils and pandoc.utils.stringify then
        return pandoc.utils.stringify(inline)
    end
    return ""
end

local function text_between(elements, start_idx, end_idx)
    if end_idx <= start_idx + 1 then
        return ""
    end
    local buffer = {}
    for j = start_idx + 1, end_idx - 1 do
        local text = stringify_inline(elements[j])
        if text ~= "" then
            table.insert(buffer, text)
        end
    end
    return table.concat(buffer)
end

local function find_closing(elements, start_idx, target)
    for j = start_idx, #elements do
        local el = elements[j]
        if el.t == "Str" and el.text == target then
            return j
        end
    end
    return nil
end

local function process_default_quotes(block)
    local elements = block.c
    for i, el in ipairs(elements) do
        if el.t == "Str" and (el.text == left_double_quote or el.text == right_double_quote) then
            local prev_text = i > 1 and elements[i - 1].t == "Str" and elements[i - 1].text or ""
            local next_text = i < #elements and elements[i + 1].t == "Str" and elements[i + 1].text or ""

            if is_chinese(prev_text) or is_chinese(next_text) then
                local replaced_text
                if FORMAT:match 'html' or FORMAT:match 'epub' then
                    replaced_text = (el.text == left_double_quote) and "「" or "」"
                elseif FORMAT:match 'latex' then
                    replaced_text = (el.text == left_double_quote) and "«" or "»"
                end

                if replaced_text then
                    elements[i] = pandoc.Str(replaced_text)
                end
            end
        end
    end
    return block
end

local function process_typst_quotes(block)
    local elements = block.c
    local processed = {}
    local quote_pairs = {
        {
            left = left_double_quote,
            right = right_double_quote,
            latin = '"',
            chinese_left = "«",
            chinese_right = "»"
        },
        {
            left = left_single_quote,
            right = right_single_quote,
            latin = "'",
            chinese_left = "‹",
            chinese_right = "›"
        }
    }

    for i = 1, #elements do
        if not processed[i] then
            local el = elements[i]
            if el.t == "Str" then
                for _, quote in ipairs(quote_pairs) do
                    if el.text == quote.left then
                        local closing_idx = find_closing(elements, i + 1, quote.right)
                        if closing_idx then
                            local enclosed_text = text_between(elements, i, closing_idx)
                            local has_chinese = is_chinese(enclosed_text or "")
                            if has_chinese then
                                elements[i] = pandoc.Str(quote.chinese_left)
                                elements[closing_idx] = pandoc.Str(quote.chinese_right)
                            else
                                elements[i] = pandoc.RawInline("typst", quote.latin)
                                elements[closing_idx] = pandoc.RawInline("typst", quote.latin)
                            end
                            processed[closing_idx] = true
                        end
                        break
                    elseif el.text == quote.right then
                        processed[i] = true
                    end
                end
            end
        end
    end
    return block
end

function quotes_in_bib(block)
    if FORMAT:match 'typst' then
        return process_typst_quotes(block)
    end
    return process_default_quotes(block)
end

function Pandoc(doc)
    for i, block in ipairs(doc.blocks) do
        if block.t == "Div" then
            doc.blocks[i] = pandoc.walk_block(block, { Span = quotes_in_bib })
        end
    end
    return doc
end
