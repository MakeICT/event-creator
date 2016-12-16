# -*- coding: utf-8 -*-

import httplib2
import json

from PySide import QtGui, QtCore
from apiclient import discovery

from ..Plugin import Plugin
from plugins import GoogleApps
from config import settings

import ui

from PySide import QtCore

class GoogleCalendarPlugin(GoogleApps.GoogleAppsPlugin):
	def __init__(self):
		super().__init__('GoogleCalendar')
		
		self.options = [
			{
				'name': 'Calendar ID', #@TODO: Allow user to specify multiple google calendar ID's
				'type': 'text',
			},{
				'name': 'Resources',
				'type': 'text',
			}
		]
		#@TODO: Add option for "pre" event/setup event on Google Calendar (we will use this for checkins)

		self._setResourceObjects(json.loads(self.getSetting('Resources', '[]')))
		ui.addTarget(self.name, self, self.createEvent)
		ui.addAction(self.name, 'Refresh resources', self.refreshResources)
	
	def _setResourceObjects(self, objs):
		ui.removeTagGroup('Resources')
		self.resourceObjects = objs
		if len(self.resourceObjects) > 0:
			resources = []
			for resource in self.resourceObjects:
				resources.append(resource['resourceName'])
			ui.addTagGroup('Resources', resources)
	
	def refreshResources(self):
		credentials = GoogleApps.getCredentials()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('admin', 'directory_v1', http=http)

		response = service.resources().calendars().list(customer='my_customer').execute()
		self.saveSetting('Resources', json.dumps(response['items']))
		self._setResourceObjects(response['items'])
		
	def createEvent(self, event):
		if settings.value('timezone') is not None and settings.value('timezone') != '':
			timezoneOffset = settings.value('timezone').split(' UTC')[1]
		else:
			timezoneOffset = ''
			
		selectedResources = []
		for resourceTag in event['tags']['Resources']:
			for resource in self.resourceObjects:
				if resourceTag == resource['resourceName']:
					selectedResources.append({'email': resource['resourceEmail']})
					break
					
		if event['registrationURL'] != '':
			description = '<strong>Register here:\n'
			description += '<a href="' + event['registrationURL'] + '">' + event['registrationURL'] + '</a></strong>\n'
			description += '<hr/>' + event['description']
		else:
			description = event['description']
			
		description += '\n\n' + event['priceDescription']

		eventData = {
			'summary': event['title'],
			'location': event['location'],
			'description': description,
			'start': {'dateTime': event['startTime'].toString(QtCore.Qt.ISODate) + timezoneOffset},
			'end': {'dateTime': event['stopTime'].toString(QtCore.Qt.ISODate) + timezoneOffset},
			'attendees': selectedResources
		}
		
		self.checkForInterruption()
		http = GoogleApps.getCredentials().authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)

		self.checkForInterruption()
		event = service.events().insert(calendarId=self.getSetting('Calendar ID', 'primary'), body=eventData).execute()
		
		return event['htmlLink']
		
def load():
	return GoogleCalendarPlugin()
