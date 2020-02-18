
import flask
import dash

from layouts import page_content_frame
from app_callbacks import set_app_callbacks
# from login_callbacks import set_login_callbacks

from resources import external_scripts, external_stylesheets, meta_tags

app = dash.Dash('EB Information',
		external_scripts = external_scripts,
                  #external_stylesheets = external_stylesheets,
                meta_tags = meta_tags,
               )
app.title = 'EB Information'


server = app.server

app.config.suppress_callback_exceptions = True

_app_route = '/main-app'

app_name = 'EB'
#set_login_callbacks(app, _app_route, app_name)
set_app_callbacks(app, app_name)

app.layout = page_content_frame

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")

