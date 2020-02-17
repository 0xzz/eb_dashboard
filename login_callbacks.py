import flask
import json
import hashlib

from dash.dependencies import Output, Input
from layouts import login_layout, app_layout


def set_login_callbacks(app, _app_route, app_name):

    @app.callback(Output('page-content-frame', 'children'),
                [Input('page-content-frame', 'id')])
    def dynamic_layout(_):
        session_cookie = flask.request.cookies.get('qri-auth-session')
        if not session_cookie:
            # If there's no cookie we need to login.
            return login_layout(app_name)
        return  app_layout(app_name,session_cookie = session_cookie, 
                        dcc_logout_url = '/logout')

    # Create a login route
    @app.server.route('/login', methods=['POST'])
    def route_login():
        data = flask.request.form
        username = data.get('username')
        password = data.get('password')
        hashed_password = hashlib.sha224(password.encode('utf-8')).hexdigest()

        with open('users.json') as json_file:
            users_list = json.load(json_file)
            print(users_list)

        if not username or not password:
            flask.abort(401)

        if username not in users_list or users_list[username]!=hashed_password:
            flask.abort(401)
        # actual implementation should verify the password.
        # Recommended to only keep a hash in database and use something like
        # bcrypt to encrypt the password and check the hashed results.

        # Return a redirect with
        rep = flask.redirect(_app_route)

        # Here we just store the given username in a cookie.
        # Actual session cookies should be signed or use a JWT token.

        rep.set_cookie('qri-auth-session', username, max_age=10)
        return rep
    
    @app.server.route('/logout', methods=['POST'])
    def route_logout():
        # Redirect back to the index and remove the session cookie.
        rep = flask.redirect(_app_route) #or '/'
        rep.set_cookie('qri-auth-session', '', expires=0)
        return rep