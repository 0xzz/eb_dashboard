
import dash_table
import dash_html_components as html

def get_table(df):
    return dash_table.DataTable(
            style_data={
                'whiteSpace': 'narrow',
                'height': 'auto',
                'border': 'none'
            },
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            style_cell={
                'whiteSpace': 'narrow',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'backgroundColor': 'rgb(235, 235, 235)',
            },
            style_as_list_view=True,
            style_table={'overflowX':'scroll'},
            style_header={
                'backgroundColor': '#379683',
                'fontWeight': 'bold',
                'font-size': '1.2rem',
                'color': 'white',
                'padding':'0.3rem'
            },
            style_data_conditional=[{
                'if': {'column_id': 'FY'},
                #'backgroundColor': '#379683',
                'fontWeight': 'bold',
                #'color': 'white',
            },
             {
            'if': {'row_index': 'even'},
            'backgroundColor': '#f8f6ff'
            }]
        )
