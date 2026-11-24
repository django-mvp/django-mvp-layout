# Components

With [django-cotton](https://django-cotton.com) installed, a layout is written as components. This
page covers the six components and every attribute each one takes. The components write the same
attributes the [template tags](plain-templates.md) do, so a component layout and a plain-template
layout behave the same.

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
its markup, so its sidebars and toggles are settled before the first paint. A page that does not
load the script still draws the layout in its server-rendered state and raises no error.

**Write the areas in reading order**: header, left sidebar, page, right sidebar, footer. The layout
code places them, but screen readers and the Tab key follow the order in the markup. See
[Order in the markup](layout-code.md#order-in-the-markup).

## `<c-layout>`

| Attribute | Default | |
|---|---|---|
| `view` | `hHh lpr fFf` | The [layout code](layout-code.md). A wrong code raises. |
| `container` | off | A bare attribute. Lay the layout out as a box instead of the page. With no height it is as tall as its content. Given a height or a max-height, it scrolls inside it. |
| `id` | generated | The layout's id. Give one when something outside the layout toggles it. |
| `class` | | Classes added to the layout's own. |
| `style` | | Declarations added after the layout's own. |

Any other attribute is added to the layout's element. Without `container` the layout is the page: it
scrolls with the window, and a drawer covers the window. With it, the layout is a box: a card, a
dialog, or the page area of another layout. Its drawers stay inside it, and its sidebars become
drawers by its own width. How tall it is depends on what it is given:

- **No height:** it is as tall as its content, like any card, and nothing scrolls inside it.
- **A height**, such as `style="height: 36rem"`: it fills that height and scrolls inside it.
- **A max-height**: it grows with its content up to the limit, then scrolls inside it. A fixed
  header and footer stay in view.

A box that caps its own height, such as daisyUI's `modal-box`, caps a layout inside it once the box
is a flex column: `<div class="modal-box flex flex-col">`. The layout then fills the box up to its
limit and scrolls inside it.

## `<c-layout.header>`, `<c-layout.page>`, `<c-layout.footer>`

The areas. Each takes `class` and any other attribute.

| Attribute | Default | |
|---|---|---|
| `class` | | Classes added to the area's own. |
| `tag` | `div` | On the page only. `main` draws a `<main>`, and any other value draws a `<div>`. |

Use `tag="main"` for the one page area of a whole page, and leave a nested layout's page a `<div>`,
since a document has one `<main>`.

## `<c-layout.sidebar>`

A sidebar is drawn only when it has content. A page that leaves its sidebar's block empty has no
sidebar, its column takes no space, and its toggles hide.

| Attribute | Default | |
|---|---|---|
| `side` | `left` | `left` or `right`: the `l` or `r` area of the code. |
| `collapse` | `offcanvas` | How it closes beside the page. `offcanvas` slides it away, `icons` leaves an icon rail, `none` keeps it open and gives it no toggle. |
| `breakpoint` | `lg` (left), `xl` (right) | The layout width below which it becomes a drawer over the page: `sm`, `md`, `lg`, `xl` or `2xl`. |
| `behavior` | `auto` | `auto` follows the breakpoint. `docked` keeps it beside the page at every width. `overlay` makes it a drawer at every width. |
| `width` | `16rem` (left), `18rem` (right) | Its width while open. |
| `rail-width` | `4rem` | Its width as an icon rail. |
| `closed` | off | A bare attribute. Start closed. A remembered state wins. |
| `persist` | | A name to remember its open or closed state under, across pages and visits. |
| `label` | | Its accessible name, such as Navigation. |
| `id` | generated | The sidebar's id. |
| `class` | | Classes added to the sidebar's own. |
| `style` | | Declarations added after the sidebar's own. |

An option that is not one of its choices raises, naming the choices. The breakpoint, the remembered
state and the icon rail behave as [the plain templates](plain-templates.md) describe.
The remembered state is read from the request, so the template needs the
`django.template.context_processors.request` context processor.

## `<c-layout.toggle>`

A button that opens and closes one of its layout's sidebars. It reports `aria-expanded` and
`aria-controls`, and it hides when its sidebar is absent or cannot close.

| Attribute | Default | |
|---|---|---|
| `side` | `left` | The sidebar it controls. |
| `when` | | `closed` shows the button only while its sidebar is out of sight, such as a header button that gives way to the open sidebar. `open` is the reverse. |
| `label` | Left sidebar, Right sidebar | Its accessible name. |
| `class` | | Added to the button's own. |

Its content is the icon. Without any it draws a sidebar icon.

A toggle belongs to the nearest layout around it, so the toggles of a nested layout never reach the
layout around it. A toggle outside every layout names its layout instead, with the plain
`data-mvpl-toggle` and `data-mvpl-layout` attributes. See [Add a toggle](plain-templates.md#add-a-toggle).

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
