# -*- coding: utf-8 -*-

import meetup.api
import ui

from ..Plugin import Plugin

class MeetupPlugin(Plugin):
	def __init__(self):
		super().__init__('Meetup')

		self.options = [
			{
				'name': 'API Key',
				'type': 'text',
			},{
				'name': 'Group name',
				'type': 'text',
			},{
				'name': 'Venue ID',
				'type': 'text',
			},{
				'name': 'Official registration site',
				'type': 'yesno',
			}
		]

		ui.addTarget('Meetup', self.createEvent)
		
	def createEvent(self, event):
		api = meetup.api.Client(self.getSetting('API Key'))
		group = api.GetGroup({'urlname': self.getSetting('Group name')})
		
		if event['registrationURL'] != '':
			description = 'To register for this event, please visit <a href="%s">%s</a>' % (event['registrationURL'], event['registrationURL'])
			description += '\n\n'
		else:
			description = ''
			
		description += event['description']
		
		meetupEvent = api.CreateEvent({
			'group_id': group.id,
			'name': event['title'],
			'description': description,
			'time': event['startTime'].toTime_t() * 1000,
			'duration': event['startTime'].msecsTo(event['stopTime']),
			'venue_id': self.getSetting('Venue ID'),
			'publish_status': 'draft',
		})
		
		if config.checkBool(self.getSetting('Official registration site')):
			event['registrationURL'] = meetupEvent.event_url

		return event
		
def load():
	return MeetupPlugin()
