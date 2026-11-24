# The layout code

A layout is arranged by a code of nine letters in three groups, such as `lHh LpR lff`. The groups
are the top, middle and bottom rows, and each is read left, centre and right.

| Letter | Area |
|---|---|
| `h` | the header |
| `l` | the left sidebar |
| `p` | the page |
| `r` | the right sidebar |
| `f` | the footer |

The centre column is always `h`, `p` and `f`, and the middle row is always `l p r`. The four corners
are the choices: a corner names the area that reaches it. `lhh` puts the left sidebar in the
top-left corner, so it runs beside the header. `hhh` gives the corner to the header, so the header
runs across the sidebar.

An upper-case header, sidebar or footer letter keeps that area in place while the layout scrolls.
`hHh` keeps the header at the top. `LpR` keeps both sidebars in place beside the page. For a
sidebar, any of its three letters in upper case fixes it.

The rules are those of the `view` property on Quasar's `QLayout`, so a code written for one works in
the other.

## Examples

| Code | What it gives |
|---|---|
| `hHh lpr fFf` | The default. A header and footer across the full width that stay in place, with sidebars that scroll with the page. |
| `lHh LpR lff` | The left sidebar runs the full height beside the header and footer. The header and both sidebars stay in place. A documentation site or an application shell. |
| `hHh LpR fff` | A fixed header across the top, fixed sidebars below it, and a footer that scrolls with the page. |
| `lhh lpr lff` | Nothing fixed: the whole layout scrolls as one page. |

## A wrong code

A code that does not have this shape is refused with an error that states the rules. That happens
at render time, in `<c-layout>` and in `{% layout_attrs %}`, so a typo shows up the first time the
page is opened and never draws a broken grid.

```python
from mvp_layout.view import LayoutView, LayoutViewError

LayoutView.parse("lHh LpR lff").areas
# "'left header header' 'left page right' 'left footer footer'"
```

## How the grid is drawn

The code is read on the server. The root element gets the code's `grid-template-areas` in a
`--mvpl-areas` variable, the offsets a fixed sidebar sticks at in `--mvpl-left-top` and its
siblings, and a `data-mvpl-*-fixed` attribute for each fixed area. The stylesheet is static: it
reads those variables and attributes and never changes with the code.

Each area is placed by its class (`.mvpl-header`, `.mvpl-sidebar[data-side="left"]`, `.mvpl-page`
and so on), never by where it sits in the markup.

## Order in the markup

Where an area sits in the markup does not change where it appears. It does change two other things:

- **The order a screen reader reads the page in.** Screen readers follow the document, not the grid.
- **The order the Tab key moves through it.** A sighted keyboard user who tabs from the header into
  the right sidebar before the page sees focus jump across the screen.

So write the areas in the order a reader expects the landmarks in: header, left sidebar, page,
right sidebar, footer. That is the order WCAG 2.2 success criteria 1.3.2 (Meaningful Sequence) and
2.4.3 (Focus Order) ask for.
