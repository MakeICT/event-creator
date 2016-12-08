# -*- coding: utf-8 -*-

import ui

class GmailPlugin:
	def __init__(self):
		self.options = [
			{
				'name': 'API Key',
				'type': 'text',
			}
		]

		ui.addTarget('Gmail', self.createEvent)
		
	def createEvent(self, event):
		print(event)
		pass

def load():
	return GmailPlugin()
