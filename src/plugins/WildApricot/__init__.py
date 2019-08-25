import logging
import pytz

from .wildapricot_api import WaApiClient
from plugins import EventPlugin

from config import settings
import config


class WildApricotPlugin(EventPlugin):
    def __init__(self):
        super().__init__('WildApricot')

        self.options = [
            {
                'name': 'API Key',
                'type': 'text',
            }, {
                'name': 'Level IDs for members',
                'type': 'text',
            }, {
                'name': 'Registration URL format',
                'type': 'text',
            }, {
                'name': 'Use this as registration URL',
                'type': 'yesno',
            }, {
                'name': 'Enable group-based authorizations',
                'type': 'yesno',
            }
        ]
        logging.debug('Connecting to API')
        self.api = WaApiClient()

    def _buildEvent(self, event, wa_id=None):
        if self.getGeneralSetting('timezone') is not None \
                and self.getGeneralSetting('timezone') != '':
            timezone = pytz.timezone(self.getGeneralSetting('timezone'))
        else:
            timezone = pytz.timezone("UTC")

        tags = ["instructor_name:" + event.instructor_name,
                "instructor_email:" + event.instructor_email]

        description = event.htmlSummary(omit=['reg', 'price'])

        event_data = {
            "Name": event.title,
            "StartDate": self.api.DateTimeToWADate(
                             timezone.localize(event.start_date)),
            "EndDate": self.api.DateTimeToWADate(
                           timezone.localize(event.end_date)),
            "Location": event.location,
            "RegistrationsLimit": event.registration_limit,
            "RegistrationEnabled": True,
            "StartTimeSpecified": True,
            "EndTimeSpecified": True,
            "Details": {
                "DescriptionHtml": description,
                "AccessControl": {"AccessLevel": "Public"},
                "GuestRegistrationSettings": {
                    "CreateContactMode": "CreateContactForAllGuests"
                },
                "PaymentMethod": "OnlineAndOffline",
                "SendEmailCopy": False,
                "WaitListBehaviour": "Disabled",
            },
            "Tags": tags
        }

        if wa_id:
            event_data['id'] = wa_id

        return event_data

    def _buildRSVPs(self, event, wa_id):
        rsvp_types = []

        for rsvpType in event.prices:
            registrationTypeData = {
                "EventId": wa_id,
                "Name": rsvpType.name,
                "BasePrice": str(rsvpType.value),
                "Description": rsvpType.description,
                "IsEnabled": True,
                "GuestRegistrationPolicy": "Disabled",
                "MultipleRegistrationAllowed": False,
                "WaitlistBehaviour": "Disabled",
                "UnavailabilityPolicy": "Show"
            }

            for populationType in rsvpType.availability:
                if populationType == 'Members':
                    registrationTypeData['Availability'] = 'MembersOnly'
                    registrationTypeData['AvailableForMembershipLevels'] = []

                    ids = self.getSetting('Level IDs for members').split(',')

                    for id in ids:
                        registrationTypeData['AvailableForMembershipLevels'] \
                            .append({'Id': id})
                else:
                    registrationTypeData['Availability'] = 'Everyone'

            rsvp_types.append(registrationTypeData)

        return rsvp_types

    def createEvent(self, event):
        self.api.authenticate_with_apikey(self.getSetting('API Key'))

        eventData = self._buildEvent(event)

        logging.debug('Creating event')
        eventID = self.api.execute_request('Events', eventData)

        for rsvp in self._buildRSVPs(event, eventID):
            logging.debug('Adding registration type: ' + rsvp['Name'])
            self.api.execute_request('EventRegistrationTypes', rsvp)

        auth_ids = [auth.wa_group_id for auth in event.authorizations]

        for auth in event.authorizations:
            logging.debug('Adding auth group requirements')
            self.api.SetEventAccessControl(eventID, restricted=True,
                                           any_level=False, any_group=False,
                                           group_ids=auth_ids, level_ids=[])

        registration_url = \
            'http://makeict.wildapricot.org/event-%s' % eventID

        return (eventID, registration_url)


def load():
    return WildApricotPlugin()
