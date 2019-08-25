# -*- coding: utf-8 -*-

import logging

# import ui
# from PySide import QtCore

from . import pydiscourse
from .pydiscourse import DiscourseClient
from plugins import EventPlugin

from config import settings
import config


class DiscoursePlugin(EventPlugin):
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

    def createEvent(self, event):
        logging.debug('Discourse')

        dateTimeFormat = '%Y %b %d - %I:%M %p'

        description = event.htmlSummary()

        logging.debug('Connecting to API')

        discourse_api = DiscourseClient(
            self.getSetting('Website'),
            api_username=self.getSetting('Username'),
            api_key=self.getSetting('API Key'))

        logging.debug('Creating post')
        title = 'Event notice: ' + event.title + ' (' \
            + event.start_date.strftime(dateTimeFormat) + ')'
        post = discourse_api.create_post(content=description,
                                         category_id=int(self.getSetting('Category ID')),
                                         topic_id=None, title=title)

        post_url = f"https://talk.makeict.org/t/{post['id']}"

        return (post['id'], post_url)

    def updateEvent(self, event):
        logging.debug('Discourse')

        dateTimeFormat = '%Y %b %d - %I:%M %p'

        description = event.htmlSummary()

        logging.debug('Connecting to API')

        discourse_api = DiscourseClient(
            self.getSetting('Website'),
            api_username=self.getSetting('Username'),
            api_key=self.getSetting('API Key'))

        logging.debug('Creating post')
        title = 'Event notice: ' + event.title + ' (' \
            + event.start_date.strftime(dateTimeFormat) + ')'

        post_id = next(item.ext_event_id for item in event.external_events
                       if item.platformName() == self.name)
        discourse_api.update_post(post_id=post_id,
                                  content=description,
                                  category_id=int(self.getSetting('Category ID')),
                                  topic_id=None, title=title)

def load():
    return DiscoursePlugin()
