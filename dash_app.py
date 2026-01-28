
from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.express as px
from main import Dash, Input, Output, dcc, html

PRICE_INCREASE_DATE = datetime(2021, 1, 15)

DATA_PATHS = [
    "data/pink_morsels_sales.csv",
    "data/pink_morsels_sales.csv",
    "data/pink_morsels_sales.csv",
]

def load_data() -> pd.DataFrame:
    last_error = None
    for p in DATA_PATHS:
        try:
            df = pd.read_csv(p)
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
            df["Region"] = df["Region"].astype(str).str.strip()
            df = df.dropna(subset=["Date", "Sales", "Region"])
            return df
        except Exception as e:
            last_error = e
    raise FileNotFoundError(
        "Could not find pink_morsels_sales.csv. Tried: "
        + ", ".join(DATA_PATHS)
        + f" | last error: {last_error}"
    )

df = load_data()
regions = sorted(df["Region"].unique().tolist())

app = Dash(__name__)
app.title = "Soul Foods — Pink Morsels Sales Visualiser"

app.layout = html.Div(
    style={"maxWidth": "1100px", "margin": "0 auto", "padding": "20px"},
    children=[
        html.H1("Soul Foods — Pink Morsels Sales Visualiser"),
        html.P(
            "Question: Were sales higher before or after the Pink Morsel price increase on 15 Jan 2021?"
        ),
        html.Div(
            style={"maxWidth": "520px"},
            children=[
                html.Label("Filter by region"),
                dcc.Dropdown(
                    id="region",
                    options=[{"label": "All regions", "value": "__ALL__"}]
                    + [{"label": r.title(), "value": r} for r in regions],
                    value="__ALL__",
                    clearable=False,
                ),
            ],
        ),
        html.Div(id="summary", style={"marginTop": "14px", "fontSize": "16px"}),
        dcc.Graph(id="sales_line", style={"marginTop": "10px"}),
    ],
)

@app.callback(
    Output("sales_line", "figure"),
    Output("summary", "children"),
    Input("region", "value"),
)
def update(region_value: str):
    dff = df.copy()
    if region_value != "__ALL__":
        dff = dff[dff["Region"] == region_value]

    series = (
        dff.groupby("Date", as_index=False)["Sales"]
        .sum()
        .sort_values("Date")
    )

    fig = px.line(
        series,
        x="Date",
        y="Sales",
        labels={"Date": "Date", "Sales": "Sales (€)"},
        title="Pink Morsels — Daily Sales Over Time",
    )

    fig.add_vline(
        x=PRICE_INCREASE_DATE,
        line_width=2,
        line_dash="dash",
        annotation_text="Price increase (15 Jan 2021)",
        annotation_position="top left",
    )

    before = series[series["Date"] < PRICE_INCREASE_DATE]["Sales"].sum()
    after = series[series["Date"] >= PRICE_INCREASE_DATE]["Sales"].sum()

    which = "after" if after > before else "before"
    summary = html.Div(
        [
            html.Strong("Total sales comparison: "),
            html.Span(
                f"Before 15 Jan 2021 = €{before:,.2f} | "
                f"On/After 15 Jan 2021 = €{after:,.2f}  → Higher {which}."
            ),
        ]
    )

    return fig, summary

if __name__ == "__main__":
    app.run_server(debug=True)
