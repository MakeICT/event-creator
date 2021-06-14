from datetime import datetime, timedelta, date
from distutils.util import strtobool

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField,  \
                    DecimalField, DateField, TextAreaField, TimeField, \
                    SelectMultipleField, SelectField, FloatField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, Length, Email, URL, Optional
from flask_wtf.file import FileField, FileAllowed

useHtml5Fields = True
if useHtml5Fields:
    from wtforms.fields.html5 import DateField, TimeField, IntegerField

from models import Event, EventTemplate, EventStatus


class EventForm(FlaskForm):
    eventType = SelectField('Type', choices=[], validators=[DataRequired()])
    eventStatus = SelectField('Status', choices=[], validators=[Optional()])
    eventTag = SelectField('Tag', choices=[], validators=[Optional()])

    eventTitle = StringField('Title', validators=[DataRequired()])
    image_file = FileField('Event Picture',
                           validators=[FileAllowed(['jpg', 'png'])])
    instructorName = StringField('Instructor Name',
                                 validators=[DataRequired()])
    instructorEmail = StringField('Instructor Email',
                                  validators=[DataRequired(), Email()])
    eventLocation = StringField('Location')
    eventDescription = TextAreaField('Description', render_kw={"rows": 10})
    registrationURL = StringField('Registration URL')
    registrationLimit = IntegerField('Registration Limit')
    if useHtml5Fields:
        eventDate = DateField('Date', default=date.today())
        starttime = TimeField(label='Start Time')
    else:
        eventDate = DateField('Date', default=date.today(),
                              format='%m/%d/%Y')
        starttime = TimeField(label='Start Time', format="%H:%M %p")

    duration = FloatField(label='Duration')
    minAge = IntegerField('Min. Age', validators=[Optional()])
    maxAge = IntegerField('Max. Age', validators=[Optional()])
    memberPrice = DecimalField('Member Price', places=2, validators=[Optional()])
    nonMemberPrice = DecimalField('Non-Member Price', places=2, validators=[Optional()])

    authorizations = SelectMultipleField('Required Authorizations', choices=[])
    platforms = SelectMultipleField('Platforms', choices=[])
    resources = SelectMultipleField('Resources', choices=[])

    submit = SubmitField('Submit')

    template_map = {}
    templates = []

    selectedTemplateName = ""
    save_template = HiddenField(default=False)

    def validate(self):
        if not super().validate():
            return False

        result = True
        start_datetime = datetime.combine(self.eventDate.data, self.starttime.data)

        check = strtobool(self.save_template.data)
        print(self.save_template.data, check)

        if not check and not start_datetime > datetime.now():
            self.eventDate.errors.append('start of event must be in the future')
            self.starttime.errors.append('start of event must be in the future')
            result = False

        return result

    def collectEventDetails(self):
        details = {
            'title': self.eventTitle.data.strip(),
            'image_file': self.image_file.data,
            'status': self.eventStatus.data,
            'event_type': self.eventType.data,
            'host_email': self.instructorEmail.data.strip(),
            'host_name': self.instructorName.data.strip(),
            'location': self.eventLocation.data.strip(),
            'start_date': self.eventDate.data,
            'start_time': self.starttime.data,
            'duration': timedelta(hours=self.duration.data),
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
            details['prices'].append({'name': 'MakeICT Members',
                                      'price': float(self.memberPrice.data),
                                      'description': '',
                                      'availability': ['Members']
                                      })

        if self.nonMemberPrice is not None:
            details['prices'].append({
                'name': 'Non-Members',
                'price': float(self.nonMemberPrice.data),
                'description': '',
                'availability': ['Everyone']})

        return details

    def loadTemplates(self):
        self.template_map = {}
        self.templates = []

        for t in EventTemplate.query.all():
            self.template_map[t.uniqueName()] = t.id
        self.templates.append("Select Template")

        for t in sorted(self.template_map.keys(), key=str.lower):
            self.templates.append(t)

    def populate(self, event):
        """
        Loads values from the provided Event or EventTemplate object into the
        form.
        """
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
        self.eventPlatforms = [plat.name for plat in event.platforms]
        self.starttime.data = event.start_time
        self.duration.data = event.duration.seconds/3600
        self.eventType.data = event.event_type.name
        self.eventTag.data = event.tags[0].name
        self.starttime.data = event.start_time
        self.image_file.data = event.image_file
        # self.image_file.default = event.image_file

        if event.authorizations:
            self.authorizations.default = [auth.name for auth in event.authorizations]
        if event.resources:
            self.resources.default = [res.name for res in event.resources]
        self.platforms.default = [plat.name for plat in event.platforms]

        for price in event.prices:
            if (price.name == 'MakeICT Members'):
                self.memberPrice.data = price.value
            elif (price.name == 'Non-Members'):
                self.nonMemberPrice.data = price.value
        if isinstance(event, Event):
            # fields specific to real events
            self.eventDate.data = event.start_date
            self.eventStatus.data = event.status.name
        else:
            # fields specific to templates
            self.eventDate.data = datetime.now().date()
            self.eventStatus.data = EventStatus.draft.name
            self.selectedTemplateName = event.uniqueName()
