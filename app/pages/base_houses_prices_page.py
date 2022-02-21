import dash_core_components as dcc
import dash_html_components as html

from .base_page import BasePage


class BaseHousesPricesPage(BasePage):
    """Base House Price Page that privides basic html layout for house data"""

    KEYS = None

    @classmethod
    def layout(cls, params=None) -> html:
        return html.Div(
            [
                cls._render_cities_dropdown("row-inputs-container-left"),
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
    def _render_cities_dropdown(cls, class_name):
        cities = cls._get_cities_options()
        city_value = cls._get_option_by_name(cities, "Poznań").get("value")
        return html.Div(
            dcc.Dropdown(
                id=cls.KEYS.CITY_DROPDOWN, options=cities, value=[city_value], multi=True, className="chart-dropdown"
            ),
            className=class_name,
        )

    @classmethod
    def _render_data_graph(cls, class_name):
        return html.Div(
            [
                dcc.Graph(id=cls.KEYS.GRAPH, figure=cls._get_houses_price_graph(), className="chart-chart"),
                html.Div(
                    [
                        html.A("", target="_blank", id=cls.KEYS.OFFER_LINK, href=""),
                    ],
                    className="offer-textholder",
                ),
            ],
            className=class_name,
        )

    @classmethod
    def _render_area_range_slider(cls, class_name):
        areas = cls._get_areas_options()
        min_area = min([area for area in areas.keys()])
        max_area = max([area for area in areas.keys()])
        return html.Div(
            [
                html.Label("Area size m²", className="slider-label"),
                dcc.RangeSlider(
                    id=cls.KEYS.AREA_SLIDER,
                    marks=areas,
                    min=min_area,
                    max=max_area,
                    value=[0, int(len(areas) / 2)],
                    className="slider",
                    step=None,
                ),
            ],
            className=class_name,
        )

    @classmethod
    def _render_date_picker_range(cls, class_name):
        return html.Div(
            dcc.DatePickerRange(id=cls.KEYS.DATE_PICKER, **cls._get_date_picker_data(), className=class_name),
        )

    @classmethod
    def _render_price_from_dropdown(cls, class_name):
        prices_from = cls._get_prices_options(greater_than=True)
        return html.Div(
            dcc.Dropdown(
                id=cls.KEYS.PRICE_FROM, options=prices_from, value=prices_from[0].get("value"), className=class_name
            ),
        )

    @classmethod
    def _render_price_to_dropdown(cls, class_name):
        prices_to = cls._get_prices_options(greater_than=False)
        return html.Div(
            dcc.Dropdown(
                id=cls.KEYS.PRICE_TO, options=prices_to, value=prices_to[-1].get("value"), className=class_name
            ),
        )

    @classmethod
    def _get_date_picker_data(cls):
        meta = cls.data_loader.get_metadata()
        return {
            "min_date_allowed": meta.get("min_date"),
            "max_date_allowed": meta.get("max_date"),
            "start_date": meta.get("start_date"),
            "end_date": meta.get("max_date"),
        }

    @classmethod
    def _get_dict_format(cls, objects):
        return [{"label": x, "value": x} for x in objects]

    @classmethod
    def _get_price_dict_format(cls, objects, sign="<"):
        return [{"label": f"{sign} {x} zł", "value": x} for x in objects]

    @classmethod
    def _get_cities_options(cls):
        cities = cls.data_loader.get_metadata().get("available_cities")
        return cls._get_dict_format(cities)

    @classmethod
    def _get_prices_options(cls, greater_than=True):
        prices = list(range(0, 1100000, 100000))
        sign = ">" if greater_than else "<"
        return cls._get_price_dict_format(prices, sign)

    @classmethod
    def _get_areas_options(cls):
        areas = cls.data_loader.get_metadata().get("areas")
        areas = [area for area in areas if area]
        small_areas = list(range(int(min(areas)), 100, 10))
        large_areas = list(range(100, int(max(areas)), 1000))
        all_areas = small_areas + large_areas
        return {i: str(all_areas[i]) for i in range(0, len(all_areas) - 1)}

    @classmethod
    def _get_option_by_name(cls, options, name):
        return list(filter(lambda opt: opt["label"] == name, options))[0]
