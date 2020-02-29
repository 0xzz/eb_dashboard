import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from helpers import load_140_485_by_FY
from .default_config import default_config
from .get_table import get_table

def get_overall_140_485_view():

    df_140_485 = load_140_485_by_FY()

    tb_layout = get_table(df_140_485)

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
        dcc.Tabs([
            dcc.Tab(fig_140_485_layout,label="View Trend"),
            dcc.Tab(tb_layout,label="View Table")
        ])
    ])
        
    
    
    
    # html.Div([
    #     html.Div([tb_layout],className = "col-lg-5", style={'margin':'1rem'}),
    #     html.Div([fig_140_485_layout],className = "col-lg-5", style={'margin':'1rem'})
    # ], className = "row")