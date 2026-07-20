# MAS export-view shells (`*__any.html`) — drop-in manifest

The archetype-neutral page shells the export factory injects payload JSON into.
`payload_factory/render/export.py` loads them from THIS directory (package data,
same convention as `render/templates/*.j2`).

## Add the real shells here (two ways — pick one)

**A. Clean copy (best).** The originals on disk are UTF-8; copy them straight in:

```
cp /path/to/your/templates/{1_welcome,2_landing,3_risk,4_map,5_scenario,5.1_deepdive,6_combined}__any.html \
   src/payload_factory/render/templates/mas_pages/
```

**B. Save-then-repair.** If you only have the pasted copies (which get corrupted:
`·`→`Â·`, `—`→`â`, `🏭`→`ð­`), save them here anyway, then run the repair tool
from the repo root — it reverses the corruption byte-perfectly and skips clean files:

```
python fix_mojibake.py src/payload_factory/render/templates/mas_pages/*.html
# add --check first to see what it would change, changing nothing
```

Either way the factory reads them by the exact filenames below; nothing else needs editing.

## The set — filename · injection token · shaper · external deps to vendor

| page | filename | token | payload slice | shaper (`render/pages.py`) | CDN deps to vendor (Phase-4 self-containment) |
|---|---|---|---|---|---|
| 1 Welcome | `1_welcome__any.html` | `__MAS_PAGE1__` | `MAS_P1` | `page_1` ✅ | **none — already self-contained** |
| 2 Landing | `2_landing__any.html` | `__MAS_PAGE2__` | `MAS_P2` | `page_2` ✅ | Leaflet (unpkg) |
| 3 Risk | `3_risk__any.html` | `__MAS_PAGE3__` | `MAS_P3` | `page_3` ✅ | Leaflet (unpkg) |
| 4 Map | `4_map__any.html` | `__MAS_PAGE4__` | `MAS_P4` | `page_4` ✅ | Leaflet (unpkg) · Google-Fonts (Oswald) |
| 5 Scenario | `5_scenario__any.html` | `__MAS_PAGE5__` | `MAS_P5` | `page_5` ✅ | Leaflet (unpkg) · Google-Fonts |
| 5.1 Deep-dive | `5.1_deepdive__any.html` | `__MAS_PAYLOAD__` | `PAYLOAD.page_deepdive` | `page_deepdive` ✅ | Google-Fonts |
| 6 Combined | `6_combined__any.html` | `__MAS_PAGE6__` | `MAS_P6` | `page_6` ✅ | Font-Awesome (cdnjs) · Google-Fonts |

✅ all 7 shapers built (`render/pages.py`) and contract-tested. Each renders crash-safe from a
stamped payload; identity + geometry are payload-driven, analytic/presentation content is honest-empty
(`[TO_BE_FILLED]` / empty arrays) until its MAS_DERIVED source (opportunity menu, hazard screen, VIP
anchors) is attached — never fabricated.

## Binding contract (shared by every shell)

Each shell reads its JSON from `<script id="mas-pageN" type="application/json">TOKEN</script>`
then binds by attribute: `data-bind-html` (→ `strings[key]`), `data-bind-block`
(→ `blocks[key]`, innerHTML), `data-bind-attr` (`attr:key` or `key@attr` → attribute).
So a shaper returns `{strings:{…}, blocks:{…}, …page-specific arrays…}`. Numbers arrive
pre-shaped from the deterministic core — the browser never computes (payload.py contract).

## Self-containment (Phase 4, after shells land)

The MAS export view is self-contained (no external requests). Page 1 already is.
For the rest, vendor Leaflet (inline CSS+JS), drop Google-Fonts to the Oswald/system
stack the CSS already falls back to, and replace Font-Awesome (page 6 only) with the
inline-SVG icon set the shells already ship. Then `tests/test_render_export.py`'s
no-external-URL assertion can point at the real shells too.
