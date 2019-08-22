from main import db, Event, Platform, ExternalEvent
import plugins

loadedPlugins = plugins.loadAllFromPath()

event = Event.query.first()

if not event.sync_date:
    loadedPlugins['WildApricot'].createEvent(event)
    event.updateSyncDate()
