--- Convert all paragraphs to use "Body Text" style instead of "First Paragraph" style in DOCX output
--- This is particularly useful for Chinese documents where the "First Paragraph" style is not needed

--- Copyright: © 2025–Present Tom Ben
--- License: MIT License

function Para(para)
    -- If not DOCX output, return element unchanged
    if FORMAT ~= 'docx' then
        return para
    end

    -- Wrap paragraph in a Div with custom-style attribute set to "Body Text"
    -- This ensures all paragraphs use the "Body Text" style instead of "First Paragraph"
    return pandoc.Div(para, pandoc.Attr("", {}, { ["custom-style"] = "Body Text" }))
end
