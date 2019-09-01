from flask import render_template, url_for, redirect, request, session, Flask, Response, flash
from flask_login import login_user, logout_user, current_user, login_required, LoginManager, UserMixin

from plugins import WildApricot
from main import app, loadedPlugins

login_manager = LoginManager()
login_manager.init_app(app)


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
    
    error = None
    if request.method == 'POST':        
        user = validateWAUser(request.form['username'], request.form['password'])
        if user is None:
            flash('Please check your login details and try again.')
        else:
            login_user(user)
            return redirect(url_for('home'))
        
    
        """Logout the current user."""
    user = current_user
    
    if user is not None:
        user.authenticated = False
        logout_user()
            
    return render_template('login.html', error=error)

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    
    if user is not None:
        user.authenticated = False
        logout_user()
        
    return render_template("login.html")

def validateWAUser(username, password):
    waplugin = loadedPlugins['WildApricot']
#    approved = waplugin.isUserValid(username, password)
# 
#    if not approved:
#        return None
    
    user = waplugin.loadUser(username, password)
    
    if user is None:
        return None
    
    try:
        groups = user.groups
    
        authorizedGroups = waplugin.getSetting('Authorized Groups').split(',')
        
        for group in authorizedGroups:
            if groups.count(group) > 0:
                return user
    except:
        return None
    
    return None