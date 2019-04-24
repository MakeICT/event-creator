import sys,datetime
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, DecimalField, DateField, DateTimeField, TextAreaField, TimeField
#from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, URL, Optional
from wtforms.fields.simple import TextAreaField


class NewClassForm(FlaskForm):
    tagGroups = []
    
    classTitle = StringField('Title', validators=[DataRequired()])
    instructorName = StringField('Instructor Name', validators=[DataRequired()])
    instructorEmail = StringField('Instructor Email', validators=[DataRequired(), Email()])
    classLocation = StringField('Location')
    classDescription = TextAreaField('Description')
    registrationURL = StringField('Registration URL')
    registrationLimit = IntegerField('Registration Limit', validators=[DataRequired()])
    classDate = DateField('Date', format='%m/%d/%Y')
    starttime = TimeField(label='Start time(CDT)', format="%H:%M %p")
    endtime = TimeField(label='End time(CDT)', format="%H:%M %p")
    minAge = IntegerField('Min Age', validators=[Optional()])
    maxAge = IntegerField('Max Age', validators=[Optional()])
    memberPrice = DecimalField(places=2, validators=[Optional()])
    nonMemberPrice = DecimalField(places=2, validators=[Optional()])
    submit = SubmitField('Submit')


    def collectEventDetails(self):
        date = self.classDate.data
        
        event = {
            'title': self.classTitle.data.strip(),
            'location': self.classLocation.data.strip(),
            'startTime': datetime.datetime.combine(date, self.starttime.data),
            'stopTime': datetime.datetime.combine(date, self.endtime.data),
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
            'price': self.memberPrice.data,
            'description': '',
            'availability': ['Everyone']                
            })
            
            
        #     for rsvpType in _getChildren(mainWindowUI.priceList):
        #       event['prices'].append({
        #        'name': rsvpType.name,
        #        'price': rsvpType.price,
        #        'description': rsvpType.description,
        #        'availability': rsvpType.availability,
        #       })
        #         
        #     priceDescription = 'The price for this event is'
        #     for i, priceGroup in enumerate(event['prices']):
        #         if priceGroup['price'] > 0:
        #             event['isFree'] = False
        #             priceDescription += ' $%0.2f for %s' % (priceGroup['price'], priceGroup['name'])
        #         else:
        #             priceDescription += ' FREE for ' + priceGroup['name']
        #             
        #         if len(event['prices']) > 2:
        #             if i < len(event['prices'])-1:
        #                 priceDescription += ','
        #         if len(event['prices']) > 1 and i == len(event['prices'])-2:
        #             priceDescription += ' and'
        # 
        #     if event['isFree']:
        #         event['priceDescription'] = 'This event is FREE!'
        #     else:
        #         event['priceDescription'] = priceDescription + '.'
        # 
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
     
        try:
            auths = event['tags']['Required auth\'s']
        except KeyError:
            auths=None
     
        if auths:
            event['authorizationDescription'] = "Required authorizations: "
     
            if len(auths) > 0:
                event['authorizationDescription'] += ','.join(auths)
     
        else:
            event['authorizationDescription'] = None
        
        return event