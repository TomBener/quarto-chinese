--- Use custom fonts in DOCX, HTML, EPUB, LaTeX and Typst

--- Copyright: © 2025–Present Tom Ben
--- License: MIT License

local FONTS = {
    fangsong = {
        docx = "FZFangSong-Z02",
        latex = "\\fangsong",
        css = "FZFangSong-Z02, FangSong, STFangsong, 仿宋, serif",
        typst = "FZFangSong-Z02"
    },
    kaiti = {
        docx = "FZKai-Z03",
        latex = "\\kaishu",
        css = "FZKai-Z03, KaiTi, STKaiti, 楷体, serif",
        typst = "FZKai-Z03"
    }
}

local function xml_escape(text)
    return (text:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"))
end

-- DOCX: a run cannot hold other inlines, so the span content is rewritten as
-- raw runs that carry the font. Bold, italic, underline, strikeout, small caps,
-- superscript, subscript and links inside the span are kept by writing the
-- matching run properties. Code, math, citations and notes are left to pandoc
-- and use the default font.

-- Run properties in the order the OOXML schema requires
local RPR_ORDER = { "rStyle", "b", "i", "smallCaps", "strike", "u", "vertAlign" }

local function with_prop(props, key, value)
    local copy = {}
    for k, v in pairs(props) do
        copy[k] = v
    end
    copy[key] = value
    return copy
end

-- docx-quotes cannot see text inside these raw runs, so its corner-quote
-- replacement is repeated here
local DOCX_QUOTES = { ["「"] = "“", ["」"] = "”", ["『"] = "‘", ["』"] = "’" }

local function docx_run(text, font, props)
    for corner, curly in pairs(DOCX_QUOTES) do
        text = text:gsub(corner, curly)
    end
    local rpr = {}
    if props.rStyle then
        rpr[#rpr + 1] = '<w:rStyle w:val="' .. props.rStyle .. '"/>'
    end
    rpr[#rpr + 1] = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="'
        .. font .. '" w:cs="Times New Roman" w:hint="eastAsia"/>'
    for _, key in ipairs(RPR_ORDER) do
        local value = props[key]
        if key ~= "rStyle" and value then
            if value == true then
                rpr[#rpr + 1] = "<w:" .. key .. "/>"
            else
                rpr[#rpr + 1] = "<w:" .. key .. ' w:val="' .. value .. '"/>'
            end
        end
    end
    return pandoc.RawInline("openxml", '<w:r><w:rPr>' .. table.concat(rpr)
        .. '</w:rPr><w:t xml:space="preserve">' .. xml_escape(text) .. "</w:t></w:r>")
end

local STYLE_PROPS = {
    Emph = { "i", true },
    Strong = { "b", true },
    Underline = { "u", "single" },
    Strikeout = { "strike", true },
    SmallCaps = { "smallCaps", true },
    Superscript = { "vertAlign", "superscript" },
    Subscript = { "vertAlign", "subscript" }
}

local function docx_runs(inlines, font, props, out)
    for _, el in ipairs(inlines) do
        local style = STYLE_PROPS[el.t]
        if el.t == "Str" then
            out:insert(docx_run(el.text, font, props))
        elseif el.t == "Space" or el.t == "SoftBreak" then
            out:insert(docx_run(" ", font, props))
        elseif el.t == "LineBreak" then
            out:insert(pandoc.RawInline("openxml", "<w:r><w:br/></w:r>"))
        elseif style then
            docx_runs(el.content, font, with_prop(props, style[1], style[2]), out)
        elseif el.t == "Span" then
            docx_runs(el.content, font, props, out)
        elseif el.t == "Quoted" then
            local single = el.quotetype == "SingleQuote"
            out:insert(docx_run(single and "‘" or "“", font, props))
            docx_runs(el.content, font, props, out)
            out:insert(docx_run(single and "’" or "”", font, props))
        elseif el.t == "Link" then
            local content = pandoc.Inlines {}
            docx_runs(el.content, font, with_prop(props, "rStyle", "Hyperlink"), content)
            el.content = content
            out:insert(el)
        else
            out:insert(el)
        end
    end
    return out
end

-- Put raw markup before and after the span content. Pandoc still writes the
-- content itself, so special characters are escaped and emphasis, links and
-- citations inside the span are kept.
local function wrap_inlines(format, before, content, after)
    local result = pandoc.Inlines { pandoc.RawInline(format, before) }
    result:extend(content)
    result:insert(pandoc.RawInline(format, after))
    return result
end

function Span(span)
    local font
    if span.classes:includes("fangsong") then
        font = FONTS.fangsong
    elseif span.classes:includes("kaiti") then
        font = FONTS.kaiti
    else
        return nil
    end

    if FORMAT == "docx" then
        return docx_runs(span.content, font.docx, {}, pandoc.Inlines {})
    elseif FORMAT == "latex" then
        -- For LaTeX/PDF output, use font commands provided by `ctex`
        return wrap_inlines("latex", "{" .. font.latex .. " ", span.content, "}")
    elseif FORMAT == "html" or FORMAT == "epub" then
        -- For HTML and EPUB output, use CSS font-family with fallback fonts
        -- Note: EPUB readers may override these settings based on user preferences
        span.attributes["style"] = "font-family: " .. font.css .. ";"
        return span
    elseif FORMAT == "typst" then
        -- For Typst output, use text function with font parameter
        return wrap_inlines("typst", '#text(font: "' .. font.typst .. '")[', span.content, "]")
    end
    -- For other formats, preserve the original span with classes
    return nil
end
