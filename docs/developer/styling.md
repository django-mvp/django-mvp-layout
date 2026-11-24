# Styling

The package ships one stylesheet, `mvp_layout/layout.css`. It is plain CSS and needs no build in
the host project. It places the areas, sizes and animates the sidebars, and draws the drawers. The
colours, type and everything inside the areas are the host project's.

## The stylesheet stays out of the way

Every class, data attribute, CSS variable and cookie the package uses starts with `mvpl`:
`.mvpl-grid`, `data-mvpl-view`, `--mvpl-w`, `mvpl-nav`. A host project's own names don't collide
with them, and every rule is scoped to a layout's own elements, so the stylesheet styles nothing
else on the page.

The stylesheet is plain CSS rather than generated from Tailwind utilities, for three reasons:

- The layout is a handful of grid, sticky and container-query rules, not a set of utility classes.
  Tailwind's prefix option protects utility class names, and namespaced class names give the same
  protection here.
- A host project gets the file as it is, whether it uses Tailwind or not.
- The markup in [a plain template](without-cotton.md) stays readable: `mvpl-header` rather than a
  row of prefixed utilities.

Selectors use one class plus the layout's own structure (`.mvpl-grid > .mvpl-sidebar`), so a host's
element selectors, such as `aside { … }`, don't outrank them. A host rule written against the
package's classes on purpose does.

## Colours

| Variable | Default | |
|---|---|---|
| `--mvpl-sidebar-bg` | `--color-base-100`, then `Canvas` | A sidebar's and a drawer's background. |
| `--mvpl-line` | `--color-base-300`, then a mix of `CanvasText` and `Canvas` | The border between a sidebar and the page. |

The defaults read daisyUI's theme variables when they are there, and fall back to the system colours
when they are not, so a layout is legible with no theme at all. Set either variable on a layout or
on a single sidebar:

```html
<c-layout view="lHh LpR lff" style="--mvpl-sidebar-bg: var(--color-base-200);">
```

## Sizes

| Variable | Default | |
|---|---|---|
| `--mvpl-w` | `16rem` left, `18rem` right | A sidebar's open width. The `width` attribute sets it. |
| `--mvpl-rail-w` | `4rem` | An icon rail's width. The `rail-width` attribute sets it. |

The header's and footer's heights are measured by the script, so a fixed sidebar sticks just below
a fixed header whatever its height.

## Styling the inside of an icon rail with Tailwind

A host project on Tailwind v4 can add a variant for content inside a sidebar closed to its icon
rail:

```css
@custom-variant mvpl-rail (&:where(.mvpl-sidebar[data-mvpl-rail] *));
```

```html
<a class="mvpl-rail:justify-center mvpl-rail:px-0" href="/inbox/">…</a>
```

`.mvpl-rail-hide` and `.mvpl-rail-only` cover the common case without Tailwind; see
[Labels in an icon rail](cotton.md#labels-in-an-icon-rail).

## Hooks for the host's own rules

| Selector | Matches |
|---|---|
| `.mvpl-sidebar[data-state="closed"]` | A sidebar closed beside the page. |
| `.mvpl-sidebar[data-mvpl-rail]` | A sidebar closed to its icon rail. |
| `.mvpl-sidebar[data-overlay="open"]` | An open drawer. |
| `.mvpl[data-mvpl-scrolled]` | A layout scrolled away from its top. The package draws a line under a fixed header then. |
