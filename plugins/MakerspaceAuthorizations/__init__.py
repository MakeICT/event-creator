# -*- coding: utf-8 -*-

import ui

from ..Plugin import Plugin

class MakerspaceAuthorizationsPlugin(Plugin):
	def __init__(self):
		super().__init__('MakerspaceAuthorizations')

		self.options = [
			{
				'name': 'Authorization list',
				'type': 'text',
			}
		]

		ui.addTarget('Makerspace Authorizations', self.createEvent)
		
	def createEvent(self, event):
		print(event)
		pass

def load():
	return MakerspaceAuthorizationsPlugin()
