# Installation

```bash
pip install django-mvp-layout
```

Add the app to `INSTALLED_APPS`, with [django-cotton](https://django-cotton.com) if you use the
components:

```python
INSTALLED_APPS = [
    # ...
    "django_cotton",
    "mvp_layout",
]
```

Load the stylesheet and the script in the base template's head, without `defer`, so a sidebar is
drawn in its remembered state before the page paints:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'mvp_layout/layout.css' %}" />
<script src="{% static 'mvp_layout/layout.js' %}"></script>
```

Then lay out the page with [the components](cotton.md), or with the template tags in
[a plain base template](without-cotton.md).
