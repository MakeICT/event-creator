# -*- coding: utf-8 -*-

import logging

import meetup.api
import ui

from plugins import Plugin
import config

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
				'name': 'Use this as registration URL',
				'type': 'yesno',
			},{
				'name': 'Title prepend',
				'type': 'text',
			},{
				'name': 'Title append',
				'type': 'text',
			},{
				'name': 'Allow RSVP',
				'type': 'yesno',
			}
		]
		#@TODO: Allow option for publishing meetup events immediately
		#@TODO: Download venue list and add them to the location dropdown in the UI
		ui.addTarget(self.name, self, self.createEvent)
		
	def createEvent(self, event):
		api = meetup.api.Client(self.getSetting('API Key'))
		group = api.GetGroup({'urlname': self.getSetting('Group name')})
		
		if event['registrationURL'] != '':
			description = 'To register for this event, please visit <a href="%s">%s</a>' % (event['registrationURL'], event['registrationURL'])
			description += '\n\n'
		else:
			description = ''
			
		description += event['description']
		
		prepend = self.getSetting('Title prepend', '')
		append = self.getSetting('Title append', '')
		if prepend != '':
			title = prepend + ' ' + event['title']
		else:
			title = event['title']
			
		if append != '':
			title += ' ' + append
		rsvp_limit = 1;
		if config.checkBool(self.getSetting("Allow RSVP")):
			rsvp_limit=0

		meetup_details = {
			'group_id': group.id,
			'name': title,
			'description': description,
			'time': event['startTime'].toTime_t() * 1000,
			'duration': event['startTime'].msecsTo(event['stopTime']),
			'venue_id': self.getSetting('Venue ID'),
			'publish_status': 'draft',
			'rsvp_limit': rsvp_limit,
			'guest_limit': 0,
			'waitlisting': 'off',
		}
		if event['registrationURL'] != '':
			meetup_details['question_0'] = "This event requires external registration. Please follow the link in the event description to register for this class. Registering on Meetup does not reserve your spot for this event."
		
		self.checkForInterruption()
		meetupEvent = api.CreateEvent(meetup_details)
		
		if config.checkBool(self.getSetting('Use this as registration URL')):
			event['registrationURL'] = meetupEvent.event_url
			
		return meetupEvent.event_url

def load():
	return MeetupPlugin()
