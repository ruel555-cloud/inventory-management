---
name: vue-saas-redesign
description: Redesign a Vue 3 application's UI into a modern SaaS-style interface - a vertical navigation sidebar on the left replacing a top nav bar, a concrete design-token system, consistent spacing, and a polished professional look. Use this skill when asked to modernize, restyle, or redesign a Vue 3 app's interface, or to move its navigation into a sidebar.
---

# Vue 3 SaaS Redesign

This skill turns a conventional Vue 3 SPA - top nav bar, hard-coded hex colors,
ad-hoc spacing - into a modern SaaS-style interface built on design tokens.

The end state has three properties:

1. **Navigation is a fixed vertical sidebar on the left**, not a horizontal bar.
2. **Every color, space, radius and shadow comes from a CSS custom property.**
   No literal hex values survive outside the token block.
3. **Spacing is on a single 4px scale.** No arbitrary `padding: 13px`.

## Step 0: Survey before changing anything

Find these four things and write down the file:line of each. Every later step
depends on them.

| What | Typical location | Why it matters |
|---|---|---|
| The app shell | `src/App.vue` template | Holds the nav you are replacing |
| Global stylesheet | Unscoped `<style>` in `App.vue`, or `main.css` | Where tokens get defined |
| The nav links | `<router-link>` list in the shell | Become sidebar items |
| Sticky offsets | Any `position: sticky; top: <header height>` | Breaks when the header goes away |

Check whether the app already uses CSS custom properties. Most do not - they
carry literal hex values in every component. Introducing the token block is
usually the largest and most valuable part of this work.

## The token system

Define this as the **first thing** in the global stylesheet. Everything else in
the redesign references it.

```css
:root {
  /* Surfaces - three depths, light to dark */
  --surface-page: #f8fafc;
  --surface-raised: #ffffff;
  --surface-sunken: #f1f5f9;
  --surface-hover: #f8fafc;

  /* Sidebar gets its own dark surface scale */
  --sidebar-bg: #0f172a;
  --sidebar-item: #94a3b8;
  --sidebar-item-hover: #e2e8f0;
  --sidebar-item-active: #ffffff;
  --sidebar-active-bg: #1e293b;
  --sidebar-border: #1e293b;

  /* Text - four weights of emphasis, never more */
  --text-strong: #0f172a;
  --text-body: #1e293b;
  --text-muted: #64748b;
  --text-subtle: #94a3b8;

  /* Borders */
  --border: #e2e8f0;
  --border-strong: #cbd5e1;
  --border-interactive: #94a3b8;

  /* Accent */
  --accent: #3b82f6;
  --accent-hover: #2563eb;
  --accent-tint: #eff6ff;
  --accent-ring: rgba(59, 130, 246, 0.1);

  /* Semantic - each is text / tint / strong-text */
  --success: #059669;  --success-tint: #d1fae5;  --success-ink: #065f46;
  --warning: #ea580c;  --warning-tint: #fed7aa;  --warning-ink: #92400e;
  --danger:  #dc2626;  --danger-tint:  #fecaca;  --danger-ink:  #991b1b;
  --info:    #2563eb;  --info-tint:    #dbeafe;  --info-ink:    #1e40af;

  /* Spacing - a strict 4px scale. Nothing off-scale is permitted. */
  --space-1: 0.25rem;  /*  4px */
  --space-2: 0.5rem;   /*  8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-5: 1.25rem;  /* 20px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-10: 2.5rem;  /* 40px */
  --space-12: 3rem;    /* 48px */

  /* Type scale */
  --text-xs: 0.75rem;
  --text-sm: 0.813rem;
  --text-base: 0.875rem;
  --text-md: 0.938rem;
  --text-lg: 1.125rem;
  --text-xl: 1.5rem;
  --text-2xl: 1.875rem;
  --text-3xl: 2.25rem;

  --weight-normal: 400;
  --weight-medium: 500;
  --weight-semibold: 600;
  --weight-bold: 700;

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 10px;
  --radius-full: 9999px;

  /* Elevation - keep shadows subtle; SaaS UIs lean on borders, not drop shadows */
  --shadow-sm: 0 1px 2px 0 rgba(15, 23, 42, 0.04);
  --shadow-md: 0 1px 3px 0 rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 4px 12px 0 rgba(15, 23, 42, 0.10);

  /* Sidebar geometry */
  --sidebar-width: 240px;
  --sidebar-width-collapsed: 64px;
  --sidebar-item-height: 40px;
  --sidebar-pad-x: var(--space-3);

  /* Content geometry */
  --content-max: 1600px;
  --content-pad-x: var(--space-8);
  --content-pad-y: var(--space-6);

  --transition: 150ms ease;
}
```

### Rules for the token set

- **Four text weights, no more.** `strong` for headings, `body` for content,
  `muted` for labels, `subtle` for placeholders. A fifth grey always turns out
  to be one of these four.
- **Semantic colors come in threes.** A text color, a background tint, and an
  ink color for text on that tint. Badges need all three.
- **The sidebar has its own surface scale.** A dark sidebar against a light
  content area is the defining SaaS look; do not reuse `--surface-*` for it.
- **Spacing is 4px-based and exhaustive.** If a value is not on the scale,
  change the design rather than adding a token.

## Migrating literal values to tokens

Work file by file, not with a global find-replace - the same hex often means
different things in different places.

```bash
# Find every literal color still in the codebase
grep -rnE '#[0-9a-fA-F]{3,6}' src/ --include=*.vue --include=*.css

# Find off-scale spacing
grep -rnE '(padding|margin|gap): *[0-9]+px' src/
```

Map each hit by **role**, not by value:

```css
/* Before */
.card { background: #ffffff; border: 1px solid #e2e8f0; padding: 1.25rem; }

/* After */
.card {
  background: var(--surface-raised);
  border: 1px solid var(--border);
  padding: var(--space-5);
}
```

Two values that look identical may be different tokens. `#e2e8f0` as a card
border is `--border`; the same hex as a slider track is `--surface-sunken`.

## The sidebar shell

Replace the column layout (`header` above `main`) with a two-column grid.

```css
.app {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  min-height: 100vh;
}

.sidebar {
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  padding: var(--space-6) var(--sidebar-pad-x);
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-nav { display: flex; flex-direction: column; gap: var(--space-1); }

.sidebar-nav a {
  display: flex;
  align-items: center;
  height: var(--sidebar-item-height);
  padding: 0 var(--space-3);
  border-radius: var(--radius-sm);
  color: var(--sidebar-item);
  font-size: var(--text-base);
  font-weight: var(--weight-medium);
  text-decoration: none;
  transition: background var(--transition), color var(--transition);
}

.sidebar-nav a:hover { background: var(--sidebar-active-bg); color: var(--sidebar-item-hover); }
.sidebar-nav a.active { background: var(--sidebar-active-bg); color: var(--sidebar-item-active); }

/* Sidebar footer pins secondary controls to the bottom */
.sidebar-footer { margin-top: auto; display: flex; flex-direction: column; gap: var(--space-2); }
```

### Where the old header's contents go

| Was in the top nav | Goes to |
|---|---|
| Logo / product name | Top of the sidebar, above the nav list |
| Nav links | `.sidebar-nav`, one per row |
| Profile menu | `.sidebar-footer` |
| Language / theme switcher | `.sidebar-footer` |
| Page-level filters | Stay in the content column, above the page content |

Preserve the existing active-link mechanism. If the app binds
`:class="{ active: $route.path === '/x' }"` rather than using
`router-link-active`, keep that - swapping it is a separate change and a
separate risk.

## Content column

```css
.content {
  display: flex;
  flex-direction: column;
  min-width: 0;   /* without this, wide tables force the grid column open */
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max);
  padding: var(--content-pad-y) var(--content-pad-x);
}
```

`min-width: 0` is not optional. A grid column defaults to `min-width: auto`,
so one wide table will push the layout sideways and produce horizontal page
scroll that no amount of `overflow-x` on the table will fix.

## Sticky offsets

Anything previously stuck below a fixed-height header is now wrong. A filter bar
written as `position: sticky; top: 70px` was offset by the header height; with
the header gone it must become `top: 0` inside the content column.

Search for these before declaring the migration done:

```bash
grep -rn "position: *sticky" src/
grep -rn "top: *[0-9]" src/
```

## Polish that does the most work

In rough order of visible effect per line changed:

1. **Consistent card treatment.** One border color, one radius, one padding
   value across every panel. Mismatched cards read as unfinished more than any
   other single thing.
2. **Table density.** Row padding on `--space-3`, a `--surface-sunken` header
   row, `--border` dividers, and a hover state.
3. **Restrained shadows.** `--shadow-sm` on raised surfaces only. Heavy drop
   shadows read as dated.
4. **A single focus ring.** `box-shadow: 0 0 0 3px var(--accent-ring)` on every
   interactive element, applied identically.
5. **Uppercase micro-labels.** `--text-xs`, `--weight-semibold`, letter-spacing
   0.5px, `--text-muted` for stat labels and form labels.

## Reference implementation: this repository

`inventory-management` is a worked example of the starting state this skill
expects. Its specifics:

- Shell and all global CSS live in one unscoped `<style>` block in
  `client/src/App.vue`. There is no `main.css` and `main.js` imports no CSS.
- Seven `<router-link>`s sit in `<nav class="nav-tabs">` inside a 70px-high
  `.top-nav`, pushed right by `margin-left: auto`.
- Active state is manual: `:class="{ active: $route.path === '/orders' }"`.
- **No CSS custom properties exist.** Every color is a literal hex, repeated
  across `App.vue` and roughly a dozen scoped component blocks.
- `FilterBar` is `position: sticky; top: 70px` - exactly the offset that breaks
  when the header is removed.
- Views are Options API with `setup()`; modal components use `<script setup>`.
  Match whichever form the file already uses.
- Existing palette maps cleanly onto the tokens above: `#f8fafc` page,
  `#0f172a` strong text, `#64748b` muted, `#e2e8f0` border, `#3b82f6` accent.

## Constraints

- **Do not change behavior.** This is a presentation change. Router paths,
  component APIs, data fetching and filter logic stay exactly as they are.
- **Respect the project's own rules.** If `CLAUDE.md` mandates delegating `.vue`
  edits to a subagent, or forbids emojis in the UI, those still apply here.
- **Keep i18n intact.** Nav labels usually come from a `t()` call. Moving a link
  into the sidebar must not turn it into a hard-coded string.
- **Scoped styles stay scoped.** Migrate their literals to `var(--…)`; do not
  hoist component styles into the global block.
