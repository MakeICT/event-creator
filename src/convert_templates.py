import json
import os
from dateutil.parser import parse

from main import db
from models import Event, EventTemplate, EventType
from models import Platform, Price, Resource, Authorization


# import logging

# logging.basicConfig(filename='db.log')
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class JSON_Template():
    fields_names = [
        'title',
        'host_name',
        'host_email',
        'location',
        'description',
        'registration_limit',
        'duration',
        'min_age',
        'max_age',
        'event_type',
        'image_file',
        'platforms',
        'authorizations',
        'resources',
        'prices',
        ]

    def __init__(self, path):
        self.populateTemplate(path)

    def isBlank(self, myString):
        return not (myString and myString.strip())

    def isNotBlank(self, myString):
        return bool(myString and myString.strip())

    def populateTemplate(self, path):
        with open(path) as json_file:
            data = json.load(json_file)

            self.title = data.get('title', '')
            self.description = data.get('description', '')
            self.host_email = data.get('instructorEmail', '')
            self.host_name = data.get('instructorName', '')
            self.location = data.get('location', '')
            self.registration_limit = data.get('registrationLimit', '')

            value = data.get('classDate', '')
            if self.isNotBlank(value):
                self.classDate = parse(value, fuzzy=True)

            value = data.get('startTime', '')
            if self.isNotBlank(value):
                self.starttime = parse(value, fuzzy=True)

            value = data.get('stopTime', '')
            if self.isNotBlank(value):
                self.endtime = parse(value, fuzzy=True)

            self.duration = self.endtime - self.starttime

            self.min_age = data.get('minimumAge', '')
            self.max_age = data.get('maximumAge', '')

            self.event_type = EventType._class
            self.image_file = 'default.jpg'

            # linked tables
            self.price_list = data.get('prices', [])

            taglist = data.get('tags', [])

            self.req_auths = []
            self.calendar_resources = []

            for tags in taglist:
                if tags == "Required auth's":
                    self.req_auths = taglist[tags]
                elif tags == "Resources":
                    for r in taglist[tags]:
                        if r[0:11] == 'Makerspace ':
                            r = r[11:]
                        self.calendar_resources.append(r)

            self.platforms = Platform.query.all()
            self.authorizations = [Authorization.query.filter_by(name=auth).first()
                                   for auth in self.req_auths]
            self.resources = [Resource.query.filter_by(name=res).first()
                              for res in self.calendar_resources]
            self.prices = [Price(name=price['name'],
                           description=price['description'],
                           value=price['price'],
                           availability=price['availability'][0] if price['availability'] else "")
                           for price in self.price_list]

    def printTemplate(self):
        for field in self.fields_names:
            try:
                print(f"{field}: {getattr(self, field)}")
            except AttributeError:
                pass

    def convertTemplate(self):
        # breakpoint()
        db_template = EventTemplate()
        for field in self.fields_names:
            try:
                # print(f"{field}: {getattr(self, field)}")
                setattr(db_template, field, getattr(self, field))
            except (AttributeError, TypeError):
                pass
        if db_template.title:
            db.session.add(db_template)
            db.session.commit()


basepath = './EventTemplates/'
EventTemplate.query.delete()
Price.query.delete()

# r=root, d=directories, f = files
count = 0
for r, d, f in os.walk(basepath):
    for file in f:
        count = count+1
        # print('\n\n')
        t = JSON_Template(os.path.join(r, file))
        t.convertTemplate()
        t.printTemplate()
        print('\n\n')

print(len(EventTemplate.query.all()), count)

for t in EventTemplate.query.all():
    attrs = vars(t)
    # print(f"{t.title}:\n {t.prices} \n {t.authorizations}")