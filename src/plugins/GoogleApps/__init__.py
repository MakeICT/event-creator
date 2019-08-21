# -*- coding: utf-8 -*-

import logging
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

credentialsPath = os.path.join(os.path.dirname(__file__), 'credentials.dat')
instance = None
waitForAuthDialog = None


class GoogleAppsPlugin(Plugin):
    def __init__(self, name='GoogleApps'):
        global instance

        super().__init__(name)
        self.options = [
            {
                'name': 'Client ID',
                'type': 'text',
            },{
                'name': 'Client secret',
                'type': 'password',
            }
        ]

        if name == 'GoogleApps' and instance is None:
            instance = self
            ui.addAction(self.name, 'Reauthorize', self.reauthorize)

    def reauthorize(self):
        if os.path.exists(credentialsPath):
            logging.debug('Deleting credentials')
            os.remove(credentialsPath)

        self._getCredentials()

    def _getCredentials(self, callback=None):
        storage = Storage(credentialsPath)
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            logging.debug('Missing or bad credentials. Authorization required')

            flow = OAuth2WebServerFlow(
                client_id = self.getSetting('Client ID'),
                client_secret = self.getSetting('Client secret'),
                prompt = 'consent',
                scope = [
                    'https://www.googleapis.com/auth/calendar',
                    'https://www.googleapis.com/auth/gmail.compose',
                    'https://www.googleapis.com/auth/gmail.send',
                    'https://www.googleapis.com/auth/admin.directory.resource.calendar',
                ],
                redirect_uri = 'http://localhost:8080/',
            )

            # bug in google code and encoding chars?
            authURI = flow.step1_get_authorize_url().replace('%3A', ':').replace('%2F', '/')
            QtGui.QDesktopServices.openUrl(authURI)

            dialog = showWaitForCodeDialog()
            def codeReceived(code):
                dialog.hide()
                credentials = flow.step2_exchange(code)
                storage.put(credentials)
                if callback is not None:
                    callback(credentials)

            codeReceiver.waitForCode(codeReceived)
        else:
            if callback is not None:
                callback(credentials)

        return credentials

    def prepare(self, callback=None):
        instance._getCredentials(callback)


def showWaitForCodeDialog():
    global waitForAuthDialog

    if waitForAuthDialog is None:
        waitForAuthDialog = QtGui.QDialog(None)
        waitForAuthDialog.setWindowTitle('Authorization required...')
        waitForAuthDialog.setModal(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel('A window requesting authorization will appear in your browser.\n\nPlease accept the authorization to continue.'))
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Cancel)
        layout.addWidget(buttonBox)
        waitForAuthDialog.setLayout(layout)

        buttonBox.rejected.connect(codeReceiver.cancel)
        buttonBox.rejected.connect(waitForAuthDialog.close)

    waitForAuthDialog.show()

    return waitForAuthDialog


def load():
    global instance
    if instance is None:
        instance = GoogleAppsPlugin()
    return instance


def getCredentials(callback=None):
    return instance._getCredentials(callback)
