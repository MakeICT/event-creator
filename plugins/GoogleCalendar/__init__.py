# -*- coding: utf-8 -*-

import httplib2

from PySide import QtGui, QtCore
from apiclient import discovery

from ..Plugin import Plugin
from plugins import GoogleApps
from config import settings

import ui

class GoogleCalendarPlugin(Plugin):
	def __init__(self):
		super().__init__('GoogleCalendar')
		
		self.options = [{
			'name': 'Calendar ID', #@TODO: Allow user to specify multiple google calendar ID's
			'type': 'text',
		}]
		#@TODO: Add option for "pre" event/setup event on Google Calendar (we will use this for checkins)

		ui.addTarget(self.name, self.createEvent)
		
	def createEvent(self, event):
		credentials = GoogleApps.getCredentials()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)
		
		if settings.value('timezone') is not None and settings.value('timezone') != '':
			timezoneOffset = settings.value('timezone').split(' UTC')[1]
		else:
			timezoneOffset = ''
			
		#@TODO: add link to registration URL to google calendar event

		event = {
			'summary': event['title'],
			'location': event['location'],
			'description': event['description'],
			'start': {'dateTime': event['startTime'].toString(QtCore.Qt.ISODate) + timezoneOffset},
			'end': {'dateTime': event['stopTime'].toString(QtCore.Qt.ISODate) + timezoneOffset},
		}
		
		event = service.events().insert(calendarId=self.getSetting('Calendar ID', 'primary'), body=event).execute()
		
def load():
	return GoogleCalendarPlugin()
