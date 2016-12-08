# -*- coding: utf-8 -*-

import ui

class WildApricotPlugin:
	def __init__(self):
		self.options = [
			{
				'name': 'API Key',
				'type': 'text',
			},{
				'name': 'Customer ID',
				'type': 'text',
			}
		]

		ui.addTarget('WildApricot', self.createEvent)
		
	def createEvent(self, event):
		print(event)
		pass

def load():
	return WildApricotPlugin()