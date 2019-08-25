from main import db, loadedPlugins
from models import Event, Platform, ExternalEvent


def SyncEvent(event):
    platform_list = [Platform.query.all()]
    event.platforms = platform_list
    db.session.add(event)

    db.session.commit()

    if not event.fullySynced():
        for platform in event.platforms:
            if platform.id in [ext.platform_id for ext in event.external_events]:
                pass
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
