import sys, datetime, dateparser, json, os
from dateutil.parser import parse
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, DecimalField, DateField, DateTimeField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Length, Email, URL, Optional
from wtforms.fields.simple import TextAreaField

useHtml5Fields = True
if useHtml5Fields:
    from wtforms.fields.html5 import DateField, TimeField, IntegerField


class NewClassForm(FlaskForm):
    tagGroups = []
    auths = []

    classTitle = StringField('Title', validators=[DataRequired()])
    instructorName = StringField('Instructor Name', validators=[DataRequired()])
    instructorEmail = StringField('Instructor Email', validators=[DataRequired(), Email()])
    classLocation = StringField('Location')
    classDescription = TextAreaField('Description')
    registrationURL = StringField('Registration URL')
    registrationLimit = IntegerField('Registration Limit', validators=[DataRequired()])
    if useHtml5Fields:
        classDate = DateField('Date', default=datetime.date.today())
        starttime = TimeField(label='Start time(CDT)')
        endtime = TimeField(label='End time(CDT)')
    else:
        classDate = DateField('Date', default=datetime.date.today(), format='%m/%d/%Y')
        starttime = TimeField(label='Start time(CDT)', format="%H:%M %p")
        endtime = TimeField(label='End time(CDT)', format="%H:%M %p")
    minAge = IntegerField('Min Age', validators=[Optional()])
    maxAge = IntegerField('Max Age', validators=[Optional()])
    memberPrice = DecimalField(places=2, validators=[Optional()])
    nonMemberPrice = DecimalField(places=2, validators=[Optional()])
            
    submit = SubmitField('Submit')

    templateRequiredAuths = []
    templates = {}
    
    def setSelectedAuthorizations(self, selected):
        self.auths = selected



    def collectEventDetails(self):
        date = self.classDate.data
        
        event = {
            'title': self.classTitle.data.strip(),
            'location': self.classLocation.data.strip(),
            'startTime': datetime.datetime.combine(date, self.starttime.data.time()),
            'stopTime': datetime.datetime.combine(date, self.endtime.data.time()),
            'description': self.classDescription.data.strip(),
            'registrationURL': self.registrationURL.data.strip(),
            'registrationLimit': self.registrationLimit.data,
            'prices': [],
            'tags': {},
            'isFree': True,
            'priceDescription': '',
            'instructorName': self.instructorName.data.strip(),
            'instructorEmail': self.instructorEmail.data.strip(),
            'minimumAge': self.minAge.data if self.minAge.data is not None else 0,
            'maximumAge': self.maxAge.data if self.maxAge.data is not None else 0,
            'pre-requisites':[],
            'resources':[],
        }
        
        if self.memberPrice is not None:
           event['prices'].append({
            'name': 'MakeICT Members',
            'price': self.memberPrice.data,
            'description': '',
            'availability': ['Members']                
            })
            
        if self.nonMemberPrice is not None:
           event['prices'].append({
            'name': 'Non-Members',
            'price': self.nonMemberPrice.data,
            'description': '',
            'availability': ['Everyone']                
            })
            
        event['instructorDescription'] = 'Instructor: ' + event['instructorName']
     
        if(event['minimumAge'] > 0):
            if(event['maximumAge'] > 0):
                assert event['minimumAge'] < event['maximumAge'], "You did the age thing wrong..."
                event['ageDescription'] = 'Ages: %d-%d' % (event['minimumAge'],event['maximumAge'])
            else:
                event['ageDescription'] = 'Ages: %d and up' % (event['minimumAge'])
     
        elif(event['maximumAge'] > 0):
            event['ageDescription'] = 'Ages: %d and under' % (event['maximumAge'])
     
        else:
            event['ageDescription'] = None
     
        for tagGroup in self.tagGroups:
            event['tags'][tagGroup['name']] = []
            for checkbox in tagGroup['checkboxes']:
                if checkbox.isChecked():
                    event['tags'][tagGroup['name']].append(checkbox.text())

        event['tags']['Required auth\'s'] = self.auths
     
        if self.auths:
            event['authorizationDescription'] = "Required authorizations: "
     
            if len(self.auths) > 0:
                event['authorizationDescription'] += ','.join(self.auths)
     
        else:
            event['authorizationDescription'] = None
        
        return event
    
    
    
    def loadTemplates(self):
        self.templates = {}
        basepath = 'EventTemplates/'
        
        # r=root, d=directories, f = files
        for r, d, f in os.walk(basepath):
            for file in f:
                self.templates[file] = (os.path.join(r, file))
        

    
    def populateTemplate(self, templateName):
    
        templateFile = self.templates.get(templateName, '')
        
        if self.isBlank(templateFile):
            templateFile = self.templates.get('default')
            
        with open(templateFile) as json_file:
            data = json.load(json_file)
        
            self.classTitle.data = data.get('title', '')
            self.instructorName.data = data.get('instructorName', '')
            self.instructorEmail.data = data.get('instructorEmail', '')
            self.classLocation.data = data.get('location', '')
            self.classDescription.data = data.get('description', '')
            self.registrationURL.data = data.get('location', '')
            self.registrationLimit.data = data.get('registrationLimit', '')
            
            value = data.get('classDate', '')            
            if self.isNotBlank(value) :
                self.classDate.data = parse(value, fuzzy=True) 

            value = data.get('startTime', '')            
            if self.isNotBlank(value) :
                self.starttime.data = parse(value, fuzzy=True) 

            value = data.get('stopTime', '')            
            if self.isNotBlank(value) :
                self.endtime.data = parse(value, fuzzy=True) 

            self.minAge.data = data.get('minimumAge', '')
            self.maxAge.data = data.get('maximumAge', '')
            
            pricelist = data.get('prices', [])
            
            for price in pricelist :
              name = price['name']
              
              if (name == 'MakeICT Members') :
                  self.memberPrice.data = price['price']
              elif (name == 'Non-Members') :
                  self.nonMemberPrice.data = price['price']
                    
            taglist = data.get('tags', [])
            
            self.templateRequiredAuths = []
            
            for tags in taglist :
              if tags == "Required auth's" :
                self.templateRequiredAuths = taglist[tags]
                                    
            
    def isBlank (self, myString):
        return not (myString and myString.strip())

    def isNotBlank (self, myString):
        return bool(myString and myString.strip())