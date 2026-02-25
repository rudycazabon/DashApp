# Checkpoint 10 — Keyboard Navigation

## Date
2026-02-25

## Summary
Added three keyboard navigation schemes to DashApp:
1. **Tab / Shift-Tab** — switch between tabs at the top of the screen
2. **Up / Down** — move focus between list items (Collapsibles) within a tab
3. **Left / Right** — collapse / expand the focused list item

## Files Changed

### New
- `tools/widget.py` — `NavigableToolWidget(Widget)` base class

### Modified
- `tui/app.py` — added `BINDINGS` with `priority=True` for Tab/Shift-Tab; added `action_next_tab` / `action_prev_tab`
- `tools/gmail/tool.py` — `GmailWidget` now extends `NavigableToolWidget`
- `tools/calendar/tool.py` — `CalendarWidget` now extends `NavigableToolWidget`
- `tools/outlook/tool.py` — `OutlookWidget` now extends `NavigableToolWidget`
- `tools/outlook_calendar/tool.py` — `OutlookCalendarWidget` now extends `NavigableToolWidget`
- `tools/jira/tool.py` — `JiraWidget` now extends `NavigableToolWidget`

## Design Decisions

### Tab / Shift-Tab (app-level, `priority=True`)
Overrides Textual's built-in focus-cycling behaviour. `priority=True` ensures the
binding is resolved before any child widget's Tab handling, so Tab always switches
tabs rather than moving focus within a tab's content area.

### Up / Down / Left / Right (widget-level, `priority=True`)
`NavigableToolWidget.BINDINGS` uses `priority=True` so these bindings are checked
before `VerticalScroll`'s default `up → scroll_up` / `down → scroll_down` bindings.
This makes arrow keys navigate Collapsible items instead of scrolling.

`_top_level_collapsibles()` queries only direct Collapsible children of `#scroll`,
so for Jira (nested structure) Up/Down navigates between project Collapsibles;
inner issue Collapsibles are accessible via Right/Left on the focused project entry.

Navigation wraps cyclically (last item → first, first item → last).

## Test Status
All 90 existing tests pass. No new tests added (navigation is pure Textual widget
behaviour with no testable logic beyond the existing test coverage).
