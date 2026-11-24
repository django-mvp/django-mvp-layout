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

### Changed

- django-mvp is no longer a runtime dependency, and django-cotton (2.9 or later) is. A project
  that relied on this package to install django-mvp must now depend on it directly.
