python
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

PRICE_INCREASE_DATE = pd.Timestamp("2021-01-15")

DATA_CANDIDATES = [
    Path("data") / "pink_morsels_sales.csv",
    Path("pink_morsels_sales.csv"),
]

REGION_OPTIONS = ["all", "north", "east", "south", "west"]

def load_sales() -> pd.DataFrame:
    last_err = None
    for p in DATA_CANDIDATES:
        try:
            df = pd.read_csv(p)
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
            df["Region"] = df["Region"].astype(str).str.strip().str.lower()
            df = df.dropna(subset=["Date", "Sales", "Region"])
            return df
        except Exception as e:
            last_err = e
    raise FileNotFoundError(
        "Could not find pink_morsels_sales.csv. Tried: "
        + ", ".join(str(x) for x in DATA_CANDIDATES)
        + f" | last error: {last_err}"
    )

df = load_sales()

app = Dash(__name__)
app.title = "Soul Foods — Pink Morsels Sales Visualiser"

app.layout = html.Div(
    className="page",
    children=[
        html.Div(
            className="header",
            children=[
                html.Div(
                    className="header__text",
                    children=[
                        html.H1("Soul Foods — Pink Morsels Sales Visualiser", className="title"),
                        html.P(
                            "Filter by region to see whether sales were higher before or after the price increase on 15 Jan 2021.",
                            className="subtitle",
                        ),
                    ],
                ),
                html.Div(
                    className="badge",
                    children=[
                        html.Div("Marker Date"),
                        html.Div("15 Jan 2021", className="badge__date"),
                    ],
                ),
            ],
        ),
        html.Div(
            className="grid",
            children=[
                html.Div(
                    className="card controls",
                    children=[
                        html.Div(className="card__title", children="Region filter"),
                        dcc.RadioItems(
                            id="region",
                            options=[{"label": r.title(), "value": r} for r in REGION_OPTIONS],
                            value="all",
                            inline=True,
                            className="radio",
                            inputClassName="radio__input",
                            labelClassName="radio__label",
                        ),
                        html.Div(id="summary", className="summary"),
                    ],
                ),
                html.Div(
                    className="card chart",
                    children=[
                        html.Div(className="card__title", children="Daily Sales Trend"),
                        dcc.Graph(
                            id="sales_line",
                            className="graph",
                            config={"displayModeBar": True, "displaylogo": False},
                        ),
                        html.Div(
                            className="hint",
                            children='Tip: Use the region filter to compare patterns. “All” aggregates across regions.',
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="footer",
            children=[
                html.Div("“Make it so.” — Jean-Luc Picard"),
            ],
        ),
    ],
)

@app.callback(
    Output("sales_line", "figure"),
    Output("summary", "children"),
    Input("region", "value"),
)
def render(region_value: str):
    r = (region_value or "all").strip().lower()
    if r not in REGION_OPTIONS:
        r = "all"

    dff = df if r == "all" else df[df["Region"] == r]

    daily = (
        dff.groupby("Date", as_index=False)["Sales"]
        .sum()
        .sort_values("Date")
    )

    before_total = daily[daily["Date"] < PRICE_INCREASE_DATE]["Sales"].sum()
    after_total = daily[daily["Date"] >= PRICE_INCREASE_DATE]["Sales"].sum()
    higher = "AFTER" if after_total > before_total else "BEFORE"

    fig = px.line(
        daily,
        x="Date",
        y="Sales",
        labels={"Date": "Date", "Sales": "Sales"},
    )

    fig.update_layout(
        title="Pink Morsels — Sales Over Time",
        margin=dict(l=30, r=20, t=50, b=30),
        hovermode="x unified",
    )

    fig.add_shape(
        type="line",
        xref="x",
        yref="paper",
        x0=PRICE_INCREASE_DATE,
        x1=PRICE_INCREASE_DATE,
        y0=0,
        y1=1,
        line={"dash": "dash", "width": 2},
    )
    fig.add_annotation(
        x=PRICE_INCREASE_DATE,
        y=1,
        xref="x",
        yref="paper",
        text="Price increase (15 Jan 2021)",
        showarrow=False,
        yanchor="bottom",
        xanchor="left",
    )

    summary = (
        f"Region: {r.title()} | "
        f"Total before 15 Jan 2021: {before_total:,.2f} | "
        f"Total on/after 15 Jan 2021: {after_total:,.2f} → Higher {higher}"
    )

    return fig, summary

if __name__ == "__main__":
    app.run(debug=True)
\`\`\`

### `assets/styles.css`
\`\`\`css
:root{
  --bg1:#0b1220;
  --bg2:#101a33;
  --card:rgba(255,255,255,.06);
  --card2:rgba(255,255,255,.08);
  --text:#e9eefc;
  --muted:rgba(233,238,252,.72);
  --border:rgba(255,255,255,.12);
  --shadow: 0 10px 28px rgba(0,0,0,.35);
  --radius: 18px;
}

*{ box-sizing:border-box; }

body{
  margin:0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  color: var(--text);
  background:
    radial-gradient(900px 500px at 15% 10%, rgba(155,99,255,.35), transparent 60%),
    radial-gradient(900px 500px at 85% 20%, rgba(70,190,255,.28), transparent 60%),
    linear-gradient(160deg, var(--bg1), var(--bg2));
  min-height: 100vh;
}

.page{
  max-width: 1150px;
  margin: 0 auto;
  padding: 22px 18px 30px;
}

.header{
  display:flex;
  gap: 16px;
  align-items: stretch;
  justify-content: space-between;
  padding: 18px 18px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.04));
  box-shadow: var(--shadow);
}

.header__text{ flex: 1; min-width: 260px; }

.title{
  margin: 0 0 8px 0;
  font-size: 26px;
  letter-spacing: .2px;
}

.subtitle{
  margin: 0;
  color: var(--muted);
  line-height: 1.4;
}

.badge{
  min-width: 150px;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 12px 12px;
  background: rgba(255,255,255,.05);
  display:flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
}

.badge__date{
  font-weight: 700;
  font-size: 15px;
}

.grid{
  display:grid;
  grid-template-columns: 1fr 2fr;
  gap: 16px;
  margin-top: 16px;
}

.card{
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: linear-gradient(180deg, var(--card), rgba(255,255,255,.03));
  box-shadow: var(--shadow);
  padding: 16px;
}

.card__title{
  font-weight: 700;
  margin-bottom: 10px;
  letter-spacing: .2px;
}

.controls{
  display:flex;
  flex-direction: column;
  gap: 12px;
}

.summary{
  padding: 12px 12px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: rgba(0,0,0,.18);
  color: var(--text);
  line-height: 1.35;
}

.radio{
  display:flex;
  flex-wrap: wrap;
  gap: 10px;
}

.radio__label{
  display:flex;
  align-items:center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,.04);
  cursor: pointer;
  user-select: none;
  transition: transform .08s ease, background .15s ease, border-color .15s ease;
}

.radio__label:hover{
  transform: translateY(-1px);
  background: rgba(255,255,255,.07);
  border-color: rgba(255,255,255,.18);
}

.radio__input{
  transform: scale(1.05);
}

.chart .graph{
  width: 100%;
  height: 520px;
}

.hint{
  margin-top: 10px;
  color: var(--muted);
  font-size: 13px;
}

.footer{
  margin-top: 14px;
  text-align: center;
  color: rgba(233,238,252,.62);
  font-size: 13px;
}

@media (max-width: 980px){
  .grid{ grid-template-columns: 1fr; }
  .chart .graph{ height: 460px; }
}
