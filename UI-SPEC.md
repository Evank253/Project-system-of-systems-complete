# UI-SPEC

Design language: **dark engineering control center** — serious research/engineering tooling, not cyberpunk.

## Rules

- Deep dark surface (`#070A0F` base, `#0B0F17`/`#101622` panels), subtle 4rem grid lines, 1px tactical borders.
- Monospace accents (JetBrains Mono) for all technical values: statuses, hashes, IDs, endpoints, latencies.
- Display type: Outfit (heavy, tight) for headings; IBM Plex Sans for body.
- Accent: instrument cyan `#38BDF8`, used sparingly. Status colors: emerald `#10B981`, amber `#F59E0B`, crimson `#EF4444`, slate `#64748B`.
- Restrained motion: masked line-by-line hero reveal, slow invariant marquee, scroll reveals (once), hover micro-interactions. No neon, no glow abuse, no fake telemetry.

## Screens

1. **Home** — hero (KETCHUM / SYSTEM-OF-SYSTEMS + status strip: SYSTEM STATUS → LIVE · EVIDENCE → E0–E5 · AUTHORITY → HUMAN CONTROLLED · [RUN TEST]), invariant marquee, architecture map (8 sections), evidence/authority/TEVV overviews, live-state panel.
2. **/explorer** — filterable component registry; row per component; detail drawer with all registry fields incl. `[PLACEHOLDER]`s.
3. **/test** — connector catalog with configured state; task input; [RUN TEST]; factual result panel; execution history.
4. **/evidence** — E0–E5 ladder + NOT_MEASURED first-class card; upgrade rules; evidence records with hashes; benchmarks surface (historical vs current — both explicitly empty).
5. **/docs** — spec document index + markdown reader served by `/api/docs`.

## Honesty requirements in UI

- A component is never styled as verified/qualified unless the record says so (none do).
- Unconfigured connectors show `NOT_CONFIGURED`, never a friendly fake success.
- Empty states are explicit ("no records exist yet — run a live test"), never blank dashes.
- Every interactive element carries a `data-testid` (kebab-case).
