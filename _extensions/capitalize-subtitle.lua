--[[
capitalize-subtitle – Capitalize first letter after colons and em dashes in bibliography entries

This filter capitalizes the first letter after colons and em dashes in bibliography
entries, following APA and similar styles that require subtitle capitalization.

It only processes paragraphs within bibliography divs
Must be run after Citeproc

Copyright: © 2025–present Tom Ben
License: MIT
]]

local EXTRA_PUNCT = "“”‘’«»‹›„‟「」『』﹁﹂﹃﹄–—‐"
local APOSTROPHES = "'’"
local HYPHENS = "%-‐"
local AFTER_PUNCT_CLASS = "%s%p" .. EXTRA_PUNCT
local WORD_TAIL_PATTERN = "[%a" .. APOSTROPHES .. HYPHENS .. "]*"
local TRIGGER_TAIL_PATTERN = "[^%a" .. APOSTROPHES .. HYPHENS .. "]*$"

local function is_punctuation(char)
    if not char or char == "" then
        return true
    end
    if char:match("[%s%p]") then
        return true
    end
    return EXTRA_PUNCT:find(char, 1, true) ~= nil
end

local INTERNAL_MARKS = {
    {
        mark = ":",
        skip = function(punct)
            return punct == "" or punct:find("/")
        end,
    },
    { mark = "—" },
}

local function capitalize_internal_marks(text)
    for _, config in ipairs(INTERNAL_MARKS) do
        local pattern = config.mark .. "([" .. AFTER_PUNCT_CLASS .. "]*)([a-z])"
        text = text:gsub(pattern, function(punct, letter)
            -- Require some separation after colon (e.g., space or quote) to avoid URLs and protocols
            if config.skip and config.skip(punct) then
                return config.mark .. punct .. letter
            end
            return config.mark .. punct .. letter:upper()
        end)
    end

    return text
end

--- Capitalize first letter if it's lowercase.
--- Returns transformed string and a boolean indicating whether capitalization occurred.
local function capitalize_first(str)
    if not str or str == "" then
        return str, false
    end
    -- Separate leading punctuation/spaces (including common typographic quotes) from the word
    local leading, remainder = str:match("^([%s%p" .. EXTRA_PUNCT .. "]*)(.*)")
    if not remainder or remainder == "" then
        return str, false
    end
    local already_capitalized = remainder:match("^([A-Z]" .. WORD_TAIL_PATTERN .. ")")
    if already_capitalized then
        return str, true
    end
    local word, suffix = remainder:match("^([a-z]" .. WORD_TAIL_PATTERN .. ")(.*)")
    if not word then
        local first_char = remainder:sub(1, 1)
        if not is_punctuation(first_char) then
            return str, true
        end
        return str, false
    end
    -- Only capitalize when the word is purely alphabetic (with optional hyphen/apostrophe)
    -- and is followed by punctuation/space or nothing. This avoids changing items like e2105061118.
    local next_char = suffix:sub(1, 1)
    if suffix ~= "" and not is_punctuation(next_char) then
        return str, false
    end
    return leading .. word:sub(1, 1):upper() .. word:sub(2) .. suffix, true
end

local process_inlines --- forward declaration for mutual recursion

local SIMPLE_WRAPPERS = {
    Emph = pandoc.Emph,
    Strong = pandoc.Strong,
    SmallCaps = pandoc.SmallCaps,
}

local function rebuild_container(elem, capitalize_next)
    if not elem.content then
        return nil, capitalize_next
    end

    local processed
    processed, capitalize_next = process_inlines(elem.content, capitalize_next)

    local wrap = SIMPLE_WRAPPERS[elem.t]
    if wrap then
        return wrap(processed), capitalize_next
    elseif elem.t == "Span" then
        return pandoc.Span(processed, elem.attr), capitalize_next
    elseif elem.t == "Quoted" then
        return pandoc.Quoted(elem.quotetype, processed), capitalize_next
    end

    return nil, capitalize_next
end

--- Process a list of inlines recursively: capitalize word after colon or em dash.
-- Returns processed inline list and updated capitalize_next flag.
function process_inlines(inlines_list, capitalize_next)
    local result = {}
    capitalize_next = capitalize_next or false

    for _, elem in ipairs(inlines_list) do
        if elem.t == "Str" then
            local text = elem.text

            text = capitalize_internal_marks(text)

            if capitalize_next then
                local new_text, consumed = capitalize_first(text)
                text = new_text
                capitalize_next = not consumed
            end

            if text:find(":" .. TRIGGER_TAIL_PATTERN) or text:find("—" .. TRIGGER_TAIL_PATTERN) then
                capitalize_next = true
            end

            result[#result + 1] = pandoc.Str(text)
        elseif elem.t == "Space" or elem.t == "SoftBreak" or elem.t == "LineBreak" then
            result[#result + 1] = elem
        else
            local rebuilt
            rebuilt, capitalize_next = rebuild_container(elem, capitalize_next)
            if rebuilt then
                result[#result + 1] = rebuilt
            else
                result[#result + 1] = elem
                capitalize_next = false
            end
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
