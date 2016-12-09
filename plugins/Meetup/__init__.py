# -*- coding: utf-8 -*-

import ui

from ..Plugin import Plugin

class MeetupPlugin(Plugin):
	def __init__(self):
		super().__init__('Meetup')

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
