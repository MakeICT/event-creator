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

    def createEvent(self, event):
        logging.debug('Discourse')

        dateTimeFormat = '%Y %b %d - %I:%M %p'

        description = "**Starting:** " \
            + event.start_date.strftime(dateTimeFormat)
        description += '\n' + "**Ending:** " \
            + event.end_date.strftime(dateTimeFormat)
        description += '\n' + "**Instructor:** " \
            + event.instructor_name

        if event.external_events:
            for ext_event in event.external_events:
                if ext_event.primary_event:
                    description += f"\n**Register:** [{ext_event.ext_event_url}]" \
                                   f"({ext_event.ext_event_url})"
        for price in event.prices:
            description += f"\n **Price:** {price.name} - ${price.value:.2f}"

        if event.min_age and not event.max_age:
            description += f"\n**Ages**: {event.min_age} and up\n"
        elif event.max_age and not event.min_age:
            description += f"\n**Ages**: {event.max_age} and under\n"
        elif event.min_age and event.max_age:
            description += f"\n**Ages**: {event.min_age} to {event.max_age}\n"

        if event.authorizations:
            description += f"\n**Required Authorizations:** " \
                + f"{', '.join([auth.name for auth in event.authorizations])}"

        description += '\n\n' + event.description

        logging.debug('Connecting to API')
        print('username:', self.getSetting('Username'))
        print('api key:', self.getSetting('API Key'))

        discourse_api = DiscourseClient(
            self.getSetting('Website'),
            api_username=self.getSetting('Username'),
            api_key=self.getSetting('API Key'))

        logging.debug('Creating post')
        title = 'Event notice: ' + event.title + ' (' \
            + event.start_date.strftime(dateTimeFormat) + ')'
        discourse_api.create_post(content=description,
                                  category_id=int(self.getSetting('Category ID')),
                                  topic_id=None, title=title)
        return


def load():
    return DiscoursePlugin()
