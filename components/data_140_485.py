import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from helpers import load_140_485_by_FY
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

    figure_data = [{'x': df_140_485['FY'], 
                      'y': df_140_485[col], 
                      'name':col,
                      'visible':True if 'approved' in col else 'legendonly'} \
                     for col in df_140_485.columns if col!='FY']
    figure_data.append({'x':[2011.5,2019.5],'y':[14e4/6.5*3.0,14e4/6.5*3.0],
                        'mode':'lines','line':{'color':'black','dash':'dash'},'name':'Safe 140 threshold'})

    fig_140_485_layout = dcc.Graph(
        figure={
            'data': figure_data,
            'layout': {
                'title': '140/485 data Visualization'
            }
        },
        config=default_config,
    )

    return html.Div([
        html.P('The safe threshold is computed using 140k (total annual EB green card limit) divided by 2.167 (average global 140:visa multiplication factor. An approval number higher than this threshold would lead to backlog in EB green card petition'),
        dbc.Row([
            dbc.Col([fig_140_485_layout],lg=6),
            dbc.Col([tb_layout],lg=6),
        ])
    ])
        
    
    
    
    # html.Div([
    #     html.Div([tb_layout],className = "col-lg-5", style={'margin':'1rem'}),
    #     html.Div([fig_140_485_layout],className = "col-lg-5", style={'margin':'1rem'})
    # ], className = "row")