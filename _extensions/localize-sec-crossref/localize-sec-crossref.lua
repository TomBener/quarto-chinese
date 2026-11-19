-- 章节交叉引用本地化（第一步，crossref 之前）。
--
-- 只把普通 @sec-* 引用的前缀设为「第」，编号与链接仍由 Quarto crossref 生成。
-- 「章 / 节」后缀、去除多余空格、以及使「第N章」整体落在同一个链接内，交由
-- localize-sec-crossref-post.lua 在 crossref 之后（at: post-render）完成——彼时
-- crossref 已按各输出格式生成引用节点，才能把后缀并入链接内部。

local function is_plain_reference(citation)
  local mode = tostring(citation.mode)
  return (mode == "AuthorInText" or mode == "NormalCitation")
    and #citation.prefix == 0
    and #citation.suffix == 0
end

function Pandoc(doc)
  local is_sec = {}

  doc:walk({
    Header = function(header)
      local identifier = header.identifier or header.attr.identifier
      if identifier and identifier:match("^sec%-") then
        is_sec[identifier] = true
      end
    end,
  })

  return doc:walk({
    Cite = function(cite)
      if #cite.citations ~= 1 then
        return nil
      end

      local citation = cite.citations[1]
      if not is_sec[citation.id] or not is_plain_reference(citation) then
        return nil
      end

      citation.prefix = pandoc.Inlines({ pandoc.Str("第") })
      return cite
    end,
  })
end
