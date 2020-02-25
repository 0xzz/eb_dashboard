from helpers import load_140_485_by_FY
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from .default_config import default_config

def get_overall_140_485_view():

    df_140_485 = load_140_485_by_FY()

    tb_layout = dash_table.DataTable(
        # id = 'table',
        columns=[{"name": i, "id": i} for i in df_140_485.columns],
        data=df_140_485.to_dict('records'),
        sort_action="native",
        style_cell={
            'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
    )

    fig_140_485_layout = dcc.Graph(
        #id='example-graph',
        figure={
            'data': [{'x': df_140_485['FY'], 'y': df_140_485[col], 'name':col} \
                        for col in df_140_485.columns if col!='FY'],
            'layout': {
                'title': '140/485 data Visualization'
            }
        },
        config=default_config,
    )

    return html.Div([
        html.Div([tb_layout],className = "col-lg-5", style={'margin':'1rem'}),
        html.Div([fig_140_485_layout],className = "col-lg-5", style={'margin':'1rem'})
    ], className = "row")