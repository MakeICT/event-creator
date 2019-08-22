from main import db, Event, Platform, ExternalEvent
import plugins

loadedPlugins = plugins.loadAllFromPath()

for plugin in loadedPlugins:
    if not Platform.query.filter_by(name=plugin).first():
        print(f"Adding new platform: {plugin}")
        new_platform = Platform(name=plugin)
        db.session.add(new_platform)
        db.session.commit()

event = Event.query.first()

active_plugins = ['WildApricot', 'Discourse']

if not event.sync_date:
    for platform in active_plugins:
        event_id = loadedPlugins[platform].createEvent(event)
        for ext_event in event.external_events:
            if ext_event.ext_event_id == event_id:
                ext_event.primary_event = True
                db.session.add(ext_event)
                db.session.commit()

    event.updateSyncDate()
