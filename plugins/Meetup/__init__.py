# -*- coding: utf-8 -*-

import ui

class MeetupPlugin:
	def __init__(self):
		self.options = [
			{
				'name': 'API Key',
				'type': 'text',
			}
		]

		ui.addTarget('Meetup', self.createEvent)
		
	def createEvent(self, event):
		print(event)
		pass

def load():
	return MeetupPlugin()
