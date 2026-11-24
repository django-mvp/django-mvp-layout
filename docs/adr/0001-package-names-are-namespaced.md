# ADR 0001 — The package's attributes and styles are namespaced

**Status:** accepted

## Decision

Every data attribute the package writes or reads starts with `data-mvpl-`, and every class,
variable and cookie starts with `mvpl`. The generated stylesheet is one cascade layer, `@layer mvpl`,
and the base template links it before the host's own styles block. A host project's rule on a
package class therefore wins without raising its specificity.

## Why

A host page shares its attribute and class names with the package. An unprefixed `data-state` or
`data-side` can meet the package's rules, and unlayered package rules with high specificity beat a
host's single-class rule. A layer loses to any unlayered host rule at any specificity, which is what
a host expects. Lowering the package's specificity with `:where()` would rewrite every selector the
look depends on.

The Cotton components and every host template write these names, so they are public API from the
first release and cheap to set now and costly to rename later.

## Revisit if

Browsers the package supports stop handling `@layer`, or a host needs the package to win over its
own unlayered rules.
