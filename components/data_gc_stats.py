from helpers import load_gc_stats
import dash_table
import datetime
import dash_html_components as html
import dash_core_components as dcc
from .default_config import default_config
from .get_table import get_table
from .toggle_switch import get_toggle

def get_gc_stats_layout():

    df = load_gc_stats()

    tb_layout = get_table(df)

    fig_layout = dcc.Graph(
        id = 'gc_stats_fig',
        config=default_config,
    )

    return html.Div([
        html.P([
                'Data source can be found in DOS Annual Reports ', 
                html.A('Here', href='https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/annual-reports.html',target='_blank')
              ]),
        dcc.Tabs([
            dcc.Tab([
                get_toggle('gc_stats_stack_toggle'),
                dcc.Loading([fig_layout]),
            ], label='Historical Visa Number issued'),
            dcc.Tab(tb_layout, label='View Table')
        ])
     ])

def update_gc_stats_figure_content(isStack):
    df = load_gc_stats()

    x = list(range(2009,2020))

    fig_data = [{'x': x, 'y': df[f'{c}-EB{eb}'], 'type': 'bar','name':f'{c}-EB{eb}'} \
                        for c in ['China','India','Row'] for eb in [1,2,3]]
    fig_data.append({'x':[2008.5,2019.5],'y':[12e4,12e4],
                        'mode':'lines','line':{'color':'black','dash':'dash'},'name':'EB123 Visa Limit',
                        'visible': True if isStack else 'legendonly'})
    fig_data.append({'x':[2008.5,2019.5],'y':[4e4,4e4],
                         'mode':'lines','line':{'color':'red','dash':'dash'},'name':'EB1/2/3 Visa Limit'})
    fig_data.append({'x':[2008.5,2019.5],'y':[2800,2800],
                         'mode':'lines','line':{'color':'orange','dash':'dash'},'name':'EB1/2/3 7% cap'})
    
    figure_content={
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
    }

    return figure_content