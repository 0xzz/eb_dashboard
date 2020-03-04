import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from .default_config import default_config
from .get_table import get_table
from .local_info import get_local_info_component

def get_overall_140_485_view(app, id, df_140_485):

    tb_layout = get_table(df_140_485)

    figure_data = [{'x': df_140_485['FY'], 
                      'y': df_140_485[col], 
                      'name':col,
                      'visible':True if 'approved' in col else 'legendonly'} \
                     for col in df_140_485.columns if col!='FY']
    figure_data.append({'x':[2011.5,2019.5],'y':[14e4/6.5*3.0,14e4/6.5*3.0],
                        'mode':'lines','line':{'color':'black','dash':'dash'},'name':'Safe 140 threshold'})

    fig_140_485_layout = dcc.Graph(
        figure={
            'data': figure_data,
            'layout': {
                'title': '140/485 data Visualization'
            }
        },
        config=default_config,
    )

    with open("docs/total_140_485.md", "rb") as file:
        faq_md = file.read().decode('utf8')
    info_component = dcc.Markdown(faq_md)
    info_button, info_section = get_local_info_component(app, id, info_component)

    return html.Div([
        dbc.Row([
            html.H4('140/485 Annual numbers Summary', id=id),
            info_button
        ], className='Section-Title'),
        info_section,
        dcc.Tabs([
            dcc.Tab(fig_140_485_layout,label="View Trend"),
            dcc.Tab(tb_layout,label="View Table")
        ])
    ])