# Right to left

A layout mirrors itself when the page is written right to left. This page covers which sidebar
`left` and `right` name in each direction and how to turn the mirror on.

## What `left` and `right` mean

`left` and `right` name the sidebar at the reading start and the reading end. They are the names
Quasar's `QLayout` uses, so a layout code written for one works in the other.

| Page direction | `left` is drawn at | `right` is drawn at |
|---|---|---|
| Left to right | the left edge | the right edge |
| Right to left | the right edge | the left edge |

The same holds for a sidebar's `side` argument, for the `l` and `r` letters of a
[layout code](layout-code.md), and for `data-mvpl-toggle="left"` on a toggle.

## Turn the mirror on

Set `dir="rtl"` on the `html` element:

1. Put `dir="rtl"` on the `<html>` tag of your base template.
2. Reload the page.

The left sidebar is now at the right, and the header, page and footer follow the same direction.
The stylesheet needs nothing extra: it places everything with logical properties.

A drawer slides in from the side its name gives. Under `dir="rtl"` the left sidebar's drawer comes
from the right edge, at a narrow width as well as a wide one.
