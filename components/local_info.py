import dash_html_components as html
from dash.dependencies import Output, Input, State, ClientsideFunction

def get_local_info_component(app, id, info_component, hidden = True):
    icon_id = f'{id}_info_icon'
    button_id = f'{id}_info_button'
    info_id = f'{id}_info'
    
    info_button = get_info_button(icon_id, button_id, hidden)
    info_section = html.P([info_component], id=info_id)

    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='display_info'
        ),
        [Output(info_id, 'style'),
         Output(icon_id, 'className')],
        [Input(button_id, 'n_clicks')]
    )

    return info_button, info_section

def get_info_button(icon_id, button_id, hidden):
    this_n_clicks = 1
    if hidden:
        this_n_clicks = 0
    return html.Button([
        html.I(className="fa fa-question-circle", style={'font-size':'2rem'}, id = icon_id),
        ' Info'
        ],
        id=button_id,
        n_clicks = this_n_clicks,
        className = 'btn btn-info-outline p-2',
        style={'margin':'6px'}
    )
