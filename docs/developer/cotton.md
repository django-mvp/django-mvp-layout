# Using the components

With [django-cotton](https://django-cotton.com) installed, a layout is written as components.

```html
{% load static %}
<link rel="stylesheet" href="{% static 'mvp_layout/layout.css' %}" />
<script src="{% static 'mvp_layout/layout.js' %}"></script>

<c-layout view="lHh LpR lff" id="app">
  <c-layout.header>
    <c-layout.toggle side="left" when="closed" label="Navigation" />
    My project
  </c-layout.header>
  <c-layout.sidebar side="left" collapse="icons" persist="nav" label="Navigation">
    …
  </c-layout.sidebar>
  <c-layout.page tag="main">{% block content %}{% endblock content %}</c-layout.page>
  <c-layout.sidebar side="right" persist="aside" label="On this page">{% block aside %}{% endblock aside %}</c-layout.sidebar>
  <c-layout.footer>…</c-layout.footer>
</c-layout>
```

Load the script in the head and without `defer`. Each layout mounts itself from a script right after
its markup, so its sidebars and toggles are settled before the first paint.

Write the areas in reading order: header, left sidebar, page, right sidebar, footer. The layout code
places them, but screen readers and the Tab key follow the markup. See
[Order in the markup](layout-code.md#order-in-the-markup).

## `<c-layout>`

| Attribute | Default | |
|---|---|---|
| `view` | `hHh lpr fFf` | The [layout code](layout-code.md). A wrong code raises. |
| `container` | off | Fill the box the layout is placed in and scroll inside it, instead of the window. Give the layout a height. |
| `id` | generated | The layout's id. Give one when something outside the layout toggles it. |
| `class`, `style` | | Added to the layout's own. |

Without `container` the layout is the page: it scrolls with the window, and a drawer covers the
window. With it, the layout is a box: a card, a dialog, or the page area of another layout. It
scrolls inside itself, and its drawers stay inside it.

## `<c-layout.header>`, `<c-layout.page>`, `<c-layout.footer>`

The areas. Each takes `class` and any other attribute. `<c-layout.page tag="main">` draws a `<main>`.
Use it for the one page area of a whole page, and leave a nested layout's page a `<div>`, since a
document has one `<main>`.

## `<c-layout.sidebar>`

A sidebar is drawn only when it has content. A page that leaves its sidebar's block empty has no
sidebar, its column takes no space, and its toggles hide.

| Attribute | Default | |
|---|---|---|
| `side` | `left` | `left` or `right`: the `l` or `r` area of the code. |
| `collapse` | `offcanvas` | How it closes beside the page. `offcanvas` slides it away, `icons` leaves an icon rail, `none` keeps it open and gives it no toggle. |
| `breakpoint` | `lg` (left), `xl` (right) | The layout width below which it becomes a drawer over the page: `sm` 40rem, `md` 48rem, `lg` 64rem, `xl` 80rem, `2xl` 96rem. |
| `behavior` | `auto` | `auto` follows the breakpoint. `docked` keeps it beside the page at every width. `overlay` makes it a drawer at every width. |
| `width` | `16rem` (left), `18rem` (right) | Its width while open. |
| `rail-width` | `4rem` | Its width as an icon rail. |
| `closed` | off | Start closed. A remembered state wins. |
| `persist` | | A name to remember its open or closed state under, across pages and visits. |
| `label` | | Its accessible name, such as Navigation. |

An option that is not one of its choices raises, naming the choices.

**The breakpoint is the layout's width, not the window's.** A layout in a narrow card turns its
sidebars into drawers even on a wide screen. The stylesheet does this with container queries.

**A remembered state is a cookie**, `mvpl-<persist>=open` or `closed`, written by the script and read
by the server. The sidebar is drawn in that state, so it never opens and then snaps shut on load. The
server reads it from `request`, so the template needs the
`django.template.context_processors.request` context processor. The cookie decides only beside the
page. A drawer always starts closed.

### Labels in an icon rail

Inside a sidebar closed to its icon rail:

- `.mvpl-rail-hide` hides an element, such as the label beside an icon.
- `.mvpl-rail-only` shows an element only in the rail.

```html
<a href="/inbox/"><svg aria-hidden="true">…</svg><span class="mvpl-rail-hide">Inbox</span></a>
```

## `<c-layout.toggle>`

A button that opens and closes one of its layout's sidebars. It reports `aria-expanded` and
`aria-controls`, and it hides when its sidebar is absent or cannot close.

| Attribute | Default | |
|---|---|---|
| `side` | `left` | The sidebar it controls. |
| `when` | | `closed` shows the button only while its sidebar is out of sight, such as a header button that gives way to the open sidebar. `open` is the reverse. |
| `label` | Left sidebar, Right sidebar | Its accessible name. |
| `class` | | Added to its own. |

Its slot is the icon. Without one it draws a sidebar icon.

A toggle belongs to the nearest layout around it. One outside every layout, such as a mobile dock,
names its layout instead:

```html
<button type="button" data-mvpl-toggle="left" data-mvpl-layout="app">Menu</button>
```

Any element with `data-mvpl-when="left-closed"` (or `right-open`, and so on) shows only in that
state, such as a title that appears in the header while the sidebar with the logo is closed.

## Drawers

Below its breakpoint, or always with `behavior="overlay"`, a sidebar is a drawer, and an open
drawer is a modal dialog:

- focus moves into it, and returns to the button that opened it when it closes,
- the rest of its layout is inert,
- the page behind a whole-page drawer does not scroll,
- Escape closes the topmost drawer only, so a drawer in a `<dialog>` closes before the dialog,
- the backdrop, any element with `data-mvpl-close`, and following a link inside it close it.

## Nesting

A layout goes anywhere a box does, including the page area of another layout:

```html
<c-layout view="lHh Lpr lff" container style="height: 36rem">
  <c-layout.header>…</c-layout.header>
  <c-layout.sidebar side="left" label="Projects">…</c-layout.sidebar>
  <c-layout.page>
    <c-layout view="hHh lpR fff" container style="height: 100%">
      …
    </c-layout>
  </c-layout.page>
</c-layout>
```

A toggle controls the nearest layout around it, so the inner layout's toggles never reach the outer
one.
