--- Emulate Pandoc's extension `east_asian_line_breaks` in Quarto
--- Ignore soft break adjacent to Chinese characters in paragraphs, tight list items and table cells
--- Tracking Quarto issue: https://github.com/quarto-dev/quarto-cli/issues/8520

--- Copyright: © 2024–Present Tom Ben
--- License: MIT License

function is_chinese(text)
  return text:find("[\228-\233][\128-\191][\128-\191]")
end

function is_ascii(char)
  if char == nil then return false end
  local ascii_code = string.byte(char)
  return ascii_code >= 0 and ascii_code <= 127
end

function is_chinese_punctuation(char)
  if char == nil then return false end
  local punctuation_marks = "，。！？；：“”‘’（）【】《》〈〉「」『』、"
  return string.find(punctuation_marks, char, 1, true) ~= nil
end

function is_alphanumeric(char)
  if char == nil then return false end
  return char:match("[%w]") ~= nil
end

-- Text of an inline element (Str, Code, Math ...), or nil if it has none
local function inline_text(el)
  local text = el.text
  if type(text) == "string" and #text > 0 then
    return text
  end
  return nil
end

-- Whether a soft break between `prev` and `nxt` should be dropped
local function removable(prev, nxt)
  local p_text = inline_text(prev)
  local n_text = inline_text(nxt)

  local prev_char -- Stores the last UTF-8 character of p_text
  if p_text then
    for char_item in p_text:gmatch("([\0-\x7F\xC2-\xF4][\x80-\xBF]*)") do
      prev_char = char_item
    end
  end

  local next_char -- Stores the first UTF-8 character of n_text
  if n_text then
    for char_item in n_text:gmatch("([\0-\x7F\xC2-\xF4][\x80-\xBF]*)") do
      next_char = char_item
      break -- Found the first character
    end
  end

  -- Rule 1: Remove soft break between Chinese characters
  -- Rule 2: Remove soft break after Chinese punctuation, whatever follows
  --         (also before a link, citation or cross-reference such as `。\n@tbl-x`)
  -- Rule 3: Remove soft break before Chinese punctuation, whatever precedes
  -- Rule 4: Keep soft break between Chinese chars and ASCII alphanumeric,
  -- which preserves spacing between Chinese and English words
  return (prev_char ~= nil and next_char ~= nil and is_chinese(prev_char) and is_chinese(next_char))
    or is_chinese_punctuation(prev_char)
    or is_chinese_punctuation(next_char)
end

-- Drop removable soft breaks. Two Str joined by a dropped break are merged
-- into one, so later filters that work on single Str (e.g. auto-correct.py)
-- see the same text as if the source line had not been broken there.
local function ignore_softbreaks(para)
  local cs = para.content
  local out = pandoc.List()
  local k = 1
  while k <= #cs do
    local v = cs[k]
    local prev = out[#out]
    local nxt = cs[k + 1]
    if v.t == 'SoftBreak' and prev and nxt and removable(prev, nxt) then
      if prev.t == 'Str' and nxt.t == 'Str' then
        out[#out] = pandoc.Str(prev.text .. nxt.text)
        k = k + 2
      else
        k = k + 1
      end
    else
      out:insert(v)
      k = k + 1
    end
  end
  para.content = out
  return para
end

-- Tight list items and table cells are Plain blocks, not Para
return {
  {
    Para = ignore_softbreaks,
    Plain = ignore_softbreaks
  }
}
