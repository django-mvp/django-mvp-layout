# Tasks: Layouts in plain templates

Paths are repository-relative. `verify` means `uv run pytest -n auto --dist loadscope` plus
`uv run pre-commit run --all-files`. Per-task runs use the narrowest scope that covers the change.

## Phase 1: Foundation

- [ ] T001 Add the test pages' plumbing: `docs/` on the template search path in `tests/settings.py`, an empty `tests/templates/layouts/` directory with a `.gitkeep`, and the new tests' modules in `[tool.forge.conformance] non-mirror-paths` in `pyproject.toml` (`tests/test_layout_js.py`, `tests/test_build_css.py`).

## Phase 2: User Story 1 — A developer lays out a page by a layout code in a plain template (P1)

### Group 1: the layout code and the tags

- [ ] T002 [US1] Test first, then `mvp_layout/view.py`: `tests/test_view.py::TestLayoutView` for the default code, extra spaces, each fixed flag, each corner offset, the areas value and a refusal that states the rules (FR-004, FR-005, SC-002).
- [ ] T003 [US1] Test first, then `layout_attrs` in `mvp_layout/templatetags/mvp_layout.py`: `tests/test_templatetags/test_mvp_layout.py::TestLayoutAttrs` for each attribute, `container`, `css_class`, `style` and a wrong code raising at render time (FR-002).
- [ ] T004 [US1] Test first, then `sidebar_attrs`: `TestSidebarAttrs` for each option and default, a wrong option naming its choices, `width` and `rail_width` as variables, the cookie drawn into `data-state` and `data-mvpl-rail`, a missing request, a value that is not open or closed, `collapse="none"`, a shared `persist` name (FR-003, FR-005, FR-016).

### Group 2: the stylesheet, the base template and the page in a browser

- [ ] T005 [US1] Port `scripts/build_css.py` and generate `mvp_layout/static/mvp_layout/layout.css`; test first `tests/test_build_css.py::TestTheStylesheet` for the committed file matching the script's output (FR-022, FR-024). Evidence: the generated file against the prototype's with `git diff --no-index`.
- [ ] T006 [US1] Port `docs/examples/base.html`; add the test pages and routes (default, contained, nested, narrow box, empty aside, outside toggle, right-to-left, heavy) in `tests/templates/layouts/` and `tests/urls.py`; test first `tests/test_layout_js.py::TestTheBaseTemplate` that each page renders and extends the base template (FR-001).
- [ ] T007 [US1] Browser tests `tests/test_layout_js.py::TestPlacement` for: every valid code's corners and fixed areas at desktop width, the contained layout filling its box, nested layouts, a sidebar a drawer in a narrow box on a wide window, an empty panel taking no space, the host's own `aside` and `header` rules untouched outside a layout, colour and size variables honoured, and the layout mirroring under `dir="rtl"` at both widths (FR-004, FR-007, FR-008, FR-010, FR-021, FR-022, FR-023, SC-002, SC-007).
- [ ] T008 [US1] Documentation: `docs/developer/layout-code.md`, `plain-templates.md` (the base template, both tags and every argument, the empty sidebar, the markup order), `styling.md` (variables, hooks, daisyUI fallback, every `mvpl` class and attribute), `right-to-left.md` (which side each name means in each direction), and `index.md`'s toctree (FR-006, FR-021, FR-022, FR-025).

## Phase 3: User Story 2 — A user opens, closes and collapses the sidebars (P1)

### Group 1: toggles, rails, drawers and the remembered state

- [ ] T009 [US2] Test first, then port `mvp_layout/static/mvp_layout/layout.js`: `TestToggles` (open, close, `aria-expanded`, `aria-controls`, `data-mvpl-when`, a toggle outside its layout, `collapse="none"` offering no toggle, an empty panel hiding its toggles) and `TestIconRail` (rail width, `mvpl-rail-only`, `mvpl-rail-hide`) (FR-007, FR-009, FR-011).
- [ ] T010 [US2] `TestDrawers`: opens as a modal dialog at phone width, focus in and back to the opener, Escape, backdrop and a link inside closing it, inert siblings, the page locked behind a whole-page drawer, resizing across the breakpoint closing an open drawer (FR-012, FR-014, edge cases).
- [ ] T011 [US2] `TestRememberedState`: closed with a `persist` name stays closed on reload with no frame showing it open, a sidebar with no name remembers nothing, two sidebars with one name share it (FR-016, SC-003).

### Group 2: focus, wheel, nesting, right-to-left and the heavy page

- [ ] T012 [US2] Test first, then the Tab trap: `TestDrawerFocus` for Tab and Shift+Tab staying inside an open drawer in a whole-page layout and in a contained one, and Escape closing only the topmost of nested drawers (FR-012, FR-013).
- [ ] T013 [US2] `TestTheWheel`: a fixed sidebar and a contained layout pass the wheel on to the page at the end of their own scrolling, and an open drawer keeps it (FR-015).
- [ ] T014 [US2] `TestRightToLeft`: every toggle, rail and drawer behaviour above run with `dir="rtl"` at phone and desktop width, and the drawer sliding in from the side its name gives (FR-021, SC-004).
- [ ] T015 [US2] `TestSidebarTransition`: open and close a docked sidebar on the heavy page and assert no long task (a frame over 50 ms) was reported, changing how the sidebar animates and recording why in `decisions.md` if one is (SC-005).
- [ ] T016 [US2] Documentation: `docs/developer/plain-templates.md` gains toggles, `data-mvpl-toggle`, `data-mvpl-when`, `data-mvpl-close`, `data-mvpl-layout`, the cookie and its need for the request context processor; `layout-code.md` and `styling.md` gain the rail classes (FR-011, FR-016, FR-025).

## Phase 4: User Story 3 — A developer controls a layout from their own script (P2)

- [ ] T017 [US3] Test first, then `MvpLayout`: `tests/test_layout_js.py::TestScriptInterface` for mounting by id and by element, mounting twice changing nothing, `state`, `open`, `close`, `toggle` with their remembered state, `sync` after the markup changed, `mvpl:change` on every change, and an unknown id raising an error that names it (FR-017, FR-018).
- [ ] T018 [US3] `TestLateLayouts`: a layout inserted after load by an insertion that runs scripts and by one that does not is mounted (FR-020).
- [ ] T019 [US3] Type the script: `// @ts-check`, JSDoc types, `tsconfig.json`, the local pre-commit hook in `.pre-commit-config.yaml` that runs `tsc`; test first that the hook fails on a deliberately mistyped call, shown in the task's evidence rather than committed (FR-019, SC-006).
- [ ] T020 [US3] Documentation: `docs/developer/scripting.md` for `MvpLayout`, each function, `mvpl:change` and its detail, and mounting a layout added later (FR-025).
