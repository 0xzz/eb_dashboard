from helpers import load_gc_stats
import dash_table
import datetime
import dash_html_components as html
import dash_core_components as dcc
from .default_config import default_config


def get_gc_stats():

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

    fig_layout = dcc.Graph(
        figure={
            'data': [{'x': x, 'y': df[f'{c}-EB{eb}'], 'type': 'bar','name':f'{c}-EB{eb}'} \
                        for c in ['China','India','Row'] for eb in [1,2,3]],
            'layout': {
                'title': 'Historical Green Card Visa Number Issued by Fisical year',
                'barmode':'stack',
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
        html.Div('Data source at https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/annual-reports.html'),
        fig_layout,
        tb_layout,
    ])