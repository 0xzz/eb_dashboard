import datetime

import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from helpers import load_140_stats
from .default_config import default_config
from .get_table import get_table


def get_140_stats(isStack):

    df = load_140_stats()

    tb_layout = get_table(df)

    x = list(range(2009,2020))

    fig_data = [{'x': x, 'y': df[f'{c}-EB{eb}-Approved'], 'type': 'bar','name':f'{c}-EB{eb}-Approved'} \
                for c in ['China','India','Row'] for eb in [1,2,3]]
    fig_data.append({'x':[2008,2020],'y':[4e4/2.4,4e4/2.4],
                        'mode':'lines','line':{'color':'black','dash':'dash'},'name':'Safe EB1 140 threshold'})
    fig_data.append({'x':[2008,2020],'y':[4e4/2.0,4e4/2.0],
                        'mode':'lines','line':{'color':'red','dash':'dash'},'name':'Safe EB2 140 threshold'})
    fig_data.append({'x':[2008,2020],'y':[4e4/2.1,4e4/2.1],
                        'mode':'lines','line':{'color':'orange','dash':'dash'},'name':'Safe EB3 140 threshold'})
    
    fig_layout = dcc.Graph(
        figure={
            'data': fig_data,
            'layout': {
                'title': 'Historical 140 Approval by Fisical Year',
                'barmode':'stack' if isStack else 'group',
                'xaxis' : {
                    'tickmode' : 'linear',
                    'tick0':2009,
                    'dtick':1
                },
            }
        },
        config=default_config,
    )

    fig_layout2 = dcc.Graph(
        figure={
            'data': [{'x': x, 'y': df[f'{c}-EB{eb}-Deny_rate'],'name':f'{c}-EB{eb}-Denial-Rate'} \
                        for c in ['China','India','Row'] for eb in [1,2,3]],
            'layout': {
                'title': 'Historical 140 Denial Rate by Country By Fisical Year',
                'xaxis' : {
                    'tickmode' : 'linear',
                    'tick0':2009,
                    'dtick':1
                },
                # 'autosize': False
            }
        },
        config=default_config,
    )
    
    # return html.Div([
    #     dbc.Row([
    #         dbc.Col([fig_layout],lg=6),
    #         dbc.Col([fig_layout2],lg=6),
    #     ]),
    #     html.Div([
    #         tb_layout
    #     ], style={'overflow-x': 'auto'})
    # ])


    return dcc.Tabs(children=[
            dcc.Tab(fig_layout,label="140 Approval Stats"),
            dcc.Tab(fig_layout2,label="140 Denial Rate"),
            dcc.Tab(tb_layout,label="View Table")
            # dbc.Col([fig_140_485_layout],lg=6),
            # dbc.Col([tb_layout],lg=6),
        ])