    
import dash_html_components as html
import dash_daq as daq
              
def get_toggle(toggle_id, default_Value = True):
    return html.Div([
    html.Div('Switch Stack/Group Mode',id = toggle_id+'_display', style={'display':'inline-block'}),
    html.Div([daq.ToggleSwitch(
        id=toggle_id,
        value=default_Value
    )], style = {'display':'inline-block'})
    ])