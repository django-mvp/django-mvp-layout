# Prototype: the layout package

Issue: https://github.com/django-mvp/django-mvp/issues/717 (where the idea started, in django-mvp)

A page, or a box inside a page, is laid out by a nine-letter layout code such as `lHh LpR lff`,
read the way Quasar's `QLayout` reads its `view` property. The package has Cotton components and two
template tags for projects that don't use Cotton. It depends on Django and django-cotton only.
django-mvp's shell is to be rebuilt on it afterwards, which is django-mvp's own work.

Demo: http://devserver:8066/ (overview), http://devserver:8066/playground/,
http://devserver:8066/nested/ and http://devserver:8066/without-cotton/

## The features

The template tags are the base layer and the Cotton components are written on them, so the plain
templates are built first (Sam, 2026-11-24).

### 1. Layouts in plain templates (feature)

A developer arranges a page, or a box inside one, by a layout code in ordinary Django templates,
copying `docs/examples/base.html` and extending it with blocks, and gets sidebars that open, close,
collapse to an icon rail and turn into drawers by themselves.

- `{% layout_attrs view container class style %}` and
  `{% sidebar_attrs side collapse breakpoint behavior persist closed width rail_width class %}`
  write a layout's and a sidebar's attributes. A wrong option or code raises.
- `data-mvpl-toggle` buttons, with `data-mvpl-layout` for a toggle outside the layout.
- An empty `.mvpl-panel` hides its sidebar and its toggles.
- Breakpoints measured against the layout's own width (container queries).
- Drawers are modal dialogs: focus in and back, Escape closes the topmost only, the rest of the
  layout inert, the page locked behind a whole-page drawer, backdrop and links close it.
- The remembered state is a cookie, `mvpl-<persist>`, drawn by the server.
- Only a drawer keeps the mouse wheel. Fixed sidebars and contained layouts pass it on to the page.
- Script API: `MvpLayout("app")` mounts a layout by id or element. `MvpLayout.sync`, `state`,
  `toggle`, `open` and `close` take the same, and a `mvpl:change` event fires on the layout.

### 2. Layouts with Cotton (feature)

A developer writes the same layouts as Cotton components, `<c-layout view="…">` and its areas.

- `<c-layout view container id class style>`, `<c-layout.header>`, `<c-layout.page tag>`,
  `<c-layout.footer>`.
- `<c-layout.sidebar side collapse breakpoint behavior width rail-width closed persist label>`,
  drawn only when it has content.
- `<c-layout.toggle side when label>`.

Depends on 1. The components write their attributes with its tags and add only markup.

### 3. The demo project (resolve)

Overview, playground, nested layouts and the Without Cotton page, which extends
`docs/examples/base.html` itself.

## Shared pieces

| Piece | Where it occurs | Becomes | Built by |
|---|---|---|---|
| Reading the code | `mvp_layout/view.py` | The parser, used by the tags | 1 |
| Sidebar options and the cookie | `mvp_layout/templatetags/mvp_layout.py` | The tags, used by plain templates and the components | 1 |
| Drawer rules per breakpoint | `scripts/build_css.py` writes `mvp_layout/static/mvp_layout/layout.css` | The stylesheet, checked by a test | 1 |
| Behaviour | `mvp_layout/static/mvp_layout/layout.js` | The script | 1 |
| The base template | `docs/examples/base.html` | Documentation and the demo's Without Cotton page | 1 |

## The look

| File | Lands in |
|---|---|
| `mvp_layout/templates/cotton/layout/*.html` | Same paths |
| `mvp_layout/static/mvp_layout/layout.css`, `scripts/build_css.py` | Same paths |
| `mvp_layout/static/mvp_layout/layout.js` | Same path |
| `docs/examples/base.html` | Same path |
| `demo/` (templates, views, `assets/demo.css`) | Same paths |

Screens for the parity check, each at 390 and 1440 wide: the four demo pages above, the playground
at each width setting, and the nested page with the settings dialog and the filters drawer open.

## The data model

None. The only state is the sidebar cookie.

## Decisions

- 2026-11-24: The layout is a standalone package, not part of django-mvp. (Sam)
- 2026-11-24: Keep `view` as the attribute name, as Quasar does. (Sam)
- 2026-11-24: Document that the order of the areas in the markup sets reading and Tab order. (Sam)
- 2026-11-24: Provide Cotton components and document plain templates with a copyable base.html. (Sam)
- 2026-11-24: Named django-mvp-layout, imported as mvp_layout. (Sam)
- 2026-11-24: Fixed sidebars pass the wheel on to the page, as in sphinx-daisyui. (Sam)
- 2026-11-24: The script stays plain JavaScript. (Sam)
- 2026-11-24: A layout is mounted with `MvpLayout("app")`, by id. (Sam)
- 2026-11-24: The layout has to work right-to-left. Designed in the build, not now. (Sam)
- 2026-11-24: Plain templates and their tags are built first, and the Cotton components on them.
  (Sam)

## Decided on my own

- **Plain CSS, not Tailwind**, with every class, attribute, variable and cookie prefixed `mvpl-`.
- **No daisyUI dependency.** Colours read daisyUI's theme variables and fall back to system colours.
- **Components are `<c-layout>` and `<c-layout.…>`**, not `<c-mvp_layout.…>`.
- **Areas are written header, left sidebar, page, right sidebar, footer** everywhere.
- **The script is type-checked** with `// @ts-check` and JSDoc, and tested in a real browser
  rather than in jsdom.

## Faked or skipped

- **The script is not type-checked yet.** `// @ts-check`, JSDoc types and a `tsc --noEmit` hook
  belong to feature 1.
- **Focus is not trapped** in a contained drawer. Only the layout's own areas are inert. Feature 1.
- **Right-to-left is not tested or documented.** Feature 1. Set by hand with `dir="rtl"`, the layout
  already mirrors with the same stylesheet: the grid follows the writing direction, borders and
  drawers use logical properties, and `--mvpl-dir` flips the drawer's slide. The `left` sidebar is
  drawn on the right and its drawer slides in from the right. Still open:
  - whether `left` and `right` are the right names when they mean the start and end side, in the
    sidebar's `side` attribute, `data-mvpl-toggle`, `data-mvpl-when` and the code's `l` and `r`,
    or whether they become `start` and `end`, and what Quasar's `view` does in right-to-left,
  - browser tests in right-to-left at both widths, and a demo switch to show it,
  - the docs, which say left and right throughout.
- **Width transitions** on docked sidebars animate `width`. Fine in the demo, unmeasured on a heavy
  page. Feature 1.
- **The browser tests cover the demo pages only.** Feature 1.
