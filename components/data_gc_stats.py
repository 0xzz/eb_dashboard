from helpers import load_gc_stats
import dash_table
import datetime
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from .default_config import default_config
from .get_table import get_table
from .toggle_switch import get_toggle
from .local_info import get_local_info_component

def get_gc_stats_layout(app, id, df):

    tb_layout = get_table(df)

    fig_data_store = dcc.Store(id=f'{id}_figure_data', 
                                data = get_140_stats_fig_data(df))

    fig_layout = dcc.Graph(
        id = f'{id}_figure',
        config=default_config,
    )

    info_component = html.Div([
        'Data source can be found in DOS Annual Reports ', 
        html.A('Here', href='https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/annual-reports.html',target='_blank')
    ])
    info_button, info_section = get_local_info_component(app, id, info_component)

    return html.Div([
        dbc.Row([
            html.H4('Historical Green Card Visa issued statistics', id = id),  
            info_button
        ], className='Section-Title'),
        info_section,
        fig_data_store,
        dcc.Tabs([
            dcc.Tab([
                get_toggle('gc_stats_stack_toggle'),
                fig_layout,
            ], label='Historical Visa Number issued'),
            dcc.Tab(tb_layout, label='View Table')
        ])
     ])

def get_140_stats_fig_data(df):

    x = list(range(2009,2020))

    fig_data = [{'x': x, 'y': df[f'{c}-EB{eb}'], 'type': 'bar','name':f'{c}-EB{eb}'} \
                        for c in ['China','India','Row'] for eb in [1,2,3]]
    fig_data.append({'x':[2008.5,2019.5],'y':[12e4,12e4],
                        'mode':'lines','line':{'color':'black','dash':'dash'},'name':'EB123 Visa Limit',
                    })
    fig_data.append({'x':[2008.5,2019.5],'y':[4e4,4e4],
                         'mode':'lines','line':{'color':'red','dash':'dash'},'name':'EB1/2/3 Visa Limit'})
    fig_data.append({'x':[2008.5,2019.5],'y':[2800,2800],
                         'mode':'lines','line':{'color':'orange','dash':'dash'},'name':'EB1/2/3 7% cap'})
    
    figure_content={
        'data': fig_data,
        'layout': {
            'title': 'Historical Green Card Visa Number Issued by Fisical year',
            'barmode':'stack',
            'xaxis' : {
                'tickmode' : 'array',
                'tickvals' : x,
                'ticktext' : [f'FY{xx}' for xx in x]
            },
        }
    }

    return figure_content