import pandas as pd
import numpy as np

import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from helpers import load_140_stats, load_gc_stats
from .default_config import default_config
from .default_config import default_multiplication_factor
from .get_table import get_table

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

def get_backlog(multiplication_factor, isStack):

    df140 = load_140_stats()
    df_visa = load_gc_stats()

    df485 = compute_df485(df140, multiplication_factor)
    df485_backlog = compute_backlog(df485, df_visa)

    tb485_layout = get_table(df485)
    tb485_backlog_layout = get_table(df485_backlog[[col for col in df485_backlog if 'backlog' in col or 'FY' in col]])

    demand_supply_fig_layout = get_demand_supply_fig(df485, df_visa, isStack)
    backlog_fig_layout = get_backlog_fig(df485, df_visa, df485_backlog)

    #India. At end of FY2018, India EB2 reached to Mar 2009
    #       At end of FY2018, India EB3 reached to Jan 2009
    #Assuming that, at the end of FY2018, all backlog before 2009 and half of the demand in 2009 have been satisfied

    return  html.Div([
        demand_supply_fig_layout,
        html.H6('EB123 Green Card Demand Estimation by Country by FY'),
        tb485_layout,
        html.P([
            html.Div('Note: Please note that the backlog here referes to the green card demands (regardless on if the petitioner has submitted 485 or not) that already have a PD. If a person already has an approved 140, we asume he/she brings or will bring [1*multiplication factor] number of green card demand.'),
            html.Div('      The backlog analysis will help you understand how many people are in front of you in the long waiting queue. Based on simple computation, you can esitmate how long you would need to wait to get a green card.'),
            html.Div('Disclaimer: We take no legal responsibility for the accuracy of the following backlog analysis.', style={'font-weight': 'bold'}),
            html.Div('Assumptions', style={'font-weight': 'bold'}),
            html.Div('  1. The backlogs are estimated based on a simple demand-supply model plus an initial offset. The initial offset are estimated using historical visa bulletins.'),
            html.Div('  2. The green card demands are estimated based on the 140-GreeCard multiplication factors typed in the above 3x3 input grid.'),
            html.Div('  3. Because EB2 PERM and EB3 PERM can relatively easily downgrade/upgrade, we have combined the backlog of EB2 and EB3 when plotting.'),
            html.Div('  3. For EB1, we assume that at the end of FY 2013, all backlogs before 2013 and 60% of 2013 demand had been satisfied for all countries.'),
            html.Div('  4. For China EB2 & EB3, we assume that at the end of FY2019, all backlogs before 2015 has been cleared and 80% of 2015 demands have been satisfied. This is because the VB for China-EB2 and 3 were at June and Nov 2015 at the end of FY2019.'),
            html.Div('  5. For Row EB2 & EB3, we assume that at the end of FY 2018, all backlogs before 2017 and 75% of 2017 demands had been satisfied. This is because the VBs for ROW EB2/3 were current at that time.'),
            html.Div('  6. For India EB2 & EB3, we assume that at the end of FY 2018, all backlogs before FY2009 and 50% of 2009 demands were cleared. This is because Inida EB2/3 moved to Mar 2009 and Jan 2009 at the end of FY 2019, respectively.')
        ]),
        backlog_fig_layout,
        html.H6('EB123 Green Card Backlog Estimation by Country by FY'),
        tb485_backlog_layout
    ])

def get_demand_supply_fig(df485, df_visa, isStack):

    x = list(range(2009,2020))

    fig_data = [{'x': x, 'y': df485[f'{c}-EB{eb}'], 
                'type': 'bar','name':f'{c}-EB{eb} Demand', 
                'visible': True if c=='China' else 'legendonly'} \
                        for c in ['China','India','Row'] for eb in [1,2,3]]
    for c in ['China','India','Row']:
        for eb in [1,2,3]:
            fig_data.append({'x': x, 'y': df_visa[f'{c}-EB{eb}'], 
            'name':f'{c}-EB{eb} Issued', 
            'line':{'width':4},
            'visible': True if c=='China' else 'legendonly'})
    fig_data.append({'x':[2008.5,2019.5],'y':[2800,2800],
                         'mode':'lines','line':{'color':'black','dash':'dot'},
                         'name':'EB1/2/3 7% Cap'})
    fig_data.append({'x':[2008.5,2019.5],'y':[12e4,12e4],
                        'mode':'lines','line':{'color':'black','dash':'dash'},
                        'name':'EB123 Visa Limit','visible':'legendonly'})
    fig_data.append({'x':[2008.5,2019.5],'y':[4e4,4e4],
                         'mode':'lines','line':{'color':'red','dash':'dash'},
                         'name':'EB1/2/3 Visa Limit','visible': 'legendonly'})

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

    return fig_layout



def get_backlog_fig(df485, df_visa, df485_backlog):

    x = np.array(list(range(2009,2020)))
    figs = []
    for c in ['China','India','Row']:
        df485[f'{c}-EB23'] = df485[f'{c}-EB2'] +df485[f'{c}-EB3'] 
        df_visa[f'{c}-EB23'] = df_visa[f'{c}-EB2'] +df_visa[f'{c}-EB3'] 
        df485_backlog[f'{c}-EB23-backlog'] = df485_backlog[f'{c}-EB2-backlog'] +df485_backlog[f'{c}-EB3-backlog'] 
    for eb in [1,23]:
        for c in ['China','India','Row']:
            col = f'{c}-EB{eb}'
            # print(df485[col], df_visa[col], df485_backlog[f'{col}-backlog'])

            fig_data = [{'x': x+0.5, 'y': df485[col].values, 'type': 'bar','name':f'{c}-EB{eb} Demand', 'marker':{'color':'#EE4444'}},
                 {'x': x+0.5, 'y': df_visa[col].values, 'base': -df_visa[col].values, 'type': 'bar','name':f'{c}-EB{eb} Issued', 'marker':{'color':'#44EE44'}},
                 {'x': x+0.9, 'y': df485_backlog[f'{col}-backlog'].values, 'type': 'lines','name':f'{c}-EB{eb} backlog','marker':{'color':'black'}}
            ]

            fig_layout = dcc.Graph(
                figure={
                    'data': fig_data,
                    'layout': {
                        'title': f'{c}-EB{eb} Backlog Analysis',
                        'barmode': 'stack',
                        'legend':{'x':.01, 'y':.99,
                                   'bgcolor':"#DDDDDD00",
                                #   'bordercolor':'gray',
                                #   'borderwidth':2},
                        },
                        'xaxis' : {
                            'tickmode' : 'linear',
                            'tick0':2009,
                            'dtick':1
                        },
                    }
                },
                config=default_config,
                style={'margin':'1rem'}
            )
            figs.append(dbc.Col([fig_layout],md=4))

    return dbc.Row(figs)
