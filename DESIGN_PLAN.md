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
| `--slate-900` | `#0f172a` | High-contrast text |

**Semantic aliases** (used in components):
- `--color-primary` / `--color-primary-foreground` — role-specific
- `--color-secondary` / `--color-secondary-foreground` — role-specific
- `--color-accent` / `--color-accent-foreground` — role-specific
- `--color-success` = `--emerald-500`
- `--color-warning` = `--saffron-500`
- `--color-error` = `#dc2626`
- `--color-info` = `--navy-500`

---

## 2. Typography — Deliberate Pairing

| Role | Font | Usage |
|------|------|-------|
| **Display** | `Instrument Serif` (variable, 400/500/600) | Page titles, hero numbers, stat values — *authority, government gravitas* |
| **Body** | `DM Sans` (variable, 400/500/600) | All UI text, tables, forms — *legible at density* |
| **Mono** | `JetBrains Mono` (variable, 400/500) | IDs, timestamps, code, monetary values — *technical precision* |

**Type Scale (fluid, clamp-based):**

```css
--text-xs:      clamp(0.6875rem, 0.65rem + 0.15vw, 0.75rem);      /* 11-12px */
--text-sm:      clamp(0.8125rem, 0.775rem + 0.15vw, 0.875rem);    /* 13-14px */
--text-base:    clamp(0.9375rem, 0.9rem + 0.15vw, 1rem);          /* 15-16px */
--text-lg:      clamp(1.0625rem, 1.025rem + 0.15vw, 1.125rem);    /* 17-18px */
--text-xl:      clamp(1.25rem, 1.175rem + 0.3vw, 1.375rem);       /* 20-22px */
--text-2xl:     clamp(1.5rem, 1.375rem + 0.5vw, 1.75rem);         /* 24-28px */
--text-3xl:     clamp(1.875rem, 1.625rem + 1vw, 2.25rem);         /* 30-36px */
--text-4xl:     clamp(2.25rem, 1.875rem + 1.5vw, 3rem);           /* 36-48px */
```

**Weights:** 400 (regular), 500 (medium), 600 (semibold) — no 700, keeps it refined.

---

## 3. Layout — Density with Breathing Room

**Grid:** 12-column, 24px gutters, 32px page margins (lg: 48px)
**Container max-widths:**
- Admin (dense tables): `1400px`
- Employer (cards + forms): `1100px`
- Candidate (centered flows): `900px`

**Spacing scale (Tailwind-compatible):**
```
0.5  1  1.5  2  2.5  3  3.5  4  5  6  7  8  9  10  12  16  20  24
2px 4px 6px 8px 10px 12px 14px 16px 20px 24px 28px 32px 36px 40px 48px 64px 80px 96px
```

**Card elevation:**
- Level 0: `border only` (tables, inline cards)
- Level 1: `gov-shadow` (default cards)
- Level 2: `gov-shadow-lg` (hover, modals, dropdowns)
- Level 3: `gov-shadow-xl` (toasts, popovers)

```css
--gov-shadow: 0 1px 2px rgba(10,20,40,0.04), 0 1px 3px rgba(10,20,40,0.06);
--gov-shadow-lg: 0 4px 8px -2px rgba(10,20,40,0.08), 0 2px 4px -2px rgba(10,20,40,0.04);
--gov-shadow-xl: 0 10px 20px -5px rgba(10,20,40,0.1), 0 4px 8px -4px rgba(10,20,40,0.06);
```

---

## 4. Signature Element — "Allocation Pulse"

**Concept:** A subtle, ambient indicator that an allocation cycle is active — appears in the admin sidebar and dashboard header. Not a spinner. A breathing ring that pulses once per cycle step (5 stages).

```css
@keyframes allocation-pulse {
  0%, 100% { transform: scale(1); opacity: 0.4; }
  50% { transform: scale(1.15); opacity: 1; }
}

.allocation-pulse::before {
  content: "";
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid var(--color-primary);
  animation: allocation-pulse 3s ease-in-out infinite;
}
```

**Placement:** Top-right of admin sidebar (next to "Allocation Cycles" label), and as a small indicator in the dashboard header when a cycle is `running`. Only visible to admin role. Embodies the product's core action.

---

## 5. Role-Specific Identity

### Admin — "Mission Control"
- **Primary:** Navy (`--navy-600`)
- **Sidebar:** Dark navy (`--navy-900`) with white text, active item = saffron accent bar left
- **Tables:** High density, hover = slate-50, selected = navy-50 + left border
- **Empty states:** Icon + "No allocation cycles yet" + "Run Allocation" CTA
- **Tone:** Precise, authoritative, data-dense

### Employer — "Talent Hub"
- **Primary:** Saffron (`--saffron-500`)
- **Sidebar:** White, active item = saffron background + white text
- **Cards:** Warmth — saffron-50 backgrounds for featured items
- **Forms:** Generous, guided, inline validation
- **Tone:** Welcoming, action-oriented, "post an opportunity"

### Candidate — "Pathway"
- **Primary:** Emerald (`--emerald-500`)
- **Sidebar:** White, active item = emerald background + white text
- **Progress:** Visual stepper on profile (6 steps), match cards with score badges
- **Empty states:** Illustrative, encouraging ("Your profile is 60% complete — add skills to see matches")
- **Tone:** Encouraging, clear next steps, low anxiety

---

## 6. Component Elevations

### StatsCard
- **Icon container:** `rounded-xl p-3` with role-primary-100 bg
- **Value:** `--text-3xl` Display font, tabular-nums
- **Trend:** Inline flex, 12px icon + 11px text
- **Hover:** `shadow-lg` + `translate-y-[-2px]`

### PageHeader
- **Breadcrumbs:** 12px mono, separators = `/` in mono
- **Title:** `--text-3xl` Display, `--text-2xl` on mobile
- **Description:** `--text-base` body, max-w-2xl
- **Actions:** Right-aligned, gap-2

### Table (Admin)
- **Header:** 11px uppercase mono, tracking-wider, text-muted
- **Row height:** 48px (compact), 56px (comfortable) — toggle in header
- **Hover:** `bg-slate-50/50`
- **Selected:** `bg-navy-50` + `border-l-2 border-navy-500`
- **Sortable:** Chevron mono 10px, only on hover/focus
- **Pagination:** 12px mono for page numbers

### Button
- **Primary:** Role-primary bg, white text, `shadow-sm`
- **Secondary:** Role-primary-100 bg, role-primary-700 text
- **Outline:** 1px role-primary border, role-primary text
- **Ghost:** Transparent, role-primary text
- **Loading:** Spinner replaces icon, width locked
- **Disabled:** 40% opacity, cursor-not-allowed

### Badge
- **Status variants:** success/warning/error/info + neutral
- **Size:** sm (10px/px-2), md (11px/px-2.5)
- **Dot variant:** 6px dot + label for inline status

### EmptyState
- **Illustration:** Role-specific SVG (admin=database, employer=briefcase, candidate=compass)
- **Title:** 16px semibold
- **Description:** 14px muted, max-w-sm
- **Action:** Primary button, centered

### Loading / Skeleton
- **Skeleton:** `bg-slate-200 animate-pulse` with `bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200` shimmer
- **Page loader:** Role-primary spinner, centered, "Loading [page]…"
- **Table skeleton:** 5 rows × col count, stagger delay 50ms

---

## 7. Motion — Restrained, Purposeful

| Interaction | Duration | Easing | Use Case |
|-------------|----------|--------|----------|
| Hover (cards, buttons, rows) | 150ms | `ease-out` | All interactive |
| Sidebar slide | 200ms | `ease-in-out` | Mobile nav |
| Modal/Dialog enter | 180ms | `ease-out` | Confirmations, forms |
| Toast slide-in | 250ms | `ease-out` | Notifications |
| Table row select | 100ms | `ease-out` | Checkbox selection |
| Allocation pulse | 3000ms | `ease-in-out` | Signature element only |

**Reduced motion:** `@media (prefers-reduced-motion: reduce)` — all transitions → 0ms, pulse animation paused.

---

## 8. Accessibility Floor (Non-Negotiable)

- **Contrast:** All text ≥ 4.5:1 (AA), large text ≥ 3:1
- **Focus:** Visible 2px ring, offset 2px, role-primary color
- **Keyboard:** Every interactive element reachable, operable
- **ARIA:** `aria-live` for toasts, `aria-sort` for tables, `aria-expanded` for dropdowns
- **Color-blind safe:** Status never color-only — always icon + label or pattern
- **Touch targets:** ≥ 44×44px (mobile)

---

## 9. Implementation Order

1. **Tokens & CSS Variables** — Extend `globals.css` with full palette, type scale, shadows
2. **Fonts** — Add `@font-face` for Instrument Serif, DM Sans, JetBrains Mono (self-hosted via next/font)
3. **Base Components** — Button, Badge, Card, Input, Table (update existing)
4. **Layout Primitives** — PageHeader, StatsCard, EmptyState, Skeleton (update existing)
5. **Role Layouts** — AdminLayout, EmployerLayout, ApplicantLayout (apply role theming)
6. **Signature** — AllocationPulse component + sidebar integration
7. **Page Polish** — Admin dashboard, candidates, opportunities, allocations, matching, audit
8. **Employer Pages** — Dashboard, internships, internships/new, internships/[id]
9. **Candidate Pages** — Dashboard, profile, internships, applications, offers
10. **Cross-cutting** — Toast, Dialog, Dropdown, Select, Tooltip polish
11. **QA Pass** — Mobile, reduced motion, keyboard, contrast audit

---

## 10. What We're NOT Doing

- Dark mode (government portals rarely use it; adds complexity without user demand)
- Animation library (Framer Motion) — CSS transitions suffice
- Component library abstraction — keep it in `components/ui` and `components/shared`
- Design tokens package — CSS variables are the single source of truth
- A/B testing variants — this is a deliberate design, not a template

---

## 11. Success Criteria

- Admin can scan 50-row table without eye strain (density + contrast)
- Employer creates opportunity in < 3 minutes (guided form, clear feedback)
- Candidate completes profile in one session (progress visualization, inline save)
- Zero console errors, zero layout shift on load
- Lighthouse: Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 90
- **Signature moment:** Admin sees the allocation pulse and knows "the engine is running" without reading text