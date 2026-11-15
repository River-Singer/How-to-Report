# How-to-Report PPT technology component

This derivative retains the SVG checker, text estimator, DrawingML converter,
native Chart/Table compiler, structured Master/Layout builder and OOXML helpers
from the local PPT-Master 6.9.0 snapshot. Hugo He copyright and MIT terms are
retained in [LICENSE](LICENSE). Exact copied bytes and derivative changes are
recorded in [provenance.json](provenance.json).

The supported HTR entry is `scripts/ppt_runtime.py` at the enclosing Skill root.
It validates local structured SVG projects and exports a checked native PPTX
with explicit user theme values. The component includes technical geometry and
font-measurement data with their original notices. Visual template catalogs,
icons, themes, example slides and style presets are supplied by the selected
user template outside this component.

Declared text placeholder carriers retain one editable native text frame.
Aligned absolute or relative row baselines preserve authored hard breaks,
blank rows, line spacing, run formatting and the complete slot geometry.

Install the dependencies in [requirements.txt](requirements.txt) for this
production path. The component performs local checking and compilation. Native
PowerPoint rendering/editing and audience review have separate evidence.
