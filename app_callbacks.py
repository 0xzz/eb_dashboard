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

from dash.dependencies import Output, Input, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html

from components.analysis_backlog import update_backlog_components, estimate_wait_time

def set_app_callbacks(app, app_name):

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
        # with open('backlog.json','w') as f:
        #     json.dump(backlog_dict, f)

        return demand_fig_content, demand_table, backlogs_tabs, backlog_dict

    @app.callback(
        [Output('pd-picker','min_date_allowed'),
        Output('future-annual-supply-info-div','children'),
        Output('future-annual-supply','value'),
        Output('multifactor_placeholder','children')],
        [Input('user-eb-type','value')],
        [State(f'factor_{c}-{eb}', 'value') \
            for c in ['China', 'India', 'Row'] \
            for eb in [1,2,3]]
    )
    def update_pd_related_defaults(eb_type, *args):
        ci = ['China','India','Row'].index(eb_type.split('-')[0])
        eb = eb_type.split('-')[1][2:]
        if (eb=='1'):
            mf_msg = args[ci*3+0]
        else:
            mf_msg = f'EB2 {args[ci*3+1]}, EB3 {args[ci*3+2]}'

        info_msg = f'Annual Supply for {eb_type}'
        min_pd_date = datetime.datetime(2017,6,2)
        annual_supply = 3000
        if(eb_type=='China-EB23'):
            min_pd_date = datetime.datetime(2015,8,1)
            annual_supply = 6000
        return min_pd_date, info_msg, annual_supply, mf_msg

    @app.callback(
        Output('wait-time-estimation','children'),
        [Input('user-eb-type','value'),
        Input('pd-picker','date'),
        Input('future-annual-supply','value'),
        Input('future-annual-so','value'),
        Input('gc_backlogs_data', 'data')]
    )
    def call_estimate_wait_time( eb_type, pd, future_supply, future_so, backlog_dict):
        pd = pd.split(' ')[0]
        return estimate_wait_time(eb_type, pd, future_supply, future_so, backlog_dict)

    # @app.callback(
    #     Output('demand_div', 'children'),
    #     [Input(f'factor_{c}-{eb}', 'value') \
    #         for c in ['China', 'India', 'Row'] \
    #         for eb in [1,2,3]] \
    #     + [Input('gc_demand_stack_toggle','value')]
    # )
    # def update_backlog_analysis(*arg):
    #     factors = {}
    #     ind = 0
    #     for c in ['China','India','Row']:
    #         for eb in [1,2,3]:
    #             factors[f'{c}-EB{eb}'] = arg[ind]
    #             ind+=1
    #     # print(factors)
    #     isStack = arg[-1]
    #     backlog_layout = get_backlog(factors, isStack)
    #     return backlog_layout

    # @app.callback(
    #     Output('gc_stats_fig', 'figure'),
    #     [Input('gc_stats_stack_toggle','value')]
    # )
    # def update_gc_analysis(isStack):
    #     return update_gc_stats_figure_content(isStack)

def is_button_clicked(ind, time_stamp_list):
    t0 = time_stamp_list[ind]
    for i, t in enumerate(time_stamp_list):
        if i!=ind and t>=t0:
            return False
    return True