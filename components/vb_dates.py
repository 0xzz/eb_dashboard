import datetime

import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from .default_config import default_config
from .local_info import get_local_info_component

def get_final_action_dates_figures(app, id, *argv):

    eb1_dates, eb2_dates, eb3_dates = argv[0], argv[1], argv[2]
    
    tabs_content =[
            dcc.Graph(
                figure={
                    'data': [{'x': df['date'], 'y': df[col], 'name':col, 'mode':'lines+markers','hoverinfo':"x+y"} for col in df.columns if col!='date'],
                    'layout': {
                        'title': f'Eb-{i+1} Final Action Dates',
                        'xaxis': {'range':[datetime.datetime(2013,10,1),datetime.datetime(2020,4,1)]},
                        'margin':{'l':35, 'r':25,'b':30},
                        'legend':{'x':.05, 'y':.95,
                                  'bgcolor':"#DDDDDD",
                                  'bordercolor':'gray',
                                  'borderwidth':2},
                    }
                },
                config=default_config,
            ) for i, df in enumerate([eb1_dates, eb2_dates, eb3_dates])]

    tabs_content.append(
            dcc.Graph(
                figure={
                    'data': [{'x': df['date'], 'y': df[f'China-EB{i+1}'], 'name':f'China-EB{i+1}','mode':'lines+markers', 'hoverinfo':"x+y"} 
                    for i, df in enumerate([eb1_dates, eb2_dates, eb3_dates])],
                    'layout': {
                        'title': f'China EB Final Action Dates',
                        'xaxis': {'range':[datetime.datetime(2013,10,1),datetime.datetime(2020,4,1)]},
                        'margin':{'l':35, 'r':25,'b':30},
                        'legend':{'x':.05, 'y':.95,
                                  'bgcolor':"#DDDDDD",
                                  'bordercolor':'gray',
                                  'borderwidth':2},
                    }
                },
                config=default_config,
            ))
    with open("docs/vb.md", "rb") as file:
        vb_faq_md = file.read().decode('utf8')
    info_component = dcc.Markdown(vb_faq_md)
    info_button, info_section = get_local_info_component(app, id, info_component)

    return html.Div([
        dbc.Row([
            html.H4('Final Action Dates History',id=id,style={'display':'inline-block'}),
            info_button
        ], className='Section-Title'),
        info_section,
        dcc.Tabs(children=[
            dcc.Tab([tabs_content[0]],label="EB 1"),
            dcc.Tab([tabs_content[1]],label="EB 2"),
            dcc.Tab([tabs_content[2]],label="EB 3"),
            dcc.Tab([tabs_content[3]],label="China All EB")
        ])
    ])
