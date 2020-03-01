import datetime

import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from helpers import load_140_stats
from .default_config import default_config
from .get_table import get_table
from .toggle_switch import get_toggle


def get_140_stats():

    df = load_140_stats()
    x = list(range(2009,2020))

    tb_layout = get_table(df)

    fig1_data_store = dcc.Store(id='140_stats_figure_data', 
                                data = get_140_stats_fig_data(x, df))
    fig_layout = dcc.Graph(
        config=default_config,
        id='140_stats_fig'
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
            }
        },
        config=default_config,
    )
 
    return html.Div([
        html.P([
                html.Div([
                  'Data source at USCIS ', 
                  html.A('here', href='https://www.uscis.gov/sites/default/files/USCIS/Resources/Reports%20and%20Studies/Immigration%20Forms%20Data/Employment-based/I140_by_class_country_FY09_19.pdf', target='_blank')
                ]),
                html.Div('''Please note that the approved numbers of FY2019 have been 
corrected using the pending numbers and 2019 denial rate. The safe EB 140 thresholds
are computed using 40k divided by the corresponding global EB123 multiplication 
factors: 2.4, 2.0, and 2.1, respectively.
'''),
        ]),
        fig1_data_store,
        dcc.Tabs(children=[
            dcc.Tab([
                get_toggle('140_stats_stack_toggle'),
                dcc.Loading([fig_layout]),
                ],label="140 Approval Stats"),
            dcc.Tab(fig_layout2,label="140 Denial Rate"),
            dcc.Tab(tb_layout,label="View Table")
        ])
    ])

def get_140_stats_fig_data(x, df):

    fig_data = [{'x': x, 'y': df[f'{c}-EB{eb}-Approved'], 'type': 'bar','name':f'{c}-EB{eb}-Approved'} \
                for c in ['China','India','Row'] for eb in [1,2,3]]
    fig_data.append({'x':[2008,2020],'y':[4e4/2.4,4e4/2.4],
                        'mode':'lines','line':{'color':'black','dash':'dash'},'name':'Safe EB1 140 threshold'})
    fig_data.append({'x':[2008,2020],'y':[4e4/2.0,4e4/2.0],
                        'mode':'lines','line':{'color':'red','dash':'dash'},'name':'Safe EB2 140 threshold'})
    fig_data.append({'x':[2008,2020],'y':[4e4/2.1,4e4/2.1],
                        'mode':'lines','line':{'color':'orange','dash':'dash'},'name':'Safe EB3 140 threshold'})

    fig_content = {
            'data': fig_data,
            'layout': {
                'title': 'Historical 140 Approval by Fisical Year',
                'barmode':'stack',
                'xaxis' : {
                    'tickmode' : 'linear',
                    'tick0':2009,
                    'dtick':1
                },
            }
        }
        
    return fig_content