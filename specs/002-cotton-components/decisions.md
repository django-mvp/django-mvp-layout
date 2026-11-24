# Decisions — 002, layouts with Cotton components

Rationale too long for the specification, and every assumption made without asking the repository
owner. The specification stands alone. This file records why it reads the way it does.

## The reading the specification was written from

A developer whose project uses django-cotton writes a layout as `<c-layout view="…">` with its areas
inside, instead of the plain-template tags and blocks. The components are thin: each writes its
attributes with the plain-template feature's tags and adds only markup, so a component layout and a
plain-template layout carry the same attributes and behave the same. Layouts nest by writing
`<c-layout container>` inside a box. The tags, stylesheet, script, base template, every behaviour of
sidebars, drawers and toggles, and right-to-left belong to issue #3. The demonstration pages belong
to issue #5.

## Self-resolved assumptions

**Two stories, both a developer's.** Writing a page layout and laying out a box inside a page are the
two things a developer sets out to do with the components. Every option of every component is a
scenario under the first. A site user's experience (drawers, focus, the remembered state) is the
plain-template feature's, because it comes from the script and stylesheet, not from the components.
So this specification has no site-user story.

**No behaviour restated.** The scenarios check that the components produce the tags' attributes and
compose correctly (nearest-layout toggles, unique ids, empty sidebars not drawn). They do not repeat
how a drawer or a breakpoint behaves. A second statement of the same rule would be a second place to
keep in step.

**No goal id.** `GOALS.md` still holds its placeholder rows and `docs/ROADMAP.md` has no items, so
the specification cites none and says so, rather than inventing a goal. It points at the README's
*Scope & philosophy* instead.

**`tag` on the page area is not validated.** `main` draws `main`, anything else a `div`, as the
prototype does. Sidebar options are validated because a wrong one silently breaks the layout. A wrong
`tag` still draws a working page area.

**A missing script is harmless.** The prototype guards the mount call, and a page that renders a
layout without the script still shows the server-drawn state. Kept as a requirement, because a
page can render before its script loads, or without it in a test.

**Ids are generated per page.** Nested layouts on one page need distinct ids for toggles and
`aria-controls`. The prototype generates them with a tag in the shared tags file, so the requirement
is uniqueness on the page, and the planning notes say where the tag lives.

**django-cotton is required, not optional.** The prototype declares it as a dependency. The plain
templates work without using it, but the components are the package's main way in, and an optional
extra would make `<c-layout>` fail with a missing-template error instead of an install-time one.

**Left and right follow issue #3.** Right-to-left naming is that feature's decision. The components
pass `side` through, so they follow it with no requirement of their own.

## Design review (one round)

**Applied to the plan.** An empty `persist` is none given, a change to the shared sidebar tag the sidebar component cannot do without (Cotton always passes the empty default). The toggle's default names are translated and the English catalogue ships. Documentation is checked against each component's `<c-vars>` names, not only its `@prop` lines. Tests use the existing `render` fixture. The toggle's parity side is FS-001's plain toggles. The sidebar leaves its defaults to the tag. The mount call uses `escapejs`.
**ADR:** none — local to this feature, nothing downstream inherits it

**Carried as watch items.** Classes are compared as sets (trailing spaces). `closed` and `container` are bare attributes, which the components page says. No CSP nonce on the mount script, as in the base template.
**ADR:** none — local to this feature

**SC-001 is restated (approved by the orchestrator, 2026-11-24).** It measured the demonstration pages, which issue 5 owns, so no task here could demonstrate it. It now measures the suite's own layout pages, written as components and covering every layout on the prototype's overview, playground and nested pages, including the settings dialog and filters drawer. `spec.md` carries the new wording.
**ADR:** none — a wording change to one criterion
