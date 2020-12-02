# -*- coding: utf-8 -*-

import logging
import requests 
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import pytz

#add meetup api module from git submodule to path
import importlib
import sys
import os
sys.path.insert(1, '~/Projects/MakeICT/event-creator/src/plugins/Meetup/meetup_api/')


from plugins.Meetup.meetup.api import Client
from plugins.Meetup.meetup import exceptions

from plugins import EventPlugin
import config

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("meetup.log")
logger.addHandler(file_handler)
logger.error("TEST LOG")

class MeetupPlugin(EventPlugin):
    api = None

    def __init__(self):
        super().__init__('Meetup')

        self.options = [
            {
                'name': 'API Key',
                'type': 'text',
            }, {
                'name': 'Group name',
                'type': 'text',
            }, {
                'name': 'Venue ID',
                'type': 'text',
            }, {
                'name': 'Use this as registration URL',
                'type': 'yesno',
            }, {
                'name': 'Title prepend',
                'type': 'text',
            }, {
                'name': 'Title append',
                'type': 'text',
            }, {
                'name': 'Allow RSVP',
                'type': 'yesno',
            }, {
                'name': 'Post as draft',
                'type': 'yesno',
            }
        ]
        # @TODO: Download venue list and add them to the location dropdown in the UI
        # ui.addTarget(self.name, self, self.createEvent)

    def connectAPI(self):
        logger.error("connect")
        try:
            client_id = self.getSetting('client id')
            client_secret = self.getSetting('client secret')
            email = self.getSetting('email')
            password = self.getSetting('password')

            redirect_uri = self.getSetting('redirect uri')
            base_url = 'https://secure.meetup.com/oauth2'
            token_url = base_url + '/access'
            auth_url = base_url + '/authorize'
            session_url = "https://api.meetup.com/sessions"

            # Request authorization code
            r_parameters = {"scope": 'event_management',
                            "client_id": {client_id},
                            "redirect_uri": {redirect_uri},
                            "response_type": 'anonymous_code'
                            }
            response = requests.get(auth_url, params=r_parameters)
            logger.error(f"MEETUP RESPONSE:{response.status_code}, {response.reason}, {response.headers}, {response.url}")
            logger.error(dir(response))
            code = response.url.split('=')[1]
            logger.error(response.url)

            # Request access token
            r_parameters = {"client_id": {client_id},
                            "client_secret": {client_secret},
                            "grant_type": 'anonymous_code',
                            "redirect_uri": {redirect_uri},
                            "code": {code}
                            }
            response = requests.post(token_url, params=r_parameters)
            #logger.error('MEETUP RESPONSE:', response.status_code, response.headers, response.json())
            logger.error(response.status_code)
            access_token = response.json()['access_token']

            # Request oauth token with credentials
            r_parameters = {"email": {email},
                            "password": {password}
                            }
            r_headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.post(session_url, params=r_parameters, headers=r_headers)
            logger.error(f'MEETUP RESPONSE: {response.status_code}, {response.headers}, {response.json()}')
            oauth_token = response.json()['oauth_token']

            # Connect to API
            self.api = Client(oauth_token)

            # return api
        except:
            logger.error("CONNECT ERROR!")
            logger.error("CONNECT ERROR:", exc_info=True)

    def _buildEvent(self, event):
        logger.error("build")
        if self.getGeneralSetting('timezone') is not None \
                and self.getGeneralSetting('timezone') != '':
            timezone = pytz.timezone(self.getGeneralSetting('timezone'))
        else:
            timezone = pytz.timezone("UTC")

        title = event.title
        description = event.htmlSummary(omit=['time'])

        # if event['registrationURL'] != '':
        #     description = '<p>To register for this event, please visit ' \
        #         + '<a href="%s">%s</a></p><p><br></p>' \
        #         % (event['registrationURL'], event['registrationURL'])
        #     # description += '\n\n'
        # else:
        #     description = ''

        rsvp_limit = 1

        if config.checkBool(self.getSetting("Allow RSVP")):
            rsvp_limit = 0

        if config.checkBool(self.getSetting("post as draft")):
            publish_status = 'draft'
        else:
            publish_status = 'published'

        group = self.api.GetGroup({'urlname': self.getSetting('group name')})

        meetup_details = {
            'group_id': group.id,
            'urlname': self.getSetting('group name'),
            'name': title,
            'description': description,
            'time': int(timezone.localize(event.start_date).timestamp()) * 1000,
            'duration': int((event.end_date - event.start_date).total_seconds()*1000),
            'venue_id': self.getSetting('Venue ID'),
            'publish_status': publish_status,
            'rsvp_limit': rsvp_limit,
            'guest_limit': 0,
            'waitlisting': 'off',
        }
        # print(meetup_details['time'])
        if event.registrationURL():
            meetup_details['question_0'] = \
                "This event requires external registration. Please follow " \
                "the link in the event description to register for this class. " \
                "Registering on Meetup does not reserve your spot for this event."
        logger.error("finish build")
        return meetup_details

    def createEvent(self, event):
        self.connectAPI()
        logger.error("create")

        event_data = self._buildEvent(event)
        try:
            meetupEvent = self.api.CreateEvent(event_data)
        except:
            logger.error("ERROR:", exc_info=True)
        # print(meetupEvent.__dict__)

        # if config.checkBool(self.getSetting('Use this as registration URL')):
        #     event['registrationURL'] = meetupEvent.event_url
        logger.error("finish create")
        return (meetupEvent.id, meetupEvent.link)

    def updateEvent(self, event):
        logger.error("update")
        self.connectAPI()

        event_data = self._buildEvent(event)
        meetup_id = event.getExternalEventByPlatformName('Meetup').ext_event_id
        event_data['id'] = meetup_id
        print(meetup_id)
        meetupEvent = self.api.EditEvent(event_data)

        return (meetupEvent.id, meetupEvent.link)

    def deleteEvent(self, event):
        logger.error("delete")
        self.connectAPI()

        meetup_id = event.getExternalEventByPlatformName('Meetup').ext_event_id

        try:
            self.api.DeleteEvent({'id': meetup_id,'urlname': self.getSetting('group name')})
        except exceptions.HttpNotAccessibleError:
            print('Already deleted?')


def load():
    return MeetupPlugin()
