--- Route DOCX table styles for Quarto output.
---
--- Quarto often renders labeled floats (`#fig-*`, `#tbl-*`) with table wrappers.
--- We map wrapper/container tables -> `FigureTable` (no border),
--- and real data tables -> `Table` (three-line style).
--- Unlabeled figures (normal image path without `#fig-*`) are not affected.
--- Only table `custom-style` is changed.
--- Cannot use as a Quarto format filter since it needs to run after crossref labeling.

--- Copyright: © 2026–Present Tom Ben
--- License: MIT License

local STYLE_WRAPPER = "FigureTable"
local STYLE_DATA = "Table"

local function has_id_prefix(attr, prefix)
  local id = attr and attr.identifier
  if not id then
    return false
  end
  return id:sub(1, #prefix + 1) == (prefix .. "-")
end

local function first_row(tbl)
  if not tbl.bodies or #tbl.bodies == 0 then
    return nil
  end
  local body = tbl.bodies[1]
  if not body.body or #body.body == 0 then
    return nil
  end
  return body.body[1]
end

local function first_cell(tbl)
  local row = first_row(tbl)
  if not row or not row.cells or #row.cells == 0 then
    return nil
  end
  return row.cells[1], row
end

local function block_has_div_id_prefix(block, prefix)
  if block.t ~= "Div" then
    return false
  end

  if has_id_prefix(block.attr, prefix) then
    return true
  end

  for _, child in ipairs(block.content or {}) do
    if block_has_div_id_prefix(child, prefix) then
      return true
    end
  end

  return false
end

local function cell_has_div_prefix(cell, prefix)
  for _, block in ipairs(cell.contents or {}) do
    if block_has_div_id_prefix(block, prefix) then
      return true
    end
  end
  return false
end

-- Return wrapper type for labeled crossref tables: "fig", "tbl", or nil.
local function crossref_wrapper_kind(tbl)
  local cell, row = first_cell(tbl)
  if not cell then
    return nil
  end

  -- Keep this strict to avoid matching real data tables.
  if not row or not row.cells or #row.cells ~= 1 then
    return nil
  end

  if cell_has_div_prefix(cell, "fig") then
    return "fig"
  end

  if cell_has_div_prefix(cell, "tbl") then
    return "tbl"
  end

  return nil
end

local function set_table_style(tbl, style_name)
  tbl.attr = tbl.attr or pandoc.Attr("", {}, {})
  tbl.attr.attributes = tbl.attr.attributes or {}
  tbl.attr.attributes["custom-style"] = style_name
  return tbl
end

local function set_all_col_align(tbl, align)
  if not tbl.colspecs then
    return tbl
  end

  for i, cs in ipairs(tbl.colspecs) do
    cs[1] = align
    tbl.colspecs[i] = cs
  end

  return tbl
end

function Table(tbl)
  if not FORMAT:match("docx") then
    return nil
  end

  -- Respect style decisions that may already be set by another pass.
  if tbl.attr and tbl.attr.attributes and tbl.attr.attributes["custom-style"] then
    return tbl
  end

  -- Wrapper for labeled figures: keep centered figure layout.
  local wrapper_kind = crossref_wrapper_kind(tbl)
  if wrapper_kind == "fig" then
    set_all_col_align(tbl, pandoc.AlignCenter)
    return set_table_style(tbl, STYLE_WRAPPER)
  end

  -- Wrapper for labeled tables: keep table body at default (not forced center).
  if wrapper_kind == "tbl" then
    set_all_col_align(tbl, pandoc.AlignDefault)
    return set_table_style(tbl, STYLE_WRAPPER)
  end

  -- Default: real data table.
  return set_table_style(tbl, STYLE_DATA)
end

function Div(div)
  if not FORMAT:match("docx") then
    return nil
  end

  -- Figure layouts (e.g. layout-ncol) may put tables inside `Div(id="fig-*")`.
  if has_id_prefix(div.attr, "fig") then
    return div:walk({
      Table = function(tbl)
        return set_table_style(tbl, STYLE_WRAPPER)
      end
    })
  end

  return nil
end
