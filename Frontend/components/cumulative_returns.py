import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts, JsCode


def cumulative_returns(portfolio_df: pd.DataFrame):
    if portfolio_df is None or portfolio_df.empty:
        st.warning("No portfolio data available.")
        return

    if "date" not in portfolio_df.columns or "cum_return" not in portfolio_df.columns:
        st.error(
            f"portfolio_df must contain 'date' and 'cum_return'. "
            f"Columns: {list(portfolio_df.columns)}"
        )
        return

    df = portfolio_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["cum_return"] = pd.to_numeric(df["cum_return"], errors="coerce")
    df = df.dropna(subset=["date", "cum_return"]).sort_values("date")

    if df.empty:
        st.warning("No valid data for cumulative returns.")
        return

    dates = df["date"].dt.strftime("%Y-%m-%d").tolist()
    values = (df["cum_return"] * 100).tolist()

    plot_dates = [dates[0]]
    plot_values = [values[0]]

    for i in range(1, len(values)):
        prev_val = values[i - 1]
        curr_val = values[i]

        if prev_val * curr_val < 0:
            plot_dates.append(f"{dates[i]}_zero")
            plot_values.append(0)

        plot_dates.append(dates[i])
        plot_values.append(curr_val)

    positive_values = [max(v, 0) for v in plot_values]
    negative_values = [min(v, 0) for v in plot_values]

    series_data = [{"value": v, "symbolSize": 16} for v in values]

    chart_min = min(values)
    chart_max = max(values)
    padding = (chart_max - chart_min) * 0.1 if chart_max > chart_min else max(abs(chart_max) * 0.1, 1)

    chart_option = {
        "title": {"text": "Cumulative Returns", "left": "center"},
        "tooltip": {"show": False},
        "legend": {"data": ["Cummulative Return"], "top": 40},
        "grid": {"top": 80},
        "toolbox": {
            "feature": {
                "saveAsImage": {},
                "dataView": {"readOnly": True},
                "restore": {},
                "dataZoom": {}
            }
        },
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": plot_dates,
            "axisLabel": {
                "formatter": JsCode(
                    """
                    function (value) {
                        if (value.endsWith('_zero')) return '';
                        return value.slice(0, 7);
                    }
                    """
                )
            }
        },
        "yAxis": [{
            "type": "value",
            "name": "Return (%)",
            "min": chart_min - padding,
            "max": chart_max + padding,
            "axisLabel": {
                "formatter": JsCode(
                    "function(value) { return value.toFixed(2) + '%'; }"
                )
            }
        }],
        "dataZoom": [{"type": "inside"}, {"type": "slider"}],
        "series": [
            {
                "name": "Positive Area",
                "type": "line",
                "data": positive_values,
                "symbol": "none",
                "lineStyle": {"opacity": 0},
                "areaStyle": {
                    "color": "#00C853",
                    "opacity": 0.45
                },
                "z": 1
            },
            {
                "name": "Negative Area",
                "type": "line",
                "data": negative_values,
                "symbol": "none",
                "lineStyle": {"opacity": 0},
                "areaStyle": {
                    "color": "#FF1744",
                    "opacity": 0.45
                },
                "z": 1
            },
            {
                "name": "Cumulative Return",
                "type": "line",
                "symbol": "circle",
                "symbolSize": JsCode(
                    """
                    function (value, params) {
                        return params.name.endsWith('_zero') ? 0 : 10;
                    }
                    """
                ),
                "data": plot_values,
                "lineStyle": {
                    "width": 2,
                    "color": "#7EC8FF"
                },
                "itemStyle": {
                    "color": "#7EC8FF",
                    "borderColor": "#7EC8FF"
                },
                "z": 3
            }
        ]
    }

    st_echarts(chart_option, height="500px", key="cumulative_returns_chart")