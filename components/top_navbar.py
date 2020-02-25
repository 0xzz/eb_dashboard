import dash_bootstrap_components as dbc
import dash_html_components as html


def get_navbar(app_name):

    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("About", href="#")),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="More",
                caret=False,
                color='Info',
                children=[
                    dbc.DropdownMenuItem(getHtmlA("Final Action Dates History", "FAD")),
                    dbc.DropdownMenuItem(getHtmlA("140/485 Anual Data", "data_140_485")),
                    dbc.DropdownMenuItem(getHtmlA("140 Statistics", "data_140")),
                    dbc.DropdownMenuItem(getHtmlA("Visa Statistics", "data_gc")),
                    dbc.DropdownMenuItem(getHtmlA("Backlog Analysis", "data_backlog")),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("When can I green?"),
                    dbc.DropdownMenuItem("Tutorial"),
                    dbc.DropdownMenuItem("USCIS/DOS Links"),
                ],
            ),
        ],
        brand= 'Employment-Based Immigrant Visa Stats',
        brand_style = {'fontSize':'2rem'},
        sticky="top",
        color="#DFEEFF",
        # dark=True,
    )

    return navbar

def getHtmlA(name, id):
    return html.A(name, href=f'#{id}')