import sys
import datetime
import dateparser
import json
import os
from dateutil.parser import parse
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, \
                    BooleanField, IntegerField, DecimalField, \
                    DateField, DateTimeField, TextAreaField, TimeField, \
                    SelectMultipleField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, Email, URL, Optional
from wtforms.fields.simple import TextAreaField

from models import Event, EventTemplate, EventStatus, EventType, Authorization, Price, Resource, Platform

useHtml5Fields = True
if useHtml5Fields:
    from wtforms.fields.html5 import DateField, TimeField, IntegerField


class EventForm(FlaskForm):
    tagGroups = []
    auths = []

    eventType = SelectField('Type', choices=[], validators=[DataRequired()])
    eventStatus = SelectField('Status', choices=[], validators=[Optional()])
    eventTag = SelectField('Tag', choices=[], validators=[Optional()])

    eventTitle = StringField('Title', validators=[DataRequired()])
    instructorName = StringField('Instructor Name',
                                 validators=[DataRequired()])
    instructorEmail = StringField('Instructor Email',
                                  validators=[DataRequired(), Email()])
    eventLocation = StringField('Location')
    eventDescription = TextAreaField('Description', render_kw={"rows": 10})
    registrationURL = StringField('Registration URL')
    registrationLimit = IntegerField('Registration Limit',
                                     validators=[DataRequired()])
    if useHtml5Fields:
        eventDate = DateField('Date', default=datetime.date.today())
        starttime = TimeField(label='Start time(CDT)')
        duration = FloatField(label='Duration (Hours)')
    else:
        eventDate = DateField('Date', default=datetime.date.today(),
                              format='%m/%d/%Y')
        starttime = TimeField(label='Start time(CDT)', format="%H:%M %p")
        duration = FloatField(label='Duration (Hours)')
    minAge = IntegerField('Min Age', validators=[Optional()])
    maxAge = IntegerField('Max Age', validators=[Optional()])
    memberPrice = DecimalField(places=2, validators=[Optional()])
    nonMemberPrice = DecimalField(places=2, validators=[Optional()])

    authorizations = SelectMultipleField('Required Authorizations', choices=[])
    platforms = SelectMultipleField('Platforms', choices=[])
    resources = SelectMultipleField('Resources', choices=[])

    submit = SubmitField('Submit')

    templateRequiredAuths = []
    calendarResources = []
    template_map = {}
    templates = []

    selectedTemplateName = ""
    selectedTemplateFullName = ""

    def setSelectedAuthorizations(self, selected):
        self.auths = selected

    def collectEventDetails(self):
        event = {
            'title': self.eventTitle.data.strip(),
            'status': self.eventStatus.data,
            'event_type': self.eventType.data,
            'host_email': self.instructorEmail.data.strip(),
            'host_name': self.instructorName.data.strip(),
            'location': self.eventLocation.data.strip(),
            'start_date': self.eventDate.data,
            'start_time': self.starttime.data,
            'duration': datetime.timedelta(hours=self.duration.data),
            'description': self.eventDescription.data.strip(),
            'min_age': self.minAge.data if self.minAge.data is not None else 0,
            'max_age': self.maxAge.data if self.maxAge.data is not None else 0,
            'registration_limit': self.registrationLimit.data,
            'prices': [],
            'authorizations': self.authorizations.data,
            'platforms': self.platforms.data,
            'resources': self.resources.data,
            'tags': [self.eventTag.data],
        }

        if self.memberPrice is not None:
            event['prices'].append({'name': 'MakeICT Members',
                                    'price': float(self.memberPrice.data),
                                    'description': '',
                                    'availability': ['Members']
                                    })

        if self.nonMemberPrice is not None:
            event['prices'].append({
                'name': 'Non-Members',
                'price': float(self.nonMemberPrice.data),
                'description': '',
                'availability': ['Everyone']})

        # for tagGroup in self.tagGroups:
        #     event['tags'][tagGroup['name']] = []
        #     for checkbox in tagGroup['checkboxes']:
        #         if checkbox.isChecked():
        #             event['tags'][tagGroup['name']].append(checkbox.text())

        # event['tags']['Required auth\'s'] = self.auths
        # event['tags']['Resources'] = self.resources.data

        return event

    def loadTemplates(self):
        self.template_map = {}
        self.templates = []

        basepath = 'EventTemplates/'

        # r=root, d=directories, f = files
        for r, d, f in os.walk(basepath):
            for file in f:
                self.template_map[file] = (os.path.join(r, file))

        self.templates.append("Select Template")

        for t in sorted(self.template_map.keys(), key=str.lower):
            self.templates.append(t)

    def populate(self, event):
        assert isinstance(event, (EventTemplate, Event)), "Unsupported type"

        # fields shared between events and templates
        self.eventTitle.data = event.title
        self.instructorName.data = event.host_name
        self.instructorEmail.data = event.host_email
        self.eventLocation.data = event.location
        self.eventDescription.data = event.description
        self.registrationLimit.data = event.registration_limit
        self.minAge.data = event.min_age
        self.maxAge.data = event.max_age
        self.templateRequiredAuths = [auth.name for auth in event.authorizations]
        self.calendarResources = [res.name for res in event.resources]
        self.starttime.data = event.start_time
        self.duration.data = event.duration.seconds/3600

        for price in event.prices:
            if (price.name == 'MakeICT Members'):
                self.memberPrice.data = price.value
            elif (price.name == 'Non-Members'):
                self.nonMemberPrice.data = price.value
        if isinstance(event, Event):
            # fields specific to real events
            self.eventDate.data = event.start_date

            self.eventStatus.data = event.status.name
            self.eventType.data = event.event_type.name
        else:
            self.eventDate.data = datetime.now().date()

            self.eventStatus.data = EventStatus.draft.name
            self.eventType.data = EventType.event.name


    def populateTemplate(self, templateName):
        templateFile = self.template_map.get(templateName, '')

        if self.isBlank(templateFile):
            templateFile = self.template_map.get('default')

        with open(templateFile) as json_file:

            self.selectedTemplateName = templateName
            self.selectedTemplateFullName = templateFile[15:]
            self.selectedTemplateFullName = self.selectedTemplateFullName \
                                                .replace("\\", "/")

            data = json.load(json_file)

            self.eventTitle.data = data.get('title', '')
            self.instructorName.data = data.get('instructorName', '')
            self.instructorEmail.data = data.get('instructorEmail', '')
            self.eventLocation.data = data.get('location', '')
            self.eventDescription.data = data.get('description', '')
            self.registrationURL.data = data.get('location', '')
            self.registrationLimit.data = data.get('registrationLimit', '')

            value = data.get('classDate', '')
            if self.isNotBlank(value):
                self.classDate.data = parse(value, fuzzy=True)

            value = data.get('startTime', '')
            if self.isNotBlank(value):
                self.starttime.data = parse(value, fuzzy=True)

            # value = data.get('stopTime', '')
            # if self.isNotBlank(value):
            #     self.endtime.data = parse(value, fuzzy=True)

            self.minAge.data = data.get('minimumAge', '')
            self.maxAge.data = data.get('maximumAge', '')

            pricelist = data.get('prices', [])

            for price in pricelist :
                name = price['name']

                if (name == 'MakeICT Members'):
                    self.memberPrice.data = price['price']
                elif (name == 'Non-Members'):
                    self.nonMemberPrice.data = price['price']

            taglist = data.get('tags', [])

            self.templateRequiredAuths = []

            for tags in taglist:
                if tags == "Required auth's":
                    self.templateRequiredAuths = taglist[tags]
                elif tags == "Resources":
                    self.calendarResources = taglist[tags]

    def deleteTemplate(selfself, templateName):
        
        if templateName != '':
            if not templateName.endswith(".js"):
                templateName += ".js"
            
            if os.path.exists('EventTemplates/' + templateName):    
                os.remove('EventTemplates/' + templateName)
                print("Deleting")
                return "Template " + templateName + " deleted!"
            
        return "Unable to delete template " + templateName + "!"
   
    def saveTemplate(self, event, templateName):

        if templateName != '':
            if not templateName.endswith(".js"):
                templateName += ".js"

            value = event.get('classDate', '')
            if value:
                del event['classDate']

            value = event.get('startTime', '')
            if value:
                event['startTime'] = value.isoformat()
            value = event.get('stopTime', '')
            if value:
                event['stopTime'] = value.isoformat()

            self.createDirectoryIfNeeded(templateName)
            with open('EventTemplates/' + templateName , 'w') as outfile:
                jstr = json.dump(event, outfile, sort_keys=True, indent=4,
                                 ensure_ascii=False)

            return os.path.basename(outfile.name)

    def populateEvent(self, event):
        self.eventTitle.data = event.title
        self.instructorName.data = event.host_name
        self.instructorEmail.data = event.host_email
        self.eventLocation.data = event.location
        self.eventDescription.data = event.description
        # self.registrationURL.data = event.registrationURL()
        self.registrationLimit.data = event.registration_limit
        self.eventDate.data = event.start_date
        self.starttime.data = event.start_time
        self.duration.data = event.duration.seconds/3600
        self.minAge.data = event.min_age
        self.maxAge.data = event.max_age
        self.templateRequiredAuths = [auth.name for auth in event.authorizations]
        self.calendarResources = [res.name for res in event.resources]

        for price in event.prices:
            if (price.name == 'MakeICT Members'):
                self.memberPrice.data = price.value
            elif (price.name == 'Non-Members'):
                self.nonMemberPrice.data = price.value

    def createDirectoryIfNeeded(self, fpath):
        fpath = fpath.replace("\\", "/")
        index = fpath.rfind("/")

        if index > 0:
            dirpath = fpath[0:index]
            os.makedirs('EventTemplates/' + dirpath, exist_ok=True)

    def isBlank (self, myString):
        return not (myString and myString.strip())

    def isNotBlank (self, myString):
        return bool(myString and myString.strip())