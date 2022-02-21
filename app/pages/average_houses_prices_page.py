import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from data_loaders import AverageHousesPricesLoader
from data_loaders import AveragePricesParameters as avg_params
from plotly import express as px
from plotly import graph_objects as go

from .base_houses_prices_page import BaseHousesPricesPage


class AverageHousesPricesKeys:
    CITY_DROPDOWN = "AVG_CITY_DROPDOWN"
    GRAPH = "AVG_GRAPH"
    OFFER_LINK = "AVG_OFFER_LINK"
    AREA_SLIDER = "AVG_AREA_SLIDER"
    PRICE_FROM = "AVG_PRICE_FROM"
    PRICE_TO = "AVG_PRICE_TO"
    GROUP_AVG_RADIO = "AVG_GROUP_AVG_RADIO"


class AverageHousesPricesPage(BaseHousesPricesPage):
    data_loader = AverageHousesPricesLoader()
    KEYS = AverageHousesPricesKeys()

    @classmethod
    def layout(cls, params={}):
        return html.Div(
            [
                cls._render_cities_dropdown("row-inputs-container-left"),
                cls._render_avg_radios("row-inputs-container-right"),
                cls._render_data_graph("chart-container"),
                cls._render_area_range_slider("row-inputs-container-range"),
                html.Div(
                    [
                        cls._render_price_from_dropdown("chart-dropdown"),
                        cls._render_price_to_dropdown("chart-dropdown"),
                    ],
                    className="row-inputs-container",
                ),
            ],
            className="page-container",
        )

    @classmethod
    def register_callbacks(cls, app):
        @app.callback(
            Output(cls.KEYS.GRAPH, "figure"),
            [
                Input(cls.KEYS.CITY_DROPDOWN, "value"),
                Input(cls.KEYS.PRICE_FROM, "value"),
                Input(cls.KEYS.PRICE_TO, "value"),
                Input(cls.KEYS.AREA_SLIDER, "value"),
                Input(cls.KEYS.GROUP_AVG_RADIO, "value"),
            ],
        )
        def callback_update_figure(city_value, price_from, price_to, area, avg_group_by):
            cls._update_param(avg_params.CITY, city_value)
            cls._update_param(avg_params.PRICE_FROM, price_from)
            cls._update_param(avg_params.PRICE_TO, price_to)
            areas = cls._get_areas_options()
            cls._update_param(avg_params.AREA, [areas[area[0]], areas[area[1]]])
            cls._update_param(avg_params.AVG_GROUP_BY, avg_group_by)
            return cls._get_houses_price_graph()

    @classmethod
    def _render_avg_radios(cls, class_name):
        options = [avg_params.DAY, avg_params.WEEK, avg_params.MONTH, avg_params.YEAR]
        avg_group_options = [{"label": f"by {val}", "value": val} for val in options]
        return dcc.RadioItems(
            id=cls.KEYS.GROUP_AVG_RADIO,
            options=avg_group_options,
            value=options[0],
            className=class_name,
        )

    @classmethod
    def _get_houses_price_graph(cls):
        data = {
            "Primary market": cls.dataframe.get("primary_market_data"),
            "Aftermarket": cls.dataframe.get("aftermarket_data"),
        }
        return cls._make_scatter(data, "<b>Average houses prices in selected cities</b>")

    @classmethod
    def _make_scatter(cls, data, title):
        color = {"Aftermarket": "pink", "Primary market": "deeppink"}
        fill = {"Aftermarket": "rgba(100, 26, 161, 0.6)", "Primary market": "rgba(100, 26, 161, 1)"}
        fig = go.Figure()
        # fig = px.histogram(data["Aftermarket"], x="datetime", y="price_mk", histfunc="avg", title="Histogram on Date Axes")
        fig.update_traces(xbins=dict(size="D3"))  # bins used for histogram
        fig.update_xaxes(showgrid=True, ticklabelmode="period", dtick="D3", tickformat="%b\n%Y")

        for label, market in data.items():
            fig.add_traces(
                go.Scatter(
                    x=market.datetime,
                    y=market.price_mk,
                    mode="lines+markers",
                    marker=dict(
                        color=color[label],
                        size=8,
                    ),
                    line=dict(
                        color=color[label],
                        width=0.5,
                    ),
                    fillcolor=fill[label],
                    hoveron="points+fills",
                    fill="tozeroy",
                    name=label,
                )
            )

        fig.update_layout(bargap=0.1)
        datetimes = data["Aftermarket"].datetime
        fig.update_traces(
            # hoveron = 'points+fills',
            hovertemplate="Date: %{x}<br>Avg price:%{y}<br><extra></extra>",
        )
        fig.update_layout(
            clickmode="event+select",
            title_text=title,
            title_font=dict(
                size=20,
                color="rgb(101, 102, 148)",
            ),
            font_color="rgb(82, 83, 130)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            xaxis=dict(
                title="Date",
                showticklabels=True,
                tickvals=datetimes,
                ticktext=datetimes,
                showgrid=False,
                tickfont=dict(color="crimson", size=8),
                rangeslider=dict(thickness=0.1, visible=True),
                type="date",
                rangeselector=dict(
                    bgcolor="pink",
                    buttons=list(
                        [
                            dict(count=1, label="1d", step="day", stepmode="backward"),
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all"),
                        ]
                    ),
                ),
            ),
            yaxis=dict(
                title="Average price",
                showgrid=False,
                zeroline=False,
            ),
        )
        return fig
