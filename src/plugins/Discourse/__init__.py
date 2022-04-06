# -*- coding: utf-8 -*-

import logging

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
        logging.debug('Discourse')

        dateTimeFormat = '%Y %b %d - %I:%M %p'

        description = f"<h1>{event.title}</h1> {event.htmlSummary()}"

        logging.debug('Connecting to API')

        discourse_api = DiscourseClient(
            self.getSetting('Website'),
            api_username=self.getSetting('Username'),
            api_key=self.getSetting('API Key'))

        logging.debug('Creating post')
        title = f"Event Updates for {event.start_date.strftime('%B %Y')}"
        topic_ext_id = f"{self.getSetting('Category ID')}_event_updates_{event.start_date.month}-{event.start_date.year}"
        topic_id = None
        try:
            topic = discourse_api._get(f"/t/external_id/{topic_ext_id}.json", override_request_kwargs={"allow_redirects": True})
            topic_id = topic['id']
            title = None
        except DiscourseClientError:
            # create the monthly topic if it doesn't exist
            monthly_topic_description = f"Event updates for {event.start_date.month} {event.start_date.year}"
            discourse_api.create_post(content=monthly_topic_description,
                                      category_id=int(self.getSetting('Category ID')),
                                      external_id=topic_ext_id, title=title)
        

        post = discourse_api.create_post(content=description,
                                         category_id=int(self.getSetting('Category ID')),
                                         external_id=topic_ext_id, title=title, topic_id=topic_id)

        post_url = f"https://talk.makeict.org/t/{post['id']}"

        return (post['id'], post_url)

    def updateEvent(self, event):
        logging.debug('Discourse')
        self.deleteEvent(event)
        self.createEvent(event)

        return True

    def deleteEvent(self, event):
        logging.debug('Discourse')

        logging.debug('Connecting to API')

        discourse_api = DiscourseClient(
            self.getSetting('Website'),
            api_username=self.getSetting('Username'),
            api_key=self.getSetting('API Key'))

        logging.debug('Deleting post')

        post_id = next(item.ext_event_id for item in event.external_events
                       if item.platformName() == self.name)

        discourse_api._delete(f"/posts/{post_id}.json")


def load():
    return DiscoursePlugin()
