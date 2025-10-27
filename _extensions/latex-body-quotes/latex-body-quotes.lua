-- Replace Chinese corner brackets with guillemets for LaTeX output.
-- This filter is responsible for body text only; header handling lives in latex-header-quotes.
-- The filter is run before citeproc to avoid touching bibliography, which is handled separately in cnbib-quotes.

--- Copyright: © 2025–Present Tom Ben
--- License: MIT License

function Str(el)
    if not FORMAT:match('latex') then
        return el
    end

    local replacements = {
        ['「'] = '«',
        ['」'] = '»',
        ['『'] = '‹',
        ['』'] = '›'
    }

    for original, replacement in pairs(replacements) do
        el.text = el.text:gsub(original, replacement)
    end

    return el
end
