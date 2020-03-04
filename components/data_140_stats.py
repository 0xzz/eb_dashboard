import datetime

import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from .default_config import default_config
from .get_table import get_table
from .toggle_switch import get_toggle
from .local_info import get_local_info_component


def get_140_stats(app, id, df):

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
                    'tickmode' : 'array',
                    'tickvals' : x,
                    'ticktext' : [f'FY{xx}' for xx in x]
                },
            }
        },
        config=default_config,
    )
 
 
    with open("docs/stats_140.md", "rb") as file:
        faq_md = file.read().decode('utf8')
    info_component = dcc.Markdown(faq_md)
    info_button, info_section = get_local_info_component(app, id, info_component)

    return html.Div([
        dbc.Row([
            html.H4('Historical 140 Statstics', id=id),
            info_button
        ], className='Section-Title'),
        info_section,
        fig1_data_store,
        dcc.Tabs(children=[
            dcc.Tab([
                get_toggle('140_stats_stack_toggle'),
                fig_layout,
                ],label="140 Approval Stats"),
            dcc.Tab(fig_layout2,label="140 Denial Rate"),
            dcc.Tab(tb_layout,label="View Table")
        ])
    ])

def get_140_stats_fig_data(x, df):

    fig_data = [{'x': x, 'y': df[f'{c}-EB{eb}-Approved'], 'type': 'bar','name':f'{c}-EB{eb}-Approved'} \
                for c in ['China','India','Row'] for eb in [1,2,3]]
    fig_data.append({'x':[2008.5,2019.5],'y':[4e4/2.4,4e4/2.4],
                        'mode':'lines','line':{'color':'black','dash':'dash'},'name':'Safe EB1 140 threshold'})
    fig_data.append({'x':[2008.5,2019.5],'y':[4e4/2.0,4e4/2.0],
                        'mode':'lines','line':{'color':'red','dash':'dash'},'name':'Safe EB2 140 threshold'})
    fig_data.append({'x':[2008.5,2019.5],'y':[4e4/2.1,4e4/2.1],
                        'mode':'lines','line':{'color':'orange','dash':'dash'},'name':'Safe EB3 140 threshold'})

    fig_content = {
            'data': fig_data,
            'layout': {
                'title': 'Historical 140 Approval by Fisical Year',
                'barmode':'stack',
                'xaxis' : {
                    'tickmode' : 'array',
                    'tickvals' : x,
                    'ticktext' : [f'FY{xx}' for xx in x]
                },
            }
        }
        
    return fig_content