from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_oauth import OAuth
from forms import NewClassForm
from attrdict import AttrDict
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import plugins
from plugins import WildApricot, MakerspaceAuthorizations
import json
from config import settings
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime

targets = []
actions = {}
loadedPlugins = {}

populationTypes = ['Everybody']
lastTemplateFile = None


app = Flask(__name__)

app.config['SECRET_KEY'] = settings.get('General', 'SECRET_KEY')
app.config['GOOGLE_CLIENT_ID'] = settings.get('Google', 'Client ID')
app.config['GOOGLE_CLIENT_SECRET'] = settings.get('Google', 'Client Secret')
app.config['REDIRECT_URI'] = settings.get('Google','OATH Redirect URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

oauth = OAuth()

google = oauth.remote_app('google',
base_url='https://www.google.com/accounts/',
authorize_url='https://accounts.google.com/o/oauth2/auth',
request_token_url=None,
request_token_params={'scope': 'https://www.googleapis.com/auth/plus.login', 'response_type': 'code'},
access_token_url='https://accounts.google.com/o/oauth2/token',
access_token_method='POST',
access_token_params={'grant_type': 'authorization_code'},
consumer_key=app.config['GOOGLE_CLIENT_ID'],
consumer_secret=app.config['GOOGLE_CLIENT_SECRET'])

association_table = db.Table('association', db.Model.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('authorization_id', db.Integer, db.ForeignKey('authorization.id'))
)

class Event(db.Model):
    _tablename_="event"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=False, nullable=False)
    instructor_email = db.Column(db.String(120), unique=False, nullable=True)
    instructor_name = db.Column(db.String(60))
    location = db.Column(db.String(120))
    start_date = db.Column(db.Date(), nullable=True, default=None)
    end_date = db.Column(db.Date(), nullable=True, default=None)
    # duration = db.Column(db.Interval(), nullable=False, default=datetime.timedelta(hours=1))
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    description = db.Column(db.String(500), nullable=False)
    min_age = db.Column(db.Integer(), nullable=True)
    max_age = db.Column(db.Integer(), nullable=True)
    registration_limit = db.Column(db.Integer(), nullable=True)
    member_price = db.Column(db.Float(), nullable=True)
    nonmember_price = db.Column(db.Float(), nullable=True)

    authorizations = db.relationship("Authorization", secondary=association_table)

    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow)
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"Event('{self.title}', '{self.start_date}')"

class Authorization(db.Model):
    _tablename_="authorization"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    wa_group_id = db.Column(db.Integer, nullable=False, unique=True)

    events = db.relationship("Event", secondary=association_table, back_populates="authorizations")

    def __repr__(self):
        return f"Authorization('{self.name}': '{self.wa_id}')"

# class Price(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(40), nullable=False, unique=True)
#     value = db.Column(db.Float(), nullable=False)

# class Location(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(40), nullable=False, unique=True)
#     description = db.Column(db.String(120), nullable=False, unique=True)


@app.route("/home")
def home():
    access_token = session.get('access_token')
    if access_token is None:
      return redirect(url_for('login'))
    
    access_token = access_token[0]
    
    
    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo', None, headers)
    try:
      res = urlopen(req)
      response = json.load(res) 
    except URLError as e:
      if e.code == 401:
        # Unauthorized - bad token
        session.pop('access_token', None)
        return redirect(url_for('login'))
    
    return render_template('home.html', title='Home')

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route(app.config['REDIRECT_URI'])
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('createClass'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

@app.route('/createClass', methods=['GET', 'POST'], defaults={'template':None}, strict_slashes=False)
@app.route("/createClass/<template>", methods=['GET', 'POST'])
def createClass(template):
    
    access_token = session.get('access_token')
    if access_token is None:
      return redirect(url_for('login'))

    form = NewClassForm()
    if request.method == 'GET':
        if not template:
            print("NO TEMPLATE!")
            return redirect(url_for('createClass')+'/default.js')
        form.loadTemplates()
        
        authorizations=authorizationsplugin.getAuthorizations()

        form.populateTemplate(template)
        return render_template('createClass.html', title='Create Event', form=form, authorizations=authorizations)

    if request.method == 'POST':
        if form.validate_on_submit():
            flash(f'Class created for {form.classTitle.data}!', 'success')

            # FIXME 
            # There must be a better way to do the checkboxes, but this is the only way I have found that works        
            selected_authorizations = request.form.getlist("authorizations")
            form.setSelectedAuthorizations(selected_authorizations)
            event=form.collectEventDetails()
            event_entry = Event(title=event["title"],
                                instructor_email = event["instructorEmail"],
                                instructor_name = event["instructorName"],
                                location = event["location"],
                                start_date = event["startTime"],
                                end_date = event["stopTime"],
                                description = event["description"],
                                min_age = event["minimumAge"],
                                max_age = event["maximumAge"],
                                registration_limit = event["registrationLimit"],
                                member_price = None,
                                nonmember_price = None,
                                
                                authorizations = [],
                                )
            db.session.add(event_entry)
            db.session.commit()
            print(event)
            
            indicatorValue = request.form.get('ts_indicator', '')
            
            if indicatorValue == "save_template":
              form.saveTemplate(dict(event), request.form["ts_name"])
                  
                           
            # waplugin.createEvent(event)
            return redirect(url_for('home'))
    

    
def setPlugins(plugins):
    global loadedPlugins
    loadedPlugins = plugins

def _getChildren(parent):
    for i in range(parent.count()):
        yield parent.itemAt(i).widget()



#setPlugins(plugins.loadAllFromPath())

waplugin = WildApricot.load()
authorizationsplugin = MakerspaceAuthorizations.load();


if __name__ == '__main__':
    app.run(debug=True)