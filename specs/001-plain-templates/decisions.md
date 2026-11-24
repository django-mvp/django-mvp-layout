# Decisions: Layouts in plain templates

The request was settled from the prototype and its recorded decisions rather than by questions.
Each place it was silent is recorded here: what was open, what was chosen, and why it holds.

## The feature's boundary

**Open**: whether the Cotton components and the demo pages belong to this feature.
**Chosen**: neither. The Cotton components are the next feature, written on this one's tags,
stylesheet and script. The demo pages are separate work that follows both.
**Why**: the maintainer set this order on 2026-11-24: the template tags are the base layer and the
components are built on them. Every shared piece is built here once, so the components add only
markup.

## The story count

**Open**: how many stories the request's ten bullets make.
**Chosen**: three. A developer writing a layout (tags, base template, options, nesting, errors,
styles, right-to-left markup), a site user operating the sidebars (toggles, rails, drawers, focus,
scrolling, the remembered state, right-to-left use), and a developer controlling a layout from
their own script.
**Why**: what a developer configures and what a site user then does are separate stories. Every
option, safeguard and failure mode of one of those is a scenario under it. The script interface is
something a developer sets out to do on its own, after the layout exists.

## `css_class`, not `class`

**Open**: the request writes the tags' extra class argument as `class`. The prototype writes
`css_class`.
**Chosen**: `css_class`.
**Why**: a template tag's arguments are a Python function's keyword arguments, and `class` is a
reserved word. The prototype's documentation already says so.

## The sides' names in right-to-left

**Open**: whether `left` and `right` become `start` and `end`. The prototype left it open and the
request asks for it to be decided.
**Chosen**: decided in the build's research, from what Quasar's `view` does in right-to-left and
from CSS logical-property practice. The spec requires only that the chosen names mean one side
everywhere and that the documentation says which.
**Why**: it is a question of how the names are built and read, which belongs to research, and the
prototype already mirrors correctly with either name. The research records the decision in
`research.md`, and it is an ADR if it changes the public names.

## Remembered state that cannot apply

**Open**: what a sidebar does with a remembered value it cannot take.
**Chosen**: its own options win. `collapse="none"` is always open, and a value that is neither
open nor closed is ignored.
**Why**: the prototype's tag already does this, and a stale cookie must never leave a sidebar the
developer set never to close stuck closed.

## No request in the context

**Open**: whether a template rendered without the request context processor fails.
**Chosen**: it renders, with every sidebar in its options' state. The documentation names the
processor as needed for the remembered state.
**Why**: templates render outside requests (emails, tests). The prototype reads cookies only when a
request is present.

## Shared remembered state

**Open**: two sidebars with the same `persist` name.
**Chosen**: they share one cookie and so one remembered state.
**Why**: the name is the cookie. Sharing is how one navigation sidebar stays the same across
pages written with different layouts.

## Width transitions

**Open**: the prototype animates a docked sidebar's width and never measured it.
**Chosen**: the build measures it on a heavy page and SC-005 sets the bar at no frame longer than
50 ms. If it fails, the build changes how the sidebar animates and records why.
**Why**: 50 ms is the long-task threshold browsers report, so it is measurable without a judgement
call.

## Goals and roadmap

**Open**: the spec cites a goal id. `GOALS.md` has three rows with no goals written, and the
roadmap has no item.
**Chosen**: the spec cites none and says so. It points at the README's scope statement, which
describes this feature as the package's purpose.
**Why**: citing an empty row would be a link to nothing. Writing the goals is separate work, and
the spec's header is updated when they exist.

## Browser tests on their own pages

**Open**: the prototype's browser tests run against the demo pages, which are replaced later.
**Chosen**: this feature's browser tests run on test pages of their own.
**Why**: the feature must be testable before the demo exists, and the request asks for browser
tests beyond the demo pages.

## Data attributes carry the package's prefix

**Open**: the prototype's tags, stylesheet and script use `data-side`, `data-collapse`,
`data-breakpoint`, `data-behavior`, `data-state`, `data-persist`, `data-overlay` and `data-mode`.
FR-022 says every data attribute starts with `mvpl`.
**Chosen**: rename them to `data-mvpl-side` and so on, in the tags, the generated stylesheet and
the script.
**Why**: the requirement is explicit and a host project's own `data-state` would otherwise meet the
package's rules. The look is unchanged. The Cotton components write their attributes through the
tags, so they follow without a change of their own.

## The stylesheet is one cascade layer

**Open**: how a host's rules on the package's classes take effect (US1 scenario 11) when the
prototype's rules are unlayered and some have high specificity.
**Chosen**: the generator wraps its output in `@layer mvpl`, and the base template links it before
the host's `styles` block.
**Why**: any unlayered host rule beats a layered one at any specificity, and a host's own layers
that follow ours beat it too. The alternative, lowering the package's specificity with `:where()`,
rewrites every selector the look depends on.

## The package's runtime dependencies

**Open**: `main` lists django-mvp as a runtime dependency, which pulls in a CSS component library.
FR-023 and Article XII forbid that.
**Chosen**: runtime dependencies are `django` and `django-cotton`. django-mvp moves to the
development group for the demo.
**Why**: the prototype settled it and `PROTOTYPE.md` records it. The demo is replaced by issue 5.

## Drop what no requirement asks for

`LayoutView.explain` and its four `*_reaches_*` fields, the `layout_view` and `layout_uid` tags and
the `MvpLayout.mount` alias are not ported. No requirement in this specification reads them, and a
later feature that needs one adds it.

## Watch items from the design review

- The `closed` argument is truthiness-tested. The documentation says it takes `True` or `False`.
- `width`, `rail_width` and `style` go into a style attribute escaped but unchecked. They are
  template-author input, and the documentation never shows them fed from request or model data.
- The script's toggle names are typed as `'left' | 'right'`.
- A test of host variables asserts that the variable is honoured and that the fallback is a
  system colour keyword, never a specific colour value.
- Changing the sidebar's animation for SC-005 changes the ported look, so it needs the side-by-side
  comparison with the prototype as well as a decision entry.
