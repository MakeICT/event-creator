# -*- coding: utf-8 -*-

import logging

# import ui
# from PySide import QtCore

from . import pydiscourse
from .pydiscourse import DiscourseClient
from plugins import Plugin

from config import settings
import config


class DiscoursePlugin(Plugin):
    def __init__(self):
        super().__init__('Discourse')

        self.options = [
            {
                'name': 'Website',
                'type': 'text',
            }, {
                'name': 'Username',
                'type': 'text',
            }, {
                'name': 'API Key',
                'type': 'text',
            }, {
                'name': 'Category ID',
                'type': 'text',
            }, {
                'name': 'Date/Time format',
                'type': 'text',
            },
        ]

        # ui.addTarget(self.name, self, self.createForumPost)
        # ui.addPopulationType('Members')

    def createForumPost(self, event):
        logging.debug('Discourse')

        dateTimeFormat = self.getSetting(
                                'Date/Time format', 'yyyy MMM dd - h:mm ap')

        description = "**Starting:** " \
            + event['startTime'].toString(dateTimeFormat)
        description += '\n' + "**Ending:** " \
            + event['stopTime'].toString(dateTimeFormat)
        description += '\n' + "**Instructor:** " \
            + ' '.join(event['instructorDescription'].split(' ')[1:])

        if event['registrationURL'] and event['registrationURL'] != '':
            description += '\n' + "**Register:** " + '[' \
                + event['registrationURL'] + '](' + event['registrationURL'] + ')'

        description += '\n' + "**Price:** " + event['priceDescription'][28:]

        if event['ageDescription']:
            description += '\n' + "**Ages:** " \
                + ' '.join(event['ageDescription'].split(' ')[1:])

        if event['authorizationDescription']:
            description += '\n' + "**Required Authorizations:** " \
                + ', '.join(event['authorizationDescription'].split(' ')[2:])

        description += '\n\n' + event['description']

        self.checkForInterruption()

        logging.debug('Connecting to API')
        print('username:', self.getSetting('Username'))
        print('api key:', self.getSetting('API Key'))

        discourse_api = DiscourseClient(
            self.getSetting('Website'),
            api_username=self.getSetting('Username'),
            api_key=self.getSetting('API Key'))

        self.checkForInterruption()
        logging.debug('Creating post')
        title = 'Event notice: ' + event['title'] + ' (' \
            + event['startTime'].toString(dateTimeFormat) + ')'
        discourse_api.create_post(content=description,
                                  category_id=int(self.getSetting('Category ID')),
                                  topic_id=None, title=title)
        return


def load():
    return DiscoursePlugin()
