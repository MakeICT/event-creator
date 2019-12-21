import datetime
from dateutil.parser import parse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json

from flask_navbar import Nav
from flask_navbar.elements import Navbar, View
from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, logout_user, current_user, login_required

from config import settings
from main import app, db, loadedPlugins
from forms import EventForm
from models import Event, EventStatus, EventType
from models import Authorization, Price, Platform, Resource
from event_sync import SyncEvent, SyncEvents, DeleteEvent, MissingExternalEventError

nav = Nav()
nav.init_app(app)

@nav.navigation()
def top_nav():
    items = [View('Home', 'home'),
             View('Create Event', 'create_event'),
             View('Events', 'upcoming_events'),
             View('Calendar', 'calendar')]

    if current_user.is_authenticated :
      items.append(View('Log Out', 'logout'))
    else:
      items.append(View('Log In', 'login'))
    return Navbar('', *items)


@app.route("/")
@app.route("/home")
def home():
    return render_template('calendar.html', title='Home')


def populate_select_boxes(event_form):
    auth_list = [auth.name for auth in Authorization.query.all()]
    plat_list = [plat.name for plat in Platform.query.all()]
    res_list = [res.name for res in Resource.query.all()]
    event_type_list = [event_type.name for event_type in EventType]
    event_status_list = [event_status.name for event_status in EventStatus]

    event_form.eventType.choices = [(t.name, t.name) for t in EventType]
    event_form.eventStatus.choices = [(s.name, s.name) for s in EventStatus]
    event_form.authorizations.choices = [(auth, auth) for auth in auth_list]
    event_form.platforms.choices = [(plat, plat) for plat in plat_list]
    event_form.resources.choices = [(res, res) for res in res_list]

def update_event_details(event, event_form):
    selected_authorizations = request.form.getlist("authorizations")
    event_form.setSelectedAuthorizations(selected_authorizations)
    details = event_form.collectEventDetails()
    details["authorizations"] = [Authorization.query.filter_by(name=auth).first()
                                 for auth in details["authorizations"]]
    details["platforms"] = [Platform.query.filter_by(name=plat).first()
                            for plat in details["platforms"]]
    details["resources"] = [Resource.query.filter_by(name=res).first()
                            for res in details["resources"]]
    if None in details["authorizations"]:
        print("INVALID EVENT AUTHORIZATIONS!!!!")
    details["prices"] = [Price(name=price['name'],
                         description=price['description'],
                         value=price['price'],
                         availability=price['availability'][0])
                         for price in details['prices']]

    for attribute in details:
        setattr(event, attribute, details[attribute])


@app.route('/create_event', methods=['GET', 'POST'],
           defaults={'template': None}, strict_slashes=False)
@app.route("/create_event/<template>", methods=['GET', 'POST'])
@login_required
def create_event(template):
    form = EventForm()
    populate_select_boxes(form)

    if request.method == 'GET':
        if not template or template == "Select Template":
            print("NO TEMPLATE!")
            return redirect(url_for('create_event')+'/default.js')
        form.loadTemplates()
        form.populateTemplate(template)
        if form.templateRequiredAuths:
            form.authorizations.default = [auth for auth in form.templateRequiredAuths]
        if form.calendarResources:
            form.resources.default = [res for res in form.calendarResources]
        form.platforms.default = [plat.name for plat in form.platforms]

        form.process()
        form.populateTemplate(template)

    if request.method == 'POST':
        if form.validate_on_submit():
            event = Event()
            update_event_details(event, form)

            indicatorValue = request.form.get('ts_indicator', '')

            if indicatorValue == "save_template":
                templateFile = request.form.get('ts_name', '')

                templateName = form.saveTemplate(dict(event), request.form["ts_name"])
                form.loadTemplates()
                flash("Template Saved as " + templateName + "!", 'success')

                form.populateTemplate(templateName)
                return render_template('create_event.html', title='Create Event',
                                       form=form)
            elif indicatorValue == "delete_template":
                flash(form.deleteTemplate(request.form.get('ts_name', '')), 'success')

                return redirect(url_for('create_event')+'/default.js')                
            else:
                flash(f'Class created for {form.eventTitle.data}!', 'success')
                db.session.add(event)
                db.session.commit()
                return redirect(url_for('upcoming_events'))
        else:
            flash(f'Event failed to post! Check form for errors.', 'danger')

    form.loadTemplates()
    return render_template('create_event.html', title='Create Event',
                           form=form)


@app.route('/events', methods=['GET'])
def upcoming_events():
    upcoming_events = Event.query.all()
    upcoming_events = sorted(upcoming_events, key=lambda event: event.start_date)
    event_list = []
    needs_sync = 0
    for event in upcoming_events:
        if not event.fullySynced():
            needs_sync = 1
        if event.start_date >= datetime.datetime.today().date():
            if event.registration_limit:
                spots_available = event.registration_limit
                spots = None
                if spots_available > 0:
                    spots = str(spots_available) + 'Register'
                else:
                    spots = 'FULL'

            event_list.append({
                "Id": event.id,
                "Name": event.title,
                "Date": event.start_date.strftime('%b %d %Y'),
                "Time": event.start_time.strftime('%I:%M %p'),
                "Description": event.htmlSummary(all_links=True),
                "Register": "http://makeict.wildapricot.org/event-"
                            + str(event.id),
                "Synced": 1 if event.fullySynced() else 0,
            })
            #       str(event['Id']))
            # print(start_date.strftime('%b %d') + ' | ' + start_date.strftime('%I:%M %p') + 
            #       ' | ' + event['Name'] + ' | ' + '<a href="http://makeict.wildapricot.org/event-' + 
            #       str(event['Id']) + '" target="_blank">Register</a><br />')

    return render_template('events.html', events=event_list, sync_all=needs_sync)


@app.route('/event/<event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        # TODO: 404
        pass

    form = EventForm()
    populate_select_boxes(form)

    if request.method == 'GET':
        form.populate(event)
        if form.templateRequiredAuths:
            form.authorizations.default = [auth for auth in form.templateRequiredAuths]
        if form.calendarResources:
            form.resources.default = [res for res in form.calendarResources]
        form.platforms.default = [plat.name for plat in event.platforms]
        form.eventType.default = event.event_type.name
        form.eventStatus.default = event.status.name

        form.process()
        form.populate(event)

    if request.method == 'POST':
        if form.validate_on_submit():
            update_event_details(event, form)

            event.update()

            flash(f'{form.eventTitle.data} has been updated!', 'success')
            return redirect(url_for('upcoming_events'))
        else:
            flash(f'Event failed to update! Check form for errors.', 'danger')

    return render_template('edit_event.html', title='Edit Event',
                           form=form, event=event)


@app.route('/sync_all')
@login_required
def sync_all():
    events = Event.query.all()
    SyncEvents(events)
    return redirect(url_for('upcoming_events'))


@app.route('/sync/<event_id>')
@login_required
def sync(event_id):
    try:
        result = SyncEvent(Event.query.get(event_id))
    except MissingExternalEventError as e:
        flash(f'Event failed to sync to {e.platform}! Has it been remotely deleted?', 'danger')
    return redirect(url_for('upcoming_events'))


@app.route('/delete/<event_id>')
def delete(event_id):
    event = Event.query.get(event_id)
    try:
        result = DeleteEvent(event)
    except MissingExternalEventError as e:
        flash(f'Failed to delete {event.name} from  {e.platform}!', 'danger')
    return redirect(url_for('upcoming_events'))


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
        if event.start_date >= start_date_range.date() and event.start_date <= end_date_range.date():
            if event.registration_limit:
                spots_available = event.registration_limit
                spots = None
                if spots_available > 0:
                    spots = str(spots_available) + 'Register'
                else:
                    spots = 'FULL'

            start_date = event.start_date

            event_list.append({
                                "Id": event.id,
                                "title": event.title,
                                "Name": event.title,
                                "start": start_date.isoformat(),
                                "Date": start_date.isoformat(),
                                "Time": start_date.isoformat(),
                                "Description": event.description,
                                "Register": "http://makeict.wildapricot.org/event-"
                                            + str(event.id),
                              })

    return json.dumps(event_list)
