# ADR 0002 — Sidebars are named `left` and `right`, and follow the reading direction

**Status:** accepted

## Decision

A sidebar's side is `left` or `right`, and so are the letters `l` and `r` in a layout code. They
name the reading-start side and the reading-end side. In a left-to-right document `left` is drawn at
the left. In a right-to-left document `left` is drawn at the right and its drawer slides in from the
right. The documentation says so wherever a side is named.

## Why

The layout code's letters are Quasar's, so a code written for one works in the other, and Quasar
swaps their meaning in right-to-left documents. Renaming only the `side` option to `start` and `end`
would leave the code's `l` and `r` meaning start and end under a different name, so one name would
mean two sides. Renaming the letters to `s` and `e` would end compatibility with Quasar's codes. The
stylesheet already uses logical properties for everything it draws, so only the public names stay
`left` and `right`.

## Revisit if

The layout code stops following Quasar's letters.
