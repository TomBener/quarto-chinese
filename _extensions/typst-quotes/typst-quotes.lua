-- Replace Chinese corner brackets with guillemets for Typst output.
-- The filter is run before citeproc to avoid touching bibliography

--- Copyright: © 2025–Present Tom Ben
--- License: MIT License

function Str(el)
    if not FORMAT:match('typst') then
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
