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

def is_button_clicked(ind, time_stamp_list):
    t0 = time_stamp_list[ind]
    for i, t in enumerate(time_stamp_list):
        if i!=ind and t>=t0:
            return False
    return True

def get_session_obj(session_id):
    '''
    given sesion id, read the session objects from local file system and return the objects
    '''
    file_path = os.path.join('sessions',session_id,'session.pkl')
    with open(file_path,'rb') as f:
        s_obj = pickle.load(f)
    return s_obj

def save_session_obj(sobj):
    '''
    save the session object to the correct location
    '''
    file_path = os.path.join(sobj.dir_path,'session.pkl')
    with open(file_path,'wb') as f:
        pickle.dump(sobj,f)

def found_session(session_id):
    file_path = os.path.join('sessions',session_id,'session.pkl')
    return os.path.isfile(file_path)