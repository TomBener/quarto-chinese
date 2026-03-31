-- citation-punctuation.lua
-- Move trailing punctuation before a standalone citation line to after the citation.
-- This mimics notes-after-punctuation behavior for author-date / numeric styles.

-- Copyright: © 2026–Present Tom Ben
--- License: MIT License

local TRAILING_PUNCT = {
  ",",
  "，",
  ";",
  "；",
  ".",
  "。",
  "?",
  "？",
  "!",
  "！",
  "......",
  "……",
  "...",
  "…"
}

local EXACT_PUNCT = {}
for _, p in ipairs(TRAILING_PUNCT) do
  EXACT_PUNCT[p] = true
end

local function is_break(el)
  return el and (el.t == "SoftBreak" or el.t == "LineBreak")
end

local function is_space(el)
  return el and el.t == "Space"
end

local function ends_with(text, suffix)
  return #text >= #suffix and text:sub(-#suffix) == suffix
end

local function split_trailing_punct(text)
  for _, p in ipairs(TRAILING_PUNCT) do
    if ends_with(text, p) then
      return text:sub(1, #text - #p), p
    end
  end
  return nil, nil
end

local function is_punct_str(el)
  return el and el.t == "Str" and EXACT_PUNCT[el.text] == true
end

local function strip_one_trailing_punct(text, punct)
  if punct ~= "" and ends_with(text, punct) then
    return text:sub(1, #text - #punct), true
  end
  return text, false
end

local function is_normal_cite(el)
  if not (el and el.t == "Cite" and el.citations and #el.citations > 0) then
    return false
  end
  for _, c in ipairs(el.citations) do
    if c.mode ~= "NormalCitation" then
      return false
    end
  end
  return true
end

local function set_break_to_spacing(inlines, idx)
  local before = inlines[idx - 1]
  local after = inlines[idx + 1]
  if not after then
    inlines:remove(idx)
    return -1
  end
  if is_space(before) then
    inlines:remove(idx)
    return -1
  end
  if is_punct_str(after) then
    inlines:remove(idx)
    return -1
  end
  inlines[idx] = pandoc.Space()
  return 0
end

function Inlines(inlines)
  local i = 2
  while i <= #inlines do
    if is_normal_cite(inlines[i]) and is_break(inlines[i - 1]) then
      local cite_idx = i

      -- If the token before the break ends with punctuation, move that
      -- punctuation to directly after the citation.
      local before_idx = cite_idx - 2
      local before = inlines[before_idx]
      if before and before.t == "Str" then
        local after_punct = inlines[cite_idx + 1]
        if is_punct_str(after_punct) then
          -- Dedupe accidental punctuation on both sides of citation:
          -- "word, [@key]," -> "word [@key],"
          local stripped, removed = strip_one_trailing_punct(before.text, after_punct.text)
          if removed then
            before.text = stripped
            if stripped == "" then
              inlines:remove(before_idx)
              cite_idx = cite_idx - 1
              i = i - 1
            end
          end
        else
          local stripped, punct = split_trailing_punct(before.text)
          if punct then
            before.text = stripped
            if stripped == "" then
              inlines:remove(before_idx)
              cite_idx = cite_idx - 1
              i = i - 1
            end
            inlines:insert(cite_idx + 1, pandoc.Str(punct))
          end
        end
      end

      -- Convert citation-leading line break to a regular inline separator.
      if is_break(inlines[cite_idx - 1]) then
        cite_idx = cite_idx + set_break_to_spacing(inlines, cite_idx - 1)
      end

      -- If citation is followed by a line break, inline it.
      local after_cite = inlines[cite_idx + 1]
      if is_break(after_cite) then
        set_break_to_spacing(inlines, cite_idx + 1)
      elseif is_punct_str(after_cite) and is_break(inlines[cite_idx + 2]) then
        -- Handle patterns like: [@key].<newline>Next sentence
        set_break_to_spacing(inlines, cite_idx + 2)
      end
    end
    i = i + 1
  end

  return inlines
end
