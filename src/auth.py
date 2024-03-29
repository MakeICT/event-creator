from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, logout_user, current_user, login_required,\
                        LoginManager, UserMixin

from main import app, loadedPlugins, settings

login_manager = LoginManager()
login_manager.init_app(app)
waplugin = loadedPlugins['WildApricot']

class User(UserMixin):
    def __init__(self, email):
        self.email = email
        self.firstName = ''
        self.lastName = ''
        self.groups = []
        self.id = 0


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page
    """
    # redirect to home page if a user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    url = waplugin.getOauthURL(settings.get('plugin-WildApricot', 'redirect_uri'))
    return redirect(url)

@app.route('/oauth_redirect', methods=['GET', 'POST'])
def oauth():
    """
    Oauth redirect page
    """
    email = waplugin.authenticateWithCode(request.args['code'], settings.get('plugin-WildApricot', 'redirect_uri'))

    user = validateWAUser(email)

    if user:
        login_user(user)
        flash("Login successful!", 'success')
        return redirect(url_for('home'))
    else:
        flash('Login failed!', 'danger')
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        user = validateWAUser(request.form['username'], request.form['password'])
        if not user:
            flash('Please check your login details and try again.', 'danger')
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html', error=error)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """
    Logout the current user.
    """
    if current_user.is_authenticated:
        logout_user()

    return redirect(url_for('home'))


def validateWAUser(username):
    """
    Authenticate username, password and group membership against Wild Apricot
    """
    user = waplugin.loadUser(username)

    if user:
        authorizedGroups = waplugin.getSetting('Authorized Groups').split(',')

        for group in authorizedGroups:
            if user.groups.count(group) > 0:
                return user

    return None
