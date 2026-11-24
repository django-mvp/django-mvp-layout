# Feature Specification: Layouts with Cotton components

**Feature Branch**: `002-cotton-components`

**Created**: 2026-11-24

**Status**: Draft

**Serves**: no goal id yet. `GOALS.md` still holds its placeholder rows, so there is no goal to cite.
This feature serves what the README's *Scope & philosophy* names as the package's purpose: a header,
two sidebars, a page and a footer arranged by a layout code, in a page or in a box inside one.

**Roadmap**: none. `docs/ROADMAP.md` has no items yet.

**Depends on**: the plain-template layout feature (issue #3), which provides the layout tags, the
stylesheet, the script and the behaviour of sidebars, drawers and toggles. The components here are
written on those tags.

**Input**: A developer writes the same layouts as Cotton components instead of plain templates:
`<c-layout>` with its header, page, footer, sidebars and toggles, nesting inside itself with
`container`. The components write their attributes with the layout tags and add only markup, so a
component layout and a plain-template layout draw the same page.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer lays out a page with Cotton components (Priority: P1)

A developer whose project uses django-cotton lays out a page by writing `<c-layout view="…">` and
putting its areas inside it: `<c-layout.header>`, `<c-layout.sidebar>` on either side,
`<c-layout.page>` and `<c-layout.footer>`, with `<c-layout.toggle>` buttons wherever they want a
sidebar opened and closed. They set each sidebar's options as attributes. They write no template
tags, no data attributes and no script, and the page behaves exactly as the same layout written in a
plain template does.

**Why this priority**: it is the feature. Everything else in this specification is a variation of
writing a layout this way.

**Independent Test**: render a template that uses every component, with the stylesheet and script
loaded, and confirm the layout, its sidebars and its toggles carry the same attributes the layout
tags write for the same options, and that the sidebars open, close and become drawers as the
plain-template layout's do.

**Acceptance Scenarios**:

1. **Given** a template with `<c-layout view="lHh LpR lff">` holding a header, a left sidebar, a page,
   a right sidebar and a footer, **When** it renders, **Then** the layout carries the attributes the
   layout tag writes for that code, and each area is drawn as that area.
2. **Given** a `<c-layout>` with no `view`, **When** it renders, **Then** it is arranged by the
   layout tag's default code.
3. **Given** a `<c-layout>` with a code that is not a valid layout code, **When** it renders, **Then**
   rendering fails with the layout tag's error.
4. **Given** a `<c-layout>` with no `id`, **When** two layouts render on one page, **Then** each gets
   a generated id and no two ids on the page are the same.
5. **Given** a `<c-layout id="app">`, **When** it renders, **Then** the layout's id is `app`, so a
   toggle outside the layout can name it.
6. **Given** a `<c-layout>` with `class`, `style` or any other attribute, **When** it renders,
   **Then** the layout carries them alongside its own.
7. **Given** the layout script is loaded in the head, **When** a `<c-layout>` is parsed, **Then** it
   mounts itself before the rest of the page is parsed, so its sidebars and toggles are in their
   state at first paint.
8. **Given** the layout script is not loaded, **When** a `<c-layout>` renders and the page loads,
   **Then** the page raises no script error.
9. **Given** `<c-layout.page tag="main">`, **When** it renders, **Then** the page area is a `main`
   element; with no `tag`, or any other value, it is a `div`.
10. **Given** a `<c-layout.header>`, `<c-layout.page>` or `<c-layout.footer>` with `class` or any
    other attribute, **When** it renders, **Then** the area carries them alongside its own.
11. **Given** a `<c-layout.sidebar>` with any of `side`, `collapse`, `breakpoint`, `behavior`,
    `width`, `rail-width`, `closed` and `persist`, **When** it renders, **Then** the sidebar carries
    exactly the attributes the sidebar tag writes for the same options, including the state a
    remembered cookie gives it.
12. **Given** a `<c-layout.sidebar>` with an option that is not one of its choices, **When** it
    renders, **Then** rendering fails with the sidebar tag's error naming the choices.
13. **Given** a `<c-layout.sidebar label="Navigation">`, **When** it renders, **Then** the sidebar's
    accessible name is the label.
14. **Given** a `<c-layout.sidebar>` whose content is empty or only whitespace, **When** it renders,
    **Then** no sidebar is drawn, its column takes no space, and its toggles hide.
15. **Given** a `<c-layout.toggle side="right">`, **When** it is pressed, **Then** it opens or closes
    the right sidebar of the nearest layout around it, and it reports whether that sidebar is open.
16. **Given** a `<c-layout.toggle>` with no `side`, **When** it renders, **Then** it controls the
    left sidebar.
17. **Given** a `<c-layout.toggle when="closed">`, **When** it renders, **Then** it carries the
    same visibility rule a plain-template toggle with that value carries.
18. **Given** a `<c-layout.toggle>` with no `label`, **When** it renders, **Then** it has an
    accessible name that says which sidebar it controls; with a `label`, the label is its name.
19. **Given** a `<c-layout.toggle>` with content inside it, **When** it renders, **Then** the content
    is the button's icon; with no content, the button draws a default icon.
---

### User Story 2 - A developer lays out a box inside a page (Priority: P2)

A developer puts a layout inside a card, a dialog, a tab, or the page area of another layout, by
writing `<c-layout container>` there. With no height the inner layout is as tall as its content.
Given a height, or a max-height it reaches, it fills it and scrolls inside it. It keeps its drawers
inside it and answers to its own width, so a layout in a narrow card turns its sidebars into drawers
on a wide screen, as the plain-template feature specifies. Its toggles reach only its own sidebars.

**Why this priority**: nesting is what the package offers beyond a page frame, and it is built on
everything Story 1 delivers.

**Independent Test**: render a `<c-layout container>` with sidebars and toggles inside the page area
of an outer `<c-layout>`, and confirm the inner layout is contained and its toggles operate the inner
sidebars only.

**Acceptance Scenarios**:

1. **Given** `<c-layout container>`, **When** it renders, **Then** the layout carries the attributes
   the layout tag writes for a contained layout.
2. **Given** a `<c-layout container>` inside the `<c-layout.page>` of another layout, **When** a
   toggle inside the inner layout is pressed, **Then** the inner layout's sidebar opens or closes and
   the outer layout's sidebars do not change.
3. **Given** a page with several nested layouts and no ids given, **When** it renders, **Then** every
   layout and sidebar id on the page is unique.

---

### Edge Cases

- A sidebar whose only content is a template block left empty by the page is drawn as no sidebar
  (Story 1, scenario 14).
- The areas are written in any order: the layout code places them, but reading and Tab order follow
  the markup, and the documentation says to write them header, left sidebar, page, right sidebar,
  footer.
- A nested layout's page stays a `div` unless the developer asks for `main`, since a document has
  one `main`.
- A toggle placed outside every layout is a plain button with the plain-template data attributes;
  `<c-layout.toggle>` belongs to the nearest layout around it.
- The same page renders twice in one process: generated ids are unique within each render.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `<c-layout>` MUST arrange its areas by its `view` layout code, writing the layout's
  attributes with the layout tag, so its default code, validation and error are the tag's.
- **FR-002**: `<c-layout>` MUST accept `container`, `id`, `class`, `style` and any other attribute,
  pass `container`, `class` and `style` to the layout tag, and add the rest to the layout element.
- **FR-003**: `<c-layout>` MUST use the `id` given, or generate one unique on the page when none is.
- **FR-004**: `<c-layout>` MUST mount itself with the layout script immediately after its markup,
  and MUST do nothing, without error, when the script is not loaded.
- **FR-005**: `<c-layout.header>`, `<c-layout.page>` and `<c-layout.footer>` MUST draw their areas,
  each accepting `class` and any other attribute.
- **FR-006**: `<c-layout.page>` MUST draw a `main` element when `tag="main"` and a `div` otherwise.
- **FR-007**: `<c-layout.sidebar>` MUST accept `side`, `collapse`, `breakpoint`, `behavior`, `width`,
  `rail-width`, `closed`, `persist`, `label`, `id`, `class` and any other attribute, and MUST write
  the sidebar's attributes with the sidebar tag, so its defaults, validation, error and remembered
  state are the tag's.
- **FR-008**: `<c-layout.sidebar>` MUST give the sidebar its `label` as its accessible name, and MUST
  use the `id` given or generate one unique on the page.
- **FR-009**: `<c-layout.sidebar>` MUST draw nothing at all when its content is empty or whitespace.
- **FR-010**: `<c-layout.toggle>` MUST draw a button that controls the `side` sidebar (left by
  default) of the nearest layout around it, with `when`, `label` and `class` passed through to the
  toggle markup the script reads, and MUST give it a default accessible name naming its side when no
  `label` is given.
- **FR-011**: `<c-layout.toggle>` MUST use its content as the button's icon, and draw a default icon
  when it has none.
- **FR-012**: A layout written with the components MUST carry the same layout, sidebar and toggle
  attributes as the same layout written with the plain-template tags and data attributes, so the
  two behave identically.
- **FR-013**: A `<c-layout container>` MUST work inside any box, including the page area of another
  `<c-layout>`, with its toggles reaching only its own sidebars.
- **FR-014**: The component names `c-layout`, `c-layout.header`, `c-layout.page`, `c-layout.footer`,
  `c-layout.sidebar` and `c-layout.toggle` MUST be the public names. Each component's attributes MUST
  be documented on the component itself and on the developer documentation's components page, which
  also says that the order of the areas in the markup sets reading and Tab order.
- **FR-015**: A host project with django-cotton installed MUST be able to use the components with
  no setup beyond installing this package and loading its stylesheet and script.

### Traceability

| Story | Requirements |
|---|---|
| User Story 1 | FR-001 to FR-012, FR-014, FR-015 |
| User Story 2 | FR-003, FR-008, FR-013 |

### Key Entities

None. The package stores nothing. The only state is the sidebar cookie, which the plain-template
feature owns.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every layout on the prototype's overview, playground and nested pages, the nested
  page's settings dialog and filters drawer included, can be written with the six components alone,
  with no layout tag, data attribute or script in the page template. The test suite's own layout pages
  hold those layouts written as components.
- **SC-002**: For every combination of layout and sidebar options the tests use, a component layout
  and a plain-template layout render identical layout, sidebar and toggle attributes.
- **SC-003**: Every attribute each component accepts appears on the developer documentation's
  components page, and every attribute documented there is accepted.
- **SC-004**: A page holding several nested layouts with no ids given renders with no repeated id.

## Clarifications

### Session 2026-11-24

- Q: Is a sidebar with empty content drawn hidden, or not drawn at all? → A: Not drawn at all. Its
  column takes no space and its toggles hide, which the script does when it finds no sidebar.
  (FR-009, Story 1 scenario 14.)
- Q: What id does a layout or sidebar get when none is given? → A: A generated one, unique on the
  page, so nested layouts never collide. A given id is used as written. (FR-003, FR-008.)
- Q: What happens when a page renders the components but does not load the script? → A: The layout
  draws in its server-rendered state and the page raises no error. The mount call is guarded.
  (FR-004.)
- Q: Should a `tag` value other than `main` on the page area be refused, as a wrong sidebar option
  is? → A: No. `main` draws a `main` element and anything else draws a `div`, as the agreed design
  does. `tag` is an element choice, not a layout option, and the only meaningful alternative to the
  default is `main`. (FR-006.)
- Q: Do the components name sides `left` and `right`, or `start` and `end`? → A: Whatever the
  plain-template feature decides for right-to-left. The components pass `side` through to its tags
  and data attributes, so they follow its names and add none of their own. (Assumptions.)

## Assumptions

- The plain-template layout feature (issue #3) is delivered first, with the layout tag, the sidebar
  tag, the stylesheet and the script. It left out the tag that generates unique ids, so this feature
  adds that tag to the same tags file. This feature restates none of the delivered behaviour: drawers, focus, Escape, the cookie, scrolling, breakpoints and right-to-left
  are specified there.
- If that feature renames `left` and `right` to `start` and `end`, the components' `side` attribute
  and the toggle's default name follow it.
- django-cotton 2.9 or later, which resolves `<c-layout>` to the component directory's `index.html`.
- The demonstration pages that use these components are separate work (issue #5).

## Out of Scope

- The layout tags, stylesheet, script, base template and every behaviour they provide (issue #3).
- The demonstration project's pages (issue #5).
- Rebuilding django-mvp's application shell on this package, which is django-mvp's own work.
