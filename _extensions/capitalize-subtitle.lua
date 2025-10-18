--[[
capitalize-subtitle – Capitalize first letter after colons and em dashes in bibliography entries

This filter capitalizes the first letter after colons and em dashes in bibliography
entries, following APA and similar styles that require subtitle capitalization.

It only processes paragraphs within bibliography divs
Must be run after Citeproc

Copyright: © 2025–present Tom Ben
License: MIT
]]

--- Capitalize first letter if it's lowercase
local function capitalize_first(str)
    if not str or str == "" then
        return str
    end
    -- Separate leading punctuation/spaces from the word to evaluate
    local leading, remainder = str:match("^([%s%p]*)(.*)")
    if not remainder or remainder == "" then
        return str
    end
    local word, suffix = remainder:match("^([a-z][%a%-']*)(.*)")
    if not word then
        return str
    end
    -- Only capitalize when the word is purely alphabetic (with optional hyphen/apostrophe)
    -- and is followed by punctuation/space or nothing. This avoids changing items like e2105061118.
    local next_char = suffix:sub(1, 1)
    if suffix ~= "" and not next_char:match("[%s%p]") then
        return str
    end
    return leading .. word:sub(1, 1):upper() .. word:sub(2) .. suffix
end

--- Process a list of inlines recursively: capitalize word after colon or em dash.
-- Returns processed inline list and updated capitalize_next flag.
local function process_inlines(inlines_list, capitalize_next)
    local result = {}
    capitalize_next = capitalize_next or false

    for _, elem in ipairs(inlines_list) do
        if elem.t == "Str" then
            local text = elem.text

            -- Handle em dash followed by text (—word or word—word)
            text = text:gsub("(—)([a-z])", function(dash, letter)
                return dash .. letter:upper()
            end)

            if capitalize_next then
                text = capitalize_first(text)
                capitalize_next = false
            end

            if text:match(":$") or text:match("—$") then
                capitalize_next = true
            end

            result[#result + 1] = pandoc.Str(text)
        elseif elem.t == "Space" or elem.t == "SoftBreak" or elem.t == "LineBreak" then
            result[#result + 1] = elem
        elseif elem.t == "Emph" then
            local processed_content
            processed_content, capitalize_next = process_inlines(elem.content, capitalize_next)
            result[#result + 1] = pandoc.Emph(processed_content)
        else
            result[#result + 1] = elem
            capitalize_next = false
        end
    end

    return result, capitalize_next
end

--- Process paragraphs: capitalize word after colon or em dash
local function process_para(para)
    local processed_content = process_inlines(para.content, false)
    return pandoc.Para(processed_content)
end

--- Only process divs with bibliography classes
function Div(div)
    -- Check for bibliography-related classes
    if div.classes:includes("references") or
        div.classes:includes("csl-bib-body") or
        div.classes:includes("csl-entry") then
        return pandoc.walk_block(div, { Para = process_para })
    end
end
