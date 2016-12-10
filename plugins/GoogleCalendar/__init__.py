# -*- coding: utf-8 -*-

import httplib2
import json

from PySide import QtGui, QtCore
from apiclient import discovery

from ..Plugin import Plugin
from plugins import GoogleApps
from config import settings

import ui

class GoogleCalendarPlugin(Plugin):
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
		ui.addTarget(self.name, self.createEvent)
	
	def _setResourceObjects(self, objs):
		ui.removeTagGroup('Resources')
		self.resourceObjects = objs
		if len(self.resourceObjects) > 0:
			resources = []
			for resource in self.resourceObjects:
				resources.append(resource['resourceName'])
			ui.addTagGroup('Resources', resources)
	
	#@TODO: Make this available through the UI
	def refreshResources(self):
		credentials = GoogleApps.getCredentials()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('admin', 'directory_v1', http=http)

		response = service.resources().calendars().list(customer='my_customer').execute()
		self.saveSetting('Resources', json.dumps(response['items']))
		self._setResourceObjects(response['items'])
		
	def createEvent(self, event):
		credentials = GoogleApps.getCredentials()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)
		
		if settings.value('timezone') is not None and settings.value('timezone') != '':
			timezoneOffset = settings.value('timezone').split(' UTC')[1]
		else:
			timezoneOffset = ''
			
		#@TODO: add link to registration URL to google calendar event description
		selectedResources = []
		for resourceTag in event['tags']['Resources']:
			for resource in self.resourceObjects:
				if resourceTag == resource['resourceName']:
					selectedResources.append({'email': resource['resourceEmail']})
					break
		
		eventData = {
			'summary': event['title'],
			'location': event['location'],
			'description': event['description'],
			'start': {'dateTime': event['startTime'].toString(QtCore.Qt.ISODate) + timezoneOffset},
			'end': {'dateTime': event['stopTime'].toString(QtCore.Qt.ISODate) + timezoneOffset},
			'attendees': selectedResources
		}
		
		event = service.events().insert(calendarId=self.getSetting('Calendar ID', 'primary'), body=eventData).execute()
		
def load():
	return GoogleCalendarPlugin()
