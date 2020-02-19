
import flask
import dash

from layouts import get_app_layout

from app_callbacks import set_app_callbacks
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from resources import external_scripts, external_stylesheets, meta_tags



# body = dbc.Container(
#     [
#         dbc.Row(
#             [
#                 dbc.Col(
#                     [
#                         html.H2("Heading"),
#                         html.P(
#                             """\
# Donec id elit non mi porta gravida at eget metus.
# Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum
# nibh, ut fermentum massa justo sit amet risus. Etiam porta sem
# malesuada magna mollis euismod. Donec sed odio dui. Donec id elit non
# mi porta gravida at eget metus. Fusce dapibus, tellus ac cursus
# commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit
# amet risus. Etiam porta sem malesuada magna mollis euismod. Donec sed
# odio dui."""
#                         ),
#                         dbc.Button("View details", color="secondary"),
#                     ],
#                     md=4,
#                 ),
#                 dbc.Col(
#                     [
#                         html.H2("Graph"),
#                         dcc.Graph(
#                             figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
#                         ),
#                     ]
#                 ),
#             ]
#         )
#     ],
#     className="mt-4",
# )

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# app.layout = html.Div([navbar, body])

# if __name__ == "__main__":
#     app.run_server()

app = dash.Dash('EB Information',
		            external_scripts = [dbc.themes.BOOTSTRAP],
                  #external_stylesheets = external_stylesheets,
                # meta_tags = meta_tags,
               )
app.title = 'EB Information'


server = app.server

app.config.suppress_callback_exceptions = True

app_name = 'EB Information'
set_app_callbacks(app, app_name)

app.layout = get_app_layout(app_name)

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")

