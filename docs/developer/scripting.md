# Scripting a layout

The layout's script exposes one global, `MvpLayout`, so a script of your own can mount a layout,
read and change its sidebars and listen for changes. This page covers each function, the object
`state` returns, the `mvpl:change` event and how a layout added after the page loads is mounted.

Every function takes a layout, given as its element or as its id. A side is `"left"` or `"right"`.
They name the reading-start and reading-end sides, so under `dir="rtl"` the `"left"` sidebar is
drawn at the right.

## Change a sidebar from a script

1. Load the script in the head, without `defer`, as the base template does.
2. Open a sidebar:

   ```js
   MvpLayout.open("app", "left");
   ```

3. Close it again:

   ```js
   MvpLayout.close("app", "left");
   ```

`open` and `close` do what the sidebar's own toggle does. A sidebar beside the page is opened or
closed, and the new state is remembered when the sidebar has a `persist` name. A drawer is shown or
hidden, and focus moves into it or returns to the element that had it. A call that would change
nothing, such as opening a sidebar that is already showing, does nothing.

## Read a layout's state

Call `MvpLayout.state` to learn which sidebars a layout has and whether each is showing:

```js
const sidebars = MvpLayout.state("app");
if (sidebars.left.present && sidebars.left.visible) {
  // The left sidebar is on screen, beside the page or as a drawer.
}
```

It returns an object with a `left` and a `right` entry. The entry for a side with no sidebar is
`{ present: false }`. The entry for a sidebar has these keys:

| Key | Value |
|---|---|
| `present` | `true`. |
| `mode` | `"docked"` when the sidebar is beside the page, `"overlay"` when it is a drawer. The stylesheet decides, from the layout's width. |
| `state` | `"open"` or `"closed"`, the state of a sidebar beside the page. |
| `collapse` | The sidebar's `collapse` option: `"offcanvas"`, `"icons"` or `"none"`. |
| `rail` | `true` when the sidebar is closed to its icon rail. |
| `visible` | `true` when the sidebar is showing: open beside the page, a drawer that is open, or a sidebar that never closes. |

A sidebar whose panel is empty is not present.

## Reference

### `MvpLayout(layout)`

Mounts the layout and returns its element. Mounting a layout that is already mounted changes
nothing: it adds no second observer and keeps its state, and the layout reports its state once, as
every call to `sync` does.

```js
const app = MvpLayout("app");
MvpLayout(app) === app; // true
```

### `MvpLayout.sync(layout)`

Brings the layout's toggles and sidebars in line with its markup, then reports the state. Call it
after your script changes what a layout holds, such as adding a toggle or marking a sidebar closed.
The script calls it itself on every change it makes and whenever the layout is resized.

### `MvpLayout.state(layout)`

Returns the object described in [Read a layout's state](#read-a-layouts-state).

### `MvpLayout.toggle(layout, side)`

Closes a showing sidebar and opens a closed one, as its toggle does.

### `MvpLayout.open(layout, side)`

Shows the sidebar, whatever its mode. It does nothing for a sidebar that is showing.

### `MvpLayout.close(layout, side)`

Hides the sidebar. It does nothing for a sidebar that is hidden, and for a sidebar beside the page
that never closes (`collapse="none"`).

### An id that names no layout

Every function throws an `Error` when the id matches no layout, or matches an element that is not
one. The message names the id:

```js
try {
  MvpLayout.open("missing", "left");
} catch (error) {
  console.error(error.message); // MvpLayout: no layout has the id "missing"
}
```

## Listen for changes

The layout dispatches `mvpl:change` on its own element each time its state changes. The event
bubbles and its `detail` is the object `MvpLayout.state` returns, so a listener on the layout or on
`document` is enough:

```js
document.getElementById("app").addEventListener("mvpl:change", (event) => {
  console.log(event.detail.left.visible);
});
```

The event fires when:

- a sidebar is opened or closed, by a toggle, the keyboard or a function above,
- a sidebar changes between beside the page and a drawer, such as when the window is resized across
  its breakpoint,
- the layout is mounted or synced.

One change can fire the event more than once, so a listener should read `detail` and not count
events.

## Mount a layout added later

A layout inserted after the page loads is mounted without a call from you, whether the insertion
runs scripts or not. Both of these mount it:

```js
// Markup only, as htmx and innerHTML insert it.
container.insertAdjacentHTML("beforeend", html);

// Markup and a script that mounts it.
const script = document.createElement("script");
script.textContent = 'MvpLayout("late")';
container.append(script);
```

The script observes the document for added layouts, so the insertion in the first example is
enough. The sidebars of a late layout are given ids, its toggles work, and it reports `mvpl:change`
as any other layout does.

## Check your script's types

`layout.js` carries JSDoc types for the whole interface and is type-checked by the repository's own
checks. A TypeScript project can check its calls against them by including the script in its
`tsconfig.json`.
