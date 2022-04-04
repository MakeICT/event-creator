# -*- coding: utf-8 -*-

import logging
from requests_oauthlib import OAuth2Session
import pytz
from time import time
import pandas as pd

from gql import Client, gql
# from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport

#add meetup api module from git submodule to path
import importlib
import sys
import os
import json
sys.path.insert(1, '~/Projects/MakeICT/event-creator/src/plugins/Meetup/meetup_api/')


# from plugins.Meetup.meetup.api import Client
# from plugins.Meetup.meetup import exceptions

from plugins import EventPlugin
import config


class MeetupPlugin(EventPlugin):
    oauth = None
    token = None
    client_id = None
    client_secret = None

    redirect_uri = None
    base_url = 'https://secure.meetup.com/oauth2'
    token_url = base_url + '/access'
    auth_url = base_url + '/authorize'
    gql_url = 'https://api.meetup.com/gql'

    def __init__(self):
        super().__init__('Meetup')
        self.client_id = self.getSetting('client id')
        self.client_secret = self.getSetting('client secret')
        self.redirect_uri = self.getSetting('redirect uri')

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
        
    def token_saver(self, token):
        print("Saving Token!!")
        config.save('plugin-Meetup', 'token', json.dumps(token))
        self.token = token

    def authenticateOauth(self):
        extra = {
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        self.token = config.settings.get('plugin-Meetup', 'token')
        if self.token:
            self.token = json.loads(self.token)
            self.oauth = OAuth2Session(self.client_id, auto_refresh_url=self.token_url, redirect_uri=self.redirect_uri,
                                  auto_refresh_kwargs=extra, token_updater=self.token_saver, token=self.token)
        else:
            self.oauth = OAuth2Session(self.client_id, auto_refresh_url=self.token_url, redirect_uri=self.redirect_uri,
                                auto_refresh_kwargs=extra, token_updater=self.token_saver)
            authorization_url, state = self.oauth.authorization_url(self.auth_url)
            print(authorization_url)

            print('Please go to %s and authorize access.' % authorization_url)
            authorization_response = input('Enter the full callback URL: ')

            self.token = self.oauth.fetch_token(
                    self.token_url,
                    authorization_response=authorization_response,
                    include_client_id=True,
                    client_secret=self.client_secret)
            self.token_saver(self.token)
        
        if self.token['expires_at'] < time() + 60:
            new_token = self.oauth.refresh_token(self.token_url, **extra)
            print(new_token)
            self.token_saver(new_token)

        print(self.token)
        # return api

    def _call(self, query, variables):
        self.authenticateOauth()

        headers = {
            'Authorization': 'Bearer ' + self.token['access_token'],
            'Content-Type': 'application/json'
        }

        # Select your transport with a defined url endpoint
        transport = RequestsHTTPTransport(url=self.gql_url, headers=headers)

        # Create a GraphQL client using the defined transport
        client = Client(transport=transport, fetch_schema_from_transport=False)

        result = client.execute(gql(query), variable_values=variables)

        return result

    def _buildEvent(self, event):
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
            publish_status = 'DRAFT'
        else:
            publish_status = 'PUBLISHED'

        meetup_details = {
            'groupUrlname': self.getSetting('group name'),
            'title': title,
            'description': description,
            'startDateTime': timezone.localize(event.startDateTime()).strftime("%Y-%m-%dT%H:%M"),
            'duration': pd.Timedelta(event.endDateTime() - event.startDateTime()).isoformat(),
            'venueId': self.getSetting('Venue ID'),
            'publishStatus': publish_status,
            # 'rsvp_limit': rsvp_limit,
            # 'guest_limit': 0,
            # 'waitlisting': 'off',
        }
        # print(meetup_details['time'])
        if event.registrationURL():
            meetup_details['question'] = \
                "This event requires external registration. Please follow " \
                "the link in the event description to register for this class. " \
                "Registering on Meetup does not reserve your spot for this event."

        return meetup_details

    def createEvent(self, event):
        event_data = self._buildEvent(event)
        query = """
        mutation($input: CreateEventInput!) {
          createEvent(input: $input) {
            event {
              id
              eventUrl
            }
            errors {
              message
              code
              field
            }
          }
        }
        """

        variables = {
            "input": {
                **event_data
            }
        }

        # if config.checkBool(self.getSetting('Use this as registration URL')):
        #     event['registrationURL'] = meetupEvent.event_url

        result = self._call(query, variables)
        print(result)

        event_info = result['createEvent']['event']
        return (event_info['id'].split('!')[0], event_info['eventUrl'])

    def updateEvent(self, event):
        event_data = self._buildEvent(event)
        meetup_id = event.getExternalEventByPlatformName('Meetup').ext_event_id
        event_data['eventId'] = meetup_id.split('!')[0]
        event_data.pop('groupUrlname')

        query = """
        mutation($input: EditEventInput!) {
          editEvent(input: $input) {
            event {
              id
              eventUrl
            }
            errors {
              message
              code
              field
            }
          }
        }
        """

        variables = {
            "input": {
                **event_data
            }
        }

        print(meetup_id)
        result = self._call(query, variables)
        print(result)

        event_info = result['editEvent']['event']
        return (event_info['id'], event_info['eventUrl'])

    def deleteEvent(self, event):
        meetup_id = event.getExternalEventByPlatformName('Meetup').ext_event_id.split('!')[0]


        query = """
        mutation($input: DeleteEventInput!) {
          deleteEvent(input: $input) {
            success
            errors {
              message
              code
              field
            }
          }
        }
        """

        variables = {
            "input": {
                "eventId": meetup_id
            }
        }

        result = self._call(query, variables)
        print(result)
        if not result['deleteEvent']['success']:
            print('Already deleted?')


def load():
    return MeetupPlugin()
