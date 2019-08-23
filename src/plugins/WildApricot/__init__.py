import logging
import pytz

from .wildapricot_api import WaApiClient
from plugins import Plugin

from config import settings
import config


class WildApricotPlugin(Plugin):
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

    def createEvent(self, event):
        if self.getGeneralSetting('timezone') is not None \
                and self.getGeneralSetting('timezone') != '':
            timezone = pytz.timezone(self.getGeneralSetting('timezone'))
        else:
            timezone = pytz.timezone("UTC")

        tags = ["instructor_name:" + event.instructor_name,
                "instructor_email:" + event.instructor_email]

        description = event.htmlSummary(omit=['reg', 'price'])

        logging.debug('Connecting to API')
        api = WaApiClient()
        api.authenticate_with_apikey(self.getSetting('API Key'))

        eventData = {
            "Name": event.title,
            "StartDate": api.DateTimeToWADate(
                             timezone.localize(event.start_date)),
            "EndDate": api.DateTimeToWADate(
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

        logging.debug('Creating event')
        eventID = api.execute_request('Events', eventData)

        for rsvpType in event.prices:
            registrationTypeData = {
                "EventId": eventID,
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

            logging.debug('Adding registration type: ' + rsvpType.name)
            api.execute_request('EventRegistrationTypes', registrationTypeData)

        auth_ids = [auth.wa_group_id for auth in event.authorizations]

        for auth in event.authorizations:
            logging.debug('Adding auth group requirements')
            api.SetEventAccessControl(eventID, restricted=True,
                                      any_level=False, any_group=False,
                                      group_ids=auth_ids, level_ids=[])

        registration_url = \
            'http://makeict.wildapricot.org/event-%s' % eventID

        return (eventID, registration_url)


def load():
    return WildApricotPlugin()
