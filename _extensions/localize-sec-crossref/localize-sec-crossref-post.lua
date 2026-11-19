-- 章节交叉引用本地化（第二步，crossref 之后，at: post-render）。
--
-- Quarto crossref 已把 @sec-* 渲染成带编号的引用，但存在两处问题：
--   1) 若把「章 / 节」后缀追加在链接之外，会出现「第 6」是链接而「章」不是；
--   2) crossref 在前缀与编号之间插入的空格（HTML/DOCX 为不换行空格）在中文里多余。
-- 本 filter 按各输出格式的节点形态重建引用，使「第N章 / 第N节」整体成为单个
-- 链接且不含空格。一级标题写「章」，其余写「节」。章节层级在处理引用前先扫描
-- 全文标题记录，以支持前向引用。

--- Copyright: © 2026–Present Tom Ben
--- License: MIT License

local suffix_for = {}

local function collect_levels(doc)
  doc:walk({
    Header = function(header)
      local id = header.identifier
      if id:match("^sec%-") then
        suffix_for[id] = (header.level == 1) and "章" or "节"
      end
    end,
  })
end

-- 去除 ASCII 空白与不换行空格（U+00A0）。
-- 不用 %s：macOS 的 UTF-8 区域设置下 %s 也匹配 0xA0 字节，会截掉汉字的末字节。
local function strip_spaces(s)
  return (s:gsub("[ \t\r\n]", ""):gsub("\u{a0}", ""))
end

local function is_space_inline(el)
  if el.t == "Space" then
    return true
  end
  return el.t == "Str" and el.text ~= "" and strip_spaces(el.text) == ""
end

-- HTML / DOCX / EPUB：crossref 生成 Link，前缀与编号都在 Link 内部，
-- 只需把「章 / 节」并入链接文本并去掉空格。
local function fix_link(link)
  local id = tostring(link.target):match("^#(sec%-[%w%-]+)$")
  if not id or not suffix_for[id] then
    return nil
  end

  local is_xref = false
  for _, cls in ipairs(link.classes) do
    if cls == "quarto-xref" then
      is_xref = true
      break
    end
  end
  if not is_xref then
    return nil
  end

  local body = strip_spaces(pandoc.utils.stringify(link.content))
  if not body:match("^第") then
    return nil
  end

  link.content = pandoc.Inlines({ pandoc.Str(body .. suffix_for[id]) })
  return link
end

-- LaTeX / Typst：crossref 生成 RawInline，「第」前缀与编号是相邻的独立节点，
-- 需在行内序列层面重建为单个成链的原生标记。
local function fix_inlines(inlines)
  local changed = false
  local out = pandoc.Inlines({})
  local i, n = 1, #inlines

  while i <= n do
    local el = inlines[i]

    -- LaTeX: 「第」 nbsp \ref{sec-X}  ->  \hyperref[sec-X]{第\ref*{sec-X}章}
    if el.t == "RawInline" and el.format == "latex" then
      local id = el.text:match("^\\ref%{(sec%-[%w%-]+)%}$")
      if id and suffix_for[id] then
        while #out > 0 and is_space_inline(out[#out]) do
          out:remove(#out)
        end
        if #out > 0 and out[#out].t == "Str" and out[#out].text == "第" then
          out:remove(#out)
        end
        out:insert(pandoc.RawInline("latex",
          "\\hyperref[" .. id .. "]{第\\ref*{" .. id .. "}" .. suffix_for[id] .. "}"))
        changed = true
        i = i + 1
        goto continue
      end
    end

    -- Typst: #ref(<sec-X>, supplement: [ 第 ])  ->
    --        #link(<sec-X>)[第#ref(<sec-X>, supplement: none)章]
    if el.t == "RawInline" and el.format == "typst" then
      local id = el.text:match("^#ref%(<(sec%-[%w%-]+)>, supplement: %[$")
      if id and suffix_for[id] then
        local j = i + 1
        while j <= n do
          local nxt = inlines[j]
          if nxt.t == "RawInline" and nxt.format == "typst" and nxt.text == "])" then
            break
          end
          j = j + 1
        end
        out:insert(pandoc.RawInline("typst",
          "#link(<" .. id .. ">)[第#ref(<" .. id .. ">, supplement: none)"
          .. suffix_for[id] .. "]"))
        changed = true
        i = j + 1
        goto continue
      end
    end

    out:insert(el)
    i = i + 1
    ::continue::
  end

  if changed then
    return out
  end
  return nil
end

function Pandoc(doc)
  collect_levels(doc)
  return doc:walk({
    Link = fix_link,
    Inlines = fix_inlines,
  })
end
