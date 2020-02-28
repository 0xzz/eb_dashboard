
import dash_table
import dash_html_components as html

def get_table(df):
    return html.Div([
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            sort_action="native",
            style_cell={
                'minWidth': '40px', 'width': '50px', 'maxWidth': '80px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
        )
    ], style = {'overflow-x':'auto'})
