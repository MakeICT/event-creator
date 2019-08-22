from main import db, Event, Platform, ExternalEvent
import plugins

loadedPlugins = plugins.loadAllFromPath()

for plugin in loadedPlugins:
    if not Platform.query.filter_by(name=plugin).first():
        print(f"Adding new platform: {plugin}")
        new_platform = Platform(name=plugin)
        db.session.add(new_platform)
        db.session.commit()

events = Event.query.all()

active_plugins = ['WildApricot', 'Discourse']

for event in events:
    if not event.sync_date:
        for platform in active_plugins:
            event_id = loadedPlugins[platform].createEvent(event)
            # Set first external event as primary event
            if len(event.external_events) == 1:
                ext_event = event.external_events[0]
                ext_event.primary_event = True
                db.session.add(ext_event)
                db.session.commit()

        event.updateSyncDate()
