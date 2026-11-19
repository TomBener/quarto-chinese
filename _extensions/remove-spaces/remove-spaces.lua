--- Remove spaces around Chinese characters except citations

--- Copyright: © 2024–Present Tom Ben
--- License: MIT License

-- Check if a code point is a CJK character or CJK/fullwidth punctuation.
-- Accented Latin letters (é, ö) and symbols such as — or “ do not count,
-- so the space in "café au lait" or "José García" is kept.
local function is_cjk_codepoint(cp)
  return (cp >= 0x2E80 and cp <= 0x9FFF)   -- CJK radicals, punctuation, kana, ideographs
      or (cp >= 0xF900 and cp <= 0xFAFF)   -- CJK compatibility ideographs
      or (cp >= 0xFE30 and cp <= 0xFE4F)   -- CJK compatibility forms
      or (cp >= 0xFF00 and cp <= 0xFFEF)   -- fullwidth forms (，。！？)
      or (cp >= 0x20000 and cp <= 0x3FFFF) -- CJK extension B and later
end

-- First or last UTF-8 character of a string, as a code point
local function first_codepoint(text)
  return text ~= "" and utf8.codepoint(text, 1) or nil
end

local function last_codepoint(text)
  return text ~= "" and utf8.codepoint(text, utf8.offset(text, -1)) or nil
end

local function is_cjk(cp)
  return cp ~= nil and is_cjk_codepoint(cp)
end

-- Process the paragraph to remove spaces adjacent to non-ASCII characters
local function process_paragraph(para)
  local cs = para.content
  local new_content = {}

  for i, elem in ipairs(cs) do
    -- If the element is not a Space, always keep it
    if elem.t ~= 'Space' then
      table.insert(new_content, elem)
    else
      -- Element is a Space, determine whether to keep it
      local next_elem = cs[i + 1]
      local prev_elem = cs[i - 1]

      -- Check adjacent characters for Chinese text
      local next_char = next_elem and next_elem.t == 'Str' and first_codepoint(next_elem.text)
      local prev_char = prev_elem and prev_elem.t == 'Str' and last_codepoint(prev_elem.text)

      -- Check if adjacent elements are citations or citation-related elements
      local next_is_cite = next_elem and (next_elem.t == 'Cite' or next_elem.t == 'Note')
      local prev_is_cite = prev_elem and (prev_elem.t == 'Cite' or prev_elem.t == 'Note')

      -- Determine if we need to remove this space
      local has_adjacent_chinese = (next_char and is_cjk(next_char)) or (prev_char and is_cjk(prev_char))
      local is_adjacent_to_cite = (prev_is_cite and next_char and is_cjk(next_char)) or
          (next_is_cite and prev_char and is_cjk(prev_char))

      -- Keep space if:
      -- 1. It's not adjacent to Chinese characters, OR
      -- 2. It's between a citation and Chinese characters
      if not has_adjacent_chinese or is_adjacent_to_cite then
        table.insert(new_content, elem)
      end
      -- Otherwise, remove the space (by not adding it to new_content)
    end
  end

  para.content = new_content
  return para
end

-- Return the filter for Pandoc
return {
  { Para = process_paragraph }
}
