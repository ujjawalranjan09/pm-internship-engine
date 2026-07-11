# Design Plan — PM Internship Allocation Engine

**Product:** Government internship allocation engine (admin/employer/candidate portals)
**Audience:** Civil servants, HR professionals, students — high-trust, high-data-density context
**Goal:** One cohesive visual system with three role-specific identities that feels authoritative, not templated

---

## 1. Color System — Role-Coded Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--navy-900` | `#0a1428` | Primary text, admin brand |
| `--navy-600` | `#1a2f4a` | Primary actions, admin sidebar active |
| `--navy-500` | `#1e3a5f` | Borders, focus rings, admin accent |
| `--saffron-500` | `#f97316` | Employer brand, warnings, CTAs |
| `--saffron-600` | `#ea580c` | Employer hover, active states |
| `--emerald-500` | `#10b981` | Candidate brand, success, "matched" state |
| `--emerald-600` | `#059669` | Candidate hover |
| `--slate-50` | `#f8fafc` | Page background (all roles) |
| `--slate-100` | `#f1f5f9` | Card backgrounds, subtle separation |
| `--slate-900` | `#0f172a` | Body text |
| `--amber-500` | `#f59e0b` | Pending/warning (shared) |
| `--red-500` | `#ef4444` | Error/destructive (shared) |

**Role Identity Assignment:**
- **Admin** → Navy (`--navy-600` primary, `--navy-50` surfaces)
- **Employer** → Saffron (`--saffron-500` primary, `--saffron-50` surfaces)
- **Candidate** → Emerald (`--emerald-500` primary, `--emerald-50` surfaces)

Each role gets its own 50/100/500/600 scale derived from the base token — not just recolored buttons. Sidebar, header accent, stats card icon bg, empty-state icon bg, and focus rings all shift per role.

---

## 2. Typography — Distinctive Pairing

| Role | Display | Body | Data/Mono |
|------|---------|------|-----------|
| **All** | **Space Grotesk** (variable, 300–700) — geometric, technical, government-credible | **DM Sans** (variable, 400–600) — neutral, readable at small sizes | **JetBrains Mono** — numbers, IDs, code, timestamps |

**Type Scale (rem, clamp for fluidity):**
- `--text-display`: `clamp(1.75rem, 2vw + 1rem, 2.5rem)` / 700 / -0.02em
- `--text-h1`: `clamp(1.5rem, 1.5vw + 1rem, 2rem)` / 600 / -0.01em
- `--text-h2`: `1.25rem` / 600
- `--text-h3`: `1.125rem` / 600
- `--text-base`: `0.9375rem` / 400 (15px — slightly larger than 14px default for data density)
- `--text-sm`: `0.8125rem` / 400 (13px)
- `--text-xs`: `0.75rem` / 400 (12px)
- `--text-data`: `0.8125rem` / 500 / JetBrains Mono — for counts, currency, dates

**Why this pair:** Space Grotesk has character in its numerals and caps (distinctive "3", "5", "G") without being decorative. DM Sans disappears at body size — exactly what dense tables need. JetBrains Mono keeps columns aligned.

---

## 3. Layout System

**Spacing Scale (rem):** `0.25 | 0.5 | 0.75 | 1 | 1.5 | 2 | 3 | 4 | 6 | 8`
- All padding/margin/gap values drawn from this scale — no arbitrary px.
- `--space-unit`: `0.25rem` (4px base)

**Container Widths:**
- `--container-sm`: `640px` (forms, modals)
- `--container-md`: `1024px` (most pages)
- `--container-lg`: `1280px` (wide tables)
- `--container-full`: `100%` (full-bleed dashboards)

**Sidebar:** Fixed 260px (16.25rem) — wider than current 256px for longer labels.
**Header:** 64px (4rem) — consistent across roles.
**Content Max-Width:** `1280px` with `1.5rem` side padding on desktop, `1rem` mobile.

**Grid:** 12-column with `1.5rem` gutters. Cards use `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 xl:max-col-span-1` pattern for stats grids.

---

## 4. Signature Element — "Allocation Pulse"

**The one thing this page is remembered by:** A subtle, data-driven ambient indicator in the admin header that reflects *system health in real time*.

- **Visual:** 8px diameter dot in the header, right of the logo, with a 24px glow ring
- **States:**
  - **Idle (no active cycles):** Steady navy pulse — `animation: pulse-navy 3s ease-in-out infinite`
  - **Running allocation:** Rotating saffron arc (conic-gradient spinner) — `animation: spin 1s linear infinite`
  - **Just completed:** Emerald ripple expanding outward — `animation: ripple-emerald 1.5s ease-out`
  - **Error/attention needed:** Steady red — no animation

- **Data source:** Polls `/admin/analytics/overview` every 30s (TanStack Query). Shows `pendingAllocations > 0` → running, `lastCycleStatus === "completed"` → ripple, `lastCycleStatus === "failed"` → red.

**Why it works:** Government dashboards are often static. This makes the *engine* feel alive without being distracting. It's the only animated element in the header — everything else is motionless. Chanel's rule: one accessory.

---

## 5. Component Refinements

### Cards
- **Elevation:** Single `box-shadow` token `--gov-shadow` (0 1px 3px rgba(30,58,95,0.08), 0 1px 2px rgba(30,58,95,0.06)) — no `shadow-md/lg` from Tailwind.
- **Border:** `1px solid var(--border)` — consistent hairline.
- **Radius:** `0.75rem` (12px) — slightly rounder than current 8px for approachability.
- **Hover:** `shadow-[var(--gov-shadow-lg)]` (0 10px 15px -3px rgba(30,58,95,0.08), 0 4px 6px -2px rgba(30,58,95,0.04)) + `translateY(-1px)` — subtle lift.

### Tables (Critical for Admin)
- **Density toggle:** Three modes — `comfortable` (current), `compact` (12px cell padding, 11px font), `dense` (8px padding, 11px font, no hover). Persisted in localStorage per role.
- **Row striping:** `even:bg-muted/30` — subtle, not zebra.
- **Sorted column highlight:** `bg-navy-50/50` on the sorted column only.
- **Sticky first column** for candidate/opportunity name — `position: sticky; left: 0; background: white; z-index: 1;`.
- **Empty state inline:** When filtered results = 0, show inline illustration + "No matches for current filters" — not a full-card empty state.

### Buttons
- **Primary:** Navy (admin) / Saffron (employer) / Emerald (candidate) — role-colored.
- **Secondary:** Always `outline` variant with role-color border/text.
- **Ghost:** Role-color text, `hover:bg-[role]-50`.
- **Destructive:** Red — shared.
- **Loading state:** Spinner inside button, label changes to "Processing…" — no width shift (reserve space with `min-width`).
- **Focus ring:** `focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[role-color]`.

### Badges
- **Status variants:** Use semantic colors (green/amber/red) not role colors.
- **Category variants:** Role-color background + role-color-foreground text.
- **Size:** `sm` (10px padding) for tables, `md` (12px) for cards.

### Stats Cards
- **Icon background:** Role-color-50 with role-color-600 icon.
- **Trend:** Green/red only — no role color.
- **Value:** `text-data` font (JetBrains Mono) for numbers — keeps columns aligned across cards.

### Empty States
- **Illustration:** Custom SVG per context (not lucide icons):
  - No candidates → silhouette of people with `+` 
  - No opportunities → briefcase with search
  - No allocations → merge icon with dashed lines
  - No matches → two puzzle pieces not connecting
- **Tone:** Directional, not apologetic. "No candidates match your filters. Try broadening the sector or location." + primary action button.

### Loading / Skeleton
- **Shimmer:** `bg-gradient-to-r from-muted via-muted/50 to-muted` with `animate-[shimmer_1.5s_infinite]`.
- **Content-aware:** Table skeletons match column count. Card skeletons match card structure.
- **Progressive reveal:** Stats cards → tables → charts (staggered 100ms).

### Toasts
- **Position:** Top-right, stacked with 8px gap.
- **Role-color left border:** 3px solid role-color.
- **Icons:** Success (check), Error (x-circle), Warning (alert-triangle), Info (info).
- **Auto-dismiss:** 5s success/info, 8s warning, manual dismiss for error.

---

## 6. Motion — Restrained

| Interaction | Duration | Easing | Scope |
|-------------|----------|--------|-------|
| Button press | 80ms | `ease-out` | Transform scale 0.98 |
| Card hover | 150ms | `ease-out` | Shadow + translateY(-1px) |
| Sidebar slide | 200ms | `ease-in-out` | Transform X |
| Table row hover | 80ms | `ease-out` | Background only |
| Toast enter | 200ms | `ease-out` | Slide X + fade |
| Toast exit | 150ms | `ease-in` | Slide X + fade |
| Allocation Pulse | 3s/1.5s | `ease-in-out` | Header indicator only |
| Skeleton shimmer | 1.5s | `linear` | Loop |

**Reduced motion:** All animations disabled via `@media (prefers-reduced-motion: reduce)` — instant transitions.

---

## 7. Role-Specific Adaptations

### Admin (Navy)
- Header: Navy gradient logo bg, navy focus rings
- Sidebar active: `bg-navy-50 text-navy-600` with 3px left border `border-navy-600`
- Stats icons: `bg-navy-50 text-navy-600`
- Primary buttons: Navy
- Empty state icons: Navy tint

### Employer (Saffron)
- Header: Saffron logo bg
- Sidebar active: `bg-saffron-50 text-saffron-600` + left border
- Stats icons: `bg-saffron-50 text-saffron-600`
- Primary buttons: Saffron
- "Create Opportunity" = primary CTA everywhere

### Candidate (Emerald)
- Header: Emerald logo bg (`gov-gradient-emerald`: `linear-gradient(135deg, #10b981 0%, #059669 100%)`)
- Sidebar active: `bg-emerald-50 text-emerald-600` + left border
- Stats icons: `bg-emerald-50 text-emerald-600`
- Primary buttons: Emerald
- "Apply" buttons = primary
- Profile completion ring: Emerald gradient

---

## 8. Implementation Order

1. **Tokens & CSS Variables** — `globals.css` + `tailwind.config.ts` (extend theme)
2. **Typography** — Add Space Grotesk, DM Sans, JetBrains Mono via `next/font`; apply type scale
3. **Role Context Provider** — React context for current role → CSS variable injection on `<html>`
4. **Core Components** — Button, Card, Badge, Table, StatsCard, PageHeader, EmptyState, LoadingSpinner, Skeleton
5. **Layout Shells** — Admin/Employer/Candidate layouts with role-color injection
6. **Allocation Pulse** — Header component + polling hook
7. **Density Toggle** — Table density context + localStorage persistence
8. **Page Polish** — Apply to all 17 tested pages (admin: 7, employer: 4, candidate: 6)

---

## 9. Self-Critique / Risk Check

| Concern | Mitigation |
|---------|------------|
| Three role palettes = 3× maintenance | Tokens are derived; only 3 base hues. Component variants use `var(--role-primary)` etc. |
| Space Grotesk not on Google Fonts | Use `next/font/local` with variable font file (WOFF2) — 45KB variable vs 3× static |
| Data density vs. aesthetics | Density toggle gives power users compact mode; default is comfortable |
| Allocation Pulse = distraction? | Only in admin header. 8px dot. No sound, no toast. Can be disabled in settings (future). |
| Emerald for candidate — accessibility? | `--emerald-600` on white = 4.5:1 (AA). `--emerald-500` on white = 3.2:1 (AA large). Use 600 for text. |
| Table sticky column + horizontal scroll | Test thoroughly; `left: 0` + `z-index: 1` + background on cell not row |

---

## 10. Exit Criteria

- [ ] All 17 pages render with zero console errors
- [ ] Role switch (logout/login as different role) shows correct palette instantly
- [ ] Table density toggle persists and applies across all tables
- [ ] Allocation Pulse reflects backend state (idle/running/completed/error)
- [ ] `prefers-reduced-motion` disables all animation
- [ ] Mobile: sidebar slides, tables scroll horizontally, stats cards stack
- [ ] Lighthouse: Performance >90, Accessibility >95, Best Practices >90