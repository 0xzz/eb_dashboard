if(!window.dash_clientside) {window.dash_clientside = {};}
window.dash_clientside.clientside = {
    update_fig_stack_mode: function (fig_data, isStack) {
        fig_data_copy = {...fig_data}
        fig_data_copy.layout.barmode = (isStack)?'stack':'group';
        return fig_data_copy
    },
    toggle_stack_msg: function(isStack){
        var msg = (isStack)? 'Switch to Group mode': 'Switch to Stack mode';
        return msg
    },
    display_info: function(n_clicks){
        display_style={'display':'none'}
        if (n_clicks % 2==1) display_style['display'] = 'block';
        var icon_className = (n_clicks % 2==1)? 'fa fa-chevron-up': 'fa fa-question-circle'
        return [display_style,icon_className]
    }
}