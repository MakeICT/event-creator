# -*- coding: utf-8 -*-

import ui

from ..Plugin import Plugin

class GoogleCalendarPlugin(Plugin):
	def __init__(self):
		super().__init__('GoogleCalendar')

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
