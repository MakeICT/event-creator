# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("discourse.log")
logger.addHandler(file_handler)
logger.setLevel('DEBUG')
logger.debug("Loading Discourse Plugin")

# import ui
# from PySide import QtCore

from pydiscourse import DiscourseClient
from pydiscourse.exceptions import DiscourseClientError
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
        logger.debug('Discourse')

        dateTimeFormat = '%Y %b %d - %I:%M %p'

        description = event.htmlSummary()

        logger.debug('Connecting to API')

        discourse_api = DiscourseClient(
            self.getSetting('Website'),
            api_username=self.getSetting('Username'),
            api_key=self.getSetting('API Key'))

        logger.debug('Creating post')
        title = 'Event notice: ' + event.title + ' (' \
            + event.start_date.strftime(dateTimeFormat) + ')'
        try:
            post = discourse_api.create_post(content=description,
                                             category_id=int(self.getSetting('Category ID')),
                                             topic_id=None, title=title)
        except:
            logger.debug("discourse post failed!:\n", exc_info=True)

        post_url = f"https://talk.makeict.org/t/{post['id']}"

        return (post['id'], post_url)

    def updateEvent(self, event):
        logger.debug('Discourse')

        dateTimeFormat = '%Y %b %d - %I:%M %p'

        description = event.htmlSummary()

        logger.debug('Connecting to API')

        discourse_api = DiscourseClient(
            self.getSetting('Website'),
            api_username=self.getSetting('Username'),
            api_key=self.getSetting('API Key'))

        logger.debug('Updating post')
        title = 'Event notice: ' + event.title + ' (' \
            + event.start_date.strftime(dateTimeFormat) + ')'

        post_id = next(item.ext_event_id for item in event.external_events
                       if item.platformName() == self.name)
        try:
            discourse_api.update_post(post_id=post_id,
                                      content=description,
                                      category_id=int(self.getSetting('Category ID')),
                                      topic_id=None, title=title)
        except DiscourseClientError as err:
            if err.__str__() == "The requested URL or resource could not be found.":
                return False
            else:
                raise

        return True

    def deleteEvent(self, event):
        logger.debug('Discourse')

        dateTimeFormat = '%Y %b %d - %I:%M %p'

        description = event.htmlSummary()

        logger.debug('Connecting to API')

        discourse_api = DiscourseClient(
            self.getSetting('Website'),
            api_username=self.getSetting('Username'),
            api_key=self.getSetting('API Key'))

        logger.debug('Deleting post')
        title = 'Event notice: ' + event.title + ' (' \
            + event.start_date.strftime(dateTimeFormat) + ')'

        post_id = event.getExternalEventByPlatformName(self.name).ext_event_id
        try:
            post = discourse_api.update_post(post_id=post_id,
                                             content=description,
                                             category_id=int(self.getSetting('Category ID')),
                                             topic_id=None, title=title)

        except DiscourseClientError as err:
            if err.__str__() == "The requested URL or resource could not be found.":
                # Looks like the post is already gone
                return
            else:
                raise

        topic_id = post['post']['topic_id']
        discourse_api.delete_topic(topic_id=topic_id)


def load():
    return DiscoursePlugin()
