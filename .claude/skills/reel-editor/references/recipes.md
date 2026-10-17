# Scene recipes — turning what the speaker says into a visual

Time every visual to the word that carries the idea (from `words.txt`). One idea at a time; change something on
screen every 1.5–3 s. Building blocks are in `scripts/mclib.py`; `examples/example_reel.py` shows them wired up.

| They say… | Visual | Building blocks |
|---|---|---|
| A hook question | big accent headline, then the answer appears | `accent_text()`, `El(..., "rise")` |
| A statistic / price / percentage | counter card counting to the number, fixed width | `DynEl(fn)` with a `panel` + `text_sprite` |
| "from X to Y" (a change) | the counter runs X → Y on the second figure, ▲/▼ badge | `DynEl`, `icon_badge("up"/"down", bg=RED)` |
| A list of 2–3 things | row of icon tiles, one per word | `tile(label, icon)` laid out right-to-left (RTL) |
| Steps / demands / tips | one numbered card at a time | `card(ic="#١")`, `card2(..., ic="#٢")` for two lines |
| "don't do X" | card struck through on the text + ✗ on its icon | `card(...).tb / .icon_x`, `bar(RED)` with `"wipe"` |
| "do X, Y, Z" | green pill + 3 round icon badges with labels | `pill(bg=GREEN)`, `icon_badge()` |
| Compare A vs B | 2×2 cards, equal widths, ≠ between | `card(..., auto=False)`, `text_sprite("≠")` |
| Cause → effect chain | circles linked by arrows drawn on | `circle()`, `arrow().rotate(180)` with `"wipe"` |
| "not against X, against Y" | grey card + red card with ✗ | `card(border=GRAY)`, `card(ic="cross", border=RED)` |
| A source (report, study, newspaper, date) | source card with `news` icon + grey date pill | `card(ic="news")`, `pill(bg=GRAY)` — only real sources |
| Breaking-news hook | 3 white news cards sliding in from alternating sides | `news_card()`, `El(..., "slide", frm=(±520, 0))` |
| An idea / insight | bulb rising from behind the head + glow + rays | `icon_badge("bulb")` with `z=-1`, `glow()`, `rays()` |
| A country / place | flag behind the speaker, fading only at its lower edge | `iraq_flag_behind()` as a pattern; draw others the same way |
| A trend going up | a line drawn across the background behind them | full-frame line sprite, `El(..., "wipel", z=-1)` |
| Asking the audience | poll card + two answer pills; outro repeats the question + "write in the comments" | `card2(ic="q")`, `pill`, `R.outro(question=..., cta=...)` |
| Punchline | white lead line + huge accent phrase (+ red strike for a negation, ✓ for affirmation) | `text_sprite`, `accent_text`, `bar(RED)`, `icon_badge("check")` |
| B-roll from another source | near-B&W look, white flashes on its cuts, tension bed, white quote captions | `R.looks`, `Flash`, `R.beds`, `captions(quote=True)` |
| Outro | dim + name/tagline (config) + closing question + call to action | `R.outro(t0, question=(l1, l2), cta=...)` |

Icons: search chat chart columns doc house coin people person book bulb check cross eye info q news bill cart ship
basket medicine device wallet shield up down scale play heart star clock phone camera mic globe car plane tool fire,
and number badges `"#1"`, `"#٢"`. Add new ones in `icon()` in the same flat 100-unit style when a topic needs it.

Entrances: `rise` (default for serious styles), `pop` (creator), `popsoft`, `slide` (with `frm=(dx, dy)`), `wipe`
(follows reading direction), `wipel` (left→right, for lines/charts), `fade`. Exits: `fade` (default), `drop`, `cut`, `None`.
Sound kinds for `add(..., kind)`: click, swish, strike, trans, impact, soft, readout, riser, flashin, flashout, hit.
