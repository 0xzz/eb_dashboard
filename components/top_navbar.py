import dash_bootstrap_components as dbc
import dash_html_components as html


def get_navbar(app_name):

    navbar = dbc.NavbarSimple(
        children=[
            # dbc.NavItem(dbc.NavLink("VB Dates", href="#FAD")),
            # dbc.NavItem(dbc.NavLink("140/485 Annual Data", href="#data_140_485")),
            # dbc.NavItem(dbc.NavLink("Visa Stats", href="#data_140")),
            # dbc.NavItem(dbc.NavLink("Backlog", href="#data_demand")),
            dbc.NavItem(dbc.NavLink("NIU", href="http://www.niunational.org/", target="_Blank", className='navbar-item')),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Quick Nav",
                caret=False,
                # style ={},
                #className = 'navbar-item',#toggle_style={"color": "#FFFFFF", 'margin':'0.75rem', 'font-weight': 200, 'text-decoration-line': 'none'},
                children=[
                    dbc.DropdownMenuItem(getHtmlA("Wait time, Demand & Backlog", "data_demand_backlog")),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem(getHtmlA("Final Action Dates History", "FAD")),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem(getHtmlA("140 Statistics", "data_140")),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem(getHtmlA("Visa Statistics", "data_gc")),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem(getHtmlA("140/485 Annual Data", "data_140_485")),
                ],
            ),
            dbc.NavItem(dbc.Button("Contact Us", color='link', id="contact_us",  className="mr-1 contact-button")),
            dbc.Modal(
                [
                    dbc.ModalHeader("Contact US"),
                    dbc.ModalBody([
                        html.Div("This dashboard is created and maintained by volunteers & members of niunational.org."),
                        html.Div([html.Div("Leave us a comment and/or question, please click ", style={'display':'inline-block'}), html.A(" here.", href="http://www.niunational.org/2020/03/employment-base-eb123.html", target="_blank")]),
                        html.A("Donate to us", href="http://www.niunational.org/p/donation.html", target="_blank")
                    ]),
                    dbc.ModalFooter(
                        html.Div("Thanks!")
                    ),
                ],
                id="contact-us-modal",
            )

        ],
        brand= 'Employment-Based Immigrant Visa Stats',
        brand_style = {'fontSize':'2rem','color':'white'},
        sticky="top",
        color="#6c7ae0",
        # dark=True,
    )

    return navbar

def getHtmlA(name, id):
    return html.A(name, href=f'#{id}')