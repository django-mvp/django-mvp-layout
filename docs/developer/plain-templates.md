# Plain templates

A layout is two template tags and a fixed set of class names. A project writes the markup in a plain
base template that its pages extend with ordinary blocks. This page covers the base template to
copy, the markup it must keep, and both tags with every argument.

django-cotton stays installed, because the package depends on it, but a plain template never uses
it.

## Use the base template

[`docs/examples/base.html`](https://github.com/django-mvp/django-mvp-layout/blob/main/docs/examples/base.html)
is a complete base template. Copy it into your project's `templates/`, change the layout code and
the sidebars' options, and extend it:

1. Copy the file to `templates/base.html`.
2. Add the request context processor, `django.template.context_processors.request`, to your
   template settings. The tag that draws a sidebar reads its remembered state from the request.
3. Extend it in a page:

   ```html
   {% extends "base.html" %}

   {% block header %}My project{% endblock header %}

   {% block navigation %}<nav>…</nav>{% endblock navigation %}

   {% block content %}
     <h1>Hello</h1>
   {% endblock content %}
   ```

The page loads with the header, the navigation sidebar, the page and the footer drawn by the code
you chose. The base template's blocks are `title`, `styles`, `header`, `navigation`, `content`,
`aside` and `footer`.

The stylesheet is linked before the `styles` block, so the rules you add there come after the
package's own and win. See [Styling](styling.md#the-stylesheet-is-one-cascade-layer).

## Keep this markup

```html+django
{% load mvp_layout %}
<div id="app" {% layout_attrs "hHh LpR fFf" %}>
  <div class="mvpl-grid">
    <header class="mvpl-header">…</header>
    <aside {% sidebar_attrs "left" collapse="icons" persist="nav" %} aria-label="Navigation">
      <div class="mvpl-backdrop" data-mvpl-close aria-hidden="true"></div>
      <div class="mvpl-panel">…</div>
    </aside>
    <main class="mvpl-page">…</main>
    <aside {% sidebar_attrs "right" %} aria-label="On this page">
      <div class="mvpl-backdrop" data-mvpl-close aria-hidden="true"></div>
      <div class="mvpl-panel">…</div>
    </aside>
    <footer class="mvpl-footer">…</footer>
  </div>
</div>
<script>MvpLayout("app");</script>
```

The parts that have to be exactly this:

- The root carries `{% layout_attrs %}`, and its only child is `.mvpl-grid`.
- The areas are direct children of `.mvpl-grid` and carry `mvpl-header`, `mvpl-page` and
  `mvpl-footer`.
- A sidebar is an element carrying `{% sidebar_attrs %}`, holding a `.mvpl-backdrop` and a
  `.mvpl-panel`, in that order.
- The script tag after the layout mounts it before the first paint. Without it the layout mounts on
  `DOMContentLoaded`.

Write the areas in reading order, as [the layout code page](layout-code.md#order-in-the-markup)
explains.

## Put a layout in a box

Pass `container=True` to `{% layout_attrs %}` and give the root element a height, such as
`style="height: 100%"`. The layout then fills the box it is placed in and scrolls inside it, and its
sidebars become drawers by the width of the box, not the window.

## `{% layout_attrs %}`

```
{% layout_attrs view container css_class style %}
```

Every argument is optional and can be given by name. The tag writes `class="mvpl …"`, the layout's
`data-mvpl-*` attributes and a `style` with its grid areas.

| Argument | Accepts | Default |
|---|---|---|
| `view` | A [layout code](layout-code.md). | `hHh lpr fFf` |
| `container` | `True` to fill the box the layout is in. | `False` |
| `css_class` | Classes added to the layout's own. | none |
| `style` | Declarations added after the layout's own. | none |

Don't add another `class` or `style` attribute to the element, because the browser keeps only the
first. Pass them as `css_class` and `style` instead.

A `view` that is not a layout code raises `LayoutViewError`.

## `{% sidebar_attrs %}`

```
{% sidebar_attrs side collapse breakpoint behavior persist closed width rail_width css_class %}
```

Every argument is optional and can be given by name. The tag writes the sidebar's `class` and
`data-mvpl-*` attributes.

| Argument | Accepts | Default |
|---|---|---|
| `side` | `left` or `right`, the reading-start and reading-end sides. | `left` |
| `collapse` | `offcanvas` slides the sidebar away, `icons` leaves a rail, `none` never closes it beside the page. | `offcanvas` |
| `breakpoint` | `sm`, `md`, `lg`, `xl` or `2xl`, the layout width below which the sidebar is a drawer. | `lg` for the left, `xl` for the right |
| `behavior` | `auto` is a drawer below the breakpoint, `docked` is always beside the page, `overlay` is always a drawer. | `auto` |
| `persist` | The name the open or closed state is remembered under. Without one nothing is remembered. | none |
| `closed` | `True` or `False`, whether the sidebar starts closed. Any other value leaves it open. | `False` |
| `width` | The sidebar's open width, as a CSS length. | `16rem` left, `18rem` right |
| `rail_width` | The width of its icon rail, as a CSS length. | `4rem` |
| `css_class` | Classes added to the sidebar's own. | none |

A value outside the choices raises `LayoutOptionError`, and its message names the choices.

The tag reads the remembered state from `request`, so the template needs the
`django.template.context_processors.request` context processor. A sidebar with `collapse="none"` is
always open.

## Leave a sidebar empty

A sidebar whose `.mvpl-panel` is empty takes no space, and its toggles hide. A block left empty is
enough, as long as the block tags touch the panel's tags. Whitespace counts as content:

```html
<div class="mvpl-panel">{% block aside %}{% endblock aside %}</div>
```
