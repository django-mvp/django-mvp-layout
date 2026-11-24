# Feature Specification: Layouts in plain templates

**Feature Branch**: `001-plain-templates`

**Created**: 2026-11-24

**Status**: Draft

**Serves**: no goal id yet. `GOALS.md` has three rows with the goals still to be written. This
feature is the package's core purpose as the README's *Scope & philosophy* states it: a layout
arranged by a layout code, with sidebars that open, close, collapse and nest. It will serve the
first Essential goal once that row is written.

**Roadmap**: none. `docs/ROADMAP.md` holds only its template item, so no item covers this yet.

**Issue**: #3

**Input**: A developer lays out a page, or a box inside a page, by a nine-letter layout code such
as `lHh LpR lff`, read the way Quasar's `QLayout` reads its `view` property, in ordinary Django
templates with no component library. They copy a base template the package documents, extend it
with ordinary blocks, and write each layout's and sidebar's attributes with two template tags. The
sidebars then look after themselves: they open, close, shrink to an icon rail and become drawers
when the layout is narrow, and a person using the site gets drawers that behave as modal dialogs
and sidebars that stay the way they left them. A script interface lets the host project's own code
open, close and read the sidebars. The design is the one on the `prototype-layout` branch, where
it is feature 1 of `PROTOTYPE.md`.

## Clarifications

### Session 2026-11-24 (intake)

The design was settled on a working prototype before this specification was written. Its screens
and the maintainer's recorded decisions are taken as agreed. The intake reading was not put as
questions, so every place the request was silent was settled from the prototype, and each is
recorded in `decisions.md`.

- **Q: Does this feature include the Cotton components?**
  A: No. They are the next feature and are written on this one's tags, stylesheet and script. This
  feature builds every shared piece and the components add only markup.

- **Q: Does it include the demo project's pages?**
  A: No. Replacing the demo is separate work. This feature's browser tests run on pages of their
  own, so they do not wait on the demo.

- **Q: Is the tag's extra class argument written `class` or `css_class`?**
  A: `css_class`, as on the prototype. A tag's arguments are Python keyword arguments and `class`
  cannot be one. Recorded as FR-002 and FR-003.

- **Q: Are a sidebar's sides named `left` and `right`, or `start` and `end`?**
  A: Decided during the build's research, from Quasar's behaviour in right-to-left and the
  practice of CSS logical properties. Whichever is chosen applies to every place a side is named.
  Recorded as FR-021.

### Session 2026-11-24 (coverage scan)

- **Q: What does a sidebar do with no `persist` name?**
  A: It starts in the state its options give it on every page load and remembers nothing.
  Recorded as FR-016.

- **Q: What happens to a remembered state the sidebar can no longer take, such as `closed` for a
  sidebar set never to close?**
  A: The sidebar's own options win and the remembered value is ignored. Recorded as FR-016.

- **Q: Which drawer does Escape close when drawers are open in nested layouts?**
  A: Only the topmost, so a drawer inside a dialog closes before the dialog does. Recorded as
  FR-012.

- **Q: Is a layout added to the page after it loads, by a fetched fragment or a dialog's content,
  handled?**
  A: Yes. It is mounted by the same call, and one that arrives without running scripts is still
  mounted. Recorded as FR-020.

- **Q: Does a template without the request context processor still render?**
  A: Yes. It renders every sidebar in the state its options give it, and only the remembered state
  is lost. The documentation says the processor is needed for that. Recorded as FR-016.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer lays out a page by a layout code in a plain template (Priority: P1)

A developer copies the documented base template into their project, sets its layout code and each
sidebar's options with the two template tags, and extends it with ordinary blocks for the header,
the sidebars, the page and the footer. The same markup with `container` lays out a box inside a
page, and layouts nest. They choose how each sidebar collapses, the layout width below which it
becomes a drawer, whether it is always docked or always a drawer, its widths, whether it starts
closed, and a name under which its state is remembered. A wrong layout code or option stops the
page with an error that says what is allowed. They can restyle the layout through its variables and
hooks, and the package styles nothing outside it.

**Why this priority**: it is the feature. Every other story needs a layout drawn this way.

**Independent Test**: render a template extending the documented base template with several layout
codes and sidebar options, and assert the rendered attributes, the placement of each area at
desktop and phone widths in a browser, and the errors for wrong values.

**Acceptance Scenarios**:

1. **Given** a project template extending the documented base template, **When** it fills the
   header, navigation, page and footer blocks, **Then** the page renders with each area placed
   where the base template's layout code puts it.
2. **Given** a layout written with `{% layout_attrs %}` and a layout code such as `lHh LpR lff`,
   **When** the page is shown wide enough for its sidebars to be docked, **Then** each corner is
   taken by the area the code names for it, and every area whose letter is upper case stays in
   place while the layout scrolls.
3. **Given** a layout code of the wrong shape, **When** the template renders, **Then** rendering
   raises an error that states the rules of a layout code.
4. **Given** a sidebar option that is not one of its choices, **When** the template renders,
   **Then** rendering raises an error naming the allowed choices.
5. **Given** a layout with no layout code, **When** it renders, **Then** it uses the default code
   `hHh lpr fFf`.
6. **Given** a sidebar written with `{% sidebar_attrs %}` and a `collapse`, `breakpoint`,
   `behavior`, `width`, `rail_width`, `closed` and `persist`, **When** the page renders, **Then**
   the sidebar carries each option and behaves as that option describes (User Story 2).
7. **Given** a sidebar whose panel block is left empty, **When** the page renders, **Then** that
   sidebar takes no space and every toggle for it is hidden.
8. **Given** a layout with `container` placed in a box on a page, **When** the box is narrower than
   a sidebar's breakpoint while the window is wider, **Then** that sidebar is a drawer, because the
   breakpoint is measured against the layout's own width.
9. **Given** a contained layout nested inside another layout's page, **When** both are shown,
   **Then** each has its own sidebars, breakpoints and toggles, and a toggle in one acts only on
   its own layout unless it names another with `data-mvpl-layout`.
10. **Given** a button outside a layout carrying `data-mvpl-toggle` and `data-mvpl-layout` naming
    that layout, **When** it is clicked, **Then** it opens or closes that layout's sidebar.
11. **Given** a host project page with its own styles for elements such as `aside` and `header`,
    **When** a layout is on it, **Then** the package's rules apply only to the layout's own
    elements, and the host's rules on the package's classes take effect.
12. **Given** a host project that sets the layout's colour or size variables on a layout or a
    sidebar, **When** the page renders, **Then** the layout uses the values set, and with no theme
    present it still draws legible sidebars from system colours.
13. **Given** a layout in a document with `dir="rtl"`, **When** it is shown at desktop and at phone
    width, **Then** the layout mirrors: each sidebar is drawn on the side the reading direction
    gives it and its drawer slides in from that side.

---

### User Story 2 - A user opens, closes and collapses the sidebars (Priority: P1)

A person using a site built on the package opens and closes each sidebar with its toggle, closes a
sidebar to its icon rail, and on a narrow layout uses a sidebar as a drawer over the page. A drawer
behaves as a modal dialog: focus moves into it and back to the toggle, Escape closes it, nothing
behind it can be reached, the page behind does not scroll, and the backdrop or a link inside closes
it. The mouse wheel scrolls the page wherever the pointer is, except over an open drawer. A sidebar
they closed is still closed on the next page, with no flash of it open first. All of it works with
a keyboard and a screen reader, and in a right-to-left language.

**Why this priority**: the sidebars looking after themselves is what the developer installs the
package for. A layout that cannot be operated by the person using the site has no value.

**Independent Test**: in a real browser, at desktop and phone widths, click and key through the
toggles, drawers and rails of a test page, and assert state, focus, inert regions, scrolling and the
remembered state across reloads.

**Acceptance Scenarios**:

1. **Given** a docked sidebar that is open, **When** the user activates its toggle, **Then** it
   closes beside the page, the toggle reports it collapsed, and activating the toggle again opens
   it.
2. **Given** a sidebar set to collapse to an icon rail, **When** the user closes it, **Then** it
   stays beside the page at its rail width, and content the host marks for the rail only, or for
   the open sidebar only, shows or hides to match.
3. **Given** a sidebar set never to collapse, **When** the layout is wider than its breakpoint,
   **Then** it stays open and no toggle for it is offered.
4. **Given** a layout narrower than a sidebar's breakpoint, or a sidebar set always to be a drawer,
   **When** the user activates its toggle, **Then** the sidebar opens over the page as a modal
   dialog and focus moves into it.
5. **Given** an open drawer, **When** the user presses Escape, clicks the backdrop or follows a
   link inside it, **Then** it closes and focus returns to the element that opened it.
6. **Given** an open drawer, **When** the user presses Tab repeatedly, **Then** focus stays inside
   the drawer, in a whole-page layout and in a contained one alike, and nothing else in the layout
   can be reached.
7. **Given** an open drawer in a whole-page layout, **When** the user scrolls, **Then** the page
   behind it does not move.
8. **Given** open drawers in two nested layouts, **When** the user presses Escape, **Then** only the
   topmost drawer closes.
9. **Given** a fixed sidebar or a contained layout under the pointer, **When** the user turns the
   mouse wheel past the end of its own scrolling, **Then** the page scrolls; over an open drawer the
   wheel scrolls only the drawer.
10. **Given** a sidebar with a `persist` name that the user closed, **When** they load another page
    that has that sidebar, **Then** it is drawn closed from the first paint and never shows open
    first.
11. **Given** a toggle, **When** a screen reader reaches it, **Then** it announces which sidebar it
    controls and whether that sidebar is expanded.
12. **Given** a layout in a right-to-left document, **When** the user opens and closes its sidebars
    at desktop and phone widths, **Then** every behaviour above works the same, mirrored.

---

### User Story 3 - A developer controls a layout from their own script (Priority: P2)

A developer's own JavaScript mounts a layout, reads which sidebars are open and whether each is a
drawer, opens, closes or toggles a sidebar, and listens for every change. Layouts added to the page
later, by a fetched fragment or a dialog's content, are mounted the same way.

**Why this priority**: the toggles cover most pages. A host project's own controls, saved
preferences or analytics need the script interface, and it can follow the first two stories.

**Independent Test**: on a test page in a real browser, call each script function by layout id and
by element, and assert the returned state, the sidebar's resulting state and the change events.

**Acceptance Scenarios**:

1. **Given** a layout with an id, **When** the developer's script calls `MvpLayout("app")` or passes
   the element, **Then** the layout is mounted, and calling it again changes nothing.
2. **Given** a mounted layout, **When** the script calls `MvpLayout.state`, **Then** it returns, for
   each sidebar present, whether it is open and whether it is a drawer.
3. **Given** a mounted layout, **When** the script calls `MvpLayout.open`, `close` or `toggle` with
   a side, **Then** that sidebar changes as a toggle would have changed it, including its
   remembered state.
4. **Given** a listener for `mvpl:change` on a layout, **When** any sidebar in it opens, closes or
   switches between docked and drawer, **Then** the event fires on that layout carrying the new
   state.
5. **Given** a layout's markup inserted into the page after it loaded, **When** the insertion runs
   its scripts or runs none, **Then** the layout is mounted either way.
6. **Given** a layout whose markup the script changed, **When** the developer calls
   `MvpLayout.sync`, **Then** toggles and sidebars are brought back in line with the markup.
7. **Given** an id that names no layout, **When** the script calls any function with it, **Then**
   the call fails with an error naming the id.

---

### Edge Cases

- A layout code with extra or missing spaces between its groups is read the same as the code
  written with single spaces.
- A remembered value that is neither open nor closed, or a cookie the host renamed, is ignored and
  the sidebar takes its options' state.
- A layout whose header or footer height changes after load keeps its fixed sidebars just clear of
  them.
- A toggle for a sidebar whose panel is empty, or that cannot close, is hidden rather than offered
  and doing nothing.
- A layout resized across a sidebar's breakpoint while its drawer is open closes the drawer and
  frees the page, so nothing is left inert.
- Two layouts on one page with sidebars of the same `persist` name share one remembered state.
- A template rendered without a request (an email, a test) renders every sidebar in its options'
  state.

## Requirements *(mandatory)*

### Functional Requirements

**Writing a layout**

- **FR-001** (US1): The package MUST document a complete base template, `docs/examples/base.html`, that
  a host project copies and extends with ordinary blocks for the title, styles, header, navigation,
  page, aside and footer, written without django-cotton.
- **FR-002** (US1): `{% layout_attrs %}` MUST write a layout root's attributes from `view` (the layout
  code), `container`, `css_class` and `style`, every argument optional and nameable.
- **FR-003** (US1): `{% sidebar_attrs %}` MUST write a sidebar's attributes from `side`, `collapse`,
  `breakpoint`, `behavior`, `persist`, `closed`, `width`, `rail_width` and `css_class`, every
  argument optional and nameable, with the defaults the prototype uses.
- **FR-004** (US1): A layout code MUST be read as Quasar's `QLayout` reads `view`: three groups for the
  top, middle and bottom rows, each corner naming the area that reaches it, and an upper-case
  header, sidebar or footer letter making that area fixed. A missing code means `hHh lpr fFf`.
- **FR-005** (US1): A layout code of the wrong shape, and a sidebar option outside its choices, MUST
  raise an error at render time that states the rules or the allowed choices.
- **FR-006** (US1): The layout code MUST place the areas, and their order in the markup MUST set the
  reading and Tab order. The documentation MUST say so and give the order header, left sidebar,
  page, right sidebar, footer.
- **FR-007** (US1): A sidebar whose panel is empty MUST take no space, and every toggle for it MUST be
  hidden.
- **FR-008** (US1): A layout with `container` MUST fill the box it is placed in and scroll inside it.
  Layouts MUST nest, each with its own sidebars, breakpoints and toggles.

**Sidebars**

- **FR-009** (US1, US2): Each sidebar MUST support collapsing off the side, collapsing to an icon rail, and
  never collapsing, and behaviours that follow its breakpoint, stay docked, or are always a drawer.
- **FR-010** (US1, US2): A sidebar's breakpoint MUST be measured against the layout's own width, never the
  window's.
- **FR-011** (US1, US2): Any element with `data-mvpl-toggle` naming a side MUST open and close that sidebar,
  report `aria-expanded` and `aria-controls`, and act on its own layout unless `data-mvpl-layout`
  names another. `data-mvpl-when` MUST show a toggle only in the state it names, and an element
  with `data-mvpl-close` inside a drawer MUST close it.

**Drawers**

- **FR-012** (US2): An open drawer MUST behave as a modal dialog: focus moves into it and returns to its
  opener when it closes, Escape closes the topmost open drawer only, and the rest of the layout is
  inert.
- **FR-013** (US2): Focus MUST stay inside an open drawer in a contained layout as well as in a
  whole-page one.
- **FR-014** (US2): The page behind a drawer in a whole-page layout MUST not scroll while the drawer is
  open. The backdrop and any link inside the drawer MUST close it.
- **FR-015** (US2): Only an open drawer MUST keep the mouse wheel. A fixed sidebar and a contained layout
  MUST pass the wheel on to the page once their own scrolling ends.

**Remembered state**

- **FR-016** (US1, US2): A sidebar with a `persist` name MUST remember its open or closed state in a cookie
  named `mvpl-<persist>`, and the server MUST draw the remembered state so the first paint is
  already right. A sidebar with no `persist` name remembers nothing. A remembered value the sidebar
  cannot take is ignored. A template without a request in its context renders the options' state.

**Script interface**

- **FR-017** (US3): `MvpLayout(<id or element>)` MUST mount a layout, and calling it again MUST change
  nothing. `MvpLayout.sync`, `state`, `toggle`, `open` and `close` MUST take an id or an element.
- **FR-018** (US3): An `mvpl:change` event carrying the layout's state MUST fire on the layout whenever a
  sidebar's state or mode changes.
- **FR-019** (US3): The script MUST stay plain JavaScript with no build step, type-checked with
  `// @ts-check` and JSDoc types, and the type check MUST run as one of the repository's checks.
- **FR-020** (US3): Layouts inserted after the page loads MUST be mounted, whether the insertion runs
  scripts or not.

**Right-to-left**

- **FR-021** (US1, US2): The layout MUST work right-to-left with the same stylesheet, at every width. The
  build's research MUST decide whether sides are named `left` and `right` or `start` and `end`,
  and the chosen names MUST mean the same side in the sidebar's `side`, `data-mvpl-toggle`,
  `data-mvpl-when` and the layout code's letters. The documentation MUST say which side each name
  means in each direction.

**Styles**

- **FR-022** (US1): The stylesheet MUST be plain CSS needing no build in the host project, and every
  class, data attribute, variable and cookie the package uses MUST start with `mvpl`. Its rules
  MUST apply only to a layout's own elements.
- **FR-023** (US1): Colours MUST be read from daisyUI's theme variables where they exist and fall back to
  system colours, and the package MUST NOT depend on daisyUI or any CSS framework.
- **FR-024** (US1): The stylesheet MUST be generated by a script in the repository, and a check MUST fail
  when the committed stylesheet differs from what the script generates.

**Documentation**

- **FR-025** (US1, US3): The documentation MUST cover the layout code, writing a layout in a plain template,
  both tags and their arguments, toggles, the script interface, styling, right-to-left and the
  markup order. Every public name MUST be quoted on a page.

### Key Entities

- **Layout code**: the nine letters that arrange a layout (`CONTEXT.md`).
- **Sidebar state**: open or closed, and docked or drawer, for each sidebar of a layout. The
  remembered part is open or closed only, kept in the `mvpl-<persist>` cookie.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer gets a working page with two sidebars by copying the documented base
  template and extending it, with no other file written beyond their own blocks.
- **SC-002**: Every valid layout code (each of the 16 corner choices, with each area fixed and not
  fixed) places its areas in the corners it names, and every invalid code tried raises.
- **SC-003**: A sidebar closed by the user and given a `persist` name is drawn closed from the
  first paint on the next load, with no frame showing it open.
- **SC-004**: Every drawer behaviour in User Story 2 passes in a real browser at a phone width and
  a desktop width, both left-to-right and right-to-left.
- **SC-005**: Opening and closing a docked sidebar on a page whose page area is long and heavy is
  measured during the build, and produces no frame longer than 50 ms.
- **SC-006**: The script's type check, the stylesheet check, the tests, lint and the build all pass
  as repository checks.
- **SC-007**: The package's stylesheet leaves the styles of an element outside a layout exactly as
  they were.

## Assumptions

- The Cotton components are built after this feature, on its tags, stylesheet and script, and add
  only markup.
- The demo project's pages are replaced separately and are not part of this feature.
- django-cotton remains a runtime dependency of the package as a whole, even though a plain
  template never uses it.
- The defaults (breakpoint `lg` for the left sidebar and `xl` for the right, collapse off the side,
  behaviour following the breakpoint, sidebars open) are the prototype's.
- Breakpoint names are `sm`, `md`, `lg`, `xl` and `2xl`, measured against the layout's width.
