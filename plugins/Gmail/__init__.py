# -*- coding: utf-8 -*-

import ui

from ..Plugin import Plugin

class GmailPlugin(Plugin):
	def __init__(self):
		super().__init__('Gmail')

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
