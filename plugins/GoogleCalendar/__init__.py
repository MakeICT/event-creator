# -*- coding: utf-8 -*-

import httplib2

from PySide import QtGui, QtCore

from apiclient import discovery

import ui

from ..Plugin import Plugin
from plugins import GoogleApps

from config import settings

class GoogleCalendarPlugin(Plugin):
	def __init__(self):
		super().__init__('GoogleCalendar')
		
		self.options = [{
			'name': 'Calendar ID',
			'type': 'text',
		}]

		ui.addTarget(self.name, self.createEvent)
		
	def createEvent(self, event):
		credentials = GoogleApps.getCredentials()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)
		
		if settings.value('timezone') is not None and settings.value('timezone') != '':
			timezoneOffset = settings.value('timezone').split(' UTC')[1]
		else:
			timezoneOffset = ''

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
