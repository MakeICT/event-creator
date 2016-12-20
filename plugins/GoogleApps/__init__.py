# -*- coding: utf-8 -*-

import httplib2
import os
import time

from PySide import QtGui, QtCore

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

import ui

from plugins import Plugin
from . import codeReceiver

credentials = None
instance = None

class GoogleAppsPlugin(Plugin):
	def __init__(self, name='GoogleApps'):
		global instance
		
		super().__init__(name)
		self.options = [
			{
				'name': 'Application name',
				'type': 'text',
			},{
				'name': 'Client ID',
				'type': 'text',
			},{
				'name': 'Client secret',
				'type': 'password',
			}
		]
		
		if name == 'GoogleApps' and instance is None:
			instance = self
			ui.addAction(self.name, 'Authorize', self._getCredentials)
		
	def _getCredentials(self):
		global credentials
		# @TODO: consider saving Google credentials to a file so authorization can persist across executions
		if credentials is None or credentials.invalid:
			flow = OAuth2WebServerFlow(
				client_id = self.getSetting('Client ID'),
				client_secret = self.getSetting('Client secret'),
				scope = [
					'https://www.googleapis.com/auth/calendar',
					'https://www.googleapis.com/auth/gmail.compose',
					'https://www.googleapis.com/auth/gmail.send',
					'https://www.googleapis.com/auth/admin.directory.resource.calendar',
				],
				#redirect_uri = 'urn:ietf:wg:oauth:2.0:oob',
				redirect_uri = 'http://localhost:8080/',
			)
			
			# bug in google code and encoding chars?
			authURI = flow.step1_get_authorize_url().replace('%3A', ':').replace('%2F', '/')
			
			QtGui.QDesktopServices.openUrl(authURI)
			#code = QtGui.QInputDialog.getText(None, 'Authorization', 'Enter the authorization code here:')
			#QtGui.QMessageBox.information(None, 'Authorization required...', 'Please authorize in the web browser')
			dialog = QtGui.QDialog(None)
			dialog.show()
			code = codeReceiver.waitForCode()
			dialog.hide()
				
			credentials = flow.step2_exchange(code)
		
		return credentials

	def prepare(self):
		instance._getCredentials()

def load():
	global instance
	if instance is None:
		instance = GoogleAppsPlugin()
	return instance

def getCredentials():
	return instance._getCredentials()
