import logging
import pytz
from urllib.error import HTTPError

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

    def updateEvent(self, event):
        self.api.authenticate_with_apikey(self.getSetting('API Key'))
        wa_event_id = None
        for e in event.external_events:
            if e.platformName() == self.name:
                wa_event_id = e.ext_event_id
        eventData = self._buildEvent(event, wa_event_id)

        print("wa event id:", wa_event_id)

        logging.debug('Updating event')
        try:
            self.api.execute_request(f"Events/{wa_event_id}", eventData, method='PUT')
        except HTTPError as err:
            if err.code == 400:
                return False
            else:
                raise

        wa_event = self.api.GetEventByID(wa_event_id)
        wa_event_reg_types = [t for t in wa_event['Details']['RegistrationTypes']]
        wa_event_reg_type_names = [t['Name'] for t
                                   in wa_event_reg_types]

        reg_types = self._buildRSVPs(event, wa_event_id)
        new_types = [t for t in reg_types
                     if t['Name'] not in wa_event_reg_type_names]
        existing_types = [t for t in reg_types
                          if t['Name'] in wa_event_reg_type_names]

        for rtype in new_types:
            logging.debug('Adding registration type: ' + rtype['Name'])
            self.api.execute_request('EventRegistrationTypes', rtype)

        for rtype in existing_types:
            logging.debug('Updating registration type: ' + rtype['Name'])
            rtype['Id'] = next(item for item in wa_event_reg_types
                               if item['Name'] == rtype['Name'])['Id']
            self.api.execute_request(f"EventRegistrationTypes/{rtype['Id']}",
                                     rtype, method='PUT')

        for rtype in wa_event_reg_types:
            if rtype['Name'] not in [rt['Name'] for rt in new_types] and \
               rtype['Name'] not in [rt['Name'] for rt in existing_types]:
                self.api.execute_request(f"EventRegistrationTypes/{rtype['Id']}",
                                         method="DELETE")

        auth_ids = [auth.wa_group_id for auth in event.authorizations]

        for auth in event.authorizations:
            logging.debug('Adding auth group requirements')
            self.api.SetEventAccessControl(int(wa_event_id), restricted=True,
                                           any_level=False, any_group=False,
                                           group_ids=auth_ids, level_ids=[])

        registration_url = \
            'http://makeict.wildapricot.org/event-%s' % wa_event_id

        return (wa_event_id, registration_url)


def load():
    return WildApricotPlugin()
