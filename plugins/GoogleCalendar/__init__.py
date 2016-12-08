# -*- coding: utf-8 -*-

import ui

class GoogleCalendarPlugin:
	def __init__(self):
		self.options = [
			{
				'name': 'API Key',
				'type': 'text',
			}
		]

		ui.addTarget('Google Calendar', self.createEvent)
		
	def createEvent(self, event):
		print(event)
		pass

def load():
	return GoogleCalendarPlugin()
