# -*- coding: utf-8 -*-

import ui

class FacebookPlugin:
	def __init__(self):
		self.options = [
			{
				'name': 'Username',
				'type': 'text',
			},{
				'name': 'Password',
				'type': 'password',
			}
		]

		ui.addTarget('Facebook', self.createEvent)
		
	def createEvent(self, event):
		print(event)
		pass

def load():
	return FacebookPlugin()
