from helpers import load_gc_stats
import dash_table
import datetime
import dash_html_components as html
import dash_core_components as dcc
from .default_config import default_config


def get_gc_stats(isStack):

    df = load_gc_stats()

    tb_layout = dash_table.DataTable(
        # id = 'table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        sort_action="native",
        style_cell={
            'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
    )

    x = list(range(2009,2020))

    fig_data = [{'x': x, 'y': df[f'{c}-EB{eb}'], 'type': 'bar','name':f'{c}-EB{eb}'} \
                        for c in ['China','India','Row'] for eb in [1,2,3]]
    fig_data.append({'x':[2008.5,2019.5],'y':[12e4,12e4],
                        'mode':'lines','line':{'color':'black','dash':'dash'},'name':'EB123 Visa Limit'})
    fig_data.append({'x':[2008.5,2019.5],'y':[4e4,4e4],
                         'mode':'lines','line':{'color':'red','dash':'dash'},'name':'EB1/2/3 Visa Limit'})
    
    fig_layout = dcc.Graph(
        figure={
            'data': fig_data,
            'layout': {
                'title': 'Historical Green Card Visa Number Issued by Fisical year',
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

    return html.Div([
        fig_layout,
        html.Div([
            tb_layout
        ], style={'overflow-x': 'auto'})
    ])