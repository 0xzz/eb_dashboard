import pandas as pd
import numpy as np
import datetime

import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from .default_config import default_config, default_multiplication_factor
from .get_table import get_table
from .toggle_switch import get_toggle
from .local_info import get_local_info_component

from helpers import load_140_stats, load_gc_stats

def get_demand_backlog_layout(app, id):

    info_component1 = html.Div('''The green card demandsand backlogs are estimated based on 140 
    approval numbers and the multiplication numbers. Please note that these 
    numbers do not equal to the amount of pending 485/CP application. Instead, the numbers 
    here equal to the "amount of green card demand who already has a PD". 
    ''')
    info_button1, info_section1 = get_local_info_component(app, id, info_component1)

    info_component2 = html.Ul([
            html.Li('Note: Please note that the backlog here referes to the green card demands (regardless on if the petitioner has submitted 485 or not) that already have a PD. If a person already has an approved 140, we asume he/she brings or will bring [1*multiplication factor] number of green card demand.'),
            html.Li('      The backlog analysis will help you understand how many people are in front of you in the long waiting queue. Based on simple computation, you can esitmate how long you would need to wait to get a green card.'),
            html.Li('Disclaimer: We take no legal responsibility for the accuracy of the following backlog analysis.', style={'font-weight': 'bold'}),
            html.Li([html.Div('Assumptions', style={'font-weight': 'bold'}),
                html.Ul([
                    html.Li('  1. The backlogs are estimated based on a simple demand-supply model plus an initial offset. The initial offset are estimated using historical visa bulletins.'),
                    html.Li('  2. The green card demands are estimated based on the 140-GreeCard multiplication factors typed in the above 3x3 input grid.'),
                    html.Li('  3. Because EB2 PERM and EB3 PERM can relatively easily downgrade/upgrade, we have combined the backlog of EB2 and EB3 when plotting.'),
                    html.Li('  3. For EB1, we assume that at the end of FY 2013, all backlogs before 2013 and 60% of 2013 demand had been satisfied for all countries.'),
                    html.Li('  4. For China EB2 & EB3, we assume that at the end of FY2019, all backlogs before 2015 has been cleared and 80% of 2015 demands have been satisfied. This is because the VB for China-EB2 and 3 were at June and Nov 2015 at the end of FY2019.'),
                    html.Li('  5. For Row EB2 & EB3, we assume that at the end of FY 2018, all backlogs before 2017 and 75% of 2017 demands had been satisfied. This is because the VBs for ROW EB2/3 were current at that time.'),
                    html.Li('  6. For India EB2 & EB3, we assume that at the end of FY 2018, all backlogs before FY2009 and 50% of 2009 demands were cleared. This is because Inida EB2/3 moved to Mar 2009 and Jan 2009 at the end of FY 2019, respectively.')
                ])
            ])
        ])
    info_button2, info_section2 = get_local_info_component(app, id+'-backlog', info_component2)

    multiplication_factor_layout = dbc.Row([
      dbc.Col([
        html.Div(f'{c}-EB{eb}'),
        dcc.Input(
                id=f'factor_{c}-{eb}',
                type='number',
                value = default_multiplication_factor[f'{c}-EB{eb}'],
                placeholder= default_multiplication_factor[f'{c}-EB{eb}'],
                step = 0.01, min = 0.5, max = 5.0, style={'maxWidth': '80px'}
            )
      ], sm=4) for c in ['China','India','Row'] for eb in [1,2,3]])

    gc_demand_figure_layout = dcc.Graph(
        id = 'gc_demand_figure',
        config=default_config,
    )

    return html.Div([
        dbc.Row([
            html.H4('EB Green Card Demand and Backlog Anlysis', id=id),
            info_button1
        ], className='Section-Title'),
        info_section1,
        html.Div([
            html.Div('Please type in the [140:green card] multiplication factors'),
            multiplication_factor_layout
        ]),
        html.H6('EB123 Green Card Demand Estimation by Country by FY'),
        dcc.Store(id='gc_demand_figure_content', data = {}),
        dcc.Tabs([
            dcc.Tab([
                get_toggle('gc_demand_stack_toggle', False),
                gc_demand_figure_layout
            ],label="View Trend"),
            dcc.Tab(id='gc_demand_table_layout', label="View Table")
        ]),
        dbc.Row([
            html.H6('EB123 Green Card Backlog Estimation by Country by FY'),
            info_button2
        ], className='Section-Title'),
        info_section2,
        dcc.Tabs(id='gc_backlogs_tabs')
    ])

def update_backlog_components(multiplication_factor):

    df140 = load_140_stats()
    df_visa = load_gc_stats()

    df485 = compute_df485(df140, multiplication_factor)
    df485_backlog = compute_backlog(df485, df_visa)

    demand_supply_fig_content = get_demand_supply_fig_content(df485, df_visa)
    tb485_layout = get_table(df485)
    
    backlog_fig_tabs = get_backlog_fig(df485, df_visa, df485_backlog, multiplication_factor)
    tb485_backlog_layout = get_table(df485_backlog[[col for col in df485_backlog if 'backlog' in col or 'FY' in col]])

    return demand_supply_fig_content, tb485_layout, \
        backlog_fig_tabs+[dcc.Tab(tb485_backlog_layout, label='View Table')]

def get_demand_supply_fig_content(df485, df_visa):

    x = list(range(2009,2020))
    #x = [datetime.datetime(yr,10,1) for yr in range(2009, 2020)]
    x_range = [2008.5,2019.5]
    fig_data = [{'x': x, 'y': df485[f'{c}-EB{eb}'], 
                'type': 'bar','name':f'{c}-EB{eb} Demand', 'opacity':0.7,
                'visible': True if c=='China' else 'legendonly'} \
                        for c in ['China','India','Row'] for eb in [1,2,3]]
    for c in ['China','India','Row']:
        for eb in [1,2,3]:
            fig_data.append({'x': x, 'y': df_visa[f'{c}-EB{eb}'], 
            'name':f'{c}-EB{eb} Issued',
            'line':{'width':4},
            'visible': True if c=='China' else 'legendonly'})
    fig_data.append({'x':x_range,'y':[2800,2800],
                         'mode':'lines','line':{'color':'black','dash':'dot'},
                         'name':'EB1/2/3 7% Cap'})
    fig_data.append({'x':x_range,'y':[12e4,12e4],
                        'mode':'lines','line':{'color':'black','dash':'dash'},
                        'name':'EB123 Visa Limit','visible':'legendonly'})
    fig_data.append({'x':x_range,'y':[4e4,4e4],
                         'mode':'lines','line':{'color':'red','dash':'dash'},
                         'name':'EB1/2/3 Visa Limit','visible': 'legendonly'})

    fig_content={
            'data': fig_data,
            'layout': {
                'title': 'Green Card Demand (based on 140 stats) and Visa Number Issued',
                'barmode': 'group',
                'xaxis' : {
                    'tickmode' : 'array',
                    'tickvals' : x,
                    'ticktext' : [f'FY{xx}' for xx in x]
                },
            }
        }

    return fig_content

def compute_df485(df140, multiplication_factor):
    df485 = pd.DataFrame(index=range(2009,2020))
    df485['FY']=list(range(2009,2020))

    for eb in [1,2,3]:
        for c in ['China', 'India', 'Row']:
            df485[f'{c}-EB{eb}'] = (df140[f'{c}-EB{eb}-Approved'].values*multiplication_factor[f'{c}-EB{eb}'])
    df485 = df485.round().astype(int)
    df485['World-Total-EB123'] = df485.values.sum(axis=1)
    return df485

def compute_backlog(df485, df_visa):
    df485_backlog = pd.DataFrame(index = df485.index) #estimate the 485 backlog at the end of each FY year
    df485_backlog['FY']=list(range(2009,2020))
    CList = ['China','India','Row']
    for eb in [1,2,3]:
        for c in CList:
            df485_backlog[f'{c}-EB{eb}-cum-demand'] = df485[f'{c}-EB{eb}'].values.cumsum()
            df485_backlog[f'{c}-EB{eb}-cum-supply'] = df_visa[f'{c}-EB{eb}'].values.cumsum()
            df485_backlog[f'{c}-EB{eb}-backlog'] = df485_backlog[f'{c}-EB{eb}-cum-demand'] - df485_backlog[f'{c}-EB{eb}-cum-supply']

    for c in CList:
        #shift deficit so that the backlog at end of 2013 is a quarter of 2013 demand (i.e., all backlogs before 2012 is cleared, and 60% of 2013 demand is satisfied)
        df485_backlog[f'{c}-EB1-backlog'] = df485_backlog[f'{c}-EB1-backlog'] - df485_backlog[f'{c}-EB1-backlog'].iloc[4] + df485[f'{c}-EB1'].iloc[4]*0.4


    #assumption for EB23
    #China. At end of FY2014, EB23 moved to end of 2009. Therefore we assume that all backlog before and include 2009 is cleared at end of 2014. The backlog at end of 2014 should equal to the cum demand from 2010 to 2014
    #df485_backlog['China-EB23-backlog'] = df485_backlog['China-EB23-backlog'] - df485_backlog['China-EB23-backlog'].iloc[5] + df485['China-EB23'].iloc[1:6].sum()
    #China. At end of FY2019, EB2 is around june, 2015, EB3 is around nov 2015. Therefore we assume that all backlog before and include 2019 is cleared at the 4/5 of 2015. The backlog at end of 2019 should equal to the cum demand from 2015 (20%) to 2019
    df485_backlog['China-EB2-backlog'] = df485_backlog['China-EB2-backlog'] - df485_backlog['China-EB2-backlog'].iloc[-1] + \
                                        df485['China-EB2'].iloc[6]*0.2+df485['China-EB2'].iloc[7:].sum()
    df485_backlog['China-EB3-backlog'] = df485_backlog['China-EB3-backlog'] - df485_backlog['China-EB3-backlog'].iloc[-1] + \
                                        df485['China-EB3'].iloc[6]*0.2+df485['China-EB3'].iloc[7:].sum()

    #ROW. At end of FY2017, both EB23-row are current. Therefore we assume that the backlog at end of 2017=2017 demand*0.75
    df485_backlog['Row-EB2-backlog'] = df485_backlog['Row-EB2-backlog'] - df485_backlog['Row-EB2-backlog'].iloc[8] + \
                                        df485['Row-EB2'].iloc[8]*0.5
    df485_backlog['Row-EB3-backlog'] = df485_backlog['Row-EB3-backlog'] - df485_backlog['Row-EB3-backlog'].iloc[8] + \
                                        df485['Row-EB3'].iloc[8]*0.5

    #India. At end of FY2018, India EB2 reached to Mar 2009
    #       At end of FY2018, India EB3 reached to Jan 2009
    #Assuming that, at the end of FY2018, all backlog before 2009 and half of the demand in 2009 have been satisfied
    df485_backlog['India-EB2-backlog'] = df485_backlog['India-EB2-backlog'] - df485_backlog['India-EB2-backlog'].iloc[-2] + \
                                        df485['Row-EB2'].iloc[0]*0.5 + df485['Row-EB2'].iloc[1:].sum()
    df485_backlog['India-EB3-backlog'] = df485_backlog['India-EB3-backlog'] - df485_backlog['India-EB3-backlog'].iloc[-2] + \
                                        df485['Row-EB3'].iloc[0]*0.5 + df485['Row-EB3'].iloc[1:].sum()

    df485_backlog = df485_backlog.round().astype(int)

    return df485_backlog



def get_backlog_fig(df485, df_visa, df485_backlog, multiplication_factor):
    x = np.array(list(range(2009,2020)))
    fig_tabs = []
    for c in ['China','India','Row']:
        df485[f'{c}-EB23'] = df485[f'{c}-EB2'] +df485[f'{c}-EB3'] 
        df_visa[f'{c}-EB23'] = df_visa[f'{c}-EB2'] +df_visa[f'{c}-EB3'] 
        df485_backlog[f'{c}-EB23-backlog'] = df485_backlog[f'{c}-EB2-backlog'] +df485_backlog[f'{c}-EB3-backlog'] 
    for eb in [1,23]:
        for c in ['China','India','Row']:
            col = f'{c}-EB{eb}'
            # print(df485[col], df_visa[col], df485_backlog[f'{col}-backlog'])

            fig_data = [
                {'x': x+0.49, 'y': df485[col].values, 'type': 'bar','name':f'{c}-EB{eb} Demand', 'marker':{'color':'#EE4444'},
                        'hoverinfo':'x+y','hovertemplate':'FY%{x:.0f}<br>add %{y}'},
                {'x': x+0.49, 'y': -df_visa[col].values, 'base': 0, 'type': 'bar','name':f'{c}-EB{eb} Issued', 'marker':{'color':'#44EE44'},
                        'hoverinfo':'x+y','hovertemplate':'FY%{x:.0f}<br>clear %{y}'},
                {'x': x+1.0, 'y': df485_backlog[f'{col}-backlog'].values, 'type': 'lines','name':f'{c}-EB{eb} backlog','marker':{'color':'black'},
                        'hoverinfo':'x+y','hovertemplate':'At Begining of FY%{x:.0f}<br>Total Backlog: %{y}'}
            ]

            if(eb==1):
                mf_msg = f'[MultiFactor={multiplication_factor[col]}]'
            else:
                c1= f'{c}-EB2'
                c2= f'{c}-EB3'
                mf_msg = f'[MultiFactor={multiplication_factor[c1]}(EB2), {multiplication_factor[c2]}(EB3)]'

            fig_layout = dcc.Graph(
                figure={
                    'data': fig_data,
                    'layout': {
                        # 'hovermode':'closest',
                        'title': f'{c}-EB{eb} Backlog {mf_msg}',
                        'font': {
                            'size': '0.85rem'
                        },
                        'barmode': 'stack',
                        'legend':{'x':.01, 'y':.99,
                                   'bgcolor':"#DDDDDD00",
                                #   'bordercolor':'gray',
                                #   'borderwidth':2},
                        },
                        'xaxis' : {
                            'tickmode' : 'linear',
                            'tick0' : 2009,
                            'dtick' : 1
                        },
                    }
                },
                config=default_config,
                style={'margin':'1rem'}
            )
            fig_tabs.append(dcc.Tab([fig_layout],label = f'{c}-EB{eb}'))

    return fig_tabs
