# Research — 002, layouts with Cotton components

## Assumptions checked

- **django-cotton resolves `<c-layout>` to `cotton/layout/index.html`.** The installed django-cotton
  is 2.9.0, and its loader tries `<name>.html` and then `<name>/index.html`. Holds.
- **The agreed components render.** On the prototype's demo (http://devserver:8066/), the overview,
  /playground/, /nested/ and /without-cotton/ pages all return 200. /nested/ draws six layouts, each
  followed by its own mount call, with seven sidebars and eleven toggles. Holds.
- **The tags the components call exist on `main`.** They do not yet: `main` still carries the package
  template's sample component and no layout tags. They arrive with issue #3, which this feature
  depends on and is built after. Recorded as the dependency, not a defect.
- **The package declares django-cotton.** `main`'s `pyproject.toml` depends on `django-mvp`, which
  brings django-cotton with it, but does not declare django-cotton itself. The prototype declares it
  and drops `django-mvp`. Recorded in the planning notes for the build to settle against what issue #3
  leaves.
