"""Render a Profile to a standalone HTML brief.

No free-generated commentary: every sentence here is a template
filled from `Profile` fields (an f-string against real numbers), never
a call out to a model asked to "write something about this state".
The one-line takeaways under STRENGTHS/CONCERNS name the indicator,
the value, the national figure and the rank — nothing else.
"""

from __future__ import annotations

import html as _html

from .data import DOMAIN_LABEL, Profile, Row, _fmt_unit


def _esc(s: str) -> str:
    return _html.escape(str(s))


def _fmt(v: float, unit: str) -> str:
    return f"{v:,.1f}" if unit == "rate_1000" else f"{v:,.1f}%"


def _direction_word(r: Row) -> str:
    if r.delta is None:
        return ""
    bad = (r.delta > 0) == r.worse_high
    return "worse than" if bad else "better than"


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def _takeaway(r: Row) -> str:
    """Deliberately doesn't restate r.label — the card title already shows it
    right above this sentence; repeating it read as a template stutter."""
    word = _direction_word(r)
    rank_txt = f", {_ordinal(r.rank)} of {r.n_ranked} states" if r.rank else ""
    return (f"{_fmt(r.value, r.unit)}, {abs(r.delta):.1f} pts {word} the national "
           f"{_fmt(r.national, r.unit)}{rank_txt}.")


def _row_html(r: Row) -> str:
    delta_cls = ""
    delta_txt = "—"
    if r.delta is not None:
        bad = (r.delta > 0) == r.worse_high
        delta_cls = "bad" if bad else "good"
        sign = "+" if r.delta > 0 else ""
        delta_txt = f"{sign}{r.delta:.1f}"
    rank_txt = f"{_ordinal(r.rank)} / {r.n_ranked}" if r.rank else "—"
    ci = f"{r.ci_low:,.1f}–{r.ci_high:,.1f}"
    natl = _fmt(r.national, r.unit) if r.national is not None else "—"
    return f"""
    <tr>
      <td class="ind">{_esc(r.label)}</td>
      <td class="tnum val">{_fmt(r.value, r.unit)}</td>
      <td class="tnum ci">{ci}</td>
      <td class="tnum natl">{natl}</td>
      <td class="tnum delta {delta_cls}">{delta_txt}</td>
      <td class="tnum rank">{rank_txt}</td>
      <td class="src mono">{_esc(r.psi_method)}</td>
    </tr>"""


def _domain_section(domain: str, rows: list[Row]) -> str:
    label = DOMAIN_LABEL.get(domain, domain.replace("_", " ").title())
    body = "".join(_row_html(r) for r in rows)
    return f"""
  <section class="domain">
    <h2>{_esc(label)}</h2>
    <div class="twrap"><table>
      <thead><tr>
        <th>Indicator</th><th>State</th><th>95% interval</th><th>National</th>
        <th>Δ vs national</th><th>Rank</th><th>Basis</th>
      </tr></thead>
      <tbody>{body}</tbody>
    </table></div>
  </section>"""


def _headline_card(r: Row, kind: str) -> str:
    return f"""
    <div class="card {kind}">
      <div class="k">{_esc(DOMAIN_LABEL.get(r.domain, r.domain))}</div>
      <div class="v">{_esc(r.label)}</div>
      <div class="t">{_takeaway(r)}</div>
    </div>"""


def _parts(p: Profile) -> tuple[str, str]:
    """(head_html, body_html) — split at the actual </head><body> seam, not
    guessed from string position, so render() and render_artifact() can each
    wrap them correctly: render() needs a real <body> tag inserted between
    the two; render_artifact() needs neither (the Artifact tool supplies
    its own doctype/html/head/body, charset and viewport)."""
    headline = "".join(_headline_card(r, "concern") for r in p.concerns) + \
              "".join(_headline_card(r, "strength") for r in p.strengths)
    sections = "".join(_domain_section(d, rows) for d, rows in p.by_domain.items())
    src_rows = "".join(
        f'<div class="s"><b>{_esc(s.get("provider",""))}</b> — {_esc(s.get("title",""))}'
        f'<br><span class="mono">{_esc(s.get("licence",""))}</span></div>'
        for s in p.sources)
    pop_m = p.population / 1e6

    head = f"""<title>{_esc(p.state_name)} Health Profile</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{{
  color-scheme: light;
  --ground:#F7F5F0; --surface:#FFFFFF; --sunk:#EFEBE1;
  --ink:#201C16; --muted:#5B564C; --faint:#8C8778;
  --line:#DDD6C4; --line-strong:#C7BEA4;
  --accent:#2B6E5C; --accent-ink:#1E4D40;
  --good:#2B6E5C; --bad:#A2432B;
  --shadow:0 1px 2px rgba(32,28,22,.05), 0 10px 30px rgba(32,28,22,.05);
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    color-scheme: dark;
    --ground:#17140F; --surface:#1E1A14; --sunk:#141110;
    --ink:#EDE8DC; --muted:#A8A192; --faint:#736C5C;
    --line:#332D22; --line-strong:#453E2E;
    --accent:#5FBFA1; --accent-ink:#8FDCC3;
    --good:#5FBFA1; --bad:#E08D71;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px rgba(0,0,0,.35);
  }}
}}
:root[data-theme="dark"]{{
  color-scheme: dark;
  --ground:#17140F; --surface:#1E1A14; --sunk:#141110;
  --ink:#EDE8DC; --muted:#A8A192; --faint:#736C5C;
  --line:#332D22; --line-strong:#453E2E;
  --accent:#5FBFA1; --accent-ink:#8FDCC3;
  --good:#5FBFA1; --bad:#E08D71;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px rgba(0,0,0,.35);
}}
*{{box-sizing:border-box}}
body{{margin:0; background:var(--ground); color:var(--ink);
  font-family:"Inter",ui-sans-serif,system-ui,sans-serif; font-size:15.5px; line-height:1.55;
  -webkit-font-smoothing:antialiased;}}
.serif{{font-family:"Source Serif 4",Georgia,serif}}
.mono{{font-family:"JetBrains Mono",ui-monospace,monospace}}
.tnum{{font-variant-numeric:tabular-nums}}
.page{{max-width:920px; margin:0 auto; padding:56px 28px 80px}}

.masthead{{display:flex; justify-content:space-between; align-items:baseline;
  border-bottom:2px solid var(--ink); padding-bottom:14px; margin-bottom:36px}}
.masthead .mark{{font-weight:700; font-size:15px; letter-spacing:.22em}}
.masthead .lbl{{font-family:"JetBrains Mono"; font-size:11.5px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--muted)}}

.title h1{{font-size:44px; margin:0 0 6px; font-weight:600; letter-spacing:-.01em}}
.title .meta{{font-family:"JetBrains Mono"; font-size:13px; color:var(--muted); letter-spacing:.01em}}
.title .meta b{{color:var(--ink); font-weight:500}}
.title{{margin-bottom:34px}}

.headline{{display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1px;
  background:var(--line); border:1px solid var(--line); margin-bottom:44px}}
.card{{background:var(--surface); padding:16px 18px; border-top:3px solid var(--line-strong)}}
.card.concern{{border-top-color:var(--bad)}}
.card.strength{{border-top-color:var(--good)}}
.card .k{{font-family:"JetBrains Mono"; font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--faint)}}
.card .v{{font-weight:600; font-size:16px; margin:4px 0 6px}}
.card .t{{font-size:13px; color:var(--muted); line-height:1.5}}

.domain{{margin-bottom:38px}}
.domain h2{{font-size:13px; letter-spacing:.1em; text-transform:uppercase; color:var(--accent-ink);
  font-weight:600; margin:0 0 10px; padding-bottom:8px; border-bottom:1px solid var(--line)}}
.twrap{{overflow-x:auto}}
table{{width:100%; border-collapse:collapse; font-size:13.5px}}
th{{text-align:left; font-family:"JetBrains Mono"; font-size:10.5px; letter-spacing:.06em;
  text-transform:uppercase; color:var(--faint); font-weight:500; padding:6px 10px; white-space:nowrap}}
th:not(:first-child), td:not(:first-child){{text-align:right}}
td{{padding:9px 10px; border-top:1px solid var(--line); white-space:nowrap}}
td.ind{{white-space:normal; font-weight:500}}
td.ci, td.src{{color:var(--faint); font-size:12px}}
td.natl{{color:var(--muted)}}
td.delta.good{{color:var(--good)}}
td.delta.bad{{color:var(--bad)}}
tr:hover td{{background:var(--sunk)}}

.methods{{margin-top:54px; padding-top:22px; border-top:2px solid var(--ink)}}
.methods h3{{font-size:13px; letter-spacing:.1em; text-transform:uppercase; margin:0 0 10px}}
.methods p{{font-size:13px; color:var(--muted); max-width:760px; margin:0 0 10px}}
.methods .s{{font-size:12.5px; color:var(--muted); margin-top:8px}}
.methods .s .mono{{color:var(--faint); font-size:11.5px}}

@media print{{
  body{{background:#fff}}
  .page{{max-width:none; padding:0 8mm}}
  .card, table{{box-shadow:none}}
}}
</style>"""

    body = f"""<div class="page">
  <div class="masthead">
    <span class="mark">ÀLÁÁFÌA</span>
    <span class="lbl">State health profile · {_esc(p.survey_id)} · built {_esc(p.built)}</span>
  </div>

  <div class="title">
    <h1 class="serif">{_esc(p.state_name)}</h1>
    <div class="meta">
      <span class="mono">{_esc(p.state_pcode)}</span> ·
      population <b>{pop_m:,.1f}M</b> (WorldPop 2020) ·
      area <b>{p.area_km2:,.0f} km²</b> ·
      {len(p.rows)} indicators modelled
    </div>
  </div>

  <div class="headline">{headline}</div>

  {sections}

  <div class="methods">
    <h3>How to read this</h3>
    <p>Every figure is the state's own {_esc(p.survey_id)} survey estimate, shrunk toward a
    regression on geography in proportion to how noisy that state's own sample is
    (Fay&ndash;Herriot small-area estimation) &mdash; not the raw survey number, and not a
    guess. <b>Basis</b> says whether the margin of error came from the survey's own
    published confidence interval (<span class="mono">api_ci</span>) or an approximation
    (<span class="mono">deff_approx</span>) where it didn't publish one. <b>Rank</b> is
    among the other states this indicator could be fitted for that round &mdash; 1st is
    always the best outcome, regardless of whether that means the highest or lowest
    number. Full method, every documented approximation, and the LGA-level breakdown
    (synthetic, not locally measured) are in the estimates explorer and
    <span class="mono">platform/model/README.md</span>.</p>
    {src_rows}
  </div>
</div>"""
    return head, body


def render(p: Profile) -> str:
    """The full standalone document — open it directly, email it, host it
    anywhere. This is the actual deliverable."""
    head, body = _parts(p)
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{head}
</head><body>
{body}
</body></html>"""


def render_artifact(p: Profile) -> str:
    """head + body content only, no wrapping tags — for the Artifact tool,
    which supplies its own doctype/html/head/charset/viewport/body and
    wraps whatever it's given. Only for
    previewing/sharing a link; the file in build/ is the real deliverable."""
    head, body = _parts(p)
    return f"{head}\n{body}"
