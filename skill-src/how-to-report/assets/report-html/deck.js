(() => {
  "use strict";
  const slides = Array.from(document.querySelectorAll(".slide"));
  const root = document.documentElement;
  const deck = document.getElementById("deck");
  const shell = document.querySelector(".deck-shell");
  const previous = document.getElementById("previous");
  const next = document.getElementById("next");
  const readAll = document.getElementById("read-all");
  const counter = document.getElementById("page-number");
  const warning = document.getElementById("layout-warning");
  const style = getComputedStyle(root);
  const WIDTH = parseFloat(style.getPropertyValue("--canvas-width"));
  const HEIGHT = parseFloat(style.getPropertyValue("--canvas-height"));
  let active = 0;
  let reading = false;
  let frame = 0;
  const directory = document.getElementById("contents-dialog");
  const notesPanel = document.getElementById("notes-panel");
  const notesToggle = document.getElementById("notes-toggle");
  const more = document.getElementById("more-menu");
  const moreToggle = document.getElementById("more-toggle");
  const returnButton = document.getElementById("backup-return");
  const route = DECK_ROUTE.map(id => slides.findIndex(slide => slide.dataset.pageId === id));
  const history = [];
  let notesOpen = false;
  function routeStep(direction) {
    const position = route.indexOf(active);
    if (position < 0) return;
    const target = position + direction;
    if (target >= 0 && target < route.length) goTo(route[target]);
  }
  function setNotes(value) {
    notesOpen = value && Boolean(notesToggle);
    notesPanel.hidden = !notesOpen;
    notesToggle?.setAttribute("aria-expanded", String(notesOpen));
    document.body.classList.toggle("notes-open", notesOpen);
    fit(); updateWarning();
  }
  function setMore(value) {
    more.hidden = !value;
    moreToggle.setAttribute("aria-expanded", String(value));
  }
  function jump(id, backup = false) {
    const index = slides.findIndex(slide => slide.dataset.pageId === id);
    if (index < 0) return false;
    if (backup) history.push(active); else history.length = 0;
    goTo(index); return true;
  }
  function returnFromBackup() {
    goTo(history.length ? history.pop() : route[0]);
  }
  async function fullscreen() {
    const status = document.getElementById("control-status");
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen();
      else throw new Error("unavailable");
      status.textContent = "";
    } catch (_) { status.textContent = document.documentElement.lang === "zh-CN" ? "当前浏览器无法进入全屏。" : "Fullscreen is unavailable in this browser."; }
  }

  function fit() {
    if (reading) return;
    const scale = Math.max(0.01, Math.min((innerWidth - (notesOpen && innerWidth > 850 ? 386 : 76)) / WIDTH, (innerHeight - 132) / HEIGHT));
    deck.style.transform = "scale(" + scale + ")";
    shell.style.width = WIDTH * scale + "px";
    shell.style.height = HEIGHT * scale + "px";
  }
  function inspectLayout() {
    const wasReading = reading;
    if (wasReading) {
      document.body.classList.replace("reading-mode", "deck-mode");
      reading = false;
      fit();
    }
    const result = {scope: "actual_dom_geometry_only", pageCount: slides.length, currentPageId: slides[active].dataset.pageId, canvas: {width: WIDTH, height: HEIGHT}, viewport: {width: innerWidth, height: innerHeight}, pages: [], issues: []};
    for (const slide of slides) {
      if (!slide.classList.contains("active")) slide.classList.add("measuring");
      const bounds = slide.getBoundingClientRect();
      const scale = bounds.width / WIDTH;
      const page = {id: slide.dataset.pageId, width: bounds.width, height: bounds.height, issues: [], elements: [], bars: [], charts: []};
      const add = (kind, id) => {
        const issue = {kind, id, pageId: page.id};
        page.issues.push(issue); result.issues.push(issue);
      };
      for (const element of slide.querySelectorAll(".page-element, .layout-node, .chart-content, .page-header, .page-content, .page-footer")) {
        const r = element.getBoundingClientRect();
        const id = element.dataset.elementId || element.className;
        page.elements.push({id, x: r.x, y: r.y, width: r.width, height: r.height});
        if (r.left < bounds.left - 1 || r.right > bounds.right + 1 || r.top < bounds.top - 1 || r.bottom > bounds.bottom + 1) add("outside_slide", id);
        if (element.scrollHeight > element.clientHeight + 2 || element.scrollWidth > element.clientWidth + 2) add("content_overflow", id);
      }
      const content = slide.querySelector(".page-content").getBoundingClientRect();
      const footer = slide.querySelector(".page-footer").getBoundingClientRect();
      for (const leaf of slide.querySelectorAll(".page-content h2, .page-content p, .page-content small, .page-content .value, .page-content caption, .page-content th, .page-content td, .chart-label, .chart-value, .hierarchy-levels li")) {
        // Empty optional limits have display:none; they have no rendered box.
        // Continue measuring actual visible text, including overfull content.
        if (!leaf.getClientRects().length) continue;
        const r = leaf.getBoundingClientRect();
        if (r.bottom > footer.top + 1 || r.top < content.top - 1) add("text_outside_content", leaf.closest("[data-element-id]")?.dataset.elementId || leaf.tagName);
        const panel = leaf.closest(".composed-element");
        if (panel) {
          const panelRect = panel.getBoundingClientRect();
          if (r.left < panelRect.left-1 || r.right > panelRect.right+1 || r.top < panelRect.top-1 || r.bottom > panelRect.bottom+1) add("text_outside_panel", panel.dataset.elementId);
          if (!leaf.closest(".element-footer") && r.bottom > panel.querySelector(".element-footer").getBoundingClientRect().top+1) add("text_overlaps_panel_footer", panel.dataset.elementId);
        }
      }
      for (const row of slide.querySelectorAll(".data-row, .chart-bar-row")) {
        const bar = row.querySelector(".bar");
        const track = row.querySelector(".track").getBoundingClientRect();
        const r = bar?.getBoundingClientRect();
        const id = row.dataset.elementId || row.dataset.datumId;
        page.bars.push({id, value: row.dataset.value, label: row.querySelector(".value, .chart-value").textContent, left: r ? (r.left-track.left)/scale : null, width: r ? r.width/scale : null});
        if (r && (!Number.isFinite(r.width) || r.width < 0 || r.left < track.left-1 || r.right > track.right+1)) add("invalid_bar_geometry", id);
      }
      for (const chart of slide.querySelectorAll("[data-chart-kind]")) {
        const record = {elementId: chart.closest("[data-element-id]").dataset.elementId, kind: chart.dataset.chartKind, unit: chart.dataset.unit, data: [], segments: []};
        for (const datum of chart.querySelectorAll("[data-datum-id]")) record.data.push({id: datum.dataset.datumId, value: datum.dataset.value, text: datum.textContent, refs: JSON.parse(datum.dataset.refs)});
        for (const path of chart.querySelectorAll(".line-segment")) record.segments.push({seriesId: path.dataset.seriesId, pointCount: Number(path.dataset.pointCount), path: path.getAttribute("d")});
        for (const geometry of chart.querySelectorAll("svg path, svg circle")) {
          const r = geometry.getBoundingClientRect();
          if (![r.x,r.y,r.width,r.height].every(Number.isFinite)) add("invalid_chart_geometry", record.elementId);
          const box = geometry.getBBox();
          const view = geometry.ownerSVGElement.viewBox.baseVal;
          if (![box.x,box.y,box.width,box.height].every(Number.isFinite) || box.x < view.x-0.1 || box.y < view.y-0.1 || box.x+box.width > view.x+view.width+0.1 || box.y+box.height > view.y+view.height+0.1) add("svg_outside_viewbox", record.elementId);
        }
        page.charts.push(record);
      }
      for (const svg of slide.querySelectorAll(".diagram-content svg, .schedule-content svg")) {
        const box = svg.getBBox(), view = svg.viewBox.baseVal;
        if (box.x < view.x-1 || box.y < view.y-1 || box.x+box.width > view.x+view.width+1 || box.y+box.height > view.y+view.height+1) add("svg_outside_viewbox", svg.closest("[data-element-id]")?.dataset.elementId);
      }
      slide.classList.remove("measuring");
      result.pages.push(page);
    }
    if (wasReading) {
      reading = true;
      document.body.classList.replace("deck-mode", "reading-mode");
      shell.style.width = ""; shell.style.height = "";
    }
    return result;
  }
  function updateWarning() {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => {
      const check = inspectLayout();
      warning.hidden = !check.issues.some(issue => issue.pageId === slides[active].dataset.pageId);
    });
  }
  function goTo(index, updateHash = true) {
    if (!Number.isInteger(index)) return false;
    slides[active].querySelectorAll("video").forEach(video => video.pause());
    active = Math.min(slides.length-1, Math.max(0, index));
    slides.forEach((slide, i) => {
      slide.classList.toggle("active", i === active);
      slide.setAttribute("aria-hidden", String(!reading && i !== active));
      slide.inert = !reading && i !== active;
    });
    const routePosition = route.indexOf(active);
    previous.disabled = routePosition <= 0; next.disabled = routePosition < 0 || routePosition >= route.length-1;
    returnButton.hidden = !history.length && routePosition >= 0;
    document.querySelectorAll(".page-dots [data-jump]").forEach(button => button.setAttribute("aria-current", String(button.dataset.jump === slides[active].dataset.pageId)));
    const note = slides[active].querySelector(".speaker-notes");
    document.getElementById("notes-text").textContent = note?.content.textContent || (document.documentElement.lang === "zh-CN" ? "本页未提供讲稿。" : "No speaker notes for this page.");
    counter.value = (active+1) + " / " + slides.length;
    if (updateHash && location.hash !== "#" + slides[active].dataset.pageId) location.hash = slides[active].dataset.pageId;
    updateWarning();
    return true;
  }
  function fromHash() {
    const id = location.hash.slice(1);
    const index = slides.findIndex(slide => slide.dataset.pageId === id);
    if (index >= 0 && index !== active) history.length = 0;
    goTo(index < 0 ? route[0] : index, false);
  }
  function setReading(value) {
    reading = value;
    document.body.classList.toggle("reading-mode", reading);
    document.body.classList.toggle("deck-mode", !reading);
    readAll.textContent = reading ? DECK_LABELS.deck : DECK_LABELS.all;
    readAll.setAttribute("aria-pressed", String(reading));
    if (reading) { shell.style.width = ""; shell.style.height = ""; }
    else fit();
    goTo(active, false);
  }
  previous.addEventListener("click", () => routeStep(-1));
  next.addEventListener("click", () => routeStep(1));
  readAll.addEventListener("click", () => { setReading(!reading); setMore(false); });
  document.getElementById("contents-toggle").addEventListener("click", () => { directory.showModal(); setMore(false); });
  document.getElementById("contents-close").addEventListener("click", () => directory.close());
  directory.addEventListener("close", () => document.getElementById("contents-toggle").focus());
  document.querySelectorAll("[data-jump]").forEach(button => button.addEventListener("click", () => { jump(button.dataset.jump); if (directory.open) directory.close(); }));
  document.querySelectorAll("[data-backup-target]").forEach(button => button.addEventListener("click", () => jump(button.dataset.backupTarget, true)));
  returnButton.addEventListener("click", returnFromBackup);
  notesToggle?.addEventListener("click", () => setNotes(!notesOpen));
  document.getElementById("notes-close").addEventListener("click", () => { setNotes(false); notesToggle?.focus(); });
  moreToggle.addEventListener("click", () => setMore(more.hidden));
  document.getElementById("fullscreen").addEventListener("click", fullscreen);
  document.getElementById("print-deck").addEventListener("click", () => { setMore(false); window.print(); });
  addEventListener("click", event => { if (!event.target.closest("#more-menu,#more-toggle")) setMore(false); });
  addEventListener("fullscreenchange", () => { fit(); updateWarning(); });
  addEventListener("hashchange", fromHash);
  addEventListener("resize", () => { fit(); updateWarning(); });
  addEventListener("keydown", event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.target.closest("input,textarea,select,[contenteditable]")) return;
    if (event.key === "Escape") { setMore(false); if (notesOpen) setNotes(false); return; }
    if (directory.open || event.target.closest("video") || reading) return;
    if (["ArrowRight", "PageDown", "ArrowLeft", "PageUp", "Home", "End", "f", "F", "n", "N"].includes(event.key)) {
      event.preventDefault();
      if (["ArrowRight", "PageDown"].includes(event.key)) routeStep(1);
      else if (["ArrowLeft", "PageUp"].includes(event.key)) routeStep(-1);
      else if (event.key === "Home") goTo(route[0]);
      else if (event.key === "End") goTo(route[route.length-1]);
      else if (event.key.toLowerCase() === "f") fullscreen();
      else setNotes(!notesOpen);
    }
  });
  // Print must expose all slides, including those inert during interactive navigation.
  addEventListener("beforeprint", () => {
    slides.forEach(slide => slide.querySelectorAll("video").forEach(video => video.pause()));
    document.body.classList.remove("reading-mode");
    document.body.classList.add("deck-mode");
    slides.forEach(slide => { slide.inert = false; slide.setAttribute("aria-hidden", "false"); });
  });
  addEventListener("afterprint", () => {
    document.body.classList.toggle("reading-mode", reading);
    document.body.classList.toggle("deck-mode", !reading);
    goTo(active, false);
  });
  document.body.classList.add("scripted", "deck-mode");
  window.reportDeck = {inspectLayout, goTo, next: () => routeStep(1), previous: () => routeStep(-1), setReading, setNotes, jump, returnFromBackup};
  fit(); fromHash();
  document.fonts.ready.then(updateWarning);
})();
