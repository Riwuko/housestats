import dash
import dash_core_components as dcc
import dash_html_components as html
from config import celery_app, AppConfig, DBConfig, db
import celery.states as states
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.server.config["SQLALCHEMY_DATABASE_URI"] = DBConfig.URL
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.server.config["SECRET_KEY"] = AppConfig.SECRET_KEY

db.init_app(app.server)

app.layout = html.Div(children=[
  html.H1(children='Hello Dash'),

  html.Div(children='''
    Dash: A web application framework for Python.
  '''),

])

from scrappers import OLXContentScraper
from parsers import OLXContentParser
scraped_data = OLXContentScraper("https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/pomorskie/").scrap()
OLXContentParser(scraped_data).parse()

#---------------------------------------------------------------------------------------
#   Sample of a callback with a celery process
#---------------------------------------------------------------------------------------
@app.callback(Output('markdown-box' , 'children' ) ,
              [Input('input-box'    , 'value'    )])
def update_text(text):
    if text is None:
        return ''' '''
    task = celery_app.send_task('tasks.add', args=[1, 2], kwargs={})

    #------------------------------------
    # Results of the task executed
    #res = celery.AsyncResult(task.id)
    #if res.state == states.PENDING:
    #    result = res.state
    #else:
    #    result = str(res.result)
    #------------------------------------
    return '''{}  `{}` '''.format(text,task.id)





if __name__ == '__main__':
  app.run_server(host='0.0.0.0', port=8080, debug=True, threaded=True)
