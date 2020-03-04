
import dash_html_components as html
import dash_daq as daq

def get_page_view():
    return html.Div([
        html.Div(id='dummy-page-div'),
        daq.LEDDisplay(id='access_count', value=666),
        html.Div('Total Page Views', style={'font-weight':'bold'})
    ], style={'text-align': 'center', 'margin': '10px'})
              