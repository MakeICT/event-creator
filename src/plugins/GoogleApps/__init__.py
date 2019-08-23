# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import os

import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from plugins import Plugin

credentialsPath = os.path.join(os.path.dirname(__file__), 'credentials.json')
instance = None


class GoogleAppsPlugin(Plugin):
    def __init__(self, name='GoogleApps'):
        global instance

        super().__init__(name)
        self.options = [
            {
                'name': 'Client ID',
                'type': 'text',
            }, {
                'name': 'Client secret',
                'type': 'password',
            }
        ]

        if name == 'GoogleApps' and instance is None:
            instance = self

    def reauthorize(self):
        if os.path.exists(credentialsPath):
            logging.debug('Deleting credentials')
            os.remove(credentialsPath)

        self._getCredentials()

    def _getCredentials(self, callback=None):
        credentials = None
        SCOPES = ['https://www.googleapis.com/auth/calendar',
                  'https://www.googleapis.com/auth/admin.directory.resource.calendar']
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentialsPath, SCOPES)
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)

        else:
            if callback is not None:
                callback(credentials)

        return credentials

    def prepare(self, callback=None):
        instance._getCredentials(callback)


def load():
    global instance
    if instance is None:
        instance = GoogleAppsPlugin()
    return instance


def getCredentials(callback=None):
    return instance._getCredentials(callback)
