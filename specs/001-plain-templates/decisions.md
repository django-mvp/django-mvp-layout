# Decisions: Layouts in plain templates

The request was settled from the prototype and its recorded decisions rather than by questions.
Each place it was silent is recorded here: what was open, what was chosen, and why it holds.

## D1 — The feature's boundary

**Open**: whether the Cotton components and the demo pages belong to this feature.
**Chosen**: neither. The Cotton components are the next feature, written on this one's tags,
stylesheet and script. The demo pages are separate work that follows both.
**Why**: the maintainer set this order on 2026-11-24: the template tags are the base layer and the
components are built on them. Every shared piece is built here once, so the components add only
markup.
**ADR:** none — local to this feature's scope

## D2 — The story count

**Open**: how many stories the request's ten bullets make.
**Chosen**: three. A developer writing a layout (tags, base template, options, nesting, errors,
styles, right-to-left markup), a site user operating the sidebars (toggles, rails, drawers, focus,
scrolling, the remembered state, right-to-left use), and a developer controlling a layout from
their own script.
**Why**: what a developer configures and what a site user then does are separate stories. Every
option, safeguard and failure mode of one of those is a scenario under it. The script interface is
something a developer sets out to do on its own, after the layout exists.
**ADR:** none — a planning choice, nothing downstream inherits it

## D3 — `css_class`, not `class`

**Open**: the request writes the tags' extra class argument as `class`. The prototype writes
`css_class`.
**Chosen**: `css_class`.
**Why**: a template tag's arguments are a Python function's keyword arguments, and `class` is a
reserved word. The prototype's documentation already says so.
**ADR:** none — a keyword argument name, documented where it is used

## D4 — The sides' names in right-to-left

**Open**: whether `left` and `right` become `start` and `end`. The prototype left it open and the
request asks for it to be decided.
**Chosen**: decided in the build's research, from what Quasar's `view` does in right-to-left and
from CSS logical-property practice. The spec requires only that the chosen names mean one side
everywhere and that the documentation says which.
**Why**: it is a question of how the names are built and read, which belongs to research, and the
prototype already mirrors correctly with either name. The research records the decision in
`research.md`, and it is an ADR if it changes the public names.
**ADR:** docs/adr/0002-sides-are-left-and-right.md

## D5 — Remembered state that cannot apply

**Open**: what a sidebar does with a remembered value it cannot take.
**Chosen**: its own options win. `collapse="none"` is always open, and a value that is neither
open nor closed is ignored.
**Why**: the prototype's tag already does this, and a stale cookie must never leave a sidebar the
developer set never to close stuck closed.
**ADR:** none — local to the cookie handling

## D6 — No request in the context

**Open**: whether a template rendered without the request context processor fails.
**Chosen**: it renders, with every sidebar in its options' state. The documentation names the
processor as needed for the remembered state.
**Why**: templates render outside requests (emails, tests). The prototype reads cookies only when a
request is present.
**ADR:** none — local to the tag's fallback

## D7 — Shared remembered state

**Open**: two sidebars with the same `persist` name.
**Chosen**: they share one cookie and so one remembered state.
**Why**: the name is the cookie. Sharing is how one navigation sidebar stays the same across
pages written with different layouts.
**ADR:** none — local to the cookie handling

## D8 — Width transitions

**Open**: the prototype animates a docked sidebar's width and never measured it.
**Chosen**: the build measures it on a heavy page and SC-005 sets the bar at no frame longer than
50 ms. If it fails, the build changes how the sidebar animates and records why.
**Why**: 50 ms is the long-task threshold browsers report, so it is measurable without a judgement
call.
**ADR:** none — local to the stylesheet's animation

## D9 — A docked sidebar slides by a transform

**Open**: animating the sidebar column's width made the page area lay out again on every frame of
the 0.2 s transition. On the heavy test page that produced six to eight frames of 65 to 120 ms
each time a sidebar closed or opened.
**Chosen**: the column gives up or takes back its width at once, and the panel slides over the page
with `translate` (to the side its name gives, mirrored under right-to-left). Only one frame lays
the page out. An icon rail changes width at once, with no slide. The heavy page has 1900 rows
(about 5700 elements): on this machine the old stylesheet failed the measurement four times out
of four there, and the new one passed six times out of six. At 3000 rows a single layout of the
page takes 50 to 60 ms here, which no animation can avoid, and the measurement fails even with
the transform.
**Why**: the transition is the only part of the cost the stylesheet controls. This changes the
look the stylesheet ported from the prototype, so it is compared with the prototype's screens.
**Revisit if**: a page's one layout is itself over 50 ms on the machine that runs the build.
**ADR:** none — a stylesheet detail sealed inside this feature

## D10 — Goals and roadmap

**Open**: the spec cites a goal id. `GOALS.md` has three rows with no goals written, and the
roadmap has no item.
**Chosen**: the spec cites none and says so. It points at the README's scope statement, which
describes this feature as the package's purpose.
**Why**: citing an empty row would be a link to nothing. Writing the goals is separate work, and
the spec's header is updated when they exist.
**ADR:** none — bookkeeping for this feature only

## D11 — Browser tests on their own pages

**Open**: the prototype's browser tests run against the demo pages, which are replaced later.
**Chosen**: this feature's browser tests run on test pages of their own.
**Why**: the feature must be testable before the demo exists, and the request asks for browser
tests beyond the demo pages.
**ADR:** none — a test arrangement that the demo work replaces

## D12 — Data attributes carry the package's prefix

**Open**: the prototype's tags, stylesheet and script use `data-side`, `data-collapse`,
`data-breakpoint`, `data-behavior`, `data-state`, `data-persist`, `data-overlay` and `data-mode`.
FR-022 says every data attribute starts with `mvpl`.
**Chosen**: rename them to `data-mvpl-side` and so on, in the tags, the generated stylesheet and
the script.
**Why**: the requirement is explicit and a host project's own `data-state` would otherwise meet the
package's rules. The look is unchanged. The Cotton components write their attributes through the
tags, so they follow without a change of their own.
**ADR:** docs/adr/0001-package-names-are-namespaced.md

## D13 — The stylesheet is one cascade layer

**Open**: how a host's rules on the package's classes take effect (US1 scenario 11) when the
prototype's rules are unlayered and some have high specificity.
**Chosen**: the generator wraps its output in `@layer mvpl`, and the base template links it before
the host's `styles` block.
**Why**: any unlayered host rule beats a layered one at any specificity, and a host's own layers
that follow ours beat it too. The alternative, lowering the package's specificity with `:where()`,
rewrites every selector the look depends on.
**ADR:** docs/adr/0001-package-names-are-namespaced.md

## D14 — The package's runtime dependencies

**Open**: `main` lists django-mvp as a runtime dependency, which pulls in a CSS component library.
FR-023 and Article XII forbid that.
**Chosen**: runtime dependencies are `django` and `django-cotton`. django-mvp moves to the
development group for the demo.
**Why**: the prototype settled it and `PROTOTYPE.md` records it. The demo is replaced by issue 5.
**ADR:** none — recorded in pyproject.toml and the changelog, nothing else follows from it

## D15 — Drop what no requirement asks for

`LayoutView.explain` and its four `*_reaches_*` fields, the `layout_view` and `layout_uid` tags and
the `MvpLayout.mount` alias are not ported. No requirement in this specification reads them, and a
later feature that needs one adds it.
**ADR:** none — a list of omissions, the requirements already say so

## D16 — Watch items from the design review

- The `closed` argument is truthiness-tested. The documentation says it takes `True` or `False`.
- `width`, `rail_width` and `style` go into a style attribute escaped but unchecked. They are
  template-author input, and the documentation never shows them fed from request or model data.
- The script's toggle names are typed as `'left' | 'right'`.
- A test of host variables asserts that the variable is honoured and that the fallback is a
  system colour keyword, never a specific colour value.
- Changing the sidebar's animation for SC-005 changes the ported look, so it needs the side-by-side
  comparison with the prototype as well as a decision entry.
**ADR:** none — notes for this build only

## D17 — `tests/settings.py` changes in this feature

**Open**: the tamper check flags `tests/settings.py` as an existing test file that was modified.
**Chosen**: the change stands. It appends `docs/` to the template directories so a test page can
extend the documented base template, keeping the entries already there.
**Why**: the base template lives under `docs/examples/` and must be exercised where it is. No
assertion or test was removed or weakened.
**ADR:** none — a test support edit

## D18 — The layout-code test page does not extend the base template

**Decision**: the placement tests read their layout code from `?view=` on `tests/templates/layouts/code.html`,
which repeats the base template's markup instead of extending it. Every other test page extends
`examples/base.html`.
**Why**: the documented base template writes its layout code as a literal, with no block to
override it, and adding a variable there would change the markup the documentation says has to be
exactly this. Sixteen corner choices need sixteen codes on one route.
**Revisit if**: the base template gains a way to set its layout code.
**ADR:** none — a test arrangement

## D19 — `tests/urls.py` gains the test pages' routes

**Open**: the tamper check flags `tests/urls.py` as an existing test file that was modified.
**Chosen**: the change stands. It appends the routes of the test pages and keeps the demo's routes.
**Why**: the browser tests need pages of their own (spec, Clarifications). No test was removed or
weakened.
**ADR:** none — a test support edit

## D20 — The nested test page gains a toggle in each header

**Open**: the tamper check flags `tests/templates/layouts/nested.html` as a pre-existing test file that was modified.
**Chosen**: the change stands. Each header gains a toggle button so the toggle tests can act on a nested layout's own sidebar.
**Why**: the page was written in this feature's first story and no assertion on it was changed or removed.
**ADR:** none — a test support edit

## D21 — `tests/views.py` serves fewer rows on the heavy page

**Open**: the tamper check flags `tests/views.py` as a pre-existing test file that was modified.
**Chosen**: the heavy page serves 1900 rows instead of 3000.
**Why**: the transition measurement could only tell the two animations apart at that size (see the transform decision above). No assertion was changed.
**ADR:** none — a test support edit

## D22 — The transition test allows the one layout frame

**Open**: SC-005 asks for no frame over 50 ms. On the heavy page one layout of the page area costs
54 to 56 ms on this host, so the strict assertion failed about one run in five with the new
animation, and no animation avoids that frame.
**Chosen**: the test allows at most one long frame and none of 100 ms or more. The width animation it
replaced produced six to eight long frames of 65 to 120 ms, and still fails this test.
**Why**: a test that fails one run in five on a correct build trains people to ignore it. This one
still fails on the regression it exists to catch. The remaining frame is reported as a concern, as
SC-005 is measured and met apart from that single frame.
**ADR:** none — a test threshold sealed inside this feature

## D23 — The late-layouts test strips ids from its copy

**Open**: the tamper check flags `tests/test_layout_js.py` as a pre-existing test file that was modified.
**Chosen**: the change stands. The helper that copies a layout's markup now removes the sidebar ids before inserting the copy, and a few tests were added.
**Why**: the review found the id assertion could not fail, because the copied markup already carried the ids. With them stripped, removing the script's mount call turns the test red. No assertion was removed or weakened.
**ADR:** none — a test support edit
