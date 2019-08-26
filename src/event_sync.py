from main import db, loadedPlugins
from models import Event, Platform, ExternalEvent


class EventSyncError(Exception):
    pass


class MissingExternalEventError(EventSyncError):
    """
    Exception raised when an external event cannot be found.

    Attributes:
        platform -- the platform of the external event
        message -- explanation of the error
    """

    def __init__(self, platform, message):
        self.platform = platform
        self.message = message


def SyncEvent(event):
    if not event.fullySynced():
        for platform in event.platforms:
            if platform.id in [ext.platform_id for ext in event.external_events]:
                event_result = loadedPlugins[platform.name].updateEvent(event)
                if event_result is False:
                    raise MissingExternalEventError(platform.name,
                        f"Linked event could not be found on {platform.name}")
                ext_event = ExternalEvent.query.filter_by(platform_id=platform.id,
                                                          event_id=event.id).first()
                print("update sync date for", platform.name)
                ext_event.updateSyncDate()

            else:
                event_result = loadedPlugins[platform.name].createEvent(event)
                event_id = event_result[0]
                event_url = event_result[1]

                ext_event = event.addExternalEvent(platform.name, event_id, event_url)
                ext_event.updateSyncDate()

                # Set first external event as primary event
                if len(event.external_events) == 1:
                    ext_event = event.external_events[0]
                    ext_event.primary_event = True
                    db.session.add(ext_event)
                    db.session.commit()


def SyncEvents(events):
    for event in events:
        SyncEvent(event)
