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
            monthly_topic_description = f"Event updates for {event.start_date.strftime('%B %Y')}"
            post = discourse_api.create_post(content=monthly_topic_description,
                                              category_id=int(self.getSetting('Category ID')),
                                              external_id=topic_ext_id, title=title)
            topic_id = post['topic_id']
        post = discourse_api.create_post(content=description,
                                         topic_id=topic_id)

        post_url = f"https://talk.makeict.org/p/{post['id']}"

        return (post['id'], post_url)

    def updateEvent(self, event):
        logging.debug('Discourse')
        self.deleteEvent(event)
        post = self.createEvent(event)

        return post

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
        try:
            discourse_api._delete(f"/posts/{post_id}.json")
            logging.info(f"Deleted {event.id} from Discourse")
            post = discourse_api.post_by_id(post_id=post_id)
        except DiscourseClientError:
            logging.warning(f"Could not delete {event.id} from Discourse")
            logging.warning(f"Trying to delete using deprecated scheme")
            try:
                post = discourse_api.post_by_id(post_id=post_id)
                topic = discourse_api.topic(slug=post['topic_slug'], topic_id=post['topic_id'])
                if not topic.get('external_id'):
                    topic_id = post['topic_id']
                    discourse_api.delete_topic(topic_id=topic_id)
                    logging.info(f"Deleted {event.id} from Discourse")
            except DiscourseClientError:
                logging.error(f"Could not delete {event.id} from Discourse")



def load():
    return DiscoursePlugin()
