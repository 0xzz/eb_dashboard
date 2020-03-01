import datetime
from io import BytesIO
import pickle
import time
import base64
import os

import pandas as pd
import numpy as np

import flask, base64, hashlib
from flask import send_file

from dash.dependencies import Output, Input, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html


from components.analysis_backlog import get_backlog
# from components.data_140_stats import update_140_stats_figure_content
from components.data_gc_stats import update_gc_stats_figure_content

with open("tutorial_description.md", "r") as file:
    tutorial_description_md = file.read()

into_description_md = ''

def set_app_callbacks(app, app_name):

    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='update_140_stats_fig_stack_mode'
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
        Output('140_stats_stack_toggle_display','children'),
        [Input('140_stats_stack_toggle', 'value')]
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
        
    # Callback function for the learn-more button
    @app.callback(
        [Output("description-text", "children"),
         Output("learn-more-button", "children")],
        [Input("learn-more-button", "n_clicks")],
    )
    def learn_more(n_clicks):
        # If clicked odd times, the instructions will show; else (even times), only the header will show
        if n_clicks == None:
            n_clicks = 0
        if (n_clicks % 2) == 1:
            n_clicks += 1
            return (
                html.Div(
                    style={"padding-right": "15%"},
                    children=[dcc.Markdown(tutorial_description_md)],
                ),
                "Close Tutorial",
            )
        else:
            n_clicks += 1
            return (
                html.Div(
                    style={"padding-right": "15%"},
                    children=[dcc.Markdown(into_description_md)],
                ),
                "Tutorial",
            )

    @app.callback(
        Output('demand_div', 'children'),
        [Input(f'factor_{c}-{eb}', 'value') \
            for c in ['China', 'India', 'Row'] \
            for eb in [1,2,3]] \
        + [Input('gc_demand_stack_toggle','value')]
    )
    def update_backlog_analysis(*arg):
        factors = {}
        ind = 0
        for c in ['China','India','Row']:
            for eb in [1,2,3]:
                factors[f'{c}-EB{eb}'] = arg[ind]
                ind+=1
        # print(factors)
        isStack = arg[-1]
        backlog_layout = get_backlog(factors, isStack)
        return backlog_layout


    # @app.callback(
    #     [Output('140_stats_fig', 'figure'),
    #      Output('140_stats_stack_toggle_display','children')],
    #     [Input('140_stats_stack_toggle','value')]
    # )
    # def update_140_stats_figure(isStack):
    #     return update_140_stats_figure_content(isStack),\
    #            'Switch to Group Mode' if isStack else 'Switch to Stack Mode'

    @app.callback(
        [Output('gc_stats_fig', 'figure'),
         Output('gc_stats_stack_toggle_display','children')],
        [Input('gc_stats_stack_toggle','value')]
    )
    def update_gc_analysis(isStack):
        return update_gc_stats_figure_content(isStack),\
               'Switch to Group Mode' if isStack else 'Switch to Stack Mode'

def is_button_clicked(ind, time_stamp_list):
    t0 = time_stamp_list[ind]
    for i, t in enumerate(time_stamp_list):
        if i!=ind and t>=t0:
            return False
    return True