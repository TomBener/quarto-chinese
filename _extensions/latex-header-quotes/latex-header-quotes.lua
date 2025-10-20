-- Prepare LaTeX headers so quotation marks render correctly in the PDF body
-- while keeping proper Unicode text in PDF bookmarks.

--- Copyright: © 2025–Present Tom Ben
--- License: MIT License

local function format_is(name)
    return FORMAT:match(name) ~= nil
end

local function to_macro_block(inlines)
    return pandoc.walk_block(pandoc.Plain(inlines), {
        Quoted = function(el)
            local opening, closing
            if el.quotetype == "SingleQuote" then
                opening = pandoc.RawInline('latex', "`")
                closing = pandoc.RawInline('latex', "'")
            else
                opening = pandoc.RawInline('latex', "``")
                closing = pandoc.RawInline('latex', "''")
            end

            local result = pandoc.Inlines { opening }
            for _, inline in ipairs(el.content) do
                result:insert(inline)
            end
            result:insert(closing)
            return result
        end
    })
end

local function to_unicode_block(inlines)
    return pandoc.walk_block(pandoc.Plain(inlines), {
        Quoted = function(el)
            local opening, closing
            if el.quotetype == "SingleQuote" then
                opening, closing = '‘', '’'
            else
                opening, closing = '“', '”'
            end

            local result = pandoc.Inlines { pandoc.Str(opening) }
            for _, inline in ipairs(el.content) do
                result:insert(inline)
            end
            result:insert(pandoc.Str(closing))
            return result
        end,
        Str = function(el)
            -- Replace guillemets with curly quotes for PDF bookmarks
            local text = el.text
            text = text:gsub('«', '“')
            text = text:gsub('»', '”')
            text = text:gsub('‹', '‘')
            text = text:gsub('›', '’')
            if text ~= el.text then
                return pandoc.Str(text)
            end
            return el
        end
    })
end

function Header(header)
    if not format_is('latex') then
        return header
    end

    local attr = header.attr
    local macro_block = to_macro_block(header.content)
    local unicode_block = to_unicode_block(header.content)

    local latex_doc = pandoc.Pandoc({ macro_block }, pandoc.Meta {})
    local latex_body = pandoc.write(latex_doc, 'latex')
        :gsub('%s+$', '')
        :gsub('\n', ' ')
    local bookmark_text = pandoc.utils.stringify(unicode_block)
        :gsub('\n', ' ')

    attr.attributes['data-tex-body'] = latex_body
    attr.attributes['data-bookmark'] = bookmark_text

    return header
end

local latex_heading_levels = {
    "section",
    "subsection",
    "subsubsection",
    "paragraph",
    "subparagraph",
    "subparagraph"
}

local function escape_tex_argument(text)
    local map = {
        ['\\'] = '\\\\',
        ['{'] = '\\{',
        ['}'] = '\\}',
        ['%'] = '\\%',
        ['#'] = '\\#',
        ['&'] = '\\&',
        ['_'] = '\\_',
        ['^'] = '\\^{}',
        ['~'] = '\\~{}'
    }
    return text:gsub('[\\%%#&_{}%^~]', map)
end

local function heading_to_raw(header)
    local tex_body = header.attr.attributes['data-tex-body']
    if not tex_body then
        return nil
    end

    local bookmark = header.attr.attributes['data-bookmark'] or pandoc.utils.stringify(header)
    header.attr.attributes['data-tex-body'] = nil
    header.attr.attributes['data-bookmark'] = nil
    local short_attr = header.attr.attributes['short-title'] or header.attr.attributes['short']
    if short_attr and short_attr ~= '' then
        bookmark = short_attr
    end
    bookmark = tostring(bookmark):gsub('\n', ' ')
    local level_index = math.min(header.level, #latex_heading_levels)
    local command = latex_heading_levels[level_index]

    local classes = header.attr.classes or {}
    local unnumbered = false
    for _, class in ipairs(classes) do
        if class == 'unnumbered' then
            unnumbered = true
            break
        end
    end

    local number_attr = header.attr.attributes['number']
    if number_attr == 'no' or number_attr == 'false' or number_attr == '0' then
        unnumbered = true
    end

    local star = unnumbered and '*' or ''
    local bookmark_escaped = escape_tex_argument(bookmark)
    local texorpdfstring = '\\texorpdfstring{' .. tex_body .. '}{' .. bookmark_escaped .. '}'
    local pieces = { '\\' .. command .. star .. '{' .. texorpdfstring .. '}' }

    local identifier = header.attr.identifier
    if identifier and identifier ~= '' then
        table.insert(pieces, '\\label{' .. identifier .. '}')
    end

    if unnumbered then
        table.insert(pieces, '\\addcontentsline{toc}{' .. command .. '}{' .. bookmark_escaped .. '}')
    end

    return pandoc.RawBlock('latex', table.concat(pieces, '') .. '\n')
end

function Pandoc(doc)
    if not format_is('latex') then
        return doc
    end

    local blocks = pandoc.List:new()
    for _, block in ipairs(doc.blocks) do
        if block.t == 'Header' then
            blocks:insert(heading_to_raw(block) or block)
        else
            blocks:insert(block)
        end
    end

    doc.blocks = blocks
    return doc
end

return {
    { Header = Header },
    { Pandoc = Pandoc }
}
