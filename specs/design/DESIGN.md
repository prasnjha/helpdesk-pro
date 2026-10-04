# HelpDesk Pro — Design Tokens & Component Rules

Source: Stitch project `HelpDesk Pro Login Interface` (`projects/1841795218645747016`), design theme "HelpDesk Clarity", Inter font, light colour mode, Fidelity colour variant, ROUND_EIGHT roundness.
Screenshots: `specs/design/mockups/*.png` (one per Stitch screen, native resolution).

> **Two colour sources.** The Stitch project carries two palettes. The prose rules and the `override*` colours in the theme use the brand palette below (Tailwind slate + blue/red). The Material-generated `colors:` block in the theme's front matter is a derived palette with different hex values. Section 1 uses the brand palette because the project's overrides pin it. Section 1.4 lists the generated values for reference. Implementers should use Section 1.1–1.3 and treat 1.4 as a fallback only if a screen was built from it.

---

## 1. Colour tokens

### 1.1 Brand and semantic (authoritative)

| Token | Hex | Use |
|---|---|---|
| `primary` | `#2563EB` | Primary actions, active nav, focused field outlines, interactive ticket workflow |
| `primary-hover` | `#1D4ED8` | Hover on primary |
| `primary-active` | `#1E40AF` | Pressed primary |
| `secondary` | `#0F172A` | Headings, structural text, nav anchors |
| `critical` | `#DC2626` | Alerts, SLA breach, ticket failure, destructive actions |
| `critical-bg` | `#FEF2F2` | Error tint background |
| `critical-border` | `#FCA5A5` | Error tint border |
| `success` | `#059669` | Resolved, healthy infrastructure |
| `success-bg` | `#ECFDF5` | Success tint background |
| `warning` | `#D97706` | Pending approval, assigned triage, approaching SLA |
| `warning-bg` | `#FFFBEB` | Warning tint background |

### 1.2 Neutrals and surfaces

| Token | Hex | Use |
|---|---|---|
| `canvas` | `#F8FAFC` | Page background (Level 0) |
| `surface-sidebar` | `#F1F5F9` | Sidebar, secondary surface, hover fill, card header divider |
| `surface-card` | `#FFFFFF` | Cards, inputs, tables |
| `border` | `#E2E8F0` | Hairlines, card and input borders |
| `border-checkbox` | `#CBD5E1` | Checkbox and radio outline |
| `text-body` | `#334155` | Body text |
| `text-muted` | `#64748B` | Metadata, helper text, placeholders |
| `text-strong` | `#0F172A` | Input text and headings |

### 1.3 Status chip palette

| Status | Background | Text | Border |
|---|---|---|---|
| Open / Triage | `#EFF6FF` | `#1D4ED8` | `#BFDBFE` |
| In progress / Warning | `#FFFBEB` | `#B45309` | `#FDE68A` |
| Critical / SLA breach | `#FEF2F2` | `#B91C1C` | `#FECACA` |
| Resolved | `#ECFDF5` | `#047857` | `#A7F3D0` |

### 1.4 Generated palette (front-matter `colors:`, reference only)

| Token | Hex |
|---|---|
| `primary` | `#004ac6` |
| `primary-container` | `#2563eb` |
| `on-primary` | `#ffffff` |
| `secondary` | `#565e74` |
| `tertiary` | `#ae0010` |
| `tertiary-container` | `#d52022` |
| `error` | `#ba1a1a` |
| `error-container` | `#ffdad6` |
| `surface` / `background` | `#f8f9ff` |
| `surface-container-lowest` | `#ffffff` |
| `surface-container-low` | `#eff4ff` |
| `surface-container` | `#e5eeff` |
| `surface-container-high` | `#dce9ff` |
| `surface-container-highest` | `#d3e4fe` |
| `on-surface` | `#0b1c30` |
| `on-surface-variant` | `#434655` |
| `outline` | `#737686` |
| `outline-variant` | `#c3c6d7` |

---

## 2. Type scale

Font: **Inter** for every role. Headline tracking tightens with size.

| Token | Size / line-height | Weight | Tracking | Use |
|---|---|---|---|---|
| `headline-xl` | 36 / 44 px | 700 | -0.02em | Hero or page titles (desktop) |
| `headline-lg` | 30 / 38 px | 700 | -0.015em | Page titles |
| `headline-lg-mobile` | 24 / 32 px | 700 | -0.01em | Page titles (mobile) |
| `headline-md` | 22 / 28 px | 600 | -0.01em | Section titles |
| `headline-sm` | 18 / 24 px | 600 | — | Card titles |
| `body-lg` | 16 / 24 px | 400 | — | Lead text, empty states |
| `body-md` | 14 / 20 px | 400 | — | **Core operational baseline**: records, notes, thread content |
| `body-sm` | 12 / 16 px | 400 | — | Requester, timestamp, helper text |
| `label-lg` | 14 / 20 px | 600 | — | Form labels, button text |
| `label-md` | 12 / 16 px | 500 | — | Secondary labels |
| `label-sm` | 11 / 14 px | 600, uppercase | +0.02em | Status tags and category chips only |
| `code-sm` | 12 / 16 px | 500 | — | Inline identifiers (ticket IDs) |

---

## 3. Spacing, grid and breakpoints

Base rhythm: 4 px / 8 px.

| Token | Value | Use |
|---|---|---|
| `space-xs` | 4 px (0.25rem) | Icon and label pairs, tightly coupled inputs |
| `space-sm` | 8 px (0.5rem) | Inline component gaps |
| `space-md` | 12 px (0.75rem) | |
| `space-lg` | 16 px (1rem) | Structural gaps, mobile gutter |
| `space-xl` | 24 px (1.5rem) | Card padding, breathing room |
| `space-2xl` | 32 px (2rem) | Section spacing |
| `gutter` | 16 px | Tablet and mobile column gap |
| `gutter-lg` | 24 px | Desktop column gap |
| `margin` | 16 px | Mobile canvas margin |
| `margin-md` | 24 px | Tablet canvas margin |
| `margin-lg` | 32 px | Desktop canvas margin |

**Grid:** desktop uses a collapsible **240 px** navigation rail and a **12-column fluid grid**.

| Breakpoint | Layout |
|---|---|
| Desktop ≥ 1024 px | Split-screen ticket triage, multi-column board, dense detail panels |
| Tablet 768–1023 px | Gutter 16 px, margin 24 px. Sidebar becomes an overlay drawer. Master-detail stacks into step panels. |
| Mobile < 768 px | Margin 16 px. Single column cards. Full-width primary action bar pinned to bottom of viewport. |

---

## 4. Radius and elevation

| Token | Value | Use |
|---|---|---|
| `radius-sm` | 4 px | |
| `radius-default` | 8 px | Buttons, inputs, form controls |
| `radius-md` | 12 px | |
| `radius-card` | 16 px (up to 24 px for large containers) | Cards and containers |
| `radius-full` | 9999 px | Pills and status chips |

| Level | Surface | Shadow / border | Use |
|---|---|---|---|
| 0 | `canvas` `#F8FAFC` | none | Page background |
| 1 | `surface-card` `#FFFFFF` | `1px solid #E2E8F0`, `0 1px 2px 0 rgba(15,23,42,0.04)` | Cards, tables |
| 2 | `#FFFFFF` | `1px solid #E2E8F0`, `0 4px 6px -1px rgba(15,23,42,0.08), 0 2px 4px -2px rgba(15,23,42,0.04)` | Popovers, selects, dropdowns |
| 3 | `#FFFFFF` | `0 20px 25px -5px rgba(15,23,42,0.1), 0 8px 10px -6px rgba(15,23,42,0.04)`; backdrop `rgba(15,23,42,0.45)` with 2 px blur | Modals, drawers |
| Focus | — | `0 0 0 3px rgba(37,99,235,0.2)` | Interactive focus (no harsh shadow) |

---

## 5. Component rules

### 5.1 Buttons
- **Primary:** bg `#2563EB`, text `#FFFFFF`, radius 8 px, height 40 px, padding `0 16px`. Hover `#1D4ED8`, active `#1E40AF`. Focus: 2 px gap plus 3 px ring `rgba(37,99,235,0.3)`.
- **Secondary:** bg `#FFFFFF`, `1px solid #E2E8F0`, text `#334155`. Hover bg `#F1F5F9`, text `#0F172A`.
- **Destructive:** bg `#DC2626`, text `#FFFFFF`. Reserved for ticket deletion, role revocation, permanent rollback. Nothing else.

### 5.2 Inputs
- Height 40 px, bg `#FFFFFF`, `1px solid #E2E8F0`, radius 8 px, text `body-md` `#0F172A`, placeholder `#64748B`.
- Focus: border `#2563EB`, ring `3px rgba(37,99,235,0.15)`.
- Error: border `#DC2626`, ring `rgba(220,38,38,0.15)`, helper text `body-sm` `#DC2626` below the field.
- Checkbox and radio: 16 px, `1px solid #CBD5E1`. Checked fills `#2563EB` with white check or dot.
- Labels: `label-lg` or `label-md`, medium to semibold.

### 5.3 Status chips
- Height 24 px, radius full, horizontal padding 10 px, 1 px border, `label-sm` uppercase for tags.
- Colour mapping per Section 1.3. Breach chips use the rose palette, not the primary red fill.

### 5.4 Cards
- Bg `#FFFFFF`, `1px solid #E2E8F0`, radius 16 px, padding 24 px, shadow Level 1.
- Header: bottom divider `1px solid #F1F5F9`, actions right-aligned.

### 5.5 Ticket list rows
- Height 56–64 px. Hover bg `#F8FAFC`.
- Left priority notch: 3 px solid, colour per urgency.
- Single-line truncating summary (`body-md`). Requester and timestamp in `body-sm` `#64748B`.

### 5.6 Navigation
- Desktop: 240 px collapsible rail. Active item uses `primary` treatment. Anchors use `#0F172A`.
- Tablet/mobile: overlay drawer.

### 5.7 Tone rules
- Red (`#DC2626`) is for errors, breaches and destructive actions only. Do not use it for decoration.
- Blue is for interaction. Do not use it for status.
- Emerald and amber mark resolved and approaching-SLA states respectively.

---

## 6. Screens

Screenshots are in `specs/design/mockups/`. Each file is the Stitch screenshot at native width.

| Screen (Stitch title) | Width | File |
|---|---|---|
| HelpDesk Pro - Login | 780 | `login.png` |
| My tickets - HelpDesk Pro | 780 | `my-tickets.png` |
| New ticket - HelpDesk Pro | 780 | `new-ticket.png` |
| Ticket Detail (Customer View) - HelpDesk Pro | 780 | `ticket-detail-customer-view.png` |
| Agent Ticket Queue - HelpDesk Pro | 2560 | `agent-ticket-queue.png` |
| Ticket Detail (Active) - HelpDesk Pro | 2560 | `ticket-detail-active.png` |
| Ticket Detail (Closed Variant) - HelpDesk Pro | 2560 | `ticket-detail-closed-variant.png` |
| Admin Console - HelpDesk Pro | 2560 | `admin-console.png` |
| Knowledge Base - HelpDesk Pro | 2560 | `knowledge-base.png` |
| Article Detail: Cisco AnyConnect VPN - HelpDesk Pro | 2560 | `article-detail-cisco-anyconnect-vpn.png` |
| HelpDesk Pro Logo (asset, 96 px) | 48 | `helpdesk-pro-logo.png` |

Mobile screens are 780 px wide (2× of 390 px). Desktop screens are 2560 px wide (2× of 1280 px).
