from itertools import zip_longest
import webbrowser  
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from data_loaders.city_houses_loader import CityHousesLoader
import plotly.graph_objects as go

from .base_page import BasePage

class CityHousesPage(BasePage):
    data_loader = CityHousesLoader()

    @classmethod
    def layout(cls, params={}):
        cities = cls._get_cities_options()
        city_value = cls._get_option_by_name(cities, "Poznań").get("value")
        prices_to = cls._get_prices_options(greater_than=False)
        prices_from = cls._get_prices_options(greater_than=True)
        return html.Div(
            [
                html.Div(
                    dcc.Dropdown(
                        id='city_dropdown', options=cities, value=[city_value], multi=True, className='chart-dropdown'
                    ), className='row-inputs-container-left'
                ),
                html.Div(
                    [
                    dcc.Graph(
                        id="data-price-offer", figure=cls._get_data_price_offer_graph(cls.dataframe.get("date_sorted")), className='chart-chart'
                    ),
                    html.Div([html.A('', target='_blank', id='on-click-graph-data', href=''),], className="offer-textholder"),
                    ], className='chart-container'
                ),

                html.Div(
                    [
                        html.Div(
                            dcc.DatePickerRange( id='date-picker-range', **cls._get_date_picker_data(), className='chart-datepicker', ),
            
                        ),
                        html.Div(
                            dcc.Dropdown(id='price_from_dropdown', options=prices_from, value=prices_from[0].get("value"), className='chart-dropdown'),
                          
                        ),
                        html.Div(
                            dcc.Dropdown(id='price_to_dropdown', options=prices_to, value=prices_to[-1].get("value"), className='chart-dropdown' ),
                          
                        ),
                    ],className='row-inputs-container'),
            
            ], className='page-container')

    @classmethod
    def register_callbacks(cls, app):
        @app.callback(
            Output("data-price-offer", "figure"),
            [Input("date-picker-range", "start_date"),
            Input("date-picker-range", "end_date"),
            Input("city_dropdown", "value"),
            Input("price_from_dropdown", "value"),
            Input("price_to_dropdown", "value")],
        )
        def callback_update_figure(start_date, end_date, city_value, price_from, price_to):
            cls._update_param("start_date", start_date)
            cls._update_param("end_date", end_date)
            cls._update_param("city", city_value)
            cls._update_param("price_from", price_from)
            cls._update_param("price_to", price_to)
            return cls._get_data_price_offer_graph(cls.dataframe.get("date_sorted"))
        
        @app.callback(
            Output('on-click-graph-data', 'href'),
            Input('data-price-offer', 'clickData'))
        def display_click_data(clickData):
            if clickData:
                print(clickData["points"][0].get("text"))
                webbrowser.open_new(clickData["points"][0].get("text"))
                return clickData["points"][0].get("text")

    @classmethod
    def _get_date_picker_data(cls):
        meta = cls.data_loader.get_metadata()
        return {
            "min_date_allowed": meta.get("min_date"),
            "max_date_allowed": meta.get("max_date"),
            "start_date": meta.get("start_date"),
            "end_date": meta.get("max_date")
        }
    
    @classmethod
    def _get_dict_format(cls, objects):
        return [{'label': x, 'value': x} for x in objects]

    @classmethod
    def _get_price_dict_format(cls, objects, sign='<'):
        return [{'label': f'{sign} {x} zł', 'value': x} for x in objects]

    @classmethod
    def _get_cities_options(cls):
        cities = cls.data_loader.get_metadata().get("available_cities")
        return cls._get_dict_format(cities)

    @classmethod
    def _get_prices_options(cls, greater_than=True):
        prices = list(range(0,1100000,100000))
        sign = ">" if greater_than else "<"
        return cls._get_price_dict_format(prices, sign)

    @classmethod
    def _get_option_by_name(cls, options, name):
        return list(filter(lambda opt: opt['label'] == name, options))[0]

    @classmethod
    def _get_data_price_offer_graph(cls, data):
        return cls._make_scatter(
            data, "<b>City house offers with their prices</b>"
        )

    @classmethod
    def _make_scatter(cls, data, title):
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
        
