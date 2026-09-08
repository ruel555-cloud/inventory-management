---
name: vue-reuse-audit
description: Analyze a Vue 3 codebase's component structure for duplication and missed reuse, and report ranked findings with file:line evidence and a suggested extraction. Use when asked to audit, review, or find refactoring opportunities in Vue components, or to identify duplicated logic, repeated markup, or code that belongs in a composable or utility.
---

# Vue Reuse Audit

Produces a **report**, not a refactor. This skill finds duplication and missed
reuse in a Vue 3 codebase and hands back ranked findings with evidence. It does
not edit files. The person reading the report decides what is worth changing -
a reuse refactor typically touches many files at once, and that is a decision to
be made deliberately, not a side effect of running an audit.

## What the report contains

For each finding:

| Field | Content |
|---|---|
| **What** | One sentence naming the duplication |
| **Where** | Every `file:line` involved - all of them, not "and 4 others" |
| **Cost** | What the duplication actually causes: divergence risk, lines carried, bug surface |
| **Extraction** | Where the shared version would live, and its shape |
| **Effort** | Files touched, and whether behavior would change |

Rank by **cost of leaving it**, not by lines saved. Three copies of a
four-line formatter that must agree is worse than one 200-line component that
nothing else depends on.

## Detection passes

Run all six, from the directory holding `src/` (in this repo, `client/`). Each produces candidates; every candidate must be read before it
becomes a finding, because the greps below over-report.

### 1. Duplicated helper functions

The highest-value pass. Identical or near-identical functions defined in more
than one component.

```bash
# Named helpers defined per-file
grep -rn "const [a-z][a-zA-Z]* = (" src/views src/components | \
  sed -E 's/.*const ([a-zA-Z]+) =.*/\1/' | sort | uniq -c | sort -rn | head -20

# Then locate each repeated name
grep -rn "const formatDate" src/
```

A name appearing in 3+ files is almost always a finding. Read the bodies: if
they differ, that *is* the finding - silent divergence is worse than duplication,
because a bug fixed in one copy stays live in the others.

### 2. Repeated component shells

Structural duplication in templates - the same wrapper markup rebuilt per
component.

```bash
grep -rn "modal-overlay\|Teleport\|role=\"dialog\"" src/components
grep -c "" src/components/*.vue | sort -t: -k2 -rn
```

Look for: modal shells, card wrappers, table scaffolds, empty/loading/error
triads. If six components open with the same six lines, the shell is a component
with a `<slot>`.

### 3. Logic that belongs in a composable

Stateful logic repeated across components - fetching, filtering, sorting,
pagination, selection.

```bash
# The same loading/error/data triad rebuilt per view
grep -rn "loading = ref(true)" src/views | wc -l
grep -rn "error.value = 'Failed to" src/views
```

A `loading` / `error` / `data` triad plus a `try/catch/finally` fetch, repeated
in every view, is a `useResource()` composable. Check the existing
`src/composables/` first - the pattern may already exist and simply not be used.

### 4. Composables invoked more than once per component

Calling a composable inside a function body re-runs its setup on every
invocation instead of destructuring once in `setup()`.

```bash
for f in src/views/*.vue src/components/*.vue; do
  n=$(grep -c "useI18n()\|useAuth()\|useFilters()" "$f")
  [ "$n" -gt 1 ] && echo "$f: $n calls"
done
```

Report it as reuse rather than raw speed: the second call means the component
forgot it already had the value, and the two call sites can drift.

### 5. Duplicated constants and data-shape knowledge

The same literal set spelled out in several files - status values, category
names, warehouse lists, colour maps keyed by status.

```bash
grep -rn "'Delivered'\|'Processing'\|'Shipped'" src/ | grep -v locales
grep -rn "=> *{ *return *'#" src/   # colour-by-status maps
```

These drift the moment a value is added on the backend. They belong in one
module the API shape is mirrored in.

### 6. Duplicated styles

The same declarations repeated across scoped blocks, when a global class or a
token already exists.

```bash
grep -rn "border-radius:\|box-shadow:" src/ | \
  sed -E 's/.*(border-radius|box-shadow): *//' | sort | uniq -c | sort -rn | head
```

## What not to flag

Over-reporting makes the audit worthless. Do not raise:

- **Coincidental similarity.** Two functions with the same shape but different
  meanings should stay separate. Shared code couples the callers; that coupling
  has to be paid for by a real shared requirement.
- **Two occurrences of something small.** Two is a coincidence. Extract on the
  third, unless the two must provably agree.
- **Component size on its own.** A 1,200-line component is a smell, not a
  finding. The finding is the specific extractable thing inside it.
- **Anything requiring a behavior change** to unify. Note it as a separate
  observation; it is a redesign, not a reuse fix.
- **Generated or vendored files.**

## Report format

```markdown
## Reuse audit: <N> findings

### 1. `formatDate` reimplemented in 6 components
**Where:** views/Orders.vue:190, views/Dashboard.vue:635, views/Spending.vue:396,
components/ProductDetailModal.vue:115, components/BacklogDetailModal.vue:115,
components/ProfileDetailsModal.vue:88
**Cost:** All six format the same API date strings. Three call `useI18n()`
internally, so locale handling can diverge per copy without a test noticing.
**Extraction:** `src/utils/date.js`, taking `(dateString, locale)`.
**Effort:** 6 files, no behavior change if the bodies are identical - verify
first; if they differ, decide which is correct before unifying.
```

Lead with the finding that costs most. If there are no findings worth acting on,
say so plainly rather than padding the report.

## Reference: findings in this repository

Verified against the current tree; useful as calibration for what a real finding
looks like.

- **`formatDate` defined 6 times** - `views/Orders.vue:190`,
  `views/Dashboard.vue:635`, `views/Spending.vue:396`,
  `components/ProductDetailModal.vue:115`,
  `components/BacklogDetailModal.vue:115`,
  `components/ProfileDetailsModal.vue:88`. `Spending.vue:403` adds a
  `formatDateShort` variant.
- **Six modals share one shell** - `ProductDetailModal`, `CostDetailModal`,
  `TasksModal`, `BacklogDetailModal`, `InventoryDetailModal`,
  `ProfileDetailsModal` all open with the same `Teleport` / `Transition` /
  `.modal-overlay` / `.modal-container` structure at line 4. A `<BaseModal>`
  with a slot would absorb it.
- **`useI18n()` called twice** in `views/Orders.vue` (128, 191),
  `views/Demand.vue` (122, 194) and `views/Dashboard.vue` (315, 637) - the
  second call is inside a formatting function, re-running per call.
- **`translateCategory` defined 3 times** - `views/Inventory.vue:188`,
  `views/Spending.vue:429`, `views/Dashboard.vue:604`.
- **The loading/error/data triad appears in all 7 views** - `Spending`,
  `Inventory`, `Dashboard`, `Backlog`, `Orders`, `Restocking`, `Demand` each
  rebuild `loading = ref(true)` plus a `try/catch/finally` fetch. The clearest
  `useResource()` candidate in the codebase.
- **Currency formatting reimplemented** despite `src/utils/currency.js`
  existing: only `Dashboard.vue` and `Spending.vue` import it, while other views
  build currency strings by hand.
- **Mixed component conventions** - views use the Options API with `setup()`,
  modal components use `<script setup>`. Not a defect, but it means extracted
  code must suit both call styles.

Note the codebase already has `src/composables/` (`useFilters`, `useAuth`,
`useI18n`) and `src/utils/currency.js`. The pattern for shared code exists and
is simply under-used - always check these before proposing a new location.

## Constraints

- **Report only. Change nothing.** No edits, no refactors, no "while I was
  there" fixes. If asked to act on a finding, that is a separate request.
- **Cite exact `file:line` for every occurrence.** A finding without complete
  evidence cannot be evaluated and should not be reported.
- **Read every candidate before reporting it.** The greps above are a net, not
  a verdict.
- **Respect the project's own rules.** Where `CLAUDE.md` or an agent definition
  states a convention, a deviation from it is a finding; a deviation from your
  own preference is not.
