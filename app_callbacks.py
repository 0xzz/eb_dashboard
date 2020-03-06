import datetime
from io import BytesIO
import json
import pickle
import base64
import os

import pandas as pd
import numpy as np

import flask, base64, hashlib
from flask import send_file

import requests

from dash.dependencies import Output, Input, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html

from components.analysis_backlog import update_backlog_components, estimate_wait_time

def get_ip():
    if not flask.request.headers.getlist("X-Forwarded-For"):
        ip = flask.request.remote_addr
    else:
        ip = flask.request.headers.getlist("X-Forwarded-For")[0]
    return ip

def set_app_callbacks(app, db_url):

    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='update_fig_stack_mode'
        ),
        Output('140_stats_fig', 'figure'),
        [Input('140_stats_figure_data', 'data'),
        Input('140_stats_stack_toggle', 'value')]
    )
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggle_stack_msg'
        ),
        Output('140_stats_stack_toggle_display', 'children'),
        [Input('140_stats_stack_toggle', 'value')]
    )

    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='update_fig_stack_mode'
        ),
        Output('data_gc_figure', 'figure'),
        [Input('data_gc_figure_data', 'data'),
        Input('gc_stats_stack_toggle', 'value')]
    )

    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggle_stack_msg'
        ),
        Output('gc_stats_stack_toggle_display', 'children'),
        [Input('gc_stats_stack_toggle', 'value')]
    )

    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='update_fig_stack_mode'
        ),
        Output('gc_demand_figure', 'figure'),
        [Input('gc_demand_figure_content', 'data'),
        Input('gc_demand_stack_toggle', 'value')]
    )
    
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggle_stack_msg'
        ),
        Output('gc_demand_stack_toggle_display', 'children'),
        [Input('gc_demand_stack_toggle', 'value')]
    )


    @app.callback(
        Output("contact-us-modal", "is_open"),
        [Input("contact_us", "n_clicks")],
        [State("contact-us-modal", "is_open")]
    )
    def toggle_contact_us_modal(n1, is_open):
        if n1:
            return not is_open
        return is_open
        
    @app.callback(
        [Output('gc_demand_figure_content', 'data'),
        Output('gc_demand_table_layout', 'children'),
        Output('gc_backlogs_tabs', 'children'),
        Output('gc_backlogs_data', 'data')],        
        [Input(f'factor_{c}-{eb}', 'value') \
            for c in ['China', 'India', 'Row'] \
            for eb in [1,2,3]]
    )
    def update_backlog_analysis(*arg):
        factors = {}
        ind = 0
        for c in ['China','India','Row']:
            for eb in [1,2,3]:
                factors[f'{c}-EB{eb}'] = arg[ind]
                ind+=1
        demand_fig_content, demand_table, backlogs_tabs, backlog_dict = update_backlog_components(factors)
        return demand_fig_content, demand_table, backlogs_tabs, backlog_dict

    @app.callback(
        Output('multifactor_placeholder','children'),
        [Input('user-eb-type','value')] + [Input(f'factor_{c}-{eb}', 'value') \
            for c in ['China', 'India', 'Row'] \
            for eb in [1,2,3]]
    )
    def update_mf_factor_for_vb_prediction(eb_type, *args):
        ci = ['China','India','Row'].index(eb_type.split('-')[0])
        eb = eb_type.split('-')[1][2:]
        if (eb=='1'):
            mf_msg = args[ci*3+0]
        else:
            mf_msg = f'{args[ci*3+1]} (EB2), {args[ci*3+2]} (EB3)'
        return mf_msg

    @app.callback(
        [Output('pd-picker','min_date_allowed'),
        Output('designed-annual-supply-info-div','children'),
        Output('designed-annual-supply','children')],
        [Input('user-eb-type','value')],
        [State(f'factor_{c}-{eb}', 'value') \
            for c in ['China', 'India', 'Row'] \
            for eb in [1,2,3]]
    )
    def update_pd_related_defaults(eb_type, *args):

        info_msg = f'Annual Supply for {eb_type} after FY2019'
        min_pd_date = datetime.datetime(2017,6,2)
        annual_supply = 3000
        if(eb_type=='China-EB23'):
            min_pd_date = datetime.datetime(2015,8,1)
            annual_supply = 6000
        elif (eb_type=='India-EB1'):
            min_pd_date = datetime.datetime(2015,3,1)
        elif (eb_type=='India-EB23'):
            min_pd_date = datetime.datetime(2009,1,1)
            annual_supply = 6000
        elif (eb_type=='Row-EB1'):
            min_pd_date = datetime.datetime(2019,3,1)
            annual_supply = 32000
        elif (eb_type=='Row-EB23'):
            min_pd_date = datetime.datetime(2017,1,1)
            annual_supply = 64000

        return min_pd_date, info_msg, annual_supply

    @app.callback(
        Output('wait-time-estimation','children'),
        [Input('button-estimate-wait-time','n_clicks'),
         Input('gc_backlogs_data', 'data')],
        [State('user-eb-type','value'),
        State('multifactor_placeholder','children'),
        State('pd-picker','date'),
        State('designed-annual-supply','children'),
        State('future-annual-so','value')]
    )
    def call_estimate_wait_time(n_clicks, backlog_dict, eb_type, mf_msg, pd, future_supply, future_so):
        if(pd):
            pd = pd.split(' ')[0]
            pred_results = estimate_wait_time(eb_type, pd, future_supply, future_so, backlog_dict)
            if(n_clicks):
                user_ip = get_ip()
                new_prediction_record = {
                    'timestamp': datetime.datetime.now().__str__(), 
                    'ip': user_ip,
                    'pd': pd,
                    'eb_type': eb_type,
                    'multiFactor': mf_msg,
                    'future_supply': future_supply,
                    'future_so':future_so,
                    'results': pred_results
                }
                res = requests.post(f'https://{db_url}/prediction_record.json', data = json.dumps(new_prediction_record))

                res = requests.get(f'https://{db_url}/prediction_count.json')
                count_record = res.json()
                count_record['count'] += 1
                res = requests.put(f'https://{db_url}/prediction_count.json', data = json.dumps(count_record))
            return pred_results
        else:
            return ''

    @app.callback(
        Output('access_count','value'),
        [Input('dummy-page-div','children')]
    )
    def upload_access_count(c):
        res = requests.get(f'https://{db_url}/count.json')
        count_record = res.json()
        count_record['count'] += 1
        res = requests.put(f'https://{db_url}/count.json', data = json.dumps(count_record))
        
        user_ip = get_ip()
        if user_ip!='127.0.0.1':
            new_access_record = {'timestamp': datetime.datetime.now().__str__(), 'ip': user_ip}
            res = requests.post(f'https://{db_url}/access_record.json', data = json.dumps(new_access_record))
            print(new_access_record)
            
        return count_record['count']

def is_button_clicked(ind, time_stamp_list):
    t0 = time_stamp_list[ind]
    for i, t in enumerate(time_stamp_list):
        if i!=ind and t>=t0:
            return False
    return True