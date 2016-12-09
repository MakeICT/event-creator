# -*- coding: utf-8 -*-

import ui
from PySide import QtCore

from .WildApricotAPI import WaApiClient

from config import settings

class WildApricotPlugin(QtCore.QObject):
	def __init__(self):
		self.options = [
			{
				'name': 'API Key',
				'type': 'text',
			},{
				'name': 'Client ID',
				'type': 'text',
			},{
				'name': 'Client secret',
				'type': 'text',
			},{
				'name': 'Customer ID',
				'type': 'text',
			}
		]

		ui.addTarget('WildApricot', self.createEvent)
		
	def createEvent(self, event):
		api = WaApiClient()
		api.authenticate_with_apikey(self._getSetting('API Key'))

		# @todo: add authorizations to description
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
			"RegistrationEnabled": False,
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
		
		eventID = api.execute_request('Events', eventData)
		print(eventID)


	def _getSetting(self, setting):
		return settings.value('plugin-WildApricot/%s' % setting)
	
def load():
	return WildApricotPlugin()