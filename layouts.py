import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

# import uuid

from components.top_navbar import get_navbar
from components.intro import get_intro
from components.vb_dates import get_final_action_dates_figures
from components.data_140_485 import get_overall_140_485_view
from components.data_140_stats import get_140_stats
from components.data_gc_stats import get_gc_stats_layout
from components.analysis_backlog import get_demand_backlog_layout

from helpers import load_vb_dates, load_140_485_by_FY, load_140_stats, load_gc_stats

def get_app_layout(app, app_name):
    '''
    define app layout
    ''' 

    #load data
    eb1_vb, eb2_vb, eb3_vb = load_vb_dates()
    df_140_485 = load_140_485_by_FY()
    df_140_details = load_140_stats()
    df_gc = load_gc_stats()

    navbar = get_navbar(app_name)

    intro_layout = get_intro()

    fig_vb_dates_layout = get_final_action_dates_figures(app, 'FAD', eb1_vb, eb2_vb, eb3_vb)

    overall_140_485_layout = get_overall_140_485_view(app, 'data_140_485', df_140_485)

    stats_140_layout = get_140_stats(app, 'data_140', df_140_details)

    gc_stats_layout = get_gc_stats_layout(app, 'data_gc', df_gc)

    demand_backlog_layout = get_demand_backlog_layout(app, 'data_demand_backlog')

    return html.Div([
              navbar,
              intro_layout,
              demand_backlog_layout,
              fig_vb_dates_layout,
              stats_140_layout,
              gc_stats_layout,
              overall_140_485_layout,
            ], className="container-fluid")




    # page_titles = html.Div([
    #     html.H4(f'{app_name}', className = 'my-0 mr-1 font-weight-normal'),
    #     html.Div(' blablabla ', style={'color':'#225585'}, className='p-2 mr-md-auto'),
    #     html.Nav([
    #         #  html.A('About', href = 'https://www.qrigroup.com', target='_blank', className='p-2 text-dark'),
    #          html.A('About', href = '#', className='p-2 text-dark'),
    #         #  html.A('Report Issue', href = '#', className='p-2 text-dark'),
    #     ]),
    #     html.Div(f'Howdy, xx', className='p-2',style={'margin-left':'15px','margin-right':'15px'}),
    #     html.Button(id="learn-more-button", children=["Tutorial"], className = 'btn btn-outline-info', style={'margin-right':'15px'}),
    # ], className = 'd-flex flex-column flex-md-row align-items-center p-3 px-md-4 mb-3 bg-white border-bottom shadow-sm', style={'height':'60px'})
    
    # tutorial_elements = html.Div([
    #                         html.Div(id='description-text', style={'color':'#225585'}),
    #                     ])

    # hidden_elements = html.Div([
    #            html.Button('New Data',
    #                id='button-New-data',
    #                n_clicks_timestamp = -1),
    #            html.Button('New Crop image',
    #                id='button-New-crop',
    #                n_clicks_timestamp = -1),
    #            html.Button('New Color Selected',
    #                id='button-New-color-selection',
    #                n_clicks_timestamp = -1),
    #            ], style={'display':'none'})


    # sidebar_functions =  html.Div(id='sidebar', children=[
    #                     html.Div([
    #                         html.H6('Meta Info')
    #                     ], className = 'sidebar-header'),
    #                     html.Div([
    #                         'Curve Name ',
    #                         dcc.Input(id='input-curve-name', type='text',
    #                             placeholder="name?",
    #                             style={'display': 'inline-block', 'margin': '5px'}, 
    #                             className='col-sm-3'
    #                         ),
    #                         'Unit ',
    #                         dcc.Input(id='input-curve-unit', type='text',
    #                             placeholder="unit?",
    #                             style={'display': 'inline-block', 'margin': '5px'}, 
    #                             className='col-sm-3'
    #                         )],
    #                         style={'display':'block','margin':'5px'},
    #                         className='row'
    #                     ),
    #                     html.Div([
    #                         'Bound:   L',
    #                         dcc.Input(id='input-left-boundary', type='number',
    #                             placeholder = 0,
    #                             style={'display': 'inline-block', 'margin': '5px', 'max-width':'120px'}, 
    #                         ),
    #                         'R ',
    #                         dcc.Input(id='input-right-boundary', type='number',
    #                             placeholder = 1,
    #                             style={'display': 'inline-block', 'margin': '5px', 'max-width':'120px'},
    #                         ),
    #                         html.Div([
    #                             html.Div(id='toggle-log-scale-msg', children='Linear Scale'),
    #                             daq.ToggleSwitch(
    #                                 id='Toggle-log-scale',
    #                                 value=False,
    #                                 size=40,
    #                                 style={'display': 'inline-block', 'margin': '5px'}, 
    #                             )], style = {'display': 'inline-block'}
    #                         )], 
    #                         style={'display':'block','margin':'5px'},
    #                         className = 'row'
    #                     ),
    #                     html.Div([
    #                         html.H6('Progress')
    #                     ], className = 'sidebar-header'),
    #                     html.Div([
    #                         html.H6('AutoWellLog ToolBox', className='p-1 mr-auto'),
    #                         html.Div([
    #                             html.Button([
    #                                 html.I(className="fa fa-undo", style={'font-size':'20px'}),
    #                                 ' Undo'
    #                                 ],
    #                                 id='button-undo',
    #                                 title = 'Undo last step',
    #                                 n_clicks_timestamp = -1,
    #                                 className = 'btn btn-outline-info p-2',
    #                                 style={'margin':'6px'}
    #                             ),
    #                             html.Button([
    #                                     html.I(className="fa fa-save", style={'font-size':'20px'}),
    #                                     'Depth'
    #                                     ],
    #                                     id='button-add-depth',
    #                                     title = 'Add the current result as depth',
    #                                     n_clicks_timestamp = -1,
    #                                     className = 'btn btn-outline-primary',
    #                                     style={'margin':'6px'}
    #                             ),
    #                             html.Button([
    #                                     html.I(className="fa fa-save", style={'font-size':'20px'}),
    #                                     'Result'
    #                                     ],
    #                                     id='button-add-result',
    #                                     title = 'Add current curve/depth to results for later export',
    #                                     n_clicks_timestamp = -1,
    #                                     className = 'btn btn-outline-primary',
    #                                     style={'margin':'6px'}
    #                             ),
    #                         ]),
    #                     ], className = 'sidebar-header d-flex',
    #                     style={'margin':'10px 0px 5px 0px'}),
    #                     html.Details([
    #                         html.Summary('Depth', className='sidebar-header'),
    #                         html.Div([
    #                             html.Button('Extract Depth',
    #                                 id='button-get-depth',
    #                                 title = 'Extract depth (mD or TVD)',
    #                                 n_clicks_timestamp = -1,
    #                                 className = 'btn btn-outline-dark',
    #                                 style={'margin':'3px'}
    #                             )])
    #                         ], open='open', style = {'margin-left':'5px'}),
    #                     html.Div([
    #                         'Curve Selection Mode: ',
    #                         html.Div(id='toggle-curve-output', children='Off'),
    #                         daq.ToggleSwitch(
    #                             id='Toggle-Select-Curve',
    #                             value=False,
    #                             size=60,
    #                         )
    #                     ], className = 'row', style={'display':'none','margin':'4px'}),
    #                     html.Details([
    #                         html.Summary('Curve Tracing', className = 'sidebar-header'),
    #                         html.Div([
    #                             html.Button('Smart Trace',
    #                                 id='button-smart-trace',
    #                                 title = 'Self-Driving Curve Tracing',
    #                                 n_clicks_timestamp = -1,
    #                                 className = 'btn btn-outline-dark mr-auto p-1',
    #                             ),
    #                             html.Div([
    #                                 dcc.Slider(id='trace-mode-slider',
    #                                     min = 0, max=2,
    #                                     step=None,
    #                                     marks={0:'left',1:'mid',2:'right'},
    #                                     value = 1,
    #                                 )],
    #                                 style = {'margin': '5px 30px 5px 20px'},
    #                                 className='p-2 flex-fill'
    #                             ),
    #                             html.Div([
    #                                 dcc.Slider(id='trace-smoothmode-slider',
    #                                     min = 0, max=3,
    #                                     step=None,
    #                                     marks={0:'smoother',1:'',2:'', 3: 'sharper'},
    #                                     value = 1
    #                                 )],
    #                                 style = {'margin': '5px 20px 5px 30px'},
    #                                 className='p-2 flex-fill',
    #                             )], className='d-flex', style={'margin':'10px'})
    #                         ], open='open', style={'margin-left': '5px'}),
    #                     html.Details([
    #                         html.Summary('Color Editing',className = 'sidebar-header'),
    #                         html.Div([
    #                             html.Span(id='color-picked',
    #                                     style = {'margin': '8px 8px 1px 8px'},
    #                                     className='color-dot p-2'),  
    #                             html.Button('Select Color',
    #                                 id='button-select-color',
    #                                 title = 'Only select the picked color',
    #                                 className = 'btn btn-outline-success p-2 flex-fill',
    #                                 style={'margin':'3px'},
    #                                 n_clicks_timestamp = -1),
    #                             html.Button('Remove Color',
    #                                 id='button-remove-color',
    #                                 title = 'Remove picked color',
    #                                 className = 'btn btn-outline-danger p-2 flex-fill',
    #                                 style={'margin':'3px'},
    #                                 n_clicks_timestamp = -1),
    #                             html.Button('Remove Region',
    #                                 id='button-remove-region',
    #                                 title = 'Remove connected region of the same color',
    #                                 disabled=False,
    #                                 className = 'btn btn-outline-warning p-2 flex-fill',
    #                                 style={'margin':'3px'},
    #                                 n_clicks_timestamp = -1),
    #                             html.Button('Magic Color',
    #                                 id='button-reduce-color',
    #                                 title = 'Smartly group similar colors',
    #                                 n_clicks_timestamp = -1,
    #                                 className = 'btn btn-outline-primary p-2 flex-fill',
    #                                 style={'margin':'3px'})
    #                         ], className='d-flex')
    #                     ], open='open', style = {'margin-left':'5px'}),
    #                     html.Details([
    #                         html.Summary('Grid Editing',className='sidebar-header'),
    #                         html.Div([
    #                             html.Button('Smart Grid Removal',
    #                                 id='button-remove-grid-adaptive',
    #                                 title = 'Smart Grid Removal',
    #                                 n_clicks_timestamp = -1,
    #                                 className = 'btn btn-outline-dark p-2',
    #                                 style={'margin':'3px'}
    #                             ),
    #                             html.Button('Grid Removal',
    #                                 id='button-remove-grid-aggressive',
    #                                 title = 'Standard Grid Removal',
    #                                 n_clicks_timestamp = -1,
    #                                 className = 'btn btn-outline-dark p-2',
    #                                 style={'margin':'3px'},
    #                             )],
    #                         style={'margin': '5px'},
    #                         className='d-flex'),                        
    #                     ], open='open', style={'margin-left':'5px'}),
    #                     html.Details([
    #                         html.Summary('PS tools', className = 'sidebar-header'),
    #                         html.Div([
    #                             html.Button('Contrast',
    #                                 id='button-contrast',
    #                                 title = 'Increase the contrast of the image',
    #                                 n_clicks_timestamp = -1,
    #                                 className = 'btn btn-outline-dark p-2',
    #                                 style={'margin':'3px', 'width': '90px'}
    #                             ),
    #                             html.Button('Sharpen',
    #                                 id='button-sharpen',
    #                                 title = 'Sharpen the image',
    #                                 n_clicks_timestamp = -1,
    #                                 className = 'btn btn-outline-dark p-2',
    #                                 style={'margin':'3px', 'width': '90px'}
    #                             ),
    #                             html.Button('Denoise',
    #                                 id='button-denoise',
    #                                 title = 'Remove noise',
    #                                 n_clicks_timestamp = -1,
    #                                 disabled = True,
    #                                 className = 'btn btn-outline-dark p-2',
    #                                 style={'margin':'3px', 'width': '90px'}
    #                             ),
    #                             html.Button('Edge Detect',
    #                                 id='button-edge-detection',
    #                                 title = 'Get Edge',
    #                                 n_clicks_timestamp = -1,
    #                                 disabled = True,
    #                                 className = 'btn btn-outline-dark p-2',
    #                                 style={'margin':'3px', 'width': '90px'}
    #                             ),
    #                             html.Button('Line-Thinner',
    #                                 id='button-thinner',
    #                                 title = 'make lines thinner',
    #                                 n_clicks_timestamp = -1,
    #                                 disabled = True,
    #                                 className = 'btn btn-outline-dark p-2',
    #                                 style={'margin':'3px', 'width': '90px'}
    #                             ),
    #                             html.Button('Line-Thicker',
    #                                 id='button-thicker',
    #                                 title = 'Make lines thicker',
    #                                 n_clicks_timestamp = -1,
    #                                 disabled = True,
    #                                 className = 'btn btn-outline-dark p-2',
    #                                 style={'margin':'3px', 'width': '90px'}
    #                             ),
    #                             html.Button('Grayscale',
    #                                 id='button-grayscale',
    #                                 title = 'Convert to grayscale',
    #                                 n_clicks_timestamp = -1,
    #                                 className = 'btn btn-outline-dark p-2',
    #                                 style={'margin':'3px', 'width': '90px'}
    #                             )
    #                             ],className = 'd-flex flex-wrap')
    #                         ], style = {'margin-left':'5px'}),
    #                     html.Div([
    #                         html.H6('Message Box')
    #                     ], className = 'sidebar-header'),
    #                     html.Div(id='div-message', style={'margin-left':'5px'})
    #                 ], className="col-md-3 bg-light sidebar-sticky")
