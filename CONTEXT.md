# django-mvp-layout

The vocabulary of django-mvp-layout, which arranges page layouts by a nine-letter layout code.

The terms below are the ones to use in issues, commits and tests.

## Core concepts

**Host project**:
The Django project that installs this package. It owns the theme, the base
template, the data, and the URLs. This package renders into it and decides none
of those.
_Avoid_: consumer, client, downstream, user (a user is a person using the host
project, not the project itself).

**Component**:
A Cotton template this package ships, placed on a page with a tag. The tag name
is the file path, so renaming the file changes the public API.
_Avoid_: widget, partial, include, block.

**Layout code**:
The nine letters, in three groups, that arrange a layout, such as
`lHh LpR lff`. Passed as `view`, the name Quasar uses.
_Avoid_: layout string, template, preset.

**Area**:
One of the five parts a layout code places: header, left sidebar, page, right
sidebar, footer.
_Avoid_: region, slot (Cotton has slots, and the areas are not them).

**Page**:
The area between the sidebars. Not the whole HTML document.
_Avoid_: content, main (that is one element it can draw).

**Fixed**:
An area whose letter is upper case, held in place while the layout scrolls.
_Avoid_: pinned.

**Stacked sidebar**:
A sidebar whose panel lays its content out as a header, a body and a footer,
by one of `hbf`, `Hbf`, `hbF` and `HbF`. An upper-case letter makes that part
sticky while the sidebar scrolls.

**Drawer**:
A sidebar drawn over the page as a modal dialog, below its breakpoint or with
`behavior="overlay"`.
_Avoid_: overlay sidebar, off-canvas (offcanvas is a collapse style, not this).

**Icon rail**:
A sidebar closed to the width of its icons, with `collapse="icons"`.
_Avoid_: mini sidebar, collapsed sidebar.

**Contained layout**:
A layout with `container`, which fills the box it is placed in and scrolls
inside it.
_Avoid_: embedded layout, inner layout (an inner layout is any nested one).

## Terms deliberately not used

- **Shell**: implies an application frame with navigation and a brand. This
  package arranges areas and draws nothing inside them.
- **Responsive breakpoint**: implies the window's width. A sidebar's
  breakpoint is the layout's own width.
