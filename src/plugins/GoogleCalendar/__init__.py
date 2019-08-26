# -*- coding: utf-8 -*-

import logging

import httplib2
from googleapiclient.errors import HttpError


import json
from googleapiclient import discovery

from config import settings


def load():
    from plugins import GoogleApps, EventPlugin

    class GoogleCalendarPlugin(GoogleApps.GoogleAppsPlugin, EventPlugin):
        def __init__(self):
            super().__init__('GoogleCalendar')

            self.options = [
                {
                    'name': 'Calendar ID',  # @TODO: Allow user to specify multiple google calendar ID's
                    'type': 'text',
                }, {
                    'name': 'Resources',
                    'type': 'text',
                }
            ]
            # @TODO: Add option for "pre" event/setup event on Google Calendar (we will use this for checkins)

            resourceJSON = json.loads(self.getSetting('Resources'))
            if resourceJSON != '':
                logging.debug('Loading resources from settings')
                self._setResourceObjects(json.loads(resourceJSON))

        def _setResourceObjects(self, objs):
            # ui.removeTagGroup('Resources')
            self.resourceObjects = objs
            if len(self.resourceObjects) > 0:
                resources = []
                for resource in self.resourceObjects:
                    resources.append(resource['resourceName'])
                # ui.addTagGroup('Resources', resources)

        def refreshResources(self):
            def credentialsReceived(credentials):
                logging.debug('Downloading resources')

                http = credentials.authorize(httplib2.Http())
                service = discovery.build('admin', 'directory_v1', http=http)

                response = service.resources().calendars() \
                    .list(customer='my_customer').execute()
                self.saveSetting('Resources', json.dumps(response['items']))
                self._setResourceObjects(response['items'])

            GoogleApps.getCredentials(credentialsReceived)

        def _buildEvent(self, event):
            timezone = self.getGeneralSetting('timezone')
            description = event.htmlSummary(omit=['time'])

            event_data = {
                'summary': event.title,
                'location': event.location,
                'description': description,
                'start': {'dateTime': event.start_date.isoformat(), 'timeZone': timezone},
                'end': {'dateTime': event.end_date.isoformat(), 'timeZone': timezone},
                # 'attendees': selectedResources
            }

            return event_data

        def createEvent(self, event):
            eventData = self._buildEvent(event)

            creds = GoogleApps.getCredentials()
            service = discovery.build('calendar', 'v3', credentials=creds)

            cal_event = service.events().insert(
                    calendarId=self.getSetting('Calendar ID', 'primary'),
                    body=eventData) \
                .execute()

            return (cal_event['id'], cal_event['htmlLink'])

        def updateEvent(self, event):
            eventData = self._buildEvent(event)

            creds = GoogleApps.getCredentials()
            service = discovery.build('calendar', 'v3', credentials=creds)

            event_id = next(item.ext_event_id for item in event.external_events
                            if item.platformName() == self.name)

            cal_event = service.events().update(
                    calendarId=self.getSetting('Calendar ID', 'primary'),
                    eventId=event_id,
                    body=eventData)

            try:
                result = cal_event.execute()
                print(result)
            except HttpError as err:
                if err.resp.status == 403:
                    return False
                else:
                    raise
            return True

    return GoogleCalendarPlugin()
