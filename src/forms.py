import sys, datetime, dateparser, json, os
from dateutil.parser import parse
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, \
                    BooleanField, IntegerField, DecimalField, \
                    DateField, DateTimeField, TextAreaField, TimeField, \
                    SelectMultipleField
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

    authorizations = SelectMultipleField('Required Authorizations', choices=[])
            
    submit = SubmitField('Submit')

    templateRequiredAuths = []
    template_map = {}
    templates = []
    
    selectedTemplateName = ""
    selectedTemplateFullName = ""
            
    def setSelectedAuthorizations(self, selected):
        self.auths = selected



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
            'pre-requisites': [self.authorizations.data],
            'resources':[],
        }
        
        if self.memberPrice is not None:
           event['prices'].append({
            'name': 'MakeICT Members',
            'price': float(self.memberPrice.data),
            'description': '',
            'availability': ['Members']                
            })
            
        if self.nonMemberPrice is not None:
           event['prices'].append({
            'name': 'Non-Members',
            'price': float(self.nonMemberPrice.data),
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
        
    
    def populateTemplate(self, templateName):
    
        templateFile = self.template_map.get(templateName, '')
        
        if self.isBlank(templateFile):
            templateFile = self.template_map.get('default')
            
        with open(templateFile) as json_file:
            
            self.selectedTemplateName = templateName
            self.selectedTemplateFullName = templateFile[15:]
            self.selectedTemplateFullName = self.selectedTemplateFullName.replace("\\", "/")

            
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
                                    
    def saveTemplate(self, event, templateName):        
        
        if templateName != '':
            if not templateName.endswith(".js"):
                templateName += ".js"
        
            value = event.get('classDate', '')            
            if value :
                del event['classDate']
     
            value = event.get('startTime', '')            
            if value :
                event['startTime'] = value.isoformat() 
     
            value = event.get('stopTime', '')            
            if value :
                event['stopTime'] = value.isoformat()
     
    
            self.createDirectoryIfNeeded(templateName)
            with open('EventTemplates/' + templateName , 'w') as outfile:
                jstr = json.dump(event, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            return os.path.basename(outfile.name)
        
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