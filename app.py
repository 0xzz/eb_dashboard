
import os

import flask
import requests

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from layouts import get_app_layout
from app_callbacks import set_app_callbacks
from resources import external_scripts, external_stylesheets, meta_tags


db_url = os.environ.get('db_url')

app_name = 'GreenNet'

app = dash.Dash(app_name,
		            external_scripts = [
                  dbc.themes.BOOTSTRAP] + external_stylesheets,
                meta_tags = meta_tags,
               )

app.title = app_name

server = app.server

app.config.suppress_callback_exceptions = True

set_app_callbacks(app, db_url)

app.layout = get_app_layout(app, app_name)

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")

