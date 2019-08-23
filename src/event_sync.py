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

active_plugins = ['WildApricot', 'Discourse', 'GoogleCalendar']

for event in events:
    platform_list = [Platform.query.filter_by(name=ap).first() for ap in active_plugins]
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