from turtle import down

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from config import AppConfig, make_celery
from dash.dependencies import Input, Output
from db.models import db, migrate
from flask import Flask
from pages import AverageHousesPricesPage, CityHousesPage, CombinedPricesAveragesPage

app = Flask(__name__)
app.config.from_object(AppConfig)
app.app_context().push()
db.init_app(app)
migrate.init_app(app, db)
celery = make_celery(app)

db.create_all()
pathnames_pages = {
    "/": CombinedPricesAveragesPage,
    "/average-prices": AverageHousesPricesPage,
    "/offers-prices": CityHousesPage,
}

# meta_tags are required for the app layout to be mobile responsive
app_dash = dash.Dash(
    __name__,
    server=app,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

app_dash.layout = html.Div(
    [
        html.Div(className="app-header", children=[html.Div("houseStats |", className="app-header--title")]),
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content", children=[], className="app-content"),
    ]
)


@app_dash.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    try:
        page_class = pathnames_pages[pathname]
    except KeyError:
        return "404"
    page = page_class()
    page.load_data()

    return page.layout()


if __name__ == "__main__":
    for page_class in pathnames_pages.values():
        page_class.register_callbacks(app_dash)

    app_dash.run_server(host="0.0.0.0", port=8080, debug=True, threaded=True)
