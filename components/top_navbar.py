import dash_bootstrap_components as dbc
import dash_html_components as html


def get_navbar(app_name):

    navbar = dbc.NavbarSimple(
        children=[
            # dbc.NavItem(dbc.NavLink("VB Dates", href="#FAD")),
            # dbc.NavItem(dbc.NavLink("140/485 Annual Data", href="#data_140_485")),
            # dbc.NavItem(dbc.NavLink("Visa Stats", href="#data_140")),
            # dbc.NavItem(dbc.NavLink("Backlog", href="#data_demand")),
            dbc.NavItem(dbc.NavLink("NIU", href="http://www.niunational.org/", target="_Blank", style={'margin-top':'0.75rem','color':'white','fontWeidth':'bold'})),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Quick Nav",
                caret=False,
                color='Info',
                toggle_style ={'color':'white !important','fontWeidth':'bold','margin-top':'0.75rem'},
                children=[
                    dbc.DropdownMenuItem(getHtmlA("Wait time, Demand & Backlog", "data_demand_backlog")),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem(getHtmlA("Final Action Dates History", "FAD")),
                    dbc.DropdownMenuItem(getHtmlA("140 Statistics", "data_140")),
                    dbc.DropdownMenuItem(getHtmlA("Visa Statistics", "data_gc")),
                    dbc.DropdownMenuItem(getHtmlA("140/485 Annual Data", "data_140_485")),
                ],
            ),
            dbc.NavItem(dbc.Button("Contact Us", color='link', id="contact_us",  className="mr-1", style={'margin':'5px','font-size':'1.3rem','color':'white','fontWeidth':'bold'})),
            dbc.Modal(
                [
                    dbc.ModalHeader("Contact US"),
                    dbc.ModalBody([
                        html.Div("This dashboard is created and maintained by volunteers & members of niunational.org."),
                        html.Div([html.Div("For comments & question, "), html.A("send us an email!", href="mailto: xiang.zhai@niunational.org")]),
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
        brand_style = {'fontSize':'2rem','color':'white','fontWeidth':'bold'},
        sticky="top",
        color="#6c7ae0",
        # dark=True,
    )

    return navbar

def getHtmlA(name, id):
    return html.A(name, href=f'#{id}')