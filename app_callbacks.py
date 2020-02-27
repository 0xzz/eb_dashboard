from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html

import flask, base64, hashlib
from flask import send_file

import datetime
from io import BytesIO
import pickle
import time
import base64

import pandas as pd
import numpy as np

import os
import glob

from components.analysis_backlog import get_backlog

with open("tutorial_description.md", "r") as file:
    tutorial_description_md = file.read()

into_description_md = ''

def set_app_callbacks(app, app_name):

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
        Output('backlog_div', 'children'),
        [Input(f'factor_{c}-{eb}', 'value') \
            for c in ['China', 'India', 'Row'] \
            for eb in [1,2,3]] \
        + [Input('gc_demand_bar_plot_stack','value')]
    )
    def update_backlog_analysis(*arg):
        factors = {}
        ind = 0
        for c in ['China','India','Row']:
            for eb in [1,2,3]:
                factors[f'{c}-EB{eb}'] = arg[ind]
                ind+=1
        print(factors)
        isStack = arg[-1]
        backlog_layout = get_backlog(factors, isStack)
        return backlog_layout


def is_button_clicked(ind, time_stamp_list):
    t0 = time_stamp_list[ind]
    for i, t in enumerate(time_stamp_list):
        if i!=ind and t>=t0:
            return False
    return True