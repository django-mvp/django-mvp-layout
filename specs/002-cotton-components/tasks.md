# Tasks: Layouts with Cotton components

Paths are repository-relative. `verify` means `uv run pytest -n auto --dist loadscope` plus
`uv run pre-commit run --all-files`. Per-task runs use the narrowest scope that covers the change.

## Phase 1: Foundation

- [ ] T001 Foundation: add `tests/test_components/` to `[tool.forge.conformance] non-mirror-paths` in
  `pyproject.toml` with a comment that its subject is Cotton templates, add `tests/test_components/__init__.py`,
  and a helper in `tests/test_components/conftest.py` that renders a file under `tests/templates/components/`
  and parses its layout, sidebar and toggle elements.

## Phase 2: User Story 1 — A developer lays out a page with Cotton components (P1)

### Group 1: the id tag and the components

- [ ] T002 [US1] Test first, then `layout_uid` in `mvp_layout/templatetags/mvp_layout.py`:
  `TestLayoutUid` for the prefix, the 12-character suffix and a thousand calls with no repeat (FR-003, FR-008).
- [ ] T003 [US1] Test first, then port `index.html`, `header.html`, `page.html` and `footer.html`:
  `tests/test_components/test_layout.py` for the default code, a code, a wrong code raising the tag's
  error, a generated id, a given id, `class`, `style` and another attribute, the mount call, the page
  as `main` and as `div`, and `class` and another attribute on header, page and footer
  (FR-001 to FR-006, scenarios 1 to 10).
- [ ] T004 [US1] Test first, then port `sidebar.html`: `tests/test_components/test_sidebar.py` for every
  option, each against `{% sidebar_attrs %}` with the same options, a wrong option raising the tag's
  error, a remembered cookie, the label, a generated and a given id and an empty or whitespace slot
  drawing nothing (FR-007 to FR-009, scenarios 11 to 14).
- [ ] T005 [US1] Test first, then port `toggle.html`: `tests/test_components/test_toggle.py` for each side,
  `when`, the default and a given label, the default icon and a slot icon (FR-010, FR-011,
  scenarios 15 to 19).

### Group 2: parity, behaviour and documentation

- [ ] T006 [US1] `tests/test_components/test_parity.py`: one component page and the same page in tags and
  data attributes render equal layout, sidebar and toggle attributes for every combination the tests
  use, ids ignored (FR-012, SC-002); and a browser test that opens, closes and turns a sidebar into a drawer
  on both pages, and that a page without the script raises no error (scenarios 7 and 8, FR-004).
- [ ] T007 [US1] Port `docs/developer/cotton.md` and list it in `docs/developer/index.md`; a test that the
  attributes declared by each component's `@prop` comments equal the attributes in the page's tables
  (FR-014, SC-003). Update `README.md` and `CHANGELOG.md`.

## Phase 3: User Story 2 — A developer lays out a box inside a page (P2)

- [ ] T008 [US2] `tests/test_components/test_nested.py`: a contained layout carries the contained
  attributes, several nested layouts without ids have no repeated id, and in the browser a toggle in the inner
  layout changes only the inner layout's sidebar (FR-013, SC-004, scenarios 1 to 3).

## Notes

- Mutation checks are part of each test task: remove the markup or flip the condition the test names and watch it
  fail, then restore.
