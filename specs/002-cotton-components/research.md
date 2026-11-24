# Research — 002, layouts with Cotton components

## Assumptions checked

- **django-cotton resolves `<c-layout>` to `cotton/layout/index.html`.** The installed django-cotton
  is 2.9.0, and its loader tries `<name>.html` and then `<name>/index.html`. Holds.
- **The agreed components render.** On the prototype's demo (http://devserver:8066/), the overview,
  /playground/, /nested/ and /without-cotton/ pages all return 200. /nested/ draws six layouts, each
  followed by its own mount call, with seven sidebars and eleven toggles. Holds.
- **The tags the components call exist on `main`.** Checked again on 2026-11-24 after the plain-template
  feature merged. `layout_attrs` and `sidebar_attrs` are in `mvp_layout/templatetags/mvp_layout.py`.
  `layout_uid` is not: that feature left it out, and the unique ids this feature requires (FR-003,
  FR-008) need it. Holds for the two attribute tags, and the id tag is built here.
- **The package declares django-cotton.** The plain-template feature set the runtime dependencies to
  `django>=5.2` and `django-cotton>=2.9`, with a `deptry` ignore for the unimported package. Holds, and
  nothing more is needed.
- **Cotton resolves the components in this repository's settings.** Rendering a template file that
  uses the prototype's `<c-layout>` templates in the test settings reaches `sidebar.html` and stops at
  `layout_uid`, the one tag that is missing. Holds, and it shows Cotton only compiles a component
  from a template file: `Engine.from_string` leaves `<c-…>` as text, so tests render files under
  `tests/templates/components/`.
- **Cotton's attribute handling the components lean on.** `<c-vars>` names with a dash become
  underscores (`rail-width` is `rail_width`), a bare attribute such as `container` or `closed` arrives
  as `True`, and `{{ attrs }}` carries every attribute `<c-vars>` did not name. The build's first
  tests pin each of these, and a difference is a decision recorded in `decisions.md`.

## Planning notes answered

### The prototype (adopted)

Read `PROTOTYPE.md` and the six files under "The look" for this feature, `mvp_layout/templates/cotton/layout/`
`index.html`, `header.html`, `page.html`, `footer.html`, `sidebar.html` and `toggle.html`. They are the agreed
design and are copied across, then cleaned to the repository's standards. Nothing is redrawn.

### Shared pieces (adopted)

The parser, the sidebar options and cookie, the stylesheet and the script are used as they stand. The
components change none of them. The one addition to a shared file is the id tag, below.

### The look is ported, never redrawn (adopted)

The plan lists each of the six files. A check against `git diff origin/prototype-layout HEAD --
mvp_layout/templates/cotton/layout/` at the end names every difference, and each is either a planned
clean-up or fixed.

### The id tag (adopted, and added to the tags file)

`layout_uid` is added to `mvp_layout/templatetags/mvp_layout.py`, as the note says, not to a file of this
feature's own. It returns `<prefix>-<12 hex characters>` from `uuid.uuid4()`. The prototype used 8, and 12
keeps the chance of two ids on one page meeting negligible however many layouts nest.

### The developer page (adopted)

`docs/developer/cotton.md` is ported. The sections the plain-template pages already document (drawers,
the remembered state's cookie, container queries, icon-rail classes, nesting behaviour) are cut to a
sentence and a link.

### The dependency (adopted, nothing to do)

See above. The package template's sample component `cotton/mvp_layout/example.html` stays: issue #5
removes it.

### Left and right (adopted)

The plain-template feature kept `left` and `right` (ADR 0002). The components use them.

## What already exists

- **Layout and sidebar attributes**: the installed tags `layout_attrs` and `sidebar_attrs` in this repo.
  The components call them and write no attribute of their own. Found at step 2.
- **Extra attributes on an element**: Cotton's `{{ attrs }}`, installed package django-cotton 2.9. Found
  at step 3.
- **Empty slot check**: `slot.strip` on Cotton's slot, as the prototype's sidebar does. Found at step 3.
- **A unique id per element**: `layout_uid`, new code, three lines. Django has no per-render unique id
  tag and `{% cycle %}` and `{% firstof %}` do not make one. Step 7.
- **The default toggle icon**: an inline `<svg>` in the toggle component. daisy-cotton and django-mvp's
  icon component are not dependencies of this package. Step 7, the prototype's markup.
- **A parity check against a plain-template layout** (tests): the repository's own tags, rendered in the
  same test. Step 2.
