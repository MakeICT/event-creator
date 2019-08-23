from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_oauth import OAuth
from forms import NewClassForm
from attrdict import AttrDict
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import plugins
# from plugins import WildApricot
import json
from config import settings
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
from flask_navbar import Nav
from flask_navbar.elements import *
from dateutil.parser import parse

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
nav = Nav()
nav.init_app(app)

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

loadedPlugins = plugins.loadAllFromPath()
print(loadedPlugins)

# waplugin = WildApricot.load()

association_table = db.Table('association', db.Model.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('authorization_id', db.Integer, db.ForeignKey('authorization.id'))
)
event_price = db.Table('event_price', db.Model.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('price_id', db.Integer, db.ForeignKey('price.id'))
)
event_platform = db.Table('event_platform', db.Model.metadata,
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('platform_id', db.Integer, db.ForeignKey('platform.id')),
)

class Event(db.Model):
    _tablename_="event"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=False, nullable=False)
    instructor_email = db.Column(db.String(120), unique=False, nullable=True)
    instructor_name = db.Column(db.String(60))
    location = db.Column(db.String(120))
    start_date = db.Column(db.DateTime(), nullable=True, default=None)
    end_date = db.Column(db.DateTime(), nullable=True, default=None)
    # duration = db.Column(db.Interval(), nullable=False, default=datetime.timedelta(hours=1))
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    description = db.Column(db.String(500), nullable=False)
    min_age = db.Column(db.Integer(), nullable=True)
    max_age = db.Column(db.Integer(), nullable=True)
    registration_limit = db.Column(db.Integer(), nullable=True)

    prices = db.relationship("Price", secondary=event_price)
    authorizations = db.relationship("Authorization", secondary=association_table)
    platforms = db.relationship("Platform", secondary=event_platform)
    external_events = db.relationship("ExternalEvent")

    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow)
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow)
    sync_date = db.Column(db.DateTime, nullable=True, default=None)

    def __repr__(self):
        return f"Event('{self.title}', '{self.start_date}')"

    def addExternalEvent(self, platform_name, external_id, external_url):
        platform = Platform.query.filter_by(name=platform_name).first()
        ext_event = ExternalEvent(event_id=self.id,
                                  platform_id=platform.id,
                                  ext_event_id=external_id,
                                  ext_event_url=external_url)
        self. external_events.append(ext_event)

    def updateSyncDate(self):
        self.sync_date = datetime.datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def detailedDescription(self):
        desc = f"Instructor: {self.instructor_name}\n\n"
        desc += self.description
        if self.authorizations:
            auths = [auth.name for auth in self.authorizations]
            desc += f"\n\nRequired Authorizations: {auths}\n\n"

        if self.min_age and not self.max_age:
            desc += f"Ages: {self.min_age} and up\n\n"
        elif self.max_age and not self.min_age:
            desc += f"Ages: {self.max_age} and under\n\n"
        elif self.min_age and self.max_age:
            desc += f"Ages: {self.min_age} to {self.max_age}\n\n"

        if self.prices:
            desc += "Event Prices:\n"
            for price in self.prices:
                desc += f"- {price.name}: ${price.value:.2f}\n"

        return desc

    def htmlSummary(self, omit=[]):
        desc = ""

        if 'time' not in omit:
            desc += "<b>Time:</b> " \
                + self.start_date.strftime('%b %d %I:%M %p - ') \
                + self.end_date.strftime('%I:%M %p')

        if 'instr' not in omit:
            desc += f"<br><b>Instructor:</b> {self.instructor_name}"

        if self.external_events and 'reg' not in omit:
            for ext_event in self.external_events:
                if ext_event.primary_event:
                    desc += f"<br><b>Register:</b> <a href='{ext_event.ext_event_url}'>" \
                                   f"{ext_event.ext_event_url}</a>"

        if 'price' not in omit:
            for price in self.prices:
                desc += f"<br><b>Price:</b> {price.name} - ${price.value:.2f}"

        if 'age' not in omit:
            if self.min_age and not self.max_age:
                desc += f"<br><b>Ages</b>: {self.min_age} and up"
            elif self.max_age and not self.min_age:
                desc += f"<br><b>Ages</b>: {self.max_age} and under"
            elif self.min_age and self.max_age:
                desc += f"<br><b>Ages</b>: {self.min_age} to {self.max_age}"

        if self.authorizations and 'auth' not in omit:
            desc += f"<br><b>Required Authorizations:</b> " \
                + f"{', '.join([auth.name for auth in self.authorizations])}"

        desc += '<br><br>' + self.description

        return desc


class Authorization(db.Model):
    _tablename_="authorization"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    wa_group_id = db.Column(db.Integer, nullable=False, unique=True)

    events = db.relationship("Event", secondary=association_table, back_populates="authorizations")

    def __repr__(self):
        return f"Authorization('{self.name}': '{self.wa_group_id}')"

class Price(db.Model):
    _tablename_ = "price"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    value = db.Column(db.Float(), nullable=False)
    description = db.Column(db.String(40), nullable=True)
    availability = db.Column(db.String(30), nullable=False)

    events = db.relationship("Event", secondary=event_price, back_populates="prices")

    def __repr__(self):
        return f"Price('{self.name}': '{self.value}', '{self.availability}', '{self.events}')"


class Platform(db.Model):
    _tablename_ = "platform"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)

    events = db.relationship("Event", secondary=event_platform,
                             back_populates="platforms")


class ExternalEvent(db.Model):
    _tablename_ = "external_event"
    id = db.Column(db.Integer, primary_key=True)

    primary_event = db.Column(db.Boolean, default=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    ext_event_id = db.Column(db.String(100))
    ext_event_url = db.Column(db.String(300))

# class Location(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(40), nullable=False, unique=True)
#     description = db.Column(db.String(120), nullable=False, unique=True)


@nav.navigation()
def top_nav():
    items = [View('Home', 'home'), View('Create Class', 'createClass'), View('Events', 'upcoming_events')]

    return Navbar('', *items)

@app.route("/")
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
    print(loadedPlugins)

    access_token = session.get('access_token')
    auth_list = [auth.name for auth in Authorization.query.all()]

    if access_token is None:
      return redirect(url_for('login'))

    form = NewClassForm()
    if request.method == 'GET':
        if not template or template == "Select Template":
            print("NO TEMPLATE!")
            return redirect(url_for('createClass')+'/default.js')
        form.loadTemplates()        
        form.populateTemplate(template)

        return render_template('createClass.html', title='Create Event', form=form, authorizations=auth_list)

    if request.method == 'POST':
        if form.validate_on_submit():
            selected_authorizations = request.form.getlist("authorizations")
            form.setSelectedAuthorizations(selected_authorizations)
            event=form.collectEventDetails()
            event_auths = [Authorization.query.filter_by(name=auth).first() for auth in selected_authorizations]
            if None in event_auths:
                print("INVALID EVENT AUTHORIZATIONS!!!!")
            event_prices = [Price(name=price['name'], description=price['description'], value=price['price'], availability=price['availability'][0]) for price in event['prices']]

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

                                prices = event_prices,
                                authorizations = event_auths,
                                )

            print(event)

            indicatorValue = request.form.get('ts_indicator', '')

            if indicatorValue == "save_template":
                templateFile = request.form.get('ts_name', '')

                templateName = form.saveTemplate(dict(event), request.form["ts_name"])
                form.loadTemplates()
                flash("Template Saved as " + templateName + "!", 'success')

                form.populateTemplate(templateName)
                return render_template('createClass.html', title='Create Event', form=form, authorizations=auth_list)
            else:
                flash(f'Class created for {form.classTitle.data}!', 'success')
                db.session.add(event_entry)
                db.session.commit()
                return redirect(url_for('upcoming_events'))
        else:
            flash(f'Event failed to post! Check form for errors.', 'danger')


    form.loadTemplates()      
    return render_template('createClass.html', title='Create Event', form=form, authorizations=auth_list)

@app.route('/events', methods=['GET'])
def upcoming_events():
    upcoming_events = Event.query.all()
    upcoming_events = sorted(upcoming_events, key=lambda event: event.start_date)
    event_list = []
    for event in upcoming_events:
        if event.start_date.date() >= datetime.datetime.today().date():
        # if not event['AccessLevel'] == 'AdminOnly':
            if event.registration_limit:
                # print(event['RegistrationsLimit'], event['ConfirmedRegistrationsCount'])
                spots_available = event.registration_limit
                spots = None
                if spots_available > 0:
                    spots = str(spots_available) + 'Register'
                else:
                    spots = 'FULL'
            # start_date = WA_API.WADateToDateTime(event['StartDate'])
            start_date = event.start_date
            # if 'test' not in event.title.lower():
            event_list.append({
                                "Id": event.id,
                                "Name":event.title,
                                "Date": start_date.strftime('%b %d %Y'),
                                "Time": start_date.strftime('%I:%M %p'),
                                "Description":event.description,
                                "Register":"http://makeict.wildapricot.org/event-" + str(event.id),
                              })
            print(event_list)
            #       str(event['Id']))
            # print(start_date.strftime('%b %d') + ' | ' + start_date.strftime('%I:%M %p') + 
            #       ' | ' + event['Name'] + ' | ' + '<a href="http://makeict.wildapricot.org/event-' + 
            #       str(event['Id']) + '" target="_blank">Register</a><br />')

    print (upcoming_events)
    return render_template('events.html', events=event_list)
    
@app.route('/event/<event_id>')
def edit_event(event_id):
    e = Event.query.get(event_id)
    return render_template('edit_event.html', event=e)

@app.route('/calendar')
def calendar():
    return render_template("calendar.html")


@app.route('/calendardata')
def return_data():
    start_date_range = parse(request.args.get('start', ''), fuzzy=True)
    end_date_range = parse(request.args.get('end', ''), fuzzy=True)
    
    
    upcoming_events = Event.query.all()
    upcoming_events = sorted(upcoming_events, key=lambda event: event.start_date)
    event_list = []
    for event in upcoming_events:
        if event.start_date.date() >= start_date_range.date() and event.start_date.date() <= end_date_range.date()  :
        # if not event['AccessLevel'] == 'AdminOnly':
            if event.registration_limit:
                # print(event['RegistrationsLimit'], event['ConfirmedRegistrationsCount'])
                spots_available = event.registration_limit
                spots = None
                if spots_available > 0:
                    spots = str(spots_available) + 'Register'
                else:
                    spots = 'FULL'
            # start_date = WA_API.WADateToDateTime(event['StartDate'])
            start_date = event.start_date
            # if 'test' not in event.title.lower():
 
            event_list.append({
                                "Id": event.id,
                                "title": event.title,
                                "Name": event.title,
                                "start": start_date.strftime('%b %d %Y'),
                                "Date": start_date.strftime('%b %d %Y'),
                                "Time": start_date.strftime('%I:%M %p'),
                                "Description":event.description,
                                "Register":"http://makeict.wildapricot.org/event-" + str(event.id),
                              })

    
    return json.dumps(event_list)

def setPlugins(plugins):
    global loadedPlugins
    loadedPlugins = plugins

def _getChildren(parent):
    for i in range(parent.count()):
        yield parent.itemAt(i).widget()

if __name__ == '__main__':
    app.run(debug=True)
