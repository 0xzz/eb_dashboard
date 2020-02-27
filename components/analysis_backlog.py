import pandas as pd

import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from helpers import load_140_stats, load_gc_stats
from .default_config import default_config
from .default_config import default_multiplication_factor

def get_backlog(multiplication_factor, isStack):

    df140 = load_140_stats()
    df_visa = load_gc_stats()

    df485 = pd.DataFrame(index=range(2009,2020))
    for eb in [1,2,3]:
        for c in ['China', 'India', 'Row']:
            df485[f'{c}-EB{eb}'] = (df140[f'{c}-EB{eb}-Approved'].values*multiplication_factor[f'{c}-EB{eb}'])
    df485 = df485.round().astype(int)
    df485['World-Total-EB123'] = df485.values.sum(axis=1)

    tb_layout = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df485.columns],
        data=df485.to_dict('records'),
        sort_action="native",
        style_cell={
            'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
    )

    x = list(range(2009,2020))

    fig_data = [{'x': x, 'y': df485[f'{c}-EB{eb}'], 
                'type': 'bar','name':f'{c}-EB{eb} Demand', 
                'visible': True if c=='China' else 'legendonly'} \
                        for c in ['China','India','Row'] for eb in [1,2,3]]
    fig_data.append({'x':[2008.5,2019.5],'y':[12e4,12e4],
                        'mode':'lines','line':{'color':'black','dash':'dash'},
                        'name':'EB123 Visa Limit','visible':'legendonly'})
    fig_data.append({'x':[2008.5,2019.5],'y':[4e4,4e4],
                         'mode':'lines','line':{'color':'red','dash':'dash'},
                         'name':'EB1/2/3 Visa Limit','visible': 'legendonly'})
    fig_data.append({'x':[2008.5,2019.5],'y':[2800,2800],
                         'mode':'lines','line':{'color':'black','dash':'dot'},
                         'name':'EB1/2/3 7% Cap'})
                         
    for c in ['China','India','Row']:
        for eb in [1,2,3]:
            fig_data.append({'x': x, 'y': df_visa[f'{c}-EB{eb}'], 
            'name':f'{c}-EB{eb} Issued', 
            'line':{'width':4},
            'visible': True if c=='China' else 'legendonly'})
                        
    fig_layout = dcc.Graph(
        figure={
            'data': fig_data,
            'layout': {
                'title': 'Green Card Demand (based on 140 stats) and Visa Number Issued',
                'barmode': 'stack' if isStack else 'group',
                'xaxis' : {
                    'tickmode' : 'linear',
                    'tick0':2009,
                    'dtick':1
                },
            }
        },
        config=default_config,
    )

    return  html.Div([
        html.Div('''The green card demands are estimated based on 140 
    approval numbers and the multiplication numbers. Please note that these 
    numbers do not equal to the amount of pending 485. Instead, the numbers 
    here equal to the "amount of green card demand who already has a PD.
    '''),
        fig_layout,
        html.Div([
            tb_layout
        ], style={'overflow-x': 'auto'})
    ])