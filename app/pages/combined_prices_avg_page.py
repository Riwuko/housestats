import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from data_loaders import AverageHousesPricesLoader
from data_loaders import AveragePricesParameters as avg_params
from data_loaders import CityHousesLoader
from plotly import graph_objects as go

from .base_houses_prices_page import BaseHousesPricesPage


class CombinedPricesAveragesPricesKeys:
    CITY_DROPDOWN = "COMB_CITY_DROPDOWN"
    GRAPH = "COMB_GRAPH"
    OFFER_LINK = "COMB_OFFER_LINK"
    AREA_SLIDER = "COMB_AREA_SLIDER"
    PRICE_FROM = "COMB_PRICE_FROM"
    PRICE_TO = "COMB_PRICE_TO"
    GROUP_AVG_RADIO = "COMB_GROUP_AVG_RADIO"
    OFFER_LINK = "COMB_OFFER_LINK"
    DATE_PICKER = "COMB_DATE_PICKER"


class CombinedPricesAveragesPage(BaseHousesPricesPage):
    data_loader = CityHousesLoader()
    avg_data_loader = AverageHousesPricesLoader()
    KEYS = CombinedPricesAveragesPricesKeys()
    avg_params = {}

    @classmethod
    def load_data(cls):
        cls.dataframe = cls.data_loader.load_data(cls.params)
        cls.avg_dataframe = cls.avg_data_loader.load_data(cls.avg_params)

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
                        cls._render_date_picker_range("chart-datepicker"),
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
                Input(cls.KEYS.DATE_PICKER, "start_date"),
                Input(cls.KEYS.DATE_PICKER, "end_date"),
                Input(cls.KEYS.CITY_DROPDOWN, "value"),
                Input(cls.KEYS.PRICE_FROM, "value"),
                Input(cls.KEYS.PRICE_TO, "value"),
                Input(cls.KEYS.AREA_SLIDER, "value"),
                Input(cls.KEYS.GROUP_AVG_RADIO, "value"),
            ],
        )
        def callback_update_figure(start_date, end_date, city_value, price_from, price_to, area, avg_group_by):
            cls._update_param(avg_params.START_DATE, start_date)
            cls._update_param(avg_params.END_DATE, end_date)
            cls._update_param(avg_params.CITY, city_value)
            cls._update_param(avg_params.PRICE_FROM, price_from)
            cls._update_param(avg_params.PRICE_TO, price_to)
            areas = cls._get_areas_options()
            cls._update_param(avg_params.AREA, [areas[area[0]], areas[area[1]]])
            cls._update_avg_param(avg_params.AVG_GROUP_BY, avg_group_by)
            return cls._get_houses_price_graph()

    @classmethod
    def _update_param(cls, name, value):
        cls.params[name] = value
        cls.avg_params[name] = value
        cls.load_data()

    @classmethod
    def _update_avg_param(cls, name, value):
        cls.avg_params[name] = value
        cls.load_data()

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
        title = "<b>House offers prices and average prices in selected cities</b>"
        data = {
            "Primary market": cls.avg_dataframe.get("primary_market_data"),
            "Aftermarket": cls.avg_dataframe.get("aftermarket_data"),
        }
        bar_data = cls.dataframe.get("plain")
        traces0 = cls._make_bar(bar_data)
        traces1 = cls._make_scatter(data)
        fig = go.Figure(data=[*traces0, *traces1])
        full_price = set()
        fig.for_each_trace(
            lambda trace: trace.update(showlegend=False)
            if (trace.name in full_price and trace.name == "Full price")
            else full_price.add(trace.name)
        )
        fig.update_layout(
            legend=dict(x=1.05, font=dict(size=10)),
            clickmode="event+select",
            title=title,
            title_font=dict(
                size=20,
                color="rgb(101, 102, 148)",
            ),
            font_color="rgb(82, 83, 130)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            yaxis=dict(
                title="<br>Price per m²",
                showgrid=False,
                zeroline=False,
            ),
            yaxis2=dict(
                title="Offer full price", showgrid=False, zeroline=False, anchor="x", overlaying="y", side="right"
            ),
            xaxis2=dict(
                showgrid=False,
                zeroline=False,
            ),
            xaxis=dict(
                title="<br>House offer by date",
                showticklabels=False,
                tickvals=bar_data["index"],
                ticktext=bar_data["datetime"],
            ),
        )
        return fig

    @classmethod
    def _make_scatter(cls, data):
        line_color = {"Aftermarket": "white", "Primary market": "white"}
        color = {"Aftermarket": "pink", "Primary market": "deeppink"}

        traces = []
        for label, market in data.items():
            traces.append(
                go.Scatter(
                    x=market.datetime,
                    y=market.price_mk,
                    mode="lines+markers",
                    marker=dict(
                        color=color[label],
                        size=20,
                        line=dict(
                            color=line_color[label],
                            width=3,
                        ),
                    ),
                    line=dict(
                        color=line_color[label],
                        width=1.5,
                    ),
                    hoveron="points",
                    hovertemplate="Date: %{x}<br>Avg price:%{y}<br><extra></extra>",
                    name=f"{label} avg m² price",
                    xaxis="x2",
                    legendgroup="avg_price_mk",
                    legendgrouptitle_text="Average price per m²",
                )
            )

        return traces

    @classmethod
    def _make_bar(cls, data):
        color = {"Aftermarket": "pink", "Primary market": "deeppink"}

        traces = []
        data["index"] = list(range(len(data)))
        for lbl in data["market"].unique():
            dfp = data[data["market"] == lbl]
            traces.append(
                go.Bar(
                    x=dfp["index"],
                    y=dfp["price_mk"],
                    name=f"{lbl} price per m²",
                    legendgroup="price_mk",
                    legendgrouptitle_text="Price per m²",
                    marker=dict(color=color[lbl]),
                    customdata=data["name"],
                    text=data["website"],
                    marker_line_width=0,
                    hovertemplate="Name:%{customdata}<br>%{x}<br>Price per meter:%{y}<br>www: %{text} <extra></extra>",
                )
            )
            traces.append(
                go.Bar(
                    x=dfp["index"],
                    y=dfp["price"],
                    name="Full price",
                    yaxis="y2",
                    legendgroup="full_price",
                    legendgrouptitle_text="Full price",
                    marker=dict(color="rgba(175, 69, 204, 0.3)"),
                    customdata=data["name"],
                    text=data["website"],
                    marker_line_width=0,
                    hovertemplate="Name:%{customdata}<br>%{x}<br>Price:%{y}<br>www: %{text} <extra></extra>",
                )
            )

        return traces
