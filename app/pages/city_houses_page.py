import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from data_loaders import CityHousesLoader
import plotly.graph_objects as go

from data_loaders import HousesParameters as house_params
from .base_houses_prices_page import BaseHousesPricesPage

class CityHousesKeys():
    CITY_DROPDOWN = "CITY_DROPDOWN"
    GRAPH = "GRAPH"
    OFFER_LINK = "OFFER_LINK"
    AREA_SLIDER = "AREA_SLIDER"
    DATE_PICKER = "DATE_PICKER"
    PRICE_FROM = "PRICE_FROM"
    PRICE_TO = "PRICE_TO"

class CityHousesPage(BaseHousesPricesPage):
    data_loader = CityHousesLoader()
    KEYS = CityHousesKeys()
    
    @classmethod
    def register_callbacks(cls, app):
        @app.callback(
            Output(cls.KEYS.GRAPH, "figure"),
            [Input(cls.KEYS.DATE_PICKER, "start_date"),
            Input(cls.KEYS.DATE_PICKER, "end_date"),
            Input(cls.KEYS.CITY_DROPDOWN, "value"),
            Input(cls.KEYS.PRICE_FROM, "value"),
            Input(cls.KEYS.PRICE_TO, "value"),
            Input(cls.KEYS.AREA_SLIDER, "value"),
            ],
        )
        def callback_update_figure(start_date, end_date, city_value, price_from, price_to, area):
            cls._update_param(house_params.START_DATE, start_date)
            cls._update_param(house_params.END_DATE, end_date)
            cls._update_param(house_params.CITY, city_value)
            cls._update_param(house_params.PRICE_FROM, price_from)
            cls._update_param(house_params.PRICE_TO, price_to)
            areas = cls._get_areas_options()
            cls._update_param(house_params.AREA, [areas[area[0]], areas[area[1]]])

            return cls._get_houses_price_graph()
        
        @app.callback(
            Output(cls.KEYS.OFFER_LINK, 'href'),
            Input(cls.KEYS.GRAPH, 'clickData'))
        def display_click_data(clickData):
            if clickData:
                return clickData["points"][0].get("text")

    @classmethod
    def _get_houses_price_graph(cls):
        data = cls.dataframe.get("plain")
        return cls._make_bar(
            data, "<b>City house offers with their prices</b>"
        )

    @classmethod
    def _make_bar(cls, data, title):
        color = {'Aftermarket': 'pink', 'Primary market': 'deeppink'}
        data["index"] = list(range(len(data)))
        fig = go.Figure()
        for lbl in data['market'].unique():
            dfp = data[data['market']==lbl]
            fig.add_traces(go.Bar(x=dfp["index"], y=dfp['price'], name=lbl,
                                    marker = dict(color=color[lbl]), customdata=data["name"], text=data["website"]
                                    ))

        fig.update_traces(
            marker_line_width=0,
            hovertemplate='Name:%{customdata}<br>%{x}<br>Price:%{y}<br>www: %{text} <extra></extra>',
            showlegend=True,
        )
        fig.update_layout(
            clickmode='event+select',
            title_text=title,
            title_font = dict(
                size = 20,
                color = "rgb(101, 102, 148)",

            ),
            font_color="rgb(82, 83, 130)",
            
            plot_bgcolor ="rgba(0, 0, 0, 0)", 
            paper_bgcolor = "rgba(0, 0, 0, 0)",
            xaxis=dict(
                title="House offer",
                showticklabels=True,
                tickvals=data["index"],
                ticktext=data["datetime"],
                ticklen=20,
                dtick = 1,
                ticks="inside",
                tickfont=dict(color='crimson', size=6)
            ),
            yaxis=dict(
                title="Offer price",
                showgrid = False,
                zeroline=False,

            ),
        )
        return fig
        
