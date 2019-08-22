# -*- coding: utf-8 -*-

import logging

import meetup.api

from plugins import Plugin
import config


class MeetupPlugin(Plugin):
    def __init__(self):
        super().__init__('Meetup')

        self.options = [
            {
                'name': 'API Key',
                'type': 'text',
            }, {
                'name': 'Group name',
                'type': 'text',
            }, {
                'name': 'Venue ID',
                'type': 'text',
            }, {
                'name': 'Use this as registration URL',
                'type': 'yesno',
            }, {
                'name': 'Title prepend',
                'type': 'text',
            }, {
                'name': 'Title append',
                'type': 'text',
            }, {
                'name': 'Allow RSVP',
                'type': 'yesno',
            }, {
                'name': 'Post as draft',
                'type': 'yesno',
            }
        ]
        # @TODO: Download venue list and add them to the location dropdown in the UI
        # ui.addTarget(self.name, self, self.createEvent)

    def createEvent(self, event):
        api = meetup.api.Client(self.getSetting('API Key'))
        group = api.GetGroup({'urlname': self.getSetting('Group name')})

        if event['registrationURL'] != '':
            description = '<p>To register for this event, please visit ' \
                + '<a href="%s">%s</a></p><p><br></p>' \
                % (event['registrationURL'], event['registrationURL'])
            # description += '\n\n'
        else:
            description = ''

        description += '<p>'+event['description']+'</p>'

        if event['authorizationDescription']:
            description += event['authorizationDescription']

        prepend = self.getSetting('Title prepend', '')
        append = self.getSetting('Title append', '')
        if prepend != '':
            title = prepend + ' ' + event['title']
        else:
            title = event['title']

        if append != '':
            title += ' ' + append
        rsvp_limit = 1

        if config.checkBool(self.getSetting("Allow RSVP")):
            rsvp_limit = 0

        if config.checkBool(self.getSetting("Post as draft")):
            publish_status = 'draft'
        else:
            publish_status = 'published'

        meetup_details = {
            'group_id': group.id,
            'name': title,
            'description': description,
            'time': event['startTime'].toTime_t() * 1000,
            'duration': event['startTime'].msecsTo(event['stopTime']),
            'venue_id': self.getSetting('Venue ID'),
            'publish_status': publish_status,
            'rsvp_limit': rsvp_limit,
            'guest_limit': 0,
            'waitlisting': 'off',
        }
        if event['registrationURL'] != '':
            meetup_details['question_0'] = \
                "This event requires external registration. Please follow " \
                "the link in the event description to register for this class. " \
                "Registering on Meetup does not reserve your spot for this event."

        self.checkForInterruption()
        meetupEvent = api.CreateEvent(meetup_details)

        if config.checkBool(self.getSetting('Use this as registration URL')):
            event['registrationURL'] = meetupEvent.event_url

        return meetupEvent.event_url


def load():
    return MeetupPlugin()
