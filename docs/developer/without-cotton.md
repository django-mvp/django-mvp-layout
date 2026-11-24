# Without django-cotton

The components are a thin layer over two template tags and a fixed set of class names. A project
that doesn't use django-cotton writes the same markup itself, in a plain base template that its
pages extend with ordinary blocks.

## A base template to copy

[`docs/examples/base.html`](https://github.com/django-mvp/django-mvp-layout/blob/main/docs/examples/base.html)
is a complete base template. Copy it into your project's `templates/`, change the layout code and
the sidebars' options, and extend it:

```html
{% extends "base.html" %}

{% block header %}
  <button type="button" class="mvpl-toggle" data-mvpl-toggle="left" data-mvpl-when="closed" aria-label="Navigation">☰</button>
  My project
{% endblock header %}

{% block navigation %}<nav>…</nav>{% endblock navigation %}

{% block content %}
  <h1>Hello</h1>
{% endblock content %}
```

Its blocks are `title`, `styles`, `header`, `navigation`, `content`, `aside` and `footer`. The demo
project's Without Cotton page extends this same file, so it is tested with every change.

django-cotton still has to be installed, because the package depends on it, but this template never
uses it.

## The markup

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

## `{% layout_attrs %}`

```
{% layout_attrs view container css_class style %}
```

Every argument is optional and can be given by name. It writes `class="mvpl …"`, the layout's
`data-mvpl-*` attributes and a `style` with its grid areas. `container=True` is the components'
`container`. Don't add another `class` or `style` attribute to the element, because the browser
keeps only the first: pass them as `css_class` and `style` instead.

## `{% sidebar_attrs %}`

```
{% sidebar_attrs side collapse breakpoint behavior persist closed width rail_width css_class %}
```

The arguments are those of `<c-layout.sidebar>`, with `rail-width` written `rail_width` and `class`
written `css_class`. An option that is not one of its choices raises.

The tag reads the remembered state from `request`, so the template needs the
`django.template.context_processors.request` context processor.

## An empty sidebar

A sidebar whose `.mvpl-panel` is empty takes no space, and its toggles hide. A block left empty is
enough, as long as the block tags touch the panel's tags. Whitespace counts as content:

```html
<div class="mvpl-panel">{% block aside %}{% endblock aside %}</div>
```

## Toggles

A toggle is any element with `data-mvpl-toggle="left"` or `"right"`. The script gives it
`aria-expanded` and `aria-controls`, and hides it when its sidebar is absent or cannot close.
`data-mvpl-when` and `data-mvpl-layout` work as they do on `<c-layout.toggle>`; see
[Using the components](cotton.md#c-layouttoggle).
