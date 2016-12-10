# -*- coding: utf-8 -*-

import httplib2
import ui
import base64

from email.mime.text import MIMEText
from apiclient import discovery

from ..Plugin import Plugin
from plugins import GoogleApps

from config import settings

class GmailPlugin(Plugin):
	def __init__(self):
		super().__init__('Gmail')

		self.options = [
			{
#				'name': 'Subject format', #@TODO: allow user to format gmail subject string
#				'type': 'text',
#			},{
#				'name': 'Sender', #@TODO: allow user to specify gmail FROM address
#				'type': 'text',
#			},{
				'name': 'Destinations',
				'type': 'text',
			},{
				'name': 'Date/Time format',
				'type': 'text',
#			},{
#				'name': 'Leave as draft', #@TODO: allow gmail messages to be sent right away
#				'type': 'yesno',
			}
		]

		ui.addTarget(self.name, self.createDraftMessage)

	def createDraftMessage(self, event):
		credentials = GoogleApps.getCredentials()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('gmail', 'v1', http=http)
		
		if settings.value('timezone') is not None and settings.value('timezone') != '':
			timezoneOffset = settings.value('timezone').split(' UTC')[1]
			tzName = ' ' + settings.value('timezone').split(' ')[-2]
		else:
			timezoneOffset = ''
			tzName = ''
			
		dateTimeFormat = self.getSetting('Date/Time format', 'yyyy MMM dd - h:mm ap')

		htmlBody = '<table>'
		htmlBody += '<tr><td>Event:</td><td><strong>' + event['title'] + '</strong></td></tr>'
		htmlBody += '<tr><td>Location:</td><td>' + event['location'] + '</td></tr>'
		htmlBody += '<tr><td>Starting:</td><td>' + event['startTime'].toString(dateTimeFormat) + tzName + '</td></tr>'
		htmlBody += '<tr><td>Ending:</td><td>' + event['stopTime'].toString(dateTimeFormat) + tzName + '</td></tr>'
		htmlBody += '</table><br/>' + event['description']
			
		subject = 'Event notice: ' + event['title'] + ' (' + event['startTime'].toString(dateTimeFormat) + tzname + ')'
		
		msg = self._createMessage(self.getSetting('Destinations'), subject, htmlBody)
		draft = service.users().drafts().create(userId='me', body=msg).execute()
		print(draft)
	
	def _createMessage(self, to, subject, body):
		message = MIMEText(body)
		message['to'] = to
		message['subject'] = subject
		
		return {
			'message': {
				'raw': base64.urlsafe_b64encode(bytes(message.as_string(), 'utf-8')).decode(),
			}
		}

def load():
	return GmailPlugin()
