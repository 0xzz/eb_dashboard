import pandas as pd
import numpy as np
from scipy import interpolate
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

    with open("docs/demand.md", "rb") as file:
        demand_faq_md = file.read().decode('utf8')
    info_component1 = dcc.Markdown(demand_faq_md)
    info_button1, info_section1 = get_local_info_component(app, id, info_component1)

    with open("docs/backlog.md", "rb") as file:
        backlog_faq_md = file.read().decode('utf8')
    info_component2 = dcc.Markdown(backlog_faq_md)
    info_button2, info_section2 = get_local_info_component(app, id+'-backlog', info_component2)

    with open("docs/prediction.md", "rb") as file:
        prediction_faq_md = file.read().decode('utf8')
    info_component3 = dcc.Markdown(prediction_faq_md)
    info_button3, info_section3 = get_local_info_component(app, id+'-prediction', info_component3)

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
            html.H4('EB Green Card Wait Time, Demand and Backlog Anlysis', id=id),
        ], className='Section-Title'),
        dbc.Row([
            html.H6('Estimate Your Waiting Time'),
            info_button3
        ], className='Section-Title'),
        info_section3,
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div('Select your EB category', style={'margin': '5px'}),
                    dcc.Dropdown(
                        id='user-eb-type',
                        options=[
                            {'label': f'{c}-EB{eb}', 'value': f'{c}-EB{eb}'} 
                            for c in ['China', 'India','Row'] for eb in [1,23]
                        ],
                        value='China-EB1',
                        style={'width': '150px'}
                    )
                ]),
                dbc.Col([
                    html.Div('140:GreenCard MultiFactor', style={'margin': '5px'}),
                    html.Div(id='multifactor_placeholder', className = 'div-value-info')
                ]),
                dbc.Col([
                    html.Div(id='designed-annual-supply-info-div', style={'margin': '5px'}),
                    html.Div(id='designed-annual-supply', className = 'div-value-info')
                ]),            
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div('Type in your priority date', style={'margin': '5px'}),
                    dcc.DatePickerSingle(
                        id='pd-picker',
                        min_date_allowed=datetime.datetime(2017,6,2),
                        max_date_allowed=datetime.datetime(2020,9,30),
                        initial_visible_month=datetime.datetime(2018,2,1),
                        date=str(datetime.datetime(2018, 2, 1, 23, 59, 59))
                    )
                ]),
                dbc.Col([
                    html.Div('Expected Annual Spillover after FY2019', style={'margin': '5px'}),
                    dcc.Input(
                        id=f'future-annual-so',
                        type='number',
                        value = 0,
                        placeholder= 0,
                        step = 1, min = 0, max = 140000, style={'maxWidth': '80px'}
                    )
                ]),
                dbc.Col(dbc.Button('Let me Green', id='button-estimate-wait-time'))
            ])
        ], style={'margin':'0.5rem','padding':'0.5rem','border-radius':'6px','background-color':'#CCCCCC'}),
        html.Div(id='wait-time-estimation'),
        dbc.Row([
            html.H6('EB123 Green Card Demand Analysis'),
            info_button1
        ]),
        info_section1,
        html.H6('[140:green card] multiplication factors'),
        html.Div([
            multiplication_factor_layout
        ], style={'margin':'0.5rem','padding':'0.5rem','border-radius':'6px','background-color':'#CCCCCC'}),
        dcc.Store(id='gc_demand_figure_content', data = {}),
        dcc.Tabs([
            dcc.Tab([
                get_toggle('gc_demand_stack_toggle', False),
                gc_demand_figure_layout
            ],label="View Trend"),
            dcc.Tab(id='gc_demand_table_layout', label="View Table")
        ]),
        dbc.Row([
            html.H6('EB123 Green Card Backlog Analysis'),
            info_button2
        ], className='Section-Title'),
        info_section2,
        dcc.Tabs(id='gc_backlogs_tabs'),
        dcc.Store(id='gc_backlogs_data', data = {})
    ])

def update_backlog_components(multiplication_factor):

    df140 = load_140_stats()
    df_visa = load_gc_stats()

    df485 = compute_df485(df140, multiplication_factor)
    df485_backlog = compute_backlog(df485, df_visa)

    demand_supply_fig_content = get_demand_supply_fig_content(df485, df_visa)
    tb485_layout = get_table(df485)
    
    backlog_fig_tabs, backlog_dict = get_backlog_fig(df485, df_visa, df485_backlog, multiplication_factor)
    tb485_backlog_layout = get_table(df485_backlog[[col for col in df485_backlog if 'backlog' in col or 'FY' in col]])

    return demand_supply_fig_content, tb485_layout, \
        backlog_fig_tabs+[dcc.Tab(tb485_backlog_layout, label='View Table')],\
        backlog_dict

def get_demand_supply_fig_content(df485, df_visa):

    x = list(range(2009,2020))
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
    df485_backlog = pd.DataFrame() 
    df485_backlog['FY']=list(range(2008,2020))
    CList = ['China','India','Row']
    for eb in [1,2,3]:
        for c in CList:
            df485_backlog[f'{c}-EB{eb}-cum-demand'] = [0]+df485[f'{c}-EB{eb}'].values.cumsum().tolist()
            df485_backlog[f'{c}-EB{eb}-cum-supply'] = [0]+df_visa[f'{c}-EB{eb}'].values.cumsum().tolist()
            df485_backlog[f'{c}-EB{eb}-backlog'] = df485_backlog[f'{c}-EB{eb}-cum-demand'] - df485_backlog[f'{c}-EB{eb}-cum-supply']

    for c in CList:
        #shift deficit so that the backlog at end of 2013 is a quarter of 2013 demand (i.e., all backlogs before 2012 is cleared, and 60% of 2013 demand is satisfied)
        df485_backlog[f'{c}-EB1-backlog'] = df485_backlog[f'{c}-EB1-backlog'] - df485_backlog[f'{c}-EB1-backlog'].iloc[4] + df485[f'{c}-EB1'].iloc[4]*0.6


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

    #India. At end of FY2019, India EB2 reached to May 2009
    #       At end of FY2019, India EB3 reached to July 2009
    #Assuming that, at the end of FY2019, all backlog before 2009 and 75% of the demand in 2009 have been satisfied
    df485_backlog['India-EB2-backlog'] = df485_backlog['India-EB2-backlog'] - df485_backlog['India-EB2-backlog'].iloc[-1] + \
                                        df485['India-EB2'].iloc[0]*0.25 + df485['India-EB2'].iloc[1:].sum()
    df485_backlog['India-EB3-backlog'] = df485_backlog['India-EB3-backlog'] - df485_backlog['India-EB3-backlog'].iloc[-1] + \
                                        df485['India-EB3'].iloc[0]*0.25 + df485['India-EB3'].iloc[1:].sum()

    df485_backlog = df485_backlog.round().astype(int)

    return df485_backlog



def get_backlog_fig(df485, df_visa, df485_backlog, multiplication_factor):

    def get_interp_backlog(x0, y0):
        x0 = x0 +1
        x1 = np.linspace(x0[0],x0[-1]+1,(1+x0[-1]-x0[0])*12+1)
        f = interpolate.interp1d(x0,y0, fill_value='extrapolate')
        y1 = f(x1)
        y1 = np.array(np.rint(y1), dtype=np.int)
        yr = np.array(x1-3.0/12.0, dtype=np.int)
        mm = (np.arange(x1.size)+9) % 12 + 1
        textdata = [f'{mm}/01/{yr}' for yr, mm in zip(yr, mm)]
        return x1, y1, textdata
        
    x = np.array(list(range(2009,2020)))
    x_for_backlog = np.array(list(range(2008,2020)))
    fig_tabs = []
    for c in ['China','India','Row']:
        df485[f'{c}-EB23'] = df485[f'{c}-EB2'] +df485[f'{c}-EB3'] 
        df_visa[f'{c}-EB23'] = df_visa[f'{c}-EB2'] +df_visa[f'{c}-EB3'] 
        df485_backlog[f'{c}-EB23-backlog'] = df485_backlog[f'{c}-EB2-backlog'] +df485_backlog[f'{c}-EB3-backlog']
    
    backlog_dict = {}
    for eb in [1,23]:
        for c in ['China','India','Row']:
            col = f'{c}-EB{eb}'

            x_backlog, y_backlog, textdata_backlog = get_interp_backlog(x_for_backlog, df485_backlog[f'{col}-backlog'].values)
            backlog_dict['date'] = textdata_backlog
            backlog_dict[col] = y_backlog.tolist()

            fig_data = [
                {'x': x+0.49, 'y': df485[col].values, 'type': 'bar','name':f'{c}-EB{eb} Demand', 'marker':{'color':'#EE4444'},
                        'hovertemplate':'FY%{x:.0f}<br>add %{y}'},
                {'x': x+0.49, 'y': -df_visa[col].values, 'base': 0, 'type': 'bar','name':f'{c}-EB{eb} Issued', 'marker':{'color':'#44EE44'},
                        'hovertemplate':'FY%{x:.0f}<br>clear %{y}'},
                {'x': x_backlog, 'y': y_backlog, 'type': 'lines','name':f'{c}-EB{eb} backlog','marker':{'color':'black'},
                        'mode':'lines+markers','text': textdata_backlog,
                        'hovertemplate':'Total Backlog: %{y}<br>At %{text}'}
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
                        'hovermode':'closest',
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

    return fig_tabs, backlog_dict


def estimate_wait_time(eb_type, pd, future_supply, future_so, backlog_dict):

    def get_backlog_before(eb_type, pd, backlog_dict):
        pd = datetime.datetime.strptime(pd, '%Y-%m-%d').timestamp()
        all_pd = [datetime.datetime.strptime(p, '%m/%d/%Y').timestamp() for p in backlog_dict['date']]
        all_back = backlog_dict[eb_type]
        b = np.interp(pd, all_pd, all_back)
        return int(b)

    if('date' not in backlog_dict or future_supply<=0 or not pd):
        return ''

    bl = get_backlog_before(eb_type, pd, backlog_dict)

    df_visa = load_gc_stats()

    clear_record = get_historical_clear(bl, pd, df_visa, eb_type)

    msg_list = []

    try:
        total_month = 0

        msg_list.append(f'There are {bl} total of {eb_type} green card demands in front of your PD {pd} at the date you filed your case.')

        for i, cr in enumerate(clear_record):
            fy, cl, rm, new_month = cr['fy'], cr['clear'], cr['remaining'], cr['lapsed_month']
            total_month += new_month
            if i==0:
                msg_list.append(f'From {pd} to the end of FY{fy}, {cl} {eb_type} green card demands were cleared, {rm} were still remaining.')
            else:
                msg_list.append(f'During FY{fy}, {cl} {eb_type} green card demands were cleared, {rm} were still remaining.')

        if(len(clear_record)==0):
            remaining_bl = bl
        else:
            remaining_bl = clear_record[-1]['remaining']

        wait_time = remaining_bl/(future_supply+future_so)
        wy = int(wait_time)
        wm = int(np.round((wait_time - wy)*12.0))

        msg_list.append(f' Based on a future annual supply of {future_supply} and annual spillover of {future_so} for {eb_type}, the remaining backlog would need an additional {wy} year {wm} months starting from 2019-10-1.')

        addtional_month = wy*12 + wm
        
        green_month = 10+addtional_month
        green_yr = 2019 + int((green_month-1)/12.0)
        green_month = (green_month-1)%12+1
        msg_list.append(f' Your final action date is likely to become current at {green_yr}-{str(green_month).zfill(2):}.')

        pd_yr = int(pd.split('-')[0])
        pd_mm = int(pd.split('-')[1])
        
        total_month = (green_yr-pd_yr)*12+(green_month-pd_mm)
        total_yr = int(total_month/12)
        total_month -= total_yr*12
        msg_list.append(f' Your total wait time is {total_yr} year and {total_month} months after {pd}')

        msg = '\n\n'.join(msg_list)

    except:
        msg = 'Incorrect Input'

    return dcc.Markdown(msg)


def get_historical_clear(bl, pd, df_visa, eb_type):
    c = eb_type.split('-')[0]
    eb = eb_type.split('-')[1]
    if(eb=='EB23'):
        df_visa[f'{c}-EB23'] = df_visa[f'{c}-EB2'] + df_visa[f'{c}-EB3']

    fy, delta_days = pd_to_FY(pd)

    clear_record = []

    for yr in range(fy,2020):
        clear_record.append({'fy':yr, 'clear': df_visa[eb_type].iloc[yr-2009], 'remaining': 0, 'lapsed_month': 12})
        if(yr==fy):
            supply_fraction, date_fraction = get_yr_fraction(eb_type, yr, delta_days)
            clear_record[-1]['clear']*=supply_fraction
            clear_record[-1]['clear'] = int(clear_record[-1]['clear'])
            clear_record[-1]['lapsed_month']*=date_fraction
            clear_record[-1]['lapsed_month'] = int(clear_record[-1]['lapsed_month']+0.5)

        bl-=clear_record[-1]['clear']
        clear_record[-1]['remaining'] = bl
    
    return clear_record


def pd_to_FY(pd):
    yr, mm, _ = pd.split('-')
    yr = int(yr)
    mm = int(mm)
    fy = yr+1 if mm>=10 else yr

    pd = datetime.datetime.strptime(pd, '%Y-%m-%d')
    fy_begin = datetime.datetime(fy-1, 10, 1)
    days_after_fy_start = (pd-fy_begin).days

    return fy, days_after_fy_start


def get_yr_fraction(eb_type, yr, delta_days):
    fraction = 1.0-delta_days/365.0
    date_fraction = 1.0-delta_days/365.0

    if(eb_type=='China-EB1'):
        if(yr==2017):
            fraction = 1.0-delta_days/(365.0/12.0*8.0)
        elif(yr==2018):
            fraction = 1.0-delta_days/(365.0/12.0*6.0)
    if(fraction<0):
        fraction = 0.0

    return fraction, date_fraction