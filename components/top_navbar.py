import dash_bootstrap_components as dbc

def get_navbar(app_name):

    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("About", href="#")),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="More",
                caret=False,
                children=[
                    dbc.DropdownMenuItem("Final Action Dates History", href="#FAD"),
                    dbc.DropdownMenuItem("140/485 Data", href="#data_140_485"),
                    dbc.DropdownMenuItem("When can I green?"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Tutorial"),
                    dbc.DropdownMenuItem("USCIS/DOS Links"),
                ],
            ),
        ],
        brand=f'{app_name}',
        brand_style = {'fontSize':'2rem'},
        sticky="top",
        color="lightgray",
        # dark=True,
    )

    return navbar
