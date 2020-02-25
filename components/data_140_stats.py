from helpers import load_140_stats
import dash_table
import datetime
import dash_html_components as html
import dash_core_components as dcc
from .default_config import default_config


def get_140_stats():

    df = load_140_stats()

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
            'data': [{'x': x, 'y': df[f'{c}-EB{eb}-Approved'], 'type': 'bar','name':f'{c}-EB{eb}-Approved'} \
                        for c in ['China','India','Row'] for eb in [1,2,3]],
            'layout': {
                'title': 'Historical 140 Approval by Fisical Year',
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

    fig_layout2 = dcc.Graph(
        figure={
            'data': [{'x': x, 'y': df[f'{c}-EB{eb}-Deny_rate'],'name':f'{c}-EB{eb}-Deny-Rate'} \
                        for c in ['China','India','Row'] for eb in [1,2,3]],
            'layout': {
                'title': 'Historical 140 Deny Rate by Country By Fisical Year Fisical Year',
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
        html.Div('Data source at https://www.uscis.gov/sites/default/files/USCIS/Resources/Reports%20and%20Studies/Immigration%20Forms%20Data/Employment-based/I140_by_class_country_FY09_19.pdf'),
        fig_layout,
        fig_layout2,
        tb_layout,
    ])