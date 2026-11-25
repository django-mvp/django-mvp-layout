# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
  Everything not yet released goes under [Unreleased], grouped by change type:
  Added, Changed, Deprecated, Removed, Fixed, Security. Prepare Release promotes
  that section to a version heading and dates it.

  Do NOT write a version heading by hand. Tag Release fires on any push to main
  that touches pyproject.toml, and the only thing stopping it cutting a release
  from that push is the absence of a `## [X.Y.Z]` section matching the version
  in pyproject.toml. Writing one here defeats that guard, and the repository
  ends up with a tag and a GitHub Release for a version nobody prepared.

  Write for someone deciding whether to upgrade. Say what changed for them and
  what they have to do about it, not which files moved.
-->

## [Unreleased]

### Added

- A sidebar can stack its content as a header, a body and a footer. Give `<c-layout.sidebar>` a
  `view` of `hbf`, `Hbf`, `hbF` or `HbF` and put the content in `<c-layout.header>`, the new
  `<c-layout.body>` and `<c-layout.footer>`. An upper-case letter makes that part sticky while the
  sidebar scrolls. In a plain template, add the same class to the sidebar's `.mvpl-panel` and give
  its children `mvpl-header`, `mvpl-body` and `mvpl-footer`.

## [v0.1.2] - 2026-11-24

### Fixed

- A sidebar on a fixed side of a layout with `container`, such as the right sidebar of `hHh LpR fFf`,
  opened as a drawer that stopped short of the bottom of the layout by the header's height. It now
  runs the layout's full height.

## [v0.1.1] - 2026-11-24

### Fixed

- A layout with `container` no longer collapses to nothing when it is given no height. It is as tall
  as its content, like any card, and its fixed sidebars fill their rows instead of reaching the
  window's height. A height works as before.
- A layout with `container` and a max-height grows with its content up to the limit, then scrolls
  inside it. A box that caps its own height, such as a dialog, caps a layout inside it once the box
  is a flex column.

## [v0.1.0] - 2026-11-24

### Added

- The package, generated and not yet doing anything.
- Layouts for any Django project, written in a plain template: the `{% layout_attrs %}` and
  `{% sidebar_attrs %}` tags, one stylesheet (`mvp_layout/layout.css`) and one script
  (`mvp_layout/layout.js`) with no build step. The script exposes `MvpLayout` to mount a layout,
  read and change its sidebars and listen for `mvpl:change`.
- Layouts written as Cotton components: `<c-layout>`, `<c-layout.header>`, `<c-layout.page>`,
  `<c-layout.footer>`, `<c-layout.sidebar>` and `<c-layout.toggle>`. They write the same attributes as
  the tags, so a component layout and a plain-template layout behave the same, and a layout nests
  inside another with `container`. Each layout and sidebar without an `id` gets a generated one
  (`{% layout_uid %}`). The toggle's default accessible names are translatable, and the package ships
  its English catalogue.

### Changed

- `mvpl:change` now fires only when a layout's state changes. A resize that changed nothing, or the
  script's own first measurement after a listener was added, no longer sends an event.
- The stylesheet now opens with `@layer base, mvpl;`, so a host's `base` layer, where Tailwind's
  preflight goes, sorts below the package's layer. Before, that reset removed the sidebar borders in
  a Tailwind project. Layers a host declares after the package's stylesheet still sort above it.
- A sidebar tag given an empty `persist` now means none was given, where it used to raise.
- django-mvp is no longer a runtime dependency, and django-cotton (2.9 or later) is. A project
  that relied on this package to install django-mvp must now depend on it directly.

### Removed

- The starter component `<c-mvp_layout.example>` that the package template shipped. The components
  of this package are `<c-layout>` and the areas inside it.
