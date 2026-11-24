# Styling

The package ships one stylesheet, `mvp_layout/layout.css`. It is plain CSS and needs no build in
the host project. It places the areas, sizes and animates the sidebars, and draws the drawers. The
colours, type and everything inside the areas are the host project's. This page covers how to
restyle a layout with variables and hooks, and lists every public name the package uses.

## The stylesheet is one cascade layer

Every rule in the stylesheet is inside one cascade layer, `mvpl`. Rules outside a layer beat rules
inside one at any specificity and in any order, so your own rule on a package class wins:

```css
.mvpl-sidebar { background-color: oklch(0.96 0.01 250); }
.mvpl-sidebar[data-mvpl-state="closed"] { opacity: 0.8; }
```

Put such rules in the base template's `styles` block or in any stylesheet. No `!important` or extra
specificity is needed.

The package styles only its own elements. Every rule reaches an area through the layout's own
structure (`.mvpl-grid > .mvpl-sidebar`), so a rule of yours on a bare `aside` or `header` is not
changed, and the package changes nothing outside a layout.

## Change a colour

| Variable | Default | |
|---|---|---|
| `--mvpl-sidebar-bg` | `--color-base-100`, then `Canvas` | A sidebar's and a drawer's background. |
| `--mvpl-line` | `--color-base-300`, then a mix of `CanvasText` and `Canvas` | The border between a sidebar and the page, and the line under a fixed header. |

The defaults read daisyUI's theme variables when they are there, and fall back to the system colours
when they are not, so a layout is legible with no theme at all. Set either variable on a layout or
on a single sidebar:

```html
<div id="app" {% layout_attrs style="--mvpl-sidebar-bg: var(--color-base-200);" %}>
```

## Change a size

| Variable | Default | |
|---|---|---|
| `--mvpl-w` | `16rem` left, `18rem` right | A sidebar's open width. The `width` argument of `{% sidebar_attrs %}` sets it. |
| `--mvpl-rail-w` | `4rem` | An icon rail's width. The `rail_width` argument sets it. |

The header's and footer's heights are measured by the script, so a fixed sidebar sticks just below
a fixed header whatever its height.

## Restyle the inside of an icon rail

A host project on Tailwind v4 can add a variant for content inside a sidebar closed to its icon
rail:

```css
@custom-variant mvpl-rail (&:where(.mvpl-sidebar[data-mvpl-rail] *));
```

```html
<a class="mvpl-rail:justify-center mvpl-rail:px-0" href="/inbox/">…</a>
```

Without Tailwind, `.mvpl-rail-hide` hides an element in the rail and `.mvpl-rail-only` shows an
element only there. See
[Show different content in an icon rail](plain-templates.md#show-different-content-in-an-icon-rail).

## Every public name

Every class, data attribute, CSS variable and cookie the package uses starts with `mvpl`, so a host
project's own names don't collide with them.

### Classes

| Class | On |
|---|---|
| `.mvpl` | A layout's root. |
| `.mvpl-grid` | The layout's only child, which holds the areas. |
| `.mvpl-header`, `.mvpl-page`, `.mvpl-footer` | The areas. |
| `.mvpl-sidebar` | A sidebar's `aside`. |
| `.mvpl-panel` | What a sidebar holds, and what slides as a drawer. |
| `.mvpl-backdrop` | The shade behind an open drawer. |
| `.mvpl-rail-hide`, `.mvpl-rail-only` | Content hidden in, or shown only in, an icon rail. |
| `.mvpl-toggle` | A toggle the script hides when there is nothing to toggle. See [Add a toggle](plain-templates.md#add-a-toggle). |
| `.mvpl-locked` | The `html` element while a drawer holds the page. |

### Data attributes

| Attribute | On | Holds |
|---|---|---|
| `data-mvpl` | The root | Marks a layout. |
| `data-mvpl-view` | The root | The layout code. |
| `data-mvpl-container` | The root | Present on a layout that fills its box. |
| `data-mvpl-header-fixed`, `data-mvpl-footer-fixed`, `data-mvpl-left-fixed`, `data-mvpl-right-fixed` | The root | Present while that area stays in place. |
| `data-mvpl-scrolled` | The root | Present while the layout is scrolled away from its top. The package draws a line under a fixed header then. |
| `data-mvpl-side` | A sidebar | `left` or `right`. |
| `data-mvpl-collapse` | A sidebar | `offcanvas`, `icons` or `none`. |
| `data-mvpl-breakpoint` | A sidebar | `sm`, `md`, `lg`, `xl` or `2xl`. |
| `data-mvpl-behavior` | A sidebar | `auto`, `docked` or `overlay`. |
| `data-mvpl-state` | A sidebar | `open` or `closed`, beside the page. |
| `data-mvpl-persist` | A sidebar | The name its state is remembered under. |
| `data-mvpl-overlay` | A sidebar | `open` while its drawer is open. |
| `data-mvpl-mode` | A sidebar | `docked` or `overlay`, as the stylesheet decided. |
| `data-mvpl-rail` | A sidebar | Present while it is closed to its icon rail. |
| `data-mvpl-toggle` | A toggle | The side it toggles. |
| `data-mvpl-when` | A toggle | Shows it only while its sidebar is open or closed. |
| `data-mvpl-layout` | A toggle | The id of the layout it controls, when it sits outside it. |
| `data-mvpl-close` | A backdrop | Closes the drawer when clicked. |

### Variables

| Variable | Set by | Holds |
|---|---|---|
| `--mvpl-sidebar-bg`, `--mvpl-line` | You | Colours, as above. |
| `--mvpl-w`, `--mvpl-rail-w` | You | Sizes, as above. |
| `--mvpl-mode` | The stylesheet | `docked` or `overlay` on a sidebar. |
| `--mvpl-areas`, `--mvpl-left-top`, `--mvpl-left-bottom`, `--mvpl-right-top`, `--mvpl-right-bottom` | `{% layout_attrs %}` | The grid and the offsets fixed sidebars stick at. |
| `--mvpl-header-h`, `--mvpl-footer-h` | The script | The measured heights. |
| `--mvpl-dir` | The stylesheet | `1`, or `-1` under `dir="rtl"`. |
| `--mvpl-vh` | The stylesheet | The height a layout fills. |

### Cookie

`mvpl-<name>` holds the open or closed state of the sidebar whose `persist` is `<name>`, with the
value `open` or `closed`. The script writes it and `{% sidebar_attrs %}` reads it from the request.
See [Remember a sidebar's state](plain-templates.md#remember-a-sidebars-state).

## Hooks for your own rules

| Selector | Matches |
|---|---|
| `.mvpl-sidebar[data-mvpl-state="closed"]` | A sidebar closed beside the page. |
| `.mvpl-sidebar[data-mvpl-rail]` | A sidebar closed to its icon rail. |
| `.mvpl-sidebar[data-mvpl-overlay="open"]` | An open drawer. |
| `.mvpl[data-mvpl-scrolled]` | A layout scrolled away from its top. |

## Why one cascade layer

A layout's rules need a fairly specific selector to reach only their own areas, which would beat a
host's one-class rule in an ordinary stylesheet. Putting the whole stylesheet in one layer lets any
unlayered rule of yours win without a fight over specificity. The base template links the
stylesheet before the `styles` block, so your own layers come after it as well.
