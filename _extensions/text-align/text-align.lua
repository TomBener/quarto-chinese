--- Align the content of a div (right/center)

--- Copyright: © 2025–Present Tom Ben
--- License: MIT License

local function wrap_with(blocks, format, start, finish)
    local content = {}
    table.insert(content, pandoc.RawBlock(format, start))
    for _, block in ipairs(blocks) do
        table.insert(content, block)
    end
    table.insert(content, pandoc.RawBlock(format, finish))
    return content
end

local function align_block(el, align)
    if FORMAT == "docx" then
        if align == "right" then
            el.attributes['custom-style'] = 'Right Align'
        else
            el.attributes['custom-style'] = 'Center Align'
        end
        return el
    elseif FORMAT == "latex" then
        if align == "right" then
            return wrap_with(el.content, "latex", "\\begin{flushright}", "\\end{flushright}")
        else
            return wrap_with(el.content, "latex", "\\begin{center}", "\\end{center}")
        end
    elseif FORMAT == "typst" then
        return wrap_with(el.content, "typst", "#align(" .. align .. ")[", "]")
    elseif FORMAT == "html" or FORMAT == "epub" then
        el.attributes['style'] = "text-align: " .. align .. ";"
        return el
    else
        return el
    end
end

function Div(el)
    if el.classes:includes("right") then
        return align_block(el, "right")
    elseif el.classes:includes("center") then
        return align_block(el, "center")
    end
end
