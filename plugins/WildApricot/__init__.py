# -*- coding: utf-8 -*-

import ui
from PySide import QtCore

from .WildApricotAPI import WaApiClient
from plugins import Plugin

from config import settings
import config

class WildApricotPlugin(Plugin):
	def __init__(self):
		super().__init__('WildApricot')
		
		self.options = [
			{
				'name': 'API Key',
				'type': 'text',
			},{
				'name': 'Level IDs for members',
				'type': 'text',
			},{
				'name': 'Registration URL format',
				'type': 'text',
			},{
				'name': 'Use this as registration URL',
				'type': 'yesno',
			}
		]

		ui.addTarget(self.name, self, self.createEvent)
		ui.addPopulationType('Members')
	
	def createEvent(self, event):
		if settings.value('timezone') is not None and settings.value('timezone') != '':
			timezoneOffset = settings.value('timezone').split(' UTC')[1]
		else:
			timezoneOffset = ''
		
		eventData = {
			"Name": 'TEST: ' + event['title'],
			"StartDate": event['startTime'].toString(QtCore.Qt.ISODate) + timezoneOffset,
			"EndDate": event['stopTime'].toString(QtCore.Qt.ISODate) + timezoneOffset,
			"Location": event['location'],
			"RegistrationsLimit": event['registrationLimit'],
			"RegistrationEnabled": True,
			"StartTimeSpecified": True,
			"EndTimeSpecified": True,
			"Details": {
				"DescriptionHtml": event['description'],
				"AccessControl": { "AccessLevel": "Public" },
				"GuestRegistrationSettings": { "CreateContactMode": "CreateContactForAllGuests" },
				"PaymentMethod": "OnlineOnly",
				"SendEmailCopy": False,
				"WaitListBehaviour": "Disabled",
			},
		}
		
		#@TODO: open ticket with WildApricot so that we can have an API endpoint for enabling email reminders
		self.checkForInterruption()
		api = WaApiClient()
		api.authenticate_with_apikey(self.getSetting('API Key'))

		self.checkForInterruption()
		eventID = api.execute_request('Events', eventData)

		for rsvpType in event['prices']:
			registrationTypeData = {
				"EventId": eventID,
				"Name": rsvpType['name'],
				"BasePrice": rsvpType['price'],
				"Description": rsvpType['description'],
				"IsEnabled": True,
				"GuestRegistrationPolicy": "Disabled",
				"MultipleRegistrationAllowed": False,
				"WaitlistBehaviour": "Disabled",
				"UnavailabilityPolicy": "Show"
			}
			
			for populationType in rsvpType['availability']:
				if populationType == 'Members':
					registrationTypeData['Availability'] = 'MembersOnly'
					registrationTypeData['AvailableForMembershipLevels'] = []
					
					ids = self.getSetting('Level IDs for members').split(',')
					for id in ids:
						registrationTypeData['AvailableForMembershipLevels'].append({'Id': id})
				else:
					registrationTypeData['Availability'] = 'Everyone'
			
			self.checkForInterruption()
			api.execute_request('EventRegistrationTypes', registrationTypeData)
			
		if config.checkBool(self.getSetting('Use this as registration URL')):
			event['registrationURL'] = self.getSetting('Registration URL format', '%s') % eventID
			return event['registrationURL']
			
		if self.getSetting('Registration URL format', '') == '':
			waEvent = api.execute_request('Events/%s' % eventID)
			return waEvent['Url']
		else:
			return self.getSetting('Registration URL format', '%s') % eventID

def load():
	return WildApricotPlugin()
