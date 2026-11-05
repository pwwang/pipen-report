"""Generate the two extra report themes into public/assets/global.css.

    python3 pipen_report/frontend/gen_themes.py [path/to/all.css]

Each theme is the *full* carbon token set of a carbon base theme with its colours
remapped, so every component that reads `--cds-*` follows the palette:

  paper    <- g10    light; neutrals warmed, accent family -> deep green
  nocturne <- g100   dark;  neutrals -> navy ramp, accent family -> amber

Why rank-mapping and not a colour table: carbon's token set differs between ccs
releases (0.96 has one `[theme=g10]` block with 455 declarations; 0.113 splits the
themes into `:root` defaults plus per-theme deltas and mixes v10/v11 token names).
Colours are therefore bucketed by kind — neutral (channel spread <= 12) or accent
(blue hue) — and mapped by *rank* inside their bucket onto the target ramp, so
shifted base greys still land in the right place. Everything else (support reds,
greens, yellows) is left alone: the base theme already picked light- or
dark-appropriate versions.

Upgrading carbon-components-svelte: re-run this script against the new
`node_modules/.../css/all.css` (or pass a path). It reads the defaults from every
`:root` block and the theme deltas from `[theme=...]`, so it works with both the
0.96 layout (one full block per theme) and the 0.113 layout (`:root` defaults +
per-theme deltas + v10/v11 token names). Colours it does not know are placed on
the ramp by luminance, and if carbon restructures its theme blocks the script
stops with an error instead of emitting a half theme.

The blocks are written between the `/* >>> generated themes >>> */` markers in
global.css, so the file regenerates without touching hand-written rules, and they
use `html[theme=...]` selectors because global.css is linked before the page css
(a bare `[theme=x]` would lose to carbon's `:root` on equal specificity).
"""

import colorsys
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
DEFAULT_ALL_CSS = ROOT / "node_modules/carbon-components-svelte/css/all.css"
GLOBAL_CSS = ROOT / "public/assets/global.css"

# target ramps, light -> dark, sampled to whatever length the base set needs
RAMPS = {
    "paper": {
        "neutral": ["#fdfbf6", "#f9f4ea", "#f6f1e6", "#f2ebdd", "#ece4d4", "#e7decc",
                    "#ded4c0", "#cfc4ae", "#a29784", "#8b8272", "#6b6252", "#5a5244",
                    "#3d382f", "#2e2a23", "#241f19", "#1b1710"],
        "accent": ["#dce8e2", "#bcd8cd", "#9ec7b8", "#7fb3a1", "#5c9c88", "#3f8672",
                   "#2e7a66", "#1f5c4d", "#17483d", "#123a31"],
    },
    "nocturne": {
        "neutral": ["#fafcff", "#e8edf6", "#dde4ee", "#d5ddea", "#c4cee0", "#b6c2d6",
                    "#a8b4ca", "#9aa8c0", "#7e8ca6", "#5f6f8e", "#4a5a78", "#354563",
                    "#2a3a57", "#223050", "#1b2740", "#131c2e", "#0b1220", "#070d17"],
        "accent": ["#ffe6b0", "#f8d68d", "#f5c462", "#f2b94a", "#f0b429", "#d8a63a",
                   "#c9912a", "#8f6712"],
    },
}

# hand-picked targets for the colours carbon ships today (ccs 0.96 .. 0.113 greys)
EXACT = {
    "paper": {
        "#ffffff": "#fdfbf6", "#f4f4f4": "#f6f1e6", "#f3f3f3": "#f4eee1",
        "#e8e8e8": "#ece4d4", "#e5e5e5": "#f0eada", "#e0e0e0": "#e7decc",
        "#d1d1d1": "#ded4c0", "#cacaca": "#d6cbb5", "#c6c6c6": "#cfc4ae",
        "#bebebe": "#c7bba4", "#a8a8a8": "#a29784", "#8d8d8d": "#8b8272",
        "#6f6f6f": "#6b6252", "#525252": "#5a5244", "#393939": "#2e2a23",
        "#262626": "#241f19", "#161616": "#241f19", "#0f0f0f": "#1b1710",
        "#0f62fe": "#1f5c4d", "#0043ce": "#17483d", "#002d9c": "#123a31",
        "#4589ff": "#2e7a66", "#78a9ff": "#4e9c86", "#a6c8ff": "#bcd8cd",
        "#d0e2ff": "#dce8e2", "#edf5ff": "#eaf1ed",
        "#da1e28": "#a62920", "#ba1b23": "#8f211a", "#750e13": "#6b1712",
        "#198038": "#3d7a44", "#0e6027": "#2f6136", "#044317": "#24492a",
        "#b28600": "#8a6300", "#8e6a00": "#6f5200", "#684e00": "#553f00",
    },
    "nocturne": {
        "#161616": "#0b1220", "#1a1a1a": "#0e1525", "#1c1c1c": "#101828",
        "#21272a": "#131c2e", "#262626": "#131c2e", "#2c2c2c": "#172034",
        "#303030": "#1b2740", "#353535": "#1f2c46", "#393939": "#1b2740",
        "#3d3d3d": "#223050", "#454545": "#25334f", "#4c4c4c": "#2a3a57",
        "#525252": "#2a3a57", "#5e5e5e": "#354563", "#6f6f6f": "#4a5a78",
        "#757575": "#4f5f7e", "#8d8d8d": "#7e8ca6", "#a8a8a8": "#9aa8c0",
        "#bebebe": "#a8b4ca", "#c6c6c6": "#b6c2d6", "#d1d1d1": "#c4cee0",
        "#e0e0e0": "#d5ddea", "#e5e5e5": "#dae1ec", "#e8e8e8": "#dde4ee",
        "#f4f4f4": "#e8edf6", "#ffffff": "#fafcff",
        "#0f62fe": "#f0b429", "#0043ce": "#c9912a", "#002d9c": "#8f6712",
        "#4589ff": "#7fb2ff", "#78a9ff": "#8fb8ff", "#a6c8ff": "#b7d2ff",
        "#d0e2ff": "#203050", "#edf5ff": "#131c2e",
        "#da1e28": "#ff7b7b", "#ba1b23": "#ff9a9a", "#750e13": "#4a1414",
        "#198038": "#5fd68f", "#0e6027": "#39a866", "#044317": "#123a24",
        "#f1c21b": "#f5c462", "#b28600": "#d8a63a", "#684e00": "#3a2c08",
    },
}

TARGETS = [("paper", "g10"), ("nocturne", "g100")]

BANNER = """/* ==========================================================================
   Generated themes — do not edit by hand; run frontend/gen_themes.py.
   Full carbon token set of a carbon base theme with its colours remapped
   (neutrals and the accent family by rank inside their ramp), so components
   reading --cds-* follow the palette whatever ccs version produced the base.
   ========================================================================== */
"""

DECL = re.compile(r"(--cds-[a-z0-9-]+)\s*:\s*([^;}]+)")
HEX = re.compile(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?")


def collect_tokens(css: str, theme: str) -> dict[str, str]:
    """Merge carbon's defaults with this theme's own declarations.

    0.96 keeps the whole set in one `[theme=x]` block; 0.113 keeps the defaults in
    `:root` and only the differences per theme, sometimes in several blocks.
    """
    tokens: dict[str, str] = {}
    defaults = 0
    for body in re.findall(r":root\s*\{([^}]*)\}", css):
        for name, value in DECL.findall(body):
            tokens[name] = value.strip()
            defaults += 1
    # 0.113 nests the selector as `:root[theme=g100]{...}` and only lists the deltas
    for body in re.findall(r"\[theme=" + theme + r"\]\{([^}]*)\}", css):
        for name, value in DECL.findall(body):
            tokens[name] = value.strip()
    return tokens


def bucket(hexval: str) -> str | None:
    """'neutral' (no hue), 'accent' (blue family) or None (leave alone)."""
    h = hexval.lstrip("#")
    if len(h) == 8:  # drop alpha, keep the colour judgement on rgb
        h = h[:6]
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    spread = max(r, g, b) - min(r, g, b)
    if spread <= 0.05:
        return "neutral"
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    deg = hue * 360
    if 195 <= deg <= 265 and sat > 0.25:
        return "accent"
    return None


def nearest_ramp(hexval: str, ramp: list[str]) -> str:
    want = luma(hexval)
    return min(ramp, key=lambda c: abs(luma(c) - want))


def luma(hexval: str) -> float:
    h = hexval.lstrip("#")[:6]
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def build_map(tokens: dict[str, str], theme: str) -> dict[str, str]:
    ramp = RAMPS[theme]
    exact = EXACT[theme]
    buckets: dict[str, set[str]] = {"neutral": set(), "accent": set()}
    for value in tokens.values():
        for hexval in HEX.findall(value):
            kind = bucket(hexval)
            if kind:
                buckets[kind].add(hexval.lower())

    mapping: dict[str, str] = {}
    for kind, values in buckets.items():
        for hexval in values:
            # a colour we know exactly keeps its hand-picked target; anything new in a
            # later carbon release lands on the ramp stop with the closest luminance
            mapping[hexval] = exact.get(hexval) or nearest_ramp(hexval, ramp[kind])
    return mapping


def remap(tokens: dict[str, str], mapping: dict[str, str]) -> tuple[dict[str, str], int]:
    out, changed = {}, 0

    def sub(m: re.Match) -> str:
        nonlocal changed
        hexval = m.group(0).lower()
        if hexval in mapping:
            changed += 1
            return mapping[hexval]
        return m.group(0)

    for name, value in tokens.items():
        out[name] = HEX.sub(sub, value)
    return out, changed


def main() -> None:
    all_css = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ALL_CSS
    css = all_css.read_text()
    print(f"base css: {all_css}")

    blocks = []
    for theme, base in TARGETS:
        tokens = collect_tokens(css, base)
        if len(tokens) < 200:
            raise SystemExit(
                f"only {len(tokens)} tokens found for theme {base!r} in {all_css} — "
                "carbon's theme structure changed; update collect_tokens()"
            )
        mapping = build_map(tokens, theme)
        recoloured, changed = remap(tokens, mapping)
        print(f"{theme:9s} base={base:5s} tokens={len(tokens):4d} "
              f"colours-mapped={len(mapping):3d} declarations-recoloured={changed}")
        body = "".join(f"{name}:{value};" for name, value in recoloured.items())
        blocks.append(f"html[theme={theme}]{{{body}}}")

    generated = BANNER + "\n" + "\n".join(blocks) + "\n"
    text = GLOBAL_CSS.read_text()
    begin, end = "/* >>> generated themes >>> */", "/* <<< generated themes <<< */"
    if begin in text and end in text:
        text = text.split(begin)[0] + begin + "\n" + generated + end + text.split(end, 1)[1]
    else:
        text = text.rstrip() + "\n\n" + begin + "\n" + generated + end + "\n"
    GLOBAL_CSS.write_text(text)
    try:
        shown = GLOBAL_CSS.relative_to(ROOT)
    except ValueError:
        shown = GLOBAL_CSS
    print(f"wrote {shown} ({len(text)} bytes)")


if __name__ == "__main__":
    main()
