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

- The stylesheet now opens with `@layer base, mvpl;`, so a host's `base` layer, where Tailwind's
  preflight goes, sorts below the package's layer. Before, that reset removed the sidebar borders in
  a Tailwind project. Layers a host declares after the package's stylesheet still sort above it.
- A sidebar tag given an empty `persist` now means none was given, where it used to raise.
- django-mvp is no longer a runtime dependency, and django-cotton (2.9 or later) is. A project
  that relied on this package to install django-mvp must now depend on it directly.

### Removed

- The starter component `<c-mvp_layout.example>` that the package template shipped. The components
  of this package are `<c-layout>` and the areas inside it.
