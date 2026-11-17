"use strict";
// Request binding only; all geometry and colour application execute in the engine.
((root) => {
  function applyPalette(request, mode, paletteId, originalPaletteId = null, restoreOriginal = false) {
    const value = JSON.parse(JSON.stringify(request));
    if (mode === "native" || !["chart", "author", "recipe"].includes(mode)) return value;
    if (!paletteId && !restoreOriginal) return value;
    const selected = paletteId || originalPaletteId;
    if (mode === "chart") {
      if (selected) value.palette_id = selected;
      else delete value.palette_id;
    } else {
      if (selected) value.brief = {...(value.brief || {}), palette_id: selected};
      else if (value.brief) delete value.brief.palette_id;
    }
    return value;
  }
  const api = {applyPalette};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.STORYBOOK_REQUESTS = api;
})(typeof window !== "undefined" ? window : globalThis);
