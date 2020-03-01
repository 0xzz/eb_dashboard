if(!window.dash_clientside) {window.dash_clientside = {};}
window.dash_clientside.clientside = {
    update_140_stats_fig_stack_mode: function (fig_data, isStack) {
        fig_data["layout"]["barmode"] = (isStack)?'stack':'group';
        return fig_data
    },
    toggle_stack_msg: function(isStack){
        var msg = (isStack)? 'Switch to Group mode': 'Switch to Stack mode';
        return msg
    }
}