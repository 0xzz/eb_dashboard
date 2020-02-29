
import flask
import dash

from layouts import get_app_layout

from app_callbacks import set_app_callbacks
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from resources import external_scripts, external_stylesheets, meta_tags

from EbDashClass import CustomIndexDash

app = CustomIndexDash('EB Information',
		            external_scripts = [
                  dbc.themes.BOOTSTRAP],
                  # {
                  #   'href': 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js',
                  #   'crossorgin': 'anonymous',
                  #   'data-ad-client': 'ca-pub-4691708742212768'
                  # }],
                  #external_stylesheets = external_stylesheets,
                # meta_tags = meta_tags,
               )
app.title = 'EB Information'


server = app.server

app.config.suppress_callback_exceptions = True

app_name = 'EB Stats'
set_app_callbacks(app, app_name)

app.layout = get_app_layout(app_name)

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")

