-- itemkey-to-citekey.lua
-- Replace Zotero item-key citations with Pandoc citation keys at render time.

local function read_file(path)
  local file, err = io.open(path, "r")
  if not file then
    return nil, err
  end

  local content = file:read("*a")
  file:close()
  return content
end

local function meta_to_strings(value)
  local paths = {}

  if value == nil then
    return paths
  end

  if type(value) == "table" and value[1] ~= nil then
    for _, item in ipairs(value) do
      table.insert(paths, pandoc.utils.stringify(item))
    end
  else
    table.insert(paths, pandoc.utils.stringify(value))
  end

  return paths
end

local function normalize_entries(entries)
  if entries.items ~= nil then
    return entries.items
  end
  if entries.references ~= nil then
    return entries.references
  end
  return entries
end

local function load_item_key_map(meta)
  local map = {}
  local bibliography_paths

  if meta.bibliography == nil then
    error("itemkey-to-citekey: no bibliography configured in document metadata")
  end

  bibliography_paths = meta_to_strings(meta.bibliography)

  if #bibliography_paths == 0 then
    error("itemkey-to-citekey: bibliography metadata is empty")
  end

  local path = bibliography_paths[1]
  if not path:match("%.json$") then
    error(
      "itemkey-to-citekey: no CSL JSON source found; " ..
      "the first `bibliography` entry must be a CSL JSON file"
    )
  end

  local content, err = read_file(path)
  if not content then
    error("Could not read bibliography JSON: " .. path .. " (" .. tostring(err) .. ")")
  end

  local decoded = pandoc.json.decode(content)
  local entries = normalize_entries(decoded)

  for _, entry in ipairs(entries) do
    local item_key = entry["zotero-item-key"]
    local citation_key = entry.id
    if item_key ~= nil and citation_key ~= nil then
      map[item_key] = citation_key
    end
  end

  return map
end

local function replace_citation_ids(citations, item_key_map)
  for _, citation in ipairs(citations) do
    local replacement = item_key_map[citation.id]
    if replacement ~= nil and replacement ~= citation.id then
      citation.id = replacement
    end
  end
end

function Pandoc(doc)
  local item_key_map = load_item_key_map(doc.meta)

  return doc:walk({
    Cite = function(cite)
      replace_citation_ids(cite.citations, item_key_map)
      return cite
    end,
  })
end
