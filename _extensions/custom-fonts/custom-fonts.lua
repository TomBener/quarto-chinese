--- Use custom fonts in DOCX, HTML, EPUB, LaTeX and Typst

--- Copyright: © 2025–Present Tom Ben
--- License: MIT License

function Span(span)
    if span.classes:includes("fangsong") or span.classes:includes("kaiti") then
        local text = pandoc.utils.stringify(span.content)
        local isFangsong = span.classes:includes("fangsong")

        if FORMAT == "docx" then
            local fontName = isFangsong and "FZFangSong-Z02" or "FZKai-Z03"
            local openxml = string.format(
                '<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="%s" w:cs="Times New Roman" w:hint="eastAsia"/></w:rPr><w:t>%s</w:t></w:r>',
                fontName, text
            )
            return pandoc.RawInline("openxml", openxml)
        elseif FORMAT == "latex" or FORMAT == "pdf" then
            -- For LaTeX/PDF output, use font commands provided by `ctex`
            local fontCommand = isFangsong and "\\fangsong" or "\\kaishu"
            local latex = string.format("{%s %s}", fontCommand, text)
            return pandoc.RawInline("latex", latex)
        elseif FORMAT == "html" or FORMAT == "epub" then
            -- For HTML and EPUB output, use CSS font-family with fallback fonts
            -- Note: EPUB readers may override these settings based on user preferences
            local fontFamily = isFangsong and "FZFangSong-Z02, FangSong, STFangsong, 仿宋, serif" or
                "FZKai-Z03, KaiTi, STKaiti, 楷体, serif"
            span.attributes["style"] = string.format("font-family: %s;", fontFamily)
            return span
        elseif FORMAT == "typst" then
            -- For Typst output, use text function with font parameter
            local fontName = isFangsong and "FZFangSong-Z02" or "FZKai-Z03"
            local typst = string.format("#text(font: \"%s\")[%s]", fontName, text)
            return pandoc.RawInline("typst", typst)
        else
            -- For other formats, preserve the original span with classes
            return span
        end
    end
end
