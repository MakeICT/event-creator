# -*- coding: utf-8 -*-

import logging

import httplib2
import base64
import ui
import plugins

from email.mime.text import MIMEText
from apiclient import discovery

from config import settings

def load():
	from plugins import GoogleApps
	
	class GmailPlugin(GoogleApps.GoogleAppsPlugin):
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

			ui.addTarget(self.name, self, self.createDraftMessage)

		def createDraftMessage(self, event):
			logging.debug('Creating draft message')
			# if settings.value('timezone') is not None and settings.value('timezone') != '':
			# 	timezoneOffset = settings.value('timezone').split(' UTC')[1]
			# 	tzName = ' ' + settings.value('timezone').split(' ')[-2]
			# else:
			# 	timezoneOffset = ''
			# 	tzName = ''

			timezoneOffset=''
			tzName=''
				
			dateTimeFormat = self.getSetting('Date/Time format', 'yyyy MMM dd - h:mm ap')

			htmlBody = '<html><body><table>'
			htmlBody += '<tr><td>Event:</td><td><strong>' + event['title'] + '</strong></td></tr>'
			htmlBody += '<tr><td>Location:</td><td>' + event['location'] + '</td></tr>'
			htmlBody += '<tr><td>Starting:</td><td>' + event['startTime'].toString(dateTimeFormat) + tzName + '</td></tr>'
			htmlBody += '<tr><td>Ending:</td><td>' + event['stopTime'].toString(dateTimeFormat) + tzName + '</td></tr>'
			if event['registrationURL'] is not None and event['registrationURL'] != '':
				htmlBody += '<tr><td>Register:</td><td>' + event['registrationURL'] + '</td></tr>'
			htmlBody += '</table>'

			htmlBody += '\n\n' + event['instructorDescription']
			htmlBody += '\n\n' + event['description']
			htmlBody += '\n\n' + event['authorizationDescription']
			htmlBody += '\n\n' + event['priceDescription'] + '</body></html>'
				
			subject = 'Event notice: ' + event['title'] + ' (' + event['startTime'].toString(dateTimeFormat) + tzName + ')'
			
			msg = self._createMessage(self.getSetting('Destinations'), subject, htmlBody)

			self.checkForInterruption()
			http = GoogleApps.getCredentials().authorize(httplib2.Http())
			service = discovery.build('gmail', 'v1', http=http)

			self.checkForInterruption()
			draft = service.users().drafts().create(userId='me', body=msg).execute()
			
			logging.debug('Draft created: ' + draft['message']['id'])
			return 'https://mail.google.com/mail/#drafts?compose=%s' % draft['message']['id']
			
		def _createMessage(self, to, subject, body):
			body = body.replace('\n', '<br/>')
			
			message = MIMEText(body, 'html')
			message['to'] = to
			message['subject'] = subject
			
			return {
				'message': {
					'raw': base64.urlsafe_b64encode(bytes(message.as_string(), 'utf-8')).decode(),
				}
			}

	return GmailPlugin()
