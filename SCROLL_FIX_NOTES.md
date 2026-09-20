# Scroll fix notes

Fixed the case-detail workspace clipping issue where the Seven-field verification section could not be scrolled to all seven fields on desktop/laptop viewports.

Changes in `web/style.css`:
- made the desktop workspace use an explicit viewport-aware height rather than only `max-height`
- added `grid-template-rows: minmax(0, 1fr)` so grid children can shrink correctly
- added `min-height: 0` and explicit vertical scrolling to the right `.detail` pane
- kept the left inbox pane constrained to the same grid row
- disabled horizontal scrolling in the detail pane
- preserved natural page scrolling for <=900px responsive layouts and mobile

Validation:
- `pytest -q`: 14 passed
- `python scripts/competition_gate.py`: pass
- `/api/health`: returned `status: ok` in local public-demo mode
