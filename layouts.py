import dash_table
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html

import uuid

from helpers import load_140_485_by_FY, load_vb_dates

page_content_frame = html.Div(id='page-content-frame')


def app_layout(app_name):
    '''
    define app layout
    ''' 

    df_140_485 = load_140_485_by_FY()

    tb_layout = dash_table.DataTable(
        id = 'table',
        columns=[{"name": i, "id": i} for i in df_140_485.columns],
        data=df_140_485.to_dict('records'),
        sort_action="native",
        style_cell={
            'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
    )

    fig_140_485_layout = dcc.Graph(
        #id='example-graph',
        figure={
            'data': [{'x': df_140_485['FY'], 'y': df_140_485[col], 'name':col} \
                        for col in df_140_485.columns if col!='FY'],
            'layout': {
                'title': '140/485 data Visualization'
            }
        }
    )


    eb1_dates, eb2_dates, eb3_dates, _ = load_vb_dates()

    fig_vb_dates_layout = html.Div([
        html.Div(
            dcc.Graph(
                #id='example-graph',
                figure={
                    'data': [{'x': df['date'], 'y': df[col], 'name':col, 'hoverinfo':"x+y"} for col in df.columns if col!='date'],
                    'layout': {
                        'title': f'Eb-{i+1} Final Action Dates',
                        'margin':{'l':35, 'r':25,'b':30},
                        'legend':{'x':.05, 'y':.95,
                                  'bgcolor':"#DDDDDD",
                                  'bordercolor':'gray',
                                  'borderwidth':2}
                    }
                },
                config={
                    "displaylogo": False,
                    'modeBarButtonsToRemove': ['lasso2d']
                },
        ), className="col-md-4", style={'padding':'0.5rem','border-radius':'5px'})
        for i, df in enumerate([eb1_dates, eb2_dates, eb3_dates])],
        className = 'row')

    page_titles = html.Div([
        html.H4(f'{app_name}', className = 'my-0 mr-1 font-weight-normal'),
        html.Div(' blablabla ', style={'color':'#225585'}, className='p-2 mr-md-auto'),
        html.Nav([
            #  html.A('About', href = 'https://www.qrigroup.com', target='_blank', className='p-2 text-dark'),
             html.A('About', href = '#', className='p-2 text-dark'),
            #  html.A('Report Issue', href = '#', className='p-2 text-dark'),
        ]),
        html.Div(f'Howdy, xx', className='p-2',style={'margin-left':'15px','margin-right':'15px'}),
        html.Button(id="learn-more-button", children=["Tutorial"], className = 'btn btn-outline-info', style={'margin-right':'15px'}),
    ], className = 'd-flex flex-column flex-md-row align-items-center p-3 px-md-4 mb-3 bg-white border-bottom shadow-sm', style={'height':'60px'})
    
    tutorial_elements = html.Div([
                            html.Div(id='description-text', style={'color':'#225585'}),
                        ])

    hidden_elements = html.Div([
               html.Button('New Data',
                   id='button-New-data',
                   n_clicks_timestamp = -1),
               html.Button('New Crop image',
                   id='button-New-crop',
                   n_clicks_timestamp = -1),
               html.Button('New Color Selected',
                   id='button-New-color-selection',
                   n_clicks_timestamp = -1),
               ], style={'display':'none'})


    top_function_row =  html.Div([
                        html.Div(
                            dcc.Upload(id='upload-log-image',
                                children=html.Div([
                                    'Drag and Drop or ', html.A('Select Image Files', style={'color':'#0088FF', 'text-decoration': 'underline'})
                                ]),
                                style={
                                    'lineHeight': '40px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    #'margin': '10px'
                                },
                                multiple=False
                            ), 
                            style={'display': 'inline-block', 'padding': '5px'},
                            className="col-sm-4"
                        ),
                    ], className="row")

    log_image_html = html.Div(id='graph-holder', children=[
        html.Img(id='graph-div', src=''),
        ], style={'overflow': 'auto', 'max-width': '45vw', 'max-height': '85vh', 'padding': '5px', 'display':'none'}, className="row-sm-4"
    )

    crop_image_html = html.Div(id='crop-graph-holder', children=[
        html.Img(id='crop-graph-div', src=''),
        ], style={'overflow': 'auto', 'max-width': '25vw', 'max-height': '85vh', 'padding': '5px', 'display':'none'}, className="row-sm-3"
    )


    session_summary_table = html.Div([
                            dash_table.DataTable(id='summary-table',
                                columns=[{'name': 'name', 'id': 'name'}, {'name': 'type', 'id': 'type'}, {'name': 'depth range', 'id': 'depth range'}, {'name': 'value-range', 'id': 'value-range'}, {'name': 'unit', 'id': 'unit'}, {'name': 'log scale', 'id': 'log scale'}],
                                row_deletable = True,
                            ),
                            html.Div(id='summary-table-msg')
                        ])

    sidebar_functions =  html.Div(id='sidebar', children=[
                        html.Div([
                            html.H6('Meta Info')
                        ], className = 'sidebar-header'),
                        html.Div([
                            'Curve Name ',
                            dcc.Input(id='input-curve-name', type='text',
                                placeholder="name?",
                                style={'display': 'inline-block', 'margin': '5px'}, 
                                className='col-sm-3'
                            ),
                            'Unit ',
                            dcc.Input(id='input-curve-unit', type='text',
                                placeholder="unit?",
                                style={'display': 'inline-block', 'margin': '5px'}, 
                                className='col-sm-3'
                            )],
                            style={'display':'block','margin':'5px'},
                            className='row'
                        ),
                        html.Div([
                            'Bound:   L',
                            dcc.Input(id='input-left-boundary', type='number',
                                placeholder = 0,
                                style={'display': 'inline-block', 'margin': '5px', 'max-width':'120px'}, 
                            ),
                            'R ',
                            dcc.Input(id='input-right-boundary', type='number',
                                placeholder = 1,
                                style={'display': 'inline-block', 'margin': '5px', 'max-width':'120px'},
                            ),
                            html.Div([
                                html.Div(id='toggle-log-scale-msg', children='Linear Scale'),
                                daq.ToggleSwitch(
                                    id='Toggle-log-scale',
                                    value=False,
                                    size=40,
                                    style={'display': 'inline-block', 'margin': '5px'}, 
                                )], style = {'display': 'inline-block'}
                            )], 
                            style={'display':'block','margin':'5px'},
                            className = 'row'
                        ),
                        html.Div([
                            html.H6('Progress')
                        ], className = 'sidebar-header'),
                        session_summary_table,
                        html.Div([
                            html.H6('AutoWellLog ToolBox', className='p-1 mr-auto'),
                            html.Div([
                                html.Button([
                                    html.I(className="fa fa-undo", style={'font-size':'20px'}),
                                    ' Undo'
                                    ],
                                    id='button-undo',
                                    title = 'Undo last step',
                                    n_clicks_timestamp = -1,
                                    className = 'btn btn-outline-info p-2',
                                    style={'margin':'6px'}
                                ),
                                html.Button([
                                        html.I(className="fa fa-save", style={'font-size':'20px'}),
                                        'Depth'
                                        ],
                                        id='button-add-depth',
                                        title = 'Add the current result as depth',
                                        n_clicks_timestamp = -1,
                                        className = 'btn btn-outline-primary',
                                        style={'margin':'6px'}
                                ),
                                html.Button([
                                        html.I(className="fa fa-save", style={'font-size':'20px'}),
                                        'Result'
                                        ],
                                        id='button-add-result',
                                        title = 'Add current curve/depth to results for later export',
                                        n_clicks_timestamp = -1,
                                        className = 'btn btn-outline-primary',
                                        style={'margin':'6px'}
                                ),
                            ]),
                        ], className = 'sidebar-header d-flex',
                        style={'margin':'10px 0px 5px 0px'}),
                        html.Details([
                            html.Summary('Depth', className='sidebar-header'),
                            html.Div([
                                html.Button('Extract Depth',
                                    id='button-get-depth',
                                    title = 'Extract depth (mD or TVD)',
                                    n_clicks_timestamp = -1,
                                    className = 'btn btn-outline-dark',
                                    style={'margin':'3px'}
                                )])
                            ], open='open', style = {'margin-left':'5px'}),
                        html.Div([
                            'Curve Selection Mode: ',
                            html.Div(id='toggle-curve-output', children='Off'),
                            daq.ToggleSwitch(
                                id='Toggle-Select-Curve',
                                value=False,
                                size=60,
                            )
                        ], className = 'row', style={'display':'none','margin':'4px'}),
                        html.Details([
                            html.Summary('Curve Tracing', className = 'sidebar-header'),
                            html.Div([
                                html.Button('Smart Trace',
                                    id='button-smart-trace',
                                    title = 'Self-Driving Curve Tracing',
                                    n_clicks_timestamp = -1,
                                    className = 'btn btn-outline-dark mr-auto p-1',
                                ),
                                html.Div([
                                    dcc.Slider(id='trace-mode-slider',
                                        min = 0, max=2,
                                        step=None,
                                        marks={0:'left',1:'mid',2:'right'},
                                        value = 1,
                                    )],
                                    style = {'margin': '5px 30px 5px 20px'},
                                    className='p-2 flex-fill'
                                ),
                                html.Div([
                                    dcc.Slider(id='trace-smoothmode-slider',
                                        min = 0, max=3,
                                        step=None,
                                        marks={0:'smoother',1:'',2:'', 3: 'sharper'},
                                        value = 1
                                    )],
                                    style = {'margin': '5px 20px 5px 30px'},
                                    className='p-2 flex-fill',
                                )], className='d-flex', style={'margin':'10px'})
                            ], open='open', style={'margin-left': '5px'}),
                        html.Details([
                            html.Summary('Color Editing',className = 'sidebar-header'),
                            html.Div([
                                html.Span(id='color-picked',
                                        style = {'margin': '8px 8px 1px 8px'},
                                        className='color-dot p-2'),  
                                html.Button('Select Color',
                                    id='button-select-color',
                                    title = 'Only select the picked color',
                                    className = 'btn btn-outline-success p-2 flex-fill',
                                    style={'margin':'3px'},
                                    n_clicks_timestamp = -1),
                                html.Button('Remove Color',
                                    id='button-remove-color',
                                    title = 'Remove picked color',
                                    className = 'btn btn-outline-danger p-2 flex-fill',
                                    style={'margin':'3px'},
                                    n_clicks_timestamp = -1),
                                html.Button('Remove Region',
                                    id='button-remove-region',
                                    title = 'Remove connected region of the same color',
                                    disabled=False,
                                    className = 'btn btn-outline-warning p-2 flex-fill',
                                    style={'margin':'3px'},
                                    n_clicks_timestamp = -1),
                                html.Button('Magic Color',
                                    id='button-reduce-color',
                                    title = 'Smartly group similar colors',
                                    n_clicks_timestamp = -1,
                                    className = 'btn btn-outline-primary p-2 flex-fill',
                                    style={'margin':'3px'})
                            ], className='d-flex')
                        ], open='open', style = {'margin-left':'5px'}),
                        html.Details([
                            html.Summary('Grid Editing',className='sidebar-header'),
                            html.Div([
                                html.Button('Smart Grid Removal',
                                    id='button-remove-grid-adaptive',
                                    title = 'Smart Grid Removal',
                                    n_clicks_timestamp = -1,
                                    className = 'btn btn-outline-dark p-2',
                                    style={'margin':'3px'}
                                ),
                                html.Button('Grid Removal',
                                    id='button-remove-grid-aggressive',
                                    title = 'Standard Grid Removal',
                                    n_clicks_timestamp = -1,
                                    className = 'btn btn-outline-dark p-2',
                                    style={'margin':'3px'},
                                )],
                            style={'margin': '5px'},
                            className='d-flex'),                        
                        ], open='open', style={'margin-left':'5px'}),
                        html.Details([
                            html.Summary('PS tools', className = 'sidebar-header'),
                            html.Div([
                                html.Button('Contrast',
                                    id='button-contrast',
                                    title = 'Increase the contrast of the image',
                                    n_clicks_timestamp = -1,
                                    className = 'btn btn-outline-dark p-2',
                                    style={'margin':'3px', 'width': '90px'}
                                ),
                                html.Button('Sharpen',
                                    id='button-sharpen',
                                    title = 'Sharpen the image',
                                    n_clicks_timestamp = -1,
                                    className = 'btn btn-outline-dark p-2',
                                    style={'margin':'3px', 'width': '90px'}
                                ),
                                html.Button('Denoise',
                                    id='button-denoise',
                                    title = 'Remove noise',
                                    n_clicks_timestamp = -1,
                                    disabled = True,
                                    className = 'btn btn-outline-dark p-2',
                                    style={'margin':'3px', 'width': '90px'}
                                ),
                                html.Button('Edge Detect',
                                    id='button-edge-detection',
                                    title = 'Get Edge',
                                    n_clicks_timestamp = -1,
                                    disabled = True,
                                    className = 'btn btn-outline-dark p-2',
                                    style={'margin':'3px', 'width': '90px'}
                                ),
                                html.Button('Line-Thinner',
                                    id='button-thinner',
                                    title = 'make lines thinner',
                                    n_clicks_timestamp = -1,
                                    disabled = True,
                                    className = 'btn btn-outline-dark p-2',
                                    style={'margin':'3px', 'width': '90px'}
                                ),
                                html.Button('Line-Thicker',
                                    id='button-thicker',
                                    title = 'Make lines thicker',
                                    n_clicks_timestamp = -1,
                                    disabled = True,
                                    className = 'btn btn-outline-dark p-2',
                                    style={'margin':'3px', 'width': '90px'}
                                ),
                                html.Button('Grayscale',
                                    id='button-grayscale',
                                    title = 'Convert to grayscale',
                                    n_clicks_timestamp = -1,
                                    className = 'btn btn-outline-dark p-2',
                                    style={'margin':'3px', 'width': '90px'}
                                )
                                ],className = 'd-flex flex-wrap')
                            ], style = {'margin-left':'5px'}),
                        html.Div([
                            html.H6('Message Box')
                        ], className = 'sidebar-header'),
                        html.Div(id='div-message', style={'margin-left':'5px'})
                    ], className="col-md-3 bg-light sidebar-sticky")


    return html.Div([
              #html.Div(id='qri-auth-frame'),
              page_titles,
              tutorial_elements,
              hidden_elements,
              fig_vb_dates_layout,
              tb_layout,
              fig_140_485_layout,
              top_function_row,
              #log_image,
              html.Div([
                log_image_html,
                crop_image_html
              ], className="row"),
              sidebar_functions,
              #sidebar,
              #session_summary_table,
              #,
            ], className="container-fluid")